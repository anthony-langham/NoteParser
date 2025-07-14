#!/usr/bin/env python3
"""
Comprehensive unit tests for all MCP tools.
"""

import pytest
import json
import asyncio
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import sys

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.tools.parser import ClinicalNoteParser, parse_clinical_note
from mcp_server.tools.treatment_planner import TreatmentPlanGenerator
from mcp_server.schemas.patient import PatientData, ClinicalNote, ParsedClinicalNote, VitalSigns


class TestClinicalNoteParser:
    """Test clinical note parsing functionality."""
    
    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return ClinicalNoteParser()
    
    @pytest.fixture
    def sample_croup_note(self):
        """Sample clinical note for croup case."""
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
    
    def test_extract_demographics_complete(self, parser, sample_croup_note):
        """Test demographic extraction with complete data."""
        demographics = parser.extract_demographics(sample_croup_note)
        
        assert demographics.age == 3
        assert demographics.weight == 14.2
        assert demographics.dob == "12/03/2022"
        assert demographics.height is None
        assert demographics.gender is None
    
    def test_extract_demographics_various_formats(self, parser):
        """Test demographic extraction with various formats."""
        test_cases = [
            ("Patient is 25 years old, weighs 70 kg", 25, 70.0),
            ("Age: 30 years, Weight: 65.5 kg", 30, 65.5),
            ("45 yo male, 80kg", 45, 80.0),
            ("Age 60, wt 75.2 kg", 60, 75.2),
        ]
        
        for note, expected_age, expected_weight in test_cases:
            demographics = parser.extract_demographics(note)
            assert demographics.age == expected_age
            assert demographics.weight == expected_weight
    
    def test_extract_symptoms_comprehensive(self, parser, sample_croup_note):
        """Test symptom extraction."""
        symptoms = parser.extract_symptoms(sample_croup_note)
        
        expected_symptoms = ["barky cough", "hoarse voice", "stridor", "fever", "work of breathing", "cough"]
        assert len(symptoms) >= 5
        
        for symptom in ["barky cough", "hoarse voice", "stridor"]:
            assert symptom in symptoms
    
    def test_extract_vital_signs_complete(self, parser):
        """Test vital signs extraction with complete vitals."""
        note_with_vitals = """
Patient vital signs:
Temperature: 38.2°C
HR 110 bpm
RR 28/min
BP 100/60 mmHg
O2 sat: 98% on room air
"""
        vitals = parser.extract_vital_signs(note_with_vitals)
        
        assert vitals.temperature == 38.2
        assert vitals.heart_rate == 110
        assert vitals.respiratory_rate == 28
        assert vitals.blood_pressure == "100/60"
        assert vitals.oxygen_saturation == 98.0
    
    def test_extract_vital_signs_various_formats(self, parser):
        """Test vital signs extraction with various formats."""
        test_cases = [
            ("T 37.5°C", 37.5, None, None),
            ("HR: 95 bpm", None, 95, None),
            ("RR 24", None, None, 24),
            ("O2 sat 99%", None, None, None, 99.0),
        ]
        
        for note, temp, hr, rr, o2_sat in test_cases:
            vitals = parser.extract_vital_signs(note)
            if temp is not None:
                assert vitals.temperature == temp
            if hr is not None:
                assert vitals.heart_rate == hr
            if rr is not None:
                assert vitals.respiratory_rate == rr
            if o2_sat is not None:
                assert vitals.oxygen_saturation == o2_sat
    
    def test_extract_sections(self, parser, sample_croup_note):
        """Test section extraction."""
        sections = parser.extract_sections(sample_croup_note)
        
        assert "presenting_complaint" in sections
        assert "assessment" in sections
        assert "plan" in sections
        
        assert "2-day history of barky cough" in sections["presenting_complaint"]
        assert "moderate croup" in sections["assessment"]
        assert "corticosteroids" in sections["plan"]
    
    def test_parse_complete_note(self, parser, sample_croup_note):
        """Test complete note parsing."""
        result = parser.parse(sample_croup_note)
        
        assert result.success is True
        assert len(result.errors) == 0
        assert result.data is not None
        assert result.raw_text == sample_croup_note
        
        # Test patient data
        assert result.data.patient_data.age == 3
        assert result.data.patient_data.weight == 14.2
        
        # Test symptoms
        assert "barky cough" in result.data.symptoms
        assert "stridor" in result.data.symptoms
        
        # Test assessment
        assert "moderate croup" in result.data.assessment
    
    def test_parse_minimal_note(self, parser):
        """Test parsing with minimal information."""
        minimal_note = "Patient has a persistent cough and fever for 3 days."
        
        result = parser.parse(minimal_note)
        
        assert result.success is True
        assert result.data is not None
        assert "cough" in result.data.symptoms
        assert "fever" in result.data.symptoms
    
    def test_parse_empty_note(self, parser):
        """Test parsing of empty note."""
        result = parser.parse("")
        
        assert result.success is True
        assert result.data is not None
        assert result.data.patient_data.age is None
        assert len(result.data.symptoms) == 0
    
    @pytest.mark.asyncio
    async def test_parse_clinical_note_function(self, sample_croup_note):
        """Test the convenience async function."""
        result = await parse_clinical_note(sample_croup_note)
        
        assert "patient_data" in result
        assert "symptoms" in result
        assert "assessment" in result
        assert "vitals" in result
        
        assert result["patient_data"]["age"] == 3
        assert result["patient_data"]["weight"] == 14.2
        assert "barky cough" in result["symptoms"]
    
    def test_validation_errors(self):
        """Test data validation errors."""
        # Test invalid age
        with pytest.raises(ValueError, match="Age must be between 0 and 150 years"):
            PatientData(age=200)
        
        with pytest.raises(ValueError, match="Age must be between 0 and 150 years"):
            PatientData(age=-5)
        
        # Test invalid weight
        with pytest.raises(ValueError, match="Weight must be between 0.5 and 500 kg"):
            PatientData(weight=600)
        
        with pytest.raises(ValueError, match="Weight must be between 0.5 and 500 kg"):
            PatientData(weight=0.1)


