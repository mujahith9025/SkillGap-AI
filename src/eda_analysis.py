"""
Exploratory Data Analysis (EDA) Script
Phase 4: Data Loading and Exploratory Data Analysis

Performs automated statistical checks, missing-value audits,
duplicate inspection, and generates publication-grade visualizations.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from data_loader import DataLoader

# Setup output directory for plots
OUTPUT_PLOT_DIR = Path(__file__).resolve().parent.parent / "data" / "plots"
OUTPUT_PLOT_DIR.mkdir(parents=True, exist_ok=True)

# Set global seaborn styling
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.sans-serif": "Arial", "font.size": 11, "figure.autolayout": True})

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f" {title.upper()}")
    print("=" * 70)

def run_eda_inspection(loader: DataLoader):
    """Inspects shapes, columns, data types, missing values, and duplicates."""
    print_header("1. Dataset Structural & Quality Inspection")
    
    for name, df in loader.datasets.items():
        print(f"\n--- Table: {name}.csv ---")
        print(f"  Shape: {df.shape[0]} rows x {df.shape[1]} columns")
        print(f"  Columns & Types:\n" + "\n".join([f"    - {col:25} ({dtype})" for col, dtype in zip(df.columns, df.dtypes)]))
        
        # Missing values check
        missing = df.isnull().sum()
        missing_count = missing.sum()
        if missing_count == 0:
            print("  Missing Values: 0 (100% complete)")
        else:
            print(f"  Missing Values Found:\n{missing[missing > 0]}")
            
        # Duplicate rows check
        dup_count = df.duplicated().sum()
        print(f"  Duplicate Rows: {dup_count}")

def run_descriptive_statistics(loader: DataLoader):
    """Computes basic distribution and relational statistics."""
    print_header("2. Descriptive Domain Statistics")
    
    careers_df = loader.careers
    skills_df = loader.skills
    cs_df = loader.career_skills
    prereq_df = loader.skill_prerequisites
    res_df = loader.learning_resources
    prj_df = loader.projects
    
    print(f"[*] Total Career Roles Defined: {len(careers_df)}")
    print(f"[*] Total Unique Skills in Taxonomy: {len(skills_df)}")
    print(f"[*] Total Career-Skill Mappings: {len(cs_df)}")
    print(f"[*] Total Skill Prerequisite Dependencies: {len(prereq_df)}")
    print(f"[*] Total Curated Learning Resources: {len(res_df)}")
    print(f"[*] Total Portfolio Projects: {len(prj_df)}")
    
    # Career-skills per role statistics
    skills_per_career = cs_df.groupby("career_id").size()
    print(f"\n[*] Skills required per career role:")
    print(f"    - Minimum: {skills_per_career.min()} skills")
    print(f"    - Maximum: {skills_per_career.max()} skills")
    print(f"    - Average: {skills_per_career.mean():.1f} skills / role")
    
    # Skill Importance Distribution
    imp_dist = cs_df["importance_level"].value_counts(normalize=True) * 100
    print(f"\n[*] Skill Importance Distribution across all role requirements:")
    for level, pct in imp_dist.items():
        print(f"    - {level:10}: {cs_df['importance_level'].value_counts()[level]:2d} mappings ({pct:.1f}%)")
        
    # Top 10 most demanded skills across all roles
    merged_cs = pd.merge(cs_df, skills_df, on="skill_id")
    top_skills = merged_cs["skill_name"].value_counts().head(10)
    print(f"\n[*] Top 10 Most Common In-Demand Skills Across All 7 Roles:")
    for rank, (skill, count) in enumerate(top_skills.items(), 1):
        pct = (count / len(careers_df)) * 100
        print(f"    {rank:2d}. {skill:30} in {count}/{len(careers_df)} roles ({pct:.1f}%)")

def generate_visualizations(loader: DataLoader):
    """Generates and saves 4 comprehensive EDA visualization charts."""
    print_header("3. Generating Statistical Visualizations")
    
    # -------------------------------------------------------------
    # Plot 1: Top Most Frequent Skills
    # -------------------------------------------------------------
    merged_cs = pd.merge(loader.career_skills, loader.skills, on="skill_id")
    skill_counts = merged_cs["skill_name"].value_counts().head(12)
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        x=skill_counts.values,
        y=skill_counts.index,
        palette="crest_r",
        edgecolor="black"
    )
    plt.title("Top Most In-Demand Skills Across All 7 Career Roles", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of Career Roles Requiring Skill (out of 7)", fontsize=11)
    plt.ylabel("Standardized Skill Name", fontsize=11)
    plt.xlim(0, 7.5)
    
    for i, count in enumerate(skill_counts.values):
        ax.text(count + 0.1, i, f"{count} ({count/7*100:.0f}%)", va="center", fontsize=10, fontweight="bold")
        
    p1_path = OUTPUT_PLOT_DIR / "01_skill_frequency.png"
    plt.savefig(p1_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  [SAVED] Plot 1: {p1_path.name}")
    
    # -------------------------------------------------------------
    # Plot 2: Skill Importance Distribution
    # -------------------------------------------------------------
    plt.figure(figsize=(8, 5))
    imp_order = ["Core", "Secondary", "Optional"]
    colors = ["#e74c3c", "#f39c12", "#3498db"]
    ax = sns.countplot(
        data=loader.career_skills,
        x="importance_level",
        order=imp_order,
        palette=colors,
        edgecolor="black"
    )
    plt.title("Skill Criticality Distribution (Importance Level)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Importance Level", fontsize=11)
    plt.ylabel("Number of Role Requirements", fontsize=11)
    
    total = len(loader.career_skills)
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(f"{height} ({height/total*100:.1f}%)",
                    (p.get_x() + p.get_width() / 2., height / 2),
                    ha="center", va="center", color="white", fontsize=11, fontweight="bold")
        
    p2_path = OUTPUT_PLOT_DIR / "02_skill_importance_distribution.png"
    plt.savefig(p2_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  [SAVED] Plot 2: {p2_path.name}")

    # -------------------------------------------------------------
    # Plot 3: Career vs Skill Heatmap
    # -------------------------------------------------------------
    matrix = loader.get_career_skill_matrix()
    plt.figure(figsize=(16, 7))
    cmap = sns.color_palette(["#f8f9fa", "#aed6f1", "#f9e79f", "#f1948a"])
    sns.heatmap(
        matrix,
        cmap=cmap,
        linewidths=0.7,
        linecolor="#bdc3c7",
        cbar_kws={
            "ticks": [0.375, 1.125, 1.875, 2.625],
            "label": "Requirement Weight (0: None, 1: Optional, 2: Secondary, 3: Core)"
        }
    )
    # Set custom colorbar labels
    cbar = plt.gcf().axes[-1]
    cbar.set_yticklabels(["Not Required (0)", "Optional (1)", "Secondary (2)", "Core (3)"])
    
    plt.title("Career Role vs. Skill Requirement Matrix", fontsize=15, fontweight="bold", pad=15)
    plt.xlabel("Skills in Taxonomy", fontsize=12)
    plt.ylabel("Target Career Roles", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=10)
    
    p3_path = OUTPUT_PLOT_DIR / "03_career_skill_heatmap.png"
    plt.savefig(p3_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  [SAVED] Plot 3: {p3_path.name}")

    # -------------------------------------------------------------
    # Plot 4: Skill Categories & Difficulty Level
    # -------------------------------------------------------------
    plt.figure(figsize=(12, 6))
    diff_order = ["Beginner", "Intermediate", "Advanced"]
    sns.countplot(
        data=loader.skills,
        y="category",
        hue="difficulty_level",
        hue_order=diff_order,
        palette="viridis",
        edgecolor="black"
    )
    plt.title("Skill Taxonomy: Domain Category vs. Difficulty Level", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Number of Skills", fontsize=11)
    plt.ylabel("Technical Category", fontsize=11)
    plt.legend(title="Difficulty Level", loc="lower right")
    
    p4_path = OUTPUT_PLOT_DIR / "04_skill_difficulty_categories.png"
    plt.savefig(p4_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  [SAVED] Plot 4: {p4_path.name}")

def main():
    loader = DataLoader()
    run_eda_inspection(loader)
    run_descriptive_statistics(loader)
    generate_visualizations(loader)
    print("\n" + "=" * 70)
    print(" EXPLORATORY DATA ANALYSIS COMPLETED SUCCESSFULLY!")
    print(f" Plots generated in: {OUTPUT_PLOT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
