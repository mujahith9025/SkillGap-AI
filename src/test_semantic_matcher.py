"""
Test Runner & Threshold Evaluation Suite for Semantic Matching
Phase 11: Semantic Skill Matching using Sentence Transformers

Tests:
1. Pairwise semantic cosine similarity calculations
2. Retrieval of closest canonical skills for unmapped technical queries
3. Rigorous threshold benchmark evaluation (Precision, Recall, F1, Accuracy)
"""

import sys
from pathlib import Path
import pandas as pd

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from semantic_matcher import SemanticSkillMatcher

def main():
    print("=" * 80)
    print(" SEMANTIC AI MATCHING & THRESHOLD BENCHMARK SUITE")
    print("=" * 80)
    
    matcher = SemanticSkillMatcher(default_threshold=0.70)

    # -------------------------------------------------------------
    # 1. Pairwise Similarity Inspections
    # -------------------------------------------------------------
    print("\n--- 1. Pairwise Cosine Similarity Inspections ---")
    pair_tests = [
        ("Tableau", "Data Visualization", "Related Tool -> Field"),
        ("Power BI", "Data Visualization", "Related Tool -> Field"),
        ("PyTorch Lightning", "Deep Learning", "Framework -> Field"),
        ("Prompt Engineering", "Large Language Models (LLMs)", "Sub-skill -> Domain"),
        ("PostgreSQL", "SQL", "Dialect -> Standard"),
        ("Python", "Excel", "Unrelated Tool Pair"),
        ("SQL", "Deep Learning", "Unrelated Domain Pair"),
        ("Docker", "Statistics & Probability", "Unrelated Tool/Math Pair"),
    ]

    print(f"{'Query Term':<25} | {'Target Term':<32} | {'Cosine Sim':<12} | {'Description'}")
    print("-" * 95)
    for q, t, desc in pair_tests:
        sim = matcher.compute_cosine_similarity(q, t)
        print(f"{q:<25} | {t:<32} | {sim:>8.4f}     | {desc}")

    # -------------------------------------------------------------
    # 2. Canonical Nearest-Neighbor Search
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("--- 2. Nearest Canonical Neighbor Queries ---")
    unmapped_queries = [
        "Prompt Engineering",
        "Keras Neural Nets",
        "Postgres Database",
        "PySpark Big Data",
        "Hypothesis Testing",
        "Kubernetes Containers"
    ]

    for q in unmapped_queries:
        res = matcher.find_best_canonical_match(q, threshold=0.65)
        status = "[ACCEPTED]" if res.is_accepted else "[REJECTED]"
        print(f"Query: '{q:<25}' -> Best Match: '{res.matched_canonical:<30}' | Sim: {res.similarity_score:.4f} {status}")

    # -------------------------------------------------------------
    # 3. Labeled Validation Threshold Benchmark
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("--- 3. Labeled Benchmark Dataset Threshold Evaluation ---")
    print("=" * 80)
    
    benchmark_df, val_with_scores = matcher.evaluate_threshold_benchmark()
    
    print(f"{'Threshold (tau)':<16} | {'TP':<4} | {'FP':<4} | {'TN':<4} | {'FN':<4} | {'Precision (%)':<14} | {'Recall (%)':<12} | {'F1-Score (%)':<13} | {'Accuracy (%)'}")
    print("-" * 95)
    for _, row in benchmark_df.iterrows():
        print(f"tau = {row['threshold']:<10.2f} | {int(row['TP']):<4} | {int(row['FP']):<4} | {int(row['TN']):<4} | {int(row['FN']):<4} | {row['precision']:>10.1f}%   | {row['recall']:>8.1f}%   | {row['f1_score']:>9.1f}%   | {row['accuracy']:>9.1f}%")

    # Find optimal threshold based on max F1
    best_row = benchmark_df.loc[benchmark_df["f1_score"].idxmax()]
    print("\n" + "=" * 80)
    print(f"[*] OPTIMAL SIMILARITY THRESHOLD IDENTIFIED: tau* = {best_row['threshold']:.2f}")
    print(f"    - Maximum F1-Score : {best_row['f1_score']:.1f}%")
    print(f"    - Balanced Precision: {best_row['precision']:.1f}%")
    print(f"    - Balanced Recall   : {best_row['recall']:.1f}%")
    print(f"    - System Accuracy   : {best_row['accuracy']:.1f}%")
    print("=" * 80)

if __name__ == "__main__":
    main()
