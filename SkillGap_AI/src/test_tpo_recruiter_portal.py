import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from tpo_recruiter_portal import (
    TPORecruiterPortalEngine,
    StudentCohortProfile,
    DepartmentSkillGapReport,
    AccreditationAuditReport,
    RecruiterCandidateMatch,
    PlacementCredential
)


class TestTPORecruiterPortalEngine:

    @pytest.fixture(autouse=True)
    def setup_engine(self):
        self.engine = TPORecruiterPortalEngine()

    def test_01_cohort_initialization_and_summary(self):
        """Verifies multi-department cohort loading and aggregate TPO placement metrics."""
        summary = self.engine.get_cohort_summary()
        assert summary["total_students"] == 60
        assert summary["avg_readiness_pct"] > 60.0
        assert summary["avg_placement_probability_pct"] > 65.0
        assert summary["placement_ready_count"] > 30
        assert summary["placement_ready_pct"] > 50.0
        assert "Placed (Tier 1)" in summary["status_breakdown"]
        assert len(summary["department_breakdown"]) == 4

        # Department specific filter
        cse_summary = self.engine.get_cohort_summary(department="Computer Science & Engineering")
        assert cse_summary["total_students"] == 15
        assert cse_summary["avg_readiness_pct"] > 60.0

    def test_02_department_gap_analysis_and_remedial_actions(self):
        """Verifies skill penetration auditing and actionable remedial workshop generation."""
        reports = self.engine.get_department_gap_analysis()
        assert len(reports) == 4

        for rep in reports:
            assert isinstance(rep, DepartmentSkillGapReport)
            assert rep.total_students == 15
            assert rep.avg_readiness_pct > 0.0
            assert len(rep.top_mastered_skills) > 0
            assert len(rep.critical_skill_deficits) > 0
            assert "Tier 1 (Dream >12 LPA)" in rep.tier_distribution
            
            # Check deficit structure
            first_deficit = rep.critical_skill_deficits[0]
            assert "skill_name" in first_deficit
            assert "actual_penetration_pct" in first_deficit
            assert "benchmark_target_pct" in first_deficit
            assert "deficit_pct" in first_deficit
            assert "remedial_action" in first_deficit
            assert "workshop" in first_deficit["remedial_action"].lower()

    def test_03_accreditation_audit_report_generation(self):
        """Verifies NAAC Criterion 5.2, NIRF Metric, and NBA Attainment generation."""
        audit = self.engine.generate_accreditation_audit_report(batch_year=2026)
        assert isinstance(audit, AccreditationAuditReport)
        assert audit.batch_year == 2026
        assert audit.total_students_assessed == 60
        assert audit.placement_eligible_pct > 60.0
        assert 0.0 <= audit.naac_criterion_5_score <= 4.0
        assert 0.0 <= audit.nirf_metric_score <= 100.0
        assert 0.0 <= audit.nba_outcome_attainment_pct <= 100.0
        assert len(audit.department_benchmarks) == 4
        assert len(audit.key_faculty_interventions) >= 3
        assert "# 🏛️ Formal Accreditation & Placement Audit Report" in audit.audit_markdown_summary

    def test_04_recruiter_candidate_search_multi_factor_matching(self):
        """Verifies recruiter candidate ranking against Job Description requirements."""
        jd_text = "Seeking Senior Data Scientist with expertise in Python, PyTorch, Deep Learning, Machine Learning, and SQL."
        matches = self.engine.search_candidates(jd_text_or_skills=jd_text, min_readiness=50.0, limit=10)
        
        assert len(matches) > 0
        assert len(matches) <= 10
        
        # Verify candidate ranking is descending by fit score
        for i in range(len(matches) - 1):
            assert matches[i].recruiter_fit_score >= matches[i + 1].recruiter_fit_score

        top_cand = matches[0]
        assert isinstance(top_cand, RecruiterCandidateMatch)
        assert top_cand.recruiter_fit_score > 75.0
        assert "Python" in top_cand.matched_jd_skills
        assert top_cand.recruiter_verdict in ["Tier-1 Immediate Hire", "High Match Candidate", "Promising Candidate"]

    def test_05_recruiter_candidate_search_with_strict_filters(self):
        """Verifies candidate search with department and GitHub star constraints."""
        matches = self.engine.search_candidates(
            jd_text_or_skills=["FastAPI", "Docker", "PostgreSQL"],
            department="Computer Science & Engineering",
            min_readiness=70.0,
            min_github_stars=10,
            limit=5
        )
        assert len(matches) > 0
        for m in matches:
            assert m.department == "Computer Science & Engineering"
            assert m.github_stars >= 10
            assert m.recruiter_fit_score > 60.0

    def test_06_placement_credential_issuance_and_cryptographic_verification(self):
        """Verifies SHA-256 digital certificate issuance and tamper-proof verification."""
        cred = self.engine.issue_placement_credential(
            student_id="STU-TEST-999",
            student_name="Vikram Test",
            department="AI & Data Science",
            target_career="Data Scientist",
            skills=["Python", "SQL", "PyTorch", "Docker"],
            readiness_score=88.5,
            ats_score=91.0,
            github_grade="Grade A (Modular OOP)"
        )

        assert cred.certificate_id.startswith("CERT-2026-")
        assert len(cred.sha256_signature) == 64
        assert "verify.placement-ai.edu" in cred.verification_url

        # Verify authentic certificate
        result = self.engine.verify_placement_credential(cred.certificate_id)
        assert result["is_valid"] is True
        assert result["status"] == "VERIFIED_AUTHENTIC"
        assert result["certificate"]["student_name"] == "Vikram Test"
        assert result["certificate"]["readiness_score"] == 88.5

        # Verify authentic certificate by signature hash prefix
        hash_res = self.engine.verify_placement_credential(cred.sha256_signature[:12])
        assert hash_res["is_valid"] is True

    def test_07_tampered_credential_rejection(self):
        """Verifies that unauthorized modifications to a certificate payload fail verification."""
        cred = self.engine.issue_placement_credential(
            student_id="STU-TEST-888",
            student_name="Sneha Test",
            department="Computer Science & Engineering",
            target_career="Backend Developer (Python)",
            skills=["Python", "FastAPI"],
            readiness_score=75.0,
            ats_score=80.0,
            github_grade="Grade B (Good)"
        )

        # Non-existent certificate check
        fake_res = self.engine.verify_placement_credential("CERT-FAKE-99999999")
        assert fake_res["is_valid"] is False
        assert fake_res["status"] == "INVALID_CERTIFICATE"

        # Tamper payload in memory: change readiness score without updating sha256 signature
        cred.readiness_score = 99.9
        tamper_res = self.engine.verify_placement_credential(cred.certificate_id)
        assert tamper_res["is_valid"] is False
        assert tamper_res["status"] == "TAMPERED_PAYLOAD"
