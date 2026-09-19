"""
Personalized Recommendation Engine Module
Phase 8: Personalized Recommendation Engine

Synthesizes skill gap analysis, prerequisite dependency graphs, curated learning resources,
and portfolio projects into an explainable, milestone-driven personalized learning roadmap.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import pandas as pd

from data_loader import DataLoader
from gap_analyzer import SkillGapAnalyzer, GapAnalysisResult, PrioritizedSkill


@dataclass
class LearningResourceItem:
    """Represents a curated learning resource connected to a skill."""
    resource_id: str
    title: str
    resource_type: str
    platform: str
    cost: str
    url_or_ref: str
    estimated_hours: int


@dataclass
class SkillRecommendation:
    """Detailed recommendation for an individual missing skill."""
    step_number: int
    skill_id: str
    skill_name: str
    category: str
    importance_level: str
    importance_weight: int
    difficulty_level: str
    priority_tier: str
    reason: str
    unlocks_skills: List[str]
    resources: List[LearningResourceItem]
    total_estimated_hours: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "skill_name": self.skill_name,
            "category": self.category,
            "importance_level": self.importance_level,
            "difficulty_level": self.difficulty_level,
            "priority_tier": self.priority_tier,
            "reason": self.reason,
            "unlocks_skills": self.unlocks_skills,
            "estimated_hours": self.total_estimated_hours,
            "resources": [
                {
                    "title": r.title,
                    "platform": r.platform,
                    "type": r.resource_type,
                    "cost": r.cost,
                    "url": r.url_or_ref,
                    "hours": r.estimated_hours
                }
                for r in self.resources
            ]
        }


@dataclass
class ProjectRecommendation:
    """Portfolio project recommendation linked to career and bridged skill gaps."""
    project_id: str
    title: str
    difficulty: str
    primary_skills: str
    description: str
    key_deliverables: str
    covered_gaps: List[str]
    relevance_score: float
    recommendation_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "title": self.title,
            "difficulty": self.difficulty,
            "primary_skills": self.primary_skills,
            "covered_gaps": self.covered_gaps,
            "relevance_score": round(self.relevance_score, 1),
            "recommendation_reason": self.recommendation_reason,
            "description": self.description,
            "key_deliverables": self.key_deliverables
        }


@dataclass
class RoadmapMilestone:
    """Structured learning phase bundling sequential skills and a practical project."""
    milestone_number: int
    milestone_title: str
    objective: str
    estimated_study_hours: int
    skills: List[SkillRecommendation]
    recommended_project: Optional[ProjectRecommendation] = None


@dataclass
class PersonalizedRecommendationReport:
    """Complete personalized recommendation package for a student."""
    career_id: str
    career_title: str
    student_normalized_skills: List[str]
    weighted_readiness_pct: float
    unweighted_coverage_pct: float
    total_estimated_study_hours: int
    milestones: List[RoadmapMilestone]
    skill_recommendations: List[SkillRecommendation]
    recommended_projects: List[ProjectRecommendation]


class RecommendationEngine:
    """
    Generates explainable, personalized skill, resource, and project recommendations.
    """

    def __init__(
        self,
        data_loader: Optional[DataLoader] = None,
        gap_analyzer: Optional[SkillGapAnalyzer] = None
    ):
        self.loader = data_loader if data_loader else DataLoader()
        self.gap_analyzer = gap_analyzer if gap_analyzer else SkillGapAnalyzer(data_loader=self.loader)

    def generate_recommendations(
        self,
        student_skills: Union[List[str], str],
        career_identifier: str
    ) -> PersonalizedRecommendationReport:
        """
        Synthesizes student skills, gaps, learning resources, and portfolio projects
        into an end-to-end personalized learning roadmap.
        """
        gap_res = self.gap_analyzer.analyze_gaps(student_skills, career_identifier)
        missing_skill_names = {s["skill_name"] for s in gap_res.missing_skills}

        # 1. Attach Learning Resources to each roadmap step
        skill_recs: List[SkillRecommendation] = []
        total_hours = 0

        for prioritized_s in gap_res.learning_roadmap:
            res_df = self.loader.get_resources_for_skill(prioritized_s.skill_id)
            resources_list: List[LearningResourceItem] = []
            skill_hours = 0

            for _, rrow in res_df.iterrows():
                hrs = int(rrow["estimated_hours"])
                item = LearningResourceItem(
                    resource_id=rrow["resource_id"],
                    title=rrow["title"],
                    resource_type=rrow["resource_type"],
                    platform=rrow["platform"],
                    cost=rrow["cost"],
                    url_or_ref=rrow["url_or_ref"],
                    estimated_hours=hrs
                )
                resources_list.append(item)
                skill_hours += hrs

            # If no explicit resource found, assign default estimate
            if skill_hours == 0:
                skill_hours = 15

            total_hours += skill_hours

            rec_item = SkillRecommendation(
                step_number=prioritized_s.step_number,
                skill_id=prioritized_s.skill_id,
                skill_name=prioritized_s.skill_name,
                category=prioritized_s.category,
                importance_level=prioritized_s.importance_level,
                importance_weight=prioritized_s.importance_weight,
                difficulty_level=prioritized_s.difficulty_level,
                priority_tier=prioritized_s.priority_tier,
                reason=prioritized_s.reason,
                unlocks_skills=prioritized_s.unlocks_skills,
                resources=resources_list,
                total_estimated_hours=skill_hours
            )
            skill_recs.append(rec_item)

        # 2. Match and Rank Portfolio Projects
        project_recs = self._recommend_projects(gap_res.career_id, missing_skill_names)

        # 3. Group into 3 Structured Milestones
        milestones = self._build_milestones(skill_recs, project_recs)

        return PersonalizedRecommendationReport(
            career_id=gap_res.career_id,
            career_title=gap_res.career_title,
            student_normalized_skills=gap_res.student_normalized_skills,
            weighted_readiness_pct=gap_res.weighted_readiness_pct,
            unweighted_coverage_pct=gap_res.unweighted_coverage_pct,
            total_estimated_study_hours=total_hours,
            milestones=milestones,
            skill_recommendations=skill_recs,
            recommended_projects=project_recs
        )

    def _recommend_projects(
        self,
        career_id: str,
        missing_skill_names: Set[str]
    ) -> List[ProjectRecommendation]:
        """
        Finds and scores portfolio projects that directly exercise the student's missing skills.
        """
        prj_df = self.loader.get_projects_for_career(career_id)
        if prj_df.empty:
            return []

        ranked_projects: List[ProjectRecommendation] = []

        for _, row in prj_df.iterrows():
            primary_skills_str = row["primary_skills"]
            # Parse skills in project
            proj_skills = [s.strip() for s in primary_skills_str.split(",") if s.strip()]
            
            # Find overlap with missing skills
            covered_gaps = [s for s in proj_skills if any(m.lower() in s.lower() or s.lower() in m.lower() for m in missing_skill_names)]
            
            # Relevance score = (covered_gaps count / total project skills) * 100
            relevance = (len(covered_gaps) / len(proj_skills) * 100.0) if proj_skills else 50.0

            if covered_gaps:
                reason = f"Provides hands-on implementation practice for {len(covered_gaps)} of your key skill gaps: {', '.join(covered_gaps)}."
            else:
                reason = "Reinforces core role architecture and placement portfolio readiness."

            rec = ProjectRecommendation(
                project_id=row["project_id"],
                title=row["title"],
                difficulty=row["difficulty"],
                primary_skills=primary_skills_str,
                description=row["description"],
                key_deliverables=row["key_deliverables"],
                covered_gaps=covered_gaps,
                relevance_score=relevance,
                recommendation_reason=reason
            )
            ranked_projects.append(rec)

        # Sort projects by relevance descending
        return sorted(ranked_projects, key=lambda p: p.relevance_score, reverse=True)

    def _build_milestones(
        self,
        skill_recs: List[SkillRecommendation],
        project_recs: List[ProjectRecommendation]
    ) -> List[RoadmapMilestone]:
        """
        Partitions the sequential roadmap into 3 progressive learning milestones.
        """
        if not skill_recs:
            return []

        n = len(skill_recs)
        # Partition sizes: ~1/3 each
        chunk_1 = skill_recs[:max(1, n // 3)]
        chunk_2 = skill_recs[max(1, n // 3):max(2, (2 * n) // 3)]
        chunk_3 = skill_recs[max(2, (2 * n) // 3):]

        milestone_data = [
            (1, "Milestone 1: Core Foundations & Tooling", "Master core programming, essential math, and foundational data wrangling.", chunk_1),
            (2, "Milestone 2: Primary Modeling & Domain Frameworks", "Build algorithmic proficiency, feature engineering, and core modeling workflows.", chunk_2),
            (3, "Milestone 3: Advanced Specialization & Deployment", "Implement deep neural architectures, production deployment, and cloud integration.", chunk_3),
        ]

        milestones: List[RoadmapMilestone] = []
        for idx, title, obj, chunk in milestone_data:
            if not chunk:
                continue
            hrs = sum(s.total_estimated_hours for s in chunk)
            
            # Link a project if available
            proj = project_recs[idx - 1] if (idx - 1) < len(project_recs) else (project_recs[0] if project_recs else None)
            
            milestones.append(RoadmapMilestone(
                milestone_number=idx,
                milestone_title=title,
                objective=obj,
                estimated_study_hours=hrs,
                skills=chunk,
                recommended_project=proj
            ))

        return milestones

    def format_recommendation_report(self, report: PersonalizedRecommendationReport) -> str:
        """Generates an explainable text summary of recommendations."""
        lines = []
        lines.append("=" * 75)
        lines.append(f" PERSONALIZED CAREER RECOMMENDATION PLAN: {report.career_title.upper()}")
        lines.append("=" * 75)
        lines.append(f"Student Baseline: {', '.join(report.student_normalized_skills)}")
        lines.append(f"Current Role Readiness: {report.weighted_readiness_pct:.1f}%")
        lines.append(f"Total Estimated Commitment: ~{report.total_estimated_study_hours} Hours")

        lines.append("\n" + "=" * 75)
        lines.append(" 1. STRUCTURED LEARNING ROADMAP BY MILESTONES")
        lines.append("=" * 75)

        for m in report.milestones:
            lines.append(f"\n--- {m.milestone_title.upper()} (~{m.estimated_study_hours} Hours) ---")
            lines.append(f"Objective: {m.objective}")
            lines.append("Skills to Master:")
            for s in m.skills:
                lines.append(f"  [{s.priority_tier} Priority] Step {s.step_number:2d}: {s.skill_name} ({s.category})")
                lines.append(f"    * Why Selected: {s.reason}")
                if s.resources:
                    lines.append(f"    * Top Resource: {s.resources[0].title} ({s.resources[0].platform} | {s.resources[0].cost})")
            
            if m.recommended_project:
                lines.append(f"\n  >> Milestone Capstone Project: {m.recommended_project.title}")
                lines.append(f"     Why: {m.recommended_project.recommendation_reason}")
                lines.append(f"     Deliverables: {m.recommended_project.key_deliverables}")

        lines.append("\n" + "=" * 75)
        lines.append(" 2. RECOMMENDED PORTFOLIO PROJECTS")
        lines.append("=" * 75)
        for i, p in enumerate(report.recommended_projects, 1):
            lines.append(f"\nProject {i}: {p.title} [{p.difficulty}]")
            lines.append(f"  * Relevance Score : {p.relevance_score:.1f}% Match to Your Skill Gaps")
            lines.append(f"  * Primary Skills  : {p.primary_skills}")
            lines.append(f"  * Why Recommended : {p.recommendation_reason}")
            lines.append(f"  * Scope Summary   : {p.description}")
            lines.append(f"  * Key Portfolio Deliverables: {p.key_deliverables}")

        lines.append("\n" + "=" * 75)
        return "\n".join(lines)
