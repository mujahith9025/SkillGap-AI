"""
Test Runner for NLP-Based Natural Language Skill Extractor
Phase 10: NLP-Based Skill Extraction

Tests:
- Extraction from unstructured sentences and paragraphs
- Multi-word entity boundary resolution (Machine Learning vs Learning)
- Canonical resolution of aliases in conversational text
- Negation detection and filtering ("I don't know Django")
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from skill_extractor import NLPSkillExtractor

def main():
    print("=" * 75)
    print(" NLP-BASED SKILL EXTRACTOR - TEST RUNNER")
    print("=" * 75)
    
    extractor = NLPSkillExtractor()

    test_sentences = [
        # (Sentence, Expected Skills, Description)
        (
            "I know Python, Pandas, SQL and basic machine learning.",
            ["Python", "Pandas", "SQL", "Machine Learning"],
            "Standard conversational skill summary"
        ),
        (
            "I am proficient in Data Visualization using Tableau and Power BI, along with MS Excel.",
            ["Data Visualization", "Tableau", "Power BI", "Excel"],
            "BI and analytics skill phrase"
        ),
        (
            "Currently learning deep-learning with PyTorch and building REST APIs with FastAPI and Docker.",
            ["Deep Learning", "PyTorch", "RESTful APIs", "FastAPI", "Docker"],
            "Engineering stack with hyphenated & compound terms"
        ),
        (
            "My background is in Statistics & Probability and Scikit-Learn for classical ml, but I don't know Django or Spark.",
            ["Statistics & Probability", "Scikit-Learn", "Machine Learning"],
            "Sentence containing positive skills + explicit negation (don't know Django/Spark)"
        ),
        (
            "Experienced with Git/GitHub, AWS cloud fundamentals, and postgresql database design.",
            ["Git & GitHub", "Cloud Fundamentals (AWS/GCP)", "SQL", "Relational Database Design"],
            "Aliases and cloud/database dialects"
        )
    ]

    all_passed = True

    for idx, (sentence, expected, desc) in enumerate(test_sentences, 1):
        print(f"\n--- Test {idx}: {desc} ---")
        print(f"Input Sentence:\n  \"{sentence}\"")
        
        entities = extractor.extract_skills(sentence, include_negated=False)
        extracted_names = [e.canonical_name for e in entities]
        
        print("\nExtracted Entities:")
        for e in entities:
            print(f"  * Matched: '{e.matched_text}' [{e.start_char}:{e.end_char}] -> Canonical: {e.canonical_name} ({e.category})")
            
        print(f"Result List: {extracted_names}")
        print(f"Expected   : {expected}")
        
        # Check that all expected skills are present
        missing = set(expected) - set(extracted_names)
        if not missing:
            print("[PASS] All expected skills accurately extracted.")
        else:
            print(f"[FAIL] Missing expected skills: {missing}")
            all_passed = False

    # Check Negation Extraction explicit flag
    print("\n" + "=" * 75)
    print("--- Negation Detection Inspection ---")
    neg_sentence = "I know Python and SQL, but have no experience in Docker or PyTorch."
    print(f"Input: \"{neg_sentence}\"")
    all_entities = extractor.extract_skills(neg_sentence, include_negated=True)
    for e in all_entities:
        status = "[NEGATED]" if e.is_negated else "[ACTIVE]"
        print(f"  {status:10} {e.canonical_name:<20} (Matched: '{e.matched_text}')")
        
    active_only = extractor.extract_canonical_names(neg_sentence)
    assert "Python" in active_only and "SQL" in active_only
    assert "Docker" not in active_only and "PyTorch" not in active_only
    print("[PASS] Negated skills correctly excluded from active profile.")

    print("\n" + "=" * 75)
    if all_passed:
        print(" ALL NLP SKILL EXTRACTION TESTS COMPLETED SUCCESSFULLY!")
    else:
        print(" SOME EXTRACTION TESTS FAILED. CHECK LOGS ABOVE.")
    print("=" * 75)

if __name__ == "__main__":
    main()
