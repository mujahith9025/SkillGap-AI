# Student Skill Gap & Career Recommendation System

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![NLP Engine](https://img.shields.io/badge/NLP-SentenceTransformers-yellow.svg)](https://www.sbert.net/)
[![Visualization](https://img.shields.io/badge/Plots-Plotly-3F4F75.svg)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/Tests-11%2F11%20Passed-brightgreen.svg)]()

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
- **Interactive Visual Dashboard**: Deliver an interactive Streamlit web application featuring category radar charts, donut criticality breakdowns, cross-career rankings, and requirement heatmaps.

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
- **Multi-Format Visual Roadmaps**: Produces styled Mermaid graph flowcharts and structured ASCII linear pathways.
- **5 Interactive Plotly Visualizations**: Category Radar Chart, Matched vs. Missing Donut Chart, Cross-Career Comparison Bar, Gap Difficulty Distribution, and Career-Skill Matrix Heatmap.

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

### Run the Interactive Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Run Automated System Evaluation & Benchmarks
```bash
python -u src/system_evaluation.py
```

### Run Full System Regression & Robustness Test Suite
```bash
python -u src/test_system_robustness.py
python -u src/test_end_to_end_integration.py
```

---

## 📖 9. Example Usage Walkthrough

### Option A: Free-Text Natural Language Input
1. Open the Streamlit sidebar.
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
4. Explore interactive Radar, Donut, and Cross-Career Comparison charts.

---

## 🖼️ 10. Dashboard Preview & Screenshots

| Tab | Focus Area | Visual Components |
| :--- | :--- | :--- |
| **Tab 1: Skill Gap & Match** | Role Readiness Overview | Metric cards, Matched badges, Prioritized gap badges, Radar chart, Donut breakdown, Cross-career ranking table |
| **Tab 2: Learning Roadmap** | Sequential Milestone Path | Phase accordion containers, Time estimates, Resource links, Visual Mermaid flowchart |
| **Tab 3: Projects & Resources** | Practical Bridge Artifacts | Gap-relevance scores, Problem statements, Tech stack, Resume deliverables |
| **Tab 4: Dataset Analytics** | Curated Taxonomy Explorer | Interactive Career vs. Skill requirement matrix heatmap, Category bar charts |
| **Tab 5: Architecture** | Technical Blueprint | System pipeline architecture and heuristic scoring explanations |

---

## 📈 11. System Evaluation & Quantitative Results

The system was evaluated against manually labeled gold-standard validation sets in Phase 15 ([`src/system_evaluation.py`](file:///d:/My%20Project/src/system_evaluation.py)):

### Component Performance Metrics

| Evaluation Track | Benchmark Size | Precision (%) | Recall (%) | F1-Score (%) | Accuracy (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **NLP Skill Extraction** | 12 complex sentences (39 entities) | **100.0%** | **92.3%** | **96.0%** | — |
| **Exact Matching & Aliasing** | 41 query permutations | **100.0%** | **97.3%** | **98.6%** | **95.1%** |
| **Semantic Embedding Matching ($\tau^* = 0.50$)** | 34 labeled relationship pairs | **100.0%** | **45.0%** | **62.1%** | **67.6%** |
| **Recommendation Graph Audit** | 49 roadmaps (500 steps audited) | — | — | — | **100.0% Consistency** (0 DAG violations) |

---

## ⚠️ 12. Limitations & Boundary Conditions

1. **Curated Taxonomy Scope**: The system focuses on 32 core data science, software engineering, and AI skills across 7 roles. Unrelated domain terms (e.g., *Quantum Computing*, *Solidity*) are filtered out.
2. **Short-Keyword Semantic Nuances**: Cosine similarity on short phrases requires an empirical threshold ($\tau = 0.50$) to prevent unrelated technical terms from over-matching.
3. **Complex Sentence Negations**: Multi-clause disjunctive statements with mixed tenses may occasionally require manual verification in the UI review widget.

---

## 🔮 13. Future Enhancements

- [ ] **Dynamic Live Job Market Scraping**: Incorporate live job postings (e.g., LinkedIn / Indeed APIs) to dynamically adjust role importance weights.
- [ ] **Generative LLM Interview Simulation**: Add interactive mock technical interview practice tailored to the student's identified skill gaps.
- [ ] **Automated GitHub Repository Auditing**: Connect GitHub profiles to automatically verify student code repositories against recommended project deliverables.
- [ ] **Multi-Role Blended Career Paths**: Support hybrid careers (e.g., MLOps Engineer blending Data Engineering and Backend Development).

---

## 📁 14. Repository Folder Structure

```
student-skill-gap-system/
│
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
├── notebooks/                           # Jupyter notebooks for EDA & research
│   └── 01_data_analysis.ipynb           # Exploratory data analysis notebook
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
│   ├── analytics_dashboard.py           # 5 Plotly visual analytics chart generators
│   ├── system_evaluation.py             # Comprehensive Phase 15 evaluation suite
│   ├── test_preprocessing.py            # Preprocessing unit tests
│   ├── test_skill_matcher.py            # Skill matcher unit tests
│   ├── test_gap_analyzer.py             # Gap analyzer unit tests
│   ├── test_recommendation_engine.py    # Recommendation engine unit tests
│   ├── test_roadmap_generator.py        # Roadmap generator unit tests
│   ├── test_skill_extractor.py          # NLP extractor unit tests
│   ├── test_semantic_matcher.py         # Semantic matcher unit tests
│   ├── test_resume_parser.py            # Resume parser unit tests
│   ├── test_analytics_dashboard.py      # Analytics dashboard unit tests
│   ├── test_system_robustness.py        # Phase 16 robustness & edge cases test suite
│   └── test_end_to_end_integration.py   # Phase 17 complete integration test suite
│
├── app.py                               # 5-Tab Interactive Streamlit Web Application
├── requirements.txt                     # Pinned Python package dependencies
├── .gitignore                           # Git ignore rules
└── README.md                            # Comprehensive project documentation
```

---

## 👥 Authors & Academic Context

- **Project**: Student Skill Gap & Career Recommendation System
- **Domain**: Artificial Intelligence, Natural Language Processing, Recommender Systems, Data Science
- **Target Audience**: Final-Year B.Tech / M.Tech / BCA / MCA Major Project & Placement Portfolio

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
