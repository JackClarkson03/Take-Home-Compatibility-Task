LLM_MODEL_NAME = "gpt-3.5-turbo-1106"

FUSION_PERSONALITY_WEIGHT = 0.75

HEURISTIC_WEIGHTS = {"openness": 0.13,
                     "conscientiousness": 0.13,
                     "extraversion": 0.17,
                     "agreeableness": 0.34,
                     "neuroticism": 0.22}

# This encodes your prior belief about how important physchometrics is compared
# to compatability you get by listening to the audio
HEURISTIC_PERSONALITY_WEIGHT = 0.7

# This encodes how much of an impact the length of the audio should have on the audio vs psychometric weighting
# i.e. longer audio tapes are more informative so should give audio more weighting.
# "weight" is the maximum penalty removed from the psychometric-based compatibility weighting
# "max_cap" is the number of words in the transcript at which point all additional words don't increase audio-based weighting
HEURISTIC_PERSONALITY_BONUS = {"weight": 0.2, "max_cap": 1500}

HEURISTIC_TOPIC_WEIGHTS = {"topic_centring": 0.4,
                            "topic_stretch_factor": 1.8,
                            "social_cue_bonus": 0.45,
                            "vader_cue_bonus": 0.1}


# How much openness and conscientiousness prioritise similairty over being generally high.
OPENNESS_SIMILARITY_WEIGHT = 0.2
CONSCIENTIOUSNESS_SIMILARITY_WEIGHT = 0.2

