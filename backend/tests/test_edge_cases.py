#!/usr/bin/env python3
"""
Comprehensive edge case tests for the MCP server tools.
Tests extreme values, invalid inputs, and boundary conditions.
"""

import pytest
import json
from pathlib import Path
import sys

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.server import (
    parse_clinical_note, identify_condition, calculate_medication_dose,
    generate_treatment_plan, load_json_data
)
from mcp_server.utils.error_handler import (
    ValidationError, DataError, BusinessLogicError, ProcessingError,
    ErrorCode
)


class TestEdgeCasesParseNotes:
    """Test edge cases for clinical note parsing."""
    
    def test_empty_clinical_note(self):
        """Test parsing empty clinical note."""
        with pytest.raises(ValidationError):
            await parse_clinical_note("")
    
    def test_very_short_clinical_note(self):
        """Test parsing very short clinical note."""
        with pytest.raises(ValidationError):
            await parse_clinical_note("Sick")
    
    def test_extremely_long_clinical_note(self):
        """Test parsing extremely long clinical note."""
        long_note = "Patient presents with symptoms. " * 1000  # Very long note
        with pytest.raises(ValidationError):
            await parse_clinical_note(long_note)
    
    def test_clinical_note_with_special_characters(self):
        """Test parsing clinical note with special characters and unicode."""
        note = "Patient: José María\nAge: 5 years\nWeight: 18.5 kg\nSymptoms: fever 39°C, cough\nAssessment: possible pneumonia"
        result = await parse_clinical_note(note)
        assert result['success'] is True
        assert 'José María' in result['patient_data']['name']
    
    def test_clinical_note_with_no_identifiable_data(self):
        """Test parsing clinical note with no identifiable patient data."""
        note = "This is just random text without any clinical information or patient data."
        result = await parse_clinical_note(note)
        assert result['success'] is False
        assert 'insufficient' in result['error'].lower()


class TestEdgeCasesConditionIdentification:
    """Test edge cases for condition identification."""
    
    def test_empty_symptoms_and_assessment(self):
        """Test condition identification with empty symptoms and assessment."""
        with pytest.raises(ValidationError):
            await identify_condition([], "")
    
    def test_negative_patient_age(self):
        """Test condition identification with negative patient age."""
        with pytest.raises(ValidationError):
            await identify_condition(["fever", "cough"], "respiratory infection", patient_age=-5)
    
    def test_extremely_high_patient_age(self):
        """Test condition identification with extremely high patient age."""
        with pytest.raises(ValidationError):
            await identify_condition(["fever", "cough"], "respiratory infection", patient_age=200)
    
    def test_valid_boundary_ages(self):
        """Test condition identification with boundary ages (0 and 150)."""
        # Test age 0 (newborn)
        result = await identify_condition(["fever", "cough"], "respiratory infection", patient_age=0)
        assert result['success'] is True
        
        # Test age 150 (maximum allowed)
        result = await identify_condition(["fever", "cough"], "respiratory infection", patient_age=150)
        assert result['success'] is True
    
    def test_unknown_symptoms(self):
        """Test condition identification with completely unknown symptoms."""
        unknown_symptoms = ["purple spots", "singing voice", "rainbow vision"]
        result = await identify_condition(unknown_symptoms, "unknown condition")
        assert result['success'] is True
        assert len(result['matches']) == 0  # No matches for unknown symptoms
    
    def test_very_long_symptom_list(self):
        """Test condition identification with extremely long symptom list."""
        long_symptoms = [f"symptom_{i}" for i in range(50)]  # 50 symptoms
        with pytest.raises(ValidationError):  # Should fail due to maxItems constraint
            await identify_condition(long_symptoms, "complex condition")
    
    def test_empty_symptom_strings(self):
        """Test condition identification with empty symptom strings."""
        with pytest.raises(ValidationError):
            await identify_condition(["", "fever", ""], "respiratory infection")


