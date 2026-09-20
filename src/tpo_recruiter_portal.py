"""
TPO (Training & Placement Officer) & Corporate Recruiter Portal Engine
Section 8 Enterprise Expansion

Provides:
1. Batch-wide Cohort Analytics & Departmental Skill Deficit Analysis for College Placement Cells (TPO).
2. Automated Accreditation & NAAC / NIRF / NBA Audit Report Generator.
3. Multi-Factor Recruiter Talent Search Engine ranking students by Skill Match, Placement ML Likelihood, GitHub Code Proof, and ATS Score.
4. SHA-256 Cryptographic Placement Credential Issuer & Tamper-Proof Integrity Verifier.
"""

from dataclasses import dataclass, field
import datetime
import hashlib
import json
import math
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from data_loader import DataLoader
from skill_extractor import NLPSkillExtractor
from placement_predictor import PlacementPredictorEngine


SECRET_SALT = "AGY_PLACEMENT_CREDENTIAL_SALT_2026"


@dataclass
class StudentCohortProfile:
    """Individual student profile within an institutional batch cohort."""
    student_id: str
    name: str
    email: str
    department: str  # 'Computer Science & Engineering', 'AI & Data Science', 'Information Technology', 'Electronics & Communication'
    batch_year: int
    target_career: str
    skills: List[str]
    readiness_pct: float
    placement_probability_pct: float
    ats_score: float
    github_username: str
    github_complexity_grade: str  # 'Grade A (Modular OOP)', 'Grade B (Good)', 'Grade C (Moderate)'
    github_stars: int
    verified_credential_id: Optional[str] = None
    placed_status: str = "In Pipeline"  # 'Placed (Tier 1)', 'Placed (Tier 2)', 'In Pipeline', 'At Risk'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "batch_year": self.batch_year,
            "target_career": self.target_career,
            "skills": self.skills,
            "readiness_pct": round(self.readiness_pct, 1),
            "placement_probability_pct": round(self.placement_probability_pct, 1),
            "ats_score": round(self.ats_score, 1),
            "github_username": self.github_username,
            "github_complexity_grade": self.github_complexity_grade,
            "github_stars": self.github_stars,
            "verified_credential_id": self.verified_credential_id,
            "placed_status": self.placed_status
        }


@dataclass
class DepartmentSkillGapReport:
    """Departmental skill penetration analysis and remedial curriculum recommendations."""
    department: str
    total_students: int
    avg_readiness_pct: float
    placement_ready_count: int
    at_risk_count: int
    top_mastered_skills: List[Dict[str, Any]]  # skill_name, student_count, penetration_pct
    critical_skill_deficits: List[Dict[str, Any]]  # skill_name, student_count, actual_penetration_pct, benchmark_target_pct, deficit_pct, remedial_action
    tier_distribution: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "department": self.department,
            "total_students": self.total_students,
            "avg_readiness_pct": round(self.avg_readiness_pct, 1),
            "placement_ready_count": self.placement_ready_count,
            "at_risk_count": self.at_risk_count,
            "top_mastered_skills": self.top_mastered_skills,
            "critical_skill_deficits": self.critical_skill_deficits,
            "tier_distribution": self.tier_distribution
        }


@dataclass
class AccreditationAuditReport:
    """Formal accreditation placement and skill outcome attainment audit report."""
    institution_name: str
    batch_year: int
    audit_date: str
    total_students_assessed: int
    placement_eligible_pct: float
    tier_1_dream_offer_pct: float
    naac_criterion_5_score: float  # 0.0 - 4.0 scale
    nirf_metric_score: float  # 0.0 - 100.0 scale
    nba_outcome_attainment_pct: float  # PO3 (Design/Development) & PO5 (Modern Tool Usage)
    department_benchmarks: List[Dict[str, Any]]
    key_faculty_interventions: List[str]
    audit_markdown_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "institution_name": self.institution_name,
            "batch_year": self.batch_year,
            "audit_date": self.audit_date,
            "total_students_assessed": self.total_students_assessed,
            "placement_eligible_pct": round(self.placement_eligible_pct, 1),
            "tier_1_dream_offer_pct": round(self.tier_1_dream_offer_pct, 1),
            "naac_criterion_5_score": round(self.naac_criterion_5_score, 2),
            "nirf_metric_score": round(self.nirf_metric_score, 1),
            "nba_outcome_attainment_pct": round(self.nba_outcome_attainment_pct, 1),
            "department_benchmarks": self.department_benchmarks,
            "key_faculty_interventions": self.key_faculty_interventions,
            "audit_markdown_summary": self.audit_markdown_summary
        }


@dataclass
class RecruiterCandidateMatch:
    """Ranked student candidate matched against a Recruiter Job Description."""
    student_id: str
    name: str
    email: str
    department: str
    batch_year: int
    target_career: str
    recruiter_fit_score: float  # 0.0 - 100.0 scale
    skill_match_pct: float
    matched_jd_skills: List[str]
    missing_jd_skills: List[str]
    placement_probability_pct: float
    ats_score: float
    github_complexity_grade: str
    github_stars: int
    verified_credential_id: Optional[str]
    recruiter_verdict: str  # 'Tier-1 Immediate Hire', 'High Match Candidate', 'Promising Candidate'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "batch_year": self.batch_year,
            "target_career": self.target_career,
            "recruiter_fit_score": round(self.recruiter_fit_score, 1),
            "skill_match_pct": round(self.skill_match_pct, 1),
            "matched_jd_skills": self.matched_jd_skills,
            "missing_jd_skills": self.missing_jd_skills,
            "placement_probability_pct": round(self.placement_probability_pct, 1),
            "ats_score": round(self.ats_score, 1),
            "github_complexity_grade": self.github_complexity_grade,
            "github_stars": self.github_stars,
            "verified_credential_id": self.verified_credential_id,
            "recruiter_verdict": self.recruiter_verdict
        }


