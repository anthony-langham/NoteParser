#!/usr/bin/env python3
"""
Unit tests for the MCP server and its tool implementations.
"""

import pytest
import json
import asyncio
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import sys

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.server import (
    load_json_data,
    parse_clinical_note,
    identify_condition,
    calculate_medication_dose,
    generate_treatment_plan
)
from mcp_server.utils.error_handler import (
    DataError, ValidationError, BusinessLogicError, ProcessingError,
    ErrorCode, ErrorDetails
)


class TestDataLoading:
    """Test JSON data loading functionality."""
    
    def test_load_json_data_success(self):
        """Test successful JSON data loading."""
        mock_data = {'test': 'data', 'conditions': {'croup': {}}}
        mock_file_content = json.dumps(mock_data)
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            result = load_json_data(Path('test.json'))
            assert result == mock_data
    
    def test_load_json_data_file_not_found(self):
        """Test handling of missing file."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with pytest.raises(DataError) as exc_info:
                load_json_data(Path('nonexistent.json'))
            
            assert exc_info.value.details.code == ErrorCode.DATA_FILE_NOT_FOUND
            assert 'nonexistent.json' in exc_info.value.details.message
    
    def test_load_json_data_invalid_json(self):
        """Test handling of invalid JSON."""
        with patch('builtins.open', mock_open(read_data='invalid json')):
            with pytest.raises(DataError) as exc_info:
                load_json_data(Path('invalid.json'))
            
            assert exc_info.value.details.code == ErrorCode.DATA_FILE_CORRUPTED
    
    def test_load_json_data_non_dict(self):
        """Test handling of JSON that's not a dictionary."""
        mock_array = ['not', 'a', 'dict']
        mock_file_content = json.dumps(mock_array)
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with pytest.raises(DataError) as exc_info:
                load_json_data(Path('array.json'))
            
            assert exc_info.value.details.code == ErrorCode.DATA_FILE_CORRUPTED
            assert 'valid JSON object' in exc_info.value.details.message


class TestClinicalNoteParser:
    """Test clinical note parsing MCP tool."""
    
    @pytest.mark.asyncio
    async def test_parse_clinical_note_complete(self):
        """Test parsing a complete clinical note."""
        sample_note = """
Patient: Jack T.
DOB: 12/03/2022
Age: 3 years
Weight: 14.2 kg

Presenting complaint:
Jack presented with a 2-day history of barky cough, hoarse voice, and low-grade fever.

Assessment:
Jack presents with classic features of moderate croup (laryngotracheobronchitis).

Plan:
- Administer corticosteroids
"""
        
        result = await parse_clinical_note(sample_note)
        
        assert result['success'] is True
        assert 'patient_data' in result
        assert result['patient_data']['age'] == 3
        assert result['patient_data']['weight'] == 14.2
        assert result['patient_data']['dob'] == '12/03/2022'
        assert 'barky cough' in result['symptoms']
        assert 'hoarse voice' in result['symptoms']
        assert 'moderate croup' in result['assessment'].lower()
    
    @pytest.mark.asyncio
    async def test_parse_clinical_note_minimal(self):
        """Test parsing with minimal information."""
        minimal_note = "Patient has a persistent cough and fever."
        
        result = await parse_clinical_note(minimal_note)
        
        assert result['success'] is True
        assert 'patient_data' in result
        assert 'symptoms' in result
        assert 'cough' in result['symptoms']
        assert 'fever' in result['symptoms']
    
    @pytest.mark.asyncio
    async def test_parse_clinical_note_empty(self):
        """Test parsing with empty note."""
        result = await parse_clinical_note("")
        
        assert result['success'] is True
        assert 'patient_data' in result
        assert 'symptoms' in result
        assert result['symptoms'] == []
    
    @pytest.mark.asyncio
    async def test_parse_clinical_note_with_vitals(self):
        """Test parsing note with vital signs."""
        note_with_vitals = """
Patient: Emma S.
Age: 5 years
Weight: 18 kg

Vital signs:
T 38.5°C
HR 120 bpm
RR 30/min
O2 sat: 97%

Assessment: Febrile illness
"""
        
        result = await parse_clinical_note(note_with_vitals)
        
        assert result['success'] is True
        assert 'vitals' in result
        assert result['vitals']['temperature'] == 38.5
        assert result['vitals']['heart_rate'] == 120
        assert result['vitals']['respiratory_rate'] == 30
        assert result['vitals']['oxygen_saturation'] == 97.0