class TestEdgeCasesMedicationDosing:
    """Test edge cases for medication dose calculation."""
    
    def test_negative_weight(self):
        """Test medication dosing with negative weight."""
        with pytest.raises(ValidationError):
            await calculate_medication_dose("dexamethasone", "croup", -5.0)
    
    def test_zero_weight(self):
        """Test medication dosing with zero weight."""
        with pytest.raises(ValidationError):
            await calculate_medication_dose("dexamethasone", "croup", 0.0)
    
    def test_extremely_low_weight(self):
        """Test medication dosing with extremely low weight."""
        with pytest.raises(ValidationError):
            await calculate_medication_dose("dexamethasone", "croup", 0.1)  # Below minimum 0.5kg
    
    def test_extremely_high_weight(self):
        """Test medication dosing with extremely high weight."""
        with pytest.raises(ValidationError):
            await calculate_medication_dose("dexamethasone", "croup", 500.0)  # Above maximum 300kg
    
    def test_boundary_weights(self):
        """Test medication dosing with boundary weights."""
        # Test minimum weight (0.5kg)
        result = await calculate_medication_dose("dexamethasone", "croup", 0.5)
        assert result['success'] is True
        assert result['final_dose'] >= result['min_dose']
        
        # Test maximum weight (300kg)
        result = await calculate_medication_dose("dexamethasone", "croup", 300.0)
        assert result['success'] is True
        assert result['final_dose'] <= result['max_dose']
    
    def test_unknown_medication(self):
        """Test medication dosing with unknown medication."""
        with pytest.raises(BusinessLogicError):
            await calculate_medication_dose("unknown_drug", "croup", 15.0)
    
    def test_unknown_condition(self):
        """Test medication dosing with unknown condition."""
        with pytest.raises(BusinessLogicError):
            await calculate_medication_dose("dexamethasone", "unknown_condition", 15.0)
    
    def test_invalid_severity(self):
        """Test medication dosing with invalid severity."""
        with pytest.raises(ValidationError):
            await calculate_medication_dose("dexamethasone", "croup", 15.0, severity="critical")
    
    def test_valid_severity_options(self):
        """Test medication dosing with all valid severity options."""
        valid_severities = ["mild", "moderate", "severe", "life-threatening"]
        for severity in valid_severities:
            result = await calculate_medication_dose("dexamethasone", "croup", 15.0, severity=severity)
            assert result['success'] is True
    
    def test_empty_medication_name(self):
        """Test medication dosing with empty medication name."""
        with pytest.raises(ValidationError):
            await calculate_medication_dose("", "croup", 15.0)
    
    def test_empty_condition_name(self):
        """Test medication dosing with empty condition name."""
        with pytest.raises(ValidationError):
            await calculate_medication_dose("dexamethasone", "", 15.0)
    
    def test_medication_with_special_characters(self):
        """Test medication dosing with medication name containing special characters."""
        with pytest.raises(ValidationError):  # Should fail pattern validation
            await calculate_medication_dose("dexamethasone@#$", "croup", 15.0)


class TestEdgeCasesTreatmentPlanning:
    """Test edge cases for treatment plan generation."""
    
    def test_empty_condition(self):
        """Test treatment planning with empty condition."""
        patient_data = {"age": 5, "weight": 15.0, "name": "Test Patient"}
        with pytest.raises(ValidationError):
            await generate_treatment_plan("", "moderate", patient_data)
    
    def test_invalid_severity(self):
        """Test treatment planning with invalid severity."""
        patient_data = {"age": 5, "weight": 15.0, "name": "Test Patient"}
        with pytest.raises(ValidationError):
            await generate_treatment_plan("croup", "extreme", patient_data)
    
    def test_missing_patient_data(self):
        """Test treatment planning with missing patient data."""
        with pytest.raises(ValidationError):
            await generate_treatment_plan("croup", "moderate", {})
    
    def test_patient_data_missing_required_fields(self):
        """Test treatment planning with patient data missing required fields."""
        # Missing weight
        patient_data = {"age": 5, "name": "Test Patient"}
        with pytest.raises(ValidationError):
            await generate_treatment_plan("croup", "moderate", patient_data)
        
        # Missing age
        patient_data = {"weight": 15.0, "name": "Test Patient"}
        with pytest.raises(ValidationError):
            await generate_treatment_plan("croup", "moderate", patient_data)
    
    def test_patient_data_with_invalid_age(self):
        """Test treatment planning with invalid patient age."""
        patient_data = {"age": -5, "weight": 15.0, "name": "Test Patient"}
        with pytest.raises(ValidationError):
            await generate_treatment_plan("croup", "moderate", patient_data)
    
    def test_patient_data_with_invalid_weight(self):
        """Test treatment planning with invalid patient weight."""
        patient_data = {"age": 5, "weight": -15.0, "name": "Test Patient"}
        with pytest.raises(ValidationError):
            await generate_treatment_plan("croup", "moderate", patient_data)
    
    def test_extremely_large_calculated_doses_array(self):
        """Test treatment planning with extremely large calculated doses array."""
        patient_data = {"age": 5, "weight": 15.0, "name": "Test Patient"}
        large_doses = [{"medication": f"med_{i}", "final_dose": 5.0, "unit": "mg", "route": "oral", "frequency": "daily"} for i in range(20)]
        with pytest.raises(ValidationError):  # Should fail maxItems constraint
            await generate_treatment_plan("croup", "moderate", patient_data, large_doses)
    
    def test_unknown_condition_for_treatment_plan(self):
        """Test treatment planning with unknown condition."""
        patient_data = {"age": 5, "weight": 15.0, "name": "Test Patient"}
        with pytest.raises(BusinessLogicError):
            await generate_treatment_plan("unknown_condition", "moderate", patient_data)


