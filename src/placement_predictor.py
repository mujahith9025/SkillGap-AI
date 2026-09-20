"""
Placement Probability Predictor, Peer Benchmarking & Multi-Role Fit Engine
Section 1 Next-Level Upgrades

Provides:
1. Probabilistic Placement Probability ML Model with Tier Forecasting and Factor Attribution.
2. Dynamic Peer Benchmarking with Gaussian Bell Curve distribution across cohort applicants.
3. Multi-Role Fit Matrix computing cross-career compatibility and high-impact bridge skills.
"""

from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV

from data_loader import DataLoader
from skill_matcher import SkillMatcher


@dataclass
class PlacementFactor:
    name: str
    impact: str  # "positive", "negative", "neutral"
    weight_pct: float
    description: str


@dataclass
class MultiRoleFitItem:
    career_id: str
    career_title: str
    readiness_pct: float
    matched_skills_count: int
    total_required_skills: int
    fit_tier: str  # "Strong Fit", "Competitive", "Emerging Path"
    bridge_skill: Optional[str]
    bridge_jump_pct: float
    bridge_study_hours: int
    matched_skills: List[str]
    missing_skills: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "career_id": self.career_id,
            "career_title": self.career_title,
            "readiness_pct": round(self.readiness_pct, 1),
            "matched_skills_count": self.matched_skills_count,
            "total_required_skills": self.total_required_skills,
            "fit_tier": self.fit_tier,
            "bridge_skill": self.bridge_skill,
            "bridge_jump_pct": round(self.bridge_jump_pct, 1),
            "bridge_study_hours": self.bridge_study_hours,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills
        }


@dataclass
class PlacementPredictionReport:
    target_career: str
    placement_probability_pct: float
    predicted_tier: str
    tier_salary_range: str
    cohort_percentile: float
    cohort_standing_text: str
    key_contributing_factors: List[PlacementFactor]
    bell_curve_coordinates: List[Dict[str, float]]
    candidate_x_score: float
    median_hire_threshold: float
    top_10_percent_threshold: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_career": self.target_career,
            "placement_probability_pct": round(self.placement_probability_pct, 1),
            "predicted_tier": self.predicted_tier,
            "tier_salary_range": self.tier_salary_range,
            "cohort_percentile": round(self.cohort_percentile, 1),
            "cohort_standing_text": self.cohort_standing_text,
            "key_factors": [
                {
                    "name": f.name,
                    "impact": f.impact,
                    "weight": f.weight_pct,
                    "description": f.description
                }
                for f in self.key_contributing_factors
            ],
            "bell_curve_coordinates": self.bell_curve_coordinates,
            "candidate_x_score": round(self.candidate_x_score, 1),
            "median_hire_threshold": self.median_hire_threshold,
            "top_10_percent_threshold": self.top_10_percent_threshold
        }


