"""
End-to-End System Integration Test Suite
Phase 17: Integrate the Complete System

Validates that all pipeline layers communicate seamlessly:
Data -> Preprocessing -> NLP Extraction -> Skill Matching -> Gap Analysis -> Recommendation Engine -> Roadmap Generator -> Visual Analytics

Tests multiple diverse student personas and input formats.
"""

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


class IntegratedSkillRecommendationPipeline:
    """
    Unified façade that wraps the entire end-to-end pipeline:
    Raw Input (Text / List / PDF) -> Final Analysis, Recommendations & Visuals.
    """

    def __init__(self, data_dir: Path = None):
        self.loader = DataLoader(data_dir=data_dir)
        self.preprocessor = SkillPreprocessor(data_loader=self.loader)
        self.extractor = NLPSkillExtractor(data_loader=self.loader, preprocessor=self.preprocessor)
        self.matcher = SkillMatcher(data_loader=self.loader, preprocessor=self.preprocessor)
        self.gap_analyzer = SkillGapAnalyzer(data_loader=self.loader, skill_matcher=self.matcher)
        self.rec_engine = RecommendationEngine(data_loader=self.loader, gap_analyzer=self.gap_analyzer)
        self.roadmap_gen = RoadmapGenerator(data_loader=self.loader, recommendation_engine=self.rec_engine)
        self.resume_parser = ResumeParser(data_loader=self.loader, skill_extractor=self.extractor)

    def process_student_profile(
        self,
        raw_input: Any,
        target_career: str,
        input_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Executes the full pipeline from raw input to complete dashboard assets.
        """
        # 1. Extraction & Preprocessing
        if input_type == "resume_pdf":
            resume_profile = self.resume_parser.parse_resume(raw_input)
            extracted_skills = resume_profile.extracted_canonical_skills
            input_metadata = {
                "source": "PDF Resume",
                "valid_pdf": resume_profile.is_valid,
                "word_count": resume_profile.word_count,
                "sections": resume_profile.detected_sections
            }
        elif input_type == "text":
            extracted_skills = self.extractor.extract_canonical_names(raw_input)
            input_metadata = {"source": "Natural Language Text", "char_count": len(str(raw_input))}
        elif input_type == "skill_list":
            extracted_skills = self.preprocessor.normalize_skill_list(raw_input)
            input_metadata = {"source": "Structured Skill List", "input_count": len(raw_input)}
        else:
            raise ValueError(f"Unknown input_type: {input_type}")

        # 2. Skill Matching
        match_result = self.matcher.match_skills(extracted_skills, target_career)
        all_career_rankings = self.matcher.match_all_careers(extracted_skills)

        # 3. Gap Analysis
        gap_result = self.gap_analyzer.analyze_gaps(extracted_skills, target_career)

        # 4. Recommendation Engine
        rec_report = self.rec_engine.generate_recommendations(extracted_skills, target_career)

        # 5. Roadmap Generation
        roadmap = self.roadmap_gen.generate_roadmap(extracted_skills, target_career)

        # 6. Visual Analytics Assets
        fig_radar = VisualAnalyticsDashboard.create_category_radar_chart(match_result)
        fig_donut = VisualAnalyticsDashboard.create_matched_vs_missing_donut(match_result)
        fig_career_bar = VisualAnalyticsDashboard.create_career_comparison_bar(all_career_rankings)
        fig_gap_bar = VisualAnalyticsDashboard.create_gap_distribution_bar(gap_result)
        fig_matrix = VisualAnalyticsDashboard.create_interactive_matrix_heatmap(self.loader)

        return {
            "metadata": input_metadata,
            "extracted_skills": extracted_skills,
            "match_result": match_result,
            "all_career_rankings": all_career_rankings,
            "gap_result": gap_result,
            "rec_report": rec_report,
            "roadmap": roadmap,
            "visuals": {
                "radar": fig_radar,
                "donut": fig_donut,
                "career_bar": fig_career_bar,
                "gap_bar": fig_gap_bar,
                "matrix_heatmap": fig_matrix
            }
        }


class TestEndToEndIntegration(unittest.TestCase):
    """
    Validates end-to-end integration across multiple realistic student profiles.
    """

    @classmethod
    def setUpClass(cls):
        cls.pipeline = IntegratedSkillRecommendationPipeline()

    # -------------------------------------------------------------------------
    # PROFILE 1: Free-Text NLP Input -> Data Scientist
    # -------------------------------------------------------------------------
    def test_01_nlp_text_to_data_scientist(self):
        """Free-text NLP input should flow through extraction, matching, gaps, recs, and roadmap."""
        text = (
            "I have strong programming skills in Python and SQL. I regularly use Pandas and NumPy "
            "for data manipulation, and have built supervised models in Scikit-Learn."
        )
        out = self.pipeline.process_student_profile(text, "Data Scientist", input_type="text")

        # Verify Extraction
        self.assertIn("Python", out["extracted_skills"])
        self.assertIn("SQL", out["extracted_skills"])
        self.assertIn("Pandas", out["extracted_skills"])
        self.assertIn("NumPy", out["extracted_skills"])
        self.assertIn("Scikit-Learn", out["extracted_skills"])

        # Verify Matching
        match = out["match_result"]
        self.assertEqual(match.career_title, "Data Scientist")
        self.assertGreater(match.weighted_readiness_pct, 25.0)
        self.assertTrue(len(match.matched_skills) >= 4)

        # Verify Gaps & Prioritization
        gaps = out["gap_result"]
        self.assertTrue(len(gaps.learning_roadmap) > 0)
        self.assertTrue(len(gaps.high_priority_gaps) > 0)

        # Verify Recommendations & Projects
        rec = out["rec_report"]
        self.assertTrue(len(rec.milestones) > 0)
        self.assertTrue(len(rec.recommended_projects) > 0)

        # Verify Roadmap
        roadmap = out["roadmap"]
        self.assertIn("SEQUENTIAL LEARNING ROADMAP", roadmap.ascii_diagram)
        self.assertIn("graph TD", roadmap.mermaid_diagram)

        # Verify Visuals
        self.assertIsNotNone(out["visuals"]["radar"])
        self.assertIsNotNone(out["visuals"]["donut"])

    # -------------------------------------------------------------------------
    # PROFILE 2: PDF Resume Input -> Machine Learning Engineer
    # -------------------------------------------------------------------------
    def test_02_pdf_resume_to_ml_engineer(self):
        """PDF resume input should extract skills and generate an ML Engineer learning path."""
        resume_path = Path(__file__).resolve().parent.parent / "data" / "test_resumes" / "sample_data_scientist_resume.pdf"
        
        out = self.pipeline.process_student_profile(resume_path, "Machine Learning Engineer", input_type="resume_pdf")

        # Verify PDF Extraction
        self.assertTrue(out["metadata"]["valid_pdf"])
        self.assertGreater(len(out["extracted_skills"]), 3)

        # Verify Matching against ML Engineer
        match = out["match_result"]
        self.assertEqual(match.career_title, "Machine Learning Engineer")
        self.assertGreater(match.weighted_readiness_pct, 0.0)

        # Verify Multi-Career Ranking
        rankings = out["all_career_rankings"]
        self.assertEqual(len(rankings), 7)
        self.assertGreaterEqual(rankings[0].weighted_readiness_pct, rankings[-1].weighted_readiness_pct)

    # -------------------------------------------------------------------------
    # PROFILE 3: Slang / Synonyms Free-Text -> Business Analyst
    # -------------------------------------------------------------------------
    def test_03_synonyms_text_to_business_analyst(self):
        """Noisy terminology & aliases should normalize into canonical skills for Business Analyst."""
        text = "Experience with PostgreSQL queries, building Tablo reports, PowerBI visuals, and MS Excel pivot tables."
        out = self.pipeline.process_student_profile(text, "Business Analyst", input_type="text")

        # Canonical normalization check
        self.assertIn("SQL", out["extracted_skills"])
        self.assertIn("Tableau", out["extracted_skills"])
        self.assertIn("Power BI", out["extracted_skills"])
        self.assertIn("Excel", out["extracted_skills"])

        match = out["match_result"]
        self.assertGreater(match.weighted_readiness_pct, 40.0)
        self.assertEqual(match.career_title, "Business Analyst")

    # -------------------------------------------------------------------------
    # PROFILE 4: Structured Skill List -> Backend Developer
    # -------------------------------------------------------------------------
    def test_04_skill_list_to_backend_developer(self):
        """Structured skill list should connect directly with Backend Developer requirements."""
        skills = ["Python", "FastAPI", "SQL", "Docker", "Git & GitHub"]
        out = self.pipeline.process_student_profile(skills, "Backend Developer", input_type="skill_list")

        match = out["match_result"]
        self.assertEqual(match.career_title, "Backend Developer")
        self.assertGreater(match.weighted_readiness_pct, 35.0)

        # Verify that remaining gaps (e.g. Django, Linux, Relational DB Design) are prioritized
        gap_names = [s.skill_name for s in out["gap_result"].learning_roadmap]
        self.assertTrue(any("Django" in g or "Relational Database" in g or "Linux" in g for g in gap_names))

    # -------------------------------------------------------------------------
    # PROFILE 5: Absolute Beginner (Zero Skills) -> Data Analyst
    # -------------------------------------------------------------------------
    def test_05_beginner_zero_skills_to_data_analyst(self):
        """Zero initial skills should produce a 0% match with a full foundation roadmap."""
        out = self.pipeline.process_student_profile("", "Data Analyst", input_type="text")

        match = out["match_result"]
        self.assertEqual(match.weighted_readiness_pct, 0.0)
        self.assertEqual(len(match.matched_skills), 0)
        self.assertEqual(len(match.missing_skills), len(match.required_skills))

        # First milestone should start with beginner fundamentals
        rec = out["rec_report"]
        first_phase_skills = [s.skill_name for s in rec.milestones[0].skills]
        # In-degree 0 beginner skills like Python, SQL, Excel should appear in Phase 1
        self.assertTrue(any(s in ["Python", "SQL", "Excel", "Statistics & Probability"] for s in first_phase_skills))


def run_integration_tests():
    """Executes the end-to-end integration test suite."""
    print("=" * 80)
    print(" PHASE 17: COMPLETE SYSTEM INTEGRATION & END-TO-END PIPELINE TEST")
    print("=" * 80)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEndToEndIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print(f" ALL {result.testsRun} END-TO-END INTEGRATION TESTS PASSED (0 Failures, 0 Errors)")
        print(" Data -> Preprocessing -> Extraction -> Matching -> Gaps -> Recommendations -> Roadmap -> UI Visuals")
        print(" Complete component-to-component interoperability verified.")
    else:
        print(f" INTEGRATION FAILED: {len(result.failures)} Failures, {len(result.errors)} Errors")
    print("=" * 80)
    return result.wasSuccessful()


if __name__ == "__main__":
    run_integration_tests()