class TestEdgeCasesDataValidation:
    """Test edge cases for data file validation."""
    
    def test_corrupted_conditions_file(self):
        """Test handling of corrupted conditions file."""
        # This would need to be mocked in a real test
        pass
    
    def test_missing_conditions_file(self):
        """Test handling of missing conditions file."""
        # This would need to be mocked in a real test
        pass
    
    def test_invalid_json_in_conditions_file(self):
        """Test handling of invalid JSON in conditions file."""
        # This would need to be mocked in a real test
        pass


class TestEdgeCasesIntegrationScenarios:
    """Test edge cases for complete integration scenarios."""
    
    def test_premature_infant_scenario(self):
        """Test scenario with premature infant (very low weight)."""
        # This should handle the minimum weight boundary properly
        result = await calculate_medication_dose("dexamethasone", "croup", 0.5)  # 500g baby
        assert result['success'] is True
        assert result['final_dose'] >= result['min_dose']
    
    def test_morbidly_obese_adult_scenario(self):
        """Test scenario with morbidly obese adult (very high weight)."""
        # This should handle the maximum weight boundary and dose capping
        result = await calculate_medication_dose("prednisolone", "acute_asthma", 299.0)  # Just under max
        assert result['success'] is True
        assert result['final_dose'] <= result['max_dose']
    
    def test_elderly_patient_boundary_scenario(self):
        """Test scenario with elderly patient at age boundary."""
        result = await identify_condition(["shortness of breath", "wheeze"], "asthma exacerbation", patient_age=150)
        assert result['success'] is True
    
    def test_newborn_patient_scenario(self):
        """Test scenario with newborn patient."""
        result = await identify_condition(["fever", "poor feeding"], "possible sepsis", patient_age=0)
        assert result['success'] is True
    
    def test_medication_dose_ceiling_effect(self):
        """Test medication dose calculation hitting maximum dose ceiling."""
        # Use a heavy patient to test dose ceiling
        result = await calculate_medication_dose("dexamethasone", "croup", 200.0)
        assert result['success'] is True
        assert result['final_dose'] == result['max_dose']  # Should hit ceiling
        assert result['calculated_dose'] > result['final_dose']  # Original calculation was higher
    
    def test_medication_dose_floor_effect(self):
        """Test medication dose calculation hitting minimum dose floor."""
        # Use a very light patient to test dose floor
        result = await calculate_medication_dose("dexamethasone", "croup", 0.5)
        assert result['success'] is True
        # For very light patients, calculated dose might be below minimum
        if result['calculated_dose'] < result['min_dose']:
            assert result['final_dose'] == result['min_dose']


# Pytest fixtures for edge case testing
@pytest.fixture
def minimal_valid_patient_data():
    """Fixture providing minimal valid patient data."""
    return {
        "age": 5,
        "weight": 15.0,
        "name": "Test Patient",
        "symptoms": ["fever", "cough"],
        "assessment": "respiratory infection"
    }


@pytest.fixture
def boundary_test_weights():
    """Fixture providing boundary test weights."""
    return [0.5, 1.0, 50.0, 100.0, 200.0, 299.0, 300.0]


@pytest.fixture
def boundary_test_ages():
    """Fixture providing boundary test ages."""
    return [0, 1, 17, 18, 65, 100, 149, 150]


# Performance edge case tests
class TestPerformanceEdgeCases:
    """Test performance with edge case inputs."""
    
    def test_large_symptom_processing(self):
        """Test processing of maximum allowed symptoms."""
        max_symptoms = ["symptom_" + str(i) for i in range(19)]  # Just under limit
        result = await identify_condition(max_symptoms, "complex condition")
        assert result['success'] is True
    
    def test_maximum_length_clinical_note(self):
        """Test processing of maximum length clinical note."""
        max_note = "Patient presents with symptoms. " * 200  # Close to max length
        result = await parse_clinical_note(max_note)
        assert result['success'] is True
    
    def test_unicode_handling_in_clinical_notes(self):
        """Test handling of unicode characters in clinical notes."""
        unicode_note = """
        Patient: François Müller
        Age: 7 años
        Weight: 22.5 kg
        Symptoms: fièvre 39°C, toux sèche
        Assessment: pneumonie possible
        """
        result = await parse_clinical_note(unicode_note)
        assert result['success'] is True
        assert 'François' in result['patient_data']['name']