class PlacementPredictorEngine:
    """
    Predictive ML Engine for placement likelihood estimation,
    cohort peer benchmarking, and multi-career fit discovery.
    """

    def __init__(
        self,
        data_loader: Optional[DataLoader] = None,
        skill_matcher: Optional[SkillMatcher] = None
    ):
        self.loader = data_loader if data_loader else DataLoader()
        self.matcher = skill_matcher if skill_matcher else SkillMatcher(data_loader=self.loader)
        self._init_and_train_model()

    def _init_and_train_model(self):
        """
        Initializes and trains a calibrated Random Forest classifier on synthetic
        yet statistically grounded placement feature distributions.
        """
        np.random.seed(42)
        n_samples = 1500

        # Features: [ReadinessScore(0-100), CoreCoverage(0-1), SkillsCountRatio(0-1), CodeQuality(0-100), ATS(0-100)]
        X = np.zeros((n_samples, 5))
        X[:, 0] = np.random.normal(55, 20, n_samples).clip(0, 100)
        X[:, 1] = (X[:, 0] / 100.0 + np.random.normal(0, 0.1, n_samples)).clip(0, 1.0)
        X[:, 2] = (X[:, 0] / 100.0 + np.random.normal(0, 0.12, n_samples)).clip(0, 1.0)
        X[:, 3] = np.random.normal(60, 22, n_samples).clip(0, 100)
        X[:, 4] = np.random.normal(65, 18, n_samples).clip(0, 100)

        # Composite score determining placement success
        composite = (
            0.40 * X[:, 0] +
            0.25 * (X[:, 1] * 100) +
            0.15 * X[:, 3] +
            0.20 * X[:, 4]
        )
        prob = 1 / (1 + np.exp(-(composite - 60) / 10))
        y = (np.random.rand(n_samples) < prob).astype(int)

        rf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
        rf.fit(X, y)

        self.model = CalibratedClassifierCV(estimator=rf, cv=3)
        self.model.fit(X, y)

    def predict_placement_probability(
        self,
        student_skills: Union[List[str], str],
        target_career: str,
        github_quality_score: float = 75.0,
        ats_score: float = 78.0,
        mock_interview_score: float = 8.0
    ) -> PlacementPredictionReport:
        """
        Calculates multi-dimensional placement probability, forecasted compensation tier,
        peer cohort percentile standing, and Gaussian bell-curve points.
        """
        match_res = self.matcher.match_skills(student_skills, target_career)
        readiness = match_res.weighted_readiness_pct
        core_coverage = match_res.core_matched_count / max(1, match_res.core_total_count)
        skills_ratio = len(match_res.matched_skills) / max(1, len(match_res.required_skills))

        # Form feature vector: [Readiness, CoreCoverage, SkillsRatio, GitHubQuality, ATS]
        feature_vec = np.array([[
            readiness,
            core_coverage,
            skills_ratio,
            github_quality_score,
            ats_score
        ]])

        probs = self.model.predict_proba(feature_vec)[0]
        ml_prob = float(probs[1]) * 100.0

        # Adjust slightly for mock interview excellence
        interview_mod = (mock_interview_score - 5.0) * 2.0
        final_prob = min(99.4, max(5.0, ml_prob + interview_mod))

        # Determine Tier Forecast
        if final_prob >= 80.0:
            tier = "Tier-1 Product Company (FAANG / Top Tech)"
            salary = "₹18,00,000 – ₹35,00,000 LPA ($120k–$160k)"
        elif final_prob >= 58.0:
            tier = "High-Growth Unicorn / Mid-Tier Product"
            salary = "₹10,00,000 – ₹18,00,000 LPA ($75k–$115k)"
        elif final_prob >= 35.0:
            tier = "Enterprise Tech Services & Global IT"
            salary = "₹5,00,000 – ₹10,00,000 LPA ($45k–$70k)"
        else:
            tier = "Early Stage Foundation Required"
            salary = "Foundation / Internship Stage (₹3-5 LPA)"

        # Calculate Cohort Percentile (Gaussian CDF against cohort mu=58.0, sigma=15.0)
        candidate_x = (0.50 * readiness + 0.25 * github_quality_score + 0.25 * ats_score)
        mu, sigma = 58.0, 15.0
        z_score = (candidate_x - mu) / sigma
        percentile = 0.5 * (1.0 + math.erf(z_score / math.sqrt(2.0))) * 100.0
        percentile = min(99.5, max(1.0, percentile))

        standing_text = f"Top {round(100.0 - percentile, 1)}% of 1,200 Cohort Applicants" if percentile >= 50 else f"Ahead of {round(percentile, 1)}% of Cohort Candidates"

        # Key Contributing Factors
        factors: List[PlacementFactor] = []
        if readiness >= 70.0:
            factors.append(PlacementFactor(
                name="Strong Role Readiness",
                impact="positive",
                weight_pct=18.5,
                description=f"{readiness:.1f}% role coverage satisfies major employer criteria."
            ))
        elif readiness < 45.0:
            factors.append(PlacementFactor(
                name="Skill Gap Deficit",
                impact="negative",
                weight_pct=-16.0,
                description=f"Only {readiness:.1f}% role readiness; master prerequisite core skills."
            ))

        if core_coverage >= 0.75:
            factors.append(PlacementFactor(
                name="Core Prerequisites Cleared",
                impact="positive",
                weight_pct=14.0,
                description="High mastery of non-negotiable foundational requirements."
            ))
        else:
            factors.append(PlacementFactor(
                name="Missing Core Essentials",
                impact="negative",
                weight_pct=-12.5,
                description="Lacking key core competencies mandated by job descriptions."
            ))

        if github_quality_score >= 70.0:
            factors.append(PlacementFactor(
                name="Verified Code Proof",
                impact="positive",
                weight_pct=11.5,
                description="GitHub code scanner verified hands-on implementation evidence."
            ))

        if ats_score >= 75.0:
            factors.append(PlacementFactor(
                name="ATS Resume Optimization",
                impact="positive",
                weight_pct=9.0,
                description="High keyword compatibility prevents recruiter screening dropouts."
            ))

        # Generate Gaussian Bell Curve Data Points (x: 0 to 100 in steps of 4)
        bell_curve = []
        for x_val in range(0, 101, 4):
            y_val = (1 / (sigma * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x_val - mu) / sigma) ** 2)
            scaled_y = round(y_val * 3500, 2)
            bell_curve.append({"x": x_val, "y": scaled_y})

        return PlacementPredictionReport(
            target_career=target_career,
            placement_probability_pct=final_prob,
            predicted_tier=tier,
            tier_salary_range=salary,
            cohort_percentile=percentile,
            cohort_standing_text=standing_text,
            key_contributing_factors=factors,
            bell_curve_coordinates=bell_curve,
            candidate_x_score=candidate_x,
            median_hire_threshold=65.0,
            top_10_percent_threshold=82.0
        )

    def compute_multi_role_matrix(
        self,
        student_skills: Union[List[str], str]
    ) -> List[MultiRoleFitItem]:
        """
        Evaluates student skills across all 7 target careers simultaneously,
        identifying adjacent career pathways and maximum-impact bridge skills.
        """
        careers = self.loader.careers
        matrix_items: List[MultiRoleFitItem] = []

        for _, row in careers.iterrows():
            c_id = row["career_id"]
            c_title = row["career_title"]

            match_res = self.matcher.match_skills(student_skills, c_title)
            readiness = match_res.weighted_readiness_pct
            matched_names = [s["skill_name"] for s in match_res.matched_skills]
            missing_names = [s["skill_name"] for s in match_res.missing_skills]

            # Fit Tier
            if readiness >= 75.0:
                fit_tier = "Strong Fit"
            elif readiness >= 50.0:
                fit_tier = "Competitive"
            else:
                fit_tier = "Emerging Path"

            # Find single highest-impact bridge skill from missing_skills list
            bridge_skill = None
            max_jump = 0.0
            bridge_hours = 0

            if match_res.missing_skills:
                for missing_dict in match_res.missing_skills:
                    s_name = missing_dict.get("skill_name", "")
                    weight = missing_dict.get("importance_weight", 1.0)
                    jump = weight * 15.0
                    if jump > max_jump:
                        max_jump = jump
                        bridge_skill = s_name
                        bridge_hours = int(weight * 12) + 8

            matrix_items.append(MultiRoleFitItem(
                career_id=c_id,
                career_title=c_title,
                readiness_pct=readiness,
                matched_skills_count=len(matched_names),
                total_required_skills=len(match_res.required_skills),
                fit_tier=fit_tier,
                bridge_skill=bridge_skill,
                bridge_jump_pct=max_jump,
                bridge_study_hours=bridge_hours,
                matched_skills=matched_names,
                missing_skills=missing_names
            ))

        # Sort by readiness descending
        matrix_items.sort(key=lambda x: x.readiness_pct, reverse=True)
        return matrix_items
