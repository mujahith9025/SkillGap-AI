"""
Resume PDF Parser & Automatic Skill Extractor Module
Phase 12: Resume Upload and Skill Extraction

Provides robust PDF text extraction via PyMuPDF (fitz), section segmentation,
edge-case handling (empty/corrupted/scanned PDFs), and skill entity identification.
"""

from collections import defaultdict
from dataclasses import dataclass, field
import io
import os
from pathlib import Path
import re
from typing import Any, BinaryIO, Dict, List, Optional, Set, Tuple, Union
import pymupdf  # Modern PyMuPDF API

from data_loader import DataLoader
from preprocessing import SkillPreprocessor
from skill_extractor import NLPSkillExtractor, ExtractedSkillEntity


class ResumeParsingError(Exception):
    """Custom exception raised when a PDF resume fails validation or parsing."""
    pass


@dataclass
class ResumeSkillProfile:
    """Encapsulates the parsed skill profile extracted from a student's resume."""
    filename: str
    is_valid: bool
    page_count: int
    character_count: int
    word_count: int
    detected_sections: List[str]
    extracted_canonical_skills: List[str]
    skill_entities: List[ExtractedSkillEntity]
    text_preview: str
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filename": self.filename,
            "is_valid": self.is_valid,
            "page_count": self.page_count,
            "word_count": self.word_count,
            "detected_sections": self.detected_sections,
            "extracted_skills": self.extracted_canonical_skills,
            "skill_count": len(self.extracted_canonical_skills),
            "text_preview": self.text_preview,
            "error_message": self.error_message
        }


class ResumeParser:
    """
    Parses PDF resumes, extracts text content, detects document sections,
    and identifies student technical competencies using NLP.
    """

    # Common section header patterns in technical resumes
    SECTION_HEADERS = {
        "skills": r"\b(?:technical skills|skills & expertise|core competencies|skills|technologies|tools & technologies)\b",
        "experience": r"\b(?:work experience|experience|employment history|internships|professional experience)\b",
        "projects": r"\b(?:academic projects|projects|personal projects|key projects)\b",
        "education": r"\b(?:education|academic background|qualifications)\b",
        "certifications": r"\b(?:certifications|courses & certifications|achievements)\b"
    }

    def __init__(
        self,
        data_loader: Optional[DataLoader] = None,
        skill_extractor: Optional[NLPSkillExtractor] = None
    ):
        self.loader = data_loader if data_loader else DataLoader()
        self.extractor = skill_extractor if skill_extractor else NLPSkillExtractor(data_loader=self.loader)

    def extract_text(
        self,
        pdf_input: Union[str, Path, bytes, BinaryIO]
    ) -> Tuple[str, int, Optional[str]]:
        """
        Extracts clean text from a PDF file path or raw bytes buffer.

        Returns:
            Tuple of (extracted_text, page_count, error_message_or_None)
        """
        doc = None
        try:
            if isinstance(pdf_input, (str, Path)):
                path = Path(pdf_input)
                if not path.exists():
                    return "", 0, f"File does not exist: {path}"
                if path.stat().st_size == 0:
                    return "", 0, "PDF file is empty (0 bytes)."
                doc = pymupdf.open(str(path))
            elif isinstance(pdf_input, bytes):
                if len(pdf_input) == 0:
                    return "", 0, "PDF byte buffer is empty (0 bytes)."
                doc = pymupdf.open(stream=pdf_input, filetype="pdf")
            elif hasattr(pdf_input, "read"):
                content = pdf_input.read()
                if len(content) == 0:
                    return "", 0, "Uploaded file stream is empty (0 bytes)."
                doc = pymupdf.open(stream=content, filetype="pdf")
            else:
                return "", 0, "Unsupported PDF input type."

            page_count = len(doc)
            if page_count == 0:
                return "", 0, "PDF document contains 0 pages."

            text_parts = []
            for page_num in range(page_count):
                page = doc[page_num]
                page_text = page.get_text("text")
                if page_text:
                    text_parts.append(page_text)

            full_text = "\n".join(text_parts).strip()
            
            # Check for scanned / image-only PDFs with no extractable text layer
            word_count = len(full_text.split())
            if word_count < 10:
                return full_text, page_count, (
                    "Warning: PDF appears to be a scanned image or contains insufficient extractable text. "
                    "Please ensure the PDF has selectable text."
                )

            return full_text, page_count, None

        except Exception as e:
            return "", 0, f"Failed to parse PDF: {str(e)}"
        finally:
            if doc:
                doc.close()

    def segment_sections(self, text: str) -> Dict[str, str]:
        """
        Segments raw resume text into logical sections based on common headings.
        """
        sections: Dict[str, str] = {}
        lines = text.split("\n")
        
        current_section = "general"
        section_lines = defaultdict(list)
        
        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue
            
            # Check if this line looks like a major section header
            matched_header = None
            if len(trimmed.split()) <= 4:
                for sec_name, pattern in self.SECTION_HEADERS.items():
                    if re.search(pattern, trimmed, flags=re.IGNORECASE):
                        matched_header = sec_name
                        break
            
            if matched_header:
                current_section = matched_header
            else:
                section_lines[current_section].append(trimmed)

        for sec, lns in section_lines.items():
            sections[sec] = "\n".join(lns)

        return sections

    def parse_resume(
        self,
        pdf_input: Union[str, Path, bytes, BinaryIO],
        filename: str = "uploaded_resume.pdf"
    ) -> ResumeSkillProfile:
        """
        End-to-end pipeline: Extracts text, isolates sections, and extracts student skill profile.
        """
        if isinstance(pdf_input, (str, Path)):
            filename = Path(pdf_input).name

        raw_text, page_count, error = self.extract_text(pdf_input)

        if error and not raw_text:
            return ResumeSkillProfile(
                filename=filename,
                is_valid=False,
                page_count=page_count,
                character_count=0,
                word_count=0,
                detected_sections=[],
                extracted_canonical_skills=[],
                skill_entities=[],
                text_preview="",
                error_message=error
            )

        # Segment text into sections
        sections = self.segment_sections(raw_text)
        detected_sections = [s for s in sections.keys() if s != "general"]

        # Extract skills using NLP Skill Extractor
        # We pass both the dedicated skills section (high confidence) and full text
        extracted_entities = self.extractor.extract_skills(raw_text, include_negated=False)
        
        # Deduplicate canonical skill names preserving order of appearance
        canonical_list = []
        seen = set()
        for entity in extracted_entities:
            if entity.canonical_name not in seen:
                seen.add(entity.canonical_name)
                canonical_list.append(entity.canonical_name)

        preview = raw_text[:250].replace("\n", " ").strip() + "..." if len(raw_text) > 250 else raw_text

        return ResumeSkillProfile(
            filename=filename,
            is_valid=True,
            page_count=page_count,
            character_count=len(raw_text),
            word_count=len(raw_text.split()),
            detected_sections=detected_sections,
            extracted_canonical_skills=canonical_list,
            skill_entities=extracted_entities,
            text_preview=preview,
            error_message=error
        )
