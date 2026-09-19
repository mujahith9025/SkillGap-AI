"""
Test Runner for Resume PDF Parsing & Skill Extraction
Phase 12: Resume Upload and Skill Extraction

Generates reproducible test PDF fixtures and validates:
1. Valid Student Resume parsing & skill identification
2. Handling of Empty PDF documents
3. Handling of Corrupted / Non-PDF files
4. Interactive extraction preview for student verification
"""

import sys
from pathlib import Path
import pymupdf  # Modern PyMuPDF API

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from resume_parser import ResumeParser, ResumeSkillProfile

TEST_RESUME_DIR = Path(__file__).resolve().parent.parent / "data" / "test_resumes"
TEST_RESUME_DIR.mkdir(parents=True, exist_ok=True)


def create_sample_pdf_fixtures():
    """Generates sample test PDF fixtures on disk."""
    # 1. Valid Data Science Resume
    valid_pdf_path = TEST_RESUME_DIR / "sample_data_scientist_resume.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    
    resume_text = """
    ALEX CHEN
    Email: alex.chen@example.com | Phone: +1 555-0199 | Portfolio: github.com/alexchen-ai
    B.Tech Artificial Intelligence and Data Science (Final Year)

    TECHNICAL SKILLS
    Languages & Databases: Python, SQL, PostgreSQL, SQLite
    Data Science & ML: Pandas, NumPy, Scikit-Learn, Machine Learning, Statistics & Probability
    Visualization & BI: Tableau, Power BI, Matplotlib & Seaborn, Excel
    Tools & DevOps: Git/GitHub, Docker, Linux

    ACADEMIC PROJECTS
    1. Customer Churn Prediction Engine
       - Built classification models using Scikit-Learn (Random Forest, XGBoost).
       - Performed data preprocessing & cleaning and feature engineering using Pandas.
    2. Interactive Sales Analytics & KPI Dashboard
       - Formulated SQL queries and built interactive dashboards in Tableau and Power BI.

    EDUCATION
    Bachelor of Technology in AI & Data Science (2022 - 2026) | GPA: 8.9/10
    """
    
    # Insert text into page
    rect = pymupdf.Rect(50, 50, 550, 750)
    page.insert_textbox(rect, resume_text, fontsize=10, fontname="helv")
    doc.save(str(valid_pdf_path))
    doc.close()

    # 2. Empty Text PDF
    empty_pdf_path = TEST_RESUME_DIR / "sample_empty_resume.pdf"
    doc_empty = pymupdf.open()
    doc_empty.new_page()  # Page with no text
    doc_empty.save(str(empty_pdf_path))
    doc_empty.close()

    # 3. Corrupted PDF
    corrupt_pdf_path = TEST_RESUME_DIR / "sample_corrupted_resume.pdf"
    with open(corrupt_pdf_path, "wb") as f:
        f.write(b"NOT_A_VALID_PDF_HEADER_DATA_CORRUPTION_TEST")

    return valid_pdf_path, empty_pdf_path, corrupt_pdf_path


def main():
    print("=" * 80)
    print(" RESUME PDF PARSING & SKILL EXTRACTION TEST SUITE")
    print("=" * 80)
    
    valid_pdf, empty_pdf, corrupt_pdf = create_sample_pdf_fixtures()
    parser = ResumeParser()

    # -------------------------------------------------------------
    # Test 1: Valid PDF Resume Parsing
    # -------------------------------------------------------------
    print(f"\n--- Test 1: Valid Student Resume Parsing ({valid_pdf.name}) ---")
    profile = parser.parse_resume(valid_pdf)
    
    print(f"Validation Status : {'[VALID]' if profile.is_valid else '[INVALID]'}")
    print(f"Pages Parsed      : {profile.page_count}")
    print(f"Word Count        : {profile.word_count}")
    print(f"Detected Sections : {', '.join(profile.detected_sections)}")
    print(f"Extracted Skills  : ({len(profile.extracted_canonical_skills)} unique)")
    
    for i, s in enumerate(profile.extracted_canonical_skills, 1):
        print(f"  {i:2d}. {s}")

    # Assertions
    assert profile.is_valid, "Expected valid PDF parsing!"
    expected_sample_skills = [
        "Python", "SQL", "Pandas", "NumPy", "Scikit-Learn",
        "Machine Learning", "Statistics & Probability", "Tableau",
        "Power BI", "Matplotlib & Seaborn", "Excel", "Git & GitHub", "Docker"
    ]
    for exp in expected_sample_skills:
        assert exp in profile.extracted_canonical_skills, f"Expected '{exp}' to be extracted from resume!"
        
    print("[PASS] Valid PDF resume parsed and all technical competencies identified.")

    # -------------------------------------------------------------
    # Test 2: Empty PDF Document Handling
    # -------------------------------------------------------------
    print(f"\n--- Test 2: Empty PDF Handling ({empty_pdf.name}) ---")
    empty_profile = parser.parse_resume(empty_pdf)
    print(f"Validation Status : {'[VALID]' if empty_profile.is_valid else '[INVALID]'}")
    print(f"Warning / Notice  : {empty_profile.error_message}")
    assert empty_profile.error_message is not None, "Expected warning for empty/scanned PDF!"
    print("[PASS] Empty PDF caught gracefully with informative warning.")

    # -------------------------------------------------------------
    # Test 3: Corrupted PDF File Handling
    # -------------------------------------------------------------
    print(f"\n--- Test 3: Corrupted PDF File Handling ({corrupt_pdf.name}) ---")
    corrupt_profile = parser.parse_resume(corrupt_pdf)
    print(f"Validation Status : {'[VALID]' if corrupt_profile.is_valid else '[INVALID]'}")
    print(f"Caught Error      : {corrupt_profile.error_message}")
    assert not corrupt_profile.is_valid, "Expected corrupt file to be marked invalid!"
    print("[PASS] Corrupted non-PDF file rejected gracefully without crash.")

    print("\n" + "=" * 80)
    print(" ALL RESUME PARSER & EXTRACTION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    main()
