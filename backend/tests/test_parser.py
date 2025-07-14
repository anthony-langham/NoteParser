#!/usr/bin/env python3

import pytest
import asyncio
from mcp_server.tools.parser import ClinicalNoteParser, parse_clinical_note
from mcp_server.schemas.patient import PatientData, ClinicalNote, ParsedClinicalNote

class TestClinicalNoteParser:
    """Test cases for clinical note parsing."""

    @pytest.fixture
    def parser(self):
        return ClinicalNoteParser()

    @pytest.fixture
    def sample_note(self):
        return """
Patient: Jack T.
DOB: 12/03/2022
Age: 3 years
Weight: 14.2 kg

Presenting complaint:
Jack presented with a 2-day history of barky cough, hoarse voice, and low-grade fever. Symptoms worsened overnight, with increased work of breathing and stridor noted at rest this morning.

Assessment:
Jack presents with classic features of moderate croup (laryngotracheobronchitis), likely viral in origin.

Plan:
- Administer corticosteroids
- Plan as per local guidelines for croup
"""

    def test_extract_demographics(self, parser, sample_note):
        """Test demographic extraction."""
        demographics = parser.extract_demographics(sample_note)
        
        assert demographics.age == 3
        assert demographics.weight == 14.2
        assert demographics.dob == "12/03/2022"
        assert demographics.height is None
        assert demographics.gender is None

    def test_extract_symptoms(self, parser, sample_note):
        """Test symptom extraction."""
        symptoms = parser.extract_symptoms(sample_note)
        
        expected_symptoms = ["barky cough", "hoarse voice", "stridor", "fever", "work of breathing", "cough"]
        assert len(symptoms) == len(expected_symptoms)
        for symptom in expected_symptoms:
            assert symptom in symptoms

    def test_extract_vital_signs(self, parser):
        """Test vital signs extraction."""
        note_with_vitals = """
Patient vital signs:
T 38.2°C
HR 110 bpm
RR 28
BP 100/60 mmHg
O2 sat: 98%
"""
        vitals = parser.extract_vital_signs(note_with_vitals)
        
        assert vitals.temperature == 38.2
        assert vitals.heart_rate == 110
        assert vitals.respiratory_rate == 28
        assert vitals.blood_pressure == "100/60"
        assert vitals.oxygen_saturation == 98.0

    def test_extract_sections(self, parser, sample_note):
        """Test section extraction."""
        sections = parser.extract_sections(sample_note)
        
        assert "presenting_complaint" in sections
        assert "assessment" in sections
        assert "plan" in sections
        
        assert "2-day history of barky cough" in sections["presenting_complaint"]
        assert "moderate croup" in sections["assessment"]
        assert "corticosteroids" in sections["plan"]

    def test_parse_complete_note(self, parser, sample_note):
        """Test complete note parsing."""
        result = parser.parse(sample_note)
        
        assert result.success is True
        assert len(result.errors) == 0
        assert result.data is not None
        assert result.raw_text == sample_note
        
        # Test patient data
        assert result.data.patient_data.age == 3
        assert result.data.patient_data.weight == 14.2
        
        # Test symptoms
        assert "barky cough" in result.data.symptoms
        assert "stridor" in result.data.symptoms
        
        # Test assessment
        assert "moderate croup" in result.data.assessment

    def test_parse_malformed_note(self, parser):
        """Test parsing of malformed note."""
        malformed_note = "This is not a proper clinical note"
        
        result = parser.parse(malformed_note)
        
        assert result.success is True  # Should still succeed but with limited data
        assert result.data is not None
        assert result.data.patient_data.age is None
        assert result.data.patient_data.weight is None

    def test_parse_empty_note(self, parser):
        """Test parsing of empty note."""
        result = parser.parse("")
        
        assert result.success is True
        assert result.data is not None
        assert result.data.patient_data.age is None
        assert len(result.data.symptoms) == 0

    @pytest.mark.asyncio
    async def test_convenience_function(self, sample_note):
        """Test the convenience function."""
        result = await parse_clinical_note(sample_note)
        
        assert "patient_data" in result
        assert "symptoms" in result
        assert "assessment" in result
        assert "vitals" in result
        
        assert result["patient_data"]["age"] == 3
        assert result["patient_data"]["weight"] == 14.2
        assert "barky cough" in result["symptoms"]

    def test_age_validation(self):
        """Test age validation."""
        # Valid age
        valid_data = PatientData(age=25)
        assert valid_data.age == 25
        
        # Invalid age - should raise ValueError
        with pytest.raises(ValueError, match="Age must be between 0 and 150 years"):
            PatientData(age=200)
        
        with pytest.raises(ValueError, match="Age must be between 0 and 150 years"):
            PatientData(age=-5)

    def test_weight_validation(self):
        """Test weight validation."""
        # Valid weight
        valid_data = PatientData(weight=70.5)
        assert valid_data.weight == 70.5
        
        # Invalid weight - should raise ValueError
        with pytest.raises(ValueError, match="Weight must be between 0.5 and 500 kg"):
            PatientData(weight=600)
        
        with pytest.raises(ValueError, match="Weight must be between 0.5 and 500 kg"):
            PatientData(weight=0.1)

    def test_various_age_formats(self, parser):
        """Test different age format patterns."""
        test_cases = [
            ("Patient is 25 years old", 25),
            ("Age: 30 years", 30),
            ("45 yo male", 45),
            ("Age 60", 60),
            ("The patient is 5 years old", 5),
        ]
        
        for note, expected_age in test_cases:
            demographics = parser.extract_demographics(note)
            assert demographics.age == expected_age

    def test_various_weight_formats(self, parser):
        """Test different weight format patterns."""
        test_cases = [
            ("Weight: 75.5 kg", 75.5),
            ("Patient weighs 80 kg", 80.0),
            ("Wt: 65.2 kg", 65.2),
            ("Body weight is 70kg", 70.0),
        ]
        
        for note, expected_weight in test_cases:
            demographics = parser.extract_demographics(note)
            assert demographics.weight == expected_weight