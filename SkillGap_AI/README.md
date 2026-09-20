# SkillGap AI: Placement Readiness & Career Recommendation System

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Web Framework](https://img.shields.io/badge/UI-FastAPI%20%2B%20Vanilla%20JS-009688.svg)](https://fastapi.tiangolo.com/)
[![NLP Engine](https://img.shields.io/badge/NLP-SentenceTransformers-yellow.svg)](https://www.sbert.net/)
[![Tests](https://img.shields.io/badge/Tests-114%2F114%20Passed-brightgreen.svg)]()

An AI/NLP-powered decision-support and personalized learning recommendation system designed to bridge the transition from academic coursework to industry placement readiness. The system evaluates student technical competencies against industry career benchmarks, quantifies skill gaps, enforces topological prerequisite constraints, and generates structured, milestone-driven learning roadmaps with curated portfolio projects.

---

## 🎯 1. Problem Statement

Graduating engineering and computer science students often face a significant gap between university curricula and technical job market expectations. Key challenges include:
1. **Ambiguous Competency Benchmarks**: Students lack clarity on which specific technical skills are required for roles like Data Scientist, Machine Learning Engineer, or Data Analyst.
2. **Unstructured Skill Assessment**: Students cannot easily assess how their current coursework or resume aligns with real-world role requirements.
3. **Prerequisite Confusion**: Missing skills are often studied out of order (e.g., attempting advanced Deep Learning without mastering Linear Algebra, Statistics, or Data Preprocessing).
4. **Lack of Practical Project Direction**: Students struggle to identify capstone portfolio projects that demonstrate mastery of their specific missing competencies to recruiters.

---

## 🚀 2. Objectives

- **Standardize Skill Taxonomy**: Establish a canonical relational schema mapping careers, skills, prerequisites, resources, and portfolio projects.
- **Multimodal Profile Ingestion**: Ingest student skills via free-text natural language descriptions, PDF resume uploads, or structured selections.
- **Explainable Matching & Gap Analysis**: Compute weighted readiness scores $(\sum w_m / \sum w_r \times 100)$ that prioritize critical core skills over secondary or optional tools.
- **Prerequisite-Aware Roadmap Generation**: Apply directed acyclic graph (DAG) topological sorting (Kahn's algorithm with priority queueing) to sequence learning paths without dependency violations.
- **Portfolio-Driven Recommendations**: Pair missing skills with curated tutorials, courses, documentation, and relevant hands-on projects.
- **Interactive Visual Dashboard**: Deliver a modern, high-performance web dashboard featuring real-time readiness scoring, visual learning roadmaps, interactive code sandboxes, and recruiter matching.

---

## ✨ 3. Core Features

- **Automated Resume Parsing**: PyMuPDF-based text extraction with section segmentation (Skills, Experience, Projects, Education) and entity recognition.
- **NLP Skill Extractor**: Token-level regex matching with phrase-boundary checks, multi-word greedy entity extraction, and window-based negation detection (e.g., *"I know Python and SQL, but I do not know Docker"*).
- **Two-Tier Matching Engine**:
  - *Tier 1 (Deterministic)*: 80+ alias & abbreviation dictionary with RapidFuzz typo tolerance.
  - *Tier 2 (Semantic)*: Dense 384-dimensional vector embeddings via `sentence-transformers/all-MiniLM-L6-v2` with cosine similarity matching.
- **Skill Gap Prioritization**: Heuristic priority scoring function:
  $$\text{Priority Score}(s) = (\text{Weight} \times 10) + (\text{Unlocks In Gap} \times 5) - (\text{Difficulty Penalty} \times 2)$$
- **Prerequisite DAG Topological Sequencing**: Guarantees zero prerequisite violations in all generated learning roadmaps.
- **Multi-Format Visual Roadmaps**: Produces interactive SVG flowcharts and structured linear pathways.

---

## 🧠 4. System Architecture

```
                               ┌──────────────────────────────────────────────┐
                               │             Student Input Layer              │
                               │   (Free-Text NLP / PDF Resume / Presets)     │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │       Skill Extraction & Preprocessing       │
                               │  - Regex Tokenizer & Negation Filter         │
                               │  - Multi-word Greedy Entity Matcher          │
                               │  - Alias Dictionary & RapidFuzz Fallback     │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │           Standardized Skill Set             │
                               │        (Normalized Canonical Tokens)         │
                               └──────────┬────────────────────────┬──────────┘
                                          │                        │
                                          ▼                        ▼
               ┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐
               │         Skill Matcher Engine         │  │       Dense Semantic Matcher         │
               │   - Weighted Readiness Score Formula │  │   - Sentence Transformers Embeddings │
               │   - Multi-Career Ranking Matrix      │  │   - Cosine Similarity (tau = 0.50)   │
               └──────────────────┬───────────────────┘  └──────────────────┬───────────────────┘
                                  │                                         │
                                  └───────────────────┬─────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │            Skill Gap Analyzer                │
                               │   - Prerequisite In-Degree Computation       │
                               │   - Heuristic Priority Scoring Function      │
                               │   - Kahn's Priority-Queue Topological Sort   │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │        Personalized Recommendation Engine    │
                               │   - Curated Courses, Docs, & Time Estimates  │
                               │   - Portfolio Project Suitability Scoring    │
                               │   - Milestone Structuring (Phases 1, 2, 3)   │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │         Roadmap & Visualization Engine       │
                               │   - Styled Mermaid Graph Syntax              │
                               │   - Interactive Plotly Analytics Dashboard   │
                               │   - Streamlit Multi-Tab Web Interface        │
                               └──────────────────────────────────────────────┘
```

---

## 💻 5. Technology Stack

- **Programming Language**: Python 3.10+ / 3.11
- **Web UI & Dashboard**: Streamlit
- **Visual Analytics**: Plotly Express & Plotly Graph Objects, Matplotlib, Seaborn
- **NLP & Text Processing**: NLTK, Regular Expressions, RapidFuzz
- **Semantic Embeddings**: HuggingFace `sentence-transformers` (`all-MiniLM-L6-v2`), PyTorch
- **PDF Extraction**: PyMuPDF (`pymupdf`)
- **Data Manipulation**: Pandas, NumPy
- **Evaluation & Benchmarks**: Scikit-Learn (`precision_score`, `recall_score`, `f1_score`, `accuracy_score`)

---

## 📊 6. Dataset Description

All datasets are stored in [`data/`](file:///d:/My%20Project/data/) as relational CSV files:

| Dataset File | Records | Description | Primary Fields |
| :--- | :---: | :--- | :--- |
| [`careers.csv`](file:///d:/My%20Project/data/careers.csv) | 7 | Target industry roles | `career_id`, `career_title`, `category`, `experience_level`, `description` |
| [`skills.csv`](file:///d:/My%20Project/data/skills.csv) | 32 | Standardized technical skills | `skill_id`, `skill_name`, `category`, `difficulty_level`, `description` |
| [`career_skills.csv`](file:///d:/My%20Project/data/career_skills.csv) | 79 | Role-to-skill importance mappings | `career_id`, `skill_id`, `importance_level` (Core/Sec/Opt), `importance_weight` (3/2/1) |
| [`skill_prerequisites.csv`](file:///d:/My%20Project/data/skill_prerequisites.csv) | 28 | Directed learning dependencies | `skill_id`, `prerequisite_skill_id`, `prerequisite_type`, `reason` |
| [`learning_resources.csv`](file:///d:/My%20Project/data/learning_resources.csv) | 26 | Curated courses, docs & books | `resource_id`, `skill_id`, `title`, `platform`, `cost`, `estimated_hours` |
| [`projects.csv`](file:///d:/My%20Project/data/projects.csv) | 10 | Portfolio capstone deliverables | `project_id`, `career_id`, `title`, `difficulty`, `primary_skills`, `deliverables` |
| [`semantic_validation.csv`](file:///d:/My%20Project/data/semantic_validation.csv) | 34 | Labeled semantic benchmark pairs | `query_skill`, `target_skill`, `is_match`, `relationship_type` |

---

## ⚙️ 7. Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone Repository & Create Virtual Environment
```bash
# Clone repository
git clone https://github.com/your-username/student-skill-gap-system.git
cd student-skill-gap-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify System Setup
```bash
python src/verify_setup.py
```

---

## 🏃 8. How to Run

### Run the Web Application & REST API
```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser at `http://localhost:8000` to access the full interactive web application.

### Run Automated System Evaluation & Benchmarks
```bash
python -u src/system_evaluation.py
```

### Run Full System Regression & Robustness Test Suite
```bash
python -m pytest src/ -v
```

---

## 📖 9. Example Usage Walkthrough

### Option A: Free-Text Natural Language Input
1. Open the web interface at `http://localhost:8000`.
2. Select target career: **Data Scientist**.
3. Choose input method: **Manual Selection & Text**.
4. Enter text:
   > *"I know Python, SQL, and Pandas. I have built basic machine learning models using Scikit-Learn, but I have no experience with Docker or Django."*
5. Click **🚀 Analyze Skill Gap & Generate Roadmap**.
6. View:
   - **Weighted Readiness**: ~42.9% Match.
   - **Negated Skills**: Docker and Django are automatically excluded from student profile.
   - **Sequenced Roadmap**: Foundations $\rightarrow$ Statistics $\rightarrow$ Feature Engineering $\rightarrow$ Deep Learning $\rightarrow$ PyTorch.

### Option B: Resume PDF Upload
1. Choose input method: **📄 Upload Resume PDF**.
2. Upload a sample resume (e.g. `data/test_resumes/sample_data_scientist_resume.pdf`).
3. The system extracts detected sections (`Skills`, `Projects`, `Experience`) and displays extracted skills for user verification.
4. Explore interactive Skill Breakdown, Learning Paths, and Recruiter Match reports.

---

## ⚡ 10. Microservice API & Vector Database Architecture

The system features a decoupled FastAPI REST microservice (`api.py`) with persistent vector retrieval (`src/vector_store.py`):

```bash
# Launch FastAPI REST Microservice:
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Interactive Swagger UI Documentation:
http://localhost:8000/docs
```

### REST API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Subsystem health status and indexed vector count |
| `POST` | `/api/v1/analyze-skills` | End-to-end skill matching, gap analysis, and prerequisite roadmap |
| `POST` | `/api/v1/ats-score` | Composite ATS resume scoring & Google XYZ bullet optimization |
| `POST` | `/api/v1/interview/evaluate` | Candidate technical interview answer evaluation against rubric |
| `GET` | `/api/v1/github-scan/{user}` | Public GitHub repository audit & technical skill proof verification |
| `POST` | `/api/v1/vector/hybrid-search` | Hybrid semantic + BM25 search over skill & project embeddings |

### 🐳 Docker & CI/CD Orchestration
```bash
# Run the complete Web Application via Docker Compose:
docker-compose up --build
```

---

## 📈 12. System Evaluation & Quantitative Results

The system was evaluated against manually labeled gold-standard validation sets across 39 comprehensive test suites:

### Component Performance Metrics

| Evaluation Track | Benchmark Size | Precision (%) | Recall (%) | F1-Score (%) | Accuracy (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **NLP Skill Extraction** | 12 complex sentences (39 entities) | **100.0%** | **92.3%** | **96.0%** | — |
| **Exact Matching & Aliasing** | 41 query permutations | **100.0%** | **97.3%** | **98.6%** | **95.1%** |
| **Semantic Embedding Matching ($\tau^* = 0.50$)** | 34 labeled relationship pairs | **100.0%** | **45.0%** | **62.1%** | **67.6%** |
| **Recommendation Graph Audit** | 49 roadmaps (500 steps audited) | — | — | — | **100.0% Consistency** (0 DAG violations) |
| **Unit & Integration Test Suite** | 39 test cases across 12 test files | — | — | — | **100.0% Pass Rate** |

---

## ⚠️ 13. Limitations & Boundary Conditions

1. **Curated Taxonomy Scope**: The system focuses on core data science, software engineering, and AI skills across 7 primary roles.
2. **Short-Keyword Semantic Nuances**: Cosine similarity on short phrases uses an empirical threshold ($\tau = 0.50$) to prevent unrelated technical terms from over-matching.
3. **GitHub API Rate Limits**: Unauthenticated GitHub REST queries are limited to 60 requests/hr; the scanner includes built-in offline test fixture fallbacks.

---

## 📁 14. Repository Folder Structure

```
student-skill-gap-system/
│
├── .github/workflows/ci.yml             # GitHub Actions CI automated testing pipeline
├── data/                                # Relational CSV datasets & test files
│   ├── careers.csv                      # 7 target career roles
│   ├── skills.csv                       # 32 canonical skill taxonomies
│   ├── career_skills.csv                # 79 weighted role-skill relationships
│   ├── skill_prerequisites.csv          # 28 directed acyclic dependency edges
│   ├── learning_resources.csv           # 26 curated educational resources
│   ├── projects.csv                     # 10 structured portfolio deliverables
│   ├── semantic_validation.csv          # 34 labeled semantic benchmark pairs
│   ├── system_evaluation_report.json    # Phase 15 evaluation benchmark report
│   └── test_resumes/                    # Test PDF resumes for testing
│
├── src/                                 # Production core source code
│   ├── __init__.py
│   ├── verify_setup.py                  # Initial environment verification
│   ├── data_loader.py                   # Unified relational data loader & lookup
│   ├── preprocessing.py                 # String cleaning, alias map, RapidFuzz
│   ├── skill_extractor.py               # Rule-based & NLP entity extraction
│   ├── skill_matcher.py                 # Weighted readiness scoring & multi-role ranking
│   ├── semantic_matcher.py              # Sentence Transformers dense embedding matcher
│   ├── gap_analyzer.py                  # Heuristic priority scoring & Kahn's DAG sorting
│   ├── recommendation_engine.py         # Curated resources & project suitability matching
│   ├── roadmap_generator.py             # ASCII & Mermaid visual roadmap generation
│   ├── resume_parser.py                 # PyMuPDF PDF parser & section extractor
│   ├── analytics_dashboard.py           # Plotly visual analytics chart generators
│   ├── interview_simulator.py           # AI Mock Interview Simulator & Rubric Scorer
│   ├── job_market_scraper.py            # Live job scraping & dynamic weight recalculation
│   ├── github_scanner.py                # GitHub repository code proof scanner
│   ├── ats_optimizer.py                 # ATS Resume Scorer & Google XYZ rewriter
│   ├── vector_store.py                  # Persistent dense vector database & k-NN retrieval
│   ├── test_preprocessing.py            # Preprocessing unit tests
│   ├── test_skill_matcher.py            # Skill matcher unit tests
│   ├── test_gap_analyzer.py             # Gap analyzer unit tests
│   ├── test_recommendation_engine.py    # Recommendation engine unit tests
│   ├── test_roadmap_generator.py        # Roadmap generator unit tests
│   ├── test_skill_extractor.py          # NLP extractor unit tests
│   ├── test_semantic_matcher.py         # Semantic matcher unit tests
│   ├── test_resume_parser.py            # Resume parser unit tests
│   ├── test_analytics_dashboard.py      # Analytics dashboard unit tests
│   ├── test_interview_simulator.py      # Mock interview engine unit tests
│   ├── test_job_market_scraper.py       # Job scraper unit tests
│   ├── test_github_scanner.py           # GitHub profile scanner unit tests
│   ├── test_ats_optimizer.py            # ATS optimizer unit tests
│   ├── test_vector_store.py             # Vector store unit tests
│   ├── test_api.py                      # FastAPI REST microservice integration tests
│   ├── test_system_robustness.py        # System robustness & edge cases test suite
│   └── test_end_to_end_integration.py   # Complete end-to-end integration test suite
│
├── api.py                               # FastAPI Production Microservice & Web App
├── frontend/                            # Modern Vanilla JS + CSS Frontend
│   ├── index.html                       # 9-Section Single Page Application
│   ├── app.js                           # Frontend controller & API client
│   └── style.css                        # Design system tokens & animations
├── Dockerfile                           # Production container specification
├── docker-compose.yml                   # Container orchestration config
├── requirements.txt                     # Pinned Python package dependencies
├── .gitignore                           # Git ignore rules
└── README.md                            # Comprehensive project documentation
```

---

## 👥 Authors & Academic Context

- **Project**: Student Skill Gap & Career Recommendation System (Final-Year Major Capstone Project)
- **Domain**: Artificial Intelligence, Natural Language Processing, Recommender Systems, Vector Databases, Microservice Architecture
- **License**: MIT License

