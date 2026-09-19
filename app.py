"""
Student Skill Gap & Career Recommendation System
Phase 13: Interactive Streamlit Web Application

An AI/NLP-powered recommendation dashboard that evaluates student technical profiles
against industry career benchmarks, quantifies skill gaps, and generates
prerequisite-ordered, personalized learning roadmaps with curated projects.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

# Add src directory to system path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from data_loader import DataLoader
from preprocessing import SkillPreprocessor
from skill_extractor import NLPSkillExtractor
from skill_matcher import SkillMatcher
from semantic_matcher import SemanticSkillMatcher
from gap_analyzer import SkillGapAnalyzer
from recommendation_engine import RecommendationEngine
from roadmap_generator import RoadmapGenerator
from resume_parser import ResumeParser
from analytics_dashboard import VisualAnalyticsDashboard
from interview_simulator import MockInterviewEngine, InterviewQuestion, AnswerEvaluation


# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SkillGap AI | Student Career Roadmap Engine",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished, modern Data Science aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4b5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8fafc;
        border-radius: 10px;
        padding: 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e40af;
    }
    .metric-lbl {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
    }
    .skill-badge-matched {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        margin: 3px;
        border: 1px solid #86efac;
        font-size: 0.85rem;
    }
    .skill-badge-gap-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        margin: 3px;
        border: 1px solid #fca5a5;
        font-size: 0.85rem;
    }
    .skill-badge-gap-med {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        margin: 3px;
        border: 1px solid #fcd34d;
        font-size: 0.85rem;
    }
    .skill-badge-gap-low {
        background-color: #e0f2fe;
        color: #075985;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-block;
        margin: 3px;
        border: 1px solid #7dd3fc;
        font-size: 0.85rem;
    }
    .phase-container {
        background-color: #ffffff;
        border-left: 5px solid #3b82f6;
        padding: 16px;
        margin-bottom: 16px;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. CACHED ENGINE INITIALIZATION
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner="Initializing AI/NLP Engine & Knowledge Base...")
def get_system_engines():
    loader = DataLoader()
    preprocessor = SkillPreprocessor(data_loader=loader)
    extractor = NLPSkillExtractor(data_loader=loader, preprocessor=preprocessor)
    matcher = SkillMatcher(data_loader=loader, preprocessor=preprocessor)
    semantic_matcher = SemanticSkillMatcher(data_loader=loader)
    gap_analyzer = SkillGapAnalyzer(data_loader=loader, skill_matcher=matcher)
    rec_engine = RecommendationEngine(data_loader=loader, gap_analyzer=gap_analyzer)
    roadmap_gen = RoadmapGenerator(data_loader=loader, recommendation_engine=rec_engine)
    resume_parser = ResumeParser(data_loader=loader, skill_extractor=extractor)
    interview_engine = MockInterviewEngine(data_loader=loader, semantic_matcher=semantic_matcher)
    return loader, preprocessor, extractor, matcher, semantic_matcher, gap_analyzer, rec_engine, roadmap_gen, resume_parser, interview_engine

loader, preprocessor, extractor, matcher, semantic_matcher, gap_analyzer, rec_engine, roadmap_gen, resume_parser, interview_engine = get_system_engines()


# -----------------------------------------------------------------------------
# 3. SIDEBAR CONTROLS & PROFILE INPUT
# -----------------------------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/graduation-cap.png", width=70)
st.sidebar.title("SkillGap AI")
st.sidebar.caption("Student Placement Readiness System")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Target Career Role")

career_titles = loader.careers["career_title"].tolist()
selected_career = st.sidebar.selectbox("Select Target Role:", career_titles, index=0)

career_info = loader.get_career_by_title_or_id(selected_career)
st.sidebar.info(f"**Domain:** {career_info['category']}\n\n**Level:** {career_info['experience_level']}")

st.sidebar.markdown("---")
st.sidebar.subheader("📝 Student Profile Input")

input_mode = st.sidebar.radio(
    "Choose Input Method:",
    ["Manual Selection & Text", "📄 Upload Resume PDF", "⚡ Preset Sample Profiles"],
    index=0
)

student_input_skills = []

if input_mode == "Manual Selection & Text":
    all_taxonomy_skills = sorted(loader.skills["skill_name"].tolist())
    selected_tags = st.sidebar.multiselect(
        "Select Your Existing Skills:",
        all_taxonomy_skills,
        default=["Python", "Pandas", "SQL", "Excel"]
    )
    
    free_text_input = st.sidebar.text_area(
        "Or Describe / Paste Skills Free-form:",
        placeholder="e.g. I know Python, pandas, basic ML, SQL and Tableau..."
    )
    
    extracted_from_text = extractor.extract_canonical_names(free_text_input) if free_text_input else []
    student_input_skills = list(set(selected_tags + extracted_from_text))

elif input_mode == "📄 Upload Resume PDF":
    uploaded_file = st.sidebar.file_uploader("Upload Resume (PDF format)", type=["pdf"])
    if uploaded_file is not None:
        with st.spinner("Parsing PDF Resume & Extracting Skills..."):
            resume_profile = resume_parser.parse_resume(uploaded_file, filename=uploaded_file.name)
            
            if resume_profile.is_valid:
                st.sidebar.success(f"✓ Parsed {resume_profile.word_count} words ({resume_profile.page_count} page)")
                if resume_profile.detected_sections:
                    st.sidebar.caption(f"Sections: {', '.join(resume_profile.detected_sections)}")
                
                # Allow user to review and verify extracted skills
                verified_skills = st.sidebar.multiselect(
                    "Review / Edit Extracted Skills:",
                    sorted(loader.skills["skill_name"].tolist()),
                    default=resume_profile.extracted_canonical_skills
                )
                student_input_skills = verified_skills
            else:
                st.sidebar.error(f"Error: {resume_profile.error_message}")
                student_input_skills = []
    else:
        st.sidebar.info("Please upload a PDF resume to extract skills.")
        student_input_skills = []

elif input_mode == "⚡ Preset Sample Profiles":
    sample_choice = st.sidebar.selectbox(
        "Load Preset Student Persona:",
        [
            "Student A: Data Science Aspirant (Python, Pandas, SQL, Excel)",
            "Student B: ML Engineer Aspirant (Python, PyTorch, Git, Docker)",
            "Student C: BI & Analytics Aspirant (SQL, Tableau, Excel, Power BI)",
            "Student D: Beginner / Fresher (Python, Git)"
        ]
    )
    presets = {
        "Student A: Data Science Aspirant (Python, Pandas, SQL, Excel)": ["Python", "Pandas", "SQL", "Excel"],
        "Student B: ML Engineer Aspirant (Python, PyTorch, Git, Docker)": ["Python", "Linear Algebra", "NumPy", "Deep Learning", "PyTorch", "Git & GitHub", "Docker"],
        "Student C: BI & Analytics Aspirant (SQL, Tableau, Excel, Power BI)": ["SQL", "Excel", "Tableau", "Power BI", "Statistics & Probability"],
        "Student D: Beginner / Fresher (Python, Git)": ["Python", "Git & GitHub"]
    }
    student_input_skills = presets[sample_choice]
    st.sidebar.write("**Loaded Skills:**", ", ".join(student_input_skills))

st.sidebar.markdown("---")
analyze_button = st.sidebar.button("🚀 Analyze Skill Gap & Generate Roadmap", type="primary", use_container_width=True)


# -----------------------------------------------------------------------------
# 4. MAIN PAGE CONTENT & DASHBOARD
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">🎓 Student Skill Gap & Career Recommendation System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Bridge the transition from academic coursework to industry career placement with AI-driven gap analysis & prerequisite roadmaps.</div>', unsafe_allow_html=True)

# Tabs
tab_dashboard, tab_roadmap, tab_recommendations, tab_analytics, tab_interview, tab_about = st.tabs([
    "📊 Skill Gap & Role Match",
    "🗺️ Learning Roadmap",
    "💡 Curated Projects & Resources",
    "📈 Dataset Analytics & Heatmap",
    "🎙️ AI Mock Interviewer",
    "ℹ️ System Architecture"
])

# Display info banner if user has an empty profile
if not student_input_skills:
    st.info("ℹ️ **Fresh Profile (0 Skills Selected):** Showing the complete prerequisite foundation curriculum required to qualify for this career track.")

# Run matching and recommendation pipeline
match_result = matcher.match_skills(student_input_skills, selected_career)
gap_result = gap_analyzer.analyze_gaps(student_input_skills, selected_career)
rec_report = rec_engine.generate_recommendations(student_input_skills, selected_career)
visual_roadmap = roadmap_gen.generate_roadmap(student_input_skills, selected_career)


# =============================================================================
# TAB 1: SKILL GAP & MATCH DASHBOARD
# =============================================================================
with tab_dashboard:
    st.subheader(f"Role Readiness Assessment: {selected_career}")
    st.caption(f"Role Summary: {career_info['description']}")

    # Top Metric Score Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{match_result.weighted_readiness_pct:.1f}%</div>
            <div class="metric-lbl">Weighted Match Score</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{len(match_result.matched_skills)} / {len(match_result.required_skills)}</div>
            <div class="metric-lbl">Skills Covered</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="color: {'#16a34a' if match_result.core_matched_count >= match_result.core_total_count/2 else '#dc2626'};">
                {match_result.core_matched_count} / {match_result.core_total_count}
            </div>
            <div class="metric-lbl">Core Skills Progress</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="color: #ea580c;">~{rec_report.total_estimated_study_hours}h</div>
            <div class="metric-lbl">Est. Study Hours</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Progress bar
    st.progress(min(1.0, match_result.weighted_readiness_pct / 100.0), text=f"Overall Weighted Readiness: {match_result.weighted_readiness_pct:.1f}%")

    st.markdown("---")

    # Matched Skills vs Missing Skills Columns
    col_matched, col_gaps = st.columns(2)

    with col_matched:
        st.markdown("### ✅ Matched Competencies")
        if match_result.matched_skills:
            st.write(f"You satisfy **{len(match_result.matched_skills)}** benchmark requirements:")
            for s in match_result.matched_skills:
                st.markdown(f"""
                <span class="skill-badge-matched">✓ {s['skill_name']} ({s['importance_level']})</span>
                """, unsafe_allow_html=True)
        else:
            st.warning("No direct skill matches found for this role yet. Start with Phase 1 fundamentals!")

        if match_result.extra_skills:
            st.markdown("<br>##### 🔄 Transferable / Auxiliary Skills", unsafe_allow_html=True)
            st.caption("Skills you possess that provide cross-domain versatility:")
            for s in match_result.extra_skills:
                st.markdown(f'<span class="skill-badge-low">✦ {s}</span>', unsafe_allow_html=True)

    with col_gaps:
        st.markdown("### ⚠️ Identified Skill Gaps (By Priority)")
        st.write(f"You have **{len(match_result.missing_skills)}** missing skills to acquire:")

        if gap_result.high_priority_gaps:
            st.markdown("**🚨 High Priority (Immediate Core Focus):**")
            for s in gap_result.high_priority_gaps:
                st.markdown(f"""
                <span class="skill-badge-gap-high">! {s.skill_name} [Weight: {s.importance_weight}]</span>
                """, unsafe_allow_html=True)

        if gap_result.medium_priority_gaps:
            st.markdown("<br>**⚡ Medium Priority (Core / Secondary Build-Up):**", unsafe_allow_html=True)
            for s in gap_result.medium_priority_gaps:
                st.markdown(f"""
                <span class="skill-badge-gap-med">▲ {s.skill_name} [Weight: {s.importance_weight}]</span>
                """, unsafe_allow_html=True)

        if gap_result.low_priority_gaps:
            st.markdown("<br>**🔹 Low Priority (Auxiliary / Specialization):**", unsafe_allow_html=True)
            for s in gap_result.low_priority_gaps:
                st.markdown(f"""
                <span class="skill-badge-gap-low">▼ {s.skill_name} [Weight: {s.importance_weight}]</span>
                """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Interactive Visual Analytics Row in Tab 1
    st.markdown("### 📊 Visual Diagnostic Analytics")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        fig_radar = VisualAnalyticsDashboard.create_category_radar_chart(match_result)
        st.plotly_chart(fig_radar, use_container_width=True)
    with col_v2:
        fig_donut = VisualAnalyticsDashboard.create_matched_vs_missing_donut(match_result)
        st.plotly_chart(fig_donut, use_container_width=True)

    # Multi-Role Best Fit Ranking Preview
    st.markdown("---")
    st.subheader("🎯 Cross-Career Role Readiness Comparison")
    st.caption("Compare how your existing skill set aligns against all 7 industry career tracks:")
    
    all_rankings = matcher.match_all_careers(student_input_skills)
    fig_career_bar = VisualAnalyticsDashboard.create_career_comparison_bar(all_rankings)
    st.plotly_chart(fig_career_bar, use_container_width=True)
    
    ranking_data = []
    for rank, r in enumerate(all_rankings, 1):
        ranking_data.append({
            "Rank": f"#{rank}",
            "Career Track": r.career_title,
            "Weighted Match (%)": f"{r.weighted_readiness_pct:.1f}%",
            "Skill Coverage": f"{len(r.matched_skills)}/{len(r.required_skills)}",
            "Core Skills Satisfied": f"{r.core_matched_count}/{r.core_total_count}",
            "Is Selected": "★ (Current)" if r.career_title == selected_career else ""
        })
    st.dataframe(pd.DataFrame(ranking_data), use_container_width=True, hide_index=True)


# =============================================================================
# TAB 2: LEARNING ROADMAP
# =============================================================================
with tab_roadmap:
    st.subheader(f"🗺️ Prerequisite-Ordered Learning Roadmap: {selected_career}")
    st.caption("Skills are topologically sequenced so you always master foundational concepts before dependent technologies.")

    # Render structured phase containers
    if not visual_roadmap.phases:
        st.success("🎉 **100% Career Competencies Mastered!** You satisfy all required benchmark skills for this role. No missing gap milestones are needed. You are ready to build the Capstone Portfolio Project in Tab 3!")
    else:
        for phase in visual_roadmap.phases:
            st.markdown(f"""
            <div class="phase-container">
                <h4 style="margin:0; color:#1e40af;">📌 {phase['title']} (~{phase['estimated_hours']} Hours)</h4>
                <p style="color:#64748b; margin-top:4px; font-size:0.95rem;"><b>Phase Goal:</b> {phase['objective']}</p>
            </div>
            """, unsafe_allow_html=True)

        for s in phase["skills"]:
            with st.expander(f"Step {s['step']:02d}: {s['skill_name']}  [{s['priority']} Priority | {s['difficulty']}]"):
                col_r1, col_r2 = st.columns([3, 2])
                with col_r1:
                    st.write(f"**Why Learn Now:** {s['reason']}")
                    st.write(f"**Category:** {s['category']}")
                    st.write(f"**Estimated Commitment:** ~{s['hours']} Hours")
                with col_r2:
                    st.write(f"**Recommended Resource:**")
                    st.markdown(f"🔗 [{s['top_resource']}]({s['resource_url']})")

    # Render Visual Mermaid Graph
    st.markdown("---")
    st.subheader("📊 Visual Pipeline Graph (Mermaid)")
    st.markdown(visual_roadmap.mermaid_diagram)


# =============================================================================
# TAB 3: RECOMMENDED PROJECTS & RESOURCES
# =============================================================================
with tab_recommendations:
    st.subheader(f"💡 Recommended Portfolio Projects for {selected_career}")
    st.caption("Recruiters evaluate practical project artifacts. These projects are scored specifically against your missing skills.")

    if rec_report.recommended_projects:
        for i, proj in enumerate(rec_report.recommended_projects, 1):
            with st.container():
                st.markdown(f"### Project {i}: {proj.title} `[{proj.difficulty}]`")
                st.write(f"**Gap Relevance Score:** `{proj.relevance_score:.1f}% Match to Your Skill Gaps`")
                st.info(f"**Why Recommended:** {proj.recommendation_reason}")
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    st.write(f"**Technologies Exercised:** `{proj.primary_skills}`")
                    st.write(f"**Project Scope:** {proj.description}")
                with col_p2:
                    st.write(f"**Key Deliverables for Resume:**")
                    st.success(proj.key_deliverables)
                st.markdown("---")
    else:
        st.info("No explicit project mapped for this role yet.")

    # All Curated Resources Table
    st.subheader("📚 All Curated Learning Resources")
    all_res_data = []
    for srec in rec_report.skill_recommendations:
        for r in srec.resources:
            all_res_data.append({
                "Skill": srec.skill_name,
                "Resource Title": r.title,
                "Platform": r.platform,
                "Format": r.resource_type,
                "Cost": r.cost,
                "Est. Hours": f"{r.estimated_hours}h",
                "Link": r.url_or_ref
            })
    if all_res_data:
        st.dataframe(pd.DataFrame(all_res_data), use_container_width=True, hide_index=True)


# =============================================================================
# TAB 4: DATASET ANALYTICS & HEATMAP
# =============================================================================
with tab_analytics:
    st.subheader("📈 Exploratory Career-Skill Knowledge Analytics")
    st.caption("Interactive visual analysis of skill taxonomy distributions, gap dimensions, and career requirement density.")

    # Row 1: Skill Gaps by Category & Career Comparison
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        fig_gap_bar = VisualAnalyticsDashboard.create_gap_distribution_bar(gap_result)
        st.plotly_chart(fig_gap_bar, use_container_width=True)
    with col_a2:
        merged_cs = pd.merge(loader.career_skills, loader.skills, on="skill_id")
        skill_counts = merged_cs["skill_name"].value_counts().head(10).reset_index()
        skill_counts.columns = ["Skill", "Count"]
        fig_top = px.bar(
            skill_counts,
            x="Count",
            y="Skill",
            orientation="h",
            title="<b>Top 10 In-Demand Skills Across All 7 Roles</b>",
            color="Count",
            color_continuous_scale="Teal"
        )
        fig_top.update_layout(yaxis=dict(autorange="reversed"), height=380, margin=dict(l=20, r=20, t=50, b=40))
        st.plotly_chart(fig_top, use_container_width=True)

    # Row 2: Interactive Requirement Matrix Heatmap
    st.markdown("---")
    st.markdown("#### 🗺️ Interactive Career vs. Skill Requirement Matrix")
    st.caption("Hover over cells to inspect exact requirement importance weights (0 = Not Required, 1 = Optional, 2 = Secondary, 3 = Core).")
    fig_matrix = VisualAnalyticsDashboard.create_interactive_matrix_heatmap(loader)
    st.plotly_chart(fig_matrix, use_container_width=True)


# =============================================================================
# TAB 5: AI MOCK INTERVIEW SIMULATOR
# =============================================================================
with tab_interview:
    st.subheader(f"🎙️ AI Technical Mock Interviewer ({selected_career})")
    st.caption("Practice answering real technical interview questions specifically targeted at your identified skill gaps. Receive automated semantic scoring and rubric evaluation.")

    # 1. Select Target Gap Skill
    missing_skill_names = [s.skill_name for s in gap_result.learning_roadmap]
    available_interview_skills = missing_skill_names if missing_skill_names else sorted(loader.skills["skill_name"].tolist())

    col_int1, col_int2 = st.columns([3, 1])
    with col_int1:
        target_interview_skill = st.selectbox(
            "Select Skill Gap to Practice:",
            available_interview_skills,
            index=0 if available_interview_skills else 0
        )
    with col_int2:
        st.markdown("<br>", unsafe_allow_html=True)
        new_q_clicked = st.button("🎲 Next Question", use_container_width=True)

    # Initialize or update question index in session state
    if "current_question_idx" not in st.session_state or new_q_clicked:
        st.session_state["current_question_idx"] = 0
        st.session_state["last_evaluated_answer"] = None

    questions_for_skill = interview_engine.get_questions_for_skill(target_interview_skill)
    q_idx = st.session_state["current_question_idx"] % len(questions_for_skill)
    current_q = questions_for_skill[q_idx]

    # Display Interviewer Question Card
    st.markdown(f"""
    <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-left: 5px solid #16a34a; padding: 18px; border-radius: 8px; margin: 15px 0;">
        <div style="font-size: 0.85rem; font-weight: 700; color: #15803d; text-transform: uppercase;">
            🤖 Tech Interviewer Question &nbsp;|&nbsp; <b>Skill:</b> {current_q.skill_name} &nbsp;|&nbsp; <b>Difficulty:</b> {current_q.difficulty} &nbsp;|&nbsp; <b>Type:</b> {current_q.question_type}
        </div>
        <div style="font-size: 1.15rem; font-weight: 600; color: #1e293b; margin-top: 8px;">
            "{current_q.question_text}"
        </div>
        <div style="font-size: 0.85rem; color: #64748b; margin-top: 6px;">
            💡 <i>Interviewer Hint: {current_q.follow_up_hint}</i>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Candidate Answer Form
    with st.form("interview_answer_form"):
        candidate_response = st.text_area(
            "Your Technical Answer:",
            placeholder="Type your explanation here... Focus on underlying principles, architecture, and practical trade-offs.",
            height=140
        )
        submit_answer = st.form_submit_button("🚀 Submit Answer for AI Evaluation", type="primary")

    if submit_answer:
        if not candidate_response.strip():
            st.warning("Please type an answer before submitting.")
        else:
            with st.spinner("Analyzing answer concepts and evaluating semantic depth..."):
                eval_result = interview_engine.evaluate_candidate_answer(current_q, candidate_response)
                st.session_state["last_evaluated_answer"] = eval_result

    # Display Evaluation Feedback Card
    if st.session_state.get("last_evaluated_answer") is not None:
        eval_res: AnswerEvaluation = st.session_state["last_evaluated_answer"]
        
        st.markdown("---")
        st.markdown("### 📊 Automated AI Evaluation & Feedback Scorecard")
        
        # Top Score Metrics
        col_sc1, col_sc2, col_sc3 = st.columns(3)
        score_color = "#16a34a" if eval_res.overall_score >= 8 else ("#ea580c" if eval_res.overall_score >= 6 else "#dc2626")
        
        with col_sc1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color: {score_color};">{eval_res.overall_score} / 10</div>
                <div class="metric-lbl">Overall Technical Score</div>
            </div>
            """, unsafe_allow_html=True)
        with col_sc2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{eval_res.score_tier}</div>
                <div class="metric-lbl">Proficiency Tier</div>
            </div>
            """, unsafe_allow_html=True)
        with col_sc3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{eval_res.concept_coverage_pct:.1f}%</div>
                <div class="metric-lbl">Concept Keyword Coverage</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Concept Breakdown Tags
        col_cp1, col_cp2 = st.columns(2)
        with col_cp1:
            st.markdown("##### ✅ Key Concepts Covered")
            if eval_res.matched_concepts:
                for c in eval_res.matched_concepts:
                    st.markdown(f'<span class="skill-badge-matched">✓ {c}</span>', unsafe_allow_html=True)
            else:
                st.caption("No key domain concepts detected in the response.")

        with col_cp2:
            st.markdown("##### ⚠️ Missing Key Concepts to Address")
            if eval_res.missing_concepts:
                for c in eval_res.missing_concepts:
                    st.markdown(f'<span class="skill-badge-gap-high">! {c}</span>', unsafe_allow_html=True)
            else:
                st.success("All expected key concepts were covered!")

        # Detailed Qualitative Feedback
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"**💪 Strengths:** {eval_res.feedback_strengths}")
        st.warning(f"**🎯 Actionable Advice for Placement Interviews:** {eval_res.feedback_improvements}")

        # Benchmark Ideal Model Answer
        with st.expander("📖 View Benchmark Senior-Level Model Answer"):
            st.write(eval_res.ideal_model_answer)


