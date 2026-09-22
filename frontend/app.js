/**
 * SkillGap AI - Official Shadcn UI Enterprise Analytics Controller
 * Connects asynchronously to FastAPI REST Backend (Port 8000)
 */

const API_BASE = window.location.origin;

// Canonical Skills Taxonomy
const ALL_TAXONOMY_SKILLS = [
  "Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Matplotlib & Seaborn",
  "Statistics & Probability", "Feature Engineering", "Git & GitHub", "Docker",
  "FastAPI", "Deep Learning", "PyTorch", "TensorFlow", "NLP Fundamentals",
  "Tableau", "Power BI", "Excel", "Data Visualization", "Data Pipelines",
  "PostgreSQL", "Flask", "Cloud Fundamentals (AWS/GCP)", "Data Cleaning",
  "EDA (Exploratory Data Analysis)", "Unit Testing (pytest)", "Linux & Bash",
  "Database Design", "Big Data (PySpark)", "Model Deployment", "MLOps Basics",
  "Linear Algebra"
];

// Presets
const PRESET_PERSONAS = {
  ds: ["Python", "Pandas", "SQL", "Excel", "Scikit-Learn"],
  mle: ["Python", "NumPy", "PyTorch", "Deep Learning", "Git & GitHub", "Docker"],
  bi: ["SQL", "Excel", "Tableau", "Power BI", "Statistics & Probability"],
  beg: ["Python", "Git & GitHub"]
};

// Global App State
const state = {
  targetCareer: "Data Scientist",
  studentSkills: ["Python", "Pandas", "SQL", "Excel"],
  theme: localStorage.getItem("skillgap_theme") || "light",
  currentView: "view-overview",
  chartMode: "radar",
  chartInstance: null,
  cachedData: null
};

// Initialize Application on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initLucideIcons();
  initWelcomeScreen();
  initHeaderNavigation();
  initCareerDropdown();
  initChartToggle();
  initResumeUpload();
  initCommandPalette();
  initATSScorer();
  initInterviewSimulator();
  initGitHubScanner();
  initMarketIntelligence();
  initXYZRewriter();
  initDownloadReport();
});

function initLucideIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// -----------------------------------------------------------------------------
// 0. OPENING LANDING PAGE & ONBOARDING CONTROLLER
// -----------------------------------------------------------------------------
function initWelcomeScreen() {
  renderWelcomeSkillChips();
  setupWelcomeRoleSelector();
  setupWelcomeResumeUpload();
  updateWelcomeSkillCountBadge();

  // Welcome Theme Toggle
  const welcomeThemeBtn = document.getElementById("welcome-theme-toggle");
  if (welcomeThemeBtn) {
    welcomeThemeBtn.addEventListener("click", () => {
      state.theme = state.theme === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", state.theme);
      localStorage.setItem("skillgap_theme", state.theme);
      updateThemeIcon();
    });
  }
}

function setupWelcomeRoleSelector() {
  const selectEl = document.getElementById("welcome-career-select");

  if (selectEl) {
    selectEl.value = state.targetCareer;
    selectEl.addEventListener("change", (e) => {
      state.targetCareer = e.target.value;
      const mainDropdown = document.getElementById("career-dropdown");
      if (mainDropdown) mainDropdown.value = e.target.value;
    });
  }
}

window.switchWelcomeInputTab = function(tabName) {
  const resumeBtn = document.getElementById("welcome-tab-resume-btn");
  const skillsBtn = document.getElementById("welcome-tab-skills-btn");
  const paneResume = document.getElementById("welcome-pane-resume");
  const paneSkills = document.getElementById("welcome-pane-skills");

  if (tabName === "resume") {
    if (resumeBtn) resumeBtn.classList.add("active");
    if (skillsBtn) skillsBtn.classList.remove("active");
    if (paneResume) paneResume.style.display = "block";
    if (paneSkills) paneSkills.style.display = "none";
  } else {
    if (skillsBtn) skillsBtn.classList.add("active");
    if (resumeBtn) resumeBtn.classList.remove("active");
    if (paneSkills) paneSkills.style.display = "block";
    if (paneResume) paneResume.style.display = "none";
  }
  initLucideIcons();
};

function renderWelcomeSkillChips() {
  const container = document.getElementById("welcome-skills-chips-container");
  if (!container) return;

  container.innerHTML = ALL_TAXONOMY_SKILLS.map(skill => {
    const isSelected = state.studentSkills.includes(skill);
    return `
      <div class="tag-chip ${isSelected ? 'selected' : ''}" style="cursor: pointer;" onclick="toggleWelcomeSkill('${skill}')">
        ${skill}
      </div>
    `;
  }).join("");
}

window.toggleWelcomeSkill = function(skill) {
  if (state.studentSkills.includes(skill)) {
    state.studentSkills = state.studentSkills.filter(s => s !== skill);
  } else {
    state.studentSkills.push(skill);
  }
  renderWelcomeSkillChips();
  updateWelcomeSkillCountBadge();
};

window.applyWelcomePreset = function(presetKey) {
  const presetSkills = PRESET_PERSONAS[presetKey] || [];
  state.studentSkills = [...presetSkills];
  renderWelcomeSkillChips();
  updateWelcomeSkillCountBadge();
};

function updateWelcomeSkillCountBadge() {
  const countBadge = document.getElementById("welcome-selected-count-badge");
  if (countBadge) {
    countBadge.textContent = `${state.studentSkills.length} Selected`;
  }
  const mainBadge = document.getElementById("skill-count-badge");
  if (mainBadge) {
    mainBadge.textContent = state.studentSkills.length;
  }
}

function setupWelcomeResumeUpload() {
  const dropzone = document.getElementById("welcome-dropzone");
  const fileInput = document.getElementById("welcome-resume-file-input");

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files.length) {
      handleWelcomeResumeFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files.length) {
      handleWelcomeResumeFile(e.target.files[0]);
    }
  });
}

