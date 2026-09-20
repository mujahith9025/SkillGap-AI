import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from data_loader import DataLoader
from skill_extractor import NLPSkillExtractor
from semantic_matcher import SemanticSkillMatcher
from ats_optimizer import ATSResumeOptimizer, ATSAuditResult, ATSRedFlag, BulletPointOptimization


class TestATSOptimizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.loader = DataLoader()
        cls.extractor = NLPSkillExtractor(data_loader=cls.loader)
        cls.semantic_matcher = SemanticSkillMatcher(data_loader=cls.loader)
        cls.optimizer = ATSResumeOptimizer(
            data_loader=cls.loader,
            skill_extractor=cls.extractor,
            semantic_matcher=cls.semantic_matcher
        )

    def test_01_evaluate_high_match_resume(self):
        """Resume with matching skills and metrics should score high ATS grade."""
        resume = (
            "Alex Chen - alex.chen@example.com - (555) 123-4567 - linkedin.com/in/alex - github.com/alex\n"
            "Technical Skills: Python, Pandas, SQL, Scikit-Learn\n"
            "Work Experience: Senior Data Scientist with 4 years experience. Engineered machine learning models using Python, "
            "Pandas, SQL, and Scikit-Learn. Optimized classification latency by 35% across 200,000 daily user records.\n"
            "Education: B.S. in Computer Science"
        )
        jd = (
            "Looking for a Data Scientist proficient in Python, SQL, Pandas, and Scikit-Learn. "
            "Experience with data preprocessing and classical machine learning required."
        )

        result = self.optimizer.evaluate_ats_compatibility(resume, jd, target_career="Data Scientist")
        self.assertIsInstance(result, ATSAuditResult)
        self.assertGreaterEqual(result.overall_ats_score, 65)
        self.assertIn("Python", result.matched_jd_keywords)
        self.assertIn("SQL", result.matched_jd_keywords)
        self.assertGreater(len(result.bullet_point_improvements), 0)
        self.assertGreater(len(result.red_flags), 0)
        self.assertTrue(result.tailored_latex_preview.startswith("%-------------------------"))
        self.assertIn("\\documentclass", result.tailored_latex_preview)
        self.assertIn("<!DOCTYPE html>", result.tailored_html_preview)

    def test_02_evaluate_low_match_resume(self):
        """Resume missing core JD skills should show critical missing keywords."""
        resume = "Junior developer familiar with HTML, CSS, and basic JavaScript."
        jd = "Seeking Senior Data Scientist with Python, PyTorch, Deep Learning, SQL, and Docker background."

        result = self.optimizer.evaluate_ats_compatibility(resume, jd)
        self.assertLess(result.overall_ats_score, 60)
        self.assertIn("Python", result.missing_critical_keywords)
        self.assertGreater(len(result.formatting_recommendations), 0)

    def test_03_scan_ats_red_flags_detection(self):
        """Red flag scanner should catch missing email, passive phrases, and low metrics."""
        flawed_resume = "Responsible for helping with data entry. Worked on some reports."
        flags = self.optimizer.scan_ats_red_flags(flawed_resume)

        categories = [f.category for f in flags]
        severities = [f.severity for f in flags]
        self.assertIn("Contact Info", categories)
        self.assertIn("Action Verbs", categories)
        self.assertIn("Metric Quantification", categories)
        self.assertIn("Critical", severities)

        # Clean resume should pass with Good flags
        clean_resume = (
            "Jane Doe | jane@example.com | (555) 987-6543 | linkedin.com/in/jane | github.com/jane\n"
            "Technical Skills: Python, SQL, Docker\n"
            "Experience: Architected distributed pipelines processing 500k records, improving speed by 40% with $50k savings.\n"
            "Education: Bachelor of Science"
        )
        clean_flags = self.optimizer.scan_ats_red_flags(clean_resume)
        critical_flags = [f for f in clean_flags if f.severity == "Critical"]
        self.assertEqual(len(critical_flags), 0)

    def test_04_compute_bullet_diff(self):
        """Word level delta diff should calculate added tokens and formatted HTML string."""
        orig = "Worked on python script for churn."
        imp = "Engineered automated classification pipeline using Python, achieving 94% accuracy."
        added, removed, html_diff = self.optimizer.compute_bullet_diff(orig, imp)

        self.assertIsInstance(added, list)
        self.assertIsInstance(removed, list)
        self.assertIn("Engineered", added)
        self.assertIn("accuracy", added)
        self.assertIn('<span class="diff-add">', html_diff)

    def test_05_xyz_rewrite_suggestion(self):
        """Rewriting bullet should return Google XYZ formatted bullet and diff metadata."""
        raw_bullet = "Created dashboard for sales team."
        rewrite = self.optimizer.suggest_xyz_rewrite(raw_bullet, missing_skill="Tableau")

        self.assertIn("optimized_bullet", rewrite)
        self.assertIn("Google XYZ Formula", rewrite["formula_applied"])
        self.assertIn("diff_added_tokens", rewrite)
        self.assertIn("highlighted_html_diff", rewrite)

    def test_06_generate_tailored_latex_resume(self):
        """LaTeX generator should produce valid Jake's Resume LaTeX code with injected keywords."""
        latex = self.optimizer.generate_tailored_latex_resume(
            student_skills=["Python", "SQL", "Pandas"],
            target_career="Machine Learning Engineer",
            job_description="Need PyTorch, Docker, and FastAPI experience",
            missing_keywords=["PyTorch", "FastAPI"],
            candidate_name="Samantha Ray"
        )
        self.assertIn("\\documentclass[letterpaper,11pt]{article}", latex)
        self.assertIn("Samantha Ray", latex)
        self.assertIn("Machine Learning Engineer", latex)
        self.assertIn("PyTorch", latex)
        self.assertIn("\\section{Technical Skills}", latex)
        self.assertIn("\\section{Experience}", latex)

    def test_07_generate_tailored_html_resume(self):
        """HTML resume generator should produce valid print-ready HTML."""
        html_code = self.optimizer.generate_tailored_html_resume(
            student_skills=["Python", "SQL"],
            target_career="Data Analyst",
            job_description="Requires Tableau and PowerBI",
            missing_keywords=["Tableau"],
            candidate_name="Marcus Vance"
        )
        self.assertIn("<!DOCTYPE html>", html_code)
        self.assertIn("Marcus Vance", html_code)
        self.assertIn("Data Analyst Resume", html_code)
        self.assertIn("@media print", html_code)


if __name__ == "__main__":
    unittest.main(verbosity=2)
