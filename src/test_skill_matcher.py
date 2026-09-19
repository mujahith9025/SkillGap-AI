"""
Test Runner for Basic Skill Matching Engine
Phase 6: Basic Skill Matching Engine

Tests skill matching against multiple student profiles and target roles:
- Case 1: Student Profile -> Data Scientist
- Case 2: Student Profile -> Data Analyst
- Case 3: Student Profile -> Machine Learning Engineer
- Case 4: Cross-Career Multi-Role Ranking Comparison
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from data_loader import DataLoader
from preprocessing import SkillPreprocessor
from skill_matcher import SkillMatcher

def main():
    loader = DataLoader()
    preprocessor = SkillPreprocessor(data_loader=loader)
    matcher = SkillMatcher(data_loader=loader, preprocessor=preprocessor)
    
    print("=" * 75)
    print(" BASIC SKILL MATCHING ENGINE - VALIDATION & TEST RUNNER")
    print("=" * 75)

    # -------------------------------------------------------------
    # Test Case 1: Data Scientist Evaluation
    # -------------------------------------------------------------
    profile_1 = "Python, Pandas, NumPy, Excel, Data Viz, MySQL"
    target_role_1 = "Data Scientist"
    print(f"\n>>> TEST CASE 1: Student Skills -> {target_role_1}")
    result_1 = matcher.match_skills(profile_1, target_role_1)
    print(matcher.format_match_report(result_1))
    
    # Assertions for Case 1
    assert "Python" in [s["skill_name"] for s in result_1.matched_skills]
    assert "Pandas" in [s["skill_name"] for s in result_1.matched_skills]
    assert "SQL" in [s["skill_name"] for s in result_1.matched_skills] # via MySQL alias
    assert "Machine Learning" in [s["skill_name"] for s in result_1.missing_skills]
    assert "Scikit-Learn" in [s["skill_name"] for s in result_1.missing_skills]
    assert result_1.weighted_readiness_pct > 0.0

    # -------------------------------------------------------------
    # Test Case 2: Data Analyst Evaluation
    # -------------------------------------------------------------
    profile_2 = "SQL, Excel, Tableau, Power BI, Python, stats"
    target_role_2 = "Data Analyst"
    print(f"\n>>> TEST CASE 2: Student Skills -> {target_role_2}")
    result_2 = matcher.match_skills(profile_2, target_role_2)
    print(matcher.format_match_report(result_2))
    
    # Assertions for Case 2
    assert "SQL" in [s["skill_name"] for s in result_2.matched_skills]
    assert "Excel" in [s["skill_name"] for s in result_2.matched_skills]
    assert "Tableau" in [s["skill_name"] for s in result_2.matched_skills]
    assert "Power BI" in [s["skill_name"] for s in result_2.matched_skills]
    assert "Business Metrics & KPI Modeling" in [s["skill_name"] for s in result_2.missing_skills]
    assert result_2.weighted_readiness_pct >= 50.0

    # -------------------------------------------------------------
    # Test Case 3: Machine Learning Engineer Evaluation
    # -------------------------------------------------------------
    profile_3 = "Python, Linear Algebra, NumPy, Deep Learning, PyTorch, Git, Docker"
    target_role_3 = "Machine Learning Engineer"
    print(f"\n>>> TEST CASE 3: Student Skills -> {target_role_3}")
    result_3 = matcher.match_skills(profile_3, target_role_3)
    print(matcher.format_match_report(result_3))
    
    # Assertions for Case 3
    assert "PyTorch" in [s["skill_name"] for s in result_3.matched_skills]
    assert "Docker" in [s["skill_name"] for s in result_3.matched_skills]
    assert "Git & GitHub" in [s["skill_name"] for s in result_3.matched_skills]
    assert "MLOps & Model Deployment" in [s["skill_name"] for s in result_3.missing_skills]

    # -------------------------------------------------------------
    # Test Case 4: Cross-Career Best Fit Ranking
    # -------------------------------------------------------------
    general_ai_profile = "Python, SQL, PyTorch, Deep Learning, FastAPI, Docker, Git"
    print("\n" + "=" * 75)
    print(f">>> TEST CASE 4: Multi-Career Best Fit Ranking for Profile:")
    print(f"    Skills: {general_ai_profile}")
    print("=" * 75)
    
    ranked_careers = matcher.match_all_careers(general_ai_profile)
    print(f"{'Rank':<5} | {'Career Title':<30} | {'Weighted Score':<16} | {'Coverage':<12} | {'Core Progress'}")
    print("-" * 75)
    for rank, res in enumerate(ranked_careers, 1):
        print(f"{rank:<5} | {res.career_title:<30} | {res.weighted_readiness_pct:>6.1f}%          | {res.unweighted_coverage_pct:>5.1f}%       | {res.core_matched_count}/{res.core_total_count} core")

    print("\n[SUCCESS] All 3 career matching test cases and cross-career rankings completed successfully!")
    print("=" * 75)

if __name__ == "__main__":
    main()
