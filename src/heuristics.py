# --- Heuristic Compatibility Functions --- #


# Import Libraries
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean

from . import config


# Euclidean Distance Instead of Cosine Similarity
def _scaled_euclidean_similarity(vec1, vec2) -> float:
    """
    Calculated the similarity based on Euclidean distance, scaled to [0,1]
    """
    distance = euclidean(np.array(vec1), np.array(vec2))
    similarity = 1 / (1 + distance)
    return similarity


# Explanable Scores for Each Personality Trait
def _score_openness(p1_score, p2_score):
    """
    Similarity on openness is generally good, with a bias towards high openness.
    """
    similarity = 1.0 - abs(p1_score - p2_score)
    avg_score = (p1_score + p2_score) / 2

    return (0.7 * similarity) + (0.3 * avg_score)


def _score_conscientiousness(p1_score, p2_score):
    """
    Similarity on conscientiousness is generally good, with a bias towards high conscientiousness.
    """
    similarity = 1.0 - abs(p1_score - p2_score)
    avg_score = (p1_score + p2_score) / 2

    return (0.7 * similarity) + (0.3 * avg_score)


def _score_extraversion(p1_score, p2_score):
    """
    Complementary extraversion scores are preferred.
    """
    return abs(p1_score - p2_score)


def _score_agreeableness(p1_score, p2_score):
    """
    Agreeableness is generally good for compatibility.
    """
    penalty = (1 - p1_score) * (1 - p2_score)
    return max(0, min(1,(p1_score + p2_score) / 2 - (penalty * 0.25)))


def _score_neuroticism(p1_score, p2_score):
    """
    Neuroticism is generally bad for compatibility.
    """
    friction_score = 1 - ((p1_score + p2_score)/2)
    clash_penalty = p1_score * p2_score
    return max(0, min(1, friction_score - (clash_penalty * 0.25)))


def _time_embedded_vector_weighting(personality_weight, word_count):
    '''
    Calculates the new psychometric vs. audio compatibility weighting
    based on the length of conversation.
    '''
    word_count_bonus = -0.2

    if word_count <= 1500:
        word_count_bonus = word_count / 7500 - 0.2
    else:
        word_count_bonus = 0.2
    
    return np.clip(personality_weight + word_count_bonus, 0.0, 1.0)



def calculate_heuristic_score(pers_vec_1: list[float], pers_vec_2: list[float], analysis_results: dict) -> dict:

    # How compatible people are based on individual personality trait heuristics
    scores = {"openness": _score_openness(pers_vec_1[0], pers_vec_2[0]),
              "conscientiousness": _score_conscientiousness(pers_vec_1[1], pers_vec_2[1]),
              "extraversion": _score_extraversion(pers_vec_1[2], pers_vec_2[2]),
              "agreeableness": _score_agreeableness(pers_vec_1[3], pers_vec_2[3]),
              "neuroticism": _score_neuroticism(pers_vec_1[4], pers_vec_2[4])}
    
    topic_vec = analysis_results["topic_vector"]

    engagement_score = analysis_results["engagement_score"]
    vadeder_engagement = analysis_results["vader_engagement"] * config.HEURISTIC_TOPIC_WEIGHTS['vader_cue_bonus']

    # How interested is the least intersted person in the conversation.
    interest_1 = _scaled_euclidean_similarity(pers_vec_1, topic_vec)
    interest_2 = _scaled_euclidean_similarity(pers_vec_2, topic_vec)
    min_interest = min(interest_1, interest_2)

    # Scale the Topic Interest Vector to a Wider Range of Value (Necessary due to min)
    mu = config.HEURISTIC_TOPIC_WEIGHTS["topic_centring"]
    stretch_factor = config.HEURISTIC_TOPIC_WEIGHTS["topic_stretch_factor"]
    vec_interest = np.clip(mu + stretch_factor*(min_interest - mu), 0.0, 1.0)

    # Implement Score for Engagement of Participants as a proxy for interest in the topic
    engagenent_adjustment = (engagement_score - 0.5) * config.HEURISTIC_TOPIC_WEIGHTS["social_cue_bonus"]
    scores_topic = np.clip(vec_interest + engagenent_adjustment + vadeder_engagement, 0.0, 1.0)

    # How important are different personality traits and topic contexual personality
    weights = {"openness": config.HEURISTIC_WEIGHTS["openness"],
               "conscientiousness": config.HEURISTIC_WEIGHTS["conscientiousness"],
               "extraversion": config.HEURISTIC_WEIGHTS["extraversion"],
               "agreeableness": config.HEURISTIC_WEIGHTS["agreeableness"],
               "neuroticism": config.HEURISTIC_WEIGHTS["neuroticism"]}
    
    
    word_count = analysis_results["word_count"]
    personality_weight = config.HEURISTIC_PERSONALITY_WEIGHT
    p_weight = _time_embedded_vector_weighting(personality_weight, word_count)
    
    final_score = sum(scores[key] * weights[key] for key in weights) * p_weight + scores_topic * (1-p_weight)

    explanation = (f"Final Score: {final_score:.2f}." 
                   f"Topic Interest: {vec_interest:.2f}, Social Cue Bonus: {engagenent_adjustment + vadeder_engagement:.2f}, Length of Audio Bonus: {personality_weight - p_weight:.2f}. "
                   f"Trait Scores (0-1): Openness: {scores["openness"]:.2f}, Conscientiousness: {scores['conscientiousness']:.2f}, "
                   f"Extraversion: {scores['extraversion']:.2f}, Agreeableness: {scores['agreeableness']:.2f}, Neuroticosim: {scores['neuroticism']:.2f}.")
    return {"match_score": final_score, "explanation": explanation, "breakdown": scores}




# Baseline Compatibility Score
def baseline_compatibility_score(vec1, vec2):
    score = cosine_similarity(vec1.reshape(1,-1), vec2.reshape(1,-1))[0][0]

    # Interpret the score
    if score > 0.8:
        interpretation = "High compatibility in this conversation."
    elif score > 0.5:
        interpretation = "Moderate compatibility in this conversation."
    else:
        interpretation = "Low compatibility in this conversation."
    return {"score": score, "interpretation": interpretation}