class TestConditionIdentification:
    """Test condition identification MCP tool."""
    
    @pytest.fixture
    def mock_conditions_data(self):
        """Mock conditions data for testing."""
        return {
            'croup': {
                'name': 'Croup (Laryngotracheobronchitis)',
                'symptoms': {
                    'primary': ['barky cough', 'hoarse voice', 'stridor'],
                    'secondary': ['fever', 'rhinitis']
                },
                'age_groups': ['pediatric']
            },
            'bronchiolitis': {
                'name': 'Bronchiolitis',
                'symptoms': {
                    'primary': ['wheezing', 'cough', 'respiratory distress'],
                    'secondary': ['fever', 'poor feeding']
                },
                'age_groups': ['pediatric']
            }
        }
    
    @pytest.mark.asyncio
    async def test_identify_condition_success(self, mock_conditions_data):
        """Test successful condition identification."""
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_data):
            result = await identify_condition(
                ['barky cough', 'hoarse voice', 'stridor'], 
                'moderate croup symptoms', 
                3
            )
            
            assert result['success'] is True
            assert 'matches' in result
            assert len(result['matches']) > 0
            assert result['matches'][0]['condition_id'] == 'croup'
            assert result['matches'][0]['match_score'] > 0.5
    
    @pytest.mark.asyncio
    async def test_identify_condition_no_data(self):
        """Test condition identification when no data file exists."""
        with patch('mcp_server.server.load_json_data', side_effect=DataError(ErrorDetails(
            code=ErrorCode.DATA_FILE_NOT_FOUND,
            message="Data file not found",
            details={},
            recoverable=False
        ))):
            result = await identify_condition(['cough'], 'cough', 3)
            
            assert result['success'] is False
            assert 'error' in result
            assert result['error']['code'] == ErrorCode.DATA_FILE_NOT_FOUND.value
    
    @pytest.mark.asyncio
    async def test_identify_condition_no_matches(self, mock_conditions_data):
        """Test condition identification with no symptom matches."""
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_data):
            result = await identify_condition(
                ['completely_unrelated_symptom'], 
                'unrelated symptoms', 
                30
            )
            
            assert result['success'] is True
            assert len(result['matches']) == 0
    
    @pytest.mark.asyncio
    async def test_identify_condition_age_filtering(self, mock_conditions_data):
        """Test that age filtering works correctly."""
        # Add adult-only condition
        mock_conditions_data['myocardial_infarction'] = {
            'name': 'Myocardial Infarction',
            'symptoms': {
                'primary': ['chest pain', 'shortness of breath'],
                'secondary': ['nausea', 'sweating']
            },
            'age_groups': ['adult']
        }
        
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_data):
            # Test pediatric patient
            result = await identify_condition(
                ['chest pain'], 'chest pain', 5
            )
            
            assert result['success'] is True
            # Should not match adult-only conditions
            condition_ids = [m['condition_id'] for m in result['matches']]
            assert 'myocardial_infarction' not in condition_ids


