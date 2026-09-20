"""
Skill Matching Engine Module
Phase 6: Basic Skill Matching Engine

Provides exact and normalized skill matching, gap identification,
weighted readiness score calculations, and multi-role ranking.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union, Tuple
import pandas as pd

from data_loader import DataLoader
from preprocessing import SkillPreprocessor


@dataclass
class SkillMatchResult:
    """Encapsulates the complete result of a skill matching evaluation."""
    career_id: str
    career_title: str
    student_raw_skills: List[str]
    student_normalized_skills: List[str]
    required_skills: List[Dict[str, Any]]
    matched_skills: List[Dict[str, Any]]
    missing_skills: List[Dict[str, Any]]
    extra_skills: List[str]
    unweighted_coverage_pct: float
    weighted_readiness_pct: float
    core_matched_count: int
    core_total_count: int
    secondary_matched_count: int
    secondary_total_count: int
    optional_matched_count: int
    optional_total_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Converts result into a serializable dictionary."""
        return {
            "career_id": self.career_id,
            "career_title": self.career_title,
            "student_normalized_skills": self.student_normalized_skills,
            "unweighted_coverage_pct": round(self.unweighted_coverage_pct, 2),
            "weighted_readiness_pct": round(self.weighted_readiness_pct, 2),
            "matched_count": len(self.matched_skills),
            "missing_count": len(self.missing_skills),
            "total_required_count": len(self.required_skills),
            "core_progress": f"{self.core_matched_count}/{self.core_total_count}",
            "secondary_progress": f"{self.secondary_matched_count}/{self.secondary_total_count}",
            "optional_progress": f"{self.optional_matched_count}/{self.optional_total_count}",
            "matched_skills": [s["skill_name"] for s in self.matched_skills],
            "missing_skills": [s["skill_name"] for s in self.missing_skills],
            "extra_skills": self.extra_skills,
        }


