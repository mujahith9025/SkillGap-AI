"""
AI Mock Interview Simulator Module
Interactive Skill-Gap Targeted Technical Interview Simulator

Provides structured interview questions, automated concept-coverage evaluation,
semantic answer scoring, actionable feedback, and optional live LLM integration.
"""

from dataclasses import dataclass, field
import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from data_loader import DataLoader
from semantic_matcher import SemanticSkillMatcher


@dataclass
class InterviewQuestion:
    """Represents a targeted technical interview question for a skill gap."""
    question_id: str
    skill_name: str
    difficulty: str
    question_type: str  # 'Conceptual', 'Scenario/Practical', 'System Design'
    question_text: str
    key_concepts: List[str]
    sample_model_answer: str
    follow_up_hint: str


@dataclass
class AnswerEvaluation:
    """Encapsulates the qualitative & quantitative assessment of a candidate's answer."""
    question_id: str
    skill_name: str
    candidate_answer: str
    overall_score: int  # 1 to 10
    score_tier: str     # 'Excellent', 'Good', 'Needs Improvement', 'Insufficient'
    concept_coverage_pct: float
    matched_concepts: List[str]
    missing_concepts: List[str]
    feedback_strengths: str
    feedback_improvements: str
    ideal_model_answer: str


class MockInterviewEngine:
    """
    Manages technical interview simulations targeting specific student skill gaps.
    """

    # Comprehensive question knowledge base covering technical domain skills
    QUESTION_BANK: Dict[str, List[Dict[str, Any]]] = {
        "Python": [
            {
                "difficulty": "Intermediate",
                "type": "Conceptual",
                "text": "Can you explain the difference between deep copy and shallow copy in Python? When would you use each?",
                "key_concepts": ["reference", "nested objects", "copy module", "memory address", "mutability"],
                "model_answer": "A shallow copy constructs a new compound object and inserts references to the original child objects into it. If a child object is mutable and modified, the change reflects in both. A deep copy recursively duplicates all nested objects, creating an independent clone in memory. You use deep copy when you need to safely alter nested data without affecting the original structure.",
                "hint": "Think about how nested lists or dictionaries behave when passed by reference."
            },
            {
                "difficulty": "Intermediate",
                "type": "Scenario/Practical",
                "text": "How do Python generators work, and why are they preferred over lists when processing large datasets?",
                "key_concepts": ["yield", "lazy evaluation", "memory efficiency", "iterator protocol", "stream processing"],
                "model_answer": "Generators use the 'yield' keyword to produce values on-the-fly one at a time, adhering to the iterator protocol. Unlike lists which allocate the entire collection in RAM upfront, generators compute elements lazily, maintaining minimal memory overhead during large-scale data ingestion or file streaming.",
                "hint": "Focus on memory allocation differences between yield and return."
            }
        ],
        "SQL": [
            {
                "difficulty": "Intermediate",
                "type": "Scenario/Practical",
                "text": "What is the difference between WHERE and HAVING clauses in SQL? Provide an example scenario.",
                "key_concepts": ["aggregation", "group by", "row-level filter", "aggregate functions", "execution order"],
                "model_answer": "WHERE filters individual rows BEFORE any aggregation or GROUP BY operations take place and cannot contain aggregate functions like SUM() or COUNT(). HAVING filters grouped records AFTER aggregation has been performed. For instance, WHERE filters active employees, while HAVING COUNT(order_id) > 5 filters customers with more than 5 orders.",
                "hint": "Consider the SQL query execution pipeline order."
            },
            {
                "difficulty": "Advanced",
                "type": "Conceptual",
                "text": "Explain Window Functions in SQL (e.g. ROW_NUMBER, RANK, DENSE_RANK) and how they differ from GROUP BY.",
                "key_concepts": ["over clause", "partition by", "order by", "preserves row count", "ranking"],
                "model_answer": "Window functions perform calculations across a set of table rows related to the current row using the OVER() clause with optional PARTITION BY and ORDER BY. Unlike GROUP BY which collapses multiple rows into a single summary row, window functions preserve the original row granularity while appending aggregated/ranking metrics.",
                "hint": "Highlight whether the number of output rows equals the input rows."
            }
        ],
        "Machine Learning": [
            {
                "difficulty": "Intermediate",
                "type": "Conceptual",
                "text": "Explain the Bias-Variance Tradeoff. What techniques would you use if your model has high variance?",
                "key_concepts": ["overfitting", "underfitting", "regularization", "cross-validation", "model complexity", "pruning"],
                "model_answer": "Bias is the error from overly simplistic assumptions (leading to underfitting), while Variance is the error from excessive sensitivity to small fluctuations in training data (leading to overfitting). High variance means the model fails to generalize. To mitigate high variance: apply L1/L2 regularization, gather more training data, use cross-validation, apply feature selection, or use ensemble bagging like Random Forests.",
                "hint": "Relate high variance to overfitting and discuss regularization strategies."
            },
            {
                "difficulty": "Intermediate",
                "type": "Scenario/Practical",
                "text": "Why is accuracy often a misleading metric for imbalanced classification, and what alternatives should you use?",
                "key_concepts": ["imbalanced classes", "precision", "recall", "f1-score", "roc-auc", "confusion matrix"],
                "model_answer": "In imbalanced datasets (e.g. 99% non-fraud, 1% fraud), a trivial model predicting only the majority class achieves 99% accuracy while failing completely at detecting the target event. Better evaluation metrics include Precision, Recall, F1-Score (the harmonic mean of precision and recall), PR-AUC, and ROC-AUC.",
                "hint": "Consider a disease detection or fraud detection scenario with 99:1 class ratio."
            }
        ],
        "Deep Learning": [
            {
                "difficulty": "Advanced",
                "type": "Conceptual",
                "text": "What causes the Vanishing and Exploding Gradient problems in deep neural networks, and how do we resolve them?",
                "key_concepts": ["backpropagation", "chain rule", "relu", "batch normalization", "residual connections", "gradient clipping"],
                "model_answer": "During backpropagation, gradients are computed via the chain rule through successive layers. When using saturating activation functions like Sigmoid or Tanh, derivative values (< 0.25) multiply exponentially, shrinking gradients toward zero (vanishing) and halting learning in early layers. Solutions include: using ReLU/LeakyReLU activations, Batch Normalization, He/Xavier weight initialization, Residual Skip Connections (ResNets), and Gradient Clipping.",
                "hint": "Discuss activation function derivatives and structural innovations like ResNets."
            }
        ],
        "Statistics & Probability": [
            {
                "difficulty": "Intermediate",
                "type": "Conceptual",
                "text": "What is the Central Limit Theorem (CLT), and why is it foundational in statistical inference and A/B testing?",
                "key_concepts": ["sample mean", "normal distribution", "sample size n >= 30", "standard error", "hypothesis testing"],
                "model_answer": "The Central Limit Theorem states that as sample size n increases (typically n >= 30), the sampling distribution of the sample mean approaches a normal Gaussian distribution, regardless of the underlying population's original distribution shape. This allows practitioners to construct confidence intervals, calculate z-scores, and conduct hypothesis tests in A/B testing.",
                "hint": "State the condition on sample size and the distribution of the sample mean."
            }
        ],
        "Docker": [
            {
                "difficulty": "Intermediate",
                "type": "Conceptual",
                "text": "What is the fundamental architectural difference between a Docker container and a Virtual Machine (VM)?",
                "key_concepts": ["hypervisor", "guest os", "shared kernel", "lightweight", "isolation", "namespaces/cgroups"],
                "model_answer": "Virtual Machines run on top of a Hypervisor, where each VM packages a complete, heavy guest operating system with virtualized hardware. Docker containers share the host machine's Linux kernel and isolate processes using OS-level cgroups and namespaces. Containers are vastly more lightweight, boot in seconds, and require significantly less CPU/RAM overhead.",
                "hint": "Compare guest OS overhead and kernel sharing."
            }
        ],
        "FastAPI": [
            {
                "difficulty": "Intermediate",
                "type": "Scenario/Practical",
                "text": "How does FastAPI achieve high performance, and how does it utilize Pydantic for request validation?",
                "key_concepts": ["async/await", "uvicorn/starlette", "type hints", "pydantic basemodel", "automatic openapi/swagger docs"],
                "model_answer": "FastAPI is built on Starlette and Uvicorn, leveraging Python's async/await syntax for non-blocking asynchronous I/O operations comparable to NodeJS or Go. It integrates Pydantic models for automatic schema declaration, request data parsing, payload validation, and serializing outputs while automatically generating interactive Swagger/OpenAPI documentation.",
                "hint": "Mention asynchronous event loops and Python type hinting."
            }
        ],
        "Pandas": [
            {
                "difficulty": "Beginner",
                "type": "Scenario/Practical",
                "text": "What is the difference between loc and iloc in Pandas DataFrame indexing?",
                "key_concepts": ["label-based", "integer position", "slicing boundary inclusive vs exclusive", "indexing"],
                "model_answer": "'loc' is label-based indexing, where rows and columns are selected by index names or column labels, and the slice end is inclusive. 'iloc' is integer position-based indexing (0 to n-1), where positions are passed as numbers, and slice boundaries follow standard Python exclusive end behavior.",
                "hint": "Compare index label vs 0-indexed integer position."
            }
        ],
        "Feature Engineering": [
            {
                "difficulty": "Intermediate",
                "type": "Scenario/Practical",
                "text": "When would you choose One-Hot Encoding versus Target (Mean) Encoding for high-cardinality categorical variables?",
                "key_concepts": ["curse of dimensionality", "cardinality", "target leakage", "regularization/smoothing", "sparse matrix"],
                "model_answer": "One-Hot Encoding works well for low-to-medium cardinality variables (e.g. < 15 unique categories). For high-cardinality features (like 1,000 ZIP codes), One-Hot creates massive, sparse matrices leading to the curse of dimensionality. Target Encoding replaces categories with the mean target value, keeping feature dimension at 1, but requires k-fold out-of-fold estimation or smoothing to prevent target leakage and overfitting.",
                "hint": "Discuss dimensional explosion with thousands of unique categories."
            }
        ],
        "Git & GitHub": [
            {
                "difficulty": "Beginner",
                "type": "Conceptual",
                "text": "Explain the difference between git merge and git rebase. When should you avoid rebasing?",
                "key_concepts": ["commit history", "fast-forward", "linear history", "public/shared branches", "rewriting history"],
                "model_answer": "'git merge' creates a new merge commit combining history from two branches, preserving the exact non-linear timeline and branch context. 'git rebase' rewrites commit history by replaying feature commits on top of the target branch tip, creating a clean, linear history. You should NEVER rebase public/shared branches because it rewrites commit SHAs, breaking synchronization for teammates.",
                "hint": "Remember the golden rule of rebasing shared public branches."
            }
        ]
    }

    def __init__(self, data_loader: Optional[DataLoader] = None, semantic_matcher: Optional[SemanticSkillMatcher] = None):
        self.loader = data_loader if data_loader else DataLoader()
        self.semantic_matcher = semantic_matcher if semantic_matcher else SemanticSkillMatcher(data_loader=self.loader)

    def get_questions_for_skill(self, skill_name: str) -> List[InterviewQuestion]:
        """Retrieves technical interview questions for a specific skill."""
        raw_list = self.QUESTION_BANK.get(skill_name, [])
        if not raw_list:
            # Fallback generic technical problem solving question
            return [
                InterviewQuestion(
                    question_id=f"{skill_name.lower().replace(' ', '_')}_01",
                    skill_name=skill_name,
                    difficulty="Intermediate",
                    question_type="Conceptual & Applied",
                    question_text=f"How do you utilize {skill_name} in industry projects? What are its primary advantages and common pitfalls?",
                    key_concepts=["architecture", "best practices", "performance optimization", "real-world use case"],
                    sample_model_answer=f"{skill_name} is used to solve specialized technical problems in modern workflows. Key best practices include understanding core architectural abstractions, ensuring robust error handling, and optimizing performance bottlenecks.",
                    follow_up_hint="Structure your answer using: 1. Core Purpose, 2. Practical Workflow, 3. Key Challenge & Solution."
                )
            ]

        results = []
        for idx, item in enumerate(raw_list, 1):
            results.append(InterviewQuestion(
                question_id=f"{skill_name.lower().replace(' ', '_')}_{idx:02d}",
                skill_name=skill_name,
                difficulty=item["difficulty"],
                question_type=item["type"],
                question_text=item["text"],
                key_concepts=item["key_concepts"],
                sample_model_answer=item["model_answer"],
                follow_up_hint=item["hint"]
            ))
        return results

    def evaluate_candidate_answer(
        self,
        question: InterviewQuestion,
        candidate_answer: str
    ) -> AnswerEvaluation:
        """
        Evaluates a candidate's answer based on keyword presence, concept coverage,
        and semantic similarity against the benchmark model answer.
        """
        cleaned_ans = candidate_answer.strip().lower()
        if not cleaned_ans or len(cleaned_ans.split()) < 4:
            return AnswerEvaluation(
                question_id=question.question_id,
                skill_name=question.skill_name,
                candidate_answer=candidate_answer,
                overall_score=1,
                score_tier="Insufficient",
                concept_coverage_pct=0.0,
                matched_concepts=[],
                missing_concepts=question.key_concepts,
                feedback_strengths="Answer provided is too short or empty.",
                feedback_improvements="Provide a complete explanation detailing the underlying mechanisms and real-world trade-offs.",
                ideal_model_answer=question.sample_model_answer
            )

        # 1. Concept Keyword Coverage Analysis
        matched_concepts = []
        missing_concepts = []

        for concept in question.key_concepts:
            # Check direct or partial substring match in lowercased answer
            terms = [t.strip().lower() for t in re.split(r"[/, ]+", concept) if len(t) > 2]
            if any(term in cleaned_ans for term in terms):
                matched_concepts.append(concept)
            else:
                missing_concepts.append(concept)

        coverage_ratio = len(matched_concepts) / len(question.key_concepts) if question.key_concepts else 1.0

        # 2. Semantic Embedding Similarity against Model Answer
        sim_score = self.semantic_matcher.compute_cosine_similarity(candidate_answer, question.sample_model_answer)
        
        # 3. Composite Score Calculation (1 to 10 scale)
        # Score = (Concept_Coverage * 6.0) + (Semantic_Similarity * 3.0) + (Length_Bonus * 1.0)
        word_count = len(candidate_answer.split())
        length_bonus = 1.0 if word_count >= 25 else (word_count / 25.0)
        
        raw_score = (coverage_ratio * 6.0) + (max(0.0, sim_score) * 3.0) + (length_bonus * 1.0)
        final_score = int(np.clip(round(raw_score), 1, 10))

        # Determine Tier
        if final_score >= 8:
            tier = "Excellent"
            strengths = "Comprehensive answer! You demonstrated strong technical precision, covered key architectural concepts, and articulated the trade-offs clearly."
            improvements = "To make it a senior-level answer, provide a concrete real-world production edge-case example."
        elif final_score >= 6:
            tier = "Good"
            strengths = f"Solid foundational grasp. You correctly highlighted: {', '.join(matched_concepts[:3])}."
            improvements = f"To score higher, address missing core principles: {', '.join(missing_concepts[:2])}."
        elif final_score >= 4:
            tier = "Needs Improvement"
            strengths = "You understand the high-level intent of the question."
            improvements = f"The answer lacks technical depth. Be sure to explain: {', '.join(missing_concepts[:3])}."
        else:
            tier = "Insufficient"
            strengths = "Attempted answer."
            improvements = f"Review the fundamental concepts of {question.skill_name}. Expected coverage: {', '.join(question.key_concepts)}."

        return AnswerEvaluation(
            question_id=question.question_id,
            skill_name=question.skill_name,
            candidate_answer=candidate_answer,
            overall_score=final_score,
            score_tier=tier,
            concept_coverage_pct=round(coverage_ratio * 100.0, 1),
            matched_concepts=matched_concepts,
            missing_concepts=missing_concepts,
            feedback_strengths=strengths,
            feedback_improvements=improvements,
            ideal_model_answer=question.sample_model_answer
        )
