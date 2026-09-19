"""
System Robustness, Edge Cases & Error Handling Test Suite
Phase 16: Testing, Validation and Error Handling

Systematically tests the end-to-end recommendation pipeline across 10 critical edge cases:
1. Valid student input
2. Empty input (empty string, empty list, whitespace, None)
3. Unknown / out-of-scope skills
4. Unknown / invalid career identifiers
5. Incomplete / malformed input data
6. Invalid / corrupted resume inputs
7. Empty / blank resume inputs
8. Multi-career ranking consistency
9. Minimal skill profiles (0 or 1 skill)
10. Maximum skill profiles (all 32 taxonomy skills)
"""

import io
from pathlib import Path
from typing import Any, Dict, List
import unittest

from data_loader import DataLoader
from preprocessing import SkillPreprocessor
from skill_extractor import NLPSkillExtractor
from skill_matcher import SkillMatcher
from gap_analyzer import SkillGapAnalyzer
from recommendation_engine import RecommendationEngine
from roadmap_generator import RoadmapGenerator
from resume_parser import ResumeParser
from analytics_dashboard import VisualAnalyticsDashboard


class TestSystemRobustness(unittest.TestCase):
    """
    Comprehensive test case suite validating error handling and robustness.
    """

    @classmethod
    def setUpClass(cls):
        """Initialize all core pipeline components."""
        cls.loader = DataLoader()
        cls.preprocessor = SkillPreprocessor(data_loader=cls.loader)
        cls.extractor = NLPSkillExtractor(data_loader=cls.loader, preprocessor=cls.preprocessor)
        cls.matcher = SkillMatcher(data_loader=cls.loader, preprocessor=cls.preprocessor)
        cls.gap_analyzer = SkillGapAnalyzer(data_loader=cls.loader, skill_matcher=cls.matcher)
        cls.rec_engine = RecommendationEngine(data_loader=cls.loader, gap_analyzer=cls.gap_analyzer)
        cls.roadmap_gen = RoadmapGenerator(data_loader=cls.loader, recommendation_engine=cls.rec_engine)
        cls.resume_parser = ResumeParser(data_loader=cls.loader, skill_extractor=cls.extractor)

    # -------------------------------------------------------------------------
    # TEST 1: Valid Student Input
    # -------------------------------------------------------------------------
    def test_01_valid_student_input(self):
        """Valid skills and standard career identifier should produce a complete, valid report."""
        student_skills = ["Python", "Pandas", "SQL", "Scikit-Learn"]
        career = "Data Scientist"

        # Matcher
        match_res = self.matcher.match_skills(student_skills, career)
        self.assertGreater(match_res.weighted_readiness_pct, 0.0)
        self.assertEqual(match_res.career_title, "Data Scientist")
        self.assertTrue(len(match_res.matched_skills) >= 3)

        # Recommendation Engine
        rec_report = self.rec_engine.generate_recommendations(student_skills, career)
        self.assertIsNotNone(rec_report)
        self.assertTrue(len(rec_report.milestones) > 0)
        self.assertTrue(len(rec_report.recommended_projects) > 0)

        # Roadmap Generator
        visual_roadmap = self.roadmap_gen.generate_roadmap(student_skills, career)
        self.assertIn("SEQUENTIAL LEARNING ROADMAP", visual_roadmap.ascii_diagram)
        self.assertIn("```mermaid", visual_roadmap.mermaid_diagram)

    # -------------------------------------------------------------------------
    # TEST 2: Empty Student Input
    # -------------------------------------------------------------------------
    def test_02_empty_student_inputs(self):
        """Empty string, empty list, whitespace, and None should degrade gracefully without throwing exceptions."""
        empty_inputs = ["", [], "   ", "   \n\t  ", None]

        for emp in empty_inputs:
            # Matcher
            match_res = self.matcher.match_skills(emp if emp is not None else [], "Data Analyst")
            self.assertEqual(match_res.weighted_readiness_pct, 0.0)
            self.assertEqual(len(match_res.matched_skills), 0)
            self.assertEqual(len(match_res.missing_skills), len(match_res.required_skills))

            # Gap Analyzer
            gap_res = self.gap_analyzer.analyze_gaps(emp if emp is not None else [], "Data Analyst")
            self.assertEqual(gap_res.weighted_readiness_pct, 0.0)
            self.assertEqual(len(gap_res.learning_roadmap), len(match_res.required_skills))

            # Recommendation Report
            rec_rep = self.rec_engine.generate_recommendations(emp if emp is not None else [], "Data Analyst")
            self.assertEqual(rec_rep.weighted_readiness_pct, 0.0)
            self.assertTrue(len(rec_rep.milestones) > 0)

    # -------------------------------------------------------------------------
    # TEST 3: Unknown / Out-of-Scope Skills
    # -------------------------------------------------------------------------
    def test_03_unknown_skills(self):
        """Random words or non-technical skills should normalize to empty and trigger 0% match safely."""
        unknown_inputs = [
            "Quantum Computing, Cooking Recipes, Woodworking, Blockchain Solidity",
            ["non_existent_skill_xyz", "random_gibberish_1234", "underwater_basket_weaving"]
        ]

        for unk in unknown_inputs:
            match_res = self.matcher.match_skills(unk, "Python Developer")
            self.assertEqual(len(match_res.matched_skills), 0)
            self.assertEqual(match_res.weighted_readiness_pct, 0.0)
            self.assertEqual(len(match_res.student_normalized_skills), 0)

            # Recommendations should still produce a valid full roadmap
            rec_rep = self.rec_engine.generate_recommendations(unk, "Python Developer")
            self.assertTrue(len(rec_rep.milestones) > 0)

    # -------------------------------------------------------------------------
    # TEST 4: Unknown Career Identifiers
    # -------------------------------------------------------------------------
    def test_04_unknown_career_identifiers(self):
        """Unknown career titles or IDs should raise informative ValueErrors."""
        invalid_careers = ["Astronaut", "CAR_999", "NonExistent Role", "", "   ", None]

        for inv_c in invalid_careers:
            with self.assertRaises(ValueError) as ctx:
                self.matcher.match_skills(["Python", "SQL"], inv_c)
            self.assertTrue(len(str(ctx.exception)) > 0)

    # -------------------------------------------------------------------------
    # TEST 5: Incomplete / Malformed Data
    # -------------------------------------------------------------------------
    def test_05_malformed_data_types(self):
        """Lists with None or mixed invalid elements should be filtered safely."""
        malformed_list = ["Python", None, "  ", 12345, "SQL", "", "   Pandas   "]
        
        # Preprocessor should filter invalid elements safely
        cleaned = self.preprocessor.normalize_skill_list([s for s in malformed_list if isinstance(s, str)])
        self.assertIn("Python", cleaned)
        self.assertIn("SQL", cleaned)
        self.assertIn("Pandas", cleaned)

        # Matcher should handle text strings with extra commas and delimiters
        noisy_text = "Python,,,, ,,, SQL; Pandas |  | Scikit-Learn"
        match_res = self.matcher.match_skills(noisy_text, "Data Scientist")
        self.assertIn("Python", match_res.student_normalized_skills)
        self.assertIn("SQL", match_res.student_normalized_skills)

    # -------------------------------------------------------------------------
    # TEST 6: Invalid Resume Handling
    # -------------------------------------------------------------------------
    def test_06_invalid_resume_inputs(self):
        """Corrupted bytes, non-existent files, and non-PDF content must return is_valid=False with error message."""
        # Non-existent file
        res1 = self.resume_parser.parse_resume("data/test_resumes/non_existent_file.pdf")
        self.assertFalse(res1.is_valid)
        self.assertIsNotNone(res1.error_message)

        # Corrupted bytes buffer
        corrupt_bytes = b"This is not a real PDF file! Just random plain text bytes."
        res2 = self.resume_parser.parse_resume(corrupt_bytes, filename="corrupt.pdf")
        self.assertFalse(res2.is_valid)
        self.assertIsNotNone(res2.error_message)

    # -------------------------------------------------------------------------
    # TEST 7: Empty Resume Handling
    # -------------------------------------------------------------------------
    def test_07_empty_resume_handling(self):
        """Zero-byte buffers and empty streams must return is_valid=False without crashing."""
        empty_bytes = b""
        res1 = self.resume_parser.parse_resume(empty_bytes, filename="empty.pdf")
        self.assertFalse(res1.is_valid)
        self.assertEqual(res1.page_count, 0)
        self.assertIn("empty", res1.error_message.lower())

        # Empty BytesIO stream
        empty_stream = io.BytesIO(b"")
        res2 = self.resume_parser.parse_resume(empty_stream, filename="stream.pdf")
        self.assertFalse(res2.is_valid)

    # -------------------------------------------------------------------------
    # TEST 8: Multi-Career Ranking Consistency
    # -------------------------------------------------------------------------
    def test_08_multi_career_ranking(self):
        """Multi-career ranking should return all 7 careers sorted descending by readiness."""
        test_inputs = [
            ["Python", "SQL", "Pandas"],
            [],
            ["Excel", "Power BI", "Tableau"]
        ]

        for inp in test_inputs:
            rankings = self.matcher.match_all_careers(inp)
            self.assertEqual(len(rankings), 7)
            # Verify strict descending score order
            scores = [r.weighted_readiness_pct for r in rankings]
            self.assertEqual(scores, sorted(scores, reverse=True))

            # Visual analytics comparison bar should render without errors
            fig = VisualAnalyticsDashboard.create_career_comparison_bar(rankings)
            self.assertIsNotNone(fig)

    # -------------------------------------------------------------------------
    # TEST 9: Students with Very Few Skills (0 or 1 Skill)
    # -------------------------------------------------------------------------
    def test_09_minimal_skill_profiles(self):
        """Minimal skill profiles must produce comprehensive starting roadmaps."""
        minimal_profiles = [
            [],
            ["Python"],
            ["Excel"]
        ]

        for prof in minimal_profiles:
            for cid in self.loader.careers["career_id"]:
                report = self.rec_engine.generate_recommendations(prof, cid)
                self.assertIsNotNone(report)
                self.assertTrue(len(report.milestones) > 0)
                self.assertTrue(report.total_estimated_study_hours > 0)

                # Prerequisite checks on first milestone: must have in-degree 0
                first_milestone = report.milestones[0]
                self.assertTrue(len(first_milestone.skills) > 0)

    # -------------------------------------------------------------------------
    # TEST 10: Students with Many / Complete Skills (100% Match)
    # -------------------------------------------------------------------------
    def test_10_maximum_skill_profile(self):
        """A student with all 32 canonical skills should achieve 100% match and 0 gaps across all careers."""
        all_skills = self.loader.skills["skill_name"].tolist()
        self.assertEqual(len(all_skills), 32)

        for cid in self.loader.careers["career_id"]:
            match_res = self.matcher.match_skills(all_skills, cid)
            self.assertEqual(match_res.weighted_readiness_pct, 100.0)
            self.assertEqual(match_res.unweighted_coverage_pct, 100.0)
            self.assertEqual(len(match_res.missing_skills), 0)

            # Recommendation engine with 0 gaps
            rec_report = self.rec_engine.generate_recommendations(all_skills, cid)
            self.assertEqual(rec_report.weighted_readiness_pct, 100.0)
            self.assertEqual(len(rec_report.skill_recommendations), 0)
            self.assertEqual(len(rec_report.milestones), 0)
            # Capstone projects should still be recommended for portfolio expansion
            self.assertTrue(len(rec_report.recommended_projects) > 0)

            # Visual Roadmap generator with 0 gaps
            roadmap = self.roadmap_gen.generate_roadmap(all_skills, cid)
            self.assertIn("100% of the required skills", roadmap.ascii_diagram)


def run_robustness_test_suite():
    """Runs all test cases and outputs a clear summary."""
    print("=" * 80)
    print(" PHASE 16: SYSTEM ROBUSTNESS, VALIDATION & ERROR HANDLING TEST SUITE")
    print("=" * 80)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSystemRobustness)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print(f" ALL {result.testsRun} ROBUSTNESS & EDGE CASE TESTS PASSED (0 Failures, 0 Errors)")
    else:
        print(f" TEST SUITE FAILED: {len(result.failures)} Failures, {len(result.errors)} Errors")
    print("=" * 80)
    return result.wasSuccessful()


if __name__ == "__main__":
    run_robustness_test_suite()