@dataclass
class PlacementCredential:
    """Tamper-proof digital placement certificate with SHA-256 cryptographic signature."""
    certificate_id: str
    student_id: str
    student_name: str
    department: str
    institution: str
    target_career: str
    skills_certified: List[str]
    readiness_score: float
    ats_score: float
    github_grade: str
    issue_date: str
    sha256_signature: str
    verification_url: str
    is_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "student_id": self.student_id,
            "student_name": self.student_name,
            "department": self.department,
            "institution": self.institution,
            "target_career": self.target_career,
            "skills_certified": self.skills_certified,
            "readiness_score": round(self.readiness_score, 1),
            "ats_score": round(self.ats_score, 1),
            "github_grade": self.github_grade,
            "issue_date": self.issue_date,
            "sha256_signature": self.sha256_signature,
            "verification_url": self.verification_url,
            "is_valid": self.is_valid
        }


class TPORecruiterPortalEngine:
    """
    Enterprise Engine for University Placement Officers (TPO) and Corporate Recruiters.
    """

    def __init__(self, data_loader: Optional[DataLoader] = None):
        self.loader = data_loader if data_loader else DataLoader()
        self.extractor = NLPSkillExtractor(self.loader)
        self.predictor = PlacementPredictorEngine(self.loader)
        self.credentials_db: Dict[str, PlacementCredential] = {}
        self.cohort: List[StudentCohortProfile] = []
        self._initialize_synthetic_cohort()

    def _initialize_synthetic_cohort(self):
        """Initializes a representative multi-department cohort of 60 students."""
        raw_cohort_data = [
            # Data Science & AI Department
            ("STU-2026-001", "Aarav Sharma", "aarav.sharma@institution.edu", "AI & Data Science", 2026, "Data Scientist", ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "Deep Learning", "PyTorch"], 88.5, 92.4, 89.0, "aarav-ai", "Grade A (Modular OOP)", 14),
            ("STU-2026-002", "Priya Nair", "priya.nair@institution.edu", "AI & Data Science", 2026, "Data Scientist", ["Python", "SQL", "Pandas", "Scikit-Learn", "Matplotlib", "Statistics"], 72.0, 78.5, 84.0, "priya-ds", "Grade A (Modular OOP)", 8),
            ("STU-2026-003", "Rohan Verma", "rohan.verma@institution.edu", "AI & Data Science", 2026, "Machine Learning Engineer", ["Python", "Docker", "FastAPI", "PyTorch", "Git", "Machine Learning", "Deep Learning"], 85.0, 89.2, 86.5, "rohan-mlops", "Grade A (Modular OOP)", 22),
            ("STU-2026-004", "Ananya Deshmukh", "ananya.d@institution.edu", "AI & Data Science", 2026, "Data Scientist", ["Python", "SQL", "Pandas", "Tableau", "Power BI", "Statistics"], 68.0, 74.0, 81.0, "ananya-analytics", "Grade B (Good)", 5),
            ("STU-2026-005", "Kavya Patel", "kavya.p@institution.edu", "AI & Data Science", 2026, "AI Research Assistant", ["Python", "PyTorch", "Transformers", "NLP", "Linear Algebra", "Calculus"], 82.0, 85.6, 88.0, "kavya-nlp", "Grade A (Modular OOP)", 19),
            ("STU-2026-006", "Siddharth Rao", "sid.rao@institution.edu", "AI & Data Science", 2026, "Data Scientist", ["Python", "SQL", "Pandas"], 42.0, 48.0, 62.0, "sid-codes", "Grade C (Moderate)", 1),
            ("STU-2026-007", "Tanvi Kulkarni", "tanvi.k@institution.edu", "AI & Data Science", 2026, "Machine Learning Engineer", ["Python", "SQL", "Docker", "AWS", "Scikit-Learn", "FastAPI"], 79.5, 83.2, 85.0, "tanvi-cloud-ml", "Grade A (Modular OOP)", 11),
            ("STU-2026-008", "Vikram Joshi", "vikram.j@institution.edu", "AI & Data Science", 2026, "Data Scientist", ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "TensorFlow"], 76.0, 80.5, 83.0, "vikram-ds", "Grade B (Good)", 6),
            ("STU-2026-009", "Meera Iyer", "meera.i@institution.edu", "AI & Data Science", 2026, "Business Intelligence Analyst", ["SQL", "Power BI", "Tableau", "Excel", "Data Modeling"], 86.0, 88.0, 87.5, "meera-bi", "Grade B (Good)", 4),
            ("STU-2026-010", "Aditya Sen", "aditya.sen@institution.edu", "AI & Data Science", 2026, "Data Scientist", ["Python", "Statistics"], 34.0, 38.0, 55.0, "aditya-s", "Grade C (Moderate)", 0),
            ("STU-2026-011", "Sneha Roy", "sneha.roy@institution.edu", "AI & Data Science", 2026, "Data Analyst", ["Python", "SQL", "Pandas", "Excel", "Tableau"], 81.0, 84.5, 86.0, "sneha-data", "Grade B (Good)", 7),
            ("STU-2026-012", "Varun Bhat", "varun.bhat@institution.edu", "AI & Data Science", 2026, "Machine Learning Engineer", ["Python", "PyTorch", "CUDA", "C++", "Computer Vision"], 84.0, 87.2, 85.0, "varun-cv", "Grade A (Modular OOP)", 16),
            ("STU-2026-013", "Ishaan Kapoor", "ishaan.k@institution.edu", "AI & Data Science", 2026, "Data Scientist", ["Python", "SQL", "Pandas", "Scikit-Learn", "FastAPI"], 74.5, 79.0, 82.5, "ishaan-k", "Grade B (Good)", 9),
            ("STU-2026-014", "Diya Mukherjee", "diya.m@institution.edu", "AI & Data Science", 2026, "AI Research Assistant", ["Python", "PyTorch", "Hugging Face", "LLMs", "RAG"], 91.0, 94.0, 92.0, "diya-llms", "Grade A (Modular OOP)", 28),
            ("STU-2026-015", "Manish Pillai", "manish.p@institution.edu", "AI & Data Science", 2026, "Data Engineer", ["Python", "SQL", "PySpark", "Kafka", "PostgreSQL"], 80.0, 83.5, 84.0, "manish-de", "Grade A (Modular OOP)", 12),

            # Computer Science & Engineering Department
            ("STU-2026-016", "Rahul Gupta", "rahul.gupta@institution.edu", "Computer Science & Engineering", 2026, "Backend Developer (Python)", ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "Git", "REST APIs"], 92.0, 95.0, 91.5, "rahul-backend", "Grade A (Modular OOP)", 31),
            ("STU-2026-017", "Neha Singhania", "neha.s@institution.edu", "Computer Science & Engineering", 2026, "Backend Developer (Python)", ["Python", "Django", "SQL", "HTML", "CSS", "Git"], 74.0, 78.0, 82.0, "neha-web", "Grade B (Good)", 8),
            ("STU-2026-018", "Arjun Reddy", "arjun.reddy@institution.edu", "Computer Science & Engineering", 2026, "Data Engineer", ["Python", "SQL", "Apache Spark", "Airflow", "Docker", "PostgreSQL"], 87.5, 90.2, 88.0, "arjun-pipelines", "Grade A (Modular OOP)", 18),
            ("STU-2026-019", "Divya Menon", "divya.m@institution.edu", "Computer Science & Engineering", 2026, "Backend Developer (Python)", ["Python", "Flask", "SQL", "Git"], 62.0, 68.0, 75.0, "divya-dev", "Grade B (Good)", 3),
            ("STU-2026-020", "Kunal Ghosh", "kunal.g@institution.edu", "Computer Science & Engineering", 2026, "Backend Developer (Python)", ["Python", "FastAPI", "SQL", "Docker", "AWS", "CI/CD"], 86.0, 89.5, 87.0, "kunal-cloud", "Grade A (Modular OOP)", 15),
            ("STU-2026-021", "Shruti Hegde", "shruti.h@institution.edu", "Computer Science & Engineering", 2026, "Data Scientist", ["Python", "SQL", "Pandas", "Scikit-Learn"], 65.0, 71.0, 79.0, "shruti-h", "Grade B (Good)", 4),
            ("STU-2026-022", "Gaurav Malhotra", "gaurav.m@institution.edu", "Computer Science & Engineering", 2026, "Backend Developer (Python)", ["Python", "FastAPI", "PostgreSQL", "Docker", "Microservices"], 88.0, 91.0, 89.0, "gaurav-arch", "Grade A (Modular OOP)", 21),
            ("STU-2026-023", "Pooja Trivedi", "pooja.t@institution.edu", "Computer Science & Engineering", 2026, "Data Analyst", ["SQL", "Excel", "Python", "Tableau"], 77.0, 81.0, 83.5, "pooja-insights", "Grade B (Good)", 5),
            ("STU-2026-024", "Nikhil Saxena", "nikhil.s@institution.edu", "Computer Science & Engineering", 2026, "Backend Developer (Python)", ["Python", "SQL"], 40.0, 46.0, 60.0, "nikhil-s", "Grade C (Moderate)", 1),
            ("STU-2026-025", "Swati Bose", "swati.b@institution.edu", "Computer Science & Engineering", 2026, "Machine Learning Engineer", ["Python", "TensorFlow", "Scikit-Learn", "Docker", "FastAPI"], 81.5, 85.0, 86.0, "swati-ai", "Grade A (Modular OOP)", 13),
            ("STU-2026-026", "Abhishek Das", "abhishek.d@institution.edu", "Computer Science & Engineering", 2026, "Backend Developer (Python)", ["Python", "Django", "PostgreSQL", "Redis", "Celery"], 83.0, 86.5, 85.0, "abhi-django", "Grade A (Modular OOP)", 14),
            ("STU-2026-027", "Rhea George", "rhea.g@institution.edu", "Computer Science & Engineering", 2026, "Data Engineer", ["Python", "SQL", "Kafka", "Docker", "PostgreSQL"], 82.0, 85.5, 84.5, "rhea-dataflow", "Grade A (Modular OOP)", 10),
            ("STU-2026-028", "Tarun Jain", "tarun.j@institution.edu", "Computer Science & Engineering", 2026, "Backend Developer (Python)", ["Python", "FastAPI", "SQL", "Git"], 70.0, 75.0, 80.0, "tarun-j", "Grade B (Good)", 6),
            ("STU-2026-029", "Harini Venkat", "harini.v@institution.edu", "Computer Science & Engineering", 2026, "Data Scientist", ["Python", "SQL", "Pandas", "Scikit-Learn", "PyTorch"], 78.0, 82.0, 84.0, "harini-ml", "Grade B (Good)", 8),
            ("STU-2026-030", "Deepak Pandey", "deepak.p@institution.edu", "Computer Science & Engineering", 2026, "Backend Developer (Python)", ["Python", "C++"], 38.0, 44.0, 58.0, "deepak-cpp", "Grade C (Moderate)", 0),

            # Information Technology Department
            ("STU-2026-031", "Sanjay Choudhury", "sanjay.c@institution.edu", "Information Technology", 2026, "Data Engineer", ["SQL", "Python", "ETL Pipelines", "Airflow", "PostgreSQL", "Docker"], 84.0, 87.0, 86.0, "sanjay-etl", "Grade A (Modular OOP)", 16),
            ("STU-2026-032", "Bhavna Mishra", "bhavna.m@institution.edu", "Information Technology", 2026, "Business Intelligence Analyst", ["SQL", "Power BI", "Tableau", "Excel", "Data Warehousing"], 88.0, 90.5, 89.0, "bhavna-bi", "Grade B (Good)", 7),
            ("STU-2026-033", "Mohit Bansal", "mohit.b@institution.edu", "Information Technology", 2026, "Backend Developer (Python)", ["Python", "Flask", "PostgreSQL", "Git", "REST APIs"], 75.0, 79.5, 81.0, "mohit-dev", "Grade B (Good)", 9),
            ("STU-2026-034", "Kritika Soni", "kritika.s@institution.edu", "Information Technology", 2026, "Data Analyst", ["SQL", "Python", "Pandas", "Tableau", "Excel"], 82.5, 85.5, 87.0, "kritika-analytics", "Grade B (Good)", 8),
            ("STU-2026-035", "Akash Agarwal", "akash.a@institution.edu", "Information Technology", 2026, "Data Scientist", ["Python", "SQL", "Pandas", "Scikit-Learn"], 68.0, 73.0, 80.0, "akash-ds", "Grade B (Good)", 4),
            ("STU-2026-036", "Shweta Tiwari", "shweta.t@institution.edu", "Information Technology", 2026, "Business Intelligence Analyst", ["SQL", "Power BI", "Excel", "DAX"], 79.0, 82.5, 84.0, "shweta-powerbi", "Grade B (Good)", 3),
            ("STU-2026-037", "Prateek Mathur", "prateek.m@institution.edu", "Information Technology", 2026, "Backend Developer (Python)", ["Python", "Django", "SQL", "Docker"], 76.0, 80.0, 82.0, "prateek-m", "Grade B (Good)", 6),
            ("STU-2026-038", "Nandini Rathi", "nandini.r@institution.edu", "Information Technology", 2026, "Data Engineer", ["Python", "SQL", "PySpark", "AWS S3", "Airflow"], 85.5, 88.5, 87.5, "nandini-cloud", "Grade A (Modular OOP)", 17),
            ("STU-2026-039", "Umesh Yadav", "umesh.y@institution.edu", "Information Technology", 2026, "Data Analyst", ["Excel", "SQL"], 48.0, 54.0, 66.0, "umesh-sql", "Grade C (Moderate)", 1),
            ("STU-2026-040", "Aishwarya Seth", "aishwarya.s@institution.edu", "Information Technology", 2026, "Data Scientist", ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning"], 80.0, 84.0, 85.0, "aishwarya-ml", "Grade A (Modular OOP)", 11),
            ("STU-2026-041", "Rajesh Varma", "rajesh.v@institution.edu", "Information Technology", 2026, "Backend Developer (Python)", ["Python", "FastAPI", "MongoDB", "Docker"], 78.0, 82.0, 83.0, "rajesh-api", "Grade B (Good)", 10),
            ("STU-2026-042", "Pallavi Hegde", "pallavi.h@institution.edu", "Information Technology", 2026, "Data Analyst", ["SQL", "Tableau", "Power BI", "Excel"], 83.0, 86.0, 88.0, "pallavi-viz", "Grade B (Good)", 5),
            ("STU-2026-043", "Sameer Qureshi", "sameer.q@institution.edu", "Information Technology", 2026, "Data Engineer", ["SQL", "Python", "Kafka"], 58.0, 64.0, 72.0, "sameer-q", "Grade B (Good)", 2),
            ("STU-2026-044", "Simran Kaur", "simran.k@institution.edu", "Information Technology", 2026, "Machine Learning Engineer", ["Python", "PyTorch", "FastAPI", "Docker", "Machine Learning"], 86.0, 89.0, 88.0, "simran-ml", "Grade A (Modular OOP)", 15),
            ("STU-2026-045", "Karthik Raja", "karthik.r@institution.edu", "Information Technology", 2026, "Data Scientist", ["Python", "SQL"], 45.0, 50.0, 64.0, "karthik-r", "Grade C (Moderate)", 0),

            # Electronics & Communication Department
            ("STU-2026-046", "Manoj Kumar", "manoj.k@institution.edu", "Electronics & Communication", 2026, "Machine Learning Engineer", ["Python", "C++", "PyTorch", "Embedded Systems", "Edge AI"], 83.0, 86.0, 84.0, "manoj-edge-ai", "Grade A (Modular OOP)", 14),
            ("STU-2026-047", "Geeta Sundaram", "geeta.s@institution.edu", "Electronics & Communication", 2026, "Data Analyst", ["Python", "SQL", "Excel", "Power BI"], 73.0, 77.0, 81.0, "geeta-analyst", "Grade B (Good)", 4),
            ("STU-2026-048", "Ashwin Prasad", "ashwin.p@institution.edu", "Electronics & Communication", 2026, "AI Research Assistant", ["Python", "PyTorch", "Signal Processing", "NumPy", "SciPy"], 80.0, 83.0, 85.0, "ashwin-dsp", "Grade A (Modular OOP)", 12),
            ("STU-2026-049", "Lavanya Krishnan", "lavanya.k@institution.edu", "Electronics & Communication", 2026, "Data Scientist", ["Python", "SQL", "Pandas", "Scikit-Learn"], 66.0, 71.0, 78.0, "lavanya-ds", "Grade B (Good)", 3),
            ("STU-2026-050", "Pranav Swaminathan", "pranav.s@institution.edu", "Electronics & Communication", 2026, "Backend Developer (Python)", ["Python", "FastAPI", "SQL", "Git"], 71.0, 76.0, 80.0, "pranav-dev", "Grade B (Good)", 6),
            ("STU-2026-051", "Shalini Rangan", "shalini.r@institution.edu", "Electronics & Communication", 2026, "Business Intelligence Analyst", ["SQL", "Excel", "Tableau"], 70.0, 74.0, 79.0, "shalini-bi", "Grade B (Good)", 2),
            ("STU-2026-052", "Girish Nambiar", "girish.n@institution.edu", "Electronics & Communication", 2026, "Data Engineer", ["Python", "SQL", "Linux", "Docker"], 74.0, 78.0, 81.0, "girish-infra", "Grade B (Good)", 7),
            ("STU-2026-053", "Ritu Bhattacharya", "ritu.b@institution.edu", "Electronics & Communication", 2026, "AI Research Assistant", ["Python", "MATLAB", "Statistics"], 52.0, 58.0, 68.0, "ritu-res", "Grade C (Moderate)", 1),
            ("STU-2026-054", "Vijay Raghavan", "vijay.r@institution.edu", "Electronics & Communication", 2026, "Machine Learning Engineer", ["Python", "TensorFlow", "Computer Vision", "OpenCV"], 79.0, 83.0, 83.5, "vijay-cv", "Grade B (Good)", 11),
            ("STU-2026-055", "Soumya Hegde", "soumya.h@institution.edu", "Electronics & Communication", 2026, "Data Analyst", ["SQL", "Excel", "Python"], 60.0, 66.0, 74.0, "soumya-analytics", "Grade C (Moderate)", 2),
            ("STU-2026-056", "Chirag Shah", "chirag.s@institution.edu", "Electronics & Communication", 2026, "Backend Developer (Python)", ["Python", "Flask", "SQL"], 63.0, 68.0, 75.0, "chirag-web", "Grade B (Good)", 4),
            ("STU-2026-057", "Madhuri Dixit", "madhuri.d@institution.edu", "Electronics & Communication", 2026, "Data Scientist", ["Python", "SQL", "Pandas", "Statistics", "Machine Learning"], 77.0, 81.5, 84.0, "madhuri-ds", "Grade B (Good)", 8),
            ("STU-2026-058", "Naveen Chandran", "naveen.c@institution.edu", "Electronics & Communication", 2026, "Data Engineer", ["SQL", "Python", "PostgreSQL"], 65.0, 70.0, 77.0, "naveen-db", "Grade B (Good)", 3),
            ("STU-2026-059", "Harshita Singhal", "harshita.s@institution.edu", "Electronics & Communication", 2026, "AI Research Assistant", ["Python", "PyTorch", "NLP"], 76.0, 80.0, 83.0, "harshita-nlp", "Grade B (Good)", 7),
            ("STU-2026-060", "Lokesh Jain", "lokesh.j@institution.edu", "Electronics & Communication", 2026, "Backend Developer (Python)", ["Python"], 32.0, 36.0, 52.0, "lokesh-j", "Grade C (Moderate)", 0)
        ]

        self.cohort = []
        for row in raw_cohort_data:
            stu_id, name, email, dept, batch, career, skills, readiness, plac_prob, ats, gh_user, gh_grade, stars = row
            
            # Determine placement status based on probability
            if plac_prob >= 88.0:
                status = "Placed (Tier 1)"
            elif plac_prob >= 75.0:
                status = "Placed (Tier 2)"
            elif plac_prob >= 55.0:
                status = "In Pipeline"
            else:
                status = "At Risk"

            # Auto-issue verified credential for top readiness students
            cert_id = None
            if readiness >= 75.0:
                cert = self.issue_placement_credential(
                    student_id=stu_id,
                    student_name=name,
                    department=dept,
                    target_career=career,
                    skills=skills,
                    readiness_score=readiness,
                    ats_score=ats,
                    github_grade=gh_grade
                )
                cert_id = cert.certificate_id

            profile = StudentCohortProfile(
                student_id=stu_id,
                name=name,
                email=email,
                department=dept,
                batch_year=batch,
                target_career=career,
                skills=skills,
                readiness_pct=readiness,
                placement_probability_pct=plac_prob,
                ats_score=ats,
                github_username=gh_user,
                github_complexity_grade=gh_grade,
                github_stars=stars,
                verified_credential_id=cert_id,
                placed_status=status
            )
            self.cohort.append(profile)

    # =========================================================================
    # 1. TPO COHORT ANALYTICS & GAP REPORTING
    # =========================================================================

    def get_cohort_summary(
        self,
        department: Optional[str] = None,
        batch_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Calculates institutional aggregate placement metrics across students."""
        filtered = self.cohort
        if department and department.lower() != "all":
            filtered = [s for s in filtered if s.department.lower() == department.lower()]
        if batch_year:
            filtered = [s for s in filtered if s.batch_year == batch_year]

        total = len(filtered)
        if total == 0:
            return {
                "total_students": 0,
                "avg_readiness_pct": 0.0,
                "avg_placement_probability_pct": 0.0,
                "placement_ready_count": 0,
                "placement_ready_pct": 0.0,
                "at_risk_count": 0,
                "verified_credentials_count": 0,
                "status_breakdown": {},
                "department_breakdown": {}
            }

        avg_readiness = sum(s.readiness_pct for s in filtered) / total
        avg_prob = sum(s.placement_probability_pct for s in filtered) / total
        ready_count = sum(1 for s in filtered if s.placement_probability_pct >= 75.0)
        at_risk_count = sum(1 for s in filtered if s.placement_probability_pct < 55.0)
        verified_count = sum(1 for s in filtered if s.verified_credential_id is not None)

        status_breakdown = {}
        for s in filtered:
            status_breakdown[s.placed_status] = status_breakdown.get(s.placed_status, 0) + 1

        department_breakdown = {}
        for s in self.cohort:
            if s.department not in department_breakdown:
                department_breakdown[s.department] = {
                    "student_count": 0,
                    "avg_readiness_pct": 0.0,
                    "placed_count": 0
                }
            d = department_breakdown[s.department]
            d["student_count"] += 1
            d["avg_readiness_pct"] += s.readiness_pct
            if "Placed" in s.placed_status:
                d["placed_count"] += 1

        for dept, d in department_breakdown.items():
            if d["student_count"] > 0:
                d["avg_readiness_pct"] = round(d["avg_readiness_pct"] / d["student_count"], 1)

        return {
            "total_students": total,
            "avg_readiness_pct": round(avg_readiness, 1),
            "avg_placement_probability_pct": round(avg_prob, 1),
            "placement_ready_count": ready_count,
            "placement_ready_pct": round((ready_count / total) * 100, 1),
            "at_risk_count": at_risk_count,
            "verified_credentials_count": verified_count,
            "status_breakdown": status_breakdown,
            "department_breakdown": department_breakdown
        }

    def get_department_gap_analysis(
        self,
        department: Optional[str] = None
    ) -> List[DepartmentSkillGapReport]:
        """Audits skill penetration and flags critical deficits with faculty interventions."""
        departments = [
            "AI & Data Science",
            "Computer Science & Engineering",
            "Information Technology",
            "Electronics & Communication"
        ]
        if department and department.lower() != "all":
            departments = [d for d in departments if d.lower() == department.lower()]

        benchmark_industry_skills = [
            ("Python", 80.0, "Fundamental core scripting & algorithms"),
            ("SQL", 75.0, "Relational data extraction & querying"),
            ("Docker", 60.0, "Containerization & deployment pipelines"),
            ("FastAPI", 50.0, "Modern microservice REST API development"),
            ("PyTorch", 45.0, "Deep neural network architectures & AI"),
            ("Pandas", 65.0, "Vectorized data wrangling & feature engineering"),
            ("Scikit-Learn", 55.0, "Classical machine learning modeling"),
            ("Git", 70.0, "Version control, code reviews & branch workflows"),
            ("PostgreSQL", 50.0, "Production relational schema modeling"),
            ("AWS", 40.0, "Cloud infrastructure & serverless compute")
        ]

        reports: List[DepartmentSkillGapReport] = []

        for dept in departments:
            dept_students = [s for s in self.cohort if s.department == dept]
            total = len(dept_students)
            if total == 0:
                continue

            avg_readiness = sum(s.readiness_pct for s in dept_students) / total
            ready_count = sum(1 for s in dept_students if s.placement_probability_pct >= 75.0)
            at_risk_count = sum(1 for s in dept_students if s.placement_probability_pct < 55.0)

            # Calculate skill frequencies
            skill_counts: Dict[str, int] = {}
            for s in dept_students:
                for skill in s.skills:
                    canonical = skill.strip()
                    skill_counts[canonical] = skill_counts.get(canonical, 0) + 1

            mastered_list = []
            for skill, count in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True):
                pct = (count / total) * 100
                if pct >= 50.0:
                    mastered_list.append({
                        "skill_name": skill,
                        "student_count": count,
                        "penetration_pct": round(pct, 1)
                    })

            deficits_list = []
            for target_skill, target_pct, desc in benchmark_industry_skills:
                actual_count = 0
                for s in dept_students:
                    if any(target_skill.lower() == sk.lower() for sk in s.skills):
                        actual_count += 1
                actual_pct = (actual_count / total) * 100
                if actual_pct < target_pct:
                    deficit = target_pct - actual_pct
                    remedial_action = f"Conduct a 3-week hands-on lab workshop on {target_skill} ({desc}) to bridge the {deficit:.0f}% deficit."
                    deficits_list.append({
                        "skill_name": target_skill,
                        "student_count": actual_count,
                        "actual_penetration_pct": round(actual_pct, 1),
                        "benchmark_target_pct": round(target_pct, 1),
                        "deficit_pct": round(deficit, 1),
                        "remedial_action": remedial_action
                    })

            # Sort deficits by magnitude
            deficits_list.sort(key=lambda x: x["deficit_pct"], reverse=True)

            tier_dist = {
                "Tier 1 (Dream >12 LPA)": sum(1 for s in dept_students if s.placement_probability_pct >= 88.0),
                "Tier 2 (Core 6-12 LPA)": sum(1 for s in dept_students if 75.0 <= s.placement_probability_pct < 88.0),
                "Tier 3 (Service 3.5-6 LPA)": sum(1 for s in dept_students if 55.0 <= s.placement_probability_pct < 75.0),
                "At Risk / Unready": sum(1 for s in dept_students if s.placement_probability_pct < 55.0)
            }

            reports.append(DepartmentSkillGapReport(
                department=dept,
                total_students=total,
                avg_readiness_pct=avg_readiness,
                placement_ready_count=ready_count,
                at_risk_count=at_risk_count,
                top_mastered_skills=mastered_list[:5],
                critical_skill_deficits=deficits_list[:4],
                tier_distribution=tier_dist
            ))

        return reports

    # =========================================================================
    # 2. ACCREDITATION & NAAC / NIRF AUDIT REPORT GENERATOR
    # =========================================================================

    def generate_accreditation_audit_report(
        self,
        batch_year: int = 2026,
        institution_name: str = "National Institute of Technology & Engineering"
    ) -> AccreditationAuditReport:
        """Generates a comprehensive NAAC Criterion 5.2 / NIRF Metric / NBA Attainment placement audit."""
        filtered = [s for s in self.cohort if s.batch_year == batch_year]
        total = len(filtered) or 1

        placed_count = sum(1 for s in filtered if "Placed" in s.placed_status)
        tier_1_count = sum(1 for s in filtered if s.placed_status == "Placed (Tier 1)")
        
        placement_pct = (placed_count / total) * 100
        tier_1_pct = (tier_1_count / total) * 100

        # NAAC Criterion 5.2 (Student Progression to Placement): 0.0 - 4.0 GPA scale
        naac_score = min(4.0, (placement_pct / 100.0) * 4.0)

        # NIRF Placement Metric (Metric GPH - Graduation Outcomes): 0 - 100 scale
        nirf_score = min(100.0, (placement_pct * 0.70) + (tier_1_pct * 0.30))

        # NBA Program Outcome Attainment (PO3: Design/Development, PO5: Modern Tool Usage):
        # Attainment based on verified AST complexity grades and credential counts
        high_proof_count = sum(1 for s in filtered if s.github_complexity_grade.startswith("Grade A") or s.verified_credential_id)
        nba_attainment_pct = (high_proof_count / total) * 100

        # Department benchmarks
        dept_benchmarks = []
        for dept in ["AI & Data Science", "Computer Science & Engineering", "Information Technology", "Electronics & Communication"]:
            d_students = [s for s in filtered if s.department == dept]
            d_total = len(d_students) or 1
            d_placed = sum(1 for s in d_students if "Placed" in s.placed_status)
            d_avg_readiness = sum(s.readiness_pct for s in d_students) / d_total
            dept_benchmarks.append({
                "department": dept,
                "cohort_size": d_total,
                "placement_rate_pct": round((d_placed / d_total) * 100, 1),
                "avg_readiness_pct": round(d_avg_readiness, 1),
                "accreditation_grade": "A+" if d_avg_readiness >= 75.0 else ("A" if d_avg_readiness >= 65.0 else "B")
            })

        interventions = [
            "Mandate 40 hours of Docker & Containerization practical labs for CSE & IT Batches.",
            "Establish an AI & MLOps Special Interest Group (SIG) to accelerate PyTorch & FastAPI adoption in ECE.",
            "Integrate automated ATS Resume & Google XYZ quantification workshops into pre-final semester curriculum.",
            "Incentivize open-source GitHub contribution sprints to raise batch AST code complexity grades."
        ]

        today_str = datetime.date.today().strftime("%B %d, %Y")
        
        md_summary = f"""# 🏛️ Formal Accreditation & Placement Audit Report (Batch {batch_year})
**Institution:** {institution_name}  
**Audit Generated:** {today_str}  
**Total Candidates Assessed:** {total} Students across 4 Departments  

---

## 📊 Summary Performance Indicators
- **Placement Progression Rate:** **{placement_pct:.1f}%** ({placed_count}/{total} Students)
- **Dream Offer (Tier 1 >12 LPA) Share:** **{tier_1_pct:.1f}%** ({tier_1_count} Students)
- **NAAC Criterion 5.2 Attainment Score:** **{naac_score:.2f} / 4.00** (Grade A++ Benchmark)
- **NIRF Graduation Outcome Metric (GPH):** **{nirf_score:.1f} / 100.0**
- **NBA Outcome Attainment (PO3/PO5 Tools):** **{nba_attainment_pct:.1f}%**

---

## 🏢 Departmental Attainment Breakdown
| Department | Cohort Size | Placement Rate (%) | Avg Skill Readiness | NAAC Rating |
| :--- | :--- | :--- | :--- | :--- |
"""
        for b in dept_benchmarks:
            md_summary += f"| **{b['department']}** | {b['cohort_size']} | {b['placement_rate_pct']}% | {b['avg_readiness_pct']}% | **{b['accreditation_grade']}** |\n"

        md_summary += f"""
---

## 🎯 Targeted Faculty & Institutional Interventions
"""
        for i, item in enumerate(interventions, 1):
            md_summary += f"{i}. {item}\n"

        return AccreditationAuditReport(
            institution_name=institution_name,
            batch_year=batch_year,
            audit_date=today_str,
            total_students_assessed=total,
            placement_eligible_pct=placement_pct,
            tier_1_dream_offer_pct=tier_1_pct,
            naac_criterion_5_score=naac_score,
            nirf_metric_score=nirf_score,
            nba_outcome_attainment_pct=nba_attainment_pct,
            department_benchmarks=dept_benchmarks,
            key_faculty_interventions=interventions,
            audit_markdown_summary=md_summary
        )

    # =========================================================================
    # 3. RECRUITER TALENT SEARCH ENGINE
    # =========================================================================

    def search_candidates(
        self,
        jd_text_or_skills: Union[str, List[str]],
        target_career: Optional[str] = None,
        min_readiness: float = 0.0,
        min_ats: float = 0.0,
        min_github_stars: int = 0,
        department: Optional[str] = None,
        limit: int = 20
    ) -> List[RecruiterCandidateMatch]:
        """
        Ranks student candidates against a corporate Job Description using multi-factor fit scoring.
        Formula: 0.40 * Skill Match + 0.25 * Placement Likelihood + 0.20 * GitHub Proof + 0.15 * ATS Score.
        """
        # Parse query skills
        if isinstance(jd_text_or_skills, str):
            # Extract skills via NLP skill extractor
            extracted = self.extractor.extract_canonical_names(jd_text_or_skills)
            if not extracted:
                # Fallback splitting
                extracted = [s.strip() for s in re.split(r"[,;\n\s]+", jd_text_or_skills) if len(s.strip()) > 2]
            target_skills = list(set(extracted))
        else:
            target_skills = list(set(jd_text_or_skills))

        if not target_skills and target_career:
            # Fallback to target career curriculum skills
            career_skills = self.loader.get_skills_for_career(target_career)
            target_skills = [s["skill_name"] for s in career_skills]

        if not target_skills:
            target_skills = ["Python", "SQL", "Git"]

        matches: List[RecruiterCandidateMatch] = []

        for stu in self.cohort:
            # Apply hard filters
            if department and department.lower() != "all" and stu.department.lower() != department.lower():
                continue
            if stu.readiness_pct < min_readiness:
                continue
            if stu.ats_score < min_ats:
                continue
            if stu.github_stars < min_github_stars:
                continue

            stu_skills_lower = [s.lower() for s in stu.skills]

            matched = [s for s in target_skills if s.lower() in stu_skills_lower]
            missing = [s for s in target_skills if s.lower() not in stu_skills_lower]

            skill_match_ratio = len(matched) / len(target_skills) if target_skills else 0.0
            skill_match_pct = skill_match_ratio * 100.0

            # GitHub code proof score (0 - 100)
            gh_score = 50.0
            if "Grade A" in stu.github_complexity_grade:
                gh_score = 95.0
            elif "Grade B" in stu.github_complexity_grade:
                gh_score = 75.0
            gh_score = min(100.0, gh_score + min(stu.github_stars * 1.5, 10.0))

            # Multi-factor fit score
            # 0.40 * Skill Match + 0.25 * Placement Probability + 0.20 * GitHub + 0.15 * ATS
            fit_score = (
                (skill_match_pct * 0.40) +
                (stu.placement_probability_pct * 0.25) +
                (gh_score * 0.20) +
                (stu.ats_score * 0.15)
            )

            # Recruiter verdict
            if fit_score >= 85.0:
                verdict = "Tier-1 Immediate Hire"
            elif fit_score >= 72.0:
                verdict = "High Match Candidate"
            else:
                verdict = "Promising Candidate"

            matches.append(RecruiterCandidateMatch(
                student_id=stu.student_id,
                name=stu.name,
                email=stu.email,
                department=stu.department,
                batch_year=stu.batch_year,
                target_career=stu.target_career,
                recruiter_fit_score=fit_score,
                skill_match_pct=skill_match_pct,
                matched_jd_skills=matched,
                missing_jd_skills=missing,
                placement_probability_pct=stu.placement_probability_pct,
                ats_score=stu.ats_score,
                github_complexity_grade=stu.github_complexity_grade,
                github_stars=stu.github_stars,
                verified_credential_id=stu.verified_credential_id,
                recruiter_verdict=verdict
            ))

        # Sort by recruiter fit score descending
        matches.sort(key=lambda x: x.recruiter_fit_score, reverse=True)
        return matches[:limit]

    # =========================================================================
    # 4. SHA-256 CRYPTOGRAPHIC PLACEMENT CREDENTIALING
    # =========================================================================

    def issue_placement_credential(
        self,
        student_id: str,
        student_name: str,
        department: str,
        target_career: str,
        skills: List[str],
        readiness_score: float,
        ats_score: float,
        github_grade: str,
        institution: str = "National Institute of Technology & Engineering"
    ) -> PlacementCredential:
        """
        Issues a tamper-proof digital certificate with deterministic SHA-256 cryptographic signature.
        """
        issue_date = datetime.date.today().isoformat()
        skills_sorted = sorted([s.strip() for s in skills if s.strip()])
        
        # Build canonical payload for hashing
        payload = f"{student_id}:{student_name}:{department}:{target_career}:{readiness_score:.1f}:{ats_score:.1f}:{github_grade}:{','.join(skills_sorted)}:{issue_date}:{SECRET_SALT}"
        sha256_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        cert_id = f"CERT-2026-{sha256_hash[:8].upper()}"
        verification_url = f"https://verify.placement-ai.edu/cert/{cert_id}?hash={sha256_hash[:16]}"

        cred = PlacementCredential(
            certificate_id=cert_id,
            student_id=student_id,
            student_name=student_name,
            department=department,
            institution=institution,
            target_career=target_career,
            skills_certified=skills_sorted,
            readiness_score=readiness_score,
            ats_score=ats_score,
            github_grade=github_grade,
            issue_date=issue_date,
            sha256_signature=sha256_hash,
            verification_url=verification_url,
            is_valid=True
        )

        self.credentials_db[cert_id] = cred
        return cred

    def verify_placement_credential(
        self,
        cert_id_or_hash: str
    ) -> Dict[str, Any]:
        """
        Verifies the cryptographic integrity of a placement certificate in real-time.
        """
        key = cert_id_or_hash.strip().upper()
        
        # Match by Certificate ID or substring of hash
        cred: Optional[PlacementCredential] = None
        if key in self.credentials_db:
            cred = self.credentials_db[key]
        else:
            for c in self.credentials_db.values():
                if c.certificate_id.upper() == key or c.sha256_signature.startswith(cert_id_or_hash.lower()):
                    cred = c
                    break

        if not cred:
            return {
                "is_valid": False,
                "status": "INVALID_CERTIFICATE",
                "message": f"No active placement certificate found matching '{cert_id_or_hash}'. Possible forgery or expired token."
            }

        # Recompute SHA-256 hash to verify zero tampering
        skills_sorted = sorted(cred.skills_certified)
        payload = f"{cred.student_id}:{cred.student_name}:{cred.department}:{cred.target_career}:{cred.readiness_score:.1f}:{cred.ats_score:.1f}:{cred.github_grade}:{','.join(skills_sorted)}:{cred.issue_date}:{SECRET_SALT}"
        expected_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        if expected_hash != cred.sha256_signature:
            return {
                "is_valid": False,
                "status": "TAMPERED_PAYLOAD",
                "message": "Certificate signature mismatch: Payload parameters have been modified after issuance."
            }

        return {
            "is_valid": True,
            "status": "VERIFIED_AUTHENTIC",
            "message": "Cryptographic signature verified against Institutional Placement Registry.",
            "certificate": cred.to_dict()
        }
