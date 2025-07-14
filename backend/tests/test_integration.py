#!/usr/bin/env python3
"""
Integration tests for the complete MCP server workflow.
"""

import pytest
import json
import asyncio
from pathlib import Path
from unittest.mock import patch, mock_open
import sys

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.server import (
    parse_clinical_note,
    identify_condition,
    calculate_medication_dose,
    generate_treatment_plan
)
from mcp_server.utils.error_handler import ErrorCode


class TestMCPServerIntegration:
    """Integration tests for the complete MCP server workflow."""
    
    @pytest.fixture
    def sample_clinical_note(self):
        """Sample clinical note from CLAUDE.md."""
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
    
    @pytest.fixture
    def mock_conditions_data(self):
        """Mock conditions data for integration testing."""
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
    
    @pytest.mark.asyncio
    async def test_complete_workflow_success(self, sample_clinical_note, mock_conditions_data):
        """Test the complete clinical decision support workflow."""
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_data):
            # Step 1: Parse clinical note
            parsed_data = await parse_clinical_note(sample_clinical_note)
            
            assert parsed_data['success'] is True
            assert parsed_data['patient_data']['age'] == 3
            assert parsed_data['patient_data']['weight'] == 14.2
            assert 'barky cough' in parsed_data['symptoms']
            assert 'hoarse voice' in parsed_data['symptoms']
            assert 'stridor' in parsed_data['symptoms']
            
            # Step 2: Identify condition
            condition_result = await identify_condition(
                parsed_data['symptoms'],
                parsed_data['assessment'],
                parsed_data['patient_data']['age']
            )
            
            assert condition_result['success'] is True
            assert len(condition_result['matches']) > 0
            assert condition_result['matches'][0]['condition_id'] == 'croup'
            
            # Step 3: Calculate medication dose
            dose_result = await calculate_medication_dose(
                'dexamethasone', 'croup', parsed_data['patient_data']['weight']
            )
            
            assert dose_result['success'] is True
            assert dose_result['dose_calculation']['medication'] == 'dexamethasone'
            assert dose_result['dose_calculation']['calculated_dose'] == 2.13  # 0.15 * 14.2
            assert dose_result['dose_calculation']['final_dose'] == 2.13
            assert dose_result['dose_calculation']['route'] == 'oral'
            
            # Step 4: Generate treatment plan
            treatment_plan = await generate_treatment_plan(
                'croup',
                'moderate',
                parsed_data,
                [dose_result['dose_calculation']]
            )
            
            assert treatment_plan['success'] is True
            plan = treatment_plan['treatment_plan']
            assert plan['condition'] == 'Croup (Laryngotracheobronchitis)'
            assert plan['severity'] == 'moderate'
            assert 'patient_summary' in plan
            assert len(plan['medications']) > 0
            assert plan['medications'][0]['medication'] == 'dexamethasone'
            assert 'red_flags' in plan
            assert 'clinical_pearls' in plan
    
    @pytest.mark.asyncio
    async def test_workflow_with_missing_data_files(self, sample_clinical_note):
        """Test workflow graceful handling when data files are missing."""
        from mcp_server.utils.error_handler import DataError, ErrorDetails
        
        with patch('mcp_server.server.load_json_data', side_effect=DataError(ErrorDetails(
            code=ErrorCode.DATA_FILE_NOT_FOUND,
            message="Data file not found",
            details={},
            recoverable=False
        ))):
            # Step 1: Parse clinical note (should still work)
            parsed_data = await parse_clinical_note(sample_clinical_note)
            assert parsed_data['success'] is True
            
            # Step 2: Identify condition (should fail gracefully)
            condition_result = await identify_condition(
                parsed_data['symptoms'],
                parsed_data['assessment'],
                parsed_data['patient_data']['age']
            )
            assert condition_result['success'] is False
            assert condition_result['error']['code'] == ErrorCode.DATA_FILE_NOT_FOUND.value
            
            # Step 3: Calculate dose (should fail gracefully)
            dose_result = await calculate_medication_dose('dexamethasone', 'croup', 14.2)
            assert dose_result['success'] is False
            assert dose_result['error']['code'] == ErrorCode.DATA_FILE_NOT_FOUND.value
            
            # Step 4: Generate treatment plan (should fail gracefully)
            treatment_plan = await generate_treatment_plan('croup', 'moderate', parsed_data, [])
            assert treatment_plan['success'] is False
            assert treatment_plan['error']['code'] == ErrorCode.DATA_FILE_NOT_FOUND.value
    
    @pytest.mark.asyncio
    async def test_workflow_with_alternative_clinical_note(self, mock_conditions_data):
        """Test workflow with a different clinical scenario."""
        alternative_note = """
Patient: Emma S.
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
"""
        
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_data):
            # Parse clinical note
            parsed_data = await parse_clinical_note(alternative_note)
            
            assert parsed_data['success'] is True
            assert parsed_data['patient_data']['age'] == 2
            assert parsed_data['patient_data']['weight'] == 12.5
            assert 'barky cough' in parsed_data['symptoms']
            assert 'hoarse voice' in parsed_data['symptoms']
            
            # Identify condition
            condition_result = await identify_condition(
                parsed_data['symptoms'],
                parsed_data['assessment'],
                parsed_data['patient_data']['age']
            )
            
            assert condition_result['success'] is True
            assert condition_result['matches'][0]['condition_id'] == 'croup'
            
            # Calculate dose for lighter patient
            dose_result = await calculate_medication_dose(
                'dexamethasone', 'croup', parsed_data['patient_data']['weight']
            )
            
            assert dose_result['success'] is True
            assert dose_result['dose_calculation']['calculated_dose'] == 1.875  # 0.15 * 12.5
            assert dose_result['dose_calculation']['final_dose'] == 1.875
            
            # Generate treatment plan for mild severity
            treatment_plan = await generate_treatment_plan(
                'croup',
                'mild',
                parsed_data,
                [dose_result['dose_calculation']]
            )
            
            assert treatment_plan['success'] is True
            assert treatment_plan['treatment_plan']['severity'] == 'mild'
    
    @pytest.mark.asyncio
    async def test_workflow_error_propagation(self, sample_clinical_note, mock_conditions_data):
        """Test that errors are properly propagated through the workflow."""
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_data):
            # Parse clinical note
            parsed_data = await parse_clinical_note(sample_clinical_note)
            assert parsed_data['success'] is True
            
            # Test invalid medication name
            dose_result = await calculate_medication_dose(
                'invalid_medication', 'croup', parsed_data['patient_data']['weight']
            )
            
            assert dose_result['success'] is False
            assert dose_result['error']['code'] == ErrorCode.MEDICATION_NOT_FOUND.value
            
            # Test invalid condition
            condition_result = await identify_condition(
                ['invalid_symptom'], 'invalid assessment', 3
            )
            
            # Should still succeed but with no matches
            assert condition_result['success'] is True
            assert len(condition_result['matches']) == 0
            
            # Test treatment plan with invalid condition
            treatment_plan = await generate_treatment_plan(
                'invalid_condition', 'mild', parsed_data, []
            )
            
            assert treatment_plan['success'] is False
            assert treatment_plan['error']['code'] == ErrorCode.CONDITION_NOT_FOUND.value
    
    @pytest.mark.asyncio
    async def test_workflow_with_minimal_clinical_note(self, mock_conditions_data):
        """Test workflow with minimal clinical information."""
        minimal_note = "3-year-old child with barky cough and hoarse voice."
        
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_data):
            # Parse minimal note
            parsed_data = await parse_clinical_note(minimal_note)
            
            assert parsed_data['success'] is True
            assert parsed_data['patient_data']['age'] == 3
            assert 'barky cough' in parsed_data['symptoms']
            assert 'hoarse voice' in parsed_data['symptoms']
            
            # Should still be able to identify condition
            condition_result = await identify_condition(
                parsed_data['symptoms'],
                parsed_data['assessment'],
                parsed_data['patient_data']['age']
            )
            
            assert condition_result['success'] is True
            assert len(condition_result['matches']) > 0
            assert condition_result['matches'][0]['condition_id'] == 'croup'
    
    @pytest.mark.asyncio
    async def test_workflow_performance(self, sample_clinical_note, mock_conditions_data):
        """Test that the workflow completes in reasonable time."""
        import time
        
        with patch('mcp_server.server.load_json_data', return_value=mock_conditions_data):
            start_time = time.time()
            
            # Run complete workflow
            parsed_data = await parse_clinical_note(sample_clinical_note)
            condition_result = await identify_condition(
                parsed_data['symptoms'],
                parsed_data['assessment'],
                parsed_data['patient_data']['age']
            )
            dose_result = await calculate_medication_dose(
                'dexamethasone', 'croup', parsed_data['patient_data']['weight']
            )
            treatment_plan = await generate_treatment_plan(
                'croup', 'moderate', parsed_data, [dose_result['dose_calculation']]
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Workflow should complete in under 1 second
            assert execution_time < 1.0
            
            # All steps should succeed
            assert parsed_data['success'] is True
            assert condition_result['success'] is True
            assert dose_result['success'] is True
            assert treatment_plan['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])