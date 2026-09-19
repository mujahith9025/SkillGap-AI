"""
Personalized Learning Roadmap Generator Module
Phase 9: Personalized Learning Roadmap Generator

Transforms prioritized skill gaps, prerequisite graphs, and portfolio projects
into structured visual learning flowcharts (ASCII diagrams, Mermaid graphs,
and milestone timelines).
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import pandas as pd

from data_loader import DataLoader
from recommendation_engine import RecommendationEngine, PersonalizedRecommendationReport, SkillRecommendation, ProjectRecommendation


@dataclass
class VisualRoadmap:
    """Encapsulates multi-format structured learning roadmaps."""
    career_id: str
    career_title: str
    student_skills: List[str]
    weighted_readiness_pct: float
    total_hours: int
    phases: List[Dict[str, Any]]
    ascii_diagram: str
    mermaid_diagram: str
    capstone_project: Optional[ProjectRecommendation]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "career_id": self.career_id,
            "career_title": self.career_title,
            "weighted_readiness_pct": round(self.weighted_readiness_pct, 1),
            "total_estimated_hours": self.total_hours,
            "phases": self.phases,
            "ascii_diagram": self.ascii_diagram,
            "mermaid_diagram": self.mermaid_diagram,
            "capstone_project": self.capstone_project.to_dict() if self.capstone_project else None
        }


class RoadmapGenerator:
    """
    Generates structured, prerequisite-aware visual learning roadmaps
    and flowcharts across multiple technical career paths.
    """

    def __init__(
        self,
        data_loader: Optional[DataLoader] = None,
        recommendation_engine: Optional[RecommendationEngine] = None
    ):
        self.loader = data_loader if data_loader else DataLoader()
        self.rec_engine = recommendation_engine if recommendation_engine else RecommendationEngine(data_loader=self.loader)

    def generate_roadmap(
        self,
        student_skills: Union[List[str], str],
        career_identifier: str
    ) -> VisualRoadmap:
        """
        Builds a full multi-format visual roadmap for a student and target career.
        """
        report = self.rec_engine.generate_recommendations(student_skills, career_identifier)
        
        # 1. Structure skills into prerequisite-depth layers (Phases)
        phases_data = self._partition_into_prerequisite_phases(report)

        # 2. Select the top capstone portfolio project
        capstone_project = report.recommended_projects[0] if report.recommended_projects else None

        # 3. Render ASCII flowchart
        ascii_flow = self._render_ascii_flowchart(report.career_title, phases_data, capstone_project)

        # 4. Generate Mermaid graph code for Streamlit and Markdown rendering
        mermaid_code = self._generate_mermaid_graph(report, phases_data, capstone_project)

        return VisualRoadmap(
            career_id=report.career_id,
            career_title=report.career_title,
            student_skills=report.student_normalized_skills,
            weighted_readiness_pct=report.weighted_readiness_pct,
            total_hours=report.total_estimated_study_hours,
            phases=phases_data,
            ascii_diagram=ascii_flow,
            mermaid_diagram=mermaid_code,
            capstone_project=capstone_project
        )

    def _partition_into_prerequisite_phases(
        self,
        report: PersonalizedRecommendationReport
    ) -> List[Dict[str, Any]]:
        """
        Partitions missing skills into sequential logical phases with duration and objectives.
        """
        phases = []
        for m in report.milestones:
            phase_skills = []
            for s in m.skills:
                phase_skills.append({
                    "step": s.step_number,
                    "skill_name": s.skill_name,
                    "category": s.category,
                    "difficulty": s.difficulty_level,
                    "priority": s.priority_tier,
                    "reason": s.reason,
                    "hours": s.total_estimated_hours,
                    "top_resource": s.resources[0].title if s.resources else "Official Documentation",
                    "resource_url": s.resources[0].url_or_ref if s.resources else "#"
                })

            phases.append({
                "phase_number": m.milestone_number,
                "title": m.milestone_title,
                "objective": m.objective,
                "estimated_hours": m.estimated_study_hours,
                "skills": phase_skills,
                "milestone_project": m.recommended_project.title if m.recommended_project else None
            })

        return phases

    def _render_ascii_flowchart(
        self,
        career_title: str,
        phases: List[Dict[str, Any]],
        capstone: Optional[ProjectRecommendation]
    ) -> str:
        """
        Renders a clean ASCII linear/layered pathway diagram.
        """
        lines = []
        lines.append("=" * 75)
        lines.append(f" SEQUENTIAL LEARNING ROADMAP: {career_title.upper()}")
        lines.append("=" * 75)

        if not phases:
            lines.append("\n[*] Congratulations! You have mastered 100% of the required skills for this career.")
            lines.append("    No missing skill gap phases required. You are ready to build the capstone portfolio project!\n")
        else:
            for p_idx, phase in enumerate(phases, 1):
                lines.append(f"\n[PHASE {p_idx}: {phase['title'].upper()}] (~{phase['estimated_hours']} Hours)")
                lines.append(f"Goal: {phase['objective']}")
                lines.append("  |")
            
            for s_idx, s in enumerate(phase["skills"]):
                is_last_in_phase = (s_idx == len(phase["skills"]) - 1)
                prefix = "  +-->"
                lines.append(f"{prefix} Step {s['step']:2d}: {s['skill_name']} [{s['difficulty']}]")
                lines.append(f"  |    Reason: {s['reason']}")
                lines.append(f"  |    Resource: {s['top_resource']}")
                if not is_last_in_phase:
                    lines.append("  |")
            
            if phase["milestone_project"]:
                lines.append("  |")
                lines.append(f"  +==> [Milestone Project: {phase['milestone_project']}]")
            
            if p_idx < len(phases):
                lines.append("  |")
                lines.append("  V")

        if capstone:
            lines.append("  |")
            lines.append("  V")
            lines.append("=" * 75)
            lines.append(f" [FINAL CAPSTONE PORTFOLIO DELIVERABLE]")
            lines.append(f" Project: {capstone.title} ({capstone.difficulty})")
            lines.append(f" Skills Tested: {capstone.primary_skills}")
            lines.append(f" Deliverables: {capstone.key_deliverables}")
            lines.append("=" * 75)

        return "\n".join(lines)

    def _generate_mermaid_graph(
        self,
        report: PersonalizedRecommendationReport,
        phases: List[Dict[str, Any]],
        capstone: Optional[ProjectRecommendation]
    ) -> str:
        """
        Generates clean, styled Mermaid graph flowchart syntax.
        """
        mermaid_lines = [
            "```mermaid",
            "graph TD",
            "  %% Styling Definitions",
            "  classDef matched fill:#27ae60,stroke:#1e8449,stroke-width:2px,color:#fff,font-weight:bold;",
            "  classDef highPriority fill:#e67e22,stroke:#d35400,stroke-width:2px,color:#fff,font-weight:bold;",
            "  classDef mediumPriority fill:#2980b9,stroke:#1f618d,stroke-width:2px,color:#fff;",
            "  classDef projectNode fill:#8e44ad,stroke:#6c3483,stroke-width:3px,color:#fff,font-weight:bold;"
        ]

        # 1. Existing Skills Subgraph
        if report.student_normalized_skills:
            mermaid_lines.append("\n  subgraph Already_Mastered [Already Mastered / Matched Skills]")
            for i, skill in enumerate(report.student_normalized_skills):
                safe_id = f"MASTERED_{i}"
                mermaid_lines.append(f'    {safe_id}["✓ {skill}"]:::matched')
            mermaid_lines.append("  end")

        # 2. Roadmap Phases Subgraphs
        prev_phase_last_node = None
        first_step_node = None

        for p_idx, p in enumerate(phases, 1):
            subgraph_id = f"Phase_{p_idx}"
            subgraph_title = f"Phase {p_idx}: {p['title'].replace('Milestone ' + str(p_idx) + ': ', '')}"
            mermaid_lines.append(f'\n  subgraph {subgraph_id} ["{subgraph_title} (~{p["estimated_hours"]}h)"]')
            
            phase_nodes = []
            for s in p["skills"]:
                node_id = f"STEP_{s['step']}"
                if first_step_node is None:
                    first_step_node = node_id
                
                cls = "highPriority" if s["priority"] == "High" else "mediumPriority"
                mermaid_lines.append(f'    {node_id}["Step {s["step"]}: {s["skill_name"]} ({s["difficulty"]})"]:::{cls}')
                phase_nodes.append(node_id)

            # Intra-phase linear connections
            for i in range(len(phase_nodes) - 1):
                mermaid_lines.append(f"    {phase_nodes[i]} --> {phase_nodes[i+1]}")

            mermaid_lines.append("  end")

            # Connect previous phase to current phase
            if prev_phase_last_node and phase_nodes:
                mermaid_lines.append(f"  {prev_phase_last_node} ==> {phase_nodes[0]}")
            
            if phase_nodes:
                prev_phase_last_node = phase_nodes[-1]

        # 3. Capstone Project Node
        if capstone:
            cap_id = "CAPSTONE_PROJECT"
            mermaid_lines.append(f'\n  {cap_id}[("★ Capstone: {capstone.title}")]:::projectNode')
            if prev_phase_last_node:
                mermaid_lines.append(f"  {prev_phase_last_node} ==> {cap_id}")

        mermaid_lines.append("```")
        return "\n".join(mermaid_lines)
