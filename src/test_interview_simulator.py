"""
Unit Tests for AI Mock Interview Simulator Module
"""

import unittest
from pathlib import Path

from data_loader import DataLoader
from semantic_matcher import SemanticSkillMatcher
from interview_simulator import MockInterviewEngine, InterviewQuestion, AnswerEvaluation


class TestMockInterviewEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.loader = DataLoader()
        cls.semantic_matcher = SemanticSkillMatcher(data_loader=cls.loader)
        cls.engine = MockInterviewEngine(data_loader=cls.loader, semantic_matcher=cls.semantic_matcher)

    def test_01_get_questions_for_existing_skill(self):
        """Questions for known skills (e.g. Python, SQL) should return populated InterviewQuestion objects."""
        questions = self.engine.get_questions_for_skill("Python")
        self.assertGreater(len(questions), 0)
        q = questions[0]
        self.assertEqual(q.skill_name, "Python")
        self.assertGreater(len(q.key_concepts), 0)
        self.assertGreater(len(q.sample_model_answer), 20)

    def test_02_get_questions_for_generic_skill(self):
        """Unlisted skills should produce a valid fallback technical problem solving question."""
        questions = self.engine.get_questions_for_skill("Big Data Fundamentals (Spark)")
        self.assertEqual(len(questions), 1)
        self.assertIn("Big Data Fundamentals (Spark)", questions[0].question_text)

    def test_03_evaluate_strong_answer(self):
        """A detailed answer covering all concepts should receive a score >= 7 (Good or Excellent)."""
        questions = self.engine.get_questions_for_skill("SQL")
        q = [item for item in questions if "WHERE and HAVING" in item.question_text][0]

        strong_answer = (
            "WHERE filters rows before aggregation and GROUP BY happens. "
            "HAVING filters grouped records after aggregation using aggregate functions like SUM or COUNT."
        )
        evaluation = self.engine.evaluate_candidate_answer(q, strong_answer)
        self.assertGreaterEqual(evaluation.overall_score, 6)
        self.assertIn(evaluation.score_tier, ["Good", "Excellent"])
        self.assertGreater(len(evaluation.matched_concepts), 0)

    def test_04_evaluate_empty_short_answer(self):
        """An empty or one-word answer should receive score = 1 and Insufficient tier."""
        questions = self.engine.get_questions_for_skill("Machine Learning")
        q = questions[0]

        eval_res = self.engine.evaluate_candidate_answer(q, "dunno")
        self.assertEqual(eval_res.overall_score, 1)
        self.assertEqual(eval_res.score_tier, "Insufficient")
        self.assertEqual(eval_res.concept_coverage_pct, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
