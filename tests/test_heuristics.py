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

    # Individual Trait Scoring Tests

    def test_scaled_euclidean_similarity(self):
        """
        Tests that identical vectors are similar and opposite vectors are not.
        """
        self.assertAlmostEqual(_scaled_euclidean_similarity([0.5]*5, [0.5]*5), 1.0, "Identical vectors should have similarity of 1.0.")
        self.assertLess(_scaled_euclidean_similarity([0.0]*5, [1.0]*5), 0.5, "Opposite vectors should have low similarity.")
        self.assertAlmostEqual(_scaled_euclidean_similarity([1.0]*5, [0.0]*5), _scaled_euclidean_similarity([0.0]*5, [1.0]*5), "Order should not matter.")


    def test_openness_scoring(self):
        """
        High openness in both partners is best. Similar but low is bad but not awful.
        """
        self.assertGreater(_score_openness(0.9, 0.9), 0.8, "Two highly open people should score high.")
        self.assertLess(_score_openness(0.1, 0.1), 0.35, "Two people with low openness should score low.")
        self.assertGreater(_score_openness(0.9, 0.9), _score_openness(0.5, 0.5), "Higher average openness should yield a higher score.")


    def test_conscientiousness_scoring(self):
        """
        High conscientiousness in both partners is best. Similar but low is bad but not awful.
        """
        self.assertGreater(_score_conscientiousness(0.9, 0.9), 0.8, "Two highly conscientious people should score high.")
        self.assertLess(_score_conscientiousness(0.1, 0.1), 0.35, "Two people with low conscientiousness should score low.")
        self.assertGreater(_score_conscientiousness(0.9, 0.9), _score_conscientiousness(0.5, 0.5), "Higher average conscientiousness should score higher.")


    def test_extraversion_scoring(self):
        """
        A balance of introversion and extraversion is best.
        """
        self.assertAlmostEqual(_score_extraversion(0.0, 1.0), 1.0, delta=0.01, msg="A pure introvert and extravert should be a perfect complementary match.")
        self.assertAlmostEqual(_score_extraversion(0.5, 0.5), 1.0, delta=0.01, msg="Two ambiverts should be a match.")
        self.assertLess(_score_extraversion(0.9, 0.9), 0.2, "Two strong extraverts should not be a complementary match.")
        self.assertLess(_score_extraversion(0.1, 0.1), 0.2, "Two strong introverts should not be a complementary match.")


    def test_agreeableness_scoring(self):
        """
        High agreeableness in both partners is best. Low agreeableness is penalized.
        """
        self.assertGreater(_score_agreeableness(0.9, 0.9), 0.85, "Two highly agreeable people should score high.")
        self.assertLess(_score_agreeableness(0.1, 0.1), 0.2, "Two highly disagreeable people should be penalized and score low.")
        self.assertTrue(0.4 < _score_agreeableness(0.5, 0.9) < 0.7, "A moderate and high agreeable person should have a moderate score.")


    def test_neuroticism_scoring(self):
        """
        Low neuroticism in both partners is best. High neuroticism is penalized.
        """
        self.assertGreater(_score_neuroticism(0.1, 0.1), 0.85, "Two emotionally stable people should score high.")
        self.assertLess(_score_neuroticism(0.9, 0.9), 0.2, "Two highly neurotic people should be penalized and score low.")
        self.assertTrue(0.4 < _score_neuroticism(0.5, 0.1) < 0.7, "A moderate and a stable person should have a moderate-to-high score.")



    # Test Overall Heuristic Scores
    def setUp(self):
        """Defines personality archetypes for testing overall score."""
        # Open, Conscientious, Extraverted, Agreeable, Not Neurotic
        self.persona_ideal_partner = [0.9, 0.8, 0.7, 0.9, 0.1]
        # Open, Conscientious, Introverted, Agreeable, Not Neurotic
        self.persona_ideal_complement = [0.9, 0.8, 0.2, 0.9, 0.1]
        # Low Openness, Low Conscientiousness, High Extraversion, Low Agreeableness, High Neuroticism
        self.persona_volatile = [0.4, 0.3, 0.9, 0.2, 0.8]
        # High Openness, High Conscientiousness, High Extraversion, Low Agreeableness, Low Neuroticism
        self.persona_argumentative = [0.7, 0.7, 0.7, 0.1, 0.2]

        self.mock_analysis_results = {
            "topic_vector": [0.9, 0.7, 0.3, 0.4, 0.6],
            "engagement_score": 0.75,
            "vader_engagement": 0.0,
            "word_count": 750}

    def test_ideal_match_score_is_high(self):
        """
        Tests the pair who are similar and stable.
        """
        result = calculate_heuristic_score(self.persona_ideal_partner, self.persona_ideal_complement, self.mock_analysis_results)
        self.assertGreater(result["match_score"], 0.7, "Ideal match score should be high")
        # print(f"\nIdeal Match Score: {result['match_score']:.2f}")

    def test_volatile_clash_score_is_low(self):
        """
        Tests two volatile individuals who should not be compatible.
        """
        result = calculate_heuristic_score(self.persona_volatile, self.persona_volatile, self.mock_analysis_results)
        self.assertLess(result["match_score"], 0.4, "Volatile clash score should be low")
        # print(f"Volatile Clash Score: {result['match_score']:.2f}")

    def test_argumentative_clash_score_is_low(self):
        """
        Tests two argumentative individuals who are likely to clash on agreeableness.
        """
        result = calculate_heuristic_score(self.persona_argumentative, self.persona_argumentative, self.mock_analysis_results)
        print(f"Argumentative Clash Score: {result['match_score']:.2f}")
        self.assertLess(result["match_score"], 0.55, "Argumentative clash score should be low/mid")
        
        
    def test_identical_average_personas(self):
        """
        Tests that two perfectly average people result in a middling score.
        """
        persona_avg = [0.5] * 5
        result = calculate_heuristic_score(persona_avg, persona_avg, self.mock_analysis_results)
        print(f"Average identical score: {result['match_score']:.2f}")
        self.assertTrue(0.35 < result["match_score"] < 0.65, "Two 'average' people should have a medium score.")
        


if __name__ == '__main__':
    unittest.main()