# --- Pipeline Architecture --- #

# Import Libraries
import whisper
from keybert import KeyBERT
import json
import os
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from . import heuristics

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
#model = whisper.load_model("base")
model_cache_dir = os.path.join(PROJECT_ROOT, "whisper_cache")
print(f"Whisper model cache set to: {model_cache_dir}")
model = whisper.load_model("base", download_root=model_cache_dir)


def transcribe_audio(audio_path: str) -> str:
    result = model.transcribe(audio_path)
    return result["text"]



# Topic Extraction
kw_model = KeyBERT(model='all-MiniLM-L6-v2')

def extract_topics(transcript: str, top_n: int = 5) -> list[str]:
    """
    Use keyBERT to find top 5 keywords/ phrases
    """
    keywords = kw_model.extract_keywords(transcript, keyphrase_ngram_range=(1,2), stop_words='english', top_n=top_n)
    topics = [topic for topic, score in keywords]
    return topics




# Create Personality Trait Representation of the Topic Vector:
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_topic_personality_vectors(topics: list[str]) -> list[float]:

    # Create the prompt
    prompt = f" Given these five personality traits: [openness, conscientiousness, extraversion, agreeableness, neuroticism], analyse these coversation topics:\n{', '.join(topics)}. Rate (0.0 - 1.0) the association of each topic with each of the five personality traits. Return ONLY a valid JSON list of 5 floats, each corresponding to the score for that trait in the given order. Example for topics 'philosophy, art': [0.9, 0.2, 0.4, 0.3, 0.2]."

    try:
        response = client.chat.completions.create(model = "gpt-3.5-turbo-1106",
                                                  response_format = {"type":"json_object"},
                                                  messages = [{"role": "system", "content": "You are a helpful assistant that returns ONLy valid JSON."},
                                                              {"role": "user", "content": prompt}],
                                                  temperature = 0.1)
        # Extract JSON from response
        result_string = response.choices[0].message.content
        result_list = json.loads(result_string)

        # Validation
        if isinstance(result_list, list) and len(result_list) == 5 and all(isinstance(x, (int, float)) for x in result_list):
            print(f"LLM-generated topic vector: {result_list}.")
            return result_list
        else:
            print(f"Warning: LLM output: {result_string} invalid. Default vector returned.")
            return [0.5, 0.5, 0.5, 0.5, 0.5]
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}. Default vector returned.")
        return [0.5, 0.5, 0.5, 0.5, 0.5]
    



# Fuse Topic and Personality Vectors:
def fuse_vectors(personality_vec: list[float], topic_vec: list[float], personality_weight: float = 0.7) -> np.ndarray:
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
def heuristic_compatibility_score(pers_vec_1: list[float], pers_vec_2: list[float], topic_vec: list[float]) -> dict:
    '''
    Scores two users compatibility given their personality vectors, and the topic vector.
    '''

    # Calculate 'Birds of a feather' score
    boaf_score = heuristics.birds_of_a_feather(pers_vec_1, pers_vec_2, topic_vec)

    # Calculate 'Opposites attract' score
    oa_score = heuristics.opposites_attract(pers_vec_1, pers_vec_2)

    # Would calculate an "in sync" metric with more time

    # Hueristic Combination
    weights = {"Similarity": 0.6, "Complementary": 0.4}
    final_score = (weights["Similarity"] * boaf_score["final_score"]) + (weights["Complementary"] * oa_score["final_score"])

    explanation = (f"Final Compatibility Score: {final_score:.2f}."
                   f"Similarity Score: {boaf_score["final_score"]:.2f} (weight: {weights["Similarity"]}) |"
                   f"Complementary Score: {oa_score["final_score"]:.2f} (weight: {weights["Complementary"]}).")
    
    return {"match_score": final_score, "explanation": explanation}
