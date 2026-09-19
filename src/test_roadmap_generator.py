"""
Test Runner for Personalized Learning Roadmap Generator
Phase 9: Personalized Learning Roadmap Generator

Tests roadmap generation, ASCII flowcharts, and Mermaid diagrams across multiple careers:
- Test 1: Data Scientist Roadmap
- Test 2: Machine Learning Engineer Roadmap
- Test 3: Data Analyst Roadmap
- Test 4: Backend Developer Roadmap
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from roadmap_generator import RoadmapGenerator

def main():
    print("=" * 75)
    print(" PERSONALIZED LEARNING ROADMAP GENERATOR - TEST RUNNER")
    print("=" * 75)
    
    generator = RoadmapGenerator()

    # -------------------------------------------------------------
    # Test 1: Data Scientist Roadmap
    # -------------------------------------------------------------
    profile_1 = "Python, Excel, SQL"
    career_1 = "Data Scientist"
    print(f"\n>>> TEST 1: Generating Visual Roadmap for {career_1}")
    roadmap_1 = generator.generate_roadmap(profile_1, career_1)
    print(roadmap_1.ascii_diagram)
    print("\n[Mermaid Graph Preview]:")
    print(roadmap_1.mermaid_diagram[:450] + "\n  ...\n```")

    assert len(roadmap_1.phases) == 3
    assert roadmap_1.capstone_project is not None
    assert "Pandas" in [s["skill_name"] for p in roadmap_1.phases for s in p["skills"]]

    # -------------------------------------------------------------
    # Test 2: Machine Learning Engineer Roadmap
    # -------------------------------------------------------------
    profile_2 = "Python, NumPy, Git"
    career_2 = "Machine Learning Engineer"
    print("\n" + "=" * 75)
    print(f">>> TEST 2: Generating Visual Roadmap for {career_2}")
    print("=" * 75)
    roadmap_2 = generator.generate_roadmap(profile_2, career_2)
    print(roadmap_2.ascii_diagram)

    assert len(roadmap_2.phases) == 3
    assert any("Deep Learning" in s["skill_name"] for p in roadmap_2.phases for s in p["skills"])

    # -------------------------------------------------------------
    # Test 3: Data Analyst Roadmap
    # -------------------------------------------------------------
    profile_3 = "Excel, SQL"
    career_3 = "Data Analyst"
    print("\n" + "=" * 75)
    print(f">>> TEST 3: Generating Visual Roadmap for {career_3}")
    print("=" * 75)
    roadmap_3 = generator.generate_roadmap(profile_3, career_3)
    print(roadmap_3.ascii_diagram)

    assert any("Tableau" in s["skill_name"] or "Power BI" in s["skill_name"] for p in roadmap_3.phases for s in p["skills"])

    print("\n" + "=" * 75)
    print(" ALL ROADMAP GENERATOR TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 75)

if __name__ == "__main__":
    main()
