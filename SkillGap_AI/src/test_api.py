"""
Integration & Functional Tests for FastAPI Microservice Backend (api.py)
Tests all endpoints: Root, Health, Skill Analysis, ATS Scoring, Interview Eval, Vector Search, and GitHub Audit.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from api import app

client = TestClient(app)


def test_01_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text or "SkillGap AI" in response.text


def test_01_api_info_endpoint():
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Data Scientist" in data["supported_careers"]


def test_02_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["subsystems"]["vector_store_indexed_docs"] > 0


def test_03_analyze_skills_endpoint():
    payload = {
        "student_skills": ["Python", "SQL", "Pandas"],
        "target_career": "Data Scientist"
    }
    response = client.post("/api/v1/analyze-skills", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_career"] == "Data Scientist"
    assert "readiness_score_pct" in data
    assert "identified_gaps" in data
    assert "prerequisite_roadmap" in data
    assert len(data["recommended_projects"]) > 0


def test_04_ats_score_endpoint():
    payload = {
        "resume_text": "Experienced data scientist skilled in Python, SQL, and Scikit-Learn predictive modeling.",
        "job_description_text": "Looking for Data Scientist proficient in Python, SQL, and Machine Learning.",
        "target_career": "Data Scientist"
    }
    response = client.post("/api/v1/ats-score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_ats_score"] > 60.0
    assert "Python" in data["matched_keywords"] or "SQL" in data["matched_keywords"]
    assert "suggested_xyz_rewrite" in data
    assert "red_flags" in data
    assert len(data["red_flags"]) > 0
    assert "tailored_latex_preview" in data
    assert "\\documentclass" in data["tailored_latex_preview"]
    assert "tailored_html_preview" in data
    assert "highlighted_html_diff" in data["bullet_point_improvements"][0]


def test_05_interview_evaluate_endpoint():
    payload = {
        "skill_name": "SQL",
        "question_text": "What is the difference between WHERE and HAVING in SQL queries?",
        "candidate_answer": "WHERE filters rows before aggregation in GROUP BY, whereas HAVING filters groups after aggregation functions like COUNT, SUM, AVG."
    }
    response = client.post("/api/v1/interview/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] >= 7
    assert data["concept_coverage_pct"] > 0


def test_06_vector_search_endpoint():
    payload = {
        "query": "convolutional neural networks for computer vision",
        "top_k": 3,
        "doc_type": "all"
    }
    response = client.post("/api/v1/vector-search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] > 0
    assert len(data["results"]) > 0


def test_07_github_scan_endpoint():
    response = client.get("/api/v1/github-scan/sample_user")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "sample_user"
    assert "quality_score" in data
    assert "verified_skills" in data
    assert len(data["repositories"]) > 0


def test_08_upload_resume_pdf_endpoint():
    sample_pdf_path = PROJECT_ROOT / "data" / "test_resumes" / "sample_data_scientist_resume.pdf"
    if sample_pdf_path.exists():
        with open(sample_pdf_path, "rb") as f:
            response = client.post(
                "/api/v1/upload-resume",
                files={"file": ("sample_data_scientist_resume.pdf", f, "application/pdf")}
            )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["skill_count"] > 0
        assert "Python" in data["extracted_skills"] or "SQL" in data["extracted_skills"]
        assert len(data["detected_sections"]) > 0


def test_09_upload_resume_txt_endpoint():
    sample_text = b"Summary: Experienced Data Analyst with expertise in Python, SQL, Tableau, and Excel."
    response = client.post(
        "/api/v1/parse-resume",
        files={"file": ("resume.txt", sample_text, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert "Python" in data["extracted_skills"]
    assert "SQL" in data["extracted_skills"]
    assert data["skill_count"] >= 2


def test_10_placement_predict_endpoint():
    payload = {
        "student_skills": ["Python", "SQL", "Pandas", "Scikit-Learn", "Git & GitHub"],
        "target_career": "Data Scientist",
        "github_quality_score": 80.0,
        "ats_score": 75.0,
        "mock_interview_score": 8.0
    }
    response = client.post("/api/v1/placement-predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "placement_probability_pct" in data
    assert 0.0 <= data["placement_probability_pct"] <= 100.0
    assert "predicted_tier" in data
    assert "cohort_percentile" in data
    assert len(data["bell_curve_coordinates"]) > 0


def test_11_multi_role_matrix_endpoint():
    payload = {
        "student_skills": ["Python", "SQL", "Pandas", "Excel"],
        "target_career": "Data Scientist"
    }
    response = client.post("/api/v1/multi-role-matrix", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_roles_evaluated"] >= 7
    assert len(data["matrix"]) >= 7
    assert "bridge_skill" in data["matrix"][0]


def test_12_roadmap_dag_endpoint():
    payload = {
        "student_skills": ["Python", "SQL"],
        "target_career": "Data Scientist"
    }
    response = client.post("/api/v1/roadmap/dag", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["total_nodes"] > 0
    assert any(n["status"] == "mastered" for n in data["nodes"])


def test_13_roadmap_calendar_sprint_endpoint():
    payload = {
        "student_skills": ["Python", "SQL"],
        "target_career": "Data Scientist",
        "target_days": 60,
        "daily_hours": 1.5
    }
    response = client.post("/api/v1/roadmap/calendar-sprint", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "weekly_sprints" in data
    assert len(data["weekly_sprints"]) > 0
    assert "ical_content" in data
    assert "BEGIN:VCALENDAR" in data["ical_content"]


def test_14_quiz_generate_endpoint():
    payload = {
        "skill_name": "Python",
        "num_questions": 3
    }
    response = client.post("/api/v1/quiz/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["skill_name"] == "Python"
    assert len(data["questions"]) == 3
    assert len(data["questions"][0]["options"]) >= 3


def test_15_quiz_evaluate_endpoint():
    payload = {
        "skill_name": "Python",
        "user_answers": [0, 1, 1]
    }
    response = client.post("/api/v1/quiz/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "passed" in data
    assert "score" in data
    assert "question_evaluations" in data


def test_16_ats_generate_resume_endpoint():
    payload = {
        "student_skills": ["Python", "SQL", "Pandas"],
        "target_career": "Data Scientist",
        "job_description": "Looking for Data Scientist with PyTorch and Docker.",
        "candidate_name": "Jordan Smith",
        "candidate_email": "jordan@example.com"
    }
    response = client.post("/api/v1/ats/generate-resume", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "latex_code" in data
    assert "html_code" in data
    assert "\\documentclass" in data["latex_code"]
    assert "Jordan Smith" in data["latex_code"]
    assert "Jordan Smith" in data["html_code"]
    assert data["filename_tex"].endswith(".tex")


def test_17_ats_scan_red_flags_endpoint():
    payload = {
        "resume_text": "Responsible for helping with data entry. Worked on reports."
    }
    response = client.post("/api/v1/ats/scan-red-flags", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "total_flags" in data
    assert data["total_flags"] > 0
    assert data["critical_count"] >= 1
    assert any(f["category"] == "Contact Info" for f in data["flags"])


def test_18_coding_problems_endpoint():
    response = client.get("/api/v1/interview/coding-problems")
    assert response.status_code == 200
    data = response.json()
    assert "total_problems" in data
    assert data["total_problems"] >= 3
    assert len(data["problems"]) >= 3
    assert "starter_code" in data["problems"][0]


def test_19_run_code_endpoint():
    payload = {
        "problem_id": "py_two_sum",
        "code": "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i\n    return []",
        "language": "python"
    }
    response = client.post("/api/v1/interview/run-code", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "all_passed" in data
    assert data["all_passed"] is True
    assert data["passed_count"] == data["total_count"]
    assert len(data["test_results"]) > 0


def test_20_interview_follow_up_endpoint():
    payload = {
        "skill_name": "SQL",
        "question_id": "sql_01",
        "question_text": "What is the difference between WHERE and HAVING in SQL queries?",
        "candidate_answer": "WHERE is for row-level filtering before group by."
    }
    response = client.post("/api/v1/interview/follow-up", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "evaluation" in data
    assert "follow_up" in data
    assert "probe_text" in data["follow_up"]
    assert "SQL" in data["follow_up"]["skill_name"]


def test_21_github_analyze_code_endpoint():
    code = """
