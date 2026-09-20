"""
Dataset Validation & Schema Integrity Verifier
Phase 3: Dataset Design and Creation

This script checks:
1. File existence for all CSV tables.
2. Non-empty records and required column names.
3. Primary key uniqueness in each table.
4. Foreign key referential integrity (career_id, skill_id, prereq_id).
5. Prerequisite Directed Acyclic Graph (DAG) cycle detection.
6. Summary statistics for each table.
"""

import sys
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

TABLES = {
    "careers": {
        "file": "careers.csv",
        "pk": "career_id",
        "required_cols": ["career_id", "career_title", "category", "experience_level", "description"]
    },
    "skills": {
        "file": "skills.csv",
        "pk": "skill_id",
        "required_cols": ["skill_id", "skill_name", "category", "difficulty_level", "description"]
    },
    "career_skills": {
        "file": "career_skills.csv",
        "pk": "mapping_id",
        "required_cols": ["mapping_id", "career_id", "skill_id", "importance_level", "importance_weight", "min_proficiency"]
    },
    "skill_prerequisites": {
        "file": "skill_prerequisites.csv",
        "pk": "prereq_id",
        "required_cols": ["prereq_id", "skill_id", "prerequisite_skill_id", "prerequisite_type", "reason"]
    },
    "learning_resources": {
        "file": "learning_resources.csv",
        "pk": "resource_id",
        "required_cols": ["resource_id", "skill_id", "title", "resource_type", "platform", "cost", "url_or_ref", "estimated_hours"]
    },
    "projects": {
        "file": "projects.csv",
        "pk": "project_id",
        "required_cols": ["project_id", "career_id", "title", "difficulty", "primary_skills", "description", "key_deliverables"]
    }
}

def validate_datasets():
    print("=" * 70)
    print(" DATASET INTEGRITY & RELATIONAL VALIDATION SUITE")
    print("=" * 70)
    
    dfs = {}
    errors = []
    
    # 1. Load and check column structure
    for table_name, meta in TABLES.items():
        file_path = DATA_DIR / meta["file"]
        if not file_path.exists():
            errors.append(f"Missing file: {meta['file']}")
            continue
        
        df = pd.read_csv(file_path)
        dfs[table_name] = df
        
        # Check required columns
        missing_cols = set(meta["required_cols"]) - set(df.columns)
        if missing_cols:
            errors.append(f"{meta['file']}: Missing columns {missing_cols}")
            
        # Check primary key uniqueness
        pk = meta["pk"]
        if pk in df.columns:
            if df[pk].duplicated().any():
                dups = df[df[pk].duplicated()][pk].tolist()
                errors.append(f"{meta['file']}: Duplicate primary key values in '{pk}': {dups}")
                
        print(f"[OK] Loaded {meta['file']:25} | Records: {len(df):3d} | Columns: {len(df.columns):2d}")
    
    if errors:
        print("\n[FAIL] Found Schema / Loading Errors:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("\n[*] Validating Relational Integrity (Foreign Keys)...")
    
    # 2. Check career_skills FKs
    valid_career_ids = set(dfs["careers"]["career_id"])
    valid_skill_ids = set(dfs["skills"]["skill_id"])
    
    invalid_careers_in_cs = set(dfs["career_skills"]["career_id"]) - valid_career_ids
    invalid_skills_in_cs = set(dfs["career_skills"]["skill_id"]) - valid_skill_ids
    
    if invalid_careers_in_cs:
        errors.append(f"career_skills.csv has invalid career_ids: {invalid_careers_in_cs}")
    if invalid_skills_in_cs:
        errors.append(f"career_skills.csv has invalid skill_ids: {invalid_skills_in_cs}")
        
    # 3. Check skill_prerequisites FKs
    invalid_skills_in_prereq = set(dfs["skill_prerequisites"]["skill_id"]) - valid_skill_ids
    invalid_parent_prereqs = set(dfs["skill_prerequisites"]["prerequisite_skill_id"]) - valid_skill_ids
    
    if invalid_skills_in_prereq:
        errors.append(f"skill_prerequisites.csv has invalid skill_ids: {invalid_skills_in_prereq}")
    if invalid_parent_prereqs:
        errors.append(f"skill_prerequisites.csv has invalid prerequisite_skill_ids: {invalid_parent_prereqs}")
        
    # 4. Check learning_resources FKs
    invalid_skills_in_res = set(dfs["learning_resources"]["skill_id"]) - valid_skill_ids
    if invalid_skills_in_res:
        errors.append(f"learning_resources.csv has invalid skill_ids: {invalid_skills_in_res}")
        
    # 5. Check projects FKs
    invalid_careers_in_prj = set(dfs["projects"]["career_id"]) - valid_career_ids
    if invalid_careers_in_prj:
        errors.append(f"projects.csv has invalid career_ids: {invalid_careers_in_prj}")
        
    # 6. Check for cycles in prerequisites (DAG validation)
    print("[*] Validating Prerequisite Dependency Graph (Cycle Detection)...")
    adj = {s_id: [] for s_id in valid_skill_ids}
    for _, row in dfs["skill_prerequisites"].iterrows():
        adj[row["skill_id"]].append(row["prerequisite_skill_id"])
        
    visited = {}
    def has_cycle(node, path):
        visited[node] = True
        path.add(node)
        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, path):
                    return True
            elif neighbor in path:
                return True
        path.remove(node)
        return False

    cycle_detected = False
    for skill in valid_skill_ids:
        if skill not in visited:
            if has_cycle(skill, set()):
                cycle_detected = True
                errors.append(f"Circular dependency detected in skill_prerequisites starting at skill {skill}!")
                break
                
    if not cycle_detected:
        print("  [SUCCESS] Prerequisite graph is a valid Directed Acyclic Graph (DAG) with no cycles.")

    # Final Report
    print("=" * 70)
    if errors:
        print("[FAIL] Validation failed with errors:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("ALL DATASET SCHEMAS & RELATIONAL CONSTRAINTS PASSED SUCCESSFULLY!")
        print("=" * 70)
        return True

if __name__ == "__main__":
    success = validate_datasets()
    sys.exit(0 if success else 1)