class TestMedicationDoseCalculation:
    """Test medication dose calculation MCP tool."""
    
    @pytest.fixture
    def mock_conditions_with_meds(self):
        """Mock conditions data with medications."""
        return {
            'croup': {
                'name': 'Croup (Laryngotracheobronchitis)',
                'medications': {
                    'first_line': {
                        'dexamethasone': {
                            'dose_mg_per_kg': 0.15,
                            'max_dose_mg': 10.0,
                            'min_dose_mg': 0.6,
                            'route': 'oral',
                            'frequency': 'single_dose',
                            'duration': '1 day',
                            'contraindications': ['known hypersensitivity']
                        },
                        'prednisolone': {
                            'dose_mg_per_kg': 1.0,
                            'max_dose_mg': 40.0,
                            'min_dose_mg': 5.0,
                            'route': 'oral',
                            'frequency': 'daily',
                            'duration': '3-5 days',
                            'contraindications': ['systemic fungal infections']
                        }
                    }
                }
            }
        }
    
    @pytest.mark.asyncio
    async def test_calculate_dose_success(self, mock_conditions_with_meds):
        """Test successful dose calculation."""
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_with_meds):
            result = await calculate_medication_dose('dexamethasone', 'croup', 14.2)
            
            assert result['success'] is True
            assert 'dose_calculation' in result
            dose_calc = result['dose_calculation']
            assert dose_calc['medication'] == 'dexamethasone'
            assert dose_calc['calculated_dose'] == 2.13  # 0.15 * 14.2
            assert dose_calc['final_dose'] == 2.13
            assert dose_calc['route'] == 'oral'
            assert dose_calc['frequency'] == 'single_dose'
    
    @pytest.mark.asyncio
    async def test_calculate_dose_max_limit(self, mock_conditions_with_meds):
        """Test dose calculation with maximum dose limit."""
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_with_meds):
            result = await calculate_medication_dose('dexamethasone', 'croup', 100.0)
            
            assert result['success'] is True
            dose_calc = result['dose_calculation']
            assert dose_calc['calculated_dose'] == 15.0  # 0.15 * 100
            assert dose_calc['final_dose'] == 10.0  # Limited by max_dose_mg
            assert dose_calc['dose_limited'] == 'maximum'
    
    @pytest.mark.asyncio
    async def test_calculate_dose_min_limit(self, mock_conditions_with_meds):
        """Test dose calculation with minimum dose limit."""
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_with_meds):
            result = await calculate_medication_dose('dexamethasone', 'croup', 2.0)
            
            assert result['success'] is True
            dose_calc = result['dose_calculation']
            assert dose_calc['calculated_dose'] == 0.3  # 0.15 * 2.0
            assert dose_calc['final_dose'] == 0.6  # Limited by min_dose_mg
            assert dose_calc['dose_limited'] == 'minimum'
    
    @pytest.mark.asyncio
    async def test_calculate_dose_invalid_medication(self, mock_conditions_with_meds):
        """Test dose calculation with invalid medication."""
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_with_meds):
            result = await calculate_medication_dose('invalid_medication', 'croup', 14.2)
            
            assert result['success'] is False
            assert 'error' in result
            assert result['error']['code'] == ErrorCode.MEDICATION_NOT_FOUND.value
    
    @pytest.mark.asyncio
    async def test_calculate_dose_invalid_condition(self, mock_conditions_with_meds):
        """Test dose calculation with invalid condition."""
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_with_meds):
            result = await calculate_medication_dose('dexamethasone', 'invalid_condition', 14.2)
            
            assert result['success'] is False
            assert 'error' in result
            assert result['error']['code'] == ErrorCode.CONDITION_NOT_FOUND.value
    
    @pytest.mark.asyncio
    async def test_calculate_dose_invalid_weight(self, mock_conditions_with_meds):
        """Test dose calculation with invalid weight."""
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_with_meds):
            result = await calculate_medication_dose('dexamethasone', 'croup', -1.0)
            
            assert result['success'] is False
            assert 'error' in result
            assert result['error']['code'] == ErrorCode.INVALID_PATIENT_DATA.value