from typing import List

class MathEngine:
    def add(self, a: int, b: int) -> int:
        return a + b
"""
    response = client.post("/api/v1/github/analyze-code", json={"code_text": code, "file_name": "math_engine.py"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid_syntax"] is True
    assert data["classes_count"] == 1
    assert data["functions_count"] == 1
    assert data["avg_cyclomatic_complexity"] >= 1.0
    assert "Modular OOP" in data["oop_modularity_tier"]


def test_22_github_audit_readme_endpoint():
    readme = """# Machine Learning Pipeline
An enterprise prediction system.

```mermaid
graph TD
    A --> B
```

## Setup
```bash
pip install -r requirements.txt
```

## Live Demo
Check it out at https://demo.streamlit.app
"""
    response = client.post("/api/v1/github/audit-readme", json={"readme_text": readme})
    assert response.status_code == 200
    data = response.json()
    assert "overall_readme_score" in data
    assert data["overall_readme_score"] > 50.0
    assert data["has_architecture_diagram"] is True
    assert data["has_installation_steps"] is True


def test_23_github_generate_blueprint_endpoint():
    response = client.post("/api/v1/github/generate-blueprint", json={"missing_skill": "Docker", "target_career": "Data Scientist"})
    assert response.status_code == 200
    data = response.json()
    assert data["target_skill"] == "Docker"
    assert "folder_tree" in data
    assert len(data["milestones"]) >= 3
    assert "Dockerfile" in data["starter_files"]


def test_24_hybrid_search_endpoint():
    response = client.post(
        "/api/v1/vector/hybrid-search",
        json={"query": "Docker containerization microservices", "top_k": 3, "mode": "hybrid", "alpha": 0.5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "Docker containerization microservices"
    assert data["mode"] == "hybrid"
    assert len(data["results"]) > 0
    first = data["results"][0]
    assert "combined_score" in first
    assert "dense_score" in first
    assert "sparse_score" in first



def test_25_knowledge_graph_explore_endpoint():
    response = client.get("/api/v1/knowledge-graph/explore?target_skill=Machine%20Learning")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert "top_gateway_skills" in data
    assert len(data["nodes"]) >= 10
    assert len(data["edges"]) >= 5
    assert data["queried_skill"] == "Machine Learning"
    assert "prerequisite_chain" in data
    assert isinstance(data["prerequisite_chain"], list)



def test_26_rag_ask_endpoint():
    response = client.post(
        "/api/v1/rag/ask",
        json={"question": "How do I optimize SQL window queries?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert len(data["citations"]) > 0
    assert "key_takeaways" in data
    assert len(data["key_takeaways"]) > 0


def test_27_market_salary_estimator_endpoint():
    response = client.post(
        "/api/v1/market/salary-estimator",
        json={"student_skills": ["Python", "SQL", "Pandas"], "target_career": "Data Scientist"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["target_career"] == "Data Scientist"
    assert data["current_salary_usd"] > 50000
    assert data["current_salary_inr_lpa"] > 5.0
    assert "skill_value_deltas" in data
    assert len(data["skill_value_deltas"]) > 0
    assert "top_salary_boost_skills" in data


def test_28_market_hiring_heatmap_endpoint():
    response = client.get("/api/v1/market/hiring-heatmap")
    assert response.status_code == 200
    data = response.json()
    assert "hubs" in data
    assert data["total_hubs"] >= 7
    first_hub = data["hubs"][0]
    assert "hub_name" in first_hub
    assert "avg_salary_inr_lpa" in first_hub
    assert "lat" in first_hub


def test_29_market_skill_velocity_endpoint():
    response = client.get("/api/v1/market/skill-velocity")
    assert response.status_code == 200
    data = response.json()
    assert "velocity_metrics" in data
    assert data["total_skills_tracked"] >= 5
    first_m = data["velocity_metrics"][0]
    assert "mom_growth_pct" in first_m
    assert "historical_trajectory_6m" in first_m


def test_30_market_recalculate_readiness_endpoint():
    response = client.post(
        "/api/v1/market/recalculate-readiness",
        json={"student_skills": ["Python", "SQL", "Pandas", "Scikit-Learn"], "target_career": "Data Scientist"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "static_readiness_pct" in data
    assert "live_market_readiness_pct" in data
    assert "comparisons" in data
    assert len(data["comparisons"]) > 0


def test_31_tpo_cohort_summary_endpoint():
    response = client.get("/api/v1/tpo/cohort-summary?department=all")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "summary" in data
    assert data["summary"]["total_students"] == 60
    assert data["summary"]["avg_readiness_pct"] > 60.0


def test_32_tpo_department_gaps_endpoint():
    response = client.get("/api/v1/tpo/department-gaps?department=all")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "reports" in data
    assert data["total_reports"] == 4
    first_rep = data["reports"][0]
    assert "top_mastered_skills" in first_rep
    assert "critical_skill_deficits" in first_rep


def test_33_tpo_accreditation_audit_endpoint():
    response = client.get("/api/v1/tpo/accreditation-audit?batch_year=2026")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "audit_report" in data
    audit = data["audit_report"]
    assert audit["batch_year"] == 2026
    assert "naac_criterion_5_score" in audit
    assert "nirf_metric_score" in audit
    assert "audit_markdown_summary" in audit


def test_34_recruiter_search_candidates_endpoint():
    response = client.post(
        "/api/v1/recruiter/search-candidates",
        json={
            "jd_text": "Need Python and SQL developer with PyTorch and Machine Learning experience",
            "min_readiness": 50.0,
            "limit": 5
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "matches" in data
    assert len(data["matches"]) > 0
    top = data["matches"][0]
    assert "recruiter_fit_score" in top
    assert "matched_jd_skills" in top
    assert "recruiter_verdict" in top


def test_35_credentials_issue_and_verify_endpoint():
    # 1. Issue certificate
    issue_resp = client.post(
        "/api/v1/credentials/issue",
        json={
            "student_id": "STU-API-TEST-01",
            "student_name": "Divya Test",
            "department": "Computer Science & Engineering",
            "target_career": "Backend Developer (Python)",
            "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
            "readiness_score": 87.5,
            "ats_score": 90.0,
            "github_grade": "Grade A (Modular OOP)"
        }
    )
    assert issue_resp.status_code == 200
    issue_data = issue_resp.json()
    assert issue_data["status"] == "success"
    cred = issue_data["credential"]
    cert_id = cred["certificate_id"]
    assert cert_id.startswith("CERT-2026-")

    # 2. Verify certificate
    verify_resp = client.get(f"/api/v1/credentials/verify/{cert_id}")
    assert verify_resp.status_code == 200
    verify_data = verify_resp.json()
    assert verify_data["is_valid"] is True
    assert verify_data["status"] == "VERIFIED_AUTHENTIC"
    assert verify_data["certificate"]["student_name"] == "Divya Test"