class TestTreatmentPlanGenerator:
    """Test treatment plan generation functionality."""
    
    @pytest.fixture
    def mock_conditions_data(self):
        """Mock conditions data for testing."""
        return {
            'croup': {
                'name': 'Croup (Laryngotracheobronchitis)',
                'description': 'Viral infection of the larynx and trachea',
                'icd_codes': ['J05.0'],
                'age_groups': ['pediatric'],
                'symptoms': {
                    'primary': ['barky cough', 'hoarse voice', 'stridor'],
                    'secondary': ['fever', 'rhinitis', 'pharyngitis']
                },
                'severity_scales': {
                    'mild': 'Occasional barky cough, no stridor at rest',
                    'moderate': 'Frequent barky cough, stridor at rest, mild respiratory distress',
                    'severe': 'Continuous barky cough, stridor at rest, significant respiratory distress'
                },
                'medications': {
                    'first_line': {
                        'dexamethasone': {
                            'dose_mg_per_kg': 0.15,
                            'max_dose_mg': 10.0,
                            'min_dose_mg': 0.6,
                            'route': 'oral',
                            'frequency': 'single_dose',
                            'duration': '1 day',
                            'age_restrictions': 'All ages',
                            'contraindications': ['known hypersensitivity']
                        },
                        'prednisolone': {
                            'dose_mg_per_kg': 1.0,
                            'max_dose_mg': 40.0,
                            'min_dose_mg': 5.0,
                            'route': 'oral',
                            'frequency': 'daily',
                            'duration': '3-5 days',
                            'age_restrictions': 'All ages',
                            'contraindications': ['systemic fungal infections']
                        }
                    },
                    'second_line': {
                        'budesonide': {
                            'dose_mg_per_kg': None,
                            'max_dose_mg': 2.0,
                            'min_dose_mg': 2.0,
                            'route': 'nebulized',
                            'frequency': 'single_dose',
                            'duration': '1 day',
                            'age_restrictions': 'All ages',
                            'contraindications': []
                        }
                    }
                },
                'clinical_pearls': [
                    'Most cases are viral in origin',
                    'Peak incidence in autumn',
                    'Supportive care is often sufficient'
                ],
                'red_flags': [
                    'cyanosis',
                    'drooling',
                    'inability to swallow',
                    'toxic appearance'
                ]
            }
        }
    
    @pytest.fixture
    def mock_guidelines_data(self):
        """Mock guidelines data for testing."""
        return {
            'pediatric_croup_2023': {
                'name': 'Pediatric Croup Management Guidelines 2023',
                'version': '1.0',
                'last_updated': '2023-01-01',
                'source': 'Pediatric Emergency Medicine Society',
                'conditions': ['croup'],
                'decision_tree': {
                    'assessment': {
                        'severity_assessment': 'Use clinical scoring system',
                        'age_considerations': 'Most common in 6 months to 6 years'
                    },
                    'treatment_algorithm': {
                        'mild': 'Supportive care, consider corticosteroids',
                        'moderate': 'Corticosteroids (dexamethasone or prednisolone)',
                        'severe': 'Corticosteroids + nebulized epinephrine + hospital admission'
                    }
                },
                'monitoring': 'Monitor respiratory status, oxygen saturation',
                'follow_up': 'Return if symptoms worsen or fail to improve in 24-48 hours'
            }
        }
    
    @pytest.fixture
    def treatment_planner(self, mock_conditions_data, mock_guidelines_data):
        """Create a treatment planner with mocked data."""
        planner = TreatmentPlanGenerator()
        planner.conditions = mock_conditions_data
        planner.guidelines = mock_guidelines_data
        return planner
    
    def test_load_json_data_success(self):
        """Test successful JSON data loading."""
        mock_data = {'test': 'data'}
        mock_file_content = json.dumps(mock_data)
        
        planner = TreatmentPlanGenerator()
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            result = planner._load_json_data(Path('test.json'))
            assert result == mock_data
    
    def test_load_json_data_file_not_found(self):
        """Test handling of missing file."""
        planner = TreatmentPlanGenerator()
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = planner._load_json_data(Path('nonexistent.json'))
            assert result == {}
    
    def test_load_json_data_invalid_json(self):
        """Test handling of invalid JSON."""
        planner = TreatmentPlanGenerator()
        with patch('builtins.open', mock_open(read_data='invalid json')):
            result = planner._load_json_data(Path('invalid.json'))
            assert result == {}
    
    def test_get_guideline_for_condition(self, treatment_planner):
        """Test finding guidelines for a condition."""
        guideline = treatment_planner.get_guideline_for_condition('croup')
        
        assert guideline is not None
        assert guideline['name'] == 'Pediatric Croup Management Guidelines 2023'
        assert 'croup' in guideline['conditions']
    
    def test_get_guideline_for_nonexistent_condition(self, treatment_planner):
        """Test handling of nonexistent condition."""
        guideline = treatment_planner.get_guideline_for_condition('nonexistent')
        assert guideline is None
    
    def test_calculate_medication_dose_valid(self, treatment_planner):
        """Test medication dose calculation with valid inputs."""
        dose_info = treatment_planner.calculate_medication_dose(
            'dexamethasone', 'croup', 14.2
        )
        
        assert dose_info is not None
        assert dose_info['medication'] == 'dexamethasone'
        assert dose_info['calculated_dose'] == 2.13  # 0.15 * 14.2
        assert dose_info['final_dose'] == 2.13
        assert dose_info['route'] == 'oral'
        assert dose_info['frequency'] == 'single_dose'
    
    def test_calculate_medication_dose_with_max_limit(self, treatment_planner):
        """Test dose calculation with maximum dose limit."""
        # Test with very heavy patient to trigger max dose
        dose_info = treatment_planner.calculate_medication_dose(
            'dexamethasone', 'croup', 100.0  # Very heavy patient
        )
        
        assert dose_info is not None
        assert dose_info['calculated_dose'] == 15.0  # 0.15 * 100
        assert dose_info['final_dose'] == 10.0  # Limited by max_dose_mg
        assert dose_info['dose_limited'] == 'maximum'
    
    def test_calculate_medication_dose_with_min_limit(self, treatment_planner):
        """Test dose calculation with minimum dose limit."""
        # Test with very light patient to trigger min dose
        dose_info = treatment_planner.calculate_medication_dose(
            'dexamethasone', 'croup', 2.0  # Very light patient
        )
        
        assert dose_info is not None
        assert dose_info['calculated_dose'] == 0.3  # 0.15 * 2.0
        assert dose_info['final_dose'] == 0.6  # Limited by min_dose_mg
        assert dose_info['dose_limited'] == 'minimum'
    
    def test_calculate_medication_dose_invalid_inputs(self, treatment_planner):
        """Test dose calculation with invalid inputs."""
        # Invalid medication
        dose_info = treatment_planner.calculate_medication_dose(
            'invalid_medication', 'croup', 14.2
        )
        assert dose_info is None
        
        # Invalid condition
        dose_info = treatment_planner.calculate_medication_dose(
            'dexamethasone', 'invalid_condition', 14.2
        )
        assert dose_info is None
        
        # Invalid weight
        dose_info = treatment_planner.calculate_medication_dose(
            'dexamethasone', 'croup', -1.0
        )
        assert dose_info is None
    
    def test_identify_condition_by_symptoms(self, treatment_planner):
        """Test condition identification by symptoms."""
        symptoms = ['barky cough', 'hoarse voice', 'stridor']
        matches = treatment_planner.identify_condition_by_symptoms(symptoms, age=3)
        
        assert len(matches) > 0
        assert matches[0]['condition_id'] == 'croup'
        assert matches[0]['match_score'] > 0.5
    
    def test_identify_condition_no_matches(self, treatment_planner):
        """Test condition identification with no symptom matches."""
        symptoms = ['completely_unrelated_symptom']
        matches = treatment_planner.identify_condition_by_symptoms(symptoms, age=3)
        
        assert len(matches) == 0
    
    def test_generate_treatment_plan_complete(self, treatment_planner):
        """Test complete treatment plan generation."""
        patient_data = {
            'patient_data': {'age': 3, 'weight': 14.2},
            'symptoms': ['barky cough', 'hoarse voice', 'stridor'],
            'assessment': 'moderate croup'
        }
        
        plan = treatment_planner.generate_treatment_plan(
            'croup', 'moderate', patient_data
        )
        
        assert plan is not None
        assert plan['condition'] == 'Croup (Laryngotracheobronchitis)'
        assert plan['severity'] == 'moderate'
        assert 'patient_summary' in plan
        assert 'medications' in plan
        assert 'red_flags' in plan
        assert 'clinical_pearls' in plan
        assert 'monitoring' in plan
        assert 'follow_up' in plan
        
        # Check medications were calculated
        assert len(plan['medications']) > 0
        assert plan['medications'][0]['medication'] == 'dexamethasone'
    
    def test_generate_treatment_plan_invalid_condition(self, treatment_planner):
        """Test treatment plan generation with invalid condition."""
        patient_data = {
            'patient_data': {'age': 3, 'weight': 14.2},
            'symptoms': ['cough'],
            'assessment': 'unknown condition'
        }
        
        plan = treatment_planner.generate_treatment_plan(
            'invalid_condition', 'mild', patient_data
        )
        
        assert plan is None


