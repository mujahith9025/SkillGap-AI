"""
Gamified Skill Assessment Quiz Engine Module
Provides pre-defined technical multiple-choice questions across all canonical skills,
evaluates student answers, and awards marks, percentages, grades, and detailed explanations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
import random

from data_loader import DataLoader


@dataclass
class QuizQuestion:
    """Represents a multiple-choice technical question for skill assessment."""
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
    """Encapsulates the evaluation outcome and marks of a skill assessment quiz."""
    skill_name: str
    score: int
    total_questions: int
    percentage: float
    passed: bool
    feedback: str
    question_evaluations: List[Dict[str, Any]]
    marks_obtained: int = 0
    total_marks: int = 0
    grade: str = "A"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "score": self.score,
            "total_questions": self.total_questions,
            "percentage": round(self.percentage, 1),
            "passed": self.passed,
            "feedback": self.feedback,
            "marks_obtained": self.score * 10,
            "total_marks": self.total_questions * 10,
            "grade": self.grade,
            "question_evaluations": self.question_evaluations
        }


# Comprehensive pre-defined technical question bank across all technical domains
TECHNICAL_QUESTION_BANK: Dict[str, List[Dict[str, Any]]] = {
    "python": [
        {
            "question": "What is the time complexity of looking up a key in a standard Python dictionary on average?",
            "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "Python dictionaries use hash tables, offering O(1) average time complexity for key lookups and insertions."
        },
        {
            "question": "Which of the following creates a generator expression in Python rather than an in-memory list?",
            "options": ["[x**2 for x in range(10)]", "(x**2 for x in range(10))", "{x**2 for x in range(10)}", "tuple(x**2 for x in range(10))"],
            "correct": 1,
            "difficulty": "Intermediate",
            "explanation": "Parentheses around a comprehension expression yield items lazily on demand without allocating full memory."
        },
        {
            "question": "What does the Python GIL (Global Interpreter Lock) primarily restrict?",
            "options": [
                "Running multiple processes simultaneously",
                "Multiple native threads executing Python bytecode concurrently in a single process",
                "Allocating more than 4GB of RAM",
                "Recursive function execution"
            ],
            "correct": 1,
            "difficulty": "Advanced",
            "explanation": "The GIL is a mutex that prevents multiple native threads from executing Python bytecodes concurrently in CPython."
        },
        {
            "question": "What is the key difference between `is` and `==` in Python?",
            "options": [
                "`==` checks memory address, `is` checks equality of values",
                "`is` checks memory address identity, `==` checks value equality",
                "Both are completely identical",
                "`is` is only used for integers"
            ],
            "correct": 1,
            "difficulty": "Beginner",
            "explanation": "`is` checks object identity (id(a) == id(b)), whereas `==` checks value equality."
        },
        {
            "question": "What happens when you pass a mutable object (like a list) as a default argument in a Python function definition?",
            "options": [
                "A fresh empty list is created every time the function is called",
                "The default list is instantiated once at function definition and shared across subsequent calls",
                "Python raises a SyntaxError at compile time",
                "The list becomes immutable automatically"
            ],
            "correct": 1,
            "difficulty": "Intermediate",
            "explanation": "Default argument expressions are evaluated once when the function definition is executed, leading to shared state across calls."
        }
    ],

    "sql": [
        {
            "question": "What is the fundamental difference between the `WHERE` and `HAVING` clauses in SQL?",
            "options": [
                "`WHERE` filters rows before aggregation; `HAVING` filters grouped summary rows after `GROUP BY`",
                "`HAVING` filters rows before aggregation; `WHERE` filters after `GROUP BY`",
                "`WHERE` is only for JOINs; `HAVING` is for subqueries",
                "They are interchangeable aliases"
            ],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "`WHERE` filters individual records before aggregation, while `HAVING` filters aggregate metric groups after `GROUP BY`."
        },
        {
            "question": "Which SQL Window function produces consecutive rankings without skipping rank numbers in the event of ties?",
            "options": ["RANK()", "DENSE_RANK()", "ROW_NUMBER()", "NTILE()"],
            "correct": 1,
            "difficulty": "Intermediate",
            "explanation": "`DENSE_RANK()` gives tied items identical ranks and increments by 1 for the next item (e.g. 1, 2, 2, 3), whereas `RANK()` leaves gaps (1, 2, 2, 4)."
        },
        {
            "question": "What index structure is most effective for speeding up range queries (`BETWEEN`, `>`, `<`) in relational databases?",
            "options": ["Hash Index", "B-Tree Index", "Bitmap Index", "Full-Text Index"],
            "correct": 1,
            "difficulty": "Advanced",
            "explanation": "B-Tree indices maintain sorted keys, making them optimal for logarithmic range traversals and ordered range searches."
        },
        {
            "question": "What does an `INNER JOIN` return when comparing two tables on a foreign key?",
            "options": [
                "Only rows that have matching values in both tables",
                "All rows from the left table and matched rows from the right table",
                "The cartesian product of both tables",
                "Only rows that do NOT match in either table"
            ],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "An INNER JOIN selects records that have matching values in both datasets."
        },
        {
            "question": "What are the ACID properties in relational database transaction management?",
            "options": [
                "Atomicity, Consistency, Isolation, Durability",
                "Accuracy, Completeness, Integrity, Dependability",
                "Aggregation, Clustering, Indexing, Deletion",
                "Authentication, Confidentiality, Identity, Decryption"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "ACID guarantees that database transactions are processed reliably (all-or-nothing atomicity, valid state consistency, isolation, and persistent durability)."
        }
    ],

    "machine learning": [
        {
            "question": "What does high variance and low bias typically signify in a supervised machine learning model?",
            "options": [
                "Underfitting the training dataset",
                "Overfitting the training data (poor generalization on test data)",
                "Optimal global convergence",
                "Excessive regularization strength"
            ],
            "correct": 1,
            "difficulty": "Beginner",
            "explanation": "High variance means the model captures noise in the training set, leading to overfitting and high generalization error."
        },
        {
            "question": "Why is ROC-AUC preferred over Accuracy on severely imbalanced classification datasets (e.g., 99% Negative, 1% Positive)?",
            "options": [
                "Accuracy is distorted by class prevalence; ROC-AUC evaluates TPR vs FPR trade-offs across all classification thresholds",
                "ROC-AUC only works on continuous regression problems",
                "Accuracy requires probability predictions",
                "ROC-AUC minimizes Mean Squared Error"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "On imbalanced datasets, predicting only the majority class gives 99% accuracy but zero recall. ROC-AUC evaluates true predictive discrimination across all thresholds."
        },
        {
            "question": "What is the primary difference between L1 (Lasso) and L2 (Ridge) regularization?",
            "options": [
                "L1 enforces sparsity by driving irrelevant weights to zero; L2 shrinks weights smoothly without setting them strictly to zero",
                "L2 zeros out coefficients, while L1 maintains continuous distributions",
                "L1 only works on neural networks; L2 only works on linear regression",
                "L1 increases variance; L2 increases bias"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "L1 norm produces diamond-shaped constraints that zero out feature weights (built-in feature selection), whereas L2 penalizes squared magnitudes."
        },
        {
            "question": "What is the core principle behind Random Forest ensemble models?",
            "options": [
                "Bagging (Bootstrap Aggregating) with random feature sub-sampling to reduce decision tree variance",
                "Sequential boosting where each tree corrects errors of previous trees",
                "Clustering data points into Voronoi cells",
                "Singular Value Decomposition on feature matrices"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "Random Forest builds multiple de-correlated decision trees on bootstrap data samples with feature subsets, averaging predictions to reduce variance."
        }
    ],

    "deep learning": [
        {
            "question": "What activation function is standard in hidden layers of deep neural networks to mitigate vanishing gradients?",
            "options": [
                "ReLU (Rectified Linear Unit)",
                "Sigmoid",
                "Softmax",
                "Linear Step Function"
            ],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "ReLU has a constant derivative of 1 for positive inputs, preventing the exponential decay of gradients during backpropagation."
        },
        {
            "question": "What is the mathematical formulation of the Scaled Dot-Product Attention in Transformer architectures?",
            "options": [
                "Softmax(Q * K^T / sqrt(d_k)) * V",
                "Sigmoid(W * X + b)",
                "Tanh(Q + K + V)",
                "Argmax(Q * K) / V"
            ],
            "correct": 0,
            "difficulty": "Advanced",
            "explanation": "Attention computes similarity scores between Query and Key vectors scaled by sqrt(d_k), normalized via Softmax, and multiplied by Value vectors."
        },
        {
            "question": "What is the main advantage of Batch Normalization in deep network training?",
            "options": [
                "Stabilizes internal covariate shift, allowing higher learning rates and faster convergence",
                "Reduces the number of parameters in the model",
                "Replaces convolutional filters with matrix inversions",
                "Eliminates the need for training labels"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "Batch Normalization normalizes activations across mini-batches, stabilizing training dynamics and accelerating convergence."
        }
    ],

    "pandas": [
        {
            "question": "What is the most vectorized way to perform conditional column operations in Pandas without a slow `.apply()`?",
            "options": [
                "`np.where(condition, true_val, false_val)` or `df.loc[condition, col] = val`",
                "Iterating with `for index, row in df.iterrows():`",
                "Exporting to CSV and re-reading",
                "Running `eval()` inside a list comprehension"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "`np.where` runs compiled C-level vector operations in NumPy memory buffers, executing 50-100x faster than row iteration in Python."
        },
        {
            "question": "What does `df.groupby('dept')['salary'].transform('mean')` do compared to `df.groupby('dept')['salary'].mean()`?",
            "options": [
                "Returns a Series with the same shape as the original DataFrame, broadcasting group means back to each row",
                "Returns an aggregated table indexed only by unique department names",
                "Deletes rows below the group mean",
                "Sorts the dataframe by salary"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "`.transform()` preserves original row count and index alignment, broadcasting calculated group metrics back across individual records."
        },
        {
            "question": "How do you drop duplicate records in a Pandas DataFrame based on specific columns?",
            "options": [
                "`df.drop_duplicates(subset=['col1', 'col2'])`",
                "`df.remove_repeats(columns=['col1', 'col2'])`",
                "`df.unique(columns=['col1', 'col2'])`",
                "`df.deduplicate()`"
            ],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "`drop_duplicates(subset=...)` drops duplicate rows matching on the given subset of columns."
        }
    ],

    "fastapi": [
        {
            "question": "How does FastAPI achieve high concurrent throughput compared to traditional WSGI frameworks like Flask?",
            "options": [
                "Built on ASGI (Starlette) and Python's native `asyncio` event loop with Pydantic validation",
                "Compiles Python code to C++ machine code at startup",
                "Bypasses all HTTP header checks",
                "Forces single-threaded execution"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "FastAPI is an ASGI framework leveraging non-blocking asynchronous coroutines (`async def`) and Pydantic schemas for rapid validation."
        },
        {
            "question": "How do you define automatic request body data validation in FastAPI?",
            "options": [
                "Declare parameter types using `pydantic.BaseModel` classes",
                "Write custom regex validation in route decorators",
                "Parse raw query strings manually",
                "Use global dictionary constants"
            ],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "FastAPI uses Pydantic BaseModel definitions to automatically deserialize JSON, validate data types, generate 422 errors, and produce Swagger schemas."
        }
    ],

    "docker": [
        {
            "question": "What is the primary benefit of multi-stage Docker builds?",
            "options": [
                "Produces lightweight production images by leaving compilers and build tools in earlier intermediate stages",
                "Allows containers to run on multiple operating systems at once",
                "Automates Kubernetes cluster provisioning",
                "Encrypts the container filesystem"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "Multi-stage builds allow developers to compile binaries in builder images and copy only required runtime artifacts into the final lean image."
        },
        {
            "question": "What is the key difference between `CMD` and `ENTRYPOINT` in a Dockerfile?",
            "options": [
                "`ENTRYPOINT` defines the base executable process; `CMD` provides default arguments that CLI flags can override",
                "`CMD` cannot be overridden when running `docker run`",
                "`ENTRYPOINT` only executes during image build time",
                "Both are identical commands"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "`ENTRYPOINT` specifies the core process, while `CMD` supplies default parameters that can be overridden by docker CLI arguments."
        }
    ],

    "scikit-learn": [
        {
            "question": "Why must you execute `pipeline.fit_transform(X_train)` and `pipeline.transform(X_test)` instead of fitting on both?",
            "options": [
                "To prevent data leakage from the test distribution into training statistics (e.g., mean, standard deviation, imputation values)",
                "Because fitting on test data raises a compile error",
                "To reduce memory usage during inference",
                "To automatically handle class imbalance"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "Fitting transformations on test data introduces data snooping, resulting in overly optimistic evaluation metrics that degrade on production data."
        },
        {
            "question": "Which scikit-learn module is used for hyperparameter tuning using cross-validation over a parameter grid?",
            "options": [
                "`sklearn.model_selection.GridSearchCV`",
                "`sklearn.metrics.ParameterOptimizer`",
                "`sklearn.preprocessing.HyperTuner`",
                "`sklearn.ensemble.GridSearch`"
            ],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "`GridSearchCV` exhaustively searches over specified parameter values with cross-validation to select the optimal hyperparameter combination."
        }
    ],

    "data structures & algorithms": [
        {
            "question": "Which data structure is optimal for implementing Breadth-First Search (BFS) graph traversal?",
            "options": ["Queue (FIFO)", "Stack (LIFO)", "Binary Search Tree", "Max Heap"],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "BFS explores nodes level by level in First-In-First-Out order, making a Queue (FIFO) the optimal data structure."
        },
        {
            "question": "What is the average and worst-case time complexity of QuickSort?",
            "options": [
                "Average: O(n log n), Worst: O(n^2)",
                "Average: O(n), Worst: O(n log n)",
                "Average: O(n^2), Worst: O(n^2)",
                "Average: O(log n), Worst: O(n)"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "QuickSort averages O(n log n) with balanced partitioning, but degrades to O(n^2) when poor pivots produce extreme splits."
        }
    ],

    "statistics & probability": [
        {
            "question": "What does the Central Limit Theorem (CLT) state?",
            "options": [
                "The sampling distribution of the sample mean approaches a normal distribution as sample size increases, regardless of population shape",
                "All continuous data is normally distributed in nature",
                "The median is always equal to the mean in large datasets",
                "Probability of independent events is always 0.5"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "The CLT guarantees that the distribution of sample means approaches normality for sufficiently large n (n >= 30), enabling hypothesis testing."
        },
        {
            "question": "What is a p-value in statistical hypothesis testing?",
            "options": [
                "The probability of observing test results at least as extreme as the actual results, assuming the null hypothesis is true",
                "The probability that the alternative hypothesis is true",
                "The probability of making a Type II error",
                "The percentage of missing data"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "A p-value measures evidence against the null hypothesis: smaller p-values indicate greater statistical incompatibility with H0."
        }
    ],

    "git & github": [
        {
            "question": "What is the difference between `git merge` and `git rebase`?",
            "options": [
                "`git merge` creates a new merge commit preserving history; `git rebase` rewrites commit history onto the target tip for a linear history",
                "`git rebase` deletes all remote branches",
                "`git merge` only works on local files; `git rebase` works on remotes",
                "There is no difference between merge and rebase"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "Merge preserves non-linear branching history with a merge commit, while rebase replays your commits atop the target branch for a clean linear log."
        }
    ],

    "pytorch": [
        {
            "question": "What does `loss.backward()` do in PyTorch?",
            "options": [
                "Computes the gradient of the loss with respect to all graph leaf tensors with `requires_grad=True` using automatic differentiation (Autograd)",
                "Updates the network weights directly",
                "Zeros out optimizer gradients",
                "Saves the model weights to disk"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "`loss.backward()` traverses the backward computation graph and populates the `.grad` attributes of parameter tensors."
        }
    ],

    "natural language processing (nlp)": [
        {
            "question": "What is the key advantage of dense vector word embeddings (e.g. Word2Vec, BERT) over sparse Bag-of-Words / TF-IDF representations?",
            "options": [
                "Dense embeddings capture semantic context, synonymy, and geometric relationships in a low-dimensional continuous space",
                "Sparse representations have zero memory overhead",
                "Dense embeddings eliminate the need for training data",
                "TF-IDF performs better on long documents"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "Dense embeddings map words and sentences into continuous vector spaces where cosine distance captures semantic similarity."
        }
    ],

    "tableau": [
        {
            "question": "What is the difference between Dimensions and Measures in Tableau?",
            "options": [
                "Dimensions contain discrete qualitative/categorical values; Measures contain continuous numeric values that can be aggregated (SUM, AVG)",
                "Measures are qualitative labels; Dimensions are numeric calculations",
                "Dimensions only exist in SQL databases; Measures exist in Excel",
                "They are identical and interchangeable"
            ],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "Dimensions slice and dice data categorically (e.g. Region, Category), while Measures represent quantitative measurable numbers (e.g. Profit, Sales)."
        }
    ],

    "power bi": [
        {
            "question": "What language is primarily used for creating custom calculations, measures, and calculated columns in Power BI?",
            "options": ["DAX (Data Analysis Expressions)", "Python Scripting", "TypeScript", "VBA"],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "DAX (Data Analysis Expressions) is the formula language used in Power BI, Analysis Services, and Power Pivot."
        }
    ],

    "big data fundamentals (spark)": [
        {
            "question": "What is an RDD (Resilient Distributed Dataset) in Apache Spark?",
            "options": [
                "An immutable, lazily evaluated, distributed collection of elements partitioned across cluster nodes",
                "A relational SQL table stored only on a single disk",
                "A real-time socket connection for GPU streaming",
                "A hardware RAID disk array"
            ],
            "correct": 0,
            "difficulty": "Intermediate",
            "explanation": "RDDs are the foundational data structure of Spark, providing fault-tolerant, in-memory distributed data collections with lazy evaluation."
        }
    ],

    "cloud fundamentals (aws/gcp)": [
        {
            "question": "Which AWS service is designed for serverless event-driven compute without managing EC2 server infrastructure?",
            "options": ["AWS Lambda", "Amazon EC2", "Amazon S3", "Amazon RDS"],
            "correct": 0,
            "difficulty": "Beginner",
            "explanation": "AWS Lambda runs backend code in response to events and automatically manages underlying compute resources."
        }
    ]
}


class QuizEngine:
    """
    Manages generation, delivery, and evaluation of technical skill assessment quizzes,
    calculating marks, percentages, grades, and question-level feedback.
    """

    def __init__(self, data_loader: Optional[DataLoader] = None):
        self.loader = data_loader if data_loader else DataLoader()
        self.question_bank = TECHNICAL_QUESTION_BANK

    def get_quiz_for_skill(
        self,
        skill_name: str,
        num_questions: int = 5
    ) -> List[QuizQuestion]:
        """
        Retrieves or compiles technical multiple-choice assessment questions for a given skill.
        """
        canonical_key = skill_name.strip().lower()
        
        # Match closest skill key
        matched_key = None
        for key in self.question_bank:
            if key == canonical_key or key in canonical_key or canonical_key in key:
                matched_key = key
                break

        questions_pool = []
        if matched_key:
            questions_pool = list(self.question_bank[matched_key])
        else:
            # Fallback to relevant category questions
            if "sql" in canonical_key or "database" in canonical_key or "relational" in canonical_key:
                questions_pool = list(self.question_bank["sql"])
            elif "learn" in canonical_key or "model" in canonical_key or "feature" in canonical_key:
                questions_pool = list(self.question_bank["machine learning"])
            elif "deep" in canonical_key or "neural" in canonical_key or "pytorch" in canonical_key or "tensor" in canonical_key:
                questions_pool = list(self.question_bank.get("deep learning", self.question_bank["machine learning"]))
            elif "docker" in canonical_key or "cloud" in canonical_key or "devops" in canonical_key:
                questions_pool = list(self.question_bank["docker"])
            elif "stat" in canonical_key or "prob" in canonical_key or "math" in canonical_key:
                questions_pool = list(self.question_bank.get("statistics & probability", self.question_bank["machine learning"]))
            elif "bi" in canonical_key or "tableau" in canonical_key or "power" in canonical_key or "visual" in canonical_key:
                questions_pool = list(self.question_bank.get("tableau", self.question_bank["pandas"]))
            else:
                questions_pool = list(self.question_bank["python"])

        # If pool has fewer items than requested, pad with related general questions
        if len(questions_pool) < num_questions:
            pad_pool = self.question_bank["python"] + self.question_bank.get("machine learning", []) + self.question_bank.get("data structures & algorithms", [])
            for item in pad_pool:
                if item not in questions_pool:
                    questions_pool.append(item)
                if len(questions_pool) >= num_questions:
                    break

        selected_raw = questions_pool[:num_questions]
        quiz_questions = []
        for i, q in enumerate(selected_raw):
            qid = f"QZ_{canonical_key.replace(' ', '_')}_{i+1}"
            quiz_questions.append(
                QuizQuestion(
                    question_id=qid,
                    skill_name=skill_name,
                    question_text=q["question"],
                    options=q["options"],
                    correct_option_index=q["correct"],
                    difficulty=q.get("difficulty", "Intermediate"),
                    explanation=q.get("explanation", "Standard technical industry concept.")
                )
            )

        return quiz_questions

    def evaluate_quiz(
        self,
        skill_name: str,
        user_answers: List[int]
    ) -> QuizResult:
        """
        Evaluates submitted option indices against correct question answers,
        calculates marks (10 marks per question), percentage, and letter grade.
        """
        questions = self.get_quiz_for_skill(skill_name, num_questions=len(user_answers) or 5)
        
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
        passed = (pct >= 60.0)

        # Award Letter Grades
        if pct >= 90.0:
            grade = "A+ (Outstanding)"
            feedback = f"🎉 Mastery Verified! Outstanding Performance! You scored {score * 10}/{total * 10} marks ({score}/{total} correct - {pct:.0f}%). You have mastered {skill_name} concepts!"
        elif pct >= 75.0:
            grade = "A (Proficient)"
            feedback = f"🎉 Mastery Verified! Great Job! You scored {score * 10}/{total * 10} marks ({score}/{total} correct - {pct:.0f}%). Strong proficiency in {skill_name}!"
        elif pct >= 60.0:
            grade = "B (Good / Pass)"
            feedback = f"🎉 Mastery Verified! You scored {score * 10}/{total * 10} marks ({score}/{total} correct - {pct:.0f}%). Good foundation in {skill_name}!"
        elif pct >= 40.0:
            grade = "C (Needs Practice)"
            feedback = f"⚠️ Quiz Not Passed ({score * 10}/{total * 10} marks - {pct:.0f}%). Review the questions and explanations below to strengthen your understanding."
        else:
            grade = "F (Revise Fundamentals)"
            feedback = f"⚠️ Quiz Not Passed ({score * 10}/{total * 10} marks - {pct:.0f}%). We recommend revising the core documentation and fundamentals for {skill_name}."

        return QuizResult(
            skill_name=skill_name,
            score=score,
            total_questions=total,
            percentage=pct,
            passed=passed,
            feedback=feedback,
            question_evaluations=evaluations,
            marks_obtained=score * 10,
            total_marks=total * 10,
            grade=grade
        )
