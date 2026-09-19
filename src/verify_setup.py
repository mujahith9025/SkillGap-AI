"""
Setup Verification Script
Phase 1: Project Definition, Requirements & Architecture

This script verifies:
1. Python version compatibility (>= 3.9)
2. Required project directory structure
3. Status of required Python dependencies
"""

import sys
import os
from pathlib import Path

REQUIRED_PYTHON_VERSION = (3, 9)
REQUIRED_DIRECTORIES = ["data", "notebooks", "src", "models"]

CORE_PACKAGES = [
    ("pandas", "Data manipulation & CSV handling"),
    ("numpy", "Numerical computing"),
    ("matplotlib", "Data visualization"),
    ("seaborn", "Statistical data visualization"),
    ("sklearn", "Machine learning utilities (scikit-learn)"),
    ("nltk", "Natural language toolkit"),
    ("spacy", "Industrial-strength NLP"),
    ("sentence_transformers", "Dense vector embeddings for semantic matching"),
    ("fitz", "PDF resume text extraction (PyMuPDF)"),
    ("streamlit", "Interactive web dashboard"),
]

def check_python_version():
    current_ver = sys.version_info
    print(f"[*] Checking Python Version: {current_ver.major}.{current_ver.minor}.{current_ver.micro}")
    if (current_ver.major, current_ver.minor) >= REQUIRED_PYTHON_VERSION:
        print("  [SUCCESS] Python version is compatible.")
        return True
    else:
        print(f"  [FAIL] Python >= {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]} is required.")
        return False

def check_directories(base_path: Path):
    print("\n[*] Checking Project Directory Structure:")
    all_ok = True
    for folder in REQUIRED_DIRECTORIES:
        folder_path = base_path / folder
        if folder_path.exists() and folder_path.is_dir():
            print(f"  [OK] Directory exists: {folder}/")
        else:
            print(f"  [CREATING] Directory created: {folder}/")
            folder_path.mkdir(parents=True, exist_ok=True)
    return all_ok

def check_dependencies():
    print("\n[*] Checking Key Package Installations:")
    installed_count = 0
    missing_packages = []
    
    for pkg_name, description in CORE_PACKAGES:
        try:
            __import__(pkg_name)
            print(f"  [INSTALLED] {pkg_name:22} - {description}")
            installed_count += 1
        except ImportError:
            print(f"  [MISSING]   {pkg_name:22} - {description}")
            missing_packages.append(pkg_name)
            
    print(f"\nSummary: {installed_count}/{len(CORE_PACKAGES)} packages currently available.")
    if missing_packages:
        print("Tip: Install missing packages using: pip install -r requirements.txt")
    return len(missing_packages) == 0

def main():
    print("=" * 65)
    print(" STUDENT SKILL GAP & CAREER RECOMMENDATION SYSTEM - SETUP CHECK")
    print("=" * 65)
    
    base_dir = Path(__file__).resolve().parent.parent
    
    py_ok = check_python_version()
    dir_ok = check_directories(base_dir)
    deps_ok = check_dependencies()
    
    print("\n" + "=" * 65)
    if py_ok and dir_ok:
        print("Phase 1 System Scaffolding is READY.")
        if not deps_ok:
            print("Action Needed: Run 'pip install -r requirements.txt' when ready.")
    else:
        print("Setup verification encountered issues. Please review logs above.")
    print("=" * 65)

if __name__ == "__main__":
    main()
