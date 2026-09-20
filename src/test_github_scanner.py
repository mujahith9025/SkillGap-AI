"""
Unit Tests for GitHub Profile & Project Code Scanner Module
"""

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from data_loader import DataLoader
from skill_extractor import NLPSkillExtractor
from github_scanner import (
    GitHubProfileScanner,
    GitHubAuditReport,
    ASTCodeAnalysisReport,
    ReadmeAuditReport,
    ProjectBlueprint
)


class TestGitHubScanner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.loader = DataLoader()
        cls.extractor = NLPSkillExtractor(data_loader=cls.loader)
        cls.scanner = GitHubProfileScanner(data_loader=cls.loader, skill_extractor=cls.extractor)

    def test_01_scan_sample_profile(self):
        """Scanning a sample profile should audit repos and return verified technical skills."""
        report = self.scanner.scan_github_profile("alex_datascientist", claimed_skills=["Python", "SQL", "PyTorch", "Docker"])
        self.assertIsInstance(report, GitHubAuditReport)
        self.assertEqual(report.username, "alex_datascientist")
        self.assertGreater(report.total_repos_audited, 0)
        self.assertIn("Python", report.verified_skills)
        self.assertGreater(report.hands_on_evidence_score, 0.0)
        self.assertGreaterEqual(len(report.top_project_blueprints), 1)

    def test_02_detect_missing_and_recommendations(self):
        """Unverified skills should generate recommended projects and tailored blueprints."""
        report = self.scanner.scan_github_profile("jordan_fresher", claimed_skills=["Python", "SQL", "Docker", "FastAPI"])
        self.assertIn("Docker", report.unverified_claimed_skills)
        self.assertGreater(len(report.recommended_projects_to_build), 0)
        self.assertGreaterEqual(len(report.top_project_blueprints), 1)

    def test_03_ast_code_analysis_clean_modular(self):
        """AST analysis of clean OOP code should detect classes, type hints, and low complexity."""
        clean_code = '''
from typing import List, Dict

class DataProcessor:
    """Processes tabular datasets with validation."""
    
    def __init__(self, name: str):
        self.name = name

    def compute_metrics(self, values: List[float]) -> Dict[str, float]:
        """Calculates mean and standard deviation."""
        if not values:
            return {"mean": 0.0}
        total = sum(values)
        return {"mean": total / len(values)}
'''
        report = self.scanner.analyze_code_quality(clean_code, "processor.py")
        self.assertIsInstance(report, ASTCodeAnalysisReport)
        self.assertTrue(report.is_valid_syntax)
        self.assertEqual(report.classes_count, 1)
        self.assertEqual(report.functions_count, 2)
        self.assertGreater(report.type_hint_coverage_pct, 60.0)
        self.assertIn("A", report.complexity_grade)
        self.assertIn("Modular OOP", report.oop_modularity_tier)

    def test_04_ast_code_analysis_syntax_error(self):
        """Invalid Python syntax should be caught gracefully without crashing."""
        broken_code = "def broken_func(:\n    return 42"
        report = self.scanner.analyze_code_quality(broken_code, "broken.py")
        self.assertFalse(report.is_valid_syntax)
        self.assertIsNotNone(report.syntax_error_message)
        self.assertIn("D", report.complexity_grade)

    def test_05_ast_code_analysis_complex_function(self):
        """Code with heavy branching should receive higher cyclomatic complexity."""
        complex_code = '''
def complex_decision(a, b, c, d, e):
    if a > 0:
        if b > 0 and c > 0:
            for x in range(10):
                if d == x:
                    return 1
                elif e == x:
                    return 2
        elif b < 0 or c < 0:
            while a > 0:
                a -= 1
    return 0
'''
        report = self.scanner.analyze_code_quality(complex_code, "complex.py")
        self.assertTrue(report.is_valid_syntax)
        self.assertGreater(report.max_cyclomatic_complexity, 7)
        self.assertEqual(report.classes_count, 0)
        self.assertIn("Procedural", report.oop_modularity_tier)

    def test_06_audit_readme_quality_high_score(self):
        """Comprehensive README markdown with diagrams and setup steps should score high."""
        readme = """# Customer Churn Prediction Engine
End-to-end machine learning microservice that predicts customer churn probability in real time.

![Build Status](https://img.shields.io/badge/build-passing-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## System Architecture
```mermaid
graph TD
    A[Client Request] --> B[FastAPI Gateway]
    B --> C[ML Inference Engine]
```

## Quickstart & Installation
```bash
git clone https://github.com/alex/churn-prediction.git
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Live Cloud Demo
Explore the interactive web app at: https://churn-predictor.streamlit.app/

## API Usage Example
```python
import requests
res = requests.post("http://localhost:8000/predict", json={"tenure": 12, "monthly_charges": 65.5})
print(res.json())
```
"""
        report = self.scanner.audit_readme_quality(readme)
        self.assertIsInstance(report, ReadmeAuditReport)
        self.assertGreaterEqual(report.overall_readme_score, 80.0)
        self.assertTrue(report.has_architecture_diagram)
        self.assertTrue(report.has_installation_steps)
        self.assertTrue(report.has_live_demo)
        self.assertTrue(report.has_usage_examples)

    def test_07_audit_readme_quality_minimal_score(self):
        """Sparse or single-line README should trigger lower score and specific recommendations."""
        readme = "# My Project\nWork in progress."
        report = self.scanner.audit_readme_quality(readme)
        self.assertLess(report.overall_readme_score, 50.0)
        self.assertGreater(len(report.actionable_recommendations), 2)

    def test_08_generate_project_blueprint_curated_docker(self):
        """Generating a blueprint for Docker should pull curated templates and milestones."""
        bp = self.scanner.generate_project_blueprint("Docker", "Data Scientist")
        self.assertIsInstance(bp, ProjectBlueprint)
        self.assertEqual(bp.target_skill, "Docker")
        self.assertIn("Dockerfile", bp.starter_files)
        self.assertEqual(len(bp.milestones), 4)
        self.assertIn("├── Dockerfile", bp.folder_tree)

    def test_09_generate_project_blueprint_dynamic_skill(self):
        """Generating a blueprint for an unmapped skill should synthesize a clean dynamic blueprint."""
        bp = self.scanner.generate_project_blueprint("Apache Kafka", "Data Engineer")
        self.assertIsInstance(bp, ProjectBlueprint)
        self.assertEqual(bp.target_skill, "Apache Kafka")
        self.assertEqual(len(bp.milestones), 4)
        self.assertIn("Apache Kafka", bp.tech_stack)


if __name__ == "__main__":
    unittest.main(verbosity=2)
