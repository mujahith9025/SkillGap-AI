import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from data_loader import DataLoader
from skill_extractor import NLPSkillExtractor
from job_market_scraper import (
    JobMarketScraper, MarketIntelligenceReport, DynamicSkillWeight,
    SalaryEstimationReport, TechHubHiringStats, SkillVelocityMetric
)



class TestJobMarketScraper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.loader = DataLoader()
        cls.extractor = NLPSkillExtractor(data_loader=cls.loader)
        cls.scraper = JobMarketScraper(data_loader=cls.loader, skill_extractor=cls.extractor)

    def test_01_fetch_job_postings(self):
        """Job postings should be parsed and contain extracted technical skills."""
        postings = self.scraper.fetch_live_job_postings()
        self.assertGreater(len(postings), 5)
        first_p = postings[0]
        self.assertTrue(len(first_p.title) > 0)
        self.assertTrue(len(first_p.company) > 0)
        self.assertGreater(len(first_p.extracted_skills), 0)

    def test_02_generate_market_intelligence_report(self):
        """Market intelligence report should aggregate frequencies across all 7 careers."""
        report = self.scraper.generate_market_intelligence_report()
        self.assertIsInstance(report, MarketIntelligenceReport)
        self.assertGreater(report.total_postings_analyzed, 5)
        self.assertEqual(len(report.career_reports), 7)
        self.assertTrue(len(report.top_market_skills) > 0)
        self.assertTrue(len(report.emerging_skills) > 0)

    def test_03_recalculate_readiness_with_live_weights(self):
        """Dynamic readiness calculation should return valid percentages and comparative breakdown."""
        student_skills = ["Python", "SQL", "Pandas", "Scikit-Learn"]
        career = "Data Scientist"

        static_pct, live_pct, comparisons = self.scraper.recalculate_readiness_with_live_weights(
            student_skills, career
        )
        self.assertGreater(static_pct, 0.0)
        self.assertGreater(live_pct, 0.0)
        self.assertLessEqual(static_pct, 100.0)
        self.assertLessEqual(live_pct, 100.0)
        self.assertGreater(len(comparisons), 5)

    def test_04_estimate_compensation_high_skills(self):
        """Should estimate salary accurately with matched skill boosts."""
        skills = ["Python", "SQL", "Pandas", "Scikit-Learn", "PyTorch", "Docker"]
        report = self.scraper.estimate_compensation(skills, target_career="Data Scientist")
        self.assertEqual(report.target_career, "Data Scientist")
        self.assertGreater(report.current_salary_usd, report.baseline_entry_salary_usd * 0.7)
        self.assertGreater(report.current_salary_inr_lpa, 15.0)
        self.assertGreater(report.max_potential_salary_usd, report.current_salary_usd)
        self.assertGreaterEqual(report.matched_skills_count, 4)

    def test_05_estimate_compensation_skill_deltas(self):
        """Missing skills should produce ranked marginal ROI deltas."""
        skills = ["Python", "SQL"]
        report = self.scraper.estimate_compensation(skills, target_career="Data Scientist")
        self.assertGreater(len(report.missing_skills), 0)
        self.assertGreater(len(report.skill_value_deltas), 0)
        # First delta should have highest salary delta
        top_delta = report.skill_value_deltas[0]
        self.assertEqual(top_delta.roi_rank, 1)
        self.assertGreater(top_delta.salary_delta_usd, 0)
        self.assertGreater(top_delta.salary_delta_inr_lpa, 0.0)
        self.assertTrue(len(report.top_salary_boost_skills) > 0)

    def test_06_get_tech_hiring_hubs(self):
        """Should return geographical tech hiring hubs across India and Global centers."""
        hubs = self.scraper.get_tech_hiring_hubs()
        self.assertGreaterEqual(len(hubs), 7)
        hub_names = [h.hub_name for h in hubs]
        self.assertTrue(any("Bengaluru" in name for name in hub_names))
        self.assertTrue(any("San Francisco" in name for name in hub_names))
        first_hub = hubs[0]
        self.assertGreater(first_hub.active_job_count, 100)
        self.assertGreater(first_hub.avg_salary_inr_lpa, 10.0)
        self.assertGreater(first_hub.remote_friendly_pct, 0)

    def test_07_get_skill_velocity_tracker(self):
        """Should compute month-over-month velocity metrics and trajectory."""
        metrics = self.scraper.get_skill_velocity_tracker()
        self.assertGreaterEqual(len(metrics), 5)
        llm_metric = next((m for m in metrics if "LLMs" in m.skill_name or "Language Models" in m.skill_name), None)
        self.assertIsNotNone(llm_metric)
        self.assertGreater(llm_metric.mom_growth_pct, 100.0)
        self.assertEqual(llm_metric.velocity_tier, "Breakout / High Surge")
        self.assertEqual(len(llm_metric.historical_trajectory_6m), 6)


if __name__ == "__main__":
    unittest.main(verbosity=2)

