import unittest
import numpy as np
import sys
import os

# Import Heuristic Score Functions
from src.heuristics import (
    _score_openness,
    _score_conscientiousness,
    _score_extraversion,
    _score_agreeableness,
    _score_neuroticism,
    _scaled_euclidean_similarity,
    calculate_heuristic_score 
)

class TestHeuristicFunctions(unittest.TestCase):

    # Individual Score Functions

    def test_scaled_euclidean_similarity(self):
        self.assertAlmostEqual(_scaled_euclidean_similarity([0.5]*5, [0.5]*5), 1.0, delta=0.01)
        self.assertLess(_scaled_euclidean_similarity([0.0]*5, [1.0]*5), 0.5, "Opposite vectors should have low similarity")

    def test_openness_scoring(self):
        # High similarity, high avg = high score
        self.assertGreater(_score_openness(0.9, 0.9), 0.8)
        # High similarity, low avg = mid score
        self.assertLess(_score_openness(0.1, 0.1), 0.5)
        # Low similarity = lower score
        self.assertLess(_score_openness(0.1, 0.9), 0.6)

    def test_conscientiousness_scoring(self):
        # High similarity, high avg = high score
        self.assertGreater(_score_conscientiousness(0.9, 0.9), 0.8)
        # High similarity, low avg = mid score
        self.assertLess(_score_conscientiousness(0.1, 0.1), 0.5)
        # Low similarity = lower score
        self.assertLess(_score_conscientiousness(0.1, 0.9), 0.6)

    def test_extraversion_scoring(self):
        # Max complementarity = high score
        self.assertAlmostEqual(_score_extraversion(0.0, 1.0), 1.0, delta=0.01)
        # No complementarity = low score
        self.assertAlmostEqual(_score_extraversion(0.5, 0.5), 0.0, delta=0.01)

    def test_agreeableness_scoring(self):
        # Both high = high score
        self.assertGreater(_score_agreeableness(0.9, 0.9), 0.85)
        # Both low = low score (due to penalty)
        self.assertLess(_score_agreeableness(0.1, 0.1), 0.2)
        # One high, one low = mid score
        self.assertAlmostEqual(_score_agreeableness(0.1, 0.9), 0.5, delta=0.1)

    def test_neuroticism_scoring(self):
        # Both low = high score (high stability)
        self.assertGreater(_score_neuroticism(0.1, 0.1), 0.85)
        # Both high = low score (low stability, high penalty)
        self.assertLess(_score_neuroticism(0.9, 0.9), 0.2)
        # One high, one low = mid score
        self.assertAlmostEqual(_score_neuroticism(0.1, 0.9), 0.5, delta=0.1)



    # Test Overall Heuristic Score for Edge Cases

    def setUp(self):
        self.persona_ideal_match_1 = [0.9, 0.8, 0.7, 0.9, 0.1]
        self.persona_ideal_match_2 = [0.9, 0.8, 0.2, 0.9, 0.1]
        self.persona_volatile_clash = [0.4, 0.3, 0.9, 0.2, 0.8]
        self.persona_argumentative = [0.8, 0.8, 0.7, 0.1, 0.2]

        self.mock_analysis_results = {
            "topic_vector": [0.9, 0.7, 0.3, 0.4, 0.6],
            "engagement_score": 0.75}

    def test_ideal_match_score_is_high(self):
        result = calculate_heuristic_score(self.persona_ideal_match_1, self.persona_ideal_match_2, self.mock_analysis_results, 0.0)
        self.assertGreater(result["match_score"], 0.7, "Ideal match score should be high")
        print(f"\nIdeal Match Score: {result['match_score']:.2f}")

    def test_volatile_clash_score_is_low(self):
        result = calculate_heuristic_score(self.persona_volatile_clash, self.persona_volatile_clash, self.mock_analysis_results, 0.0)
        self.assertLess(result["match_score"], 0.4, "Volatile clash score should be low")
        print(f"Volatile Clash Score: {result['match_score']:.2f}")

    def test_argumentative_clash_score_is_low(self):
        result = calculate_heuristic_score(self.persona_argumentative, self.persona_argumentative, self.mock_analysis_results, 0.0)
        self.assertLess(result["match_score"], 0.5, "Argumentative clash score should be low/mid")
        print(f"Argumentative Clash Score: {result['match_score']:.2f}")


if __name__ == '__main__':
    unittest.main()