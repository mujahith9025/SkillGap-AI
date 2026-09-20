"""
Test Runner for Interactive Visual Analytics Dashboard
Phase 14: Analytics Dashboard

Validates generation of all 5 Plotly visual charts:
1. Category-Wise Competency Radar Chart
2. Matched vs. Missing Donut Chart
3. Cross-Career Comparison Horizontal Bar Chart
4. Skill Gap Category & Difficulty Stacked Bar Chart
5. Interactive Career-Skill Matrix Heatmap
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from data_loader import DataLoader
from skill_matcher import SkillMatcher
from gap_analyzer import SkillGapAnalyzer
from analytics_dashboard import VisualAnalyticsDashboard

def main():
    print("=" * 80)
    print(" INTERACTIVE ANALYTICS DASHBOARD - TEST RUNNER")
    print("=" * 80)
    
    loader = DataLoader()
    matcher = SkillMatcher(data_loader=loader)
    gap_analyzer = SkillGapAnalyzer(data_loader=loader, skill_matcher=matcher)
    dashboard = VisualAnalyticsDashboard()

    profile = ["Python", "Pandas", "SQL", "Excel"]
    career = "Data Scientist"

    match_res = matcher.match_skills(profile, career)
    gap_res = gap_analyzer.analyze_gaps(profile, career)
    all_rankings = matcher.match_all_careers(profile)

    # 1. Radar Chart Test
    print("[*] Generating Category Radar Chart...")
    fig_radar = dashboard.create_category_radar_chart(match_res)
    assert fig_radar is not None
    print("  [PASS] Radar Chart generated.")

    # 2. Donut Chart Test
    print("[*] Generating Matched vs. Missing Donut Chart...")
    fig_donut = dashboard.create_matched_vs_missing_donut(match_res)
    assert fig_donut is not None
    print("  [PASS] Donut Chart generated.")

    # 3. Career Comparison Bar Test
    print("[*] Generating Cross-Career Comparison Bar Chart...")
    fig_bar = dashboard.create_career_comparison_bar(all_rankings)
    assert fig_bar is not None
    print("  [PASS] Comparison Bar Chart generated.")

    # 4. Gap Category/Difficulty Bar Test
    print("[*] Generating Gap Distribution Bar Chart...")
    fig_gap = dashboard.create_gap_distribution_bar(gap_res)
    assert fig_gap is not None
    print("  [PASS] Gap Distribution Bar Chart generated.")

    # 5. Interactive Heatmap Test
    print("[*] Generating Interactive Career Matrix Heatmap...")
    fig_map = dashboard.create_interactive_matrix_heatmap(loader)
    assert fig_map is not None
    print("  [PASS] Interactive Heatmap generated.")

    print("\n" + "=" * 80)
    print(" ALL 5 INTERACTIVE VISUALIZATIONS GENERATED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
