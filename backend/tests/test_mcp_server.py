"""
Tests for the MCP server basic functionality.
"""

import pytest
import json
import asyncio
from pathlib import Path
from unittest.mock import patch, mock_open

# Add the backend directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.server import (
    parse_clinical_note,
    identify_condition,
    calculate_medication_dose,
    generate_treatment_plan,
    load_json_data
)


class TestClinicalNoteParser:
    """Test clinical note parsing functionality."""
    
    @pytest.mark.asyncio
    async def test_parse_clinical_note_basic(self):
        """Test basic clinical note parsing."""
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
        sample_note = "Patient has a cough and fever."
        
        result = await parse_clinical_note(sample_note)
        
        assert 'patient_data' in result
        assert 'symptoms' in result
        assert 'cough' in result['symptoms']
        assert 'fever' in result['symptoms']
    
    @pytest.mark.asyncio
    async def test_parse_clinical_note_empty(self):
        """Test parsing with empty note."""
        result = await parse_clinical_note("")
        
        assert 'patient_data' in result
        assert 'symptoms' in result
        assert result['symptoms'] == []


class TestConditionIdentification:
    """Test condition identification functionality."""
    
    @pytest.mark.asyncio
    async def test_identify_condition_no_data(self):
        """Test condition identification when no data file exists."""
        with patch('mcp_server.server.load_json_data', return_value={}):
            result = await identify_condition(['barky cough'], 'croup', 3)
            assert 'error' in result
            assert 'not available' in result['error']
    
    @pytest.mark.asyncio
    async def test_identify_condition_with_data(self):
        """Test condition identification with sample data."""
        mock_conditions = {
            'croup': {
                'name': 'Croup (Laryngotracheobronchitis)',
                'symptoms': {
                    'primary': ['barky cough', 'hoarse voice', 'stridor']
                },
                'age_groups': ['pediatric']
            }
        }
        
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions):
            result = await identify_condition(['barky cough', 'hoarse voice'], 'croup', 3)
            
            assert 'matches' in result
            assert 'top_match' in result
            assert len(result['matches']) > 0
            assert result['top_match']['condition_id'] == 'croup'


class TestDoseCalculation:
    """Test medication dose calculation."""
    
    @pytest.mark.asyncio
    async def test_calculate_dose_no_data(self):
        """Test dose calculation when no data file exists."""
        with patch('mcp_server.server.load_json_data', return_value={}):
            result = await calculate_medication_dose('dexamethasone', 'croup', 14.2)
            assert 'error' in result
            assert 'not available' in result['error']
    
    @pytest.mark.asyncio
    async def test_calculate_dose_with_data(self):
        """Test dose calculation with sample data."""
        mock_conditions = {
            'croup': {
                'name': 'Croup (Laryngotracheobronchitis)',
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
        
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions):
            result = await calculate_medication_dose('dexamethasone', 'croup', 14.2)
            
            assert 'medication' in result
            assert 'final_dose' in result
            assert result['medication'] == 'dexamethasone'
            assert result['final_dose'] == 2.13  # 0.15 * 14.2
            assert result['route'] == 'oral'
            assert result['frequency'] == 'single_dose'
    
    @pytest.mark.asyncio
    async def test_calculate_dose_with_limits(self):
        """Test dose calculation with min/max limits."""
        mock_conditions = {
            'croup': {
                'name': 'Croup (Laryngotracheobronchitis)',
                'medications': {
                    'first_line': {
                        'dexamethasone': {
                            'dose_mg_per_kg': 0.15,
                            'max_dose_mg': 2.0,  # Lower max for testing
                            'min_dose_mg': 0.6,
                            'route': 'oral',
                            'frequency': 'single_dose'
                        }
                    }
                }
            }
        }
        
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions):
            result = await calculate_medication_dose('dexamethasone', 'croup', 14.2)
            
            assert result['calculated_dose'] == 2.13
            assert result['final_dose'] == 2.0  # Limited by max_dose


class TestTreatmentPlan:
    """Test treatment plan generation."""
    
    @pytest.mark.asyncio
    async def test_generate_treatment_plan_no_data(self):
        """Test treatment plan generation when no data exists."""
        with patch('mcp_server.server.load_json_data', return_value={}):
            result = await generate_treatment_plan('croup', 'moderate', {})
            assert 'error' in result
            assert 'not available' in result['error']
    
    @pytest.mark.asyncio
    async def test_generate_treatment_plan_with_data(self):
        """Test treatment plan generation with sample data."""
        mock_conditions = {
            'croup': {
                'name': 'Croup (Laryngotracheobronchitis)',
                'red_flags': ['cyanosis', 'drooling'],
                'clinical_pearls': ['viral etiology', 'supportive care']
            }
        }
        
        patient_data = {
            'patient_data': {'age': 3, 'weight': 14.2},
            'symptoms': ['barky cough', 'hoarse voice']
        }
        
        calculated_doses = [{
            'medication': 'dexamethasone',
            'final_dose': 2.13,
            'route': 'oral'
        }]
        
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions):
            result = await generate_treatment_plan('croup', 'moderate', patient_data, calculated_doses)
            
            assert 'condition' in result
            assert 'severity' in result
            assert 'patient_summary' in result
            assert 'medications' in result
            assert 'red_flags' in result
            assert 'clinical_pearls' in result
            assert result['condition'] == 'Croup (Laryngotracheobronchitis)'
            assert result['severity'] == 'moderate'
            assert result['medications'] == calculated_doses


class TestDataLoading:
    """Test JSON data loading functionality."""
    
    def test_load_json_data_success(self):
        """Test successful JSON data loading."""
        mock_data = {'test': 'data'}
        mock_file_content = json.dumps(mock_data)
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            result = load_json_data(Path('test.json'))
            assert result == mock_data
    
    def test_load_json_data_file_not_found(self):
        """Test handling of missing file."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = load_json_data(Path('nonexistent.json'))
            assert result == {}
    
    def test_load_json_data_invalid_json(self):
        """Test handling of invalid JSON."""
        with patch('builtins.open', mock_open(read_data='invalid json')):
            result = load_json_data(Path('invalid.json'))
            assert result == {}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])