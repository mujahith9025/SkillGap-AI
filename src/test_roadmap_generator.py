"""
Unit Tests for Personalized Learning Roadmap Generator Module
Phase 9 & Section 2 Upgrades: Visual Roadmap, DAG Graph, and Calendar Sprints
"""

import sys
from pathlib import Path
import pytest

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from roadmap_generator import RoadmapGenerator, VisualRoadmap


class TestRoadmapGenerator:
    @classmethod
    def setup_class(cls):
        cls.generator = RoadmapGenerator()

    def test_01_generate_visual_roadmap_data_scientist(self):
        profile = ["Python", "SQL", "Excel"]
        career = "Data Scientist"
        roadmap = self.generator.generate_roadmap(profile, career)
        
        assert isinstance(roadmap, VisualRoadmap)
        assert roadmap.career_title == "Data Scientist"
        assert len(roadmap.phases) > 0
        assert roadmap.capstone_project is not None
        assert "```mermaid" in roadmap.mermaid_diagram

    def test_02_generate_dag_graph_model(self):
        profile = ["Python", "SQL"]
        career = "Data Scientist"
        dag = self.generator.generate_dag_graph_model(profile, career)
        
        assert dag["career_title"] == "Data Scientist"
        assert len(dag["nodes"]) > 0
        assert len(dag["edges"]) > 0
        
        # Verify node statuses
        statuses = {n["status"] for n in dag["nodes"]}
        assert "mastered" in statuses
        assert ("ready" in statuses or "locked" in statuses)
        
        # Check specific node fields
        for node in dag["nodes"]:
            assert "id" in node
            assert "name" in node
            assert "status" in node
            assert "layer" in node
            assert node["status"] in ["mastered", "ready", "locked"]

    def test_03_generate_study_sprint_calendar(self):
        profile = ["Python"]
        career = "Machine Learning Engineer"
        sprints = self.generator.generate_study_sprint_calendar(profile, career, target_days=60, daily_hours=1.5)
        
        assert sprints["career_title"] == "Machine Learning Engineer"
        assert sprints["target_days"] == 60
        assert sprints["daily_hours"] == 1.5
        assert len(sprints["weekly_sprints"]) > 0
        assert "BEGIN:VCALENDAR" in sprints["ical_content"]
        assert "END:VCALENDAR" in sprints["ical_content"]
        assert "# 🎯" in sprints["notion_markdown"]

    def test_04_generate_icalendar_ics_format(self):
        profile = ["Python", "SQL"]
        career = "Backend Developer"
        sprints = self.generator.generate_study_sprint_calendar(profile, career, target_days=30, daily_hours=2.0)
        ical = sprints["ical_content"]
        
        assert "BEGIN:VCALENDAR" in ical
        assert "VERSION:2.0" in ical
        assert "BEGIN:VEVENT" in ical
        assert "SUMMARY:🚀 [SkillGap AI]" in ical
        assert "END:VEVENT" in ical
        assert "END:VCALENDAR" in ical
