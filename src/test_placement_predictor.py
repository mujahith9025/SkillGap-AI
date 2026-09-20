"""
Unit Tests for Placement Predictor & Multi-Role Fit Matrix Engine
Phase 13 / Section 1 Upgrades
"""

import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from placement_predictor import PlacementPredictorEngine, PlacementPredictionReport, MultiRoleFitItem


@pytest.fixture(scope="module")
def predictor_engine():
    return PlacementPredictorEngine()


def test_01_predict_high_match_student(predictor_engine):
    skills = [
        "Python", "SQL", "Pandas", "NumPy", "Scikit-Learn",
        "Machine Learning", "Statistics & Probability", "Matplotlib & Seaborn",
        "Excel", "Git & GitHub", "Docker"
    ]
    report = predictor_engine.predict_placement_probability(
        student_skills=skills,
        target_career="Data Scientist",
        github_quality_score=88.0,
        ats_score=85.0,
        mock_interview_score=9.0
    )

    assert isinstance(report, PlacementPredictionReport)
    assert 0.0 <= report.placement_probability_pct <= 100.0
    assert report.placement_probability_pct >= 70.0
    assert "Tier-1" in report.predicted_tier or "Unicorn" in report.predicted_tier
    assert report.cohort_percentile > 60.0
    assert len(report.bell_curve_coordinates) > 10
    assert len(report.key_contributing_factors) > 0


def test_02_predict_beginner_student(predictor_engine):
    skills = ["Python"]
    report = predictor_engine.predict_placement_probability(
        student_skills=skills,
        target_career="Data Scientist",
        github_quality_score=30.0,
        ats_score=40.0,
        mock_interview_score=4.0
    )

    assert isinstance(report, PlacementPredictionReport)
    assert 0.0 <= report.placement_probability_pct <= 100.0
    assert report.placement_probability_pct < 55.0
    assert report.cohort_percentile < 60.0
    # Negative impact factors should be identified
    neg_factors = [f for f in report.key_contributing_factors if f.impact == "negative"]
    assert len(neg_factors) > 0


def test_03_multi_role_matrix(predictor_engine):
    skills = ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn"]
    matrix = predictor_engine.compute_multi_role_matrix(skills)

    assert len(matrix) >= 7
    titles = [item.career_title for item in matrix]
    assert "Data Scientist" in titles
    assert "Machine Learning Engineer" in titles
    assert "Data Analyst" in titles

    # Verify descending sort by readiness
    readiness_list = [item.readiness_pct for item in matrix]
    assert readiness_list == sorted(readiness_list, reverse=True)

    # Verify bridge skills exist for roles with missing skills
    for item in matrix:
        if item.missing_skills:
            assert item.bridge_skill is not None
            assert item.bridge_jump_pct > 0
            assert item.bridge_study_hours > 0