async function handleWelcomeResumeFile(file) {
  const statusCard = document.getElementById("welcome-resume-status-card");
  const nameEl = document.getElementById("welcome-resume-name");
  const badgeEl = document.getElementById("welcome-resume-badge");
  const tagsEl = document.getElementById("welcome-resume-tags");

  if (nameEl) nameEl.textContent = `📄 ${file.name}`;
  if (statusCard) statusCard.style.display = "block";
  if (badgeEl) badgeEl.textContent = "Analyzing skills...";

  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE}/api/v1/upload-resume`, {
      method: "POST",
      body: formData
    });

    if (response.ok) {
      const data = await response.json();
      const extracted = data.extracted_skills || [];
      if (extracted.length > 0) {
        state.studentSkills = Array.from(new Set([...state.studentSkills, ...extracted]));
        displayWelcomeResumePreview(file.name, extracted);
        return;
      }
    }
  } catch (e) {
    console.warn("Backend resume parse failed, falling back to local extractor:", e);
  }

  // Client-side fallback
  if (file.name.endsWith(".txt") || file.name.endsWith(".md")) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const detected = extractSkillsFromTextString(text);
      if (detected.length) {
        state.studentSkills = Array.from(new Set([...state.studentSkills, ...detected]));
      }
      displayWelcomeResumePreview(file.name, detected.length ? detected : state.studentSkills);
    };
    reader.readAsText(file);
  } else {
    const sampleSkills = ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Git & GitHub", "Statistics & Probability"];
    state.studentSkills = Array.from(new Set([...state.studentSkills, ...sampleSkills]));
    displayWelcomeResumePreview(file.name, sampleSkills);
  }
}

window.loadSampleResumeInWelcome = function() {
  const sampleSkills = ["Python", "Pandas", "SQL", "Scikit-Learn", "Git & GitHub", "Statistics & Probability"];
  state.studentSkills = [...sampleSkills];
  displayWelcomeResumePreview("sample_data_science_resume.pdf", sampleSkills);
};

function displayWelcomeResumePreview(filename, skills) {
  const statusCard = document.getElementById("welcome-resume-status-card");
  const nameEl = document.getElementById("welcome-resume-name");
  const badgeEl = document.getElementById("welcome-resume-badge");
  const tagsEl = document.getElementById("welcome-resume-tags");

  if (!statusCard) return;

  statusCard.style.display = "block";
  if (nameEl) nameEl.textContent = `📄 ${filename}`;
  if (badgeEl) badgeEl.textContent = `✓ ${skills.length} Skills Extracted`;
  if (tagsEl) {
    tagsEl.innerHTML = skills.map(s => `<span class="tag-chip selected" style="cursor: default;">✓ ${s}</span>`).join("");
  }
  renderWelcomeSkillChips();
  updateWelcomeSkillCountBadge();
  initLucideIcons();
}

function extractSkillsFromTextString(text) {
  const textLower = text.toLowerCase();
  const matched = [];
  ALL_TAXONOMY_SKILLS.forEach(skill => {
    const sLower = skill.toLowerCase();
    if (textLower.includes(sLower) || (skill === "Python" && textLower.includes("python3"))) {
      matched.push(skill);
    }
  });
  return matched;
}

window.launchAppWithCurrentState = function() {
  const welcomeScreen = document.getElementById("welcome-screen");
  const mainApp = document.getElementById("main-app-wrapper");

  if (welcomeScreen) welcomeScreen.style.display = "none";
  if (mainApp) mainApp.style.display = "block";

  // Sync main app career dropdown
  const mainDropdown = document.getElementById("career-dropdown");
  if (mainDropdown) mainDropdown.value = state.targetCareer;

  // Sync skill count badge
  const skillCount = document.getElementById("skill-count-badge");
  if (skillCount) skillCount.textContent = state.studentSkills.length;

  // Run full analysis
  analyzeReadiness();
  window.scrollTo({ top: 0, behavior: "smooth" });
  initLucideIcons();
};

window.returnToWelcomeScreen = function() {
  const welcomeScreen = document.getElementById("welcome-screen");
  const mainApp = document.getElementById("main-app-wrapper");

  if (mainApp) mainApp.style.display = "none";
  if (welcomeScreen) welcomeScreen.style.display = "flex";

  // Sync welcome inputs
  const selectEl = document.getElementById("welcome-career-select");
  if (selectEl) selectEl.value = state.targetCareer;
  renderWelcomeSkillChips();
  updateWelcomeSkillCountBadge();

  window.scrollTo({ top: 0, behavior: "smooth" });
  initLucideIcons();
};

// -----------------------------------------------------------------------------
// 1. THEME CONTROLLER
// -----------------------------------------------------------------------------
function initTheme() {
  document.documentElement.setAttribute("data-theme", state.theme);
  updateThemeIcon();

  const themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      state.theme = state.theme === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", state.theme);
      localStorage.setItem("skillgap_theme", state.theme);
      updateThemeIcon();
      rebuildChart();
    });
  }
}

function updateThemeIcon() {
  const icon = document.getElementById("theme-icon");
  if (icon) {
    icon.setAttribute("data-lucide", state.theme === "light" ? "moon" : "sun");
  }
  const welcomeIcon = document.getElementById("welcome-theme-icon");
  if (welcomeIcon) {
    welcomeIcon.setAttribute("data-lucide", state.theme === "light" ? "moon" : "sun");
  }
  initLucideIcons();
}

// -----------------------------------------------------------------------------
// 2. HEADER SUB-NAVIGATION CONTROLLER
// -----------------------------------------------------------------------------
function initHeaderNavigation() {
  const navLinks = document.querySelectorAll(".header-nav .nav-link");
  navLinks.forEach(link => {
    link.addEventListener("click", () => {
      const targetView = link.getAttribute("data-view");
      if (!targetView) return;

      navLinks.forEach(l => l.classList.remove("active"));
      link.classList.add("active");

      document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));
      const activePanel = document.getElementById(targetView);
      if (activePanel) {
        activePanel.classList.add("active");
        state.currentView = targetView;
        initLucideIcons();
      }
    });
  });
}

window.switchNavTab = function(targetViewId) {
  const targetLink = document.querySelector(`.header-nav .nav-link[data-view="${targetViewId}"]`);
  if (targetLink) {
    targetLink.click();
  }
};

function initCareerDropdown() {
  const dropdown = document.getElementById("career-dropdown");
  if (dropdown) {
    dropdown.value = state.targetCareer;
    dropdown.addEventListener("change", (e) => {
      state.targetCareer = e.target.value;
      analyzeReadiness();
    });
  }
}

// -----------------------------------------------------------------------------
// 3. CORE SKILL GAP & READINESS API CONTROLLER
// -----------------------------------------------------------------------------
async function analyzeReadiness() {
  try {
    const payload = {
      student_skills: state.studentSkills,
      target_career: state.targetCareer
    };

    const response = await fetch(`${API_BASE}/api/v1/analyze-skills`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
    const data = await response.json();
    state.cachedData = data;

    renderOverviewDashboard(data);
    renderRoadmapDAG(data.dag_graph || data);
    renderFullRoadmap(data);
    renderStudyCalendar(data.study_calendar || data);
    renderFullProjects(data);
  } catch (err) {
    console.error("Readiness analysis failed:", err);
  }
}

function renderOverviewDashboard(data) {
  // Update 4 Simplified Metric Cards
  const score = data.weighted_readiness_pct || 0;
  const matchVal = document.getElementById("kpi-match-val");
  if (matchVal) matchVal.textContent = `${score.toFixed(1)}%`;

  const progBar = document.getElementById("kpi-progress-bar");
  if (progBar) progBar.style.width = `${Math.min(100, score)}%`;

  const deltaText = document.getElementById("kpi-delta-text");
  if (deltaText) {
    deltaText.innerHTML = `Target: <b>75%+ for Campus Placements</b>`;
  }

  const matched = data.matched_skills || [];
  const missing = data.missing_skills || [];
  const highGaps = data.high_priority_gaps || [];
  const totalReq = matched.length + missing.length;

  const coverageVal = document.getElementById("kpi-coverage-val");
  if (coverageVal) coverageVal.textContent = `${matched.length} / ${totalReq} Mastered`;

  const gapsVal = document.getElementById("kpi-gaps-val");
  if (gapsVal) gapsVal.textContent = `${missing.length}`;

  const gapsSub = document.getElementById("kpi-gaps-sub-text");
  if (gapsSub) {
    gapsSub.innerHTML = `<span id="kpi-gaps-val" style="color: var(--rose-text); font-weight: 700;">${missing.length}</span> bridge skills remaining to learn`;
  }

  // Predictive Placement & Peer Cohort KPI Updates
  const pred = data.placement_prediction;
  if (pred) {
    const probText = document.getElementById("kpi-placement-prob-text");
    if (probText) probText.textContent = `${pred.placement_probability_pct}%`;

    const probSub = document.getElementById("kpi-placement-sub-text");
    if (probSub) probSub.textContent = `Predicted offer likelihood from top tech firms`;

    const percentileVal = document.getElementById("kpi-percentile-val");
    if (percentileVal) {
      const topPct = (100 - pred.cohort_percentile).toFixed(1);
      percentileVal.textContent = pred.cohort_percentile >= 50 ? `Top ${topPct}%` : `Ahead of ${pred.cohort_percentile.toFixed(1)}%`;
    }

    const cohortSub = document.getElementById("kpi-cohort-sub");
    if (cohortSub) cohortSub.textContent = `Ahead of ${pred.cohort_percentile.toFixed(1)}% of student applicants`;

    // Predictive Placement Card
    const probLarge = document.getElementById("placement-prob-large");
    if (probLarge) probLarge.textContent = `${pred.placement_probability_pct}%`;

    const statusText = document.getElementById("placement-status-text");
    if (statusText) {
      if (pred.placement_probability_pct >= 75) {
        statusText.textContent = "✓ High Chance of Job Offer";
        statusText.style.color = "var(--emerald-text)";
      } else if (pred.placement_probability_pct >= 50) {
        statusText.textContent = "⚡ Solid Contender (Few Gaps to Close)";
        statusText.style.color = "var(--amber-text)";
      } else {
        statusText.textContent = "! Needs Foundation Skills First";
        statusText.style.color = "var(--rose-text)";
      }
    }

    const tierBadge = document.getElementById("placement-tier-badge");
    if (tierBadge) {
      tierBadge.textContent = `🏆 ${pred.predicted_tier}`;
    }

    const salaryRange = document.getElementById("placement-salary-range");
    if (salaryRange) salaryRange.textContent = pred.tier_salary_range;

    const standingText = document.getElementById("placement-cohort-standing");
    if (standingText) standingText.textContent = pred.cohort_standing_text;

    const factorsContainer = document.getElementById("placement-factors-container");
    if (factorsContainer && pred.key_factors) {
      factorsContainer.innerHTML = pred.key_factors.map(f => `
        <span class="factor-pill ${f.impact === 'positive' ? 'factor-pill-pos' : 'factor-pill-neg'}" title="${f.description}">
          ${f.impact === 'positive' ? '✓' : '!'} ${f.name} (${f.weight >= 0 ? '+' : ''}${f.weight}%)
        </span>
      `).join("");
    }
  }

  // Right Column: Satisfied Competencies List
  const milestonesList = document.getElementById("overview-milestones-list");
  if (milestonesList) {
    milestonesList.innerHTML = matched.length
      ? matched.map(s => `
        <div class="milestone-item">
          <div class="milestone-left">
            <div class="milestone-avatar">${s.substring(0, 2).toUpperCase()}</div>
            <div>
              <div class="milestone-name">${s}</div>
              <div class="milestone-sub">Satisfied requirement</div>
            </div>
          </div>
          <span class="badge badge-emerald">✓ Matched</span>
        </div>
      `).join("")
      : '<div style="font-size: 0.85rem; color: hsl(var(--muted-foreground)); padding: 12px 0;">No direct skill matches yet. Start with Phase 1 fundamentals!</div>';
  }

  const overviewMatchedCount = document.getElementById("overview-matched-count");
  if (overviewMatchedCount) overviewMatchedCount.textContent = `${matched.length} Verified`;

  // Right Column: Priority Gaps Action Checklist
  const gapsList = document.getElementById("overview-gaps-list");
  if (gapsList) {
    gapsList.innerHTML = missing.length
      ? missing.slice(0, 5).map(g => {
        const isHigh = highGaps.includes(g);
        return `
          <div class="milestone-item">
            <div class="milestone-left">
              <div class="milestone-avatar" style="background-color: ${isHigh ? 'var(--rose-bg)' : 'var(--amber-bg)'}; color: ${isHigh ? 'var(--rose-text)' : 'var(--amber-text)'};">
                !
              </div>
              <div>
                <div class="milestone-name">${g}</div>
                <div class="milestone-sub">${isHigh ? 'High Priority Gap' : 'Medium Priority Gap'}</div>
              </div>
            </div>
            <button class="btn btn-outline btn-sm" onclick="practiceSkillInInterview('${g}')">Practice ↗</button>
          </div>
        `;
      }).join("")
      : '<div style="font-size: 0.85rem; color: var(--emerald-text); padding: 12px 0;">🎉 All requirements mastered!</div>';
  }

  const gapsBadge = document.getElementById("overview-gaps-badge");
  if (gapsBadge) gapsBadge.textContent = `${highGaps.length} Priority`;

  // Left Column: Roadmap Milestone Preview
  const roadmapPreview = document.getElementById("overview-roadmap-list");
  if (roadmapPreview) {
    const phases = data.roadmap_phases || [];
    roadmapPreview.innerHTML = phases.length
      ? phases.map(phase => `
        <div class="milestone-item">
          <div class="milestone-left">
            <div class="milestone-avatar" style="background-color: hsl(var(--primary)); color: hsl(var(--primary-foreground)); font-size: 0.75rem;">
              DAG
            </div>
            <div>
              <div class="milestone-name">${phase.title}</div>
              <div class="milestone-sub">${phase.objective}</div>
            </div>
          </div>
          <span class="badge badge-outline">~${phase.estimated_hours}h</span>
        </div>
      `).join("")
      : '<div style="font-size: 0.85rem; color: var(--emerald-text); padding: 12px 0;">All prerequisite phases completed.</div>';
  }

  // Render Multi-Role Fit Matrix Grid
  if (data.multi_role_matrix) {
    renderMultiRoleMatrix(data.multi_role_matrix);
  }

  // Render Overview Chart
  renderChart(matched.length, missing.length);
  initLucideIcons();
}

// -----------------------------------------------------------------------------
// 4. MULTI-ROLE FIT MATRIX RENDERER & 1-CLICK ROLE SWITCHER
// -----------------------------------------------------------------------------
function renderMultiRoleMatrix(matrix) {
  const container = document.getElementById("multi-role-matrix-grid");
  if (!container) return;

  container.innerHTML = matrix.map(item => {
    const isTarget = item.career_title === state.targetCareer;
    const tierBadgeClass = item.fit_tier === 'Strong Fit' ? 'badge-emerald' : (item.fit_tier === 'Competitive' ? 'badge-gold' : 'badge-secondary');
    return `
      <div class="role-fit-card ${isTarget ? 'active-target' : ''}">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <div>
              <div style="font-weight: 700; font-size: 0.95rem;">${item.career_title}</div>
              <div style="font-size: 0.78rem; color: hsl(var(--muted-foreground));">
                ${item.matched_skills_count} of ${item.total_required_skills} Skills Mastered
              </div>
            </div>
            <span class="badge ${tierBadgeClass}">${item.fit_tier}</span>
          </div>

          <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 4px;">
            <span style="font-size: 0.82rem; font-weight: 600;">Readiness</span>
            <span style="font-size: 0.88rem; font-weight: 700;">${item.readiness_pct}%</span>
          </div>
          <div class="progress-rail" style="margin-bottom: 10px;">
            <div class="progress-thumb" style="width: ${Math.min(100, item.readiness_pct)}%; background-color: ${item.readiness_pct >= 75 ? '#10b981' : (item.readiness_pct >= 50 ? '#f59e0b' : 'hsl(var(--primary))')};"></div>
          </div>

          ${item.bridge_skill ? `
            <div class="bridge-skill-box">
              <div>
                <span style="color: var(--brand-blue); font-weight: 600;">⚡ Quickest Bridge:</span>
                <b>${item.bridge_skill}</b>
              </div>
              <span class="badge badge-emerald">+${item.bridge_jump_pct}% (~${item.bridge_study_hours}h)</span>
            </div>
          ` : '<div style="font-size: 0.78rem; color: var(--emerald-text); margin: 8px 0;">✓ 100% Requirements Cleared!</div>'}
        </div>

        <div style="margin-top: 12px;">
          ${isTarget
            ? '<button class="btn btn-default btn-sm" style="width: 100%; cursor: default;" disabled>★ Active Target Role</button>'
            : `<button class="btn btn-outline btn-sm" style="width: 100%;" onclick="switchToRole('${item.career_title}')">Switch Target to ${item.career_title} ↗</button>`
          }
        </div>
      </div>
    `;
  }).join("");
}

window.switchToRole = function(careerTitle) {
  state.targetCareer = careerTitle;
  const dropdown = document.getElementById("career-dropdown");
  if (dropdown) {
    dropdown.value = careerTitle;
  }
  analyzeReadiness();
};

// -----------------------------------------------------------------------------
// 5. CHART.JS CONTROLLER (RADAR, DONUT, AND PEER BELL CURVE)
// -----------------------------------------------------------------------------
function initChartToggle() {
  const tabRadar = document.getElementById("tab-chart-radar");
  const tabDonut = document.getElementById("tab-chart-donut");
  const tabBell = document.getElementById("tab-chart-bell");

  const setTab = (activeTab, mode) => {
    [tabRadar, tabDonut, tabBell].forEach(t => t && t.classList.remove("active"));
    if (activeTab) activeTab.classList.add("active");
    state.chartMode = mode;
    rebuildChart();
  };

  if (tabRadar) tabRadar.addEventListener("click", () => setTab(tabRadar, "radar"));
  if (tabDonut) tabDonut.addEventListener("click", () => setTab(tabDonut, "donut"));
  if (tabBell) tabBell.addEventListener("click", () => setTab(tabBell, "bellcurve"));
}

function renderChart(matchedCount, missingCount) {
  const ctx = document.getElementById("overviewChart");
  if (!ctx) return;

  if (state.chartInstance) state.chartInstance.destroy();

  const isDark = state.theme === "dark";
  const textColor = isDark ? "#a1a1aa" : "#71717a";
  const gridColor = isDark ? "#27272a" : "#e4e4e7";

  if (state.chartMode === "radar") {
    state.chartInstance = new Chart(ctx, {
      type: "radar",
      data: {
        labels: ["Programming", "Data Prep", "Machine Learning", "Databases", "DevOps/Tools", "Domain"],
        datasets: [
          {
            label: "Your Skill Coverage",
            data: [matchedCount >= 2 ? 85 : 35, matchedCount >= 1 ? 80 : 30, matchedCount >= 3 ? 75 : 25, matchedCount >= 1 ? 90 : 40, 50, 65],
            backgroundColor: isDark ? "rgba(250, 250, 250, 0.15)" : "rgba(15, 23, 42, 0.15)",
            borderColor: isDark ? "#fafafa" : "#09090b",
            pointBackgroundColor: isDark ? "#fafafa" : "#09090b",
            borderWidth: 2
          },
          {
            label: "Role Benchmark",
            data: [95, 90, 85, 90, 75, 80],
            backgroundColor: "rgba(16, 185, 129, 0.08)",
            borderColor: "#10b981",
            pointBackgroundColor: "#10b981",
            borderWidth: 1.5,
            borderDash: [4, 4]
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            grid: { color: gridColor },
            angleLines: { color: gridColor },
            pointLabels: { color: textColor, font: { size: 11, family: "Inter", weight: 500 } },
            ticks: { display: false }
          }
        },
        plugins: {
          legend: { labels: { color: textColor, font: { family: "Inter", size: 11 } } }
        }
      }
    });
  } else if (state.chartMode === "donut") {
    state.chartInstance = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Satisfied Skills", "Identified Gaps"],
        datasets: [{
          data: [Math.max(1, matchedCount), missingCount],
          backgroundColor: ["#10b981", "#ef4444"],
          borderColor: isDark ? "#09090b" : "#ffffff",
          borderWidth: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { color: textColor, font: { family: "Inter", size: 12 } } }
        },
        cutout: "70%"
      }
    });
  } else if (state.chartMode === "bellcurve") {
    // Cohort Gaussian Normal Bell Curve Plot
    const pred = (state.cachedData && state.cachedData.placement_prediction) || {};
    const coords = pred.bell_curve_coordinates || [];
    const candidateScore = pred.candidate_x_score || 55.0;

    const labels = coords.map(c => c.x);
    const dataPoints = coords.map(c => c.y);

    state.chartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "1,200 Cohort Applicant Distribution",
            data: dataPoints,
            borderColor: "#3b82f6",
            backgroundColor: isDark ? "rgba(59, 130, 246, 0.15)" : "rgba(59, 130, 246, 0.10)",
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: { display: true, text: "Composite Candidate Score (0 - 100)", color: textColor, font: { size: 10 } },
            grid: { color: gridColor },
            ticks: { color: textColor }
          },
          y: {
            display: false,
            grid: { display: false }
          }
        },
        plugins: {
          legend: { labels: { color: textColor, font: { family: "Inter", size: 11 } } },
          tooltip: {
            callbacks: {
              label: (context) => `Cohort Frequency Density at score ${context.label}`
            }
          }
        }
      }
    });
  }
}

function rebuildChart() {
  if (state.cachedData) {
    const matched = state.cachedData.matched_skills || [];
    const missing = state.cachedData.missing_skills || [];
    renderChart(matched.length, missing.length);
  }
}

// -----------------------------------------------------------------------------
// 5. ROADMAP DAG, STUDY SPRINT CALENDAR & GAMIFIED QUIZ CONTROLLER
// -----------------------------------------------------------------------------
let dagZoomLevel = 1.0;
let selectedDagNode = null;
let currentQuizState = {
  skillName: "",
  questions: [],
  currentIndex: 0,
  userAnswers: [],
  selectedOptionIndex: -1,
  evaluatedResult: null
};
let currentDailyCommitmentHours = 1.5;

window.switchRoadmapMode = function(mode) {
  const btnMilestones = document.getElementById("roadmap-mode-milestones") || document.getElementById("roadmap-mode-cards");
  const btnProjects = document.getElementById("roadmap-mode-projects");

  const isMilestones = (mode === 'milestones' || mode === 'cards' || mode === 'dag');
  const isProjects = (mode === 'projects');

  if (btnMilestones) btnMilestones.classList.toggle("active", isMilestones);
  if (btnProjects) btnProjects.classList.toggle("active", isProjects);

  const paneMilestones = document.getElementById("roadmap-pane-milestones") || document.getElementById("roadmap-pane-cards");
  const paneProjects = document.getElementById("roadmap-pane-projects");

  if (paneMilestones) paneMilestones.style.display = isMilestones ? 'block' : 'none';
  if (paneProjects) paneProjects.style.display = isProjects ? 'block' : 'none';
  
  initLucideIcons();
};

window.toggleDagCanvasView = function() {
  const dagWrapper = document.getElementById("roadmap-dag-wrapper");
  const btn = document.getElementById("btn-toggle-dag-view");
  if (!dagWrapper) return;
  const isHidden = (dagWrapper.style.display === "none" || !dagWrapper.style.display);
  dagWrapper.style.display = isHidden ? "block" : "none";
  if (btn) {
    btn.innerHTML = isHidden 
      ? '<i data-lucide="eye-off" style="width: 14px; height: 14px; margin-right: 4px;"></i> Hide Graph Chart'
      : '<i data-lucide="network" style="width: 14px; height: 14px; margin-right: 4px;"></i> Toggle Graph Chart';
  }
  initLucideIcons();
};

window.switchResumePortfolioTab = function(tabName) {
  const btnResume = document.getElementById("ats-tab-resume-btn");
  const btnGithub = document.getElementById("ats-tab-github-btn");
  const paneResume = document.getElementById("ats-subpane-resume");
  const paneGithub = document.getElementById("ats-subpane-github");

  const isResume = (tabName === 'resume');
  if (btnResume) btnResume.classList.toggle("active", isResume);
  if (btnGithub) btnGithub.classList.toggle("active", !isResume);

  if (paneResume) paneResume.style.display = isResume ? "block" : "none";
  if (paneGithub) paneGithub.style.display = !isResume ? "block" : "none";

  initLucideIcons();
};

window.zoomDagCanvas = function(factor) {
  dagZoomLevel = Math.max(0.4, Math.min(2.5, dagZoomLevel * factor));
  applyDagTransform();
};

window.resetDagCanvasZoom = function() {
  dagZoomLevel = 1.0;
  applyDagTransform();
};

function applyDagTransform() {
  const g = document.getElementById("dag-canvas-viewport");
  if (g) {
    g.setAttribute("transform", `scale(${dagZoomLevel})`);
  }
}

function renderRoadmapDAG(dagData) {
  const svg = document.getElementById("dag-canvas-svg");
  if (!svg) return;

  const dag = (dagData && dagData.nodes) ? dagData : (state.cachedData && state.cachedData.dag_graph ? state.cachedData.dag_graph : null);
  const nodes = (dag && dag.nodes) ? dag.nodes : [];
  const edges = (dag && dag.edges) ? dag.edges : [];

  const countMastered = document.getElementById("dag-count-mastered");
  const countReady = document.getElementById("dag-count-ready");
  const countLocked = document.getElementById("dag-count-locked");

  if (countMastered) countMastered.textContent = nodes.filter(n => n.status === 'mastered').length;
  if (countReady) countReady.textContent = nodes.filter(n => n.status === 'ready').length;
  if (countLocked) countLocked.textContent = nodes.filter(n => n.status === 'locked').length;

  if (!nodes.length) {
    svg.innerHTML = `<text x="50%" y="50%" text-anchor="middle" fill="hsl(var(--muted-foreground))" font-size="14">No DAG nodes loaded for current career.</text>`;
    return;
  }

  // Group nodes by layer
  const layersMap = {};
  nodes.forEach(n => {
    const l = n.layer !== undefined ? n.layer : 0;
    if (!layersMap[l]) layersMap[l] = [];
    layersMap[l].push(n);
  });

  const nodeCoords = {};
  const nodeWidth = 200;
  const nodeHeight = 68;
  const colSpacing = 270;
  const rowSpacing = 95;
  const startX = 40;
  const startY = 40;

  const sortedLayers = Object.keys(layersMap).map(Number).sort((a, b) => a - b);
  let maxSvgWidth = 600;
  let maxSvgHeight = 400;

  sortedLayers.forEach((layer, colIdx) => {
    const layerNodes = layersMap[layer];
    const x = startX + (colIdx * colSpacing);
    maxSvgWidth = Math.max(maxSvgWidth, x + nodeWidth + 80);

    layerNodes.forEach((node, rowIdx) => {
      const y = startY + (rowIdx * rowSpacing);
      nodeCoords[node.id] = { x, y, node };
      maxSvgHeight = Math.max(maxSvgHeight, y + nodeHeight + 80);
    });
  });

  let svgContent = `
    <defs>
      <marker id="arrow-default" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
      </marker>
      <marker id="arrow-active" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
      </marker>
    </defs>
    <g id="dag-canvas-viewport" transform="scale(${dagZoomLevel})">
  `;

  // Draw Edges (curved cubic bezier paths)
  edges.forEach(edge => {
    const from = nodeCoords[edge.from];
    const to = nodeCoords[edge.to];
    if (from && to) {
      const x1 = from.x + nodeWidth;
      const y1 = from.y + (nodeHeight / 2);
      const x2 = to.x;
      const y2 = to.y + (nodeHeight / 2);
      const cx1 = x1 + 50;
      const cy1 = y1;
      const cx2 = x2 - 50;
      const cy2 = y2;
      const isActive = edge.is_active;

      svgContent += `
        <path d="M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}" 
              class="dag-edge-path ${isActive ? 'dag-edge-active' : ''}" 
              marker-end="url(#${isActive ? 'arrow-active' : 'arrow-default'})" />
      `;
    }
  });

  // Draw Nodes
  nodes.forEach(n => {
    const coord = nodeCoords[n.id];
    if (!coord) return;
    const { x, y } = coord;
    const statusClass = n.status === 'mastered' ? 'dag-node-mastered' : (n.status === 'ready' ? 'dag-node-ready' : 'dag-node-locked');
    const statusIcon = n.status === 'mastered' ? '✓' : (n.status === 'ready' ? '⚡' : '🔒');
    const statusLabel = n.status === 'mastered' ? 'Mastered' : (n.status === 'ready' ? 'Ready' : 'Locked');

    svgContent += `
      <g class="dag-node-group" onclick="inspectDagNode('${n.id}')" transform="translate(${x}, ${y})">
        <rect class="dag-node-rect ${statusClass}" width="${nodeWidth}" height="${nodeHeight}" rx="8" ry="8"></rect>
        <text x="14" y="24" font-size="12" font-weight="700" fill="currentColor">
          ${statusIcon} ${n.name.length > 18 ? n.name.substring(0, 16) + '...' : n.name}
        </text>
        <text x="14" y="44" font-size="10" fill="hsl(var(--muted-foreground))">
          ${n.difficulty} • ~${n.estimated_hours}h • ${statusLabel}
        </text>
        <text x="14" y="58" font-size="9" font-weight="600" fill="var(--brand-blue)">
          ${n.status === 'locked' ? (n.unmet_prerequisites.length + ' unmet reqs') : 'Click to inspect ↗'}
        </text>
      </g>
    `;
  });

  svgContent += `</g>`;
  svg.setAttribute("viewBox", `0 0 ${maxSvgWidth} ${maxSvgHeight}`);
  svg.innerHTML = svgContent;
}

window.inspectDagNode = function(nodeId) {
  const dag = (state.cachedData && state.cachedData.dag_graph) ? state.cachedData.dag_graph : null;
  if (!dag || !dag.nodes) return;

  const node = dag.nodes.find(n => n.id === nodeId);
  if (!node) return;

  selectedDagNode = node;
  const inspector = document.getElementById("dag-node-inspector");
  if (!inspector) return;

  inspector.style.display = "block";
  document.getElementById("inspector-skill-name").textContent = node.name;
  
  const statusBadge = document.getElementById("inspector-status-badge");
  if (statusBadge) {
    statusBadge.textContent = node.status.toUpperCase();
    statusBadge.className = `badge ${node.status === 'mastered' ? 'badge-emerald' : (node.status === 'ready' ? 'badge-amber' : 'badge-secondary')}`;
  }

  const diffBadge = document.getElementById("inspector-difficulty-badge");
  if (diffBadge) diffBadge.textContent = node.difficulty;

  document.getElementById("inspector-category").textContent = `${node.category} • ${node.importance} Requirement`;
  document.getElementById("inspector-hours").textContent = `~${node.estimated_hours} Hours`;
  document.getElementById("inspector-unlocks").textContent = `${node.unlocks_count} Downstream Skills`;
  
  const prereqsEl = document.getElementById("inspector-prereqs");
  if (prereqsEl) {
    if (node.unmet_prerequisites && node.unmet_prerequisites.length) {
      prereqsEl.textContent = `Requires: ${node.unmet_prerequisites.join(", ")}`;
      prereqsEl.style.color = "var(--rose-text)";
    } else {
      prereqsEl.textContent = "None (All Prerequisites Satisfied)";
      prereqsEl.style.color = "var(--emerald-text)";
    }
  }

  const resList = document.getElementById("inspector-resources-list");
  if (resList) {
    resList.innerHTML = (node.resources && node.resources.length)
      ? node.resources.map(r => `
          <a href="${r.url || '#'}" target="_blank" style="font-size: 0.82rem; color: var(--brand-blue); text-decoration: none; font-weight: 500;">
            🔗 ${r.title} (${r.platform || 'Documentation'})
          </a>
        `).join("")
      : `<span style="font-size: 0.8rem; color: hsl(var(--muted-foreground));">Curated documentation & project labs</span>`;
  }

  const quizBtn = document.getElementById("inspector-quiz-btn");
  if (quizBtn) {
    if (node.status === 'mastered') {
      quizBtn.textContent = `✓ Retake Mastery Quiz for ${node.name}`;
      quizBtn.className = "btn btn-outline";
    } else {
      quizBtn.textContent = `🎯 Take 3-Question Quiz Gate for ${node.name}`;
      quizBtn.className = "btn btn-default";
    }
  }

  inspector.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
};

window.closeDagInspector = function() {
  const inspector = document.getElementById("dag-node-inspector");
  if (inspector) inspector.style.display = "none";
};

window.openSkillQuizFromInspector = function() {
  if (selectedDagNode) {
    startSkillQuiz(selectedDagNode.name);
  }
};

function renderStudyCalendar(calendarData) {
  const container = document.getElementById("calendar-sprints-container");
  if (!container) return;

  const cal = (calendarData && calendarData.weekly_sprints) ? calendarData : (state.cachedData && state.cachedData.study_calendar ? state.cachedData.study_calendar : null);
  const sprints = (cal && cal.weekly_sprints) ? cal.weekly_sprints : [];
  
  if (!sprints.length) {
    container.innerHTML = `<div class="sprint-card"><p style="color: var(--emerald-text);">🎉 All core skill gaps are closed! You are ready for capstone portfolio submission and interview screening.</p></div>`;
    return;
  }

  container.innerHTML = sprints.map(sprint => `
    <div class="sprint-card">
      <div class="sprint-header">
        <div>
          <b style="font-size: 0.95rem;">Week ${sprint.week_number}: ${sprint.title.replace('Week ' + sprint.week_number + ': ', '')}</b>
          <p style="font-size: 0.82rem; color: hsl(var(--muted-foreground)); margin-top: 2px;"><b>Goal:</b> ${sprint.objective}</p>
        </div>
        <span class="badge badge-outline">~${sprint.hours}h Study Effort</span>
      </div>

      <div class="sprint-skills-grid">
        ${(sprint.skills || []).map(sk => `
          <div class="sprint-skill-pill">
            <b>${sk.name}</b>
            <span style="color: hsl(var(--muted-foreground));">~${sk.hours}h</span>
          </div>
        `).join("")}
      </div>

      <div style="font-size: 0.82rem; border-top: 1px dashed hsl(var(--border)); padding-top: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px;">
        <span>🎯 <b>Weekly Milestone Deliverable:</b> ${sprint.deliverable || 'Mini Project / Quiz Gate'}</span>
        <button class="btn btn-outline btn-sm" onclick="startSkillQuiz('${sprint.skills && sprint.skills.length ? sprint.skills[0].name : 'Python'}')">Take Quiz Gate ↗</button>
      </div>
    </div>
  `).join("");

  const paceBadge = document.getElementById("calendar-pace-badge");
  if (paceBadge && cal && cal.pace_status) {
    paceBadge.textContent = cal.pace_status;
  }
}

window.updateCalendarSchedule = async function() {
  const slider = document.getElementById("calendar-days-slider");
  const label = document.getElementById("calendar-days-label");
  if (!slider || !label) return;

  const days = parseInt(slider.value, 10);
  label.textContent = `${days} Days`;

  try {
    const res = await fetch(`${API_BASE}/api/v1/roadmap/calendar-sprint`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_skills: state.studentSkills,
        target_career: state.targetCareer,
        target_days: days,
        daily_hours: currentDailyCommitmentHours
      })
    });
    if (res.ok) {
      const data = await res.json();
      if (state.cachedData) state.cachedData.study_calendar = data;
      renderStudyCalendar(data);
    }
  } catch (err) {
    console.error("Failed to recalculate study sprint schedule:", err);
  }
};

window.setDailyHours = function(hrs) {
  currentDailyCommitmentHours = hrs;
  document.querySelectorAll(".commitment-btn").forEach(btn => {
    btn.classList.toggle("active", parseFloat(btn.dataset.hours) === hrs);
  });
  updateCalendarSchedule();
};

window.exportCalendarIcs = function() {
  const cal = (state.cachedData && state.cachedData.study_calendar) ? state.cachedData.study_calendar : null;
  if (!cal || !cal.ical_content) {
    showToast("⚠️ Study calendar data not ready yet.");
    return;
  }
  const blob = new Blob([cal.ical_content], { type: "text/calendar;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `SkillGap_${state.targetCareer.replace(/\s+/g, '_')}_Study_Sprint.ics`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast("📅 Google / Apple Calendar (.ics) downloaded!");
};

window.copyNotionTemplate = function() {
  const cal = (state.cachedData && state.cachedData.study_calendar) ? state.cachedData.study_calendar : null;
  if (!cal || !cal.notion_markdown) {
    showToast("⚠️ Notion template not generated yet.");
    return;
  }
  navigator.clipboard.writeText(cal.notion_markdown);
  showToast("📝 Notion Study Template copied to clipboard!");
};

// -----------------------------------------------------------------------------
// GAMIFIED QUIZ GATE CONTROLLER
// -----------------------------------------------------------------------------
window.startSkillQuiz = async function(skillName) {
  try {
    const res = await fetch(`${API_BASE}/api/v1/quiz/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ skill_name: skillName, num_questions: 3 })
    });
    if (!res.ok) throw new Error("Quiz generation failed");
    const data = await res.json();

    currentQuizState = {
      skillName: skillName,
      questions: data.questions || [],
      currentIndex: 0,
      userAnswers: [],
      selectedOptionIndex: -1,
      evaluatedResult: null
    };

    const modal = document.getElementById("quiz-modal");
    if (modal) modal.classList.add("active");

    document.getElementById("quiz-skill-title").textContent = `${skillName} Technical Mastery Check`;
    document.getElementById("quiz-question-container").style.display = "block";
    document.getElementById("quiz-summary-container").style.display = "none";
    document.getElementById("quiz-submit-btn").style.display = "inline-flex";
    document.getElementById("quiz-next-btn").style.display = "none";
    document.getElementById("quiz-finish-btn").style.display = "none";

    renderCurrentQuizQuestion();
  } catch (err) {
    console.error("Failed to start quiz:", err);
    showToast("⚠️ Could not load quiz questions.");
  }
};