class SkillMatcher:
    """
    Evaluates student skill profiles against target career role benchmarks
    using normalized exact and alias matching.
    """

    def __init__(self, data_loader: Optional[DataLoader] = None, preprocessor: Optional[SkillPreprocessor] = None):
        self.loader = data_loader if data_loader else DataLoader()
        self.preprocessor = preprocessor if preprocessor else SkillPreprocessor(data_loader=self.loader)

    def _normalize_input_skills(self, student_skills: Union[List[str], str]) -> Tuple[List[str], List[str]]:
        """Normalizes raw input skills (string or list of strings)."""
        if isinstance(student_skills, str):
            raw_list = [s.strip() for s in student_skills.split(",") if s.strip()]
            normalized_list = self.preprocessor.parse_raw_text_skills(student_skills)
        elif isinstance(student_skills, list):
            raw_list = student_skills
            normalized_list = self.preprocessor.normalize_skill_list(student_skills)
        else:
            raw_list = []
            normalized_list = []
            
        return raw_list, normalized_list

    def match_skills(self, student_skills: Union[List[str], str], career_identifier: str) -> SkillMatchResult:
        """
        Matches a student's skills against a target career role.

        Args:
            student_skills: Free-form text string or list of skill names.
            career_identifier: Career title (e.g. 'Data Scientist') or ID ('CAR_01').

        Returns:
            SkillMatchResult with detailed matched, missing, and score metrics.
        """
        raw_skills, normalized_skills = self._normalize_input_skills(student_skills)
        normalized_skill_set = set(normalized_skills)

        # Retrieve career requirements from DataLoader
        req_df = self.loader.get_career_requirements(career_identifier)
        career_series = self.loader.get_career_by_title_or_id(career_identifier)
        if career_series is None:
            raise ValueError(f"Target career not found: {career_identifier}")

        career_id = career_series["career_id"]
        career_title = career_series["career_title"]

        required_skills: List[Dict[str, Any]] = []
        matched_skills: List[Dict[str, Any]] = []
        missing_skills: List[Dict[str, Any]] = []

        total_weight = 0
        matched_weight = 0

        core_total = 0
        core_matched = 0
        sec_total = 0
        sec_matched = 0
        opt_total = 0
        opt_matched = 0

        career_skill_names: Set[str] = set()

        for _, row in req_df.iterrows():
            skill_name = row["skill_name"]
            career_skill_names.add(skill_name)
            weight = int(row["importance_weight"])
            level = row["importance_level"]
            min_prof = row["min_proficiency"]
            
            skill_info = {
                "skill_id": row["skill_id"],
                "skill_name": skill_name,
                "category": row["category"],
                "difficulty_level": row["difficulty_level"],
                "importance_level": level,
                "importance_weight": weight,
                "min_proficiency": min_prof,
                "description": row["description_y"] if "description_y" in row else row["description"]
            }
            required_skills.append(skill_info)
            total_weight += weight

            # Track level totals
            if level == "Core":
                core_total += 1
            elif level == "Secondary":
                sec_total += 1
            elif level == "Optional":
                opt_total += 1

            # Check if student possesses this skill
            if skill_name in normalized_skill_set:
                matched_skills.append(skill_info)
                matched_weight += weight
                if level == "Core":
                    core_matched += 1
                elif level == "Secondary":
                    sec_matched += 1
                elif level == "Optional":
                    opt_matched += 1
            else:
                missing_skills.append(skill_info)

        # Calculate skills possessed by student that are not required for this career
        extra_skills = [s for s in normalized_skills if s not in career_skill_names]

        # Calculate metrics
        unweighted_cov = (len(matched_skills) / len(required_skills) * 100.0) if required_skills else 0.0
        weighted_readiness = (matched_weight / total_weight * 100.0) if total_weight > 0 else 0.0

        return SkillMatchResult(
            career_id=career_id,
            career_title=career_title,
            student_raw_skills=raw_skills,
            student_normalized_skills=normalized_skills,
            required_skills=required_skills,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            extra_skills=extra_skills,
            unweighted_coverage_pct=unweighted_cov,
            weighted_readiness_pct=weighted_readiness,
            core_matched_count=core_matched,
            core_total_count=core_total,
            secondary_matched_count=sec_matched,
            secondary_total_count=sec_total,
            optional_matched_count=opt_matched,
            optional_total_count=opt_total
        )

    def match_all_careers(self, student_skills: Union[List[str], str]) -> List[SkillMatchResult]:
        """
        Evaluates student skills against ALL careers in the database,
        returning a list sorted by weighted readiness percentage descending.
        """
        results = []
        for cid in self.loader.careers["career_id"]:
            res = self.match_skills(student_skills, cid)
            results.append(res)

        return sorted(results, key=lambda x: x.weighted_readiness_pct, reverse=True)

    def format_match_report(self, result: SkillMatchResult) -> str:
        """Generates an explainable text summary report of the match."""
        lines = []
        lines.append("=" * 70)
        lines.append(f" CAREER SKILL MATCH REPORT: {result.career_title.upper()} ({result.career_id})")
        lines.append("=" * 70)
        lines.append(f"Student Normalized Profile ({len(result.student_normalized_skills)} skills):")
        lines.append("  " + ", ".join(result.student_normalized_skills))
        lines.append("\nOverall Readiness Summary:")
        lines.append(f"  * Weighted Match Score : {result.weighted_readiness_pct:.1f}%")
        lines.append(f"  * Raw Skill Coverage   : {result.unweighted_coverage_pct:.1f}% ({len(result.matched_skills)}/{len(result.required_skills)} skills)")
        lines.append(f"  * Core Skills Progress : {result.core_matched_count}/{result.core_total_count} matched")
        lines.append(f"  * Secondary Skills     : {result.secondary_matched_count}/{result.secondary_total_count} matched")
        lines.append(f"  * Optional Skills      : {result.optional_matched_count}/{result.optional_total_count} matched")
        
        lines.append("\n[+] Matched Skills:")
        if result.matched_skills:
            for s in result.matched_skills:
                lines.append(f"    - {s['skill_name']:<30} [{s['importance_level']} | Weight: {s['importance_weight']}]")
        else:
            lines.append("    - None")

        lines.append("\n[-] Skill Gaps (Missing Skills to Acquire):")
        if result.missing_skills:
            for s in result.missing_skills:
                lines.append(f"    - {s['skill_name']:<30} [{s['importance_level']} | Weight: {s['importance_weight']}]")
        else:
            lines.append("    - No skill gaps! Profile satisfies all role requirements.")

        if result.extra_skills:
            lines.append(f"\n[*] Transferable / Auxiliary Skills Not in Target Role:")
            lines.append("    " + ", ".join(result.extra_skills))
            
        lines.append("=" * 70)
        return "\n".join(lines)
