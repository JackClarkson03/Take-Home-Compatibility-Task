LLM_MODEL_NAME = "gpt-3.5-turbo-1106"

FUSION_PERSONALITY_WEIGHT = 0.7

HEURISTIC_WEIGHTS = {"openness": 0.17,
                     "conscientiousness": 0.19,
                     "extraversion": 0.16,
                     "agreeableness": 0.29,
                     "neuroticism": 0.19}

# This encodes your prior belief about how important physchometrics is compared
# to compatability you get by listening to the audio
HEURISTIC_PERSONALITY_WEIGHT = 0.8

# This encodes how much of an impact the length of the audio should have on the audio vs physchometric weighting
# i.e. longer audio tapes are more informative so should give audio more weighting

HEURISTIC_TOPIC_WEIGHTS = {"topic_centring": 0.4,
                            "topic_stretch_factor": 1.8,
                            "social_cue_bonus": 0.2,
                            "vader_cue_bonus": 0.1}


