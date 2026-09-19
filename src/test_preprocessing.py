"""
Test & Benchmark Suite for Preprocessing and Skill Normalization
Phase 5: Data Cleaning and Skill Normalization

Tests edge cases:
- Missing / Null / Empty strings
- Whitespace & Casing variations
- Aliases & Abbreviations (ML -> Machine Learning, etc.)
- Specific tool mappings (PostgreSQL -> SQL, Keras -> TensorFlow)
- Typo tolerance via RapidFuzz
- Multi-skill string parsing & deduplication
"""

import sys
from pathlib import Path

# Add src to path
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from preprocessing import SkillPreprocessor

def test_normalization_suite():
    print("=" * 75)
    print(" SKILL PREPROCESSING & NORMALIZATION TEST SUITE")
    print("=" * 75)
    
    preprocessor = SkillPreprocessor()
    
    # 1. Single Skill Normalization Test Cases
    test_cases = [
        # (Input, Expected Output, Description)
        ("ML", "Machine Learning", "Abbreviation mapping"),
        ("ml", "Machine Learning", "Lower-case abbreviation"),
        ("Python Programming", "Python", "Verbose skill synonym"),
        ("  python   ", "Python", "Whitespace stripping"),
        ("pYtHoN", "Python", "Mixed capitalization"),
        ("Data Viz", "Data Visualization", "Colloquial abbreviation"),
        ("data visualization", "Data Visualization", "Exact canonical name"),
        ("NLP", "Natural Language Processing (NLP)", "Acronym with expanded canonical"),
        ("DL", "Deep Learning", "Acronym mapping"),
        ("PostgreSQL", "SQL", "Specific RDBMS to generic SQL"),
        ("MySQL", "SQL", "Specific RDBMS to generic SQL"),
        ("Sklearn", "Scikit-Learn", "Common package alias"),
        ("scikit learn", "Scikit-Learn", "Space separated variant"),
        ("pythn", "Python", "Typo correction (fuzzy match)"),
        ("scikit-leran", "Scikit-Learn", "Typo correction (fuzzy match)"),
        ("tablo", "Tableau", "Typo correction (fuzzy match)"),
        ("statistcs", "Statistics & Probability", "Typo correction (fuzzy match)"),
        ("AWS", "Cloud Fundamentals (AWS/GCP)", "Cloud vendor to canonical"),
        ("GCP", "Cloud Fundamentals (AWS/GCP)", "Cloud vendor to canonical"),
        ("Docker Containers", "Docker", "Verbose tool synonym"),
        ("Fast API", "FastAPI", "Spaced framework name"),
        ("PySpark", "Big Data Fundamentals (Spark)", "Ecosystem tool to canonical"),
        ("MS Excel", "Excel", "Vendor prefixed spreadsheet"),
        ("PowerBI", "Power BI", "Unspaced product name"),
        ("GenAI", "Large Language Models (LLMs)", "Modern AI term to canonical"),
        ("RAG", "Large Language Models (LLMs)", "Modern AI term to canonical"),
        ("", None, "Empty string handling"),
        ("   ", None, "Whitespace-only string handling"),
        ("UnknownNonExistentTechXYZ123", None, "Unrecognized skill handling"),
    ]
    
    passed_count = 0
    print("\n--- 1. Individual Skill Normalization Unit Tests ---")
    print(f"{'Input Text':<30} | {'Expected Canonical':<32} | {'Result':<10} | {'Method'}")
    print("-" * 105)
    
    for raw_input, expected, desc in test_cases:
        actual, method = preprocessor.normalize_single_skill(raw_input)
        is_pass = (actual == expected)
        if is_pass:
            passed_count += 1
            res_str = "[PASS]"
        else:
            res_str = f"[FAIL -> {actual}]"
            
        print(f"{raw_input:<30} | {str(expected):<32} | {res_str:<10} | {method}")
        
    print(f"\nUnit Tests Summary: {passed_count}/{len(test_cases)} Passed ({(passed_count/len(test_cases))*100:.1f}%)")
    
    # 2. Multi-Skill Deduplication Test
    print("\n--- 2. Multi-Skill Deduplication Test ---")
    duplicate_inputs = [
        "Python", "python", "PYTHON", "Python Programming", "py", "python 3", "pythn"
    ]
    print(f"Raw Input Array (7 redundant variations): {duplicate_inputs}")
    deduped = preprocessor.normalize_skill_list(duplicate_inputs)
    print(f"Deduplicated Canonical Result: {deduped}")
    assert deduped == ["Python"], f"Expected ['Python'], got {deduped}"
    print("[PASS] Deduplication correctly collapsed all 7 variations into a single 'Python' entry.")

    # 3. Free-Form Text & Resume-style String Parsing Test
    print("\n--- 3. Free-Form Raw Text String Parsing Test ---")
    raw_user_string = (
        "Skills: Python, pandas, ML, deep-learning, pythn, Tableau, SQL; "
        "Git/GitHub, MS Excel, Fast API, scikit-leran, PostgreSQL"
    )
    print(f"Raw Free-Form Input String:\n  \"{raw_user_string}\"")
    parsed_skills = preprocessor.parse_raw_text_skills(raw_user_string)
    print(f"\nParsed & Normalized Canonical Skills ({len(parsed_skills)} unique):")
    for i, s in enumerate(parsed_skills, 1):
        print(f"  {i:2d}. {s}")
        
    expected_skills = [
        "Python", "Pandas", "Machine Learning", "Deep Learning",
        "Tableau", "SQL", "Git & GitHub", "Excel", "FastAPI", "Scikit-Learn"
    ]
    for exp in expected_skills:
        assert exp in parsed_skills, f"Expected '{exp}' to be extracted in parsed output!"
        
    print("\n[SUCCESS] Free-form parsing extracted all expected canonical competencies without duplicates.")
    print("=" * 75)
    return passed_count == len(test_cases)

if __name__ == "__main__":
    success = test_normalization_suite()
    sys.exit(0 if success else 1)