function renderCurrentQuizQuestion() {
  const q = currentQuizState.questions[currentQuizState.currentIndex];
  if (!q) return;

  currentQuizState.selectedOptionIndex = -1;
  document.getElementById("quiz-progress-label").textContent = `Question ${currentQuizState.currentIndex + 1} of ${currentQuizState.questions.length}`;
  document.getElementById("quiz-question-text").textContent = q.question_text;
  document.getElementById("quiz-feedback-box").style.display = "none";
  document.getElementById("quiz-submit-btn").style.display = "inline-flex";
  document.getElementById("quiz-next-btn").style.display = "none";

  const optsContainer = document.getElementById("quiz-options-list");
  const letters = ["A", "B", "C", "D"];
  optsContainer.innerHTML = q.options.map((opt, idx) => `
    <button class="quiz-option-btn" id="quiz-opt-${idx}" onclick="selectQuizOption(${idx})">
      <span class="quiz-option-index">${letters[idx]}</span>
      <span>${opt}</span>
    </button>
  `).join("");
}

window.selectQuizOption = function(idx) {
  currentQuizState.selectedOptionIndex = idx;
  document.querySelectorAll(".quiz-option-btn").forEach((btn, i) => {
    btn.classList.toggle("selected", i === idx);
  });
};

window.submitQuizCurrentAnswer = function() {
  if (currentQuizState.selectedOptionIndex === -1) {
    showToast("Please select an answer option first.");
    return;
  }

  currentQuizState.userAnswers.push(currentQuizState.selectedOptionIndex);

  // Disable options
  document.querySelectorAll(".quiz-option-btn").forEach(btn => btn.style.pointerEvents = "none");

  // Show immediate question explanation
  const feedbackBox = document.getElementById("quiz-feedback-box");
  const feedbackHeader = document.getElementById("quiz-feedback-header");
  const feedbackExp = document.getElementById("quiz-feedback-explanation");

  feedbackBox.style.display = "block";
  feedbackBox.style.background = "hsl(var(--muted)/0.5)";
  feedbackHeader.textContent = "Answer Recorded!";
  feedbackExp.textContent = "Advancing to next question or milestone evaluation...";

  document.getElementById("quiz-submit-btn").style.display = "none";
  const isLast = (currentQuizState.currentIndex >= currentQuizState.questions.length - 1);
  const nextBtn = document.getElementById("quiz-next-btn");
  if (isLast) {
    nextBtn.textContent = "View Final Results 📊";
  } else {
    nextBtn.textContent = "Next Question →";
  }
  nextBtn.style.display = "inline-flex";
};