class TestTreatmentPlanGeneration:
    """Test treatment plan generation MCP tool."""
    
    @pytest.fixture
    def mock_complete_data(self):
        """Mock complete data for treatment plan testing."""
        return {
            'croup': {
                'name': 'Croup (Laryngotracheobronchitis)',
                'description': 'Viral infection of the larynx and trachea',
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
                ],
                'medications': {
                    'first_line': {
                        'dexamethasone': {
                            'dose_mg_per_kg': 0.15,
                            'max_dose_mg': 10.0,
                            'min_dose_mg': 0.6,
                            'route': 'oral',
                            'frequency': 'single_dose'
                        }
                    }
                }
            }
        }
    
    @pytest.mark.asyncio
    async def test_generate_treatment_plan_success(self, mock_complete_data):
        """Test successful treatment plan generation."""
        patient_data = {
            'patient_data': {'age': 3, 'weight': 14.2},
            'symptoms': ['barky cough', 'hoarse voice'],
            'assessment': 'moderate croup'
        }
        
        calculated_doses = [{
            'medication': 'dexamethasone',
            'final_dose': 2.13,
            'route': 'oral',
            'frequency': 'single_dose'
        }]
        
        with patch('mcp_server.server.load_json_data', return_value=mock_complete_data):
            result = await generate_treatment_plan('croup', 'moderate', patient_data, calculated_doses)
            
            assert result['success'] is True
            assert 'treatment_plan' in result
            
            plan = result['treatment_plan']
            assert plan['condition'] == 'Croup (Laryngotracheobronchitis)'
            assert plan['severity'] == 'moderate'
            assert 'patient_summary' in plan
            assert 'medications' in plan
            assert 'red_flags' in plan
            assert 'clinical_pearls' in plan
            assert len(plan['medications']) > 0
    
    @pytest.mark.asyncio
    async def test_generate_treatment_plan_no_data(self):
        """Test treatment plan generation when no data exists."""
        with patch('mcp_server.server.load_json_data', side_effect=DataError(ErrorDetails(
            code=ErrorCode.DATA_FILE_NOT_FOUND,
            message="Data file not found",
            details={},
            recoverable=False
        ))):
            result = await generate_treatment_plan('croup', 'moderate', {}, [])
            
            assert result['success'] is False
            assert 'error' in result
            assert result['error']['code'] == ErrorCode.DATA_FILE_NOT_FOUND.value
    
    @pytest.mark.asyncio
    async def test_generate_treatment_plan_invalid_condition(self, mock_complete_data):
        """Test treatment plan generation with invalid condition."""
        with patch('mcp_server.server.load_json_data', return_value=mock_complete_data):
            result = await generate_treatment_plan('invalid_condition', 'mild', {}, [])
            
            assert result['success'] is False
            assert 'error' in result
            assert result['error']['code'] == ErrorCode.CONDITION_NOT_FOUND.value
    
    @pytest.mark.asyncio
    async def test_generate_treatment_plan_minimal_data(self, mock_complete_data):
        """Test treatment plan generation with minimal patient data."""
        minimal_patient_data = {
            'patient_data': {},
            'symptoms': [],
            'assessment': ''
        }
        
        with patch('mcp_server.server.load_json_data', return_value=mock_complete_data):
            result = await generate_treatment_plan('croup', 'mild', minimal_patient_data, [])
            
            assert result['success'] is True
            plan = result['treatment_plan']
            assert plan['condition'] == 'Croup (Laryngotracheobronchitis)'
            assert plan['severity'] == 'mild'


class TestMCPServerErrorHandling:
    """Test error handling across all MCP tools."""
    
    @pytest.mark.asyncio
    async def test_error_handling_consistency(self):
        """Test that all tools handle errors consistently."""
        # Test that all tools return proper error format when data files are missing
        with patch('mcp_server.server.load_json_data', side_effect=DataError(ErrorDetails(
            code=ErrorCode.DATA_FILE_NOT_FOUND,
            message="Test error",
            details={},
            recoverable=False
        ))):
            
            # Test parse_clinical_note (should still work without data files)
            parse_result = await parse_clinical_note("test note")
            assert parse_result['success'] is True
            
            # Test identify_condition
            identify_result = await identify_condition(['cough'], 'test', 3)
            assert identify_result['success'] is False
            assert 'error' in identify_result
            assert identify_result['error']['code'] == ErrorCode.DATA_FILE_NOT_FOUND.value
            
            # Test calculate_medication_dose
            dose_result = await calculate_medication_dose('test', 'test', 10.0)
            assert dose_result['success'] is False
            assert 'error' in dose_result
            assert dose_result['error']['code'] == ErrorCode.DATA_FILE_NOT_FOUND.value
            
            # Test generate_treatment_plan
            plan_result = await generate_treatment_plan('test', 'mild', {}, [])
            assert plan_result['success'] is False
            assert 'error' in plan_result
            assert plan_result['error']['code'] == ErrorCode.DATA_FILE_NOT_FOUND.value


if __name__ == '__main__':
    pytest.main([__file__, '-v'])