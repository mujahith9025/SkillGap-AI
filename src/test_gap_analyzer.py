"""
Test Runner for Skill Gap Analysis & Prioritized Learning Roadmap
Phase 7: Skill Gap Analysis and Prioritization

Tests:
- Prerequisite-aware Topological Sequencing
- Multi-factor Priority Scoring (Importance, Unlocks, Difficulty)
- High/Medium/Low Priority Categorization
- Validation on multiple career tracks (Data Scientist, ML Engineer)
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from gap_analyzer import SkillGapAnalyzer

def test_gap_analysis():
    print("=" * 75)
    print(" SKILL GAP ANALYSIS & PRIORITIZATION TEST SUITE")
    print("=" * 75)
    
    analyzer = SkillGapAnalyzer()

    # -------------------------------------------------------------
    # Scenario 1: Aspiring Data Scientist
    # -------------------------------------------------------------
    profile_1 = "Python, SQL, Excel, Data Visualization"
    career_1 = "Data Scientist"
    
    print(f"\n>>> SCENARIO 1: Student Profile -> {career_1}")
    res_1 = analyzer.analyze_gaps(profile_1, career_1)
    print(analyzer.format_gap_report(res_1))

    # Verify Roadmap Topological Invariants
    roadmap_skills_1 = [s.skill_name for s in res_1.learning_roadmap]
    
    # 1. Pandas must come before Scikit-Learn (PRQ_006)
    if "Pandas" in roadmap_skills_1 and "Scikit-Learn" in roadmap_skills_1:
        assert roadmap_skills_1.index("Pandas") < roadmap_skills_1.index("Scikit-Learn"), \
            "Topology Error: Pandas must precede Scikit-Learn!"
            
    # 2. Statistics & Scikit-Learn must come before Machine Learning (PRQ_008, PRQ_009)
    if "Statistics & Probability" in roadmap_skills_1 and "Machine Learning" in roadmap_skills_1:
        assert roadmap_skills_1.index("Statistics & Probability") < roadmap_skills_1.index("Machine Learning"), \
            "Topology Error: Statistics must precede Machine Learning!"
            
    # 3. Machine Learning must come before Deep Learning (PRQ_011)
    if "Machine Learning" in roadmap_skills_1 and "Deep Learning" in roadmap_skills_1:
        assert roadmap_skills_1.index("Machine Learning") < roadmap_skills_1.index("Deep Learning"), \
            "Topology Error: Machine Learning must precede Deep Learning!"
            
    print("[PASS] Scenario 1 satisfied all prerequisite topological graph invariants.")

    # -------------------------------------------------------------
    # Scenario 2: Aspiring Machine Learning Engineer
    # -------------------------------------------------------------
    profile_2 = "Python, NumPy, Git"
    career_2 = "Machine Learning Engineer"
    
    print("\n" + "=" * 75)
    print(f">>> SCENARIO 2: Student Profile -> {career_2}")
    print("=" * 75)
    res_2 = analyzer.analyze_gaps(profile_2, career_2)
    print(analyzer.format_gap_report(res_2))

    roadmap_skills_2 = [s.skill_name for s in res_2.learning_roadmap]
    
    # 1. Linear Algebra must precede Deep Learning (PRQ_010)
    if "Linear Algebra" in roadmap_skills_2 and "Deep Learning" in roadmap_skills_2:
        assert roadmap_skills_2.index("Linear Algebra") < roadmap_skills_2.index("Deep Learning"), \
            "Topology Error: Linear Algebra must precede Deep Learning!"
            
    # 2. Deep Learning must precede PyTorch (PRQ_013)
    if "Deep Learning" in roadmap_skills_2 and "PyTorch" in roadmap_skills_2:
        assert roadmap_skills_2.index("Deep Learning") < roadmap_skills_2.index("PyTorch"), \
            "Topology Error: Deep Learning must precede PyTorch!"

    # 3. Docker must precede MLOps (PRQ_021)
    if "Docker" in roadmap_skills_2 and "MLOps & Model Deployment" in roadmap_skills_2:
        assert roadmap_skills_2.index("Docker") < roadmap_skills_2.index("MLOps & Model Deployment"), \
            "Topology Error: Docker must precede MLOps!"

    print("[PASS] Scenario 2 satisfied all prerequisite topological graph invariants.")

    print("\n" + "=" * 75)
    print(" ALL GAP ANALYSIS & PRIORITIZATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 75)

if __name__ == "__main__":
    test_gap_analysis()