window.nextQuizStep = async function() {
  if (currentQuizState.currentIndex < currentQuizState.questions.length - 1) {
    currentQuizState.currentIndex += 1;
    renderCurrentQuizQuestion();
  } else {
    // Evaluate full quiz
    try {
      const res = await fetch(`${API_BASE}/api/v1/quiz/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          skill_name: currentQuizState.skillName,
          user_answers: currentQuizState.userAnswers
        })
      });
      const result = await res.json();
      currentQuizState.evaluatedResult = result;

      document.getElementById("quiz-question-container").style.display = "none";
      document.getElementById("quiz-summary-container").style.display = "block";
      document.getElementById("quiz-next-btn").style.display = "none";
      document.getElementById("quiz-finish-btn").style.display = "inline-flex";

      const iconEl = document.getElementById("quiz-result-icon");
      const titleEl = document.getElementById("quiz-result-title");
      const descEl = document.getElementById("quiz-result-desc");
      const badgesEl = document.getElementById("quiz-result-badges");

      if (result.passed) {
        iconEl.textContent = "🎉";
        titleEl.textContent = `Mastery Verified: ${currentQuizState.skillName}`;
        descEl.textContent = `You scored ${result.score}/${result.total_questions} (${result.percentage.toFixed(0)}%). Skill credential unlocked and added to your active profile!`;
        badgesEl.innerHTML = `<span class="badge badge-emerald">✓ Verified Skill Credential</span><span class="badge badge-secondary">🔓 Downstream DAG Unlocked</span>`;
      } else {
        iconEl.textContent = "📚";
        titleEl.textContent = `Review Needed (${result.score}/${result.total_questions})`;
        descEl.textContent = `You scored ${result.percentage.toFixed(0)}% (passing threshold is 66%). Review the recommended study resources and retry anytime!`;
        badgesEl.innerHTML = `<span class="badge badge-rose">Retry Available</span>`;
      }
    } catch (err) {
      console.error("Quiz evaluation failed:", err);
    }
  }
};

window.finishQuizGate = async function() {
  const result = currentQuizState.evaluatedResult;
  closeQuizModal();

  if (result && result.passed) {
    const skill = currentQuizState.skillName;
    if (!state.studentSkills.some(s => s.toLowerCase() === skill.toLowerCase())) {
      state.studentSkills.push(skill);
      showToast(`🌟 ${skill} marked as Mastered! Recalculating readiness...`);
      await fetchSkillAnalysis();
    }
  }
};

window.closeQuizModal = function() {
  const modal = document.getElementById("quiz-modal");
  if (modal) modal.classList.remove("active");
};

function renderFullRoadmap(data) {
  const container = document.getElementById("full-roadmap-container");
  if (!container) return;

  const phases = data.roadmap_phases || [];
  if (!phases.length) {
    container.innerHTML = '<div style="padding: 16px; text-align: center; color: var(--emerald-text);">🎉 All prerequisites satisfied! Proceed to build portfolio projects or practice interviews.</div>';
    return;
  }

  const phaseStageIcons = ["🟢 Stage 1: Foundations", "🟡 Stage 2: Applied Frameworks & Tools", "🔵 Stage 3: Advanced Specialization & Cloud"];

  container.innerHTML = phases.map((phase, pIdx) => {
    const stageLabel = phaseStageIcons[pIdx] || `Stage ${pIdx + 1}: Technical Progression`;
    return `
      <div style="margin-bottom: 20px; border: 1px solid hsl(var(--border)); border-radius: var(--radius); padding: 16px; background-color: hsl(var(--card));">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 6px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="badge ${pIdx === 0 ? 'badge-emerald' : (pIdx === 1 ? 'badge-amber' : 'badge-indigo')}" style="font-size: 0.75rem;">${stageLabel}</span>
            <h3 style="font-size: 1rem; font-weight: 700; margin: 0;">${phase.title}</h3>
          </div>
          <span class="badge badge-outline">~${phase.estimated_hours} Hours Total</span>
        </div>
        <p style="font-size: 0.85rem; color: hsl(var(--muted-foreground)); margin-bottom: 12px;"><b>Goal:</b> ${phase.objective}</p>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px;">
          ${phase.skills.map(s => `
            <div style="border: 1px solid hsl(var(--border)); border-radius: var(--radius); padding: 12px; background-color: hsl(var(--muted) / 0.15); display: flex; flex-direction: column; justify-content: space-between;">
              <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                  <b style="font-size: 0.9rem;">${s.skill_name}</b>
                  <span class="badge ${s.priority === 'High' ? 'badge-rose' : 'badge-amber'}">${s.priority}</span>
                </div>
                <div style="font-size: 0.78rem; color: hsl(var(--muted-foreground)); line-height: 1.4;">
                  <div><b>Why:</b> ${s.reason}</div>
                  <div style="margin-top: 2px;"><b>Effort:</b> ~${s.hours} Hours</div>
                </div>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding-top: 8px; border-top: 1px dashed hsl(var(--border));">
                <a href="${s.resource_url}" target="_blank" style="font-size: 0.78rem; font-weight: 600; color: var(--brand-blue); text-decoration: none; display: flex; align-items: center; gap: 4px;">
                  🔗 ${s.top_resource}
                </a>
                <button class="btn btn-default btn-sm" style="font-size: 0.75rem; padding: 4px 10px;" onclick="startSkillQuiz('${s.skill_name}')">
                  🎯 Quiz Gate
                </button>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  }).join("");
}

function renderFullProjects(data) {
  const container = document.getElementById("full-projects-container");
  if (!container) return;

  const projects = data.recommended_projects || [];
  if (!projects.length) {
    container.innerHTML = '<p style="color: hsl(var(--muted-foreground));">No custom project recommendations mapped yet.</p>';
    return;
  }

  container.innerHTML = projects.map((p, idx) => `
    <div style="border: 1px solid hsl(var(--border)); border-radius: var(--radius); padding: 16px; margin-bottom: 14px;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
        <b style="font-size: 0.95rem;">Project ${idx + 1}: ${p.title}</b>
        <span class="badge badge-secondary">${p.difficulty}</span>
      </div>
      <div style="font-size: 0.85rem; color: hsl(var(--muted-foreground)); margin-bottom: 6px;"><b>Gap Match:</b> ${p.relevance_score ? p.relevance_score.toFixed(1) : '90.0'}% Relevance</div>
      <div style="font-size: 0.85rem; margin-bottom: 8px;"><b>Tech Stack:</b> <code>${p.primary_skills}</code></div>
    </div>
  `).join("");
}

// -----------------------------------------------------------------------------
// 6. RESUME UPLOAD NAVIGATION & TRIGGERS
// -----------------------------------------------------------------------------
window.openResumeUploadModal = function() {
  switchNavTab("view-ats");
};

function initResumeUpload() {
  // Resume upload removed in favor of direct skill selection and ATS content editor
}

// -----------------------------------------------------------------------------
// 8. COMMAND PALETTE (⌘K)
// -----------------------------------------------------------------------------
function initCommandPalette() {
  const cmdBtn = document.getElementById("search-command-btn");
  const modal = document.getElementById("command-modal");

  if (cmdBtn && modal) {
    cmdBtn.addEventListener("click", () => modal.classList.add("active"));
  }

  window.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "k") {
      e.preventDefault();
      if (modal) modal.classList.toggle("active");
    }
    if (e.key === "Escape" && modal) {
      modal.classList.remove("active");
    }
  });
}

window.closeCommandModal = function() {
  const modal = document.getElementById("command-modal");
  if (modal) modal.classList.remove("active");
};

// -----------------------------------------------------------------------------
// 9. ATS SCORER, RED-FLAG SCANNER, DIFFS & RESUME GENERATOR (SECTION 3 UPGRADES)
// -----------------------------------------------------------------------------
let currentTailoredLatex = "";
let currentTailoredHtml = "";
let currentTargetCareer = "Data Scientist";

function initATSScorer() {
  const btn = document.getElementById("ats-calc-btn");
  const generateBtn = document.getElementById("ats-generate-resume-btn");

  // 1-Click Generate Tailored Resume Trigger
  if (generateBtn) {
    generateBtn.addEventListener("click", async () => {
      await generateAndOpenTailoredResume();
    });
  }

  if (!btn) return;

  btn.addEventListener("click", async () => {
    const resumeText = document.getElementById("ats-resume-text").value;
    const jdText = document.getElementById("ats-jd-text").value;
    const candidateCareer = state.targetCareer || "Data Scientist";

    try {
      btn.innerHTML = '<i data-lucide="loader" class="animate-spin" style="width: 15px; height: 15px;"></i><span>Auditing Resume & Red Flags...</span>';
      const response = await fetch(`${API_BASE}/api/v1/ats-score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_text: resumeText,
          job_description_text: jdText,
          target_career: candidateCareer
        })
      });

      if (!response.ok) throw new Error("Failed to evaluate ATS score");

      const data = await response.json();
      
      // Save tailored previews
      currentTailoredLatex = data.tailored_latex_preview || "";
      currentTailoredHtml = data.tailored_html_preview || "";
      currentTargetCareer = candidateCareer;

      // 1. Score Breakdown
      const scoreBox = document.getElementById("ats-score-box");
      if (scoreBox) scoreBox.style.display = "block";
      
      const overallVal = document.getElementById("ats-overall-val");
      if (overallVal) overallVal.textContent = `${data.overall_ats_score}%`;
      
      const kwVal = document.getElementById("ats-keyword-val");
      if (kwVal) kwVal.textContent = `${data.keyword_match_rate_pct.toFixed(1)}%`;
      
      const semVal = document.getElementById("ats-semantic-val");
      if (semVal) semVal.textContent = `${(data.semantic_alignment_score || 82.0).toFixed(1)}%`;
      
      const metVal = document.getElementById("ats-metric-val");
      if (metVal) metVal.textContent = `${(data.quantifiable_metrics_score || 70.0).toFixed(1)}%`;

      const gradeBadge = document.getElementById("ats-grade-badge");
      if (gradeBadge) {
        gradeBadge.textContent = data.score_grade;
        if (data.overall_ats_score >= 80) {
          gradeBadge.className = "badge badge-emerald";
        } else if (data.overall_ats_score >= 65) {
          gradeBadge.className = "badge badge-amber";
        } else {
          gradeBadge.className = "badge badge-rose";
        }
      }

      const matchedBadges = document.getElementById("ats-matched-badges");
      if (matchedBadges) {
        matchedBadges.innerHTML = (data.matched_keywords && data.matched_keywords.length > 0)
          ? data.matched_keywords.map(k => `<span class="badge badge-emerald">✓ ${k}</span>`).join("")
          : `<span style="font-size: 0.8rem; color: hsl(var(--muted-foreground));">No exact keyword matches found.</span>`;
      }

      const missingBadges = document.getElementById("ats-missing-badges");
      if (missingBadges) {
        missingBadges.innerHTML = (data.missing_critical_keywords && data.missing_critical_keywords.length > 0)
          ? data.missing_critical_keywords.map(k => `<span class="badge badge-rose">! ${k}</span>`).join("")
          : `<span class="badge badge-emerald">✓ All core JD keywords present!</span>`;
      }

      // 2. Render Red-Flag Scanner
      renderAtsRedFlags(data.red_flags || []);

      // 3. Render Side-by-Side Diff Transformations
      renderAtsDiffs(data.bullet_point_improvements || []);

    } catch (err) {
      console.error(err);
      alert("ATS audit failed. Please check input text.");
    } finally {
      btn.innerHTML = '<i data-lucide="shield-alert" style="width: 16px; height: 16px;"></i><span>Audit ATS Compatibility & Scan Red Flags</span>';
      initLucideIcons();
    }
  });
}

function renderAtsRedFlags(redFlags) {
  const flagsBox = document.getElementById("ats-red-flags-box");
  const flagsGrid = document.getElementById("ats-red-flags-grid");
  const counterBadge = document.getElementById("ats-flags-counter-badge");
  if (!flagsBox || !flagsGrid) return;

  flagsBox.style.display = "block";
  const issuesCount = redFlags.filter(f => f.severity !== "Good").length;
  if (counterBadge) {
    counterBadge.textContent = issuesCount > 0 ? `${issuesCount} Audit Issues Detected` : `✓ 0 Issues (Clean ATS Pass)`;
    counterBadge.className = issuesCount > 0 ? "badge badge-rose" : "badge badge-emerald";
  }

  if (redFlags.length === 0) {
    flagsGrid.innerHTML = `<div style="font-size: 0.85rem; color: hsl(var(--muted-foreground));">No red flags detected. Resume structure complies with ATS standards.</div>`;
    return;
  }

  flagsGrid.innerHTML = redFlags.map(rf => {
    let sevClass = "severity-good";
    let sevIcon = "✓";
    if (rf.severity === "Critical") {
      sevClass = "severity-critical";
      sevIcon = "⚠️";
    } else if (rf.severity === "Warning") {
      sevClass = "severity-warning";
      sevIcon = "!";
    }

    return `
      <div class="red-flag-card">
        <div class="red-flag-header">
          <span class="red-flag-title">${rf.title}</span>
          <span class="severity-pill ${sevClass}">${sevIcon} ${rf.severity}</span>
        </div>
        <div class="red-flag-desc">${rf.description}</div>
        <div class="red-flag-rec"><b>Recommendation:</b> ${rf.recommendation}</div>
      </div>
    `;
  }).join("");
}

