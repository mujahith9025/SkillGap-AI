"""
Semantic AI Skill Matching Engine
Phase 11: Semantic Skill Matching using Sentence Transformers

Computes dense vector representations (embeddings) for technical skills
and evaluates semantic equivalence using cosine similarity and configurable
decision thresholds.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from data_loader import DataLoader
from preprocessing import SkillPreprocessor

MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_SIMILARITY_THRESHOLD = 0.70


@dataclass
class SemanticMatchResult:
    """Represents a semantic match between a candidate skill and canonical target."""
    query_skill: str
    matched_canonical: str
    similarity_score: float
    is_accepted: bool
    threshold_used: float
    confidence_tier: str  # 'High', 'Moderate', 'Weak'


class SemanticSkillMatcher:
    """
    Dense vector embedding matcher powered by Sentence Transformers.
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        default_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        data_loader: Optional[DataLoader] = None
    ):
        self.model_name = model_name
        self.default_threshold = default_threshold
        self.loader = data_loader if data_loader else DataLoader()
        
        print(f"[*] Initializing Sentence Transformer Model: '{self.model_name}'...")
        self.model = SentenceTransformer(self.model_name)
        
        # Extract and precompute rich contextual embeddings for all canonical taxonomy skills
        # Combining skill name with domain description provides strong semantic signal for Transformers
        self.canonical_names = self.loader.skills["skill_name"].tolist()
        self.canonical_descriptions = [
            f"{row['skill_name']} ({row['category']}): {row['description']}"
            for _, row in self.loader.skills.iterrows()
        ]
        
        print(f"[*] Precomputing contextual vector embeddings for {len(self.canonical_names)} canonical skills...")
        self.canonical_embeddings = self.model.encode(
            self.canonical_descriptions,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        print("  [SUCCESS] Canonical skill embeddings ready (Dimension: 384).")

    def encode_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generates normalized vector embeddings for given text(s)."""
        return self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

    def compute_cosine_similarity(self, text_a: str, text_b: str) -> float:
        """
        Computes pairwise cosine similarity between two skill strings:
        cos(u, v) = (u . v) / (||u|| * ||v||)
        """
        emb_a = self.encode_text(text_a).reshape(1, -1)
        emb_b = self.encode_text(text_b).reshape(1, -1)
        sim = float(cosine_similarity(emb_a, emb_b)[0][0])
        return sim

    def find_best_canonical_match(
        self,
        query_skill: str,
        threshold: Optional[float] = None
    ) -> SemanticMatchResult:
        """
        Finds the closest canonical skill in the taxonomy for an arbitrary query string.
        """
        thresh = threshold if threshold is not None else self.default_threshold
        query_emb = self.encode_text(query_skill).reshape(1, -1)
        
        # Compute cosine similarity vector against all canonical skills
        similarities = cosine_similarity(query_emb, self.canonical_embeddings)[0]
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])
        best_canonical = self.canonical_names[best_idx]
        
        is_accepted = (best_score >= thresh)
        
        if best_score >= 0.85:
            tier = "High"
        elif best_score >= 0.70:
            tier = "Moderate"
        else:
            tier = "Weak"

        return SemanticMatchResult(
            query_skill=query_skill,
            matched_canonical=best_canonical,
            similarity_score=best_score,
            is_accepted=is_accepted,
            threshold_used=thresh,
            confidence_tier=tier
        )

    def evaluate_threshold_benchmark(
        self,
        validation_csv_path: Optional[Path] = None,
        thresholds: Optional[List[float]] = None
    ) -> pd.DataFrame:
        """
        Evaluates precision, recall, F1-score, and accuracy across different
        similarity thresholds using a labeled benchmark dataset.
        """
        if validation_csv_path is None:
            validation_csv_path = Path(__file__).resolve().parent.parent / "data" / "semantic_validation.csv"

        val_df = pd.read_csv(validation_csv_path)
        if thresholds is None:
            thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]

        # Compute cosine similarities for all pairs in validation set
        similarities = []
        for _, row in val_df.iterrows():
            sim = self.compute_cosine_similarity(row["query_skill"], row["target_skill"])
            similarities.append(sim)
        
        val_df["similarity_score"] = similarities
        y_true = val_df["is_match"].values

        results = []
        for t in thresholds:
            y_pred = (val_df["similarity_score"] >= t).astype(int).values
            
            # Confusion matrix counts
            tp = int(np.sum((y_true == 1) & (y_pred == 1)))
            fp = int(np.sum((y_true == 0) & (y_pred == 1)))
            tn = int(np.sum((y_true == 0) & (y_pred == 0)))
            fn = int(np.sum((y_true == 1) & (y_pred == 0)))
            
            prec = precision_score(y_true, y_pred, zero_division=0)
            rec = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
            acc = accuracy_score(y_true, y_pred)

            results.append({
                "threshold": t,
                "TP": tp,
                "FP": fp,
                "TN": tn,
                "FN": fn,
                "precision": round(prec * 100, 1),
                "recall": round(rec * 100, 1),
                "f1_score": round(f1 * 100, 1),
                "accuracy": round(acc * 100, 1)
            })

        return pd.DataFrame(results), val_df
