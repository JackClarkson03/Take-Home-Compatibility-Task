# --- Pipeline Architecture --- #

# Import Libraries
import whisper
import json
import os
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline as hf_pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from . import heuristics
from . import config

# Define Absolute Paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
USER_PROFILES_PATH = os.path.join(PROJECT_ROOT, "data", "user_profiles.json")


# Load User Profiles
def load_user_profiles(file_path: str = USER_PROFILES_PATH) -> dict:
    """
    Loads user profiles from a JSON file into a dictionary
    """

    try:
        with open(file_path, 'r') as f:
            profiles_list = json.load(f)

        profiles_dict = {user["id"]: user for user in profiles_list}
        print("User profiles successfully loaded.")
        return profiles_dict

    except FileNotFoundError:
        print(f"ERROR: No user profiles found at {file_path}")
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise


# Transcription
model_cache_dir = os.path.join(PROJECT_ROOT, "whisper_cache")
print(f"Whisper model cache set to: {model_cache_dir}")
model = whisper.load_model("base", download_root=model_cache_dir)


def transcribe_audio(audio_path: str) -> str:

    result = model.transcribe(audio_path)
    return result["text"]



# Extract Topics and get Vector Representation:
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_topics_and_vectors(transcript: str):
    """
    This uses an LLM to extract the 5 main, high-level topics from the transcript,
    and then score those 5 topics against the 5 personality traits.
    It also analyses social cues (like style, and seniment) to esitmate conversational engagement level.
    """
    prompt = f"""
    You are a multi-stage analysis tool for the transcipt:
    \"\"\"
    {transcript}
    \"\"\"

    First, analyse the transcript and identify the 5 most important topics of themes. Do not just include simple keywords; find abstract concepts as well.

    Second, based ONLY on those 5 topics you identified, analyse their association with with these 5 personality traits: [openness, conscientiousness, extraversion, agreeableness, neuroticism].

    Finally, based on the transcripts's interactivity (e.g. questions, short responses, turn-taking) and emotional expression, estimate the overall engagement level of the participants as a single flotat between 0.0 (disengaged, bored) and 1.0 (highly engaged, animated).

    You MUST return ONLY a valid JSON object with four keys:
    1. "topics": A list of 5 topic strings.
    2. "topic_vector": A list of 5 floats (0.0 - 1.0) representing the score for each personality trait in the given order.
    3. "engagement_score": A float (0.0 - 1.0).
    """

    try:
        response = client.chat.completions.create(model = config.LLM_MODEL_NAME,
                                                  response_format = {"type": "json_object"},
                                                  messages = [{"role": "system", "content": "You are a helpful assistant that returns ONLY valid JSON."},
                                                              {"role": "user", "content": prompt}],
                                                  temperature = 0.1)
        
        result_data = json.loads(response.choices[0].message.content)

        if (isinstance(result_data, dict) and 
            "topics" in result_data and "topic_vector" in result_data and "engagement_score" in result_data and
            isinstance(result_data["topics"], list) and len(result_data["topics"]) == 5 and
            isinstance(result_data["topic_vector"], list) and len(result_data["topic_vector"]) == 5 and
            isinstance(result_data["engagement_score"], float)):

            print(f"LLM-generated topics: {result_data['topics']}")
            print(f"LLM-generated vector: {result_data['topic_vector']}")
            print(f"LLM-generated engagement: {result_data['engagement_score']}")
            return result_data["topics"], result_data["topic_vector"], result_data["engagement_score"]
        else:
            print(f"Warning: LLM output invalid: {result_data}. Falling back to defaults.")
            return ["blank topic"], [0.5] * 5, 0.0
        
    except Exception as e:
        print(f"Error: {e}. Falling back to defaults.")
        return ["blank topic"], [0.5] * 5, 0.0
    

# Second Sentiment Analysis Source
vader_analyzer = SentimentIntensityAnalyzer()

def get_vader_sentiment(transcript: str) -> float:
    scores = vader_analyzer.polarity_scores(transcript)
    return scores['compound']


# Mock function to handle OPENAI API quota exceeding
def get_topics_and_vectors_mock(transcript: str):
    """
    Temporary mock function for testing when
    running out of API calls...
    """
    print(" USING TEMPORARY HIGH-QUALITY MOCK DATA ")
    mock_topics = ["Mars Colonisation Logistics", "Future of Humanity", "Civilisation and Risk", "Population Collapse", "Extending Consciousness"]
    mock_vector = [0.9, 0.7, 0.3, 0.4, 0.6]
    mock_engagement = 0.5

    print(f"Mock topics: {mock_topics}")
    print(f"MOck vector: {mock_vector}")
    print(f"MOck engagement: {mock_engagement}")

    return mock_topics, mock_vector, mock_engagement



# Fuse Topic and Personality Vectors:
def fuse_vectors(personality_vec: list[float], topic_vec: list[float], personality_weight: float = config.FUSION_PERSONALITY_WEIGHT) -> np.ndarray:
    """
    Fuses the personality vector and topic vector using a weighted average.
    This fused vector represents a persons personality in the context of the specific conversation.
    """

    topic_weight = 1 - personality_weight

    arr_pers = np.array(personality_vec)
    arr_topic = np.array(topic_vec)

    fused_vector = (personality_weight * arr_pers) + (topic_weight * arr_topic)

    return fused_vector




# Heuristic Compatibility Score
def heuristic_compatibility_score(pers_vec_1: list[float], pers_vec_2: list[float], analysis_results: dict) -> dict:
    '''
    Scores two users compatibility given their personality vectors, and the dictionary contianing topic vector and engagement.
    '''

    return heuristics.calculate_heuristic_score(pers_vec_1, pers_vec_2, analysis_results)
