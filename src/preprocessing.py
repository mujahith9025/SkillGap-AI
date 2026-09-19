"""
Text Preprocessing and Skill Normalization Module
Phase 5: Data Cleaning and Skill Normalization

Provides deterministic text cleaning, alias resolution, canonical mapping,
and fuzzy typo correction to standardize user skill inputs.
"""

import re
from typing import Dict, List, Optional, Set, Tuple
import pandas as pd
from rapidfuzz import process, fuzz

from data_loader import DataLoader


class SkillPreprocessor:
    """
    Standardizes and normalizes noisy, user-provided skill names against
    the official canonical skill taxonomy.
    """

    # Comprehensive alias & synonym dictionary mapping variations to canonical names
    # Canonical names match skills.csv exactly
    DEFAULT_ALIAS_MAP: Dict[str, str] = {
        # Programming & Languages
        "python": "Python",
        "python3": "Python",
        "python 3": "Python",
        "python programming": "Python",
        "python development": "Python",
        "py": "Python",
        
        # Databases & SQL
        "sql": "SQL",
        "mysql": "SQL",
        "postgresql": "SQL",
        "postgres": "SQL",
        "sqlite": "SQL",
        "sql server": "SQL",
        "tsql": "SQL",
        "plsql": "SQL",
        "relational database": "Relational Database Design",
        "rdbms": "Relational Database Design",
        "database design": "Relational Database Design",
        "schema design": "Relational Database Design",
        "db design": "Relational Database Design",
        
        # Mathematics & Statistics
        "statistics": "Statistics & Probability",
        "stats": "Statistics & Probability",
        "probability": "Statistics & Probability",
        "statistics & probability": "Statistics & Probability",
        "statistics and probability": "Statistics & Probability",
        "inferential statistics": "Statistics & Probability",
        "hypothesis testing": "Statistics & Probability",
        "linear algebra": "Linear Algebra",
        "matrix algebra": "Linear Algebra",
        "matrices": "Linear Algebra",
        "vectors": "Linear Algebra",
        
        # Data Analysis & Python Data Stack
        "pandas": "Pandas",
        "pandas library": "Pandas",
        "numpy": "NumPy",
        "numpy array": "NumPy",
        "matplotlib": "Matplotlib & Seaborn",
        "seaborn": "Matplotlib & Seaborn",
        "matplotlib and seaborn": "Matplotlib & Seaborn",
        "matplotlib & seaborn": "Matplotlib & Seaborn",
        "data cleaning": "Data Preprocessing & Cleaning",
        "data preprocessing": "Data Preprocessing & Cleaning",
        "data wrangling": "Data Preprocessing & Cleaning",
        "data cleansing": "Data Preprocessing & Cleaning",
        "feature engineering": "Feature Engineering",
        "feature extraction": "Feature Engineering",
        "feature selection": "Feature Engineering",
        
        # BI & Visualization
        "data visualization": "Data Visualization",
        "data viz": "Data Visualization",
        "visualization": "Data Visualization",
        "dataviz": "Data Visualization",
        "charts": "Data Visualization",
        "tableau": "Tableau",
        "tablo": "Tableau",
        "tableau desktop": "Tableau",
        "tableau public": "Tableau",
        "power bi": "Power BI",
        "powerbi": "Power BI",
        "ms power bi": "Power BI",
        "excel": "Excel",
        "ms excel": "Excel",
        "microsoft excel": "Excel",
        "spreadsheets": "Excel",
        "pivot tables": "Excel",
        "vlookup": "Excel",
        
        # Machine Learning
        "machine learning": "Machine Learning",
        "ml": "Machine Learning",
        "scikit-learn": "Scikit-Learn",
        "scikit learn": "Scikit-Learn",
        "sklearn": "Scikit-Learn",
        "scikitlearn": "Scikit-Learn",
        "scikit-leran": "Scikit-Learn",
        "classical ml": "Machine Learning",
        "supervised learning": "Machine Learning",
        "unsupervised learning": "Machine Learning",
        
        # Deep Learning & Neural Nets
        "deep learning": "Deep Learning",
        "deep-learning": "Deep Learning",
        "deeplearning": "Deep Learning",
        "dl": "Deep Learning",
        "neural networks": "Deep Learning",
        "ann": "Deep Learning",
        "cnn": "Deep Learning",
        "rnn": "Deep Learning",
        "pytorch": "PyTorch",
        "torch": "PyTorch",
        "pytorch framework": "PyTorch",
        "tensorflow": "TensorFlow",
        "tf": "TensorFlow",
        "tensorflow 2": "TensorFlow",
        "keras": "TensorFlow",
        
        # NLP & AI
        "nlp": "Natural Language Processing (NLP)",
        "natural language processing": "Natural Language Processing (NLP)",
        "text mining": "Natural Language Processing (NLP)",
        "computational linguistics": "Natural Language Processing (NLP)",
        "cv": "Computer Vision (CV)",
        "computer vision": "Computer Vision (CV)",
        "image processing": "Computer Vision (CV)",
        "opencv": "Computer Vision (CV)",
        "llm": "Large Language Models (LLMs)",
        "llms": "Large Language Models (LLMs)",
        "large language models": "Large Language Models (LLMs)",
        "generative ai": "Large Language Models (LLMs)",
        "genai": "Large Language Models (LLMs)",
        "transformers": "Large Language Models (LLMs)",
        "chatgpt": "Large Language Models (LLMs)",
        "rag": "Large Language Models (LLMs)",
        
        # DevOps, Cloud & Tools
        "git": "Git & GitHub",
        "github": "Git & GitHub",
        "git & github": "Git & GitHub",
        "git and github": "Git & GitHub",
        "git/github": "Git & GitHub",
        "git / github": "Git & GitHub",
        "version control": "Git & GitHub",
        "docker": "Docker",
        "containerization": "Docker",
        "docker containers": "Docker",
        "linux": "Linux & Bash Scripting",
        "bash": "Linux & Bash Scripting",
        "shell scripting": "Linux & Bash Scripting",
        "linux & bash scripting": "Linux & Bash Scripting",
        "cloud": "Cloud Fundamentals (AWS/GCP)",
        "aws": "Cloud Fundamentals (AWS/GCP)",
        "gcp": "Cloud Fundamentals (AWS/GCP)",
        "azure": "Cloud Fundamentals (AWS/GCP)",
        "cloud fundamentals": "Cloud Fundamentals (AWS/GCP)",
        "cloud computing": "Cloud Fundamentals (AWS/GCP)",
        "amazon web services": "Cloud Fundamentals (AWS/GCP)",
        "google cloud": "Cloud Fundamentals (AWS/GCP)",
        "mlops": "MLOps & Model Deployment",
        "model deployment": "MLOps & Model Deployment",
        "mlops & model deployment": "MLOps & Model Deployment",
        
        # Software Engineering & Web
        "fastapi": "FastAPI",
        "fast api": "FastAPI",
        "django": "Django",
        "django framework": "Django",
        "rest api": "RESTful APIs",
        "rest apis": "RESTful APIs",
        "restful api": "RESTful APIs",
        "restful apis": "RESTful APIs",
        "rest": "RESTful APIs",
        "api development": "RESTful APIs",
        
        # Big Data & Business Analytics
        "spark": "Big Data Fundamentals (Spark)",
        "pyspark": "Big Data Fundamentals (Spark)",
        "apache spark": "Big Data Fundamentals (Spark)",
        "big data": "Big Data Fundamentals (Spark)",
        "hadoop": "Big Data Fundamentals (Spark)",
        "business metrics": "Business Metrics & KPI Modeling",
        "kpi": "Business Metrics & KPI Modeling",
        "kpis": "Business Metrics & KPI Modeling",
        "business analytics": "Business Metrics & KPI Modeling",
        "kpi modeling": "Business Metrics & KPI Modeling",
    }

    def __init__(self, data_loader: Optional[DataLoader] = None, fuzzy_threshold: float = 85.0):
        """
        Initializes the preprocessor with the canonical skills taxonomy.
        
        Args:
            data_loader: Instance of DataLoader to fetch canonical skills.
            fuzzy_threshold: Minimum RapidFuzz match ratio (0-100) to accept a typo match.
        """
        self.loader = data_loader if data_loader else DataLoader()
        self.fuzzy_threshold = fuzzy_threshold
        
        # Extract canonical skill set and lookup maps
        self.canonical_skills: Set[str] = set(self.loader.skills["skill_name"].tolist())
        self.canonical_lookup: Dict[str, str] = {s.lower(): s for s in self.canonical_skills}
        
        # Build normalized alias map
        self.alias_map: Dict[str, str] = {}
        for alias, canonical in self.DEFAULT_ALIAS_MAP.items():
            self.alias_map[self.clean_string(alias)] = canonical

    @staticmethod
    def clean_string(text: str) -> str:
        """
        Performs baseline string cleaning:
        - Strips whitespace
        - Converts to lowercase
        - Collapses multiple whitespace/tabs
        - Cleans special surrounding punctuation while preserving essential symbols (+, #, -, &, /)
        """
        if not isinstance(text, str):
            return ""
        
        cleaned = text.strip().lower()
        # Replace multiple spaces/tabs/newlines with a single space
        cleaned = re.sub(r"\s+", " ", cleaned)
        # Strip leading/trailing non-alphanumeric chars (except +, #)
        cleaned = re.sub(r"^[^\w+#]+|[^\w+#]+$", "", cleaned)
        return cleaned

    def normalize_single_skill(self, raw_skill: str) -> Tuple[Optional[str], str]:
        """
        Normalizes a single skill input string through a multi-stage pipeline:
        1. Clean and validate string
        2. Exact match against canonical skills (case-insensitive)
        3. Alias & abbreviation dictionary lookup
        4. High-confidence fuzzy string matching (typo tolerance)

        Returns:
            Tuple of (canonical_skill_name_or_None, resolution_method)
        """
        cleaned = self.clean_string(raw_skill)
        if not cleaned:
            return None, "empty_input"

        # 1. Exact canonical match (case-insensitive)
        if cleaned in self.canonical_lookup:
            return self.canonical_lookup[cleaned], "exact_canonical"

        # 2. Alias dictionary lookup
        if cleaned in self.alias_map:
            return self.alias_map[cleaned], "alias_lookup"

        # 3. Fuzzy match against all known aliases and canonical names (Typo tolerance)
        candidates = list(self.canonical_lookup.keys()) + list(self.alias_map.keys())
        best_match = process.extractOne(
            cleaned,
            candidates,
            scorer=fuzz.ratio,
            score_cutoff=self.fuzzy_threshold
        )
        
        if best_match:
            matched_key, score, _ = best_match
            if matched_key in self.canonical_lookup:
                return self.canonical_lookup[matched_key], f"fuzzy_canonical (score={score:.1f})"
            elif matched_key in self.alias_map:
                return self.alias_map[matched_key], f"fuzzy_alias (score={score:.1f})"

        return None, "unrecognized"

    def normalize_skill_list(self, raw_skills: List[str]) -> List[str]:
        """
        Normalizes an iterable of raw skill strings, filtering out unrecognized
        entries and deduplicating canonical results while preserving order.
        """
        normalized: List[str] = []
        seen: Set[str] = set()

        for raw_s in raw_skills:
            canonical, _ = self.normalize_single_skill(raw_s)
            if canonical and canonical not in seen:
                seen.add(canonical)
                normalized.append(canonical)

        return normalized

    def parse_raw_text_skills(self, text_input: str) -> List[str]:
        """
        Parses a free-form text input containing comma-separated, semicolon-separated,
        or newline/bullet-separated skills into a clean, normalized list of canonical skills.
        
        Example Input:
            "Skills: Python, pandas, ML, deep-learning, pythn, Tableau, SQL; Git"
        Returns:
            ['Python', 'Pandas', 'Machine Learning', 'Deep Learning', 'Tableau', 'SQL', 'Git & GitHub']
        """
        if not text_input or not isinstance(text_input, str):
            return []

        # Strip common resume header prefixes like "Skills:", "Technical Skills:", "Key Skills:"
        cleaned_text = re.sub(r"^(?:skills|technical skills|key skills|core competencies|competencies)\s*:\s*", "", text_input, flags=re.IGNORECASE)

        # Split on commas, semicolons, pipe (|), bullet points (•, *, ·), newlines, but NOT intra-word hyphens
        tokens = re.split(r"[,;\n|\u2022\u00b7\*]+", cleaned_text)
        
        cleaned_tokens = [t.strip() for t in tokens if t.strip()]
        return self.normalize_skill_list(cleaned_tokens)
