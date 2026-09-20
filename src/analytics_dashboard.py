"""
Interactive Analytics Dashboard & Visualizations Module
Phase 14: Analytics Dashboard

Provides interactive, publication-grade Plotly visualization figures:
1. Category-Wise Competency Radar Chart
2. Matched vs. Missing Criticality Breakdown (Donut Chart)
3. Cross-Career Role Readiness Comparison (Ranked Bar Chart)
4. Skill Gap Distribution by Category & Difficulty (Stacked Bar Chart)
5. Interactive Career-Skill Requirement Matrix (Heatmap)
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_loader import DataLoader
from skill_matcher import SkillMatchResult
from gap_analyzer import GapAnalysisResult


class VisualAnalyticsDashboard:
    """
    Generates interactive Plotly visual charts for skill gap analytics.
    """

    @staticmethod
    def create_category_radar_chart(match_result: SkillMatchResult) -> go.Figure:
        """
        Radar / Polar chart showing student coverage percentage across domain categories:
        (Programming, Math & Statistics, Machine Learning, Deep Learning, BI, Database, DevOps, etc.)
        """
        category_req = defaultdict(int)
        category_matched = defaultdict(int)

        matched_names = {s["skill_name"] for s in match_result.matched_skills}

        for req in match_result.required_skills:
            cat = req["category"]
            category_req[cat] += 1
            if req["skill_name"] in matched_names:
                category_matched[cat] += 1

        categories = list(category_req.keys())
        coverage_percentages = [
            (category_matched[c] / category_req[c] * 100.0) if category_req[c] > 0 else 0.0
            for c in categories
        ]

        # Close the radar polygon by appending first point
        r_vals = coverage_percentages + [coverage_percentages[0]]
        theta_vals = categories + [categories[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=r_vals,
            theta=theta_vals,
            fill='toself',
            fillcolor='rgba(37, 99, 235, 0.25)',
            line=dict(color='#1d4ed8', width=2.5),
            name='Student Readiness'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    ticksuffix='%',
                    tickfont=dict(size=10)
                )
            ),
            showlegend=False,
            title=dict(
                text=f"<b>Domain Category Readiness Radar ({match_result.career_title})</b>",
                font=dict(size=14)
            ),
            margin=dict(l=40, r=40, t=50, b=40),
            height=380
        )
        return fig

    @staticmethod
    def create_matched_vs_missing_donut(match_result: SkillMatchResult) -> go.Figure:
        """
        Donut chart breaking down required skills by status and criticality level:
        Matched Core, Matched Secondary, Matched Optional, Missing Core, Missing Secondary, Missing Optional.
        """
        labels = []
        values = []
        colors = []

        # Color mapping palette
        color_palette = {
            "Matched Core": "#15803d",       # Dark Green
            "Matched Secondary": "#22c55e",  # Light Green
            "Matched Optional": "#86efac",   # Mint Green
            "Missing Core": "#b91c1c",       # Crimson Red
            "Missing Secondary": "#f97316",  # Orange
            "Missing Optional": "#38bdf8"    # Sky Blue
        }

        matched_counts = defaultdict(int)
        for s in match_result.matched_skills:
            matched_counts[s["importance_level"]] += 1

        missing_counts = defaultdict(int)
        for s in match_result.missing_skills:
            missing_counts[s["importance_level"]] += 1

        for level in ["Core", "Secondary", "Optional"]:
            m_count = matched_counts[level]
            if m_count > 0:
                name = f"Matched {level}"
                labels.append(name)
                values.append(m_count)
                colors.append(color_palette[name])

        for level in ["Core", "Secondary", "Optional"]:
            g_count = missing_counts[level]
            if g_count > 0:
                name = f"Missing {level}"
                labels.append(name)
                values.append(g_count)
                colors.append(color_palette[name])

        if not values:
            fig = go.Figure()
            fig.add_annotation(
                text="No skill requirement data available.",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                font=dict(size=13, color="#64748b")
            )
            fig.update_layout(height=380, title="<b>Requirement Breakdown</b>")
            return fig

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=colors),
            textinfo='label+value',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>Count: %{value} skills<br>Percentage: %{percent}<extra></extra>'
        )])

        fig.update_layout(
            title=dict(
                text=f"<b>Requirement Breakdown by Criticality Level</b>",
                font=dict(size=14)
            ),
            showlegend=False,
            margin=dict(l=20, r=20, t=50, b=20),
            height=380
        )
        return fig

    @staticmethod
    def create_career_comparison_bar(all_rankings: List[SkillMatchResult]) -> go.Figure:
        """
        Horizontal comparison bar chart ranking student readiness across all 7 careers.
        """
        if not all_rankings:
            fig = go.Figure()
            fig.add_annotation(text="No career rankings available.", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(height=380)
            return fig

        titles = [r.career_title for r in reversed(all_rankings)]
        weighted_scores = [r.weighted_readiness_pct for r in reversed(all_rankings)]
        raw_coverages = [r.unweighted_coverage_pct for r in reversed(all_rankings)]

        fig = go.Figure()

        # Weighted score bars
        fig.add_trace(go.Bar(
            y=titles,
            x=weighted_scores,
            name='Weighted Match Score (%)',
            orientation='h',
            marker=dict(
                color=weighted_scores,
                colorscale='Blues',
                line=dict(color='#1e3a8a', width=1)
            ),
            text=[f"{v:.1f}%" for v in weighted_scores],
            textposition='inside',
            insidetextanchor='middle',
            hovertemplate='<b>%{y}</b><br>Weighted Match: %{x:.1f}%<extra></extra>'
        ))

        # Raw coverage scatter markers
        fig.add_trace(go.Scatter(
            y=titles,
            x=raw_coverages,
            name='Raw Skill Coverage (%)',
            mode='markers',
            marker=dict(color='#dc2626', size=10, symbol='diamond'),
            hovertemplate='<b>%{y}</b><br>Raw Coverage: %{x:.1f}%<extra></extra>'
        ))

        fig.update_layout(
            title=dict(
                text="<b>Student Readiness Ranking Across All 7 Career Tracks</b>",
                font=dict(size=14)
            ),
            xaxis=dict(
                title="Match Score (%)",
                range=[0, 105],
                ticksuffix='%'
            ),
            yaxis=dict(title=""),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=60, b=40),
            height=380
        )
        return fig

    @staticmethod
    def create_gap_distribution_bar(gap_result: GapAnalysisResult) -> go.Figure:
        """
        Stacked bar chart showing missing skills grouped by Technical Category and Difficulty Level.
        """
        if not gap_result.learning_roadmap:
            fig = go.Figure()
            fig.add_annotation(
                text="🎉 Congratulations! No skill gaps identified.<br>All required competencies are satisfied.",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=13, color="#16a34a")
            )
            fig.update_layout(
                title="<b>Skill Gaps by Technical Category & Learning Difficulty</b>",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=380,
                margin=dict(l=20, r=20, t=50, b=40)
            )
            return fig

        data = []
        for s in gap_result.learning_roadmap:
            data.append({
                "Skill": s.skill_name,
                "Category": s.category,
                "Difficulty": s.difficulty_level,
                "Priority": s.priority_tier,
                "Weight": s.importance_weight
            })
        df = pd.DataFrame(data)

        agg = df.groupby(["Category", "Difficulty"]).size().reset_index(name="Count")

        fig = px.bar(
            agg,
            x="Category",
            y="Count",
            color="Difficulty",
            category_orders={"Difficulty": ["Beginner", "Intermediate", "Advanced"]},
            color_discrete_map={
                "Beginner": "#10b981",
                "Intermediate": "#f59e0b",
                "Advanced": "#ef4444"
            },
            title="<b>Skill Gaps by Technical Category & Learning Difficulty</b>",
            text="Count"
        )

        fig.update_layout(
            xaxis_title="Domain Category",
            yaxis_title="Missing Skills Count",
            margin=dict(l=20, r=20, t=50, b=40),
            height=380
        )
        return fig

    @staticmethod
    def create_interactive_matrix_heatmap(loader: DataLoader) -> go.Figure:
        """
        Interactive Plotly heatmap of the Career vs. Skill requirement matrix.
        """
        matrix = loader.get_career_skill_matrix()

        fig = go.Figure(data=go.Heatmap(
            z=matrix.values,
            x=matrix.columns.tolist(),
            y=matrix.index.tolist(),
            colorscale=[
                [0.0, '#f8fafc'],
                [0.33, '#bae6fd'],
                [0.66, '#fde047'],
                [1.0, '#f87171']
            ],
            colorbar=dict(
                title="Importance Weight",
                tickvals=[0, 1, 2, 3],
                ticktext=["Not Required (0)", "Optional (1)", "Secondary (2)", "Core (3)"]
            ),
            hovertemplate='<b>Career:</b> %{y}<br><b>Skill:</b> %{x}<br><b>Weight:</b> %{z}<extra></extra>'
        ))

        fig.update_layout(
            title=dict(
                text="<b>Interactive Career Role vs. Skill Requirement Matrix</b>",
                font=dict(size=14)
            ),
            xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
            yaxis=dict(tickfont=dict(size=10)),
            margin=dict(l=20, r=20, t=50, b=80),
            height=450
        )
        return fig
