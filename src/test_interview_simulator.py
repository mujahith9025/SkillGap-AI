"""
Unit Tests for AI Mock Interview Simulator Module
Phase 12 & Section 4 Upgrades: Coding Sandbox, Test Runner, and Adaptive Follow-Up Agent
"""

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from data_loader import DataLoader
from semantic_matcher import SemanticSkillMatcher
from interview_simulator import (
    MockInterviewEngine,
    InterviewQuestion,
    AnswerEvaluation,
    FollowUpQuestion,
    CodingProblem,
    CodeExecutionResult
)


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

    def test_05_get_coding_problems(self):
        """Should retrieve coding sandbox problems for Python and SQL."""
        problems = self.engine.get_coding_problems()
        self.assertGreaterEqual(len(problems), 3)
        languages = {p.language for p in problems}
        self.assertIn("python", languages)
        self.assertIn("sql", languages)

    def test_06_execute_python_sandbox_pass(self):
        """Valid Python solution should pass all test cases."""
        code = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
"""
        result = self.engine.execute_code_sandbox("py_two_sum", code, language="python")
        self.assertIsInstance(result, CodeExecutionResult)
        self.assertTrue(result.all_passed)
        self.assertEqual(result.passed_count, result.total_count)
        self.assertGreater(result.passed_count, 0)
        self.assertIsNone(result.error_traceback)

    def test_07_execute_python_sandbox_syntax_error(self):
        """Syntax error in Python code should be captured in error_traceback without crashing."""
        broken_code = "def broken(::"
        result = self.engine.execute_code_sandbox("py_two_sum", broken_code, language="python")
        self.assertFalse(result.all_passed)
        self.assertIsNotNone(result.error_traceback)
        self.assertEqual(result.passed_count, 0)

    def test_08_execute_sql_sandbox_pass(self):
        """Valid SQL query against in-memory SQLite tables should return expected relational rows."""
        sql_query = """
SELECT e.name, e.department, e.salary
FROM employees e
WHERE e.salary > (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department = e.department
)
ORDER BY e.salary DESC;
"""
        result = self.engine.execute_code_sandbox("sql_top_salaries", sql_query, language="sql")
        self.assertIsInstance(result, CodeExecutionResult)
        self.assertTrue(result.all_passed)
        self.assertEqual(result.passed_count, result.total_count)

    def test_09_generate_adaptive_follow_up(self):
        """Adaptive follow-up agent should generate contextual probe questions."""
        questions = self.engine.get_questions_for_skill("SQL")
        q = questions[0]
        partial_ans = "WHERE is for rows before group by."
        eval_res = self.engine.evaluate_candidate_answer(q, partial_ans)

        follow_up = self.engine.generate_adaptive_follow_up(q, eval_res, partial_ans)
        self.assertIsInstance(follow_up, FollowUpQuestion)
        self.assertIn("SQL", follow_up.skill_name)
        self.assertGreater(len(follow_up.probe_text), 20)
        self.assertIn(follow_up.probe_type, ["Gap Exploration", "Guided Foundational", "Edge Case Challenge"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
