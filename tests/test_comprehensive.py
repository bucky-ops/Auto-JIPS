"""Comprehensive test suite for AJIPS."""

import pytest
from ajips.app.services.enhanced_extraction import (
    extract_salary_range,
    extract_interview_stages,
)

class TestSalaryExtraction:
    """Test salary extraction functionality."""
    
    def test_salary_range_dollar_format(self):
        """Test extraction of salary range in dollar format."""
        text = "We offer a salary of $50,000 to $100,000 per year"
        result = extract_salary_range(text)
        assert result is not None
        assert result["min"] == 50000
        assert result["max"] == 100000
    
    def test_salary_k_format(self):
        """Test extraction of salary in k format."""
        text = "Salary range: 50k-100k"
        result = extract_salary_range(text)
        assert result is not None
        assert result["min"] == 50000
        assert result["max"] == 100000
    
    def test_salary_no_match(self):
        """Test extraction when no salary is present."""
        text = "Join our amazing team"
        result = extract_salary_range(text)
        assert result is None
    
    def test_salary_single_value(self):
        """Test extraction with single salary value."""
        text = "Compensation: $75,000 per year"
        result = extract_salary_range(text)
        assert result is not None
        assert result["min"] == 75000

class TestInterviewExtraction:
    """Test interview stage detection."""
    
    def test_interview_stage_detection_phone(self):
        """Test detection of phone interview."""
        text = "Process includes phone screen and technical interview"
        result = extract_interview_stages(text)
        assert "phone" in result["stages"]
        assert "technical" in result["stages"]
    
    def test_interview_stage_detection_comprehensive(self):
        """Test detection of multiple interview stages."""
        text = "Process: phone screen, technical interview, system design, behavioral round"
        result = extract_interview_stages(text)
        assert len(result["stages"]) >= 3
    
    def test_no_interview_mention(self):
        """Test when no interview process is mentioned."""
        text = "Amazing job opportunity for talented developers"
        result = extract_interview_stages(text)
        assert result["stages"] == []
    
    def test_interview_rounds_detection(self):
        """Test detection of number of interview rounds."""
        text = "The interview process consists of 4 rounds"
        result = extract_interview_stages(text)
        assert result["estimated_rounds"] == 4

class TestIntegration:
    """Integration tests for salary and interview extraction."""
    
    def test_full_extraction_pipeline(self):
        """Test full extraction pipeline."""
        text = """
        Job: Senior Backend Engineer
        Salary: $100,000 to $150,000
        
        The interview process includes:
        - Phone screen
        - Technical interview  
        - System design interview
        - Behavioral interview
        
        Timeline: 2-3 weeks
        """
        
        salary = extract_salary_range(text)
        interview = extract_interview_stages(text)
        
        assert salary is not None
        assert salary["min"] >= 100000
        assert len(interview["stages"]) > 0
        assert interview["estimated_rounds"] >= 3
    
    def test_entry_level_job_extraction(self):
        """Test extraction from entry-level job posting."""
        text = """
        Junior Python Developer
        
        Salary: 50k-65k
        
        Interview: phone screen, coding challenge, team interview
        """
        
        salary = extract_salary_range(text)
        interview = extract_interview_stages(text)
        
        assert salary is not None
        assert len(interview["stages"]) > 0

@pytest.mark.parametrize("salary_text,expected_min", [
    ("$50,000 - $100,000", 50000),
    ("50k-100k", 50000),
    ("Salary: $75,000", 75000),
])
def test_salary_parametrized(salary_text, expected_min):
    """Parametrized test for salary extraction."""
    result = extract_salary_range(salary_text)
    assert result is not None
    assert result["min"] == expected_min

@pytest.mark.parametrize("interview_text", [
    "Phone screen and technical interview",
    "Process: coding challenge, behavioral, system design",
    "4 rounds: phone, code, design, culture",
])
def test_interview_parametrized(interview_text):
    """Parametrized test for interview stage detection."""
    result = extract_interview_stages(interview_text)
    assert len(result["stages"]) > 0