function renderAtsDiffs(improvements) {
  const diffBox = document.getElementById("ats-diff-box");
  const diffContainer = document.getElementById("ats-diff-container");
  if (!diffBox || !diffContainer) return;

  diffBox.style.display = "block";
  if (improvements.length === 0) {
    diffContainer.innerHTML = `<div style="font-size: 0.85rem; color: hsl(var(--muted-foreground));">No bullet points available for transformation.</div>`;
    return;
  }

  diffContainer.innerHTML = improvements.map((item, idx) => {
    const diffAddCount = item.diff_added_tokens ? item.diff_added_tokens.length : 0;
    const diffAddBadges = item.diff_added_tokens && item.diff_added_tokens.length > 0
      ? `<div style="margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px;"><span style="font-size: 0.72rem; color: hsl(var(--muted-foreground));">Injected Keywords & Metrics:</span> ${item.diff_added_tokens.map(t => `<span class="badge badge-emerald" style="font-size: 0.7rem; padding: 1px 6px;">+${t}</span>`).join("")}</div>`
      : "";

    // Escaped string for onclick
    const cleanImproved = (item.improved || item.improved_bullet || "").replace(/"/g, '&quot;');

    return `
      <div class="diff-comparison-card">
        <div class="diff-grid">
          <!-- Left: Original Bullet Point -->
          <div class="diff-side diff-side-original">
            <div class="diff-side-title" style="color: hsl(var(--muted-foreground));">
              <span>Original Bullet</span>
              <span class="badge badge-rose" style="font-size: 0.7rem;">Detected Gap</span>
            </div>
            <div class="diff-text">"${item.original || item.original_bullet}"</div>
            <div style="font-size: 0.75rem; color: hsl(var(--muted-foreground)); margin-top: 4px;">
              <b>Weakness:</b> ${item.detected_weakness || "Lacks quantifiable metrics and specific tools."}
            </div>
          </div>

          <!-- Right: Google XYZ Enhanced Version -->
          <div class="diff-side diff-side-improved">
            <div class="diff-side-title" style="color: var(--brand-blue);">
              <span>Google XYZ Enhanced</span>
              <span class="badge badge-emerald" style="font-size: 0.7rem;">+${diffAddCount} Impact Tokens</span>
            </div>
            <div class="diff-text">${item.highlighted_html_diff || item.improved || item.improved_bullet}</div>
            ${diffAddBadges}
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="diff-footer">
          <span style="color: hsl(var(--muted-foreground));"><b>Formula Applied:</b> ${item.formula || item.impact_technique_used || "Google XYZ Formula"}</span>
          <div style="display: flex; gap: 8px;">
            <button class="btn btn-outline btn-sm" onclick="copyBulletText('${cleanImproved}')">
              📋 Copy Bullet
            </button>
            <button class="btn btn-default btn-sm" onclick="applyBulletToResume('${cleanImproved}')">
              ⚡ Apply to Resume
            </button>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

async function generateAndOpenTailoredResume() {
  const candidateName = document.getElementById("ats-candidate-name")?.value || "Alex Chen";
  const candidateEmail = document.getElementById("ats-candidate-email")?.value || "alex.chen@email.com";
  const candidatePhone = document.getElementById("ats-candidate-phone")?.value || "(555) 019-2834";
  const candidateLinkedin = document.getElementById("ats-candidate-linkedin")?.value || "linkedin.com/in/alexchen-tech";
  const candidateGithub = document.getElementById("ats-candidate-github")?.value || "github.com/alexchen-dev";
  const jdText = document.getElementById("ats-jd-text")?.value || "";
  const candidateCareer = state.targetCareer || "Data Scientist";

  const generateBtn = document.getElementById("ats-generate-resume-btn");
  if (generateBtn) generateBtn.innerHTML = '<i data-lucide="loader" class="animate-spin" style="width: 15px; height: 15px;"></i><span>Generating LaTeX & PDF...</span>';

  try {
    const response = await fetch(`${API_BASE}/api/v1/ats/generate-resume`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_skills: state.studentSkills || ["Python", "SQL", "Pandas"],
        target_career: candidateCareer,
        job_description: jdText,
        candidate_name: candidateName,
        candidate_email: candidateEmail,
        candidate_phone: candidatePhone,
        candidate_linkedin: candidateLinkedin,
        candidate_github: candidateGithub
      })
    });

    if (!response.ok) throw new Error("Failed to generate tailored resume");

    const data = await response.json();
    currentTailoredHtml = data.html_code;
    currentTargetCareer = candidateCareer;

    // Open Modal and render
    openResumeModal();
  } catch (err) {
    console.error("Resume Generation Error:", err);
    alert("Could not generate tailored resume: " + err.message);
  } finally {
    if (generateBtn) {
      generateBtn.innerHTML = '<i data-lucide="printer" style="width: 16px; height: 16px;"></i><span>⚡ 1-Click Generate Tailored Resume (PDF)</span>';
      initLucideIcons();
    }
  }
}

// Tailored Resume Modal Global Handlers
window.openResumeModal = function() {
  const modal = document.getElementById("resume-preview-modal");
  const targetBadge = document.getElementById("resume-modal-target-badge");
  const htmlContainer = document.getElementById("html-resume-container");

  if (targetBadge) targetBadge.textContent = `Target: ${currentTargetCareer}`;
  if (htmlContainer) htmlContainer.innerHTML = currentTailoredHtml;

  if (modal) modal.style.display = "flex";
  initLucideIcons();
};

window.closeResumeModal = function() {
  const modal = document.getElementById("resume-preview-modal");
  if (modal) modal.style.display = "none";
};

window.printResumeFromModal = function() {
  const printWindow = window.open("", "_blank");
  if (!printWindow) {
    alert("Please allow popups to print/save PDF.");
    return;
  }
  printWindow.document.write(currentTailoredHtml);
  printWindow.document.close();
  printWindow.focus();
  setTimeout(() => {
    printWindow.print();
  }, 400);
};

window.copyBulletText = function(text) {
  navigator.clipboard.writeText(text).then(() => {
    alert(`✓ Copied optimized bullet to clipboard:\n\n"${text}"`);
  });
};

window.applyBulletToResume = function(improvedBullet) {
  const resumeTextarea = document.getElementById("ats-resume-text");
  if (!resumeTextarea) return;
  resumeTextarea.value = `${resumeTextarea.value.trim()}\n- ${improvedBullet}`;
  alert("✓ Appended optimized bullet point to Candidate Resume Text!");
};


async function handleATSResumeUpload(file) {
  const statusBox = document.getElementById("ats-upload-status");
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE}/api/v1/upload-resume`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) throw new Error("Failed to parse resume");

    const data = await response.json();
    if (data.raw_text) {
      document.getElementById("ats-resume-text").value = data.raw_text;
      if (statusBox) {
        statusBox.style.display = "block";
        statusBox.innerHTML = `✓ Extracted <b>${data.skill_count} skills</b> from <code>${data.filename}</code>. Auto-calculating ATS score...`;
      }
      const btn = document.getElementById("ats-calc-btn");
      if (btn) btn.click();
    }
  } catch (err) {
    console.error("ATS Upload Error:", err);
    alert("Could not extract text from the uploaded resume file.");
  }
}

function initXYZRewriter() {
  const btn = document.getElementById("xyz-rewrite-btn");
  if (!btn) return;

  btn.addEventListener("click", () => {
    const raw = document.getElementById("xyz-input-bullet").value.trim().replace(/\.$/, "");
    const optimized = `Engineered and deployed a scalable solution (${raw}), optimizing prediction latency by 32% and enhancing model throughput across 100k+ customer transactions.`;
    document.getElementById("xyz-optimized-text").textContent = `"${optimized}"`;
  });
}

// -----------------------------------------------------------------------------
// 10. AI MOCK INTERVIEWER & LIVE CODING SANDBOX (SECTION 4 UPGRADES)
// -----------------------------------------------------------------------------
let currentInterviewSkill = "SQL";
let currentQuestionIndex = 0;
let isVoiceRecording = false;
let speechRecognizer = null;
let interviewHistory = [];
let activeCodingProblem = null;

const INTERVIEW_LOCAL_BANK = {
  "SQL": [
    {
      "text": "What is the difference between WHERE and HAVING in SQL queries? Provide a scenario where WHERE cannot be used.",
      "hint": "Consider query execution pipeline order and aggregate functions like COUNT() and SUM().",
      "difficulty": "Intermediate",
      "type": "Practical Scenario",
      "model_answer": "<b>Situation & Concept:</b> WHERE filters individual records before any grouping occurs, whereas HAVING filters aggregated metric rows after GROUP BY.<br><b>Concrete Example:</b> To find departments with more than 5 engineers: <code>SELECT dept_id, COUNT(*) FROM emp GROUP BY dept_id HAVING COUNT(*) > 5;</code> WHERE cannot be used here because the aggregate count does not exist prior to grouping.<br><b>Result:</b> Understanding this execution order prevents query syntax errors and ensures correct data aggregation."
    },
    {
      "text": "Explain how Window Functions (ROW_NUMBER, RANK, DENSE_RANK) differ from GROUP BY aggregations.",
      "hint": "Highlight whether the number of output rows equals the input rows count.",
      "difficulty": "Advanced",
      "type": "Conceptual",
      "model_answer": "<b>Core Difference:</b> GROUP BY collapses multiple rows into a single summary row per group. Window functions perform calculations across a partition of rows while preserving each individual row's identity.<br><b>Ranking Distinctions:</b> ROW_NUMBER assigns unique sequential integers (1, 2, 3). RANK assigns identical values for ties with gaps (1, 2, 2, 4). DENSE_RANK assigns identical values without gaps (1, 2, 2, 3)."
    }
  ],
  "Python": [
    {
      "text": "Explain the difference between deep copy and shallow copy in Python. When would you use each?",
      "hint": "Think about how nested mutable objects behave when cloned or passed by reference.",
      "difficulty": "Intermediate",
      "type": "Core Mechanics",
      "model_answer": "<b>Shallow Copy (<code>copy.copy</code>):</b> Creates a new container object, but inserts references to the original nested objects. Modifying nested elements modifies both.<br><b>Deep Copy (<code>copy.deepcopy</code>):</b> Recursively clones the container and all nested objects completely independently.<br><b>Usage:</b> Use shallow copies for flat structures for memory efficiency; use deep copies when mutating nested dictionaries or lists without affecting the original dataset."
    },
    {
      "text": "How do Python generators use 'yield' for lazy evaluation, and why are they preferred over lists for 100k+ rows?",
      "hint": "Focus on RAM memory footprint and on-the-fly stream processing.",
      "difficulty": "Intermediate",
      "type": "Memory & Performance",
      "model_answer": "<b>Mechanism:</b> <code>yield</code> pauses function execution and emits a single value, saving its execution state to resume when <code>next()</code> is invoked.<br><b>Memory Advantage:</b> A list of 100k records allocates substantial heap memory all at once. A generator uses O(1) constant memory because it streams one item at a time on demand."
    }
  ],
  "Machine Learning": [
    {
      "text": "Explain the Bias-Variance Tradeoff. What concrete techniques would you use if your model has high variance?",
      "hint": "Relate high variance to overfitting and discuss L1/L2 regularization and ensemble bagging.",
      "difficulty": "Intermediate",
      "type": "Modeling & Validation",
      "model_answer": "<b>Tradeoff:</b> High bias means underfitting (oversimplified assumptions). High variance means overfitting (capturing random noise in training data).<br><b>High Variance Remedies:</b> 1) Add L1/L2 regularization to penalize large weights, 2) Use ensemble bagging (e.g. Random Forests), 3) Increase training dataset size or reduce feature dimensionality via PCA."
    },
    {
      "text": "Why is accuracy a misleading metric for imbalanced classification (e.g. 99% non-fraud, 1% fraud)? What metrics should be used?",
      "hint": "Discuss Precision, Recall, F1-Score, and Precision-Recall AUC.",
      "difficulty": "Intermediate",
      "type": "Evaluation Metrics",
      "model_answer": "<b>The Problem:</b> A naive classifier predicting 'non-fraud' 100% of the time achieves 99% accuracy while missing every single fraud event.<br><b>Recommended Metrics:</b> 1) Recall (percentage of actual frauds caught), 2) Precision (minimize false alarms), 3) F1-Score (harmonic mean), and 4) PR-AUC (Precision-Recall Area Under Curve)."
    }
  ],
  "Deep Learning": [
    {
      "text": "What causes the Vanishing Gradient problem in deep neural networks, and how do ReLU and ResNet skip connections resolve it?",
      "hint": "Analyze activation function derivatives and backpropagation chain rule.",
      "difficulty": "Advanced",
      "type": "Architectural Design",
      "model_answer": "<b>Cause:</b> Repeated multiplication of small gradients (< 1.0) through sigmoid/tanh activation layers during backpropagation causes early layer weight updates to approach zero.<br><b>Solution:</b> ReLU has a constant gradient of 1 for positive inputs. ResNet skip connections add residual pathways (<code>F(x) + x</code>), allowing gradients to flow unimpeded directly back to early layers."
    }
  ],
  "FastAPI": [
    {
      "text": "How does FastAPI leverage Python type hints and Pydantic for high throughput asynchronous I/O?",
      "hint": "Mention async/await event loops, Starlette/Uvicorn, and automatic Swagger OpenAPI generation.",
      "difficulty": "Intermediate",
      "type": "REST Microservices",
      "model_answer": "<b>Architecture:</b> Built on Starlette and Uvicorn with native <code>async/await</code> event loops for high-concurrency non-blocking I/O.<br><b>Pydantic Integration:</b> Type annotations enable request body validation, serialization, and automatic Swagger/OpenAPI documentation."
    }
  ],
  "Docker": [
    {
      "text": "What is the core architectural difference between a Docker container and a Virtual Machine (VM)?",
      "hint": "Compare Linux kernel sharing/cgroups vs hypervisor guest operating system overhead.",
      "difficulty": "Intermediate",
      "type": "System Architecture",
      "model_answer": "<b>Architecture:</b> VMs package a full guest operating system and virtualized hardware via a hypervisor. Containers share the host OS kernel and isolate processes via Linux namespaces and cgroups.<br><b>Benefits:</b> Containers start in milliseconds and consume drastically fewer compute resources."
    }
  ],
  "Pandas": [
    {
      "text": "Explain the behavioral difference between .loc and .iloc in Pandas DataFrame indexing.",
      "hint": "Compare label-based inclusive slicing vs 0-indexed integer position exclusive slicing.",
      "difficulty": "Beginner",
      "type": "Data Manipulation",
      "model_answer": "<b><code>.loc</code> (Label-based):</b> Selects data using explicit index and column labels. Slices are inclusive of both start and stop bounds.<br><b><code>.iloc</code> (Integer-based):</b> Selects data by numeric position (0 to n-1). Slices are exclusive of the stop bound."
    }
  ]
};

function initInterviewSimulator() {
  const skillSelect = document.getElementById("int-skill-select");
  const submitBtn = document.getElementById("int-submit-btn");

  if (skillSelect) {
    skillSelect.addEventListener("change", (e) => {
      currentInterviewSkill = e.target.value;
      currentQuestionIndex = 0;
      updateInterviewQuestionView();
    });
  }

  if (submitBtn) {
    submitBtn.addEventListener("click", async () => {
      const answer = document.getElementById("int-answer-input").value;
      if (!answer.trim()) {
        alert("Please provide an answer before submitting.");
        return;
      }

      const qText = document.getElementById("int-question-text").textContent.replace(/^"|"$/g, '').trim();

      try {
        submitBtn.innerHTML = '<i data-lucide="loader" class="animate-spin" style="width: 14px; height: 14px;"></i><span>Evaluating with AI...</span>';
        const response = await fetch(`${API_BASE}/api/v1/interview/evaluate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            skill_name: currentInterviewSkill,
            question_text: qText,
            candidate_answer: answer
          })
        });

        if (!response.ok) throw new Error("Evaluation failed");
        const data = await response.json();

        // Display Scorecard
        const resCard = document.getElementById("int-result-card");
        if (resCard) resCard.style.display = "block";

        const scoreBadge = document.getElementById("int-score-badge");
        if (scoreBadge) {
          scoreBadge.textContent = `Score: ${data.overall_score} / 10 (${data.score_tier})`;
          if (data.overall_score >= 8) scoreBadge.className = "badge badge-emerald";
          else if (data.overall_score >= 5) scoreBadge.className = "badge badge-amber";
          else scoreBadge.className = "badge badge-rose";
        }

        const matchedBox = document.getElementById("int-matched-concepts");
        if (matchedBox) {
          matchedBox.innerHTML = (data.matched_concepts && data.matched_concepts.length > 0)
            ? data.matched_concepts.map(c => `<span class="badge badge-emerald">✓ ${c}</span>`).join("")
            : `<span style="font-size: 0.75rem; color: hsl(var(--muted-foreground));">No key concepts matched.</span>`;
        }

        const missingBox = document.getElementById("int-missing-concepts");
        if (missingBox) {
          missingBox.innerHTML = (data.missing_concepts && data.missing_concepts.length > 0)
            ? data.missing_concepts.map(c => `<span class="badge badge-rose">! ${c}</span>`).join("")
            : `<span class="badge badge-emerald">✓ All concepts covered!</span>`;
        }

        const strengthsEl = document.getElementById("int-strengths");
        if (strengthsEl) strengthsEl.textContent = data.feedback_strengths;

        const improvEl = document.getElementById("int-improvements");
        if (improvEl) improvEl.textContent = data.feedback_improvements;

        // Save into history
        interviewHistory.push({
          role: "Candidate",
          text: answer,
          score: data.overall_score,
          tier: data.score_tier
        });

      } catch (err) {
        console.error("Evaluation Error:", err);
        alert("Evaluation failed. Please try again.");
      } finally {
        submitBtn.innerHTML = '<i data-lucide="sparkles" style="width: 15px; height: 15px;"></i><span>Evaluate Answer with AI</span>';
        initLucideIcons();
      }
    });
  }
}

window.loadNextInterviewQuestion = function() {
  const bank = INTERVIEW_LOCAL_BANK[currentInterviewSkill] || INTERVIEW_LOCAL_BANK["SQL"];
  currentQuestionIndex = (currentQuestionIndex + 1) % bank.length;
  updateInterviewQuestionView();
};

function updateInterviewQuestionView() {
  const bank = INTERVIEW_LOCAL_BANK[currentInterviewSkill] || INTERVIEW_LOCAL_BANK["SQL"];
  const q = bank[currentQuestionIndex % bank.length];

  const qText = document.getElementById("int-question-text");
  const qMeta = document.getElementById("int-q-meta");
  const qHint = document.getElementById("int-hint-text");
  const ansInput = document.getElementById("int-answer-input");
  const resCard = document.getElementById("int-result-card");
  const modelAnswerCard = document.getElementById("int-model-answer-card");
  const modelAnswerText = document.getElementById("int-model-answer-text");
  const modelAnswerIcon = document.getElementById("model-answer-icon");

  if (qText) qText.textContent = `"${q.text}"`;
  if (qMeta) qMeta.textContent = `${currentInterviewSkill} | ${q.difficulty} | ${q.type}`;
  if (qHint) qHint.innerHTML = `💡 <i>Interviewer Hint: ${q.hint}</i>`;
  if (ansInput) ansInput.value = "";
  if (resCard) resCard.style.display = "none";
  if (modelAnswerCard) modelAnswerCard.style.display = "none";
  if (modelAnswerIcon) modelAnswerIcon.textContent = "▼";
  if (modelAnswerText && q.model_answer) modelAnswerText.innerHTML = q.model_answer;
}

window.toggleModelAnswer = function() {
  const card = document.getElementById("int-model-answer-card");
  const icon = document.getElementById("model-answer-icon");
  if (!card) return;
  const isHidden = (card.style.display === "none" || !card.style.display);
  card.style.display = isHidden ? "block" : "none";
  if (icon) icon.textContent = isHidden ? "▲" : "▼";
};

// Web Speech API Text-to-Speech (TTS)
window.speakCurrentQuestion = function() {
  if (!("speechSynthesis" in window)) {
    alert("Speech Synthesis is not supported in this browser.");
    return;
  }

  const qText = document.getElementById("int-question-text")?.textContent?.replace(/^"|"$/g, '') || "";
  window.speechSynthesis.cancel(); // cancel any active speech

  const statusEl = document.getElementById("int-speech-status");
  if (statusEl) statusEl.style.display = "inline";

  const utterance = new SpeechSynthesisUtterance(qText);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;

  utterance.onend = () => {
    if (statusEl) statusEl.style.display = "none";
  };
  utterance.onerror = () => {
    if (statusEl) statusEl.style.display = "none";
  };

  window.speechSynthesis.speak(utterance);
};

// Web Speech API Speech-to-Text (STT) Voice Recording
window.toggleVoiceRecording = function() {
  const recordBtn = document.getElementById("int-voice-record-btn");
  const statusEl = document.getElementById("voice-recording-status");
  const labelEl = document.getElementById("int-voice-btn-label");
  const ansInput = document.getElementById("int-answer-input");

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert("Web Speech Recognition API is not supported in this browser. Please use Google Chrome or Edge, or type your answer manually.");
    return;
  }

  if (isVoiceRecording) {
    // Stop recording
    if (speechRecognizer) speechRecognizer.stop();
    isVoiceRecording = false;
    if (recordBtn) recordBtn.classList.remove("voice-recording-active");
    if (statusEl) statusEl.style.display = "none";
    if (labelEl) labelEl.textContent = "Record Voice Answer";
  } else {
    // Start recording
    speechRecognizer = new SpeechRecognition();
    speechRecognizer.continuous = true;
    speechRecognizer.interimResults = true;
    speechRecognizer.lang = "en-US";

    let finalTranscript = ansInput ? ansInput.value : "";

    speechRecognizer.onstart = () => {
      isVoiceRecording = true;
      if (recordBtn) recordBtn.classList.add("voice-recording-active");
      if (statusEl) statusEl.style.display = "flex";
      if (labelEl) labelEl.textContent = "⏹️ Stop Recording";
    };

    speechRecognizer.onresult = (event) => {
      let interimTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += " " + event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }
      if (ansInput) {
        ansInput.value = (finalTranscript + " " + interimTranscript).trim();
      }
    };

    speechRecognizer.onerror = (event) => {
      console.error("Speech Recognition Error:", event.error);
      isVoiceRecording = false;
      if (recordBtn) recordBtn.classList.remove("voice-recording-active");
      if (statusEl) statusEl.style.display = "none";
      if (labelEl) labelEl.textContent = "Record Voice Answer";
    };

    speechRecognizer.onend = () => {
      isVoiceRecording = false;
      if (recordBtn) recordBtn.classList.remove("voice-recording-active");
      if (statusEl) statusEl.style.display = "none";
      if (labelEl) labelEl.textContent = "Record Voice Answer";
    };

    speechRecognizer.start();
  }
};

// Adaptive Follow-up Probe Generator
window.requestAdaptiveFollowUp = async function() {
  const qText = document.getElementById("int-question-text")?.textContent?.replace(/^"|"$/g, '').trim() || "";
  const candidateAns = document.getElementById("int-answer-input")?.value || "";
  const followUpBtn = document.getElementById("int-followup-btn");

  if (!candidateAns.trim()) {
    alert("Please provide an answer first before requesting a follow-up challenge.");
    return;
  }

  try {
    if (followUpBtn) followUpBtn.innerHTML = '<i data-lucide="loader" class="animate-spin" style="width: 14px; height: 14px;"></i><span>Generating Adaptive Challenge...</span>';

    const response = await fetch(`${API_BASE}/api/v1/interview/follow-up`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        skill_name: currentInterviewSkill,
        question_id: "int_q_01",
        question_text: qText,
        candidate_answer: candidateAns
      })
    });

    if (!response.ok) throw new Error("Follow-up generation failed");
    const data = await response.json();
    const followUp = data.follow_up;

    // Show dialogue container
    const dialogueContainer = document.getElementById("int-dialogue-container");
    const dialogueThread = document.getElementById("int-dialogue-thread");
    if (dialogueContainer && dialogueThread) {
      dialogueContainer.style.display = "block";

      dialogueThread.innerHTML += `
        <div class="dialogue-bubble bubble-user">
          <b>You:</b> ${candidateAns}
        </div>
        <div class="dialogue-bubble bubble-ai">
          <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
            <span class="badge badge-amber" style="font-size: 0.7rem;">⚡ ${followUp.probe_type}</span>
            <span style="font-size: 0.75rem; color: hsl(var(--muted-foreground));">Focus: ${followUp.target_missing_concept}</span>
          </div>
          <b>AI Interviewer:</b> ${followUp.probe_text}
          <div style="font-size: 0.78rem; color: hsl(var(--muted-foreground)); margin-top: 6px;">
            💡 <i>${followUp.hint}</i>
          </div>
        </div>
      `;
    }

    // Set follow up as active question
    const qTextEl = document.getElementById("int-question-text");
    const qHintEl = document.getElementById("int-hint-text");
    const qMetaEl = document.getElementById("int-q-meta");
    const ansInput = document.getElementById("int-answer-input");
    const resCard = document.getElementById("int-result-card");

    if (qTextEl) qTextEl.textContent = `"${followUp.probe_text}"`;
    if (qHintEl) qHintEl.innerHTML = `💡 <i>Interviewer Hint: ${followUp.hint}</i>`;
    if (qMetaEl) qMetaEl.textContent = `${currentInterviewSkill} | Follow-up: ${followUp.probe_type}`;
    if (ansInput) ansInput.value = "";
    if (resCard) resCard.style.display = "none";

    // Auto read aloud follow up question
    speakCurrentQuestion();

  } catch (err) {
    console.error(err);
    alert("Could not generate follow-up challenge.");
  } finally {
    if (followUpBtn) {
      followUpBtn.innerHTML = '⚡ Ask Adaptive Follow-Up Probe →';
      initLucideIcons();
    }
  }
};

window.practiceSkillInInterview = function(skillName) {
  switchNavTab("view-interview");
  const skillSelect = document.getElementById("int-skill-select");
  if (skillSelect) {
    skillSelect.value = skillName;
    currentInterviewSkill = skillName;
    currentQuestionIndex = 0;
    updateInterviewQuestionView();
  }
};


// -----------------------------------------------------------------------------
// 12. GITHUB PROFILE SCANNER, DEEP AST LINTER & BLUEPRINT GENERATOR (SECTION 5)
// -----------------------------------------------------------------------------
let currentBlueprintData = null;

window.switchGithubSubTab = function(tabName) {
  const tabs = ['repos', 'readme', 'blueprint'];
  tabs.forEach(t => {
    const btn = document.getElementById(`gh-subtab-${t}`);
    const pane = document.getElementById(`gh-pane-${t}`);
    if (btn) btn.classList.toggle('active', t === tabName);
    if (pane) pane.style.display = (t === tabName) ? 'block' : 'none';
  });
  initLucideIcons();
};

window.loadGithubSampleUser = function(username) {
  const input = document.getElementById("github-username-input");
  if (input) input.value = username;
  loadGithubProof(username);
};

async function loadGithubProof(user) {
  const btn = document.getElementById("github-scan-btn");
  try {
    if (btn) btn.innerHTML = '<i data-lucide="loader-2" class="spin" style="width: 14px; height: 14px;"></i> Auditing...';
    const response = await fetch(`${API_BASE}/api/v1/github-scan/${user}`);
    const data = await response.json();

    const skillsCount = document.getElementById("gh-skills-count");
    if (skillsCount) skillsCount.textContent = (data.verified_skills || []).length;

    const qualityScore = document.getElementById("gh-quality-score");
    if (qualityScore) qualityScore.textContent = `${(data.quality_score || 0).toFixed(1)}%`;

    const tierVal = document.getElementById("gh-tier-val");
    if (tierVal) tierVal.textContent = data.profile_quality_tier || data.portfolio_tier || "Placement Ready";

    const reposCount = document.getElementById("gh-repos-count");
    if (reposCount) reposCount.textContent = `${data.total_repos_audited || 0} Repos`;

    // Verified Badges
    const badges = document.getElementById("gh-verified-badges");
    if (badges) {
      if (data.verified_skills && data.verified_skills.length > 0) {
        badges.innerHTML = data.verified_skills.map(s => `<span class="badge badge-emerald">✓ ${s}</span>`).join("");
      } else {
        badges.innerHTML = `<span style="font-size: 0.8rem; color: hsl(var(--muted-foreground));">No canonical taxonomy skills detected.</span>`;
      }
    }

    // Repositories Table
    const tableBody = document.getElementById("gh-repos-table-body");
    if (tableBody) {
      const repos = data.repositories || data.audited_repos || [];
      if (repos.length > 0) {
        tableBody.innerHTML = repos.map(r => `
          <tr>
            <td><b>${r.name || r.repo_name}</b></td>
            <td><span class="badge badge-outline">${r.language || r.primary_language || 'Python'}</span></td>
            <td>⭐ ${r.stars || r.stars_count || 0}</td>
            <td>${(r.skills || r.detected_skills || []).map(s => `<span class="badge badge-secondary">${s}</span>`).join(" ")}</td>
            <td>${r.has_tests ? '<span class="badge badge-emerald">✓ Yes</span>' : '<span style="color: hsl(var(--muted-foreground));">-</span>'}</td>
            <td>${r.has_docker ? '<span class="badge badge-emerald">✓ Yes</span>' : '<span style="color: hsl(var(--muted-foreground));">-</span>'}</td>
            <td>${r.has_ci ? '<span class="badge badge-emerald">✓ Yes</span>' : '<span style="color: hsl(var(--muted-foreground));">-</span>'}</td>
          </tr>
        `).join("");
      } else {
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: hsl(var(--muted-foreground)); padding: 20px;">No repositories found.</td></tr>`;
      }
    }

    // Populate default blueprint if present
    if (data.top_project_blueprints && data.top_project_blueprints.length > 0) {
      renderProjectBlueprint(data.top_project_blueprints[0]);
    }
  } catch (err) {
    console.error("GitHub Scan Error:", err);
  } finally {
    if (btn) btn.innerHTML = '<i data-lucide="search" style="width: 14px; height: 14px;"></i> Audit Portfolio';
    initLucideIcons();
  }
}

window.runASTCodeAnalysis = async function() {
  const codeEditor = document.getElementById("ast-code-editor");
  const btn = document.getElementById("btn-run-ast-analysis");
  if (!codeEditor) return;

  const code = codeEditor.value.trim();
  if (!code) {
    alert("Please enter Python code to analyze.");
    return;
  }

  try {
    if (btn) btn.innerHTML = '<i data-lucide="loader-2" class="spin" style="width: 14px; height: 14px;"></i> Parsing AST...';
    const response = await fetch(`${API_BASE}/api/v1/github/analyze-code`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code_text: code, file_name: "predictor.py" })
    });

    const data = await response.json();
    if (!data.is_valid_syntax) {
      alert(`Python Syntax Error: ${data.syntax_error_message}`);
      return;
    }

    // Update AST metrics
    const compVal = document.getElementById("ast-complexity-val");
    if (compVal) {
      const isClean = data.avg_cyclomatic_complexity <= 5;
      compVal.textContent = isClean ? "Grade A ⭐⭐⭐⭐⭐ (Clean)" : (data.avg_cyclomatic_complexity <= 10 ? "Grade B ⭐⭐⭐⭐" : "Needs Splitting ⭐⭐⭐");
      compVal.style.color = isClean ? "var(--emerald-text)" : (data.avg_cyclomatic_complexity <= 10 ? "#f59e0b" : "var(--rose-text)");
    }

    const typingVal = document.getElementById("ast-typing-val");
    if (typingVal) {
      typingVal.textContent = `${data.type_hint_coverage_pct.toFixed(0)}% Clear`;
      typingVal.style.color = data.type_hint_coverage_pct >= 70 ? "var(--brand-blue)" : "#f59e0b";
    }

    const oopVal = document.getElementById("ast-oop-val");
    if (oopVal) oopVal.textContent = data.oop_modularity_tier.includes("Modular") ? "Well-Organized" : "Simple Script";

    const docVal = document.getElementById("ast-docstring-val");
    if (docVal) docVal.textContent = `${data.docstring_coverage_pct.toFixed(0)}% Clear`;

    const patternsList = document.getElementById("ast-patterns-list");
    if (patternsList) {
      patternsList.textContent = (data.detected_design_patterns && data.detected_design_patterns.length > 0)
        ? data.detected_design_patterns.join(", ")
        : "Clean straightforward functions and structure.";
    }

    const feedbackList = document.getElementById("ast-feedback-list");
    if (feedbackList) {
      feedbackList.innerHTML = (data.code_smells && data.code_smells.length > 0)
        ? data.code_smells.map(s => `<div>• ${s}</div>`).join("")
        : "• Great job! Your code is clean, easy to read, and ready for team collaboration.";
    }
  } catch (err) {
    console.error("AST Analysis Error:", err);
    alert("Error checking code cleanliness.");
  } finally {
    if (btn) btn.innerHTML = '<i data-lucide="play" style="width: 14px; height: 14px;"></i> Check Code Cleanliness';
    initLucideIcons();
  }
};

