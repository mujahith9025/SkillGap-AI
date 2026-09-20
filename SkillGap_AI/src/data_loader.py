"""
Data Loader Module
Phase 4: Data Loading and Exploratory Data Analysis

Provides unified access, schema enforcement, relational joins,
and helper lookup functions for all system datasets.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

# Default path to the data folder
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class DataLoader:
    """
    Manages loading, validating, and querying relational project datasets.
    """
    
    REQUIRED_FILES = {
        "careers": "careers.csv",
        "skills": "skills.csv",
        "career_skills": "career_skills.csv",
        "skill_prerequisites": "skill_prerequisites.csv",
        "learning_resources": "learning_resources.csv",
        "projects": "projects.csv"
    }

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
        self.datasets: Dict[str, pd.DataFrame] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Loads all CSV datasets into memory with basic validation."""
        for name, filename in self.REQUIRED_FILES.items():
            filepath = self.data_dir / filename
            if not filepath.exists():
                raise FileNotFoundError(f"Required dataset file not found: {filepath}")
            
            df = pd.read_csv(filepath)
            # Strip whitespace from string columns
            df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
            self.datasets[name] = df

    @property
    def careers(self) -> pd.DataFrame:
        return self.datasets["careers"]

    @property
    def skills(self) -> pd.DataFrame:
        return self.datasets["skills"]

    @property
    def career_skills(self) -> pd.DataFrame:
        return self.datasets["career_skills"]

    @property
    def skill_prerequisites(self) -> pd.DataFrame:
        return self.datasets["skill_prerequisites"]

    @property
    def learning_resources(self) -> pd.DataFrame:
        return self.datasets["learning_resources"]

    @property
    def projects(self) -> pd.DataFrame:
        return self.datasets["projects"]

    def get_career_by_title_or_id(self, identifier: Optional[str]) -> Optional[pd.Series]:
        """Looks up a career by its ID (CAR_01) or title (e.g. 'Data Scientist')."""
        if not identifier or not isinstance(identifier, str) or not identifier.strip():
            return None
        c_df = self.careers
        cleaned = identifier.strip()
        match = c_df[(c_df["career_id"].str.upper() == cleaned.upper()) | 
                     (c_df["career_title"].str.lower() == cleaned.lower())]
        if not match.empty:
            return match.iloc[0]
        return None

    def get_career_requirements(self, career_identifier: str) -> pd.DataFrame:
        """
        Returns a joined DataFrame of all skills required for a given career,
        sorted by importance_weight descending.
        """
        if not career_identifier or not isinstance(career_identifier, str) or not career_identifier.strip():
            raise ValueError("Career identifier cannot be empty or None.")

        career_series = self.get_career_by_title_or_id(career_identifier)
        if career_series is None:
            available_careers = ", ".join(self.careers["career_title"].tolist())
            raise ValueError(f"Career not found: '{career_identifier}'. Available options: {available_careers}")
        
        cid = career_series["career_id"]
        cs_filtered = self.career_skills[self.career_skills["career_id"] == cid]
        
        # Merge with skills table to get skill details
        merged = pd.merge(
            cs_filtered,
            self.skills,
            on="skill_id",
            how="inner"
        )
        
        return merged.sort_values(by=["importance_weight", "skill_name"], ascending=[False, True])

    def get_skill_by_name_or_id(self, identifier: Optional[str]) -> Optional[pd.Series]:
        """Looks up a skill by ID (SKL_01) or exact name."""
        if not identifier or not isinstance(identifier, str) or not identifier.strip():
            return None
        s_df = self.skills
        cleaned = identifier.strip()
        match = s_df[(s_df["skill_id"].str.upper() == cleaned.upper()) | 
                     (s_df["skill_name"].str.lower() == cleaned.lower())]
        if not match.empty:
            return match.iloc[0]
        return None

    def get_career_skill_matrix(self) -> pd.DataFrame:
        """
        Constructs a binary or weighted cross-tabulation matrix:
        Rows = Careers, Columns = Skills, Values = Importance Weight (0 if not required).
        """
        merged = pd.merge(
            self.career_skills,
            self.careers[["career_id", "career_title"]],
            on="career_id"
        ).merge(
            self.skills[["skill_id", "skill_name"]],
            on="skill_id"
        )
        
        matrix = merged.pivot_table(
            index="career_title",
            columns="skill_name",
            values="importance_weight",
            fill_value=0
        )
        return matrix

    def get_prerequisites_for_skill(self, skill_id: str) -> pd.DataFrame:
        """Returns all prerequisite skills and reasons for a specified skill_id."""
        prereqs = self.skill_prerequisites[self.skill_prerequisites["skill_id"] == skill_id]
        if prereqs.empty:
            return pd.DataFrame(columns=["prerequisite_skill_id", "prerequisite_skill_name", "prerequisite_type", "reason"])
        
        # Merge with skills table to resolve prerequisite skill names
        merged = pd.merge(
            prereqs,
            self.skills[["skill_id", "skill_name"]].rename(columns={"skill_id": "prerequisite_skill_id", "skill_name": "prerequisite_skill_name"}),
            on="prerequisite_skill_id",
            how="left"
        )
        return merged[["prerequisite_skill_id", "prerequisite_skill_name", "prerequisite_type", "reason"]]

    def get_resources_for_skill(self, skill_id: str) -> pd.DataFrame:
        """Returns all curated learning resources for a specified skill."""
        return self.learning_resources[self.learning_resources["skill_id"] == skill_id]

    def get_projects_for_career(self, career_id: str) -> pd.DataFrame:
        """Returns all recommended portfolio projects for a specified career."""
        return self.projects[self.projects["career_id"] == career_id]
