"""
FastAPI Microservice REST API Backend
Provides decoupled headless endpoints for Skill Gap Analysis, ATS Resume Scoring,
GitHub Code Auditing, Vector Search, and Technical Mock Interviews.

Swagger Documentation available at: http://localhost:8000/docs
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Add src directory to system path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from data_loader import DataLoader
from preprocessing import SkillPreprocessor
from skill_extractor import NLPSkillExtractor
from skill_matcher import SkillMatcher
from semantic_matcher import SemanticSkillMatcher
from gap_analyzer import SkillGapAnalyzer
from recommendation_engine import RecommendationEngine
from roadmap_generator import RoadmapGenerator
from resume_parser import ResumeParser
from interview_simulator import MockInterviewEngine
from job_market_scraper import JobMarketScraper
from github_scanner import GitHubProfileScanner
from ats_optimizer import ATSResumeOptimizer
from vector_store import PersistentVectorStore
from placement_predictor import PlacementPredictorEngine
from quiz_engine import QuizEngine
from tpo_recruiter_portal import TPORecruiterPortalEngine

# -----------------------------------------------------------------------------
# 1. APPLICATION INITIALIZATION
# -----------------------------------------------------------------------------
app = FastAPI(
    title="SkillGap AI REST API",
    description="Microservice API for Student Skill Gap Analysis, ATS Scoring, and Placement Recommendation",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
@app.get("/api/health")
def health_check():
    """Health check endpoint for cloud load balancers and deployment probes."""
    return {
        "status": "healthy",
        "service": "SkillGap AI",
        "version": "2.0.0",
        "subsystems": {
            "vector_store_indexed_docs": len(vector_store.doc_ids)
        }
    }

# Initialize engines
loader = DataLoader()
preprocessor = SkillPreprocessor(data_loader=loader)
extractor = NLPSkillExtractor(data_loader=loader, preprocessor=preprocessor)
matcher = SkillMatcher(data_loader=loader, preprocessor=preprocessor)
semantic_matcher = SemanticSkillMatcher(data_loader=loader)
gap_analyzer = SkillGapAnalyzer(data_loader=loader, skill_matcher=matcher)
rec_engine = RecommendationEngine(data_loader=loader, gap_analyzer=gap_analyzer)
roadmap_gen = RoadmapGenerator(data_loader=loader, recommendation_engine=rec_engine)
resume_parser = ResumeParser(data_loader=loader, skill_extractor=extractor)
interview_engine = MockInterviewEngine(data_loader=loader, semantic_matcher=semantic_matcher)
market_scraper = JobMarketScraper(data_loader=loader, skill_extractor=extractor)
github_scanner = GitHubProfileScanner(data_loader=loader, skill_extractor=extractor)
ats_optimizer = ATSResumeOptimizer(data_loader=loader, skill_extractor=extractor, semantic_matcher=semantic_matcher)
vector_store = PersistentVectorStore(semantic_matcher=semantic_matcher)
placement_predictor = PlacementPredictorEngine(data_loader=loader, skill_matcher=matcher)
quiz_engine = QuizEngine(data_loader=loader)
tpo_engine = TPORecruiterPortalEngine(data_loader=loader)


from interview_simulator import MockInterviewEngine, InterviewQuestion

# -----------------------------------------------------------------------------
# 2. REQUEST & RESPONSE SCHEMAS
# -----------------------------------------------------------------------------
class SkillAnalysisRequest(BaseModel):
    student_skills: Union[List[str], str] = Field(..., json_schema_extra={"example": ["Python", "SQL", "Pandas"]})
    target_career: str = Field(..., json_schema_extra={"example": "Data Scientist"})

class ATSScoreRequest(BaseModel):
    resume_text: str = Field(..., json_schema_extra={"example": "Experienced in Python, SQL, and Scikit-Learn data modeling."})
    job_description_text: str = Field(..., json_schema_extra={"example": "Looking for Data Scientist with Python, SQL, and Deep Learning."})
    target_career: Optional[str] = Field("Data Scientist", json_schema_extra={"example": "Data Scientist"})

class ATSGenerateResumeRequest(BaseModel):
    student_skills: Union[List[str], str] = Field(..., json_schema_extra={"example": ["Python", "SQL", "Pandas"]})
    target_career: str = Field(..., json_schema_extra={"example": "Data Scientist"})
    job_description: Optional[str] = Field("", json_schema_extra={"example": "Looking for Data Scientist with PyTorch and Docker."})
    candidate_name: Optional[str] = Field("Alex Chen", json_schema_extra={"example": "Alex Chen"})
    candidate_email: Optional[str] = Field("alex.chen@email.com", json_schema_extra={"example": "alex.chen@email.com"})
    candidate_phone: Optional[str] = Field("(555) 019-2834", json_schema_extra={"example": "(555) 019-2834"})
    candidate_linkedin: Optional[str] = Field("linkedin.com/in/alexchen-tech", json_schema_extra={"example": "linkedin.com/in/alexchen-tech"})
    candidate_github: Optional[str] = Field("github.com/alexchen-dev", json_schema_extra={"example": "github.com/alexchen-dev"})

class ATSRedFlagScanRequest(BaseModel):
    resume_text: str = Field(..., json_schema_extra={"example": "Responsible for helping with data processing."})


class InterviewEvalRequest(BaseModel):
    skill_name: str = Field(..., json_schema_extra={"example": "SQL"})
    question_text: str = Field(..., json_schema_extra={"example": "What is the difference between WHERE and HAVING?"})
    candidate_answer: str = Field(..., json_schema_extra={"example": "WHERE filters before GROUP BY, HAVING filters after aggregate functions."})

class RunCodeRequest(BaseModel):
    problem_id: str = Field(..., json_schema_extra={"example": "py_two_sum"})
    code: str = Field(..., json_schema_extra={"example": "def two_sum(nums, target):\n    return [0, 1]"})
    language: Optional[str] = Field("python", json_schema_extra={"example": "python"})

class FollowUpRequest(BaseModel):
    skill_name: str = Field(..., json_schema_extra={"example": "SQL"})
    question_id: Optional[str] = Field("sql_01", json_schema_extra={"example": "sql_01"})
    question_text: str = Field(..., json_schema_extra={"example": "What is the difference between WHERE and HAVING?"})
    candidate_answer: str = Field(..., json_schema_extra={"example": "WHERE is used for row-level filtering."})


class VectorSearchRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "machine learning classification"})
    top_k: int = Field(5, json_schema_extra={"example": 5})
    doc_type: Optional[str] = Field("all", json_schema_extra={"example": "all"})

class PlacementPredictRequest(BaseModel):
    student_skills: Union[List[str], str] = Field(..., json_schema_extra={"example": ["Python", "SQL", "Pandas"]})
    target_career: str = Field(..., json_schema_extra={"example": "Data Scientist"})
    github_quality_score: Optional[float] = Field(75.0, json_schema_extra={"example": 75.0})
    ats_score: Optional[float] = Field(78.0, json_schema_extra={"example": 78.0})
    mock_interview_score: Optional[float] = Field(8.0, json_schema_extra={"example": 8.0})

class CalendarSprintRequest(BaseModel):
    student_skills: Union[List[str], str] = Field(..., json_schema_extra={"example": ["Python", "SQL"]})
    target_career: str = Field(..., json_schema_extra={"example": "Data Scientist"})
    target_days: Optional[int] = Field(60, json_schema_extra={"example": 60})
    daily_hours: Optional[float] = Field(1.5, json_schema_extra={"example": 1.5})

class QuizGenerateRequest(BaseModel):
    skill_name: str = Field(..., json_schema_extra={"example": "SQL"})
    num_questions: Optional[int] = Field(3, json_schema_extra={"example": 3})

class QuizEvaluateRequest(BaseModel):
    skill_name: str = Field(..., json_schema_extra={"example": "SQL"})
    user_answers: List[int] = Field(..., json_schema_extra={"example": [0, 1, 1]})

class CodeAnalysisRequest(BaseModel):
    code_text: str = Field(..., json_schema_extra={"example": "def process_data(x: int) -> int:\n    return x * 2"})
    file_name: Optional[str] = Field("main.py", json_schema_extra={"example": "main.py"})

class ReadmeAuditRequest(BaseModel):
    readme_text: str = Field(..., json_schema_extra={"example": "# Project\nDetailed documentation..."})

class ProjectBlueprintRequest(BaseModel):
    missing_skill: str = Field(..., json_schema_extra={"example": "Docker"})
    target_career: Optional[str] = Field("Data Scientist", json_schema_extra={"example": "Data Scientist"})

class HybridSearchRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "SQL window functions and dense rank"})
    top_k: Optional[int] = Field(5, json_schema_extra={"example": 5})
    mode: Optional[str] = Field("hybrid", json_schema_extra={"example": "hybrid"})  # 'hybrid' | 'dense' | 'bm25'
    alpha: Optional[float] = Field(0.5, json_schema_extra={"example": 0.5})
    doc_type: Optional[str] = Field("all", json_schema_extra={"example": "all"})

class RAGAskRequest(BaseModel):
    question: str = Field(..., json_schema_extra={"example": "How do I optimize SQL window queries?"})

class SalaryEstimationRequest(BaseModel):
    student_skills: Union[List[str], str] = Field(..., json_schema_extra={"example": ["Python", "SQL", "Pandas"]})
    target_career: Optional[str] = Field("Data Scientist", json_schema_extra={"example": "Data Scientist"})

class RecalculateReadinessRequest(BaseModel):
    student_skills: Union[List[str], str] = Field(..., json_schema_extra={"example": ["Python", "SQL"]})
    target_career: Optional[str] = Field("Data Scientist", json_schema_extra={"example": "Data Scientist"})

class RecruiterSearchRequest(BaseModel):
    jd_text: Optional[str] = Field(None, json_schema_extra={"example": "Looking for Senior Data Scientist with Python, SQL, and PyTorch."})
    skills: Optional[Union[List[str], str]] = Field(None, json_schema_extra={"example": ["Python", "SQL", "PyTorch"]})
    target_career: Optional[str] = Field(None, json_schema_extra={"example": "Data Scientist"})
    min_readiness: Optional[float] = Field(0.0, json_schema_extra={"example": 60.0})
    min_ats: Optional[float] = Field(0.0, json_schema_extra={"example": 70.0})
    min_github_stars: Optional[int] = Field(0, json_schema_extra={"example": 5})
    department: Optional[str] = Field("all", json_schema_extra={"example": "all"})
    limit: Optional[int] = Field(20, json_schema_extra={"example": 10})

class IssueCredentialRequest(BaseModel):
    student_id: str = Field(..., json_schema_extra={"example": "STU-2026-001"})
    student_name: str = Field(..., json_schema_extra={"example": "Aarav Sharma"})
    department: str = Field(..., json_schema_extra={"example": "AI & Data Science"})
    target_career: str = Field(..., json_schema_extra={"example": "Data Scientist"})
    skills: Union[List[str], str] = Field(..., json_schema_extra={"example": ["Python", "SQL", "PyTorch"]})
    readiness_score: float = Field(..., json_schema_extra={"example": 88.5})
    ats_score: float = Field(..., json_schema_extra={"example": 89.0})
    github_grade: str = Field(..., json_schema_extra={"example": "Grade A (Modular OOP)"})
    institution: Optional[str] = Field("National Institute of Technology & Engineering", json_schema_extra={"example": "National Institute of Technology & Engineering"})


from fastapi.responses import FileResponse

# -----------------------------------------------------------------------------
# 3. ENDPOINTS
# -----------------------------------------------------------------------------
@app.get("/api")
@app.get("/api/info")
def api_info():
    return {
        "status": "online",
        "service": "SkillGap AI Backend Microservice",
        "version": "2.0.0",
        "docs_url": "/docs",
        "supported_careers": loader.careers["career_title"].tolist(),
        "total_taxonomy_skills": len(loader.skills)
    }

@app.get("/")
def serve_index_html():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return api_info()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SkillGap AI REST Microservice",
        "subsystems": {
            "data_loader": True,
            "skill_extractor": True,
            "semantic_matcher": True,
            "vector_store_indexed_docs": len(vector_store.doc_ids)
        }
    }

@app.post("/api/v1/upload-resume")
@app.post("/api/v1/parse-resume")
async def parse_resume_endpoint(file: UploadFile = File(...)):
    """
    Parses an uploaded resume file (PDF, TXT, MD), extracts document sections,
    and extracts verified technical skills using NLP and canonical taxonomy matching.
    """
    try:
        content = await file.read()
        filename = file.filename or "uploaded_resume.pdf"
        
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")
        
        if filename.lower().endswith((".txt", ".md")):
            raw_text = content.decode("utf-8", errors="ignore")
            sections_dict = resume_parser.segment_sections(raw_text)
            detected_sections = [s for s in sections_dict.keys() if s != "general"]
            extracted_entities = extractor.extract_skills(raw_text, include_negated=False)
            canonical_list = []
            seen = set()
            for entity in extracted_entities:
                if entity.canonical_name not in seen:
                    seen.add(entity.canonical_name)
                    canonical_list.append(entity.canonical_name)
            
            preview = raw_text[:250].replace("\n", " ").strip() + "..." if len(raw_text) > 250 else raw_text
            word_count = len(raw_text.split())
            character_count = len(raw_text)
            page_count = 1
            is_valid = word_count >= 5
            error_msg = None if is_valid else "Insufficient text extracted from file."
        else:
            profile = resume_parser.parse_resume(content, filename=filename)
            raw_text, page_count, error = resume_parser.extract_text(content)
            is_valid = profile.is_valid
            detected_sections = profile.detected_sections
            canonical_list = profile.extracted_canonical_skills
            preview = profile.text_preview
            word_count = profile.word_count
            character_count = profile.character_count
            error_msg = profile.error_message
            if not raw_text and profile.text_preview:
                raw_text = profile.text_preview

        return {
            "filename": filename,
            "is_valid": is_valid,
            "page_count": page_count,
            "word_count": word_count,
            "character_count": character_count,
            "detected_sections": detected_sections,
            "extracted_skills": canonical_list,
            "skill_count": len(canonical_list),
            "raw_text": raw_text,
            "text_preview": preview,
            "error_message": error_msg
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse resume: {str(e)}")

@app.post("/api/v1/analyze-skills")
def analyze_skills(req: SkillAnalysisRequest):
    """Performs end-to-end skill matching, gap analysis, roadmap construction, predictive placement ML, and multi-role fit matrix."""
    try:
        match_res = matcher.match_skills(req.student_skills, req.target_career)
        gap_res = gap_analyzer.analyze_gaps(req.student_skills, req.target_career)
        rec_report = rec_engine.generate_recommendations(req.student_skills, req.target_career)
        roadmap = roadmap_gen.generate_roadmap(req.student_skills, req.target_career)
        placement_report = placement_predictor.predict_placement_probability(req.student_skills, req.target_career)
        multi_role_matrix = placement_predictor.compute_multi_role_matrix(req.student_skills)

        return {
            "target_career": match_res.career_title,
            "career_title": match_res.career_title,
            "readiness_score_pct": match_res.weighted_readiness_pct,
            "weighted_readiness_pct": match_res.weighted_readiness_pct,
            "matched_skills": [s["skill_name"] for s in match_res.matched_skills],
            "missing_skills": [s["skill_name"] for s in match_res.missing_skills],
            "identified_gaps": [s.skill_name for s in gap_res.high_priority_gaps + gap_res.medium_priority_gaps],
            "high_priority_gaps": [s.skill_name for s in gap_res.high_priority_gaps],
            "estimated_hours": rec_report.total_estimated_study_hours,
            "prerequisite_roadmap": roadmap.phases,
            "roadmap_phases": roadmap.phases,
            "recommended_projects": [
                {
                    "title": p.title,
                    "difficulty": p.difficulty,
                    "relevance_score": p.relevance_score,
                    "primary_skills": p.primary_skills
                }
                for p in rec_report.recommended_projects
            ] if rec_report.recommended_projects else [],
            "capstone_project": roadmap.capstone_project.to_dict() if roadmap.capstone_project else None,
            "dag_graph": roadmap.dag_graph,
            "study_calendar": roadmap.study_calendar,
            "placement_prediction": placement_report.to_dict(),
            "multi_role_matrix": [item.to_dict() for item in multi_role_matrix]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/roadmap/dag")
def get_roadmap_dag(req: SkillAnalysisRequest):
    """Generates interactive Directed Acyclic Graph (DAG) topology with nodes, statuses, layers, and prerequisite edges."""
    try:
        dag = roadmap_gen.generate_dag_graph_model(req.student_skills, req.target_career)
        return dag
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/roadmap/calendar-sprint")
def get_calendar_sprints(req: CalendarSprintRequest):
    """Generates adaptive weekly study sprints, Notion markdown, and RFC 5545 standard .ics iCalendar file."""
    try:
        sprints = roadmap_gen.generate_study_sprint_calendar(
            student_skills=req.student_skills,
            career_identifier=req.target_career,
            target_days=req.target_days or 60,
            daily_hours=req.daily_hours or 1.5
        )
        return sprints
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/quiz/generate")
def generate_skill_quiz(req: QuizGenerateRequest):
    """Generates adaptive 3-question technical micro-quiz for competency gate validation."""
    try:
        questions = quiz_engine.get_quiz_for_skill(req.skill_name, num_questions=req.num_questions or 3)
        return {
            "skill_name": req.skill_name,
            "total_questions": len(questions),
            "questions": [q.to_dict(include_answer=False) for q in questions]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/quiz/evaluate")
def evaluate_skill_quiz(req: QuizEvaluateRequest):
    """Evaluates student quiz answers and determines mastery unlock status (threshold >= 66%)."""
    try:
        result = quiz_engine.evaluate_quiz(req.skill_name, req.user_answers)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/placement-predict")
def predict_placement_endpoint(req: PlacementPredictRequest):
    """Computes statistical placement probability, salary tiers, factors, and peer cohort percentile."""
    try:
        report = placement_predictor.predict_placement_probability(
            student_skills=req.student_skills,
            target_career=req.target_career,
            github_quality_score=req.github_quality_score or 75.0,
            ats_score=req.ats_score or 78.0,
            mock_interview_score=req.mock_interview_score or 8.0
        )
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/multi-role-matrix")
def multi_role_matrix_endpoint(req: SkillAnalysisRequest):
    """Computes cross-career compatibility matrix and high-impact bridge skills for all 7 careers."""
    try:
        matrix = placement_predictor.compute_multi_role_matrix(req.student_skills)
        return {
            "student_skills": req.student_skills,
            "total_roles_evaluated": len(matrix),
            "matrix": [item.to_dict() for item in matrix]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/ats-score")
def score_ats_resume(req: ATSScoreRequest):
    """Scores resume against a target job description, detects ATS red flags, generates diffs, and prepares tailored LaTeX/HTML templates."""
    try:
        audit = ats_optimizer.evaluate_ats_compatibility(
            resume_text=req.resume_text,
            job_description_text=req.job_description_text,
            target_career=req.target_career or "Data Scientist"
        )
        sample_bullet = "Built machine learning models using Python."
        xyz = ats_optimizer.suggest_xyz_rewrite(sample_bullet)
        return {
            "overall_ats_score": audit.overall_ats_score,
            "score_grade": audit.score_grade,
            "keyword_match_rate_pct": audit.keyword_match_rate_pct,
            "semantic_alignment_score": audit.semantic_alignment_score,
            "quantifiable_metrics_score": audit.quantifiable_metrics_score,
            "matched_keywords": audit.matched_jd_keywords,
            "missing_critical_keywords": audit.missing_critical_keywords,
            "formatting_recommendations": audit.formatting_recommendations,
            "suggested_xyz_rewrite": xyz,
            "bullet_point_improvements": [
                {
                    "original": b.original_bullet,
                    "improved": b.improved_bullet,
                    "formula": b.impact_technique_used,
                    "detected_weakness": b.detected_weakness,
                    "diff_added_tokens": b.diff_added_tokens,
                    "diff_removed_tokens": b.diff_removed_tokens,
                    "highlighted_html_diff": b.highlighted_html_diff
                }
                for b in audit.bullet_point_improvements
            ],
            "red_flags": [rf.to_dict() for rf in audit.red_flags],
            "tailored_latex_preview": audit.tailored_latex_preview,
            "tailored_html_preview": audit.tailored_html_preview
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/ats/generate-resume")
def generate_tailored_resume_endpoint(req: ATSGenerateResumeRequest):
    """Generates tailored single-column ATS LaTeX source code and print-ready HTML resume with injected keywords."""
    try:
        skills = req.student_skills if isinstance(req.student_skills, list) else [s.strip() for s in req.student_skills.split(",") if s.strip()]
        latex_code = ats_optimizer.generate_tailored_latex_resume(
            student_skills=skills,
            target_career=req.target_career,
            job_description=req.job_description or "",
            candidate_name=req.candidate_name or "Alex Chen",
            candidate_email=req.candidate_email or "alex.chen@email.com",
            candidate_phone=req.candidate_phone or "(555) 019-2834",
            candidate_linkedin=req.candidate_linkedin or "linkedin.com/in/alexchen-tech",
            candidate_github=req.candidate_github or "github.com/alexchen-dev"
        )
        html_code = ats_optimizer.generate_tailored_html_resume(
            student_skills=skills,
            target_career=req.target_career,
            job_description=req.job_description or "",
            candidate_name=req.candidate_name or "Alex Chen",
            candidate_email=req.candidate_email or "alex.chen@email.com",
            candidate_phone=req.candidate_phone or "(555) 019-2834",
            candidate_linkedin=req.candidate_linkedin or "linkedin.com/in/alexchen-tech",
            candidate_github=req.candidate_github or "github.com/alexchen-dev"
        )
        return {
            "target_career": req.target_career,
            "candidate_name": req.candidate_name,
            "latex_code": latex_code,
            "html_code": html_code,
            "filename_tex": f"Resume_{req.target_career.replace(' ', '_')}_{req.candidate_name.replace(' ', '_')}.tex",
            "filename_pdf": f"Resume_{req.target_career.replace(' ', '_')}_{req.candidate_name.replace(' ', '_')}.pdf"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/ats/scan-red-flags")
def scan_ats_red_flags_endpoint(req: ATSRedFlagScanRequest):
    """Audits resume text for ATS parsing red flags, contact omissions, passive voice, and unquantified metrics."""
    try:
        flags = ats_optimizer.scan_ats_red_flags(req.resume_text)
        critical_count = sum(1 for f in flags if f.severity == "Critical")
        warning_count = sum(1 for f in flags if f.severity == "Warning")
        good_count = sum(1 for f in flags if f.severity == "Good")
        return {
            "total_flags": len(flags),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "good_count": good_count,
            "flags": [f.to_dict() for f in flags]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/interview/evaluate")
def evaluate_interview(req: InterviewEvalRequest):
    """Evaluates candidate technical interview answer against key concepts and rubric."""
    try:
        q = InterviewQuestion(
            question_id="Q_API_01",
            skill_name=req.skill_name,
            difficulty="Intermediate",
            question_type="Conceptual",
            question_text=req.question_text,
            key_concepts=["filter", "group", "aggregate", "where", "having"],
            follow_up_hint="Think about query execution order",
            sample_model_answer="WHERE filters rows before aggregation, HAVING filters groups."
        )
        eval_res = interview_engine.evaluate_candidate_answer(q, req.candidate_answer)
        return {
            "skill_name": req.skill_name,
            "overall_score": eval_res.overall_score,
            "score_tier": eval_res.score_tier,
            "concept_coverage_pct": eval_res.concept_coverage_pct,
            "matched_concepts": eval_res.matched_concepts,
            "missing_concepts": eval_res.missing_concepts,
            "feedback_strengths": eval_res.feedback_strengths,
            "feedback_improvements": eval_res.feedback_improvements
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/interview/coding-problems")
def get_coding_problems_endpoint(skill_name: Optional[str] = None):
    """Retrieves coding sandbox problems filtered by skill name or all available."""
    try:
        problems = interview_engine.get_coding_problems(skill_name=skill_name)
        return {
            "total_problems": len(problems),
            "problems": [p.to_dict() for p in problems]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/interview/run-code")
def run_code_sandbox_endpoint(req: RunCodeRequest):
    """Executes candidate Python / SQL code in sandbox against unit test cases."""
    try:
        result = interview_engine.execute_code_sandbox(
            problem_id=req.problem_id,
            code=req.code,
            language=req.language or "python"
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/interview/follow-up")
def interview_follow_up_endpoint(req: FollowUpRequest):
    """Generates an adaptive follow-up probing question based on previous answer coverage."""
    try:
        q = InterviewQuestion(
            question_id=req.question_id or "Q_01",
            skill_name=req.skill_name,
            difficulty="Intermediate",
            question_type="Conceptual",
            question_text=req.question_text,
            key_concepts=["filter", "group", "aggregate", "where", "having", "syntax", "order by"],
            follow_up_hint="Think about query execution order",
            sample_model_answer="WHERE filters rows before aggregation, HAVING filters groups."
        )
        eval_res = interview_engine.evaluate_candidate_answer(q, req.candidate_answer)
        follow_up = interview_engine.generate_adaptive_follow_up(q, eval_res, req.candidate_answer)
        return {
            "evaluation": eval_res.to_dict(),
            "follow_up": follow_up.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/github-scan/{username}")
def scan_github_profile(username: str):
    """Scans public GitHub repositories for code proof and verified technical skill signatures."""
    try:
        report = github_scanner.scan_github_profile(username)
        return {
            "username": report.username,
            "total_repos_audited": report.total_repos_audited,
            "quality_score": report.hands_on_evidence_score,
            "verified_skills": report.verified_skills,
            "unverified_claimed_skills": report.unverified_claimed_skills,
            "hands_on_evidence_score": report.hands_on_evidence_score,
            "profile_quality_tier": report.profile_quality_tier,
            "portfolio_tier": report.profile_quality_tier,
            "recommended_projects": report.recommended_projects_to_build,
            "top_project_blueprints": report.top_project_blueprints,
            "repositories": [
                {
                    "name": r.repo_name,
                    "language": r.primary_language,
                    "quality_score": r.quality_score,
                    "skills": r.detected_skills,
                    "stars": r.stars_count,
                    "has_readme": r.has_readme,
                    "has_tests": r.has_tests,
                    "has_docker": r.has_docker,
                    "has_ci": r.has_ci
                }
                for r in report.audited_repos
            ],
            "audited_repos": [
                {
                    "name": r.repo_name,
                    "language": r.primary_language,
                    "quality_score": r.quality_score,
                    "skills": r.detected_skills
                }
                for r in report.audited_repos
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/github/analyze-code")
def analyze_code_ast_endpoint(req: CodeAnalysisRequest):
    """Runs deep static code analysis (AST) measuring cyclomatic complexity, typing coverage, and OOP modularity."""
    try:
        report = github_scanner.analyze_code_quality(req.code_text, file_name=req.file_name or "main.py")
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/github/audit-readme")
def audit_readme_endpoint(req: ReadmeAuditRequest):
    """Scores repository README against open-source documentation standards (architecture diagrams, setup, live demos)."""
    try:
        report = github_scanner.audit_readme_quality(req.readme_text)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/github/generate-blueprint")
def generate_project_blueprint_endpoint(req: ProjectBlueprintRequest):
    """Generates a complete step-by-step project blueprint with folder structure and starter templates for a skill gap."""
    try:
        blueprint = github_scanner.generate_project_blueprint(
            missing_skill=req.missing_skill,
            target_career=req.target_career or "Data Scientist"
        )
        return blueprint.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/vector/hybrid-search")
def hybrid_search_endpoint(req: HybridSearchRequest):
    """Executes multi-modal search combining dense vectors and BM25 sparse keyword ranking via Reciprocal Rank Fusion."""
    try:
        results = vector_store.hybrid_search(
            query=req.query,
            top_k=req.top_k or 5,
            mode=req.mode or "hybrid",
            alpha=req.alpha if req.alpha is not None else 0.5,
            doc_type=req.doc_type or "all"
        )
        return {
            "query": req.query,
            "mode": req.mode or "hybrid",
            "count": len(results),
            "results": [r.to_dict() for r in results]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/knowledge-graph/explore")
def explore_knowledge_graph_endpoint(target_skill: Optional[str] = None):
    """Retrieves directed Knowledge Graph nodes, prerequisite edges, centrality rankings, and optional prerequisite paths."""
    try:
        graph = vector_store.get_knowledge_graph_model()
        if target_skill:
            prereq_chain = vector_store.get_prerequisite_chain(target_skill)
            graph["queried_skill"] = target_skill
            graph["prerequisite_chain"] = prereq_chain
        return graph
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/rag/ask")
def rag_ask_endpoint(req: RAGAskRequest):
    """Synthesizes technical answers grounded in retrieved vector knowledge chunks with citations and code snippets."""
    try:
        response = vector_store.ask_rag_assistant(req.question)
        return response.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/market/intelligence")
def get_market_intelligence_endpoint():
    """Returns aggregated live job market intelligence report with dynamic weights across careers."""
    try:
        report = market_scraper.generate_market_intelligence_report()
        return {
            "total_postings_analyzed": report.total_postings_analyzed,
            "last_updated": report.last_updated,
            "top_market_skills": report.top_market_skills,
            "emerging_skills": report.emerging_skills,
            "sample_job_postings": [
                {
                    "job_id": p.job_id,
                    "title": p.title,
                    "company": p.company,
                    "location": p.location,
                    "target_career": p.target_career,
                    "salary_range": p.salary_range,
                    "description_snippet": p.description_snippet,
                    "extracted_skills": p.extracted_skills,
                    "source_url": p.source_url,
                    "posted_date": p.posted_date
                }
                for p in report.sample_job_postings
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/market/salary-estimator")
def salary_estimator_endpoint(req: SalaryEstimationRequest):
    """Estimates real-time compensation breakdown and marginal Skill Value Deltas (ROI) for missing skills."""
    try:
        skills = req.student_skills
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]
        report = market_scraper.estimate_compensation(skills, target_career=req.target_career or "Data Scientist")
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/market/hiring-heatmap")
def hiring_heatmap_endpoint():
    """Returns real-world tech hiring distribution and compensation metrics across major tech hubs."""
    try:
        hubs = market_scraper.get_tech_hiring_hubs()
        return {
            "total_hubs": len(hubs),
            "hubs": [h.to_dict() for h in hubs]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/market/skill-velocity")
def skill_velocity_endpoint():
    """Tracks month-over-month (MoM) demand velocity, 6-month historical trajectories, and market momentum."""
    try:
        metrics = market_scraper.get_skill_velocity_tracker()
        return {
            "total_skills_tracked": len(metrics),
            "velocity_metrics": [m.to_dict() for m in metrics]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/market/recalculate-readiness")
def recalculate_readiness_endpoint(req: RecalculateReadinessRequest):
    """Recalculates a student's Weighted Readiness Score using dynamic market weights."""
    try:
        skills = req.student_skills
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]
        static_pct, live_pct, comparisons = market_scraper.recalculate_readiness_with_live_weights(
            skills, req.target_career or "Data Scientist"
        )
        return {
            "static_readiness_pct": static_pct,
            "live_market_readiness_pct": live_pct,
            "readiness_delta_pct": round(live_pct - static_pct, 1),
            "comparisons": comparisons
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/vector-search")
def vector_search_post(req: VectorSearchRequest):
    """Executes dense vector similarity search via POST payload."""
    results = vector_store.search(query=req.query, top_k=req.top_k, filter_type=req.doc_type)
    return {
        "query": req.query,
        "count": len(results),
        "results_count": len(results),
        "results": [
            {
                "doc_id": r.doc_id,
                "text": r.text_content,
                "similarity": r.similarity_score,
                "metadata": r.metadata
            }
            for r in results
        ]
    }

@app.get("/api/v1/vector-search")
def vector_search_get(query: str, top_k: int = 5, doc_type: str = "all"):
    """Executes dense vector similarity search via GET query params."""
    results = vector_store.search(query=query, top_k=top_k, filter_type=doc_type)
    return {
        "query": query,
        "count": len(results),
        "results_count": len(results),
        "results": [
            {
                "doc_id": r.doc_id,
                "text": r.text_content,
                "similarity": r.similarity_score,
                "metadata": r.metadata
            }
            for r in results
        ]
    }


# -----------------------------------------------------------------------------
# SECTION 8: TPO COHORT ANALYTICS, RECRUITER SEARCH & CREDENTIALS
# -----------------------------------------------------------------------------
@app.get("/api/v1/tpo/cohort-summary")
def tpo_cohort_summary_endpoint(department: Optional[str] = "all", batch_year: Optional[int] = None):
    """Calculates institutional aggregate placement metrics across multi-department student cohorts."""
    try:
        summary = tpo_engine.get_cohort_summary(department=department, batch_year=batch_year)
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/tpo/department-gaps")
def tpo_department_gaps_endpoint(department: Optional[str] = "all"):
    """Audits departmental skill penetration and flags critical deficits with faculty interventions."""
    try:
        reports = tpo_engine.get_department_gap_analysis(department=department)
        return {
            "status": "success",
            "total_reports": len(reports),
            "reports": [r.to_dict() for r in reports]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/tpo/accreditation-audit")
def tpo_accreditation_audit_endpoint(batch_year: int = 2026, institution: Optional[str] = None):
    """Generates formal NAAC Criterion 5.2 / NIRF Metric / NBA Attainment placement audit report."""
    try:
        inst_name = institution or "National Institute of Technology & Engineering"
        audit = tpo_engine.generate_accreditation_audit_report(batch_year=batch_year, institution_name=inst_name)
        return {
            "status": "success",
            "audit_report": audit.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/recruiter/search-candidates")
def recruiter_search_candidates_endpoint(req: RecruiterSearchRequest):
    """Ranks student candidates against a corporate Job Description using multi-factor fit scoring."""
    try:
        query_input = req.jd_text or req.skills or []
        if isinstance(query_input, str) and not req.jd_text:
            query_input = [s.strip() for s in query_input.split(",") if s.strip()]
        
        matches = tpo_engine.search_candidates(
            jd_text_or_skills=query_input,
            target_career=req.target_career,
            min_readiness=req.min_readiness or 0.0,
            min_ats=req.min_ats or 0.0,
            min_github_stars=req.min_github_stars or 0,
            department=req.department,
            limit=req.limit or 20
        )
        return {
            "status": "success",
            "total_matches": len(matches),
            "matches": [m.to_dict() for m in matches]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/credentials/issue")
def issue_credential_endpoint(req: IssueCredentialRequest):
    """Issues a tamper-proof digital certificate with deterministic SHA-256 cryptographic signature."""
    try:
        skills = req.skills
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]
        cred = tpo_engine.issue_placement_credential(
            student_id=req.student_id,
            student_name=req.student_name,
            department=req.department,
            target_career=req.target_career,
            skills=skills,
            readiness_score=req.readiness_score,
            ats_score=req.ats_score,
            github_grade=req.github_grade,
            institution=req.institution or "National Institute of Technology & Engineering"
        )
        return {
            "status": "success",
            "credential": cred.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/credentials/verify/{cert_id}")
def verify_credential_endpoint(cert_id: str):
    """Verifies the cryptographic integrity and validity of a placement certificate."""
    try:
        result = tpo_engine.verify_placement_credential(cert_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


from fastapi.staticfiles import StaticFiles

# Mount Frontend static files to serve the Shadcn UI Enterprise Analytics app
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
