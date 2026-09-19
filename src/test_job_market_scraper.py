"""
Unit Tests for Real-Time Job Market Scraper & Dynamic Weighting Module
"""

import unittest
from pathlib import Path

from data_loader import DataLoader
from skill_extractor import NLPSkillExtractor
from job_market_scraper import JobMarketScraper, MarketIntelligenceReport, DynamicSkillWeight


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