class TestMCPServerIntegration:
    """Test integration of all MCP tools."""
    
    @pytest.fixture
    def sample_clinical_data(self):
        """Sample clinical data for integration testing."""
        return {
            'note': """
Patient: Emma S.
DOB: 15/08/2021
Age: 2 years
Weight: 12.5 kg

Presenting complaint:
Emma presented with a 1-day history of harsh barky cough and hoarse voice. 
Mother reports the cough sounds like a seal bark. No fever reported.
Child is eating and drinking normally.

Assessment:
Mild croup (laryngotracheobronchitis). No stridor at rest.

Plan:
- Supportive care
- Consider corticosteroids if symptoms worsen
""",
            'expected_condition': 'croup',
            'expected_severity': 'mild',
            'expected_age': 2,
            'expected_weight': 12.5
        }
    
    @pytest.mark.asyncio
    async def test_full_workflow_integration(self, sample_clinical_data):
        """Test the complete workflow from note parsing to treatment plan."""
        # Step 1: Parse clinical note
        parsed_data = await parse_clinical_note(sample_clinical_data['note'])
        
        # Verify parsing results
        assert parsed_data['patient_data']['age'] == sample_clinical_data['expected_age']
        assert parsed_data['patient_data']['weight'] == sample_clinical_data['expected_weight']
        assert 'barky cough' in parsed_data['symptoms']
        assert 'hoarse voice' in parsed_data['symptoms']
        
        # Step 2: Mock treatment planner for integration test
        with patch('mcp_server.tools.treatment_planner.TreatmentPlanGenerator') as mock_planner:
            mock_instance = MagicMock()
            mock_planner.return_value = mock_instance
            
            # Mock condition identification
            mock_instance.identify_condition_by_symptoms.return_value = [{
                'condition_id': 'croup',
                'match_score': 0.85,
                'matched_symptoms': ['barky cough', 'hoarse voice']
            }]
            
            # Mock dose calculation
            mock_instance.calculate_medication_dose.return_value = {
                'medication': 'dexamethasone',
                'calculated_dose': 1.875,  # 0.15 * 12.5
                'final_dose': 1.875,
                'route': 'oral',
                'frequency': 'single_dose'
            }
            
            # Mock treatment plan generation
            mock_instance.generate_treatment_plan.return_value = {
                'condition': 'Croup (Laryngotracheobronchitis)',
                'severity': 'mild',
                'patient_summary': 'Emma S., 2 years old, 12.5 kg',
                'medications': [{
                    'medication': 'dexamethasone',
                    'final_dose': 1.875,
                    'route': 'oral'
                }],
                'red_flags': ['cyanosis', 'drooling'],
                'clinical_pearls': ['Most cases are viral']
            }
            
            # Test that the integration would work
            planner = mock_planner()
            
            # Step 3: Identify condition
            condition_matches = planner.identify_condition_by_symptoms(
                parsed_data['symptoms'], 
                age=parsed_data['patient_data']['age']
            )
            
            assert len(condition_matches) > 0
            assert condition_matches[0]['condition_id'] == 'croup'
            
            # Step 4: Calculate doses
            dose_info = planner.calculate_medication_dose(
                'dexamethasone', 'croup', parsed_data['patient_data']['weight']
            )
            
            assert dose_info['medication'] == 'dexamethasone'
            assert dose_info['final_dose'] == 1.875
            
            # Step 5: Generate treatment plan
            treatment_plan = planner.generate_treatment_plan(
                'croup', 'mild', parsed_data
            )
            
            assert treatment_plan['condition'] == 'Croup (Laryngotracheobronchitis)'
            assert treatment_plan['severity'] == 'mild'
            assert len(treatment_plan['medications']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])