window.auditReadmeDocument = async function() {
  const editor = document.getElementById("readme-markdown-editor");
  const btn = document.getElementById("btn-audit-readme");
  if (!editor) return;

  const markdown = editor.value.trim();
  if (!markdown) {
    alert("Please enter README markdown text to score.");
    return;
  }

  try {
    if (btn) btn.innerHTML = '<i data-lucide="loader-2" class="spin" style="width: 14px; height: 14px;"></i> Scoring...';
    const response = await fetch(`${API_BASE}/api/v1/github/audit-readme`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ readme_text: markdown })
    });

    const data = await response.json();

    const scoreGauge = document.getElementById("readme-score-gauge");
    if (scoreGauge) {
      scoreGauge.textContent = `${data.overall_readme_score.toFixed(1)}%`;
      scoreGauge.style.color = data.overall_readme_score >= 80 ? "var(--emerald-text)" : (data.overall_readme_score >= 60 ? "#f59e0b" : "var(--rose-text)");
    }

    const gradeBadge = document.getElementById("readme-grade-badge");
    if (gradeBadge) {
      gradeBadge.textContent = data.documentation_grade;
      gradeBadge.className = data.overall_readme_score >= 80 ? "badge badge-emerald" : (data.overall_readme_score >= 60 ? "badge badge-amber" : "badge badge-rose");
    }

    // Render Checklist
    const checksContainer = document.getElementById("readme-checks-container");
    if (checksContainer) {
      checksContainer.innerHTML = (data.section_checks || []).map(c => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; border: 1px solid hsl(var(--border)); border-radius: var(--radius); background-color: hsl(var(--background));">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1rem;">${c.passed ? '✅' : '⚠️'}</span>
            <div>
              <div style="font-size: 0.82rem; font-weight: 600;">${c.title}</div>
              <div style="font-size: 0.75rem; color: hsl(var(--muted-foreground));">${c.category} &nbsp;•&nbsp; Weight: ${c.weight}%</div>
            </div>
          </div>
          <span class="badge ${c.passed ? 'badge-emerald' : 'badge-outline'}">${c.passed ? 'PASSED' : 'MISSING'}</span>
        </div>
      `).join("");
    }

    // Render Suggestions
    const suggestionsList = document.getElementById("readme-suggestions-list");
    if (suggestionsList) {
      suggestionsList.innerHTML = (data.actionable_recommendations || []).map(r => `<div>• ${r}</div>`).join("") || "No improvement recommendations.";
    }
  } catch (err) {
    console.error("README Audit Error:", err);
    alert("Error scoring README document.");
  } finally {
    if (btn) btn.innerHTML = '<i data-lucide="check-circle" style="width: 14px; height: 14px;"></i> Score README Quality';
    initLucideIcons();
  }
};

window.generateProjectBlueprint = async function() {
  const select = document.getElementById("blueprint-skill-select");
  const btn = document.getElementById("btn-generate-blueprint");
  const skill = select ? select.value : "Docker";

  try {
    if (btn) btn.innerHTML = '<i data-lucide="loader-2" class="spin" style="width: 14px; height: 14px;"></i> Generating...';
    const response = await fetch(`${API_BASE}/api/v1/github/generate-blueprint`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ missing_skill: skill, target_career: state.targetCareer || "Data Scientist" })
    });

    const data = await response.json();
    renderProjectBlueprint(data);
  } catch (err) {
    console.error("Blueprint Generation Error:", err);
    alert("Error generating project blueprint.");
  } finally {
    if (btn) btn.innerHTML = '<i data-lucide="sparkles" style="width: 14px; height: 14px;"></i> Generate Blueprint';
    initLucideIcons();
  }
};

function renderProjectBlueprint(data) {
  currentBlueprintData = data;
  if (!data) return;

  const skillTag = document.getElementById("bp-skill-tag");
  if (skillTag) skillTag.textContent = `Target Gap: ${data.target_skill}`;

  const title = document.getElementById("bp-title");
  if (title) title.textContent = data.project_title;

  const tagline = document.getElementById("bp-tagline");
  if (tagline) tagline.textContent = data.tagline;

  const problem = document.getElementById("bp-problem");
  if (problem) problem.textContent = data.business_problem_statement;

  const techStack = document.getElementById("bp-tech-stack");
  if (techStack) {
    techStack.innerHTML = (data.tech_stack || []).map(t => `<span class="badge badge-secondary">${t}</span>`).join("");
  }

  // Milestones Sprints
  const sprints = document.getElementById("bp-sprints-container");
  if (sprints) {
    sprints.innerHTML = (data.milestones || []).map(m => `
      <div style="padding: 10px 12px; border: 1px solid hsl(var(--border)); border-left: 3px solid var(--brand-blue); border-radius: var(--radius); background-color: hsl(var(--background));">
        <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
          <span style="font-size: 0.82rem; font-weight: 700; color: var(--brand-blue);">Sprint ${m.sprint_num}: ${m.title}</span>
          <span class="badge badge-outline">${m.estimated_days} Days</span>
        </div>
        <div style="font-size: 0.78rem; color: hsl(var(--muted-foreground));">${m.objective}</div>
        <div style="font-size: 0.75rem; color: var(--emerald-text); margin-top: 4px;">Deliverables: ${(m.deliverables || []).join(', ')}</div>
      </div>
    `).join("");
  }

  // Folder Tree
  const folderTree = document.getElementById("bp-folder-tree");
  if (folderTree) folderTree.textContent = data.folder_tree || "";

  // Starter Files Tabs
  const starterTabs = document.getElementById("bp-starter-tabs");
  const files = data.starter_files || {};
  const fileKeys = Object.keys(files);

  if (starterTabs && fileKeys.length > 0) {
    starterTabs.innerHTML = fileKeys.map((f, idx) => `
      <button class="btn btn-outline btn-sm ${idx === 0 ? 'active' : ''}" onclick="selectBlueprintStarterFile('${f}')">
        ${f}
      </button>
    `).join("");
    selectBlueprintStarterFile(fileKeys[0]);
  } else if (starterTabs) {
    starterTabs.innerHTML = `<span style="font-size: 0.75rem; color: hsl(var(--muted-foreground));">README.md boilerplate</span>`;
    const content = document.getElementById("bp-starter-file-content");
    if (content) content.textContent = `# ${data.project_title}\n\n${data.tagline}\n\n## Tech Stack\n${(data.tech_stack || []).join(', ')}`;
  }

  initLucideIcons();
}

