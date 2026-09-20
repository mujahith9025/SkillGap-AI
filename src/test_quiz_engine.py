"""
Unit Tests for Quiz Engine Module
Verifies question retrieval, option formatting, exact scoring, passing gates, and failure handling.
"""

import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from quiz_engine import QuizEngine, QuizQuestion, QuizResult


class TestQuizEngine:
    @classmethod
    def setup_class(cls):
        cls.engine = QuizEngine()

    def test_01_get_quiz_for_known_skill(self):
        questions = self.engine.get_quiz_for_skill("Python", num_questions=3)
        assert len(questions) == 3
        for q in questions:
            assert isinstance(q, QuizQuestion)
            assert len(q.options) >= 3
            assert 0 <= q.correct_option_index < len(q.options)
            assert len(q.explanation) > 10

    def test_02_get_quiz_for_sql_skill(self):
        questions = self.engine.get_quiz_for_skill("SQL", num_questions=3)
        assert len(questions) == 3
        assert any("WHERE" in q.question_text or "Window" in q.question_text or "Index" in q.question_text for q in questions)

    def test_03_get_quiz_fallback_for_generic_skill(self):
        questions = self.engine.get_quiz_for_skill("Kubernetes Cluster Orchestration", num_questions=3)
        assert len(questions) == 3

    def test_04_evaluate_perfect_score(self):
        questions = self.engine.get_quiz_for_skill("Python", num_questions=3)
        correct_answers = [q.correct_option_index for q in questions]
        result = self.engine.evaluate_quiz("Python", correct_answers)
        
        assert isinstance(result, QuizResult)
        assert result.score == 3
        assert result.total_questions == 3
        assert result.percentage == 100.0
        assert result.passed is True
        assert "Mastery Verified" in result.feedback

    def test_05_evaluate_passing_two_out_of_three(self):
        questions = self.engine.get_quiz_for_skill("Machine Learning", num_questions=3)
        answers = [questions[0].correct_option_index, questions[1].correct_option_index, 99]  # 2 correct, 1 wrong
        result = self.engine.evaluate_quiz("Machine Learning", answers)
        
        assert result.score == 2
        assert result.passed is True
        assert round(result.percentage) == 67

    def test_06_evaluate_failing_score(self):
        questions = self.engine.get_quiz_for_skill("Python", num_questions=3)
        wrong_answers = [99, 99, 99]
        result = self.engine.evaluate_quiz("Python", wrong_answers)
        
        assert result.score == 0
        assert result.passed is False
        assert result.percentage == 0.0
        assert "Quiz Not Passed" in result.feedback
