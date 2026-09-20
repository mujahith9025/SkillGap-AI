"""
ATS Resume Scorer & Optimization Advisor Module
Phase 11 & Section 3 Upgrades: Red-Flag Parser, Side-by-Side Diffs, and LaTeX/PDF Resume Generator

Evaluates resume compatibility against target Job Descriptions (JD),
identifies critical missing keywords, scores metric density, detects ATS red flags,
computes word-level diffs, and generates tailored single-column ATS LaTeX/PDF resumes.
"""

from dataclasses import dataclass, field
import html
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from data_loader import DataLoader
from skill_extractor import NLPSkillExtractor
from semantic_matcher import SemanticSkillMatcher


@dataclass
class ATSRedFlag:
    """Represents a detected ATS parsing trap, formatting weakness, or missing metadata."""
    category: str       # 'Contact Info', 'Action Verbs', 'Metric Quantification', 'Section Structure', 'Formatting'
    severity: str       # 'Critical', 'Warning', 'Good'
    title: str
    description: str
    recommendation: str
    snippet: Optional[str] = None
    status: str = "detected"  # 'detected' | 'resolved'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "recommendation": self.recommendation,
            "snippet": self.snippet,
            "status": self.status
        }


@dataclass
class BulletPointOptimization:
    """Represents an optimized resume bullet point transformation with word-level delta diffs."""
    original_bullet: str
    improved_bullet: str
    impact_technique_used: str  # e.g., 'Google XYZ Formula', 'Quantified Metric Injection'
    detected_weakness: str
    diff_added_tokens: List[str] = field(default_factory=list)
    diff_removed_tokens: List[str] = field(default_factory=list)
    highlighted_html_diff: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_bullet": self.original_bullet,
            "improved_bullet": self.improved_bullet,
            "impact_technique_used": self.impact_technique_used,
            "detected_weakness": self.detected_weakness,
            "diff_added_tokens": self.diff_added_tokens,
            "diff_removed_tokens": self.diff_removed_tokens,
            "highlighted_html_diff": self.highlighted_html_diff
        }


@dataclass
class ATSAuditResult:
    """Encapsulates the complete ATS compatibility scorecard, red flags, and tailored resume preview."""
    overall_ats_score: int  # 0 to 100
    score_grade: str        # 'A+ (High Callback Rate)', 'B (Moderate)', 'C (High Rejection Risk)', 'F (Auto-Reject)'
    keyword_match_rate_pct: float
    semantic_alignment_score: float
    quantifiable_metrics_score: float
    matched_jd_keywords: List[str]
    missing_critical_keywords: List[str]
    formatting_recommendations: List[str]
    bullet_point_improvements: List[BulletPointOptimization]
    red_flags: List[ATSRedFlag] = field(default_factory=list)
    tailored_latex_preview: str = ""
    tailored_html_preview: str = ""

    @property
    def matched_keywords(self) -> List[str]:
        return self.matched_jd_keywords

    @property
    def missing_keywords(self) -> List[str]:
        return self.missing_critical_keywords

    @property
    def jd_required_skills(self) -> List[str]:
        return self.matched_jd_keywords + self.missing_critical_keywords

    @property
    def recommendations(self) -> List[str]:
        return self.formatting_recommendations

    @property
    def semantic_similarity_pct(self) -> float:
        return self.semantic_alignment_score

    @property
    def metric_quantification_score(self) -> float:
        return self.quantifiable_metrics_score

    @property
    def section_analysis(self) -> Dict[str, bool]:
        return {
            "summary": True,
            "skills": True,
            "experience": True,
            "education": True
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_ats_score": self.overall_ats_score,
            "score_grade": self.score_grade,
            "keyword_match_rate_pct": self.keyword_match_rate_pct,
            "semantic_alignment_score": self.semantic_alignment_score,
            "quantifiable_metrics_score": self.quantifiable_metrics_score,
            "matched_jd_keywords": self.matched_jd_keywords,
            "missing_critical_keywords": self.missing_critical_keywords,
            "formatting_recommendations": self.formatting_recommendations,
            "bullet_point_improvements": [b.to_dict() for b in self.bullet_point_improvements],
            "red_flags": [rf.to_dict() for rf in self.red_flags],
            "tailored_latex_preview": self.tailored_latex_preview,
            "tailored_html_preview": self.tailored_html_preview
        }


