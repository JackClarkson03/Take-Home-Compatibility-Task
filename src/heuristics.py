# --- Heuristic Compatibility Functions --- #


# Import Libraries
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# Cosine Similairt Helper Function
def _cosine_sim(vec1, vec2) -> float:
    """
    rescale cosine similarity from [-1,1] to [0,1]
    """
    sim = cosine_similarity(np.array(vec1).reshape(1,-1), np.array(vec2).reshape(1,-1))[0][0]
    return (sim + 1)/2




def birds_of_a_feather(pers_vec_1: list[float], pers_vec_2: list[float], topic_vec: list[float]) -> dict:
    """
    Calculates the 'Birds of a feather' similairty metric.
    """

    # Core Personality Similarity
    core_similarity = _cosine_sim(pers_vec_1, pers_vec_2)

    # Shared Topic Interest (a measure of the lowest interest of the two people in the topic)
    interest_1 = _cosine_sim(pers_vec_1, topic_vec)
    interest_2 = _cosine_sim(pers_vec_2, topic_vec)
    shared_interest = min(interest_1, interest_2)

    # Specific Trait Alignment
    agreeableness_sim = 1.0 - abs(pers_vec_1[3] - pers_vec_2[3])
    openness_sim = 1.0 - abs(pers_vec_1[0] - pers_vec_2[0])
    trait_alignment = (agreeableness_sim + openness_sim)/2

    # Combine with weights of importance
    weights = {"core_similarity": 0.4, "shared_interest": 0.3, "trait_alignment": 0.3}
    final_score = (weights["core_similarity"] * core_similarity) + (weights["shared_interest"] * shared_interest) + (weights["trait_alignment"] * trait_alignment)

    return {"final_score": final_score,
            "breakdown": {"core_similarity": core_similarity,
                          "shared_interest": shared_interest,
                          "trait_alignment": trait_alignment}}




def opposites_attract(pers_vec_1: list[float], pers_vec_2: list[float]) -> dict:
    """
    Calculates the 'opposites attract' metric of compatibility.
    """

    # Extraversion-Introversion
    extraversion_diff = abs(pers_vec_1[2] - pers_vec_2[2])

    # Spontaneity-Discipline
    conscientiousness_diff = abs(pers_vec_1[1] - pers_vec_2[1])

    # Stability-Sensitivity
    neuroticism_diff = abs(pers_vec_1[4] - pers_vec_2[4])

    # Combine with weights of importance
    weights = {"extraversion_diff": 0.6, "conscientiousness_diff": 0.1, "neuroticism_diff": 0.2}
    final_score = (weights["extraversion_diff"] * extraversion_diff) + (weights["conscientiousness_diff"] * conscientiousness_diff) + (weights["neuroticism_diff"] * neuroticism_diff)

    return {"final_score": final_score,
            "breakdown": {"extraversion_diff": extraversion_diff,
                          "conscientiousness_diff": conscientiousness_diff,
                          "neuroticism_diff": neuroticism_diff}}


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

