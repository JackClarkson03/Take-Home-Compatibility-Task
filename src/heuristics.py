# --- Heuristic Compatibility Functions --- #


# Import Libraries
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# Cosine Similairty Helper Function
def _cosine_sim(vec1, vec2) -> float:
    """
    rescale cosine similarity from [-1,1] to [0,1]
    """
    sim = cosine_similarity(np.array(vec1).reshape(1,-1), np.array(vec2).reshape(1,-1))[0][0]
    return (sim + 1)/2


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
    return (p1_score + p2_score) / 2 - (penalty * 0.5)


def _score_neuroticism(p1_score, p2_score):
    """
    Neuroticism is generally bad for compatibility.
    """
    friction_score = 1 - ((p1_score + p2_score)/2)
    clash_penalty = p1_score * p2_score
    return friction_score - (clash_penalty * 0.5)



def calculate_heuristic_score(pers_vec_1: list[float], pers_vec_2: list[float], topic_vec: list[float]) -> dict:

    # How compatible people are based on individual personality trait heuristics
    scores = {"openness": _score_openness(pers_vec_1[0], pers_vec_2[0]),
              "conscientiousness": _score_conscientiousness(pers_vec_1[1], pers_vec_2[1]),
              "extraversion": _score_extraversion(pers_vec_1[2], pers_vec_2[2]),
              "agreeableness": _score_agreeableness(pers_vec_1[3], pers_vec_2[3]),
              "neuroticism": _score_neuroticism(pers_vec_1[4], pers_vec_2[4])}
    
    # How compatible people are based on topic interest similarity
    interest_1 = _cosine_sim(pers_vec_1, topic_vec)
    interest_2 = _cosine_sim(pers_vec_2, topic_vec)
    scores["topic_interest"] = min(interest_1, interest_2)

    # Good to implement some social bonus based on conversational tone next.

    # How important are different personality traits and topic contexual personality
    weights = {"openness": 0.1,
               "conscientiousness": 0.15,
               "extraversion": 0.1,
               "agreeableness": 0.25,
               "neuroticism": 0.25,
               "topic_interest": 0.15}
    
    final_score = sum(scores[key] * weights[key] for key in weights)

    explanation = (f"Final Score: {final_score:.2f}." 
                   f"Key Drivers: Stability ({scores['neuroticism']:.2f}) and agreeableness ({scores['agreeableness']:.2f})")
    
    return {"match_score": final_score, "explanation": explanation}




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

