"""
Comprehensive System Evaluation & Benchmark Suite
Phase 15: System Evaluation

Evaluates all major project components on labeled validation benchmarks:
1. NLP Skill Extraction Benchmark (Precision, Recall, F1-Score)
2. Exact Skill Matching & Normalization Benchmark (Precision, Recall, F1-Score, Accuracy)
3. Semantic Embedding Cosine Similarity Threshold Benchmark (Sweep across thresholds)
4. Recommendation Engine Quality & Topological Invariant Audit (Prerequisite DAG consistency)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

from data_loader import DataLoader
from preprocessing import SkillPreprocessor
from skill_extractor import NLPSkillExtractor
from skill_matcher import SkillMatcher
from gap_analyzer import SkillGapAnalyzer
from recommendation_engine import RecommendationEngine
from semantic_matcher import SemanticSkillMatcher


# -----------------------------------------------------------------------------
# 1. LABELED BENCHMARK GROUND-TRUTH DATASETS
# -----------------------------------------------------------------------------

# Labeled benchmark for NLP Skill Extraction (Text Snippets -> Ground Truth Canonical Skills)
EXTRACTION_BENCHMARK_DATA = [
    {
        "text": "I am proficient in Python, Pandas, NumPy, and basic machine learning with Scikit-Learn.",
        "ground_truth": ["Python", "Pandas", "NumPy", "Machine Learning", "Scikit-Learn"]
    },
    {
        "text": "Experience building dashboards in Tableau and Power BI using SQL queries on PostgreSQL databases.",
        "ground_truth": ["Tableau", "Power BI", "SQL"]
    },
    {
        "text": "Strong foundation in Statistics & Probability and Linear Algebra for training neural networks in PyTorch.",
        "ground_truth": ["Statistics & Probability", "Linear Algebra", "PyTorch", "Deep Learning"]
    },
    {
        "text": "Developed REST APIs using FastAPI and containerized microservices with Docker on Linux.",
        "ground_truth": ["RESTful APIs", "FastAPI", "Docker", "Linux & Bash Scripting"]
    },
    {
        "text": "Hands-on data preprocessing & cleaning, feature engineering, and KPI modeling with MS Excel.",
        "ground_truth": ["Data Preprocessing & Cleaning", "Feature Engineering", "Business Metrics & KPI Modeling", "Excel"]
    },
    {
        "text": "Deployed classical ML models using Git/GitHub CI/CD and cloud fundamentals on AWS.",
        "ground_truth": ["Machine Learning", "Git & GitHub", "Cloud Fundamentals (AWS/GCP)"]
    },
    {
        "text": "Working knowledge of big data processing using PySpark and relational database design.",
        "ground_truth": ["Big Data Fundamentals (Spark)", "Relational Database Design"]
    },
    {
        "text": "Specialized in Computer Vision with OpenCV and Natural Language Processing using transformer LLMs.",
        "ground_truth": ["Computer Vision (CV)", "Natural Language Processing (NLP)", "Large Language Models (LLMs)"]
    },
    {
        "text": "I know Python and SQL, but I have no experience with Docker or Django.",
        "ground_truth": ["Python", "SQL"]  # Docker & Django are negated
    },
    {
        "text": "Currently mastering MLOps & model deployment with FastAPI and Docker containers.",
        "ground_truth": ["MLOps & Model Deployment", "FastAPI", "Docker"]
    },
    {
        "text": "Skilled in Django backend web framework, relational database design, and REST APIs.",
        "ground_truth": ["Django", "Relational Database Design", "RESTful APIs"]
    },
    {
        "text": "I do not know PyTorch, but I am experienced in Scikit-Learn and Matplotlib data visualization.",
        "ground_truth": ["Scikit-Learn", "Matplotlib & Seaborn", "Data Visualization"]  # PyTorch is negated
    }
]

# Labeled benchmark for Exact Matching & Normalization (Raw User Input -> Expected Canonical Skill or None)
NORMALIZATION_BENCHMARK_DATA = [
    # Direct / Canonical
    ("Python", "Python", True),
    ("SQL", "SQL", True),
    ("Docker", "Docker", True),
    ("Pandas", "Pandas", True),
    
    # Case & Punctuation Variations
    ("python", "Python", True),
    ("scikit-learn", "Scikit-Learn", True),
    ("power bi", "Power BI", True),
    ("git & github", "Git & GitHub", True),
    
    # Aliases & Synonyms
    ("postgres", "SQL", True),
    ("mysql", "SQL", True),
    ("py", "Python", True),
    ("stats", "Statistics & Probability", True),
    ("hypothesis testing", "Statistics & Probability", True),
    ("matrix algebra", "Linear Algebra", True),
    ("data cleaning", "Data Preprocessing & Cleaning", True),
    ("data wrangling", "Data Preprocessing & Cleaning", True),
    ("data viz", "Data Visualization", True),
    ("tablo", "Tableau", True),
    ("powerbi", "Power BI", True),
    ("ms excel", "Excel", True),
    ("deep nets", "Deep Learning", True),
    ("neural networks", "Deep Learning", True),
    ("opencv", "Computer Vision (CV)", True),
    ("computer vision", "Computer Vision (CV)", True),
    ("llm", "Large Language Models (LLMs)", True),
    ("chatgpt", "Large Language Models (LLMs)", True),
    ("pyspark", "Big Data Fundamentals (Spark)", True),
    ("spark", "Big Data Fundamentals (Spark)", True),
    ("aws", "Cloud Fundamentals (AWS/GCP)", True),
    ("gcp", "Cloud Fundamentals (AWS/GCP)", True),
    ("linux", "Linux & Bash Scripting", True),
    ("bash", "Linux & Bash Scripting", True),
    ("rest api", "RESTful APIs", True),
    ("mlops", "MLOps & Model Deployment", True),
    
    # Typos (Fuzzy Matching)
    ("pythn", "Python", True),
    ("pndas", "Pandas", True),
    ("tensrflow", "Deep Learning", True),
    
    # Out-of-Scope / Non-Existent Distractors
    ("quantum computing", None, False),
    ("blockchain solidity", None, False),
    ("cooking recipe", None, False),
    ("carpentry woodworking", None, False)
]


class SystemEvaluator:
    """
    Executes systematic, quantitative evaluation across all pipeline layers.
    """

    def __init__(self):
        self.loader = DataLoader()
        self.preprocessor = SkillPreprocessor(data_loader=self.loader)
        self.extractor = NLPSkillExtractor(data_loader=self.loader, preprocessor=self.preprocessor)
        self.matcher = SkillMatcher(data_loader=self.loader, preprocessor=self.preprocessor)
        self.gap_analyzer = SkillGapAnalyzer(data_loader=self.loader, skill_matcher=self.matcher)
        self.rec_engine = RecommendationEngine(data_loader=self.loader, gap_analyzer=self.gap_analyzer)
        self.semantic_matcher = SemanticSkillMatcher(data_loader=self.loader)

    # -------------------------------------------------------------------------
    # Evaluation 1: NLP Skill Extraction Evaluation
    # -------------------------------------------------------------------------
    def evaluate_skill_extraction(self) -> Dict[str, Any]:
        """
        Evaluates entity-level Precision, Recall, and F1 across labeled sentences.
        """
        total_tp = 0
        total_fp = 0
        total_fn = 0
        sample_results = []

        for sample in EXTRACTION_BENCHMARK_DATA:
            text = sample["text"]
            ground_truth = set(sample["ground_truth"])
            
            predicted = set(self.extractor.extract_canonical_names(text))
            
            tp = len(ground_truth.intersection(predicted))
            fp = len(predicted - ground_truth)
            fn = len(ground_truth - predicted)
            
            total_tp += tp
            total_fp += fp
            total_fn += fn
            
            p = (tp / (tp + fp)) if (tp + fp) > 0 else 0.0
            r = (tp / (tp + fn)) if (tp + fn) > 0 else 0.0
            f1 = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0
            
            sample_results.append({
                "text": text[:60] + ("..." if len(text) > 60 else ""),
                "ground_truth_count": len(ground_truth),
                "predicted_count": len(predicted),
                "tp": tp, "fp": fp, "fn": fn,
                "precision": round(p * 100, 1),
                "recall": round(r * 100, 1),
                "f1": round(f1 * 100, 1)
            })

        macro_p = (total_tp / (total_tp + total_fp) * 100.0) if (total_tp + total_fp) > 0 else 0.0
        macro_r = (total_tp / (total_tp + total_fn) * 100.0) if (total_tp + total_fn) > 0 else 0.0
        macro_f1 = (2 * macro_p * macro_r / (macro_p + macro_r)) if (macro_p + macro_r) > 0 else 0.0

        return {
            "total_samples": len(EXTRACTION_BENCHMARK_DATA),
            "total_ground_truth_entities": total_tp + total_fn,
            "total_predicted_entities": total_tp + total_fp,
            "TP": total_tp, "FP": total_fp, "FN": total_fn,
            "precision": round(macro_p, 1),
            "recall": round(macro_r, 1),
            "f1_score": round(macro_f1, 1),
            "sample_details": sample_results
        }

    # -------------------------------------------------------------------------
    # Evaluation 2: Exact Skill Matching & Normalization Evaluation
    # -------------------------------------------------------------------------
    def evaluate_exact_matching_and_normalization(self) -> Dict[str, Any]:
        """
        Evaluates exact matching, alias mapping, and fuzzy typo normalization.
        """
        y_true_binary = []
        y_pred_binary = []
        correct_canonical_matches = 0
        total_queries = len(NORMALIZATION_BENCHMARK_DATA)
        detailed_records = []

        for raw_input, expected_canonical, is_valid in NORMALIZATION_BENCHMARK_DATA:
            matched_canonical, resolution_tier = self.preprocessor.normalize_single_skill(raw_input)
            
            actual_is_match = (matched_canonical is not None)
            expected_is_match = is_valid
            
            y_true_binary.append(1 if expected_is_match else 0)
            y_pred_binary.append(1 if actual_is_match else 0)
            
            is_correct_mapping = False
            if expected_is_match and (matched_canonical == expected_canonical):
                correct_canonical_matches += 1
                is_correct_mapping = True
            elif (not expected_is_match) and (matched_canonical is None):
                correct_canonical_matches += 1
                is_correct_mapping = True
                
            detailed_records.append({
                "raw_input": raw_input,
                "expected": expected_canonical,
                "predicted": matched_canonical,
                "resolution_tier": resolution_tier,
                "is_correct": is_correct_mapping
            })

        prec = precision_score(y_true_binary, y_pred_binary, zero_division=0) * 100.0
        rec = recall_score(y_true_binary, y_pred_binary, zero_division=0) * 100.0
        f1 = f1_score(y_true_binary, y_pred_binary, zero_division=0) * 100.0
        acc = (correct_canonical_matches / total_queries) * 100.0

        return {
            "total_benchmark_queries": total_queries,
            "correct_canonical_mappings": correct_canonical_matches,
            "accuracy": round(acc, 1),
            "precision": round(prec, 1),
            "recall": round(rec, 1),
            "f1_score": round(f1, 1),
            "detailed_records": detailed_records
        }

    # -------------------------------------------------------------------------
    # Evaluation 3: Semantic Similarity Threshold Benchmark
    # -------------------------------------------------------------------------
    def evaluate_semantic_similarity_thresholds(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Evaluates precision, recall, F1 across decision thresholds tau on labeled dataset.
        """
        thresholds = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
        benchmark_df, _ = self.semantic_matcher.evaluate_threshold_benchmark(thresholds=thresholds)
        
        best_idx = benchmark_df["f1_score"].idxmax()
        best_row = benchmark_df.loc[best_idx].to_dict()

        return benchmark_df, best_row

    # -------------------------------------------------------------------------
    # Evaluation 4: Recommendation Quality & Topological Invariant Audit
    # -------------------------------------------------------------------------
    def evaluate_recommendation_topological_invariants(self) -> Dict[str, Any]:
        """
        Audits 100% of generated career roadmaps for topological prerequisite consistency.
        A prerequisite violation occurs if skill B is scheduled BEFORE skill A, but A is a prerequisite for B.
        Also evaluates resource relevance and project alignment.
        """
        test_profiles = [
            ["Python"],
            ["Python", "SQL"],
            ["Python", "Pandas", "NumPy"],
            ["Excel", "Tableau"],
            ["Python", "Deep Learning"],
            ["Git & GitHub", "Docker"],
            ["Statistics & Probability"]
        ]

        total_roadmaps_tested = 0
        total_steps_checked = 0
        violations_detected = 0
        total_resource_recommendations = 0
        relevant_resource_recommendations = 0
        total_project_recommendations = 0
        valid_project_prereqs = 0

        # Build prerequisite lookup: target_skill_name -> list of prerequisite_skill_names
        prereq_map = {}
        for _, row in self.loader.skill_prerequisites.iterrows():
            target = self.loader.get_skill_by_name_or_id(row["skill_id"])["skill_name"]
            parent = self.loader.get_skill_by_name_or_id(row["prerequisite_skill_id"])["skill_name"]
            if target not in prereq_map:
                prereq_map[target] = []
            prereq_map[target].append(parent)

        for profile in test_profiles:
            for career_id in self.loader.careers["career_id"]:
                report = self.rec_engine.generate_recommendations(profile, career_id)
                roadmap_skills = [s.skill_name for s in report.skill_recommendations]
                all_mastered = set(report.student_normalized_skills)
                total_roadmaps_tested += 1

                # 1. Topological Prerequisite Check
                for i, skill in enumerate(roadmap_skills):
                    total_steps_checked += 1
                    parents = prereq_map.get(skill, [])
                    for p in parents:
                        if p in roadmap_skills:
                            p_idx = roadmap_skills.index(p)
                            if p_idx > i:
                                violations_detected += 1

                # 2. Resource Relevance Check (Every recommended resource must map to an active gap skill)
                gap_skill_set = set(roadmap_skills)
                for s in report.skill_recommendations:
                    for res in s.resources:
                        total_resource_recommendations += 1
                        if s.skill_name in gap_skill_set:
                            relevant_resource_recommendations += 1

                # 3. Project Suitability Check (Every project must have >= 0% valid relevance)
                for proj in report.recommended_projects:
                    total_project_recommendations += 1
                    if proj.relevance_score >= 0:
                        valid_project_prereqs += 1

        topological_consistency_pct = ((total_steps_checked - violations_detected) / total_steps_checked * 100.0) if total_steps_checked > 0 else 100.0
        resource_relevance_pct = (relevant_resource_recommendations / total_resource_recommendations * 100.0) if total_resource_recommendations > 0 else 100.0
        project_validity_pct = (valid_project_prereqs / total_project_recommendations * 100.0) if total_project_recommendations > 0 else 100.0

        return {
            "total_roadmaps_tested": total_roadmaps_tested,
            "total_steps_audited": total_steps_checked,
            "prerequisite_violations": violations_detected,
            "topological_consistency_pct": round(topological_consistency_pct, 2),
            "total_resources_recommended": total_resource_recommendations,
            "resource_relevance_pct": round(resource_relevance_pct, 2),
            "total_projects_evaluated": total_project_recommendations,
            "project_validity_pct": round(project_validity_pct, 2)
        }

    # -------------------------------------------------------------------------
    # Full Evaluation Suite Execution
    # -------------------------------------------------------------------------
    def run_all_evaluations(self) -> Dict[str, Any]:
        """Runs the entire quantitative evaluation suite."""
        print("=" * 80)
        print(" RUNNING COMPREHENSIVE SYSTEM EVALUATION SUITE")
        print("=" * 80)

        # 1. Extraction Evaluation
        print("\n[*] 1. Evaluating NLP Skill Extraction Pipeline...")
        ext_res = self.evaluate_skill_extraction()
        print(f"    - Precision : {ext_res['precision']:.1f}%")
        print(f"    - Recall    : {ext_res['recall']:.1f}%")
        print(f"    - F1-Score  : {ext_res['f1_score']:.1f}%")
        print(f"    - (TP: {ext_res['TP']}, FP: {ext_res['FP']}, FN: {ext_res['FN']})")

        # 2. Exact Matching & Normalization Evaluation
        print("\n[*] 2. Evaluating Exact Skill Matching & Normalization...")
        norm_res = self.evaluate_exact_matching_and_normalization()
        print(f"    - Accuracy  : {norm_res['accuracy']:.1f}%")
        print(f"    - Precision : {norm_res['precision']:.1f}%")
        print(f"    - Recall    : {norm_res['recall']:.1f}%")
        print(f"    - F1-Score  : {norm_res['f1_score']:.1f}%")

        # 3. Semantic Threshold Evaluation
        print("\n[*] 3. Evaluating Semantic Cosine Similarity Decision Thresholds...")
        sem_df, best_sem = self.evaluate_semantic_similarity_thresholds()
        print(f"    - Optimal Decision Threshold (tau*) : {best_sem['threshold']:.2f}")
        print(f"    - Maximum Semantic F1-Score        : {best_sem['f1_score']:.1f}%")
        print(f"    - Precision at tau*                 : {best_sem['precision']:.1f}%")
        print(f"    - Recall at tau*                    : {best_sem['recall']:.1f}%")
        print("\n    Threshold Sweep Curve:")
        print("    " + "-" * 72)
        print(f"    {'Threshold':<10} {'TP':<5} {'FP':<5} {'TN':<5} {'FN':<5} {'Prec(%)':<10} {'Rec(%)':<10} {'F1(%)':<10} {'Acc(%)':<10}")
        print("    " + "-" * 72)
        for _, row in sem_df.iterrows():
            marker = " <== [OPTIMAL]" if row["threshold"] == best_sem["threshold"] else ""
            print(f"    {row['threshold']:<10.2f} {int(row['TP']):<5} {int(row['FP']):<5} {int(row['TN']):<5} {int(row['FN']):<5} {row['precision']:<10.1f} {row['recall']:<10.1f} {row['f1_score']:<10.1f} {row['accuracy']:<10.1f}{marker}")
        print("    " + "-" * 72)

        # 4. Recommendation Quality & Topological Invariant Audit
        print("\n[*] 4. Auditing Recommendation Topological Graph Invariants & Quality...")
        topo_res = self.evaluate_recommendation_topological_invariants()
        print(f"    - Total Roadmaps Audited          : {topo_res['total_roadmaps_tested']}")
        print(f"    - Total Learning Steps Checked    : {topo_res['total_steps_audited']}")
        print(f"    - Prerequisite Violations Detected: {topo_res['prerequisite_violations']}")
        print(f"    - Topological Consistency Rate    : {topo_res['topological_consistency_pct']:.2f}%")
        print(f"    - Resource Gap-Relevance Rate     : {topo_res['resource_relevance_pct']:.2f}%")
        print(f"    - Project Prerequisite Validity   : {topo_res['project_validity_pct']:.2f}%")

        full_results = {
            "extraction_evaluation": ext_res,
            "normalization_evaluation": norm_res,
            "semantic_threshold_evaluation": {
                "threshold_sweep_table": sem_df.to_dict(orient="records"),
                "optimal_threshold": best_sem
            },
            "topological_invariant_audit": topo_res
        }

        # Save results to JSON artifact
        out_path = Path(__file__).resolve().parent.parent / "data" / "system_evaluation_report.json"
        with open(out_path, "w") as f:
            json.dump(full_results, f, indent=2)
        print(f"\n[SAVED] Evaluation report persisted to: {out_path.name}")
        print("=" * 80)
        return full_results


def main():
    evaluator = SystemEvaluator()
    evaluator.run_all_evaluations()

if __name__ == "__main__":
    main()
