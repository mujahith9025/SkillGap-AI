"""
Test Runner for Personalized Recommendation Engine
Phase 8: Personalized Recommendation Engine

Tests end-to-end explainable recommendations across diverse profiles:
- Test 1: Data Scientist Aspirant (Bridging ML, Scikit-Learn, Statistics)
- Test 2: Data Analyst Aspirant (Bridging BI, Tableau, KPI modeling)
- Test 3: ML Engineer Aspirant (Bridging PyTorch, Docker, MLOps)
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from recommendation_engine import RecommendationEngine

def main():
    print("=" * 75)
    print(" PERSONALIZED RECOMMENDATION ENGINE - TEST SUITE")
    print("=" * 75)
    
    rec_engine = RecommendationEngine()

    # -------------------------------------------------------------
    # Test 1: Data Scientist Profile
    # -------------------------------------------------------------
    profile_1 = "Python, Pandas, NumPy, Excel"
    career_1 = "Data Scientist"
    print(f"\n>>> TEST 1: Recommendation Plan for {career_1}")
    report_1 = rec_engine.generate_recommendations(profile_1, career_1)
    print(rec_engine.format_recommendation_report(report_1))

    # Assertions for Test 1
    assert len(report_1.milestones) == 3, "Expected 3 progressive roadmap milestones!"
    assert len(report_1.recommended_projects) > 0, "Expected recommended projects!"
    assert any("Machine Learning" in s.skill_name for s in report_1.skill_recommendations), "Expected ML recommendation!"
    assert report_1.total_estimated_study_hours > 0, "Expected positive study hours estimate!"

    # -------------------------------------------------------------
    # Test 2: Data Analyst Profile
    # -------------------------------------------------------------
    profile_2 = "Excel, SQL"
    career_2 = "Data Analyst"
    print(f"\n>>> TEST 2: Recommendation Plan for {career_2}")
    report_2 = rec_engine.generate_recommendations(profile_2, career_2)
    print(rec_engine.format_recommendation_report(report_2))

    # Assertions for Test 2
    assert any("Tableau" in s.skill_name or "Power BI" in s.skill_name for s in report_2.skill_recommendations)
    assert len(report_2.recommended_projects) > 0

    # -------------------------------------------------------------
    # Test 3: Machine Learning Engineer Profile
    # -------------------------------------------------------------
    profile_3 = "Python, Scikit-Learn, Machine Learning, Git"
    career_3 = "Machine Learning Engineer"
    print(f"\n>>> TEST 3: Recommendation Plan for {career_3}")
    report_3 = rec_engine.generate_recommendations(profile_3, career_3)
    print(rec_engine.format_recommendation_report(report_3))

    # Assertions for Test 3
    assert any("Docker" in s.skill_name for s in report_3.skill_recommendations)
    assert any("MLOps" in s.skill_name for s in report_3.skill_recommendations)

    print("\n" + "=" * 75)
    print(" ALL RECOMMENDATION ENGINE TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 75)

if __name__ == "__main__":
    main()
