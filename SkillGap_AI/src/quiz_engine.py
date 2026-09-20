"""
Gamified Micro-Milestone Quiz Engine Module
Phase 10 / Section 2 Upgrades: Interactive Competency Quiz Gates

Generates 3-question adaptive technical quiz checkpoints for technical skills
and evaluates student mastery before unlocking downstream roadmap milestones.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
import random

from data_loader import DataLoader


@dataclass
class QuizQuestion:
    """Represents a multiple-choice technical question for skill validation."""
    question_id: str
    skill_name: str
    question_text: str
    options: List[str]
    correct_option_index: int
    difficulty: str
    explanation: str

    def to_dict(self, include_answer: bool = False) -> Dict[str, Any]:
        data = {
            "question_id": self.question_id,
            "skill_name": self.skill_name,
            "question_text": self.question_text,
            "options": self.options,
            "difficulty": self.difficulty,
        }
        if include_answer:
            data["correct_option_index"] = self.correct_option_index
            data["explanation"] = self.explanation
        return data


@dataclass
class QuizResult:
    """Encapsulates the evaluation outcome of a 3-question quiz gate."""
    skill_name: str
    score: int
    total_questions: int
    percentage: float
    passed: bool
    feedback: str
    question_evaluations: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "score": self.score,
            "total_questions": self.total_questions,
            "percentage": round(self.percentage, 1),
            "passed": self.passed,
            "feedback": self.feedback,
            "question_evaluations": self.question_evaluations
        }


# Comprehensive curated technical question bank across key domains
TECHNICAL_QUESTION_BANK: Dict[str, List[Dict[str, Any]]] = {
    "python": [
        {
            "question": "What is the time complexity of looking up a key in a standard Python dictionary on average?",
            "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "Python dictionaries are implemented using hash tables, offering O(1) average time complexity for key lookups and insertions."
        },
        {
            "question": "Which of the following creates a generator in Python rather than an in-memory list?",
            "options": ["[x**2 for x in range(10)]", "(x**2 for x in range(10))", "{x**2 for x in range(10)}", "tuple(x**2 for x in range(10))"],
            "correct": 1,
            "difficulty": "Intermediate",
            "explanation": "Parentheses surrounding a comprehension expression create a generator expression that yields items lazily on demand without allocating full memory."
        },
        {
            "question": "What does the Python GIL (Global Interpreter Lock) primarily prevent?",
            "options": [
                "Running multiple processes simultaneously",
                "Multiple native threads executing Python bytecode concurrently in a single process",
                "Memory allocation above 4GB",
                "Recursive function execution"
            ],
            "correct": 1,
            "difficulty": "Advanced",
            "explanation": "The GIL is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes at once in CPython."
        },
        {
            "question": "What is the key difference between `is` and `==` in Python?",
            "options": [
                "`==` checks memory address identity, `is` checks equality of values",
                "`is` checks memory address identity (object identity), `==` checks equality of values",
                "Both are completely identical in all versions of Python",
                "`is` is used only for numeric types"
            ],
            "correct": 1,
            "difficulty": "Beginner",
            "explanation": "`is` verifies whether two variables reference the exact same memory address (`id(a) == id(b)`), while `==` evaluates the `__eq__` value equality."
        }
    ],
    "sql": [
        {
            "question": "What is the fundamental difference between the `WHERE` and `HAVING` clauses in SQL?",
            "options": [
                "`WHERE` filters rows before aggregation, `HAVING` filters grouped data after `GROUP BY`",
                "`HAVING` filters rows before aggregation, `WHERE` filters after `GROUP BY`",
                "`WHERE` is only used with `JOIN` clauses, `HAVING` is used with `SELECT`",
                "There is no difference; they are interchangeable aliases"
            ],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "`WHERE` filters individual records before any grouping occurs. `HAVING` filters aggregated summary rows after the `GROUP BY` clause evaluates."
        },
        {
            "question": "Which SQL Window function produces consecutive rankings without skipping numbers in the event of ties?",
            "options": ["RANK()", "DENSE_RANK()", "ROW_NUMBER()", "NTILE()"],
            "correct": 1,
            "difficulty": "Intermediate",
            "explanation": "`DENSE_RANK()` assigns identical ranks to tied values and continues with the immediate next integer (e.g. 1, 2, 2, 3), whereas `RANK()` leaves gaps (1, 2, 2, 4)."
        },
        {
            "question": "What type of index is most effective for speeding up range queries (`BETWEEN`, `>`, `<`) in relational databases?",
            "options": ["Hash Index", "B-Tree Index", "Bitmap Index", "Full-Text Index"],
            "correct": 1,
            "difficulty": "Advanced",
            "explanation": "B-Tree indices maintain sorted key structures, making them optimal for logarithmic range searches, ordered traversals, and equality checks."
        }
    ],
    "machine learning": [
        {
            "question": "What does a high variance / low bias model typically indicate in supervised learning?",
            "options": [
                "Underfitting the training dataset",
                "Overfitting the training dataset (poor generalizability on unseen data)",
                "Optimal convergence and perfect generalization",
                "Excessive regularization penalty"
            ],
            "correct": 1,
            "difficulty": "Beginner",
            "explanation": "High variance means the model captures noise and sample fluctuations from the training data, leading to overfitting and high test error."
        },
        {
            "question": "Why is ROC-AUC often preferred over standard Accuracy for imbalanced classification tasks (e.g. 99% Negative, 1% Positive)?",
            "options": [
                "Accuracy is sensitive to class skew, whereas ROC-AUC evaluates true positive vs false positive trade-offs across all classification thresholds",
                "ROC-AUC only works on regression models",
                "Accuracy requires continuous probability scores",
                "ROC-AUC computes training loss directly"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "In skewed datasets, a naive model predicting only the majority class achieves 99% accuracy but zero predictive power. ROC-AUC evaluates discriminatory ability across all thresholds."
        },
        {
            "question": "What is the primary difference between L1 (Lasso) and L2 (Ridge) regularization?",
            "options": [
                "L1 penalizes absolute coefficient values encouraging sparsity (feature selection), while L2 penalizes squared weights shrinking them smoothly",
                "L2 sets coefficients strictly to zero, while L1 preserves small weights",
                "L1 is only applicable to neural networks, L2 to linear regression",
                "L2 is sensitive to learning rates, L1 is not"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "L1 norm ($||w||_1$) produces diamond-shaped constraint boundaries that zero out uninformative feature weights, performing built-in feature selection."
        }
    ],
    "deep learning": [
        {
            "question": "What vanishing gradient problem mitigation technique is most widely used in modern deep feedforward architectures?",
            "options": [
                "Sigmoid Activation Functions",
                "ReLU (Rectified Linear Unit) & Residual Skip Connections (ResNets)",
                "Increasing the learning rate to 10.0",
                "Removing backpropagation entirely"
            ],
            "correct": 1,
            "difficulty": "Intermediate",
            "explanation": "ReLU preserves non-saturating positive derivatives (gradient = 1 for $x > 0$), and ResNet skip connections allow gradients to flow directly across layers."
        },
        {
            "question": "What is the primary computational mechanism behind the Self-Attention mechanism in Transformer architectures?",
            "options": [
                "Recurrent hidden state iteration across sequential tokens",
                "Scaled Dot-Product Attention: $Softmax(QK^T / \\sqrt{d_k}) V$",
                "Convolutional filter sliding windows",
                "K-Means clustering of token vectors"
            ],
            "correct": 1,
            "difficulty": "Advanced",
            "explanation": "Transformers calculate attention weights dynamically between all token pairs via Query-Key dot products scaled by dimension square root, multiplied by Value matrices."
        }
    ],
    "pandas": [
        {
            "question": "What is the most vector-optimized way to perform conditional column creation in Pandas without using a slow `.apply(lambda ...)`?",
            "options": [
                "`np.where(condition, value_if_true, value_if_false)` or `.loc[condition, col] = val`",
                "Iterating with a standard Python `for index, row in df.iterrows():`",
                "Converting the dataframe to a Python dictionary and back",
                "Calling `eval()` inside an external loop"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "NumPy vectorization (`np.where`) executes in compiled C-speed memory buffers, running 50-100x faster than row-by-row Python lambda iterations."
        },
        {
            "question": "What does `df.groupby('dept')['salary'].transform('mean')` return compared to `df.groupby('dept')['salary'].mean()`?",
            "options": [
                "A Series with the same index and length as the original DataFrame, broadcasting group means back to individual rows",
                "A aggregated summary table indexed only by unique department names",
                "A boolean mask of salaries above the median",
                "A sorted copy of the salary column"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "`.transform()` preserves the original DataFrame dimensions, broadcasting aggregated statistics back across each individual row index."
        }
    ],
    "fastapi": [
        {
            "question": "How does FastAPI achieve high concurrent I/O performance compared to traditional WSGI frameworks like Flask?",
            "options": [
                "It uses ASGI and Python's native `asyncio` event loop with Starlette and Pydantic validation",
                "It compiles Python directly to C++ binaries at startup",
                "It disables all HTTP header validation",
                "It forces all endpoints to run on separate physical CPU cores"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "FastAPI is built on Starlette (ASGI) and Pydantic, allowing non-blocking asynchronous event loop handling for thousands of concurrent requests."
        },
        {
            "question": "How do you automatically declare request body validation and OpenAPI schemas in FastAPI?",
            "options": [
                "By defining Python classes inheriting from `pydantic.BaseModel` as route function parameters",
                "By writing XML schema definitions manually",
                "By using regular expressions inside query strings",
                "By creating global dictionary objects"
            ],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "FastAPI leverages Pydantic models to perform automatic type coercion, request validation, error reporting (422), and OpenAPI Swagger generation."
        }
    ],
    "docker": [
        {
            "question": "What is the primary benefit of multi-stage Docker builds?",
            "options": [
                "Minimizing final production image sizes by leaving build tools and compilers behind in earlier stages",
                "Allowing containers to run on multiple physical operating systems at the exact same instant",
                "Enabling automatic container clustering without Kubernetes",
                "Encrypting the container file system with AES-256"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "Multi-stage builds allow developers to compile dependencies in intermediate builder containers and copy only final lean artifacts into runtime images."
        },
        {
            "question": "What is the difference between `CMD` and `ENTRYPOINT` in a Dockerfile?",
            "options": [
                "`ENTRYPOINT` sets the immutable base executable, while `CMD` provides default arguments that can be easily overridden at runtime",
                "`CMD` cannot be overridden when running `docker run`",
                "`ENTRYPOINT` is only executed during image build time",
                "Both commands are completely identical in modern Docker engines"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "`ENTRYPOINT` defines the core executable container process, while `CMD` supplies default parameters that CLI arguments can override."
        }
    ],
    "scikit-learn": [
        {
            "question": "Why must you use `pipeline.fit_transform(X_train)` and `pipeline.transform(X_test)` instead of fitting on both train and test?",
            "options": [
                "To prevent data leakage from the test dataset into training statistics (e.g. mean, variance, imputation values)",
                "Because `fit()` deletes the test dataset",
                "To reduce the number of features in the test set",
                "To automatically balance classification labels"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "Fitting transformations on test data introduces data snooping/leakage, yielding overly optimistic evaluation metrics that fail in production."
        }
    ],
    "data structures & algorithms": [
        {
            "question": "Which data structure is optimal for implementing Breadth-First Search (BFS) graph traversal?",
            "options": ["Queue (FIFO)", "Stack (LIFO)", "Binary Search Tree", "Max Heap"],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "BFS explores nodes level by level in First-In-First-Out order, making a Double-Ended Queue (`deque` / FIFO queue) the optimal data structure."
        },
        {
            "question": "What is the worst-case time complexity of QuickSort if the pivot is poorly chosen?",
            "options": ["O(n^2)", "O(n log n)", "O(n)", "O(log n)"],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "When an extreme element (smallest/largest) is consistently chosen as pivot in an already sorted array without randomization, recursion depth hits $O(n)$, yielding $O(n^2)$ total operations."
        }
    ]
}


class QuizEngine:
    """
    Manages generation, delivery, and evaluation of technical micro-quizzes
    for gamified milestone validation.
    """

    def __init__(self, data_loader: Optional[DataLoader] = None):
        self.loader = data_loader if data_loader else DataLoader()
        self.question_bank = TECHNICAL_QUESTION_BANK

    def get_quiz_for_skill(
        self,
        skill_name: str,
        num_questions: int = 3
    ) -> List[QuizQuestion]:
        """
        Retrieves or dynamically compiles a 3-question micro-quiz for a given skill.
        """
        canonical_key = skill_name.strip().lower()
        
        # Match closest skill key
        matched_key = None
        for key in self.question_bank:
            if key in canonical_key or canonical_key in key:
                matched_key = key
                break

        questions_pool = []
        if matched_key:
            questions_pool = self.question_bank[matched_key]
        else:
            # Fallback to general domain questions
            if "sql" in canonical_key or "database" in canonical_key:
                questions_pool = self.question_bank["sql"]
            elif "learn" in canonical_key or "model" in canonical_key or "ai" in canonical_key:
                questions_pool = self.question_bank["machine learning"]
            elif "docker" in canonical_key or "cloud" in canonical_key:
                questions_pool = self.question_bank["docker"]
            else:
                questions_pool = self.question_bank["python"]

        # Sample up to num_questions
        selected_raw = questions_pool[:num_questions]
        if len(selected_raw) < num_questions:
            # Pad with general DSA / Python
            pad_pool = self.question_bank["python"] + self.question_bank["data structures & algorithms"]
            for item in pad_pool:
                if item not in selected_raw:
                    selected_raw.append(item)
                if len(selected_raw) >= num_questions:
                    break

        quiz_questions = []
        for i, q in enumerate(selected_raw[:num_questions]):
            qid = f"QZ_{canonical_key.replace(' ', '_')}_{i+1}"
            quiz_questions.append(
                QuizQuestion(
                    question_id=qid,
                    skill_name=skill_name,
                    question_text=q["question"],
                    options=q["options"],
                    correct_option_index=q["correct"],
                    difficulty=q.get("difficulty", "Intermediate"),
                    explanation=q.get("explanation", "Core architectural and conceptual standard practice.")
                )
            )

        return quiz_questions

    def evaluate_quiz(
        self,
        skill_name: str,
        user_answers: List[int]
    ) -> QuizResult:
        """
        Evaluates submitted option indices against correct question answers.
        Passing threshold is >= 66% (e.g. at least 2 out of 3 correct).
        """
        questions = self.get_quiz_for_skill(skill_name, num_questions=len(user_answers) or 3)
        
        score = 0
        evaluations = []

        for idx, q in enumerate(questions):
            user_choice = user_answers[idx] if idx < len(user_answers) else -1
            is_correct = (user_choice == q.correct_option_index)
            if is_correct:
                score += 1

            evaluations.append({
                "question_id": q.question_id,
                "question_text": q.question_text,
                "options": q.options,
                "user_selected_index": user_choice,
                "correct_option_index": q.correct_option_index,
                "is_correct": is_correct,
                "difficulty": q.difficulty,
                "explanation": q.explanation
            })

        total = len(questions)
        pct = (score / max(1, total)) * 100.0
        passed = (pct >= 66.0)

        if passed:
            feedback = f"🎉 Mastery Verified! You scored {score}/{total} ({pct:.0f}%). Milestone unlocked and skill credential added to your profile!"
        else:
            feedback = f"⚠️ Quiz Not Passed ({score}/{total} - {pct:.0f}%). Review the recommended resources and try again to unlock downstream DAG prerequisites."

        return QuizResult(
            skill_name=skill_name,
            score=score,
            total_questions=total,
            percentage=pct,
            passed=passed,
            feedback=feedback,
            question_evaluations=evaluations
        )
