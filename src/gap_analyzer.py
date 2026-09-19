"""
Skill Gap Analysis and Prioritization Module
Phase 7: Skill Gap Analysis and Prioritization

Provides explainable, graph-based skill gap prioritization and learning roadmap
sequencing using prerequisite DAG topological traversal, skill criticality weights,
and difficulty tier heuristics.
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field
import heapq
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import pandas as pd

from data_loader import DataLoader
from preprocessing import SkillPreprocessor
from skill_matcher import SkillMatcher, SkillMatchResult


@dataclass
class PrioritizedSkill:
    """Represents a prioritized missing skill within the learning sequence."""
    skill_id: str
    skill_name: str
    category: str
    importance_level: str
    importance_weight: int
    difficulty_level: str
    priority_tier: str  # 'High', 'Medium', 'Low'
    priority_score: float
    step_number: int
    unmet_prerequisites: List[str]
    unlocks_skills: List[str]
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "skill_name": self.skill_name,
            "category": self.category,
            "importance_level": self.importance_level,
            "importance_weight": self.importance_weight,
            "difficulty_level": self.difficulty_level,
            "priority_tier": self.priority_tier,
            "priority_score": round(self.priority_score, 2),
            "unmet_prerequisites": self.unmet_prerequisites,
            "unlocks_skills": self.unlocks_skills,
            "reason": self.reason
        }


@dataclass
class GapAnalysisResult:
    """Complete diagnostic result containing categorized gaps and sequenced roadmap."""
    career_id: str
    career_title: str
    student_normalized_skills: List[str]
    unweighted_coverage_pct: float
    weighted_readiness_pct: float
    matched_skills: List[Dict[str, Any]]
    missing_skills: List[Dict[str, Any]]
    high_priority_gaps: List[PrioritizedSkill]
    medium_priority_gaps: List[PrioritizedSkill]
    low_priority_gaps: List[PrioritizedSkill]
    learning_roadmap: List[PrioritizedSkill]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "career_title": self.career_title,
            "weighted_readiness_pct": round(self.weighted_readiness_pct, 1),
            "unweighted_coverage_pct": round(self.unweighted_coverage_pct, 1),
            "matched_count": len(self.matched_skills),
            "missing_count": len(self.missing_skills),
            "high_priority_count": len(self.high_priority_gaps),
            "medium_priority_count": len(self.medium_priority_gaps),
            "low_priority_count": len(self.low_priority_gaps),
            "learning_roadmap": [s.to_dict() for s in self.learning_roadmap]
        }


class SkillGapAnalyzer:
    """
    Analyzes skill gaps and computes dependency-aware, prioritized learning sequences
    using graph traversal and heuristic scoring.
    """

    DIFFICULTY_PENALTY = {
        "Beginner": 0.0,
        "Intermediate": 1.0,
        "Advanced": 2.0
    }

    def __init__(
        self,
        data_loader: Optional[DataLoader] = None,
        skill_matcher: Optional[SkillMatcher] = None
    ):
        self.loader = data_loader if data_loader else DataLoader()
        self.matcher = skill_matcher if skill_matcher else SkillMatcher(data_loader=self.loader)
        self._build_prerequisite_graph()

    def _build_prerequisite_graph(self):
        """Constructs adjacency maps and metadata from skill_prerequisites.csv."""
        self.prereq_graph = defaultdict(list)    # skill_id -> list of prerequisite skill_ids
        self.unlock_graph = defaultdict(list)    # prerequisite_skill_id -> list of dependent skill_ids
        self.prereq_reasons = {}                 # (skill_id, prereq_id) -> reason string
        
        prereqs_df = self.loader.skill_prerequisites
        for _, row in prereqs_df.iterrows():
            target_id = row["skill_id"]
            parent_id = row["prerequisite_skill_id"]
            self.prereq_graph[target_id].append(parent_id)
            self.unlock_graph[parent_id].append(target_id)
            self.prereq_reasons[(target_id, parent_id)] = row["reason"]

    def analyze_gaps(
        self,
        student_skills: Union[List[str], str],
        career_identifier: str
    ) -> GapAnalysisResult:
        """
        Performs full gap analysis and constructs a sequenced learning roadmap.
        """
        match_res = self.matcher.match_skills(student_skills, career_identifier)
        student_skill_names = set(match_res.student_normalized_skills)
        
        # Build map of skill_name -> skill_id
        skill_name_to_id = {row["skill_name"]: row["skill_id"] for _, row in self.loader.skills.iterrows()}
        skill_id_to_name = {row["skill_id"]: row["skill_name"] for _, row in self.loader.skills.iterrows()}
        student_skill_ids = {skill_name_to_id[s] for s in student_skill_names if s in skill_name_to_id}

        missing_skills_info = match_res.missing_skills
        missing_skill_ids = {s["skill_id"] for s in missing_skills_info}
        missing_dict_by_id = {s["skill_id"]: s for s in missing_skills_info}

        # -------------------------------------------------------------
        # 1. Compute Dependency Graph & Unmet Prerequisites for Gaps
        # -------------------------------------------------------------
        # For each missing skill, identify which prerequisites are still unmet
        unmet_prereqs_by_id = {}
        unmet_in_gap_by_id = {}
        unlocks_in_gap_by_id = {}

        for sid in missing_skill_ids:
            # Unmet prerequisites are prerequisites not possessed by the student
            all_prereqs = self.prereq_graph.get(sid, [])
            unmet = [p for p in all_prereqs if p not in student_skill_ids]
            unmet_prereqs_by_id[sid] = unmet
            
            # Prerequisite dependencies that are ALSO missing in the student's career gap set
            unmet_in_gap = [p for p in all_prereqs if p in missing_skill_ids and p not in student_skill_ids]
            unmet_in_gap_by_id[sid] = unmet_in_gap

            # Unlocked skills within this specific gap set
            unlocked = [d for d in self.unlock_graph.get(sid, []) if d in missing_skill_ids]
            unlocks_in_gap_by_id[sid] = unlocked

        # -------------------------------------------------------------
        # 2. Heuristic Priority Scoring Function
        # -------------------------------------------------------------
        # Score = (Importance_Weight * 10) + (Unlocks_Count * 5) - (Difficulty_Penalty * 2)
        priority_scores = {}
        for sid, sinfo in missing_dict_by_id.items():
            imp_weight = sinfo["importance_weight"]
            unlock_count = len(unlocks_in_gap_by_id[sid])
            diff_penalty = self.DIFFICULTY_PENALTY.get(sinfo["difficulty_level"], 1.0)
            
            # Base priority score
            score = (imp_weight * 10.0) + (unlock_count * 5.0) - (diff_penalty * 2.0)
            priority_scores[sid] = score

        # -------------------------------------------------------------
        # 3. Prerequisite-Aware Topological Roadmap Construction
        # -------------------------------------------------------------
        # We simulate progressive learning using Kahn's algorithm with priority queue
        in_degree = {sid: len(unmet_in_gap_by_id[sid]) for sid in missing_skill_ids}
        
        # State tracking
        current_student_mastery = set(student_skill_ids)
        available_queue = []  # max-heap based on priority_score: stores (-score, sid)

        for sid, deg in in_degree.items():
            if deg == 0:
                heapq.heappush(available_queue, (-priority_scores[sid], sid))

        roadmap: List[PrioritizedSkill] = []
        step = 1

        while available_queue:
            neg_score, sid = heapq.heappop(available_queue)
            score = -neg_score
            sinfo = missing_dict_by_id[sid]
            
            # Determine reason for sequencing
            unmet_names = [skill_id_to_name.get(p, p) for p in unmet_prereqs_by_id[sid]]
            unlock_names = [skill_id_to_name.get(u, u) for u in unlocks_in_gap_by_id[sid]]
            
            if sinfo["importance_level"] == "Core" and unlock_names:
                reason = f"Critical Core competency that also unlocks foundational concepts for {', '.join(unlock_names[:2])}."
            elif sinfo["importance_level"] == "Core":
                reason = "Primary core requirement essential for day-one job performance."
            elif unlock_names:
                reason = f"Unlocks advanced downstream technologies: {', '.join(unlock_names[:2])}."
            else:
                reason = f"{sinfo['importance_level']} skill for specialized domain readiness."

            # Determine Priority Tier
            if sinfo["importance_level"] == "Core" and len(unmet_prereqs_by_id[sid]) == 0:
                tier = "High"
            elif sinfo["importance_level"] == "Core" or (sinfo["importance_level"] == "Secondary" and len(unmet_prereqs_by_id[sid]) == 0):
                tier = "Medium"
            else:
                tier = "Low"

            prioritized_obj = PrioritizedSkill(
                skill_id=sid,
                skill_name=sinfo["skill_name"],
                category=sinfo["category"],
                importance_level=sinfo["importance_level"],
                importance_weight=sinfo["importance_weight"],
                difficulty_level=sinfo["difficulty_level"],
                priority_tier=tier,
                priority_score=score,
                step_number=step,
                unmet_prerequisites=unmet_names,
                unlocks_skills=unlock_names,
                reason=reason
            )
            roadmap.append(prioritized_obj)
            step += 1

            # Mark skill as learned and resolve downstream dependencies
            current_student_mastery.add(sid)
            for dependent_sid in self.unlock_graph.get(sid, []):
                if dependent_sid in in_degree:
                    in_degree[dependent_sid] -= 1
                    if in_degree[dependent_sid] == 0:
                        heapq.heappush(available_queue, (-priority_scores[dependent_sid], dependent_sid))

        # Handle any residual nodes if cycles exist or external prerequisites exist
        if len(roadmap) < len(missing_skills_info):
            remaining_sids = [sid for sid in missing_skill_ids if sid not in {s.skill_id for s in roadmap}]
            for sid in sorted(remaining_sids, key=lambda x: priority_scores[x], reverse=True):
                sinfo = missing_dict_by_id[sid]
                roadmap.append(PrioritizedSkill(
                    skill_id=sid,
                    skill_name=sinfo["skill_name"],
                    category=sinfo["category"],
                    importance_level=sinfo["importance_level"],
                    importance_weight=sinfo["importance_weight"],
                    difficulty_level=sinfo["difficulty_level"],
                    priority_tier="Low",
                    priority_score=priority_scores[sid],
                    step_number=step,
                    unmet_prerequisites=[skill_id_to_name.get(p, p) for p in unmet_prereqs_by_id[sid]],
                    unlocks_skills=[skill_id_to_name.get(u, u) for u in unlocks_in_gap_by_id[sid]],
                    reason="Scheduled following prerequisite completion."
                ))
                step += 1

        # -------------------------------------------------------------
        # 4. Group into High, Medium, Low Priority Buckets
        # -------------------------------------------------------------
        high_priority = [s for s in roadmap if s.priority_tier == "High"]
        medium_priority = [s for s in roadmap if s.priority_tier == "Medium"]
        low_priority = [s for s in roadmap if s.priority_tier == "Low"]

        return GapAnalysisResult(
            career_id=match_res.career_id,
            career_title=match_res.career_title,
            student_normalized_skills=match_res.student_normalized_skills,
            unweighted_coverage_pct=match_res.unweighted_coverage_pct,
            weighted_readiness_pct=match_res.weighted_readiness_pct,
            matched_skills=match_res.matched_skills,
            missing_skills=match_res.missing_skills,
            high_priority_gaps=high_priority,
            medium_priority_gaps=medium_priority,
            low_priority_gaps=low_priority,
            learning_roadmap=roadmap
        )

    def format_gap_report(self, result: GapAnalysisResult) -> str:
        """Formats the gap analysis and prioritized roadmap into an explainable report."""
        lines = []
        lines.append("=" * 75)
        lines.append(f" SKILL GAP & PRIORITIZED ROADMAP REPORT: {result.career_title.upper()}")
        lines.append("=" * 75)
        lines.append(f"Student Skill Base ({len(result.student_normalized_skills)} skills):")
        lines.append("  " + ", ".join(result.student_normalized_skills))
        lines.append(f"\nReadiness Status: {result.weighted_readiness_pct:.1f}% Weighted Match | {len(result.matched_skills)}/{len(result.matched_skills)+len(result.missing_skills)} Required Skills")
        
        lines.append("\n[+] Current Matched Skills:")
        if result.matched_skills:
            for s in result.matched_skills:
                lines.append(f"    * {s['skill_name']:<32} [{s['importance_level']} | Weight: {s['importance_weight']}]")
        else:
            lines.append("    * None")

        lines.append("\n[!] Skill Gaps by Priority Tier:")
        lines.append(f"  * HIGH PRIORITY ({len(result.high_priority_gaps)} skills - Critical immediate focus):")
        for s in result.high_priority_gaps:
            lines.append(f"      - {s.skill_name:<30} (Weight: {s.importance_weight}, {s.difficulty_level}) -> Score: {s.priority_score:.1f}")
            
        lines.append(f"  * MEDIUM PRIORITY ({len(result.medium_priority_gaps)} skills - Core/Secondary build-up):")
        for s in result.medium_priority_gaps:
            lines.append(f"      - {s.skill_name:<30} (Weight: {s.importance_weight}, {s.difficulty_level}) -> Score: {s.priority_score:.1f}")

        if result.low_priority_gaps:
            lines.append(f"  * LOW PRIORITY ({len(result.low_priority_gaps)} skills - Auxiliary/Specialized):")
            for s in result.low_priority_gaps:
                lines.append(f"      - {s.skill_name:<30} (Weight: {s.importance_weight}, {s.difficulty_level}) -> Score: {s.priority_score:.1f}")

        lines.append("\n" + "-" * 75)
        lines.append(" RECOMMENDED SEQUENTIAL LEARNING ROADMAP")
        lines.append("-" * 75)
        for s in result.learning_roadmap:
            lines.append(f"Step {s.step_number:2d}. [{s.priority_tier.upper()} PRIORITY] {s.skill_name} ({s.category})")
            lines.append(f"         Difficulty: {s.difficulty_level} | Importance: {s.importance_level} (Weight: {s.importance_weight})")
            lines.append(f"         Reason: {s.reason}")
            if s.unlocks_skills:
                lines.append(f"         Unlocks: {', '.join(s.unlocks_skills)}")
            lines.append("")

        lines.append("=" * 75)
        return "\n".join(lines)