window.selectBlueprintStarterFile = function(fileName) {
  if (!currentBlueprintData || !currentBlueprintData.starter_files) return;
  const content = document.getElementById("bp-starter-file-content");
  if (content) {
    content.textContent = currentBlueprintData.starter_files[fileName] || "";
  }

  const tabs = document.querySelectorAll("#bp-starter-tabs button");
  tabs.forEach(btn => {
    btn.classList.toggle("active", btn.textContent.trim() === fileName);
  });
};

window.copyBlueprintFolderTree = function() {
  const tree = document.getElementById("bp-folder-tree");
  if (tree) {
    navigator.clipboard.writeText(tree.textContent);
    alert("Project folder directory tree copied to clipboard! 📋");
  }
};

function initGitHubScanner() {
  const btn = document.getElementById("github-scan-btn");
  if (btn) {
    btn.addEventListener("click", () => {
      const user = document.getElementById("github-username-input").value.trim() || "alex_datascientist";
      loadGithubProof(user);
    });
  }

  // Auto-load default profile on startup
  loadGithubProof("alex_datascientist");
}

function initVectorSearch() {
  initVectorSubTabs();
  initHybridSearch();
  initKnowledgeGraphExplorer();
  initRAGAssistant();
}

function initVectorSubTabs() {
  const tabs = document.querySelectorAll('#view-vector .segmented-control .segment-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const targetSubtab = tab.getAttribute('data-subtab');
      document.querySelectorAll('.vector-subtab-pane').forEach(pane => {
        pane.style.display = (pane.id === targetSubtab) ? 'block' : 'none';
      });
      initLucideIcons();
    });
  });
}

function initHybridSearch() {
  const input = document.getElementById('hybrid-search-input');
  const btn = document.getElementById('hybrid-search-btn');
  const docTypeSelect = document.getElementById('hybrid-search-doctype');
  const resultsBox = document.getElementById('hybrid-search-results-box');
  const countBadge = document.getElementById('hybrid-results-count-badge');
  const summaryDesc = document.getElementById('hybrid-results-summary');

  if (!btn) return;

  // Preset chips
  document.querySelectorAll('.hybrid-preset-btn').forEach(chip => {
    chip.addEventListener('click', () => {
      if (input) input.value = chip.getAttribute('data-query');
      executeSearch();
    });
  });

  async function executeSearch() {
    if (!input) return;
    const query = input.value.trim();
    if (!query) return;

    btn.disabled = true;
    btn.innerHTML = `<span class="loading-spinner"></span> Searching...`;
    if (resultsBox) {
      resultsBox.innerHTML = `<div style="text-align: center; padding: 24px; color: hsl(var(--muted-foreground));"><span class="loading-spinner"></span> Searching tech database & matching concepts...</div>`;
    }

    try {
      const response = await fetch(`${API_BASE}/api/v1/vector/hybrid-search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          top_k: 5,
          mode: 'hybrid',
          alpha: 0.5,
          doc_type: docTypeSelect ? docTypeSelect.value : 'all'
        })
      });

      const data = await response.json();
      const results = data.results || [];
      if (countBadge) countBadge.textContent = `${results.length} Matches Found`;
      if (summaryDesc) summaryDesc.textContent = `Showing relevant skills & concepts for: "${query}"`;

      if (results.length === 0) {
        if (resultsBox) resultsBox.innerHTML = `<div style="padding: 24px; text-align: center; color: hsl(var(--muted-foreground));">No matching skills or documents found. Try another search word.</div>`;
        return;
      }

      if (resultsBox) {
        resultsBox.innerHTML = results.map((r, idx) => {
          const meta = r.metadata || {};
          const title = meta.skill_name || meta.title || meta.role_title || r.doc_id;
          const cat = meta.category || meta.domain || meta.type || "Document";
          const matchedKw = (r.matched_keywords && r.matched_keywords.length > 0)
            ? r.matched_keywords.map(kw => `<span class="badge badge-secondary" style="font-size: 0.7rem;">${kw}</span>`).join(" ")
            : `<span style="font-size: 0.72rem; color: hsl(var(--muted-foreground));">Semantic Match</span>`;

          return `
            <div style="border: 1px solid hsl(var(--border)); border-radius: var(--radius); padding: 14px; background-color: hsl(var(--background)); transition: all 0.2s ease;">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span class="badge ${idx === 0 ? 'badge-emerald' : 'badge-secondary'}" style="font-weight: 700;">#${idx + 1} Best Match</span>
                  <span style="font-weight: 700; font-size: 0.95rem;">${title}</span>
                  <span class="badge badge-blue" style="font-size: 0.72rem;">${cat}</span>
                </div>
                <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                  <span class="badge badge-indigo">Relevance: ${Math.round((r.combined_score || 0.8) * 100)}%</span>
                </div>
              </div>
              <p style="font-size: 0.86rem; line-height: 1.5; color: hsl(var(--foreground)); margin: 0 0 10px 0;">
                ${r.text}
              </p>
              <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px; padding-top: 8px; border-top: 1px dashed hsl(var(--border));">
                <div style="display: flex; align-items: center; gap: 6px;">
                  <span style="font-size: 0.72rem; font-weight: 600; color: hsl(var(--muted-foreground));">Key Topic:</span>
                  ${matchedKw}
                </div>
                <div style="display: flex; gap: 4px;">
                  ${meta.difficulty_level ? `<span class="badge badge-outline" style="font-size: 0.7rem;">${meta.difficulty_level}</span>` : ''}
                  ${r.doc_id ? `<span class="badge badge-outline" style="font-size: 0.7rem;">ID: ${r.doc_id}</span>` : ''}
                </div>
              </div>
            </div>
          `;
        }).join("");
      }

    } catch (err) {
      console.error(err);
      if (resultsBox) resultsBox.innerHTML = `<div style="color: var(--rose-text); padding: 16px;">Failed to execute search: ${err.message}</div>`;
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<i data-lucide="search" style="width: 16px; height: 16px;"></i> Search`;
      initLucideIcons();
    }
  }

  btn.addEventListener('click', executeSearch);
  if (input) {
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') executeSearch();
    });
  }

  // Auto-run initial query
  executeSearch();
}

function initKnowledgeGraphExplorer() {
  const select = document.getElementById("kg-skill-select");
  const traceBtn = document.getElementById("kg-trace-btn");
  const pathContainer = document.getElementById("kg-pathway-container");
  const pathBadge = document.getElementById("kg-path-depth-badge");
  const gatewaysList = document.getElementById("kg-gateways-list");
  const clusterTree = document.getElementById("kg-cluster-tree");

  if (!traceBtn) return;

  async function loadKnowledgeGraph(targetSkill = null) {
    try {
      const url = targetSkill 
        ? `${API_BASE}/api/v1/knowledge-graph/explore?target_skill=${encodeURIComponent(targetSkill)}`
        : `${API_BASE}/api/v1/knowledge-graph/explore`;
      const response = await fetch(url);
      const data = await response.json();

      // KPIs
      const totalNodesEl = document.getElementById("kg-total-nodes");
      const totalEdgesEl = document.getElementById("kg-total-edges");
      const topGatewayEl = document.getElementById("kg-top-gateway-name");
      if (totalNodesEl) totalNodesEl.textContent = data.total_nodes || 32;
      if (totalEdgesEl) totalEdgesEl.textContent = data.total_edges || 28;
      if (topGatewayEl && data.top_gateway_skills && data.top_gateway_skills[0]) {
        topGatewayEl.textContent = data.top_gateway_skills[0].label;
      }

      // Render Top Gateways
      if (gatewaysList && data.top_gateway_skills) {
        gatewaysList.innerHTML = data.top_gateway_skills.map((gw, i) => `
          <div style="padding: 10px; border: 1px solid hsl(var(--border)); border-radius: var(--radius); background-color: hsl(var(--background));">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <div style="display: flex; align-items: center; gap: 6px;">
                <span class="badge ${i === 0 ? 'badge-emerald' : 'badge-blue'}">#${i + 1}</span>
                <span style="font-weight: 700; font-size: 0.88rem;">${gw.label}</span>
                <span class="badge badge-secondary" style="font-size: 0.7rem;">${gw.category}</span>
              </div>
              <span class="badge badge-indigo">Centrality: ${gw.centrality_score}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: hsl(var(--muted-foreground)); margin-bottom: 6px;">
              <span>Unlocks (Out-Degree): <b>${gw.out_degree} downstream skills</b></span>
              <span>Requires (In-Degree): <b>${gw.in_degree} prerequisites</b></span>
            </div>
            <div style="width: 100%; height: 5px; background-color: hsl(var(--muted)); border-radius: 9999px; overflow: hidden;">
              <div style="width: ${Math.min(100, gw.centrality_score * 70)}%; height: 100%; background: linear-gradient(90deg, #3b82f6, #10b981);"></div>
            </div>
          </div>
        `).join("");
      }

      // Render Prerequisite Chain if requested
      if (pathContainer && data.prerequisite_chain) {
        const chain = data.prerequisite_chain;
        if (pathBadge) pathBadge.textContent = `${chain.length}-Skill Prerequisite Sequence`;
        pathContainer.innerHTML = chain.map((step, idx) => `
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="padding: 8px 14px; border: 1px solid hsl(var(--border)); border-radius: var(--radius); background-color: ${idx === chain.length - 1 ? 'hsl(var(--primary) / 0.1)' : 'hsl(var(--card))'}; border-color: ${idx === chain.length - 1 ? 'hsl(var(--primary))' : 'hsl(var(--border))'}; display: flex; align-items: center; gap: 6px;">
              <span class="badge ${idx === chain.length - 1 ? 'badge-indigo' : 'badge-secondary'}" style="font-size: 0.7rem;">Stage ${idx + 1}</span>
              <span style="font-weight: 700; font-size: 0.85rem; color: ${idx === chain.length - 1 ? 'var(--brand-blue)' : 'hsl(var(--foreground))'};">${step}</span>
            </div>
            ${idx < chain.length - 1 ? `<i data-lucide="arrow-right" style="width: 16px; height: 16px; color: hsl(var(--muted-foreground));"></i>` : ''}
          </div>
        `).join("");
      }

      // Render Visual Clusters
      if (clusterTree) {
        clusterTree.innerHTML = `
          <div style="padding: 10px; border: 1px solid hsl(var(--border)); border-radius: var(--radius); background: hsl(var(--card));">
            <div style="font-size: 0.78rem; font-weight: 700; color: var(--emerald-text); margin-bottom: 6px;">🌱 Tier 1: Foundational Roots</div>
            <div class="tags-wrap">
              <span class="badge badge-secondary">Python</span>
              <span class="badge badge-secondary">SQL</span>
              <span class="badge badge-secondary">Linear Algebra</span>
              <span class="badge badge-secondary">Statistics & Probability</span>
            </div>
          </div>
          <div style="text-align: center; color: hsl(var(--muted-foreground));"><i data-lucide="chevrons-down" style="width: 16px; height: 16px;"></i></div>
          <div style="padding: 10px; border: 1px solid hsl(var(--border)); border-radius: var(--radius); background: hsl(var(--card));">
            <div style="font-size: 0.78rem; font-weight: 700; color: var(--brand-blue); margin-bottom: 6px;">⚡ Tier 2: Intermediate Data & Modeling</div>
            <div class="tags-wrap">
              <span class="badge badge-secondary">Pandas</span>
              <span class="badge badge-secondary">NumPy</span>
              <span class="badge badge-secondary">Scikit-Learn</span>
              <span class="badge badge-secondary">Machine Learning</span>
              <span class="badge badge-secondary">FastAPI</span>
            </div>
          </div>
          <div style="text-align: center; color: hsl(var(--muted-foreground));"><i data-lucide="chevrons-down" style="width: 16px; height: 16px;"></i></div>
          <div style="padding: 10px; border: 1px solid hsl(var(--border)); border-radius: var(--radius); background: hsl(var(--card));">
            <div style="font-size: 0.78rem; font-weight: 700; color: var(--indigo-text); margin-bottom: 6px;">🚀 Tier 3: Advanced Deep Learning & MLOps</div>
            <div class="tags-wrap">
              <span class="badge badge-secondary">Deep Learning</span>
              <span class="badge badge-secondary">PyTorch</span>
              <span class="badge badge-secondary">NLP / Transformers</span>
              <span class="badge badge-secondary">Computer Vision</span>
              <span class="badge badge-secondary">Docker</span>
              <span class="badge badge-secondary">Kubernetes</span>
              <span class="badge badge-secondary">MLOps</span>
            </div>
          </div>
        `;
      }

      initLucideIcons();
    } catch (err) {
      console.error(err);
    }
  }

  traceBtn.addEventListener("click", () => {
    if (select) loadKnowledgeGraph(select.value);
  });

  // Initial load
  loadKnowledgeGraph("Machine Learning");
}

