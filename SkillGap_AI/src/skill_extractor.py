"""
NLP-Based Natural Language Skill Extractor Module
Phase 10: NLP-Based Skill Extraction

Extracts canonical skills from free-form natural-language sentences,
paragraphs, and resume blurbs using sliding-window n-gram matching,
tokenization, alias dictionaries, and negation filtering.
"""

from dataclasses import dataclass
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import pandas as pd

from data_loader import DataLoader
from preprocessing import SkillPreprocessor


@dataclass
class ExtractedSkillEntity:
    """Represents an extracted skill entity with metadata."""
    canonical_name: str
    matched_text: str
    category: str
    difficulty_level: str
    start_char: int
    end_char: int
    is_negated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "canonical_name": self.canonical_name,
            "matched_text": self.matched_text,
            "category": self.category,
            "difficulty_level": self.difficulty_level,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "is_negated": self.is_negated
        }


class NLPSkillExtractor:
    """
    Extracts canonical skill entities from arbitrary natural language text.
    """

    # Negation trigger patterns (e.g., "don't know", "no experience with", "lack")
    NEGATION_PATTERNS = [
        r"\b(?:don't|do not|haven't|have not|no|not|never|lack|lacking|without|unfamiliar with|zero experience in)\s+(?:know|have|use|experience|proficiency|skills?\s+in)?\s*[:\w\s,]*",
    ]

    def __init__(
        self,
        data_loader: Optional[DataLoader] = None,
        preprocessor: Optional[SkillPreprocessor] = None
    ):
        self.loader = data_loader if data_loader else DataLoader()
        self.preprocessor = preprocessor if preprocessor else SkillPreprocessor(data_loader=self.loader)
        self._build_extraction_index()

    def _build_extraction_index(self):
        """
        Builds a high-speed token and phrase extraction index mapping
        lowercased keywords, phrases, and aliases to canonical skills.
        """
        self.phrase_to_canonical: Dict[str, str] = {}
        
        # 1. Add canonical names
        for _, row in self.loader.skills.iterrows():
            cname = row["skill_name"]
            cleaned_c = self.preprocessor.clean_string(cname)
            self.phrase_to_canonical[cleaned_c] = cname
            
            # If canonical has parentheses (e.g. "Natural Language Processing (NLP)")
            # also index base name and acronym separately
            if "(" in cname and ")" in cname:
                base = re.sub(r"\(.*?\)", "", cname).strip().lower()
                acronym = re.search(r"\((.*?)\)", cname).group(1).strip().lower()
                self.phrase_to_canonical[base] = cname
                self.phrase_to_canonical[acronym] = cname

        # 2. Add all aliases from preprocessor dictionary
        for alias, cname in self.preprocessor.DEFAULT_ALIAS_MAP.items():
            self.phrase_to_canonical[alias.lower().strip()] = cname

        # 3. Sort phrases by length descending (longest-match first greedy strategy)
        self.sorted_phrases = sorted(self.phrase_to_canonical.keys(), key=len, reverse=True)

        # 4. Map canonical name to full metadata
        self.skill_metadata = {}
        for _, row in self.loader.skills.iterrows():
            self.skill_metadata[row["skill_name"]] = {
                "category": row["category"],
                "difficulty_level": row["difficulty_level"],
                "skill_id": row["skill_id"]
            }

    def _detect_negated_spans(self, text: str) -> List[Tuple[int, int]]:
        """Finds character spans in text that are governed by negation cues."""
        negated_spans = []
        lower_text = text.lower()
        
        # Common negation patterns: "don't know X", "no experience in X", "haven't learned X"
        for match in re.finditer(r"\b(?:don't know|do not know|no experience (?:in|with)|haven't used|not familiar with|lack|lacking|unfamiliar with)\b([^.?!;]+)", lower_text):
            start = match.start()
            end = match.end()
            negated_spans.append((start, end))
            
        return negated_spans

    def extract_skills(
        self,
        text: str,
        include_negated: bool = False
    ) -> List[ExtractedSkillEntity]:
        """
        Extracts all canonical skills from natural language text using greedy multi-word phrase matching.

        Args:
            text: Raw natural language input (sentence, paragraph, bio).
            include_negated: If False, filters out negated skills (e.g. "I don't know Docker").

        Returns:
            List of ExtractedSkillEntity objects with character offsets and metadata.
        """
        if not text or not isinstance(text, str):
            return []

        negated_spans = self._detect_negated_spans(text)
        extracted: List[ExtractedSkillEntity] = []
        occupied_spans: List[Tuple[int, int]] = []
        extracted_canonicals: Set[str] = set()

        lower_text = text.lower()

        # Greedy Longest-Match First
        for phrase in self.sorted_phrases:
            canonical = self.phrase_to_canonical[phrase]
            
            # Construct word-boundary regex pattern
            escaped_phrase = re.escape(phrase)
            # Handle special symbols like &, +, / in boundary regex
            pattern = rf"(?<!\w){escaped_phrase}(?!\w)"
            
            for match in re.finditer(pattern, lower_text):
                start, end = match.span()

                # Check if this character span overlaps with an already matched longer phrase
                is_overlapping = any(
                    (start >= o_start and start < o_end) or (end > o_start and end <= o_end)
                    for o_start, o_end in occupied_spans
                )
                
                if is_overlapping:
                    continue

                # Check if this occurrence falls inside a negation scope
                is_negated = any(
                    start >= n_start and end <= n_end
                    for n_start, n_end in negated_spans
                )

                if is_negated and not include_negated:
                    continue

                if canonical not in extracted_canonicals or is_negated:
                    meta = self.skill_metadata.get(canonical, {"category": "General", "difficulty_level": "Intermediate"})
                    
                    entity = ExtractedSkillEntity(
                        canonical_name=canonical,
                        matched_text=text[start:end],
                        category=meta["category"],
                        difficulty_level=meta["difficulty_level"],
                        start_char=start,
                        end_char=end,
                        is_negated=is_negated
                    )
                    extracted.append(entity)
                    occupied_spans.append((start, end))
                    extracted_canonicals.add(canonical)

        # Sort extracted skills by their order of appearance in the text
        extracted.sort(key=lambda e: e.start_char)
        return extracted

    def extract_canonical_names(self, text: str) -> List[str]:
        """
        Convenience method: Returns a clean list of canonical skill names extracted from text.
        """
        entities = self.extract_skills(text, include_negated=False)
        return [e.canonical_name for e in entities]