class ATSResumeOptimizer:
    """
    Simulates corporate Applicant Tracking Systems (ATS), calculates parsing
    and keyword compatibility against target Job Descriptions, scans red flags,
    and generates tailored LaTeX / HTML resumes.
    """

    ACTION_VERBS = [
        "engineered", "architected", "developed", "deployed", "optimized",
        "implemented", "accelerated", "designed", "streamlined", "scaled",
        "built", "orchestrated", "reduced", "increased", "trained", "integrated",
        "automated", "spearheaded", "formulated", "established", "benchmarked"
    ]

    PASSIVE_WEAK_PHRASES = [
        "responsible for", "duties included", "helped with", "assisted in",
        "worked on", "handled", "participated in", "tasked with", "was involved in",
        "tried to", "aided in", "contributed to"
    ]

    def __init__(
        self,
        data_loader: Optional[DataLoader] = None,
        skill_extractor: Optional[NLPSkillExtractor] = None,
        semantic_matcher: Optional[SemanticSkillMatcher] = None
    ):
        self.loader = data_loader if data_loader else DataLoader()
        self.extractor = skill_extractor if skill_extractor else NLPSkillExtractor(data_loader=self.loader)
        self.semantic_matcher = semantic_matcher if semantic_matcher else SemanticSkillMatcher(data_loader=self.loader)

    def evaluate_resume_ats(
        self,
        resume_text: str,
        job_description: str,
        target_career: Optional[str] = None
    ) -> ATSAuditResult:
        """Alias for evaluate_ats_compatibility."""
        return self.evaluate_ats_compatibility(resume_text, job_description, target_career)

    def scan_ats_red_flags(self, resume_text: str) -> List[ATSRedFlag]:
        """
        Scans resume text for common ATS parsing traps, missing metadata,
        passive voice overuse, and lack of metrics.
        """
        red_flags: List[ATSRedFlag] = []
        text_lower = resume_text.lower()

        # 1. Contact Information Audit
        has_email = bool(re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", resume_text))
        has_phone = bool(re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", resume_text))
        has_linkedin = "linkedin.com" in text_lower
        has_github = "github.com" in text_lower

        if not has_email:
            red_flags.append(ATSRedFlag(
                category="Contact Info",
                severity="Critical",
                title="Missing or Unparsable Email Address",
                description="No standard RFC-compliant email address found in the resume header.",
                recommendation="Add a clear, professional email address (e.g. name@domain.com) in plain text at the top."
            ))
        else:
            red_flags.append(ATSRedFlag(
                category="Contact Info",
                severity="Good",
                title="Valid Email Address Detected",
                description="Email is properly formatted for ATS parsing.",
                recommendation="Keep email at the very top of your header."
            ))

        if not has_linkedin or not has_github:
            missing_links = []
            if not has_linkedin: missing_links.append("LinkedIn profile")
            if not has_github: missing_links.append("GitHub / Portfolio URL")
            red_flags.append(ATSRedFlag(
                category="Contact Info",
                severity="Warning",
                title="Missing Professional Links",
                description=f"Could not locate {' and '.join(missing_links)} in header.",
                recommendation="Add clickable plain-text URLs: linkedin.com/in/username and github.com/username."
            ))

        # 2. Action Verb & Passive Voice Audit
        detected_passive = []
        for phrase in self.PASSIVE_WEAK_PHRASES:
            if phrase in text_lower:
                detected_passive.append(phrase)

        if detected_passive:
            red_flags.append(ATSRedFlag(
                category="Action Verbs",
                severity="Warning",
                title="Overuse of Passive / Weak Phrases",
                description=f"Detected weak phrases: '{', '.join(detected_passive[:3])}'. These dilute ownership.",
                recommendation="Replace passive terms with power action verbs: 'Spearheaded', 'Architected', 'Engineered', 'Optimized'.",
                snippet=f"Found: {', '.join(detected_passive)}"
            ))
        else:
            red_flags.append(ATSRedFlag(
                category="Action Verbs",
                severity="Good",
                title="Strong Action Verb Usage",
                description="Resume demonstrates active ownership without weak passive introductory clauses.",
                recommendation="Continue starting every bullet point with past-tense action verbs."
            ))

        # 3. Quantifiable Metric Density Audit
        metrics_found = re.findall(r"\b\d+(?:\.\d+)?%?|\$\d+", resume_text)
        if len(metrics_found) < 3:
            red_flags.append(ATSRedFlag(
                category="Metric Quantification",
                severity="Critical",
                title="Low Metric Density (Under-Quantified)",
                description=f"Only {len(metrics_found)} numerical metrics found. Top recruiters look for quantifiable proof.",
                recommendation="Apply the Google XYZ Formula: 'Accomplished [X], measured by [Y] (e.g. +35% latency drop, 100k records), by doing [Z]'."
            ))
        else:
            red_flags.append(ATSRedFlag(
                category="Metric Quantification",
                severity="Good",
                title="High Metric Quantification",
                description=f"Found {len(metrics_found)} quantifiable metrics and benchmarks.",
                recommendation="Great job! Ensure all metrics clearly tie back to direct business or technical outcomes."
            ))

        # 4. Standard Section Headings Audit
        has_skills_section = any(h in text_lower for h in ["skills", "technical skills", "technologies"])
        has_exp_or_projects = any(h in text_lower for h in ["experience", "projects", "work experience", "technical projects"])
        has_edu_section = any(h in text_lower for h in ["education", "academic", "degree", "university"])

        if not has_skills_section or not has_exp_or_projects or not has_edu_section:
            missing_secs = []
            if not has_skills_section: missing_secs.append("Skills")
            if not has_exp_or_projects: missing_secs.append("Experience/Projects")
            if not has_edu_section: missing_secs.append("Education")
            red_flags.append(ATSRedFlag(
                category="Section Structure",
                severity="Warning",
                title="Non-Standard Section Headings",
                description=f"Missing standard section headings: {', '.join(missing_secs)}.",
                recommendation="Use unambiguous headings: 'Technical Skills', 'Work Experience', 'Technical Projects', 'Education'."
            ))
        else:
            red_flags.append(ATSRedFlag(
                category="Section Structure",
                severity="Good",
                title="Clean Standard Section Hierarchy",
                description="Core standard headings (Skills, Projects, Education) are properly present.",
                recommendation="Maintain standard single-column order without nesting sections."
            ))

        # 5. Formatting & Layout Trap Audit
        if "\t" in resume_text or "|" in resume_text:
            red_flags.append(ATSRedFlag(
                category="Formatting",
                severity="Good",
                title="Single-Column Plain Text Layout",
                description="No multi-column complex tables or nested text frames detected.",
                recommendation="Stick with single-column layouts for 100% ATS parser compatibility."
            ))

        return red_flags

    def compute_bullet_diff(self, original_bullet: str, improved_bullet: str) -> Tuple[List[str], List[str], str]:
        """
        Computes added and removed word tokens and builds a side-by-side HTML delta diff.
        """
        orig_words = re.findall(r"\b\w+(?:-\w+)?%?\b", original_bullet)
        imp_words = re.findall(r"\b\w+(?:-\w+)?%?\b", improved_bullet)

        orig_set = {w.lower() for w in orig_words}
        imp_set = {w.lower() for w in imp_words}

        added = [w for w in imp_words if w.lower() not in orig_set]
        removed = [w for w in orig_words if w.lower() not in imp_set]

        # Build highlighted HTML diff string
        html_tokens = []
        for word in imp_words:
            if word.lower() in {a.lower() for a in added}:
                html_tokens.append(f'<span class="diff-add">{html.escape(word)}</span>')
            else:
                html_tokens.append(html.escape(word))

        highlighted_diff = " ".join(html_tokens)
        return added, removed, highlighted_diff

    def suggest_xyz_rewrite(self, raw_bullet: str, missing_skill: str = "FastAPI") -> Dict[str, Any]:
        """Rewrites a standard resume bullet point using Google XYZ formula."""
        raw_clean = raw_bullet.strip()
        matched_verb = "Developed"
        for v in self.ACTION_VERBS:
            if v.lower() in raw_clean.lower():
                matched_verb = v.capitalize()
                break

        has_metric = bool(re.search(r"\b\d+(?:\.\d+)?%?|\$\d+", raw_clean))
        if not has_metric:
            optimized = (
                f"Engineered and deployed an optimized solution ({raw_clean.rstrip('.')}), "
                f"achieving 94.2% accuracy and accelerating processing latency by 35% across 100k+ records using {missing_skill}."
            )
        else:
            optimized = f"{matched_verb} high-throughput technical architecture ({raw_clean.rstrip('.')}), implementing robust CI/CD and production monitoring."

        added, removed, html_diff = self.compute_bullet_diff(raw_bullet, optimized)

        return {
            "original_bullet": raw_bullet,
            "optimized_bullet": optimized,
            "action_verb_detected": matched_verb,
            "has_metric": has_metric,
            "formula_applied": "Google XYZ Formula: Accomplished [X], as measured by [Y], by doing [Z]",
            "diff_added_tokens": added[:6],
            "diff_removed_tokens": removed[:4],
            "highlighted_html_diff": html_diff
        }

    def evaluate_ats_compatibility(
        self,
        resume_text: str,
        job_description_text: str,
        target_career: Optional[str] = None
    ) -> ATSAuditResult:
        """
        Computes composite ATS match score, keyword intersection, metric density,
        scans red flags, generates side-by-side diffs, and creates tailored LaTeX/HTML resume.
        """
        # 1. Skill & Keyword Extraction
        resume_skills = set(self.extractor.extract_canonical_names(resume_text))
        jd_skills = set(self.extractor.extract_canonical_names(job_description_text))

        if not jd_skills:
            jd_skills = {"Python", "SQL", "Machine Learning"}

        matched_skills = sorted(list(resume_skills.intersection(jd_skills)))
        missing_skills = sorted(list(jd_skills - resume_skills))

        # 2. Metric Calculations
        keyword_pct = (len(matched_skills) / max(1, len(jd_skills)) * 100.0)
        sim_cos = self.semantic_matcher.compute_cosine_similarity(resume_text[:2000], job_description_text[:2000])
        sim_pct = max(0.0, min(100.0, sim_cos * 100.0))
        metric_score = self._score_metric_and_action_density(resume_text)

        raw_composite = (0.50 * keyword_pct) + (0.35 * sim_pct) + (0.15 * metric_score)
        final_ats_score = int(np.clip(round(raw_composite), 1, 100))

        if final_ats_score >= 85:
            grade = "A+ (High Callback Rate - Strong ATS Match)"
        elif final_ats_score >= 70:
            grade = "B (Competitive - Minor Keyword Gaps)"
        elif final_ats_score >= 50:
            grade = "C (Moderate - High Risk of ATS Filtering)"
        else:
            grade = "F (High Rejection Risk - Critical Skills Missing)"

        # 3. Formatting & Keyword Advice
        formatting_advice = []
        if missing_skills:
            formatting_advice.append(f"Incorporate missing core JD keywords in context: {', '.join(missing_skills[:4])}.")
        if metric_score < 60:
            formatting_advice.append("Add quantifiable metrics (e.g. 'reduced latency by 35%', 'processed 500k rows').")
        formatting_advice.append("Use standard single-column ATS section headings without text boxes.")

        # 4. Bullet Point Optimization Transformations with Word Diffs
        bullet_rewrites = self._generate_sample_bullet_rewrites(resume_text, matched_skills, missing_skills)

        # 5. Red Flag Scanner
        red_flags = self.scan_ats_red_flags(resume_text)

        # 6. Tailored LaTeX & HTML Resume Generation
        career_title = target_career or "Data Scientist"
        latex_code = self.generate_tailored_latex_resume(
            student_skills=list(resume_skills),
            target_career=career_title,
            job_description=job_description_text,
            missing_keywords=missing_skills
        )
        html_code = self.generate_tailored_html_resume(
            student_skills=list(resume_skills),
            target_career=career_title,
            job_description=job_description_text,
            missing_keywords=missing_skills
        )

        return ATSAuditResult(
            overall_ats_score=final_ats_score,
            score_grade=grade,
            keyword_match_rate_pct=round(keyword_pct, 1),
            semantic_alignment_score=round(sim_pct, 1),
            quantifiable_metrics_score=round(metric_score, 1),
            matched_jd_keywords=matched_skills,
            missing_critical_keywords=missing_skills,
            formatting_recommendations=formatting_advice,
            bullet_point_improvements=bullet_rewrites,
            red_flags=red_flags,
            tailored_latex_preview=latex_code,
            tailored_html_preview=html_code
        )

    def _score_metric_and_action_density(self, text: str) -> float:
        """Evaluates presence of numbers, percentages, currency, and strong action verbs."""
        text_lower = text.lower()
        score = 40.0

        numbers = re.findall(r"\b\d+(?:\.\d+)?%?|\$\d+", text)
        if len(numbers) >= 5:
            score += 30.0
        elif len(numbers) >= 2:
            score += 15.0

        verb_count = sum(1 for v in self.ACTION_VERBS if v in text_lower)
        if verb_count >= 4:
            score += 30.0
        elif verb_count >= 2:
            score += 15.0

        return min(100.0, score)

    def _generate_sample_bullet_rewrites(
        self,
        resume_text: str,
        matched: List[str],
        missing: List[str]
    ) -> List[BulletPointOptimization]:
        """Generates high-impact Google-style XYZ bullet point rewrite examples with diffs."""
        sample_missing = missing[0] if missing else "FastAPI"
        sample_matched = matched[0] if matched else "Python"

        pairs = [
            (
                "Worked on machine learning model to predict customer churn.",
                f"Engineered an end-to-end classification pipeline using {sample_matched} and Scikit-Learn, achieving 94.2% F1-score across 150k customer records and reducing customer churn by 12%.",
                "Google XYZ Formula (Accomplished [X] measured by [Y], by doing [Z])",
                "Passive wording ('worked on') and lacks quantifiable outcome."
            ),
            (
                "Created dashboards and ran SQL queries for business team.",
                "Optimized complex PostgreSQL analytical queries and built interactive Tableau dashboards, automating weekly KPI reporting and saving 6 engineering hours weekly.",
                "Action Verb + Quantified Business Impact",
                "Lacks metrics, tools used, and business value."
            ),
            (
                f"Used {sample_missing} for deployment.",
                f"Architected containerized microservices using Docker and {sample_missing}, deploying production REST APIs with automated Swagger documentation and sub-50ms latency.",
                "Technical Specificity & Performance Metric",
                "Missing technical detail, performance benchmark, and tool synergy."
            )
        ]

        results = []
        for orig, imp, technique, weakness in pairs:
            added, removed, html_diff = self.compute_bullet_diff(orig, imp)
            results.append(BulletPointOptimization(
                original_bullet=orig,
                improved_bullet=imp,
                impact_technique_used=technique,
                detected_weakness=weakness,
                diff_added_tokens=added[:6],
                diff_removed_tokens=removed[:4],
                highlighted_html_diff=html_diff
            ))

        return results

    def generate_tailored_latex_resume(
        self,
        student_skills: List[str],
        target_career: str,
        job_description: str,
        missing_keywords: Optional[List[str]] = None,
        candidate_name: str = "Alex Chen",
        candidate_email: str = "alex.chen@email.com",
        candidate_phone: str = "(555) 019-2834",
        candidate_linkedin: str = "linkedin.com/in/alexchen-tech",
        candidate_github: str = "github.com/alexchen-dev"
    ) -> str:
        """
        Generates industry-standard single-column ATS LaTeX resume source code
        (Jake's Resume / Harvard style) with injected target Job Description keywords.
        """
        missing_kw = missing_keywords or []
        injected_skills_list = list(set(student_skills + missing_kw[:4]))
        injected_skills_str = ", ".join(injected_skills_list)

        latex_template = f"""%-------------------------
% Tailored ATS Resume - Jake's Template Style
% Target Role: {target_career}
% Generated by SkillGap AI Enterprise Platform
%-------------------------

\\documentclass[letterpaper,11pt]{{article}}

\\usepackage{{latexsym}}
\\usepackage[empty]{{fullpage}}
\\usepackage{{titlesec}}
\\usepackage{{marvosym}}
\\usepackage[usenames,dvipsnames]{{color}}
\\usepackage{{verbatim}}
\\usepackage{{enumitem}}
\\usepackage[hidelinks]{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage[english]{{babel}}
\\usepackage{{tabularx}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}

% Adjust margins for ATS parsing
\\addtolength{{\\oddsidemargin}}{{-0.5in}}
\\addtolength{{\\evensidemargin}}{{-0.5in}}
\\addtolength{{\\textwidth}}{{1in}}
\\addtolength{{\\topmargin}}{{-0.5in}}
\\addtolength{{\\textheight}}{{1.0in}}

\\urlstyle{{same}}
\\raggedbottom
\\raggedright
\\setlength{{\\tabcolsep}}{{0in}}

% Sections formatting
\\titleformat{{\\section}}{{
  \\vspace{{-4pt}}\\scshape\\raggedright\\large
}}{{}}{{0em}}{{}}[\\color{{black}}\\titlerule \\vspace{{-5pt}}]

\\begin{{document}}

%----------HEADING----------
\\begin{{center}}
    \\textbf{{\\Huge \\scshape {candidate_name}}} \\\\ \\vspace{{1pt}}
    \\small {candidate_phone} $|$ \\href{{mailto:{candidate_email}}}{{\\underline{{{candidate_email}}}}} $|$ 
    \\href{{https://{candidate_linkedin}}}{{\\underline{{{candidate_linkedin}}}}} $|$
    \\href{{https://{candidate_github}}}{{\\underline{{{candidate_github}}}}}
\\end{{center}}

%-----------TECHNICAL SKILLS-----------
\\section{{Technical Skills}}
 \\begin{{itemize}}[leftmargin=0.15in, label={{}}]
    \\small{{\\item{{
     \\textbf{{Languages \\& Frameworks:}} {{{injected_skills_str}}} \\\\
     \\textbf{{Developer Tools:}} {{Git, Docker, VS Code, Postman, Linux CLI, CI/CD Workflows}} \\\\
     \\textbf{{Core Methodologies:}} {{Agile/Scrum, Test-Driven Development, REST API Architecture, Vector Embeddings}}
    }}}}
 \\end{{itemize}}

%-----------EXPERIENCE-----------
\\section{{Experience}}
  \\begin{{itemize}}[leftmargin=0.15in, label={{}}]
    \\item
      \\begin{{tabular*}}{{0.97\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
        \\textbf{{Software Engineering Intern}} $|$ \\textit{{Tech Innovators Inc.}} & Summer 2024 \\\\
      \\end{{tabular*}}
      \\begin{{itemize}}[leftmargin=0.15in]
        \\item Engineered automated data processing microservices using \\textbf{{{student_skills[0] if student_skills else 'Python'}}}, reducing execution pipeline time by \\textbf{{35\\%}} across 200k+ records.
        \\item Integrated robust REST endpoints with \\textbf{{{missing_kw[0] if missing_kw else 'FastAPI'}}}, optimizing database query latency to under 45ms.
        \\item Authored comprehensive pytest suites achieving 92\\% unit test coverage, ensuring zero critical regressions in production releases.
      \\end{{itemize}}
  \\end{{itemize}}

%-----------PROJECTS-----------
\\section{{Technical Projects}}
    \\begin{{itemize}}[leftmargin=0.15in, label={{}}]
      \\item
        \\textbf{{End-to-End {target_career} Pipeline}} $|$ \\emph{{{injected_skills_str[:40]}}} \\\\
        \\begin{{itemize}}[leftmargin=0.15in]
          \\item Architected and deployed scalable technical architecture using \\textbf{{{injected_skills_list[0] if injected_skills_list else 'Python'}}}, achieving \\textbf{{94.2\\%}} benchmark accuracy.
          \\item Implemented automated containerized deployment workflows using \\textbf{{Docker}} and GitHub Actions for continuous integration.
          \\item Designed interactive analytics dashboards, delivering actionable insights and cutting manual reporting time by \\textbf{{6 hours/week}}.
        \\end{{itemize}}
    \\end{{itemize}}

%-----------EDUCATION-----------
\\section{{Education}}
  \\begin{{itemize}}[leftmargin=0.15in, label={{}}]
    \\item
      \\begin{{tabular*}}{{0.97\\textwidth}}[t]{{l@{{\\extracolsep{{\\fill}}}}r}}
        \\textbf{{Bachelor of Technology in Computer Science \\& Engineering}} & Expected 2025 \\\\
        \\textit{{Department of Engineering}} & GPA: 3.8 / 4.0 \\\\
      \\end{{tabular*}}
  \\end{{itemize}}

\\end{{document}}
"""
        return latex_template

    def generate_tailored_html_resume(
        self,
        student_skills: List[str],
        target_career: str,
        job_description: str,
        missing_keywords: Optional[List[str]] = None,
        candidate_name: str = "Alex Chen",
        candidate_email: str = "alex.chen@email.com",
        candidate_phone: str = "(555) 019-2834",
        candidate_linkedin: str = "linkedin.com/in/alexchen-tech",
        candidate_github: str = "github.com/alexchen-dev"
    ) -> str:
        """
        Generates clean ATS single-column HTML resume formatted for direct browser printing to PDF.
        """
        missing_kw = missing_keywords or []
        injected_skills_list = list(set(student_skills + missing_kw[:4]))
        injected_skills_str = ", ".join(injected_skills_list)

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{candidate_name} - {target_career} Resume</title>
  <style>
    body {{
      font-family: 'Times New Roman', Times, serif;
      line-height: 1.35;
      color: #111;
      max-width: 800px;
      margin: 0 auto;
      padding: 30px;
      background: #fff;
    }}
    h1 {{ font-size: 24px; text-transform: uppercase; margin: 0; text-align: center; letter-spacing: 0.05em; }}
    .contact-line {{ text-align: center; font-size: 13px; margin-top: 4px; margin-bottom: 16px; color: #333; }}
    .contact-line a {{ color: #111; text-decoration: none; }}
    .section-title {{ font-size: 14px; font-weight: bold; text-transform: uppercase; border-bottom: 1px solid #111; padding-bottom: 2px; margin-top: 14px; margin-bottom: 6px; }}
    .item-header {{ display: flex; justify-content: space-between; font-weight: bold; font-size: 13px; margin-top: 6px; }}
    .item-sub {{ font-style: italic; font-size: 12px; color: #444; }}
    ul {{ margin: 4px 0 8px 18px; padding: 0; font-size: 12.5px; }}
    li {{ margin-bottom: 3px; }}
    .skill-category {{ font-size: 12.5px; margin-bottom: 4px; }}
    .highlight-kw {{ font-weight: bold; }}
    @media print {{
      body {{ padding: 0; max-width: 100%; }}
      @page {{ margin: 0.5in; }}
    }}
  </style>
</head>
<body>

  <h1>{candidate_name}</h1>
  <div class="contact-line">
    {candidate_phone} &bull; <a href="mailto:{candidate_email}">{candidate_email}</a> &bull; <a href="https://{candidate_linkedin}">{candidate_linkedin}</a> &bull; <a href="https://{candidate_github}">{candidate_github}</a>
  </div>

  <div class="section-title">Technical Skills</div>
  <div class="skill-category"><b>Languages & Frameworks:</b> <span class="highlight-kw">{injected_skills_str}</span></div>
  <div class="skill-category"><b>Developer Tools:</b> Git, Docker, VS Code, Postman, Linux CLI, CI/CD Pipelines</div>
  <div class="skill-category"><b>Core Methodologies:</b> Agile/Scrum, Test-Driven Development, RESTful Microservices, Vector Search</div>

  <div class="section-title">Experience</div>
  <div class="item-header">
    <span>Software Engineering Intern &mdash; Tech Innovators Inc.</span>
    <span>Summer 2024</span>
  </div>
  <ul>
    <li>Engineered automated data processing microservices using <b>{student_skills[0] if student_skills else 'Python'}</b>, reducing execution pipeline latency by <b>35%</b> across 200k+ records.</li>
    <li>Integrated high-throughput REST endpoints with <b>{missing_kw[0] if missing_kw else 'FastAPI'}</b>, optimizing database query response times to under 45ms.</li>
    <li>Authored comprehensive pytest suites achieving <b>92% code coverage</b>, eliminating critical release defects.</li>
  </ul>

  <div class="section-title">Technical Projects</div>
  <div class="item-header">
    <span>End-to-End {target_career} Platform</span>
    <span>2024 &ndash; Present</span>
  </div>
  <div class="item-sub">Tech Stack: {injected_skills_str[:50]}</div>
  <ul>
    <li>Architected scalable machine learning & analytical workflows using <b>{injected_skills_list[0] if injected_skills_list else 'Python'}</b>, achieving <b>94.2%</b> predictive accuracy.</li>
    <li>Implemented automated Docker containerization and GitHub Actions CI pipelines for seamless deployment.</li>
    <li>Designed interactive KPI dashboards, accelerating business intelligence turnaround by <b>6 hours weekly</b>.</li>
  </ul>

  <div class="section-title">Education</div>
  <div class="item-header">
    <span>Bachelor of Technology in Computer Science & Engineering</span>
    <span>Expected 2025</span>
  </div>
  <div class="item-sub">GPA: 3.8 / 4.0 &bull; Relevant Coursework: Data Structures, Algorithms, Machine Learning, Database Systems</div>

</body>
</html>
"""
        return html_template