# =============================================================================
# TAB 6: SYSTEM ARCHITECTURE & ABOUT
# =============================================================================
with tab_about:
    st.subheader("ℹ️ System Architecture & Engineering Specifications")
    
    st.markdown("""
    ### 🧠 System Design Highlights
    1. **Two-Tier Skill Matching Engine**:
       - **Tier 1 (Normalized Exact & Alias Matcher)**: Deterministic dictionary mapping with $80+$ aliases and RapidFuzz typo tolerance.
       - **Tier 2 (Dense Semantic AI Matcher)**: Sentence Transformers (`all-MiniLM-L6-v2`) generating $384$-dimensional vector embeddings for cosine similarity evaluation.
    2. **Explainable Prerequisite Graph (DAG)**:
       - Uses Kahn's algorithm with priority queues to sequence learning steps based on mathematical dependency traversal.
    3. **Automated Resume PDF Parser**:
       - Extracts text layers with `PyMuPDF`, performs multi-word entity extraction, and presents parsed profiles for interactive student verification.
    4. **Weighted Role Readiness Score**:
       $$\\text{Readiness Score (\\%)} = \\left( \\frac{\\sum_{s \\in \\text{Matched}} w(s)}{\\sum_{s \\in \\text{Required}} w(s)} \\right) \\times 100$$
    """)
    
    st.info("Designed and built as an applied AI & Data Science Capstone Project for technical placement preparation and portfolio demonstration.")
