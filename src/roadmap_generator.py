"""
Personalized Learning Roadmap Generator Module
Phase 9 & Section 2 Upgrades: Interactive Visual DAG, Weekly Sprints, and Calendar Export

Transforms prioritized skill gaps, prerequisite graphs, and portfolio projects
into structured visual learning flowcharts (ASCII diagrams, Mermaid graphs,
interactive DAG topologies, and weekly study sprint calendars with .ics export).
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
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
    dag_graph: Optional[Dict[str, Any]] = None
    study_calendar: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "career_id": self.career_id,
            "career_title": self.career_title,
            "weighted_readiness_pct": round(self.weighted_readiness_pct, 1),
            "total_estimated_hours": self.total_hours,
            "phases": self.phases,
            "ascii_diagram": self.ascii_diagram,
            "mermaid_diagram": self.mermaid_diagram,
            "capstone_project": self.capstone_project.to_dict() if self.capstone_project else None,
            "dag_graph": self.dag_graph,
            "study_calendar": self.study_calendar
        }


class RoadmapGenerator:
    """
    Generates structured, prerequisite-aware visual learning roadmaps,
    interactive DAG topologies, and weekly study calendars across multiple technical career paths.
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
        career_identifier: str,
        target_days: int = 60,
        daily_hours: float = 1.5
    ) -> VisualRoadmap:
        """
        Builds a full multi-format visual roadmap for a student and target career,
        including DAG topology and calendar study sprints.
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

        # 5. Build Interactive DAG Graph Model
        dag_graph = self.generate_dag_graph_model(student_skills, career_identifier)

        # 6. Build Weekly Study Sprint Calendar
        study_calendar = self.generate_study_sprint_calendar(student_skills, career_identifier, target_days, daily_hours)

        return VisualRoadmap(
            career_id=report.career_id,
            career_title=report.career_title,
            student_skills=report.student_normalized_skills,
            weighted_readiness_pct=report.weighted_readiness_pct,
            total_hours=report.total_estimated_study_hours,
            phases=phases_data,
            ascii_diagram=ascii_flow,
            mermaid_diagram=mermaid_code,
            capstone_project=capstone_project,
            dag_graph=dag_graph,
            study_calendar=study_calendar
        )

    def generate_dag_graph_model(
        self,
        student_skills: Union[List[str], str],
        career_identifier: str
    ) -> Dict[str, Any]:
        """
        Builds a complete Directed Acyclic Graph (DAG) model with nodes, statuses,
        directed prerequisite edges, and topological depth layers for interactive visual rendering.
        
        Node Statuses:
          - 'mastered': Already in student skills (Green)
          - 'ready': Missing skill with all prerequisites satisfied (Pulsing Amber)
          - 'locked': Missing skill with 1+ unmet prerequisites (Grayed out with lock)
        """
        report = self.rec_engine.generate_recommendations(student_skills, career_identifier)
        student_skills_set = {s.lower() for s in report.student_normalized_skills}
        
        # Load all career required skills
        career_skills_df = self.loader.get_career_requirements(report.career_id)
        prereqs_df = self.loader.skill_prerequisites

        # Map skill_id <-> skill_name
        skill_id_map = {row["skill_id"]: row["skill_name"] for _, row in self.loader.skills.iterrows()}
        skill_name_to_id = {row["skill_name"].lower(): row["skill_id"] for _, row in self.loader.skills.iterrows()}

        # Career skill IDs
        career_skill_ids = set(career_skills_df["skill_id"].tolist())

        # Build adjacency maps for career scope
        prereq_map = defaultdict(list)  # skill_id -> list of parent skill_ids
        unlock_map = defaultdict(list)  # skill_id -> list of child skill_ids
        edge_reasons = {}

        for _, row in prereqs_df.iterrows():
            target = row["skill_id"]
            parent = row["prerequisite_skill_id"]
            if target in career_skill_ids or parent in career_skill_ids:
                prereq_map[target].append(parent)
                unlock_map[parent].append(target)
                edge_reasons[(parent, target)] = row["reason"]

        # Build Nodes
        nodes = []
        node_ids_in_graph = set()

        # Step map from recommendation roadmap
        step_map = {rec.skill_id: rec.step_number for rec in report.skill_recommendations}
        rec_map = {rec.skill_id: rec for rec in report.skill_recommendations}

        for _, row in career_skills_df.iterrows():
            sid = row["skill_id"]
            sname = row["skill_name"]
            is_mastered = sname.lower() in student_skills_set or sid in student_skills_set
            
            # Prerequisite IDs for this skill
            all_prereqs = prereq_map.get(sid, [])
            unmet_prereqs = [skill_id_map.get(p, p) for p in all_prereqs if skill_id_map.get(p, "").lower() not in student_skills_set]

            if is_mastered:
                status = "mastered"
            elif len(unmet_prereqs) == 0:
                status = "ready"
            else:
                status = "locked"

            rec_item = rec_map.get(sid)
            hours = rec_item.total_estimated_hours if rec_item else 15
            difficulty = row.get("difficulty_level", "Intermediate")
            importance = row.get("importance_level", "Core")
            category = row.get("category", "Technical")

            nodes.append({
                "id": sid,
                "name": sname,
                "status": status,  # 'mastered' | 'ready' | 'locked'
                "step": step_map.get(sid, 0),
                "category": category,
                "importance": importance,
                "difficulty": difficulty,
                "estimated_hours": hours,
                "unmet_prerequisites": unmet_prereqs,
                "unlocks_count": len(unlock_map.get(sid, [])),
                "resources": [
                    {"title": r.title, "platform": r.platform, "url": r.url_or_ref}
                    for r in (rec_item.resources if rec_item else [])
                ]
            })
            node_ids_in_graph.add(sid)

        # Build Directed Edges
        edges = []
        for (parent, target), reason in edge_reasons.items():
            if parent in node_ids_in_graph and target in node_ids_in_graph:
                edges.append({
                    "from": parent,
                    "to": target,
                    "reason": reason,
                    "is_active": parent not in student_skills_set  # active blocker if parent unmet
                })

        # Calculate Topological Layering for SVG rendering
        # Layer 0: Mastered or nodes with 0 prereqs; Layer k: max(prereqs layer) + 1
        node_layers = {}
        for n in nodes:
            if n["status"] == "mastered":
                node_layers[n["id"]] = 0
            elif not prereq_map.get(n["id"]):
                node_layers[n["id"]] = 1

        # Iterative layer assignment
        changed = True
        iterations = 0
        while changed and iterations < 10:
            changed = False
            iterations += 1
            for n in nodes:
                nid = n["id"]
                parents = [p for p in prereq_map.get(nid, []) if p in node_ids_in_graph]
                if parents:
                    parent_layers = [node_layers.get(p, 0) for p in parents]
                    new_layer = max(parent_layers) + 1
                    if node_layers.get(nid) != new_layer:
                        node_layers[nid] = new_layer
                        changed = True

        for n in nodes:
            n["layer"] = node_layers.get(n["id"], 1)

        # Sort nodes by layer and step
        nodes.sort(key=lambda x: (x["layer"], x["step"]))

        return {
            "career_id": report.career_id,
            "career_title": report.career_title,
            "total_nodes": len(nodes),
            "mastered_count": sum(1 for n in nodes if n["status"] == "mastered"),
            "ready_count": sum(1 for n in nodes if n["status"] == "ready"),
            "locked_count": sum(1 for n in nodes if n["status"] == "locked"),
            "nodes": nodes,
            "edges": edges,
            "capstone_project": report.recommended_projects[0].to_dict() if report.recommended_projects else None
        }

    def generate_study_sprint_calendar(
        self,
        student_skills: Union[List[str], str],
        career_identifier: str,
        target_days: int = 60,
        daily_hours: float = 1.5
    ) -> Dict[str, Any]:
        """
        Generates daily/weekly study sprints, milestone targets, and calendar schedules
        adapting to the student's target placement timeline.
        """
        report = self.rec_engine.generate_recommendations(student_skills, career_identifier)
        total_hours = report.total_estimated_study_hours
        
        # Calculate available study capacity
        total_capacity_hours = max(1.0, target_days * daily_hours)
        pace_multiplier = total_capacity_hours / max(1.0, total_hours)
        
        num_weeks = max(1, (target_days + 6) // 7)
        weekly_sprints = []

        # Distribute skill gaps across weeks
        missing_skills = report.skill_recommendations
        if not missing_skills:
            # All satisfied
            return {
                "career_title": report.career_title,
                "target_days": target_days,
                "daily_hours": daily_hours,
                "total_study_hours": 0,
                "total_weeks": 1,
                "pace_status": "Placement Ready",
                "weekly_sprints": [
                    {
                        "week_number": 1,
                        "title": "Capstone Portfolio & Interview Prep",
                        "objective": "Build final capstone deliverable and take mock interviews.",
                        "hours": 10,
                        "skills": [],
                        "deliverable": "Capstone Portfolio Repository"
                    }
                ],
                "ical_content": self.generate_icalendar_ics(report.career_title, [])
            }

        # Chunk skills proportionally across available weeks
        hours_per_week = total_hours / float(num_weeks)
        current_week = 1
        current_week_hours = 0
        current_week_skills = []

        for skill in missing_skills:
            current_week_skills.append({
                "step": skill.step_number,
                "name": skill.skill_name,
                "hours": skill.total_estimated_hours,
                "difficulty": skill.difficulty_level,
                "top_resource": skill.resources[0].title if skill.resources else "Documentation"
            })
            current_week_hours += skill.total_estimated_hours

            if current_week_hours >= hours_per_week and current_week < num_weeks:
                weekly_sprints.append({
                    "week_number": current_week,
                    "title": f"Week {current_week}: {current_week_skills[0]['name']} & Core Foundations",
                    "objective": f"Master {len(current_week_skills)} prioritized competencies ({', '.join(s['name'] for s in current_week_skills)}).",
                    "hours": round(current_week_hours, 1),
                    "skills": current_week_skills,
                    "deliverable": f"Mini Project / Quiz Gate on {current_week_skills[-1]['name']}"
                })
                current_week += 1
                current_week_hours = 0
                current_week_skills = []

        # Add remaining
        if current_week_skills:
            weekly_sprints.append({
                "week_number": current_week,
                "title": f"Week {current_week}: Advanced Implementation & Capstone",
                "objective": f"Complete remaining skill gaps and build hands-on portfolio proof.",
                "hours": round(current_week_hours, 1),
                "skills": current_week_skills,
                "deliverable": report.recommended_projects[0].title if report.recommended_projects else "Comprehensive Portfolio Artifact"
            })

        # Generate iCalendar standard .ics content
        ical_str = self.generate_icalendar_ics(report.career_title, weekly_sprints)
        notion_md = self.generate_notion_markdown(report.career_title, weekly_sprints, target_days, daily_hours)

        return {
            "career_title": report.career_title,
            "target_days": target_days,
            "daily_hours": daily_hours,
            "total_study_hours": total_hours,
            "total_weeks": len(weekly_sprints),
            "pace_status": "Optimal Sprint Velocity" if pace_multiplier >= 1.0 else "Intensive Accelerated Sprint",
            "weekly_sprints": weekly_sprints,
            "ical_content": ical_str,
            "notion_markdown": notion_md
        }

    def generate_icalendar_ics(
        self,
        career_title: str,
        weekly_sprints: List[Dict[str, Any]]
    ) -> str:
        """
        Generates standard RFC 5545 iCalendar (.ics) format compatible with
        Google Calendar, Apple Calendar, and Microsoft Outlook.
        """
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//SkillGap AI//Placement Readiness Platform//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            f"X-WR-CALNAME:SkillGap AI - {career_title} Study Plan",
            "X-WR-TIMEZONE:UTC"
        ]

        base_date = datetime.now()

        for sprint in weekly_sprints:
            week_num = sprint["week_number"]
            start_date = base_date + timedelta(days=(week_num - 1) * 7)
            end_date = start_date + timedelta(days=6)
            
            dtstart_str = start_date.strftime("%Y%m%d")
            dtend_str = end_date.strftime("%Y%m%d")
            uid = f"sprint-week-{week_num}-{career_title.lower().replace(' ', '-')[:12]}@skillgap.ai"
            
            summary = f"🚀 [SkillGap AI] {sprint['title']}"
            skills_text = "\\n".join([f"- {s['name']} (~{s['hours']}h)" for s in sprint.get("skills", [])])
            description = f"Objective: {sprint['objective']}\\n\\nWeekly Skills:\\n{skills_text}\\n\\nDeliverable: {sprint.get('deliverable', 'Quiz Gate')}"

            lines.extend([
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
                f"DTSTART;VALUE=DATE:{dtstart_str}",
                f"DTEND;VALUE=DATE:{dtend_str}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{description}",
                "STATUS:CONFIRMED",
                "BEGIN:VALARM",
                "TRIGGER:-PT15M",
                "ACTION:DISPLAY",
                f"DESCRIPTION:Reminder: Daily study sprint for {career_title}",
                "END:VALARM",
                "END:VEVENT"
            ])

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines)

    def generate_notion_markdown(
        self,
        career_title: str,
        weekly_sprints: List[Dict[str, Any]],
        target_days: int,
        daily_hours: float
    ) -> str:
        """
        Generates structured Notion / Markdown study plan ready to paste into Notion.
        """
        md = [
            f"# 🎯 {career_title} Study Sprint Database",
            f"> **Target Timeline:** {target_days} Days | **Daily Effort:** {daily_hours} hrs/day | **Generated By:** SkillGap AI",
            "",
            "## 📅 Sprint Overview",
            "| Week | Focus Module | Est. Hours | Target Deliverable | Status |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]

        for s in weekly_sprints:
            skills_joined = ", ".join([sk["name"] for sk in s.get("skills", [])]) or "Capstone Prep"
            md.append(f"| Week {s['week_number']} | {skills_joined} | {s['hours']}h | {s['deliverable']} | ⏳ In Progress |")

        md.append("")
        md.append("## 📝 Daily Action Checklists")
        for s in weekly_sprints:
            md.append(f"### 📌 Week {s['week_number']}: {s['title']}")
            md.append(f"**Objective:** {s['objective']}")
            for sk in s.get("skills", []):
                md.append(f"- [ ] **{sk['name']}** (~{sk['hours']}h) - Resource: {sk['top_resource']}")
            md.append(f"- [ ] **Weekly Milestone:** Complete {s['deliverable']}")
            md.append("")

        return "\n".join(md)

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

        if report.student_normalized_skills:
            mermaid_lines.append("\n  subgraph Already_Mastered [Already Mastered / Matched Skills]")
            for i, skill in enumerate(report.student_normalized_skills):
                safe_id = f"MASTERED_{i}"
                mermaid_lines.append(f'    {safe_id}["✓ {skill}"]:::matched')
            mermaid_lines.append("  end")

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

            for i in range(len(phase_nodes) - 1):
                mermaid_lines.append(f"    {phase_nodes[i]} --> {phase_nodes[i+1]}")

            mermaid_lines.append("  end")

            if prev_phase_last_node and phase_nodes:
                mermaid_lines.append(f"  {prev_phase_last_node} ==> {phase_nodes[0]}")
            
            if phase_nodes:
                prev_phase_last_node = phase_nodes[-1]

        if capstone:
            cap_id = "CAPSTONE_PROJECT"
            mermaid_lines.append(f'\n  {cap_id}[("★ Capstone: {capstone.title}")]:::projectNode')
            if prev_phase_last_node:
                mermaid_lines.append(f"  {prev_phase_last_node} ==> {cap_id}")

        mermaid_lines.append("```")
        return "\n".join(mermaid_lines)