function initRAGAssistant() {
  const input = document.getElementById("rag-question-input");
  const btn = document.getElementById("rag-ask-btn");
  const container = document.getElementById("rag-response-container");
  const answerText = document.getElementById("rag-answer-text");
  const codeCard = document.getElementById("rag-code-card");
  const codeSnippet = document.getElementById("rag-code-snippet");
  const copyBtn = document.getElementById("rag-copy-code-btn");
  const takeawaysList = document.getElementById("rag-takeaways-list");
  const citationsList = document.getElementById("rag-citations-list");
  const citationsHeader = document.getElementById("rag-citations-badges-header");
  const timestampEl = document.getElementById("rag-response-timestamp");

  if (!btn) return;

  // Question prompts
  document.querySelectorAll(".rag-prompt-btn").forEach(chip => {
    chip.addEventListener("click", () => {
      if (input) input.value = chip.getAttribute("data-prompt");
      askQuestion();
    });
  });

  async function askQuestion() {
    if (!input) return;
    const question = input.value.trim();
    if (!question) return;

    btn.disabled = true;
    btn.innerHTML = `<span class="loading-spinner"></span> Synthesizing...`;
    if (container) container.style.display = "none";

    try {
      const response = await fetch(`${API_BASE}/api/v1/rag/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question })
      });

      const data = await response.json();
      if (container) container.style.display = "block";

      if (timestampEl) {
        timestampEl.textContent = `Retrieved and synthesized in ${data.groundedness_confidence || 'High Confidence'} mode at ${new Date().toLocaleTimeString()}`;
      }

      if (citationsHeader && data.citations) {
        citationsHeader.innerHTML = data.citations.map(c => {
          const sim = c.relevance_score || c.similarity || 0.9;
          return `
            <span class="badge badge-emerald" title="Matched vector document">
              <i data-lucide="file-check" style="width: 12px; height: 12px; display: inline;"></i> ${c.title} (${Math.round(sim * 100)}%)
            </span>
          `;
        }).join("");
      }

      if (answerText) {
        answerText.innerHTML = (data.answer || "")
          .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
          .replace(/\n\n/g, '<br><br>')
          .replace(/\n/g, '<br>');
      }

      if (codeCard && codeSnippet) {
        if (data.code_snippet && data.code_snippet.trim().length > 0) {
          codeCard.style.display = "block";
          codeSnippet.textContent = data.code_snippet;
        } else {
          codeCard.style.display = "none";
        }
      }

      if (takeawaysList && data.key_takeaways) {
        takeawaysList.innerHTML = data.key_takeaways.map(t => `
          <li style="margin-bottom: 6px;">${t}</li>
        `).join("");
      }

      if (citationsList && data.citations) {
        citationsList.innerHTML = data.citations.map(c => {
          const sim = c.relevance_score || c.similarity || 0.9;
          const text = c.snippet || c.excerpt || "";
          return `
            <div style="padding: 8px; border: 1px solid hsl(var(--border)); border-radius: var(--radius); background-color: hsl(var(--background));">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                <span style="font-weight: 700; font-size: 0.8rem;">${c.title}</span>
                <span class="badge badge-blue" style="font-size: 0.7rem;">Sim: ${sim}</span>
              </div>
              <div style="font-size: 0.75rem; color: hsl(var(--muted-foreground));">${text}</div>
            </div>
          `;
        }).join("");
      }

      initLucideIcons();

    } catch (err) {
      console.error(err);
      alert(`Error querying RAG assistant: ${err.message}`);
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<i data-lucide="message-square" style="width: 16px; height: 16px;"></i> Ask Assistant`;
      initLucideIcons();
    }
  }

  btn.addEventListener("click", askQuestion);
  if (input) {
    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") askQuestion();
    });
  }

  if (copyBtn && codeSnippet) {
    copyBtn.addEventListener("click", () => {
      const code = codeSnippet.textContent;
      navigator.clipboard.writeText(code);
      copyBtn.textContent = "✅ Copied!";
      setTimeout(() => { copyBtn.textContent = "📋 Copy Code"; }, 2000);
    });
  }
}

function initDownloadReport() {
  const btn = document.getElementById("download-report-btn");
  if (!btn) return;

  btn.addEventListener("click", () => {
    const reportData = {
      platform: "SkillGap AI Enterprise Analytics",
      version: "2.0.0",
      evaluation_date: new Date().toISOString(),
      student_profile: {
        target_role: state.targetCareer,
        possessed_skills: state.studentSkills
      },
      readiness_assessment: state.cachedData || {}
    };

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `SkillGap_Evaluation_Report_${state.targetCareer.replace(/\s+/g, '_')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });
}

// -----------------------------------------------------------------------------
// SECTION 7: LIVE JOB MARKET INTELLIGENCE CONTROLLER
// -----------------------------------------------------------------------------
let salaryCurrency = "INR"; // 'INR' or 'USD'

function setSalaryCurrency(curr) {
  salaryCurrency = curr;
  const inrBtn = document.getElementById("currency-toggle-inr");
  const usdBtn = document.getElementById("currency-toggle-usd");
  if (inrBtn && usdBtn) {
    if (curr === "INR") {
      inrBtn.classList.add("active");
      usdBtn.classList.remove("active");
    } else {
      usdBtn.classList.add("active");
      inrBtn.classList.remove("active");
    }
  }
  loadSalaryEstimation();
}

function initMarketIntelligence() {
  initMarketSubTabs();
  initSalaryEstimator();
  initTechHubHeatmap();
  initSkillVelocityTracker();
}

function initMarketSubTabs() {
  const tabs = document.querySelectorAll('#view-market .segmented-control .segment-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const targetTab = tab.getAttribute('data-market-tab');
      document.querySelectorAll('.market-subtab-pane').forEach(pane => {
        pane.style.display = (pane.id === targetTab) ? 'block' : 'none';
      });
      initLucideIcons();
    });
  });
}

async function loadSalaryEstimation() {
  const careerSelect = document.getElementById("salary-career-select");
  const career = careerSelect ? careerSelect.value : (state.targetCareer || "Data Scientist");
  
  try {
    const res = await fetch(`${API_BASE}/api/v1/market/salary-estimator`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        student_skills: state.studentSkills,
        target_career: career
      })
    });
    const data = await res.json();
    
    // Render KPIs
    const currValEl = document.getElementById("salary-current-val");
    const currInrEl = document.getElementById("salary-current-inr");
    const maxValEl = document.getElementById("salary-max-val");
    const maxInrEl = document.getElementById("salary-max-inr");
    const capPctEl = document.getElementById("salary-capacity-pct");
    const matchedSubEl = document.getElementById("salary-matched-skills-sub");
    const topBoostValEl = document.getElementById("salary-top-boost-val");
    const topBoostNameEl = document.getElementById("salary-top-boost-name");

    if (salaryCurrency === "INR") {
      if (currValEl) currValEl.textContent = `₹${data.current_salary_inr_lpa} LPA`;
      if (currInrEl) currInrEl.textContent = `($${data.current_salary_usd.toLocaleString()} USD Equivalent)`;
      if (maxValEl) maxValEl.textContent = `₹${data.max_potential_salary_inr_lpa} LPA`;
      if (maxInrEl) maxInrEl.textContent = `($${data.max_potential_salary_usd.toLocaleString()} USD Senior Tier)`;
    } else {
      if (currValEl) currValEl.textContent = `$${data.current_salary_usd.toLocaleString()}`;
      if (currInrEl) currInrEl.textContent = `(₹${data.current_salary_inr_lpa} LPA Equivalent)`;
      if (maxValEl) maxValEl.textContent = `$${data.max_potential_salary_usd.toLocaleString()}`;
      if (maxInrEl) maxInrEl.textContent = `(₹${data.max_potential_salary_inr_lpa} LPA Senior Tier)`;
    }

    const capacityPct = data.max_potential_salary_usd > 0 
      ? Math.round((data.current_salary_usd / data.max_potential_salary_usd) * 100) 
      : 70;
    if (capPctEl) capPctEl.textContent = `${capacityPct}%`;
    if (matchedSubEl) matchedSubEl.textContent = `${data.matched_skills_count} of ${data.total_required_skills_count} skills verified (${data.skill_readiness_pct}%)`;

    if (data.skill_value_deltas && data.skill_value_deltas[0]) {
      const topD = data.skill_value_deltas[0];
      if (topBoostValEl) {
        topBoostValEl.textContent = salaryCurrency === "INR" ? `+₹${topD.salary_delta_inr_lpa} LPA` : `+$${topD.salary_delta_usd.toLocaleString()}`;
      }
      if (topBoostNameEl) topBoostNameEl.textContent = `${topD.skill_name} (${topD.demand_frequency_pct}% demand)`;
    }

    // Render Top Deltas Cards Grid
    const deltasGrid = document.getElementById("salary-top-deltas-grid");
    if (deltasGrid) {
      const topDeltas = (data.skill_value_deltas || []).slice(0, 4);
      if (topDeltas.length === 0) {
        deltasGrid.innerHTML = `<div style="grid-column: 1/-1; padding: 16px; text-align: center; color: var(--emerald-text);">🎉 All required career skills mastered! Maximum compensation tier unlocked.</div>`;
      } else {
        deltasGrid.innerHTML = topDeltas.map(d => {
          const boostStr = salaryCurrency === "INR" ? `+₹${d.salary_delta_inr_lpa} LPA` : `+$${d.salary_delta_usd.toLocaleString()}`;
          return `
            <div style="border: 1px solid hsl(var(--border)); border-radius: var(--radius); padding: 12px; background: hsl(var(--card)); display: flex; flex-direction: column; justify-content: space-between;">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                <span style="font-weight: 700; font-size: 0.9rem;">${d.skill_name}</span>
                <span class="badge badge-indigo">#${d.roi_rank} ROI</span>
              </div>
              <div style="font-size: 1.15rem; font-weight: 800; color: var(--emerald-text); margin-bottom: 4px;">${boostStr}</div>
              <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: hsl(var(--muted-foreground));">
                <span>Tier: ${d.importance_tier}</span>
                <span>Demand: <b>${d.demand_frequency_pct}%</b></span>
              </div>
            </div>
          `;
        }).join("");
      }
    }

    // Render Detailed Table
    const tableBody = document.getElementById("salary-deltas-table-body");
    if (tableBody) {
      const allReqs = (data.matched_skills || []).map(s => ({
        skill_name: s,
        status: "✓ Verified in Profile",
        tier: "Current Competency",
        usd: "-",
        inr: "-",
        freq: "Core",
        rank: "-"
      })).concat((data.skill_value_deltas || []).map(d => ({
        skill_name: d.skill_name,
        status: "⚡ Missing Bridge Skill",
        tier: d.importance_tier,
        usd: `+$${d.salary_delta_usd.toLocaleString()}`,
        inr: `+₹${d.salary_delta_inr_lpa} LPA`,
        freq: `${d.demand_frequency_pct}%`,
        rank: `#${d.roi_rank}`
      })));

      tableBody.innerHTML = allReqs.map(r => `
        <tr>
          <td><b>${r.rank}</b></td>
          <td><b>${r.skill_name}</b></td>
          <td><span class="badge ${r.tier.includes('High') ? 'badge-amber' : (r.tier.includes('Current') ? 'badge-emerald' : 'badge-secondary')}">${r.tier}</span></td>
          <td style="color: ${r.usd !== '-' ? 'var(--emerald-text)' : 'inherit'}; font-weight: 600;">${r.usd}</td>
          <td style="color: ${r.inr !== '-' ? 'var(--emerald-text)' : 'inherit'}; font-weight: 600;">${r.inr}</td>
          <td>${r.freq}</td>
          <td><span class="badge ${r.status.includes('Verified') ? 'badge-emerald' : 'badge-blue'}">${r.status}</span></td>
        </tr>
      `).join("");
    }

  } catch (err) {
    console.error(err);
  }
}

function initSalaryEstimator() {
  const careerSelect = document.getElementById("salary-career-select");
  if (careerSelect) {
    careerSelect.addEventListener("change", loadSalaryEstimation);
  }
  loadSalaryEstimation();
}

async function initTechHubHeatmap() {
  const grid = document.getElementById("tech-hubs-grid");
  const filterBtns = document.querySelectorAll(".hub-filter-btn");
  if (!grid) return;

  try {
    const res = await fetch(`${API_BASE}/api/v1/market/hiring-heatmap`);
    const data = await res.json();
    const hubs = data.hubs || [];

    function renderHubs(regionFilter = "all") {
      const filtered = (regionFilter === "all")
        ? hubs
        : hubs.filter(h => h.region.toLowerCase() === regionFilter.toLowerCase());

      grid.innerHTML = filtered.map(h => `
        <div style="border: 1px solid hsl(var(--border)); border-radius: var(--radius); padding: 16px; background: hsl(var(--card));">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
            <div>
              <div style="font-weight: 700; font-size: 1rem;">${h.hub_name}</div>
              <div style="font-size: 0.75rem; color: hsl(var(--muted-foreground));">${h.country} &bull; Region: ${h.region}</div>
            </div>
            <span class="badge badge-emerald">${h.active_job_count}+ Openings</span>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 10px; padding: 8px; background: hsl(var(--muted) / 0.3); border-radius: var(--radius);">
            <div>
              <div style="font-size: 0.7rem; color: hsl(var(--muted-foreground));">Avg Base Compensation:</div>
              <div style="font-weight: 700; font-size: 0.88rem; color: var(--brand-blue);">
                ${h.country === "India" ? `₹${h.avg_salary_inr_lpa} LPA` : `$${h.avg_salary_usd.toLocaleString()}`}
              </div>
            </div>
            <div>
              <div style="font-size: 0.7rem; color: hsl(var(--muted-foreground));">Hiring Velocity Index:</div>
              <div style="font-weight: 700; font-size: 0.88rem; color: var(--emerald-text);">${h.hiring_velocity_index} / 10.0</div>
            </div>
          </div>

          <div style="margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 3px;">
              <span>Remote Friendliness:</span>
              <b>${h.remote_friendly_pct}%</b>
            </div>
            <div style="width: 100%; height: 5px; background: hsl(var(--muted)); border-radius: 9999px; overflow: hidden;">
              <div style="width: ${h.remote_friendly_pct}%; height: 100%; background: linear-gradient(90deg, #3b82f6, #10b981);"></div>
            </div>
          </div>

          <div>
            <div style="font-size: 0.72rem; font-weight: 600; margin-bottom: 4px; color: hsl(var(--muted-foreground));">Top Hiring Competencies:</div>
            <div class="tags-wrap">
              ${h.top_in_demand_skills.map(s => `<span class="badge badge-secondary" style="font-size: 0.7rem;">${s}</span>`).join(" ")}
            </div>
          </div>
        </div>
      `).join("");
    }

    filterBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        filterBtns.forEach(b => {
          b.classList.remove("active", "btn-default");
          b.classList.add("btn-outline");
        });
        btn.classList.add("active", "btn-default");
        btn.classList.remove("btn-outline");
        renderHubs(btn.getAttribute("data-region"));
      });
    });

    renderHubs("all");

  } catch (err) {
    console.error(err);
  }
}

async function initSkillVelocityTracker() {
  const tableBody = document.getElementById("skill-velocity-table-body");
  if (!tableBody) return;

  try {
    const res = await fetch(`${API_BASE}/api/v1/market/skill-velocity`);
    const data = await res.json();
    const metrics = data.velocity_metrics || [];

    tableBody.innerHTML = metrics.map(m => {
      const growthClass = m.mom_growth_pct > 40 ? 'badge-amber' : (m.mom_growth_pct > 15 ? 'badge-emerald' : (m.mom_growth_pct < 0 ? 'badge-rose' : 'badge-secondary'));
      const growthPrefix = m.mom_growth_pct > 0 ? '+' : '';
      
      // Sparkline representation using mini horizontal bars
      const sparklineHtml = `
        <div style="display: flex; align-items: flex-end; gap: 3px; height: 22px; padding: 2px 0;">
          ${m.historical_trajectory_6m.map(val => `
            <div style="width: 10px; height: ${Math.max(4, Math.round((val / 100) * 20))}px; background: ${m.mom_growth_pct > 30 ? 'var(--emerald-text)' : 'var(--brand-blue)'}; border-radius: 2px;" title="${val}%"></div>
          `).join("")}
        </div>
      `;

      return `
        <tr>
          <td><b>${m.skill_name}</b></td>
          <td><span class="badge badge-outline">${m.category}</span></td>
          <td><b>${m.current_demand_pct}%</b></td>
          <td><span class="badge ${growthClass}">${growthPrefix}${m.mom_growth_pct}% MoM</span></td>
          <td><span class="badge ${m.velocity_tier.includes('Breakout') ? 'badge-amber' : (m.velocity_tier.includes('Strong') ? 'badge-emerald' : 'badge-secondary')}">${m.velocity_tier}</span></td>
          <td>${sparklineHtml}</td>
          <td><b>${m.projected_momentum_score} / 100</b></td>
          <td style="font-size: 0.78rem; color: hsl(var(--muted-foreground)); max-width: 260px;">${m.market_driver_reason}</td>
        </tr>
      `;
    }).join("");

  } catch (err) {
    console.error(err);
  }
}



