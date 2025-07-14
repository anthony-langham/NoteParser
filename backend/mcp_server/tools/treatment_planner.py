"""
Enhanced treatment plan generator using clinical guidelines.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from ..schemas.patient import ClinicalNote

logger = logging.getLogger(__name__)


class TreatmentPlanGenerator:
    """Generates comprehensive treatment plans based on clinical guidelines."""
    
    def __init__(self, conditions_file: str = None, guidelines_file: str = None):
        """Initialize with data files."""
        if conditions_file is None:
            base_path = Path(__file__).parent.parent / "data"
            conditions_file = base_path / "conditions.json"
        if guidelines_file is None:
            base_path = Path(__file__).parent.parent / "data"
            guidelines_file = base_path / "guidelines.json"
        
        self.conditions_file = conditions_file
        self.guidelines_file = guidelines_file
        self.conditions = self._load_json_data(conditions_file)
        self.guidelines = self._load_json_data(guidelines_file)
    
    def _load_json_data(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON data from file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Data file not found: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file: {e}")
            return {}
    
    def get_guideline_for_condition(self, condition_id: str) -> Optional[Dict[str, Any]]:
        """Find guideline that covers the given condition."""
        for guideline_id, guideline_data in self.guidelines.items():
            if condition_id in guideline_data.get('conditions', []):
                return guideline_data
        return None
    
    def generate_immediate_actions(self, condition_id: str, severity: str) -> List[str]:
        """Generate immediate actions based on condition and severity."""
        guideline = self.get_guideline_for_condition(condition_id)
        if not guideline:
            return ["Supportive care", "Monitor symptoms", "Ensure adequate hydration"]
        
        treatment_algorithm = guideline.get('decision_tree', {}).get('treatment_algorithm', {})
        severity_actions = treatment_algorithm.get(severity, {}).get('immediate_actions', [])
        
        return severity_actions if severity_actions else ["Supportive care", "Monitor symptoms"]
    
    def generate_monitoring_plan(self, condition_id: str, severity: str) -> Dict[str, Any]:
        """Generate monitoring plan based on guidelines."""
        guideline = self.get_guideline_for_condition(condition_id)
        if not guideline:
            return {
                "frequency": "regular",
                "parameters": ["vital signs", "symptom progression"],
                "duration": "until improvement"
            }
        
        treatment_algorithm = guideline.get('decision_tree', {}).get('treatment_algorithm', {})
        monitoring_info = treatment_algorithm.get(severity, {}).get('monitoring', {})
        
        if isinstance(monitoring_info, dict):
            return {
                "frequency": monitoring_info.get('frequency', 'regular'),
                "parameters": monitoring_info.get('parameters', ['vital signs']),
                "duration": monitoring_info.get('duration', 'until improvement'),
                "location": monitoring_info.get('location', 'standard care area')
            }
        else:
            return {
                "frequency": "regular",
                "parameters": ["vital signs", "symptom progression"],
                "duration": "until improvement"
            }
    
    def generate_follow_up_plan(self, condition_id: str, severity: str) -> Dict[str, Any]:
        """Generate follow-up plan based on guidelines."""
        guideline = self.get_guideline_for_condition(condition_id)
        if not guideline:
            return {
                "timeline": "routine",
                "instructions": ["Follow up with primary care provider"]
            }
        
        follow_up_info = guideline.get('follow_up', {})
        treatment_algorithm = guideline.get('decision_tree', {}).get('treatment_algorithm', {})
        
        # Get severity-specific follow-up
        severity_follow_up = treatment_algorithm.get(severity, {}).get('follow_up', 'routine')
        
        follow_up_plan = {
            "timeline": severity_follow_up,
            "instructions": [],
            "parent_education": follow_up_info.get('parent_education', [])
        }
        
        # Add specific follow-up instructions based on severity
        if severity == 'mild':
            follow_up_plan["instructions"] = [follow_up_info.get('mild_cases', 'routine follow-up')]
        elif severity == 'moderate':
            follow_up_plan["instructions"] = [follow_up_info.get('moderate_cases', 'review in 24-48 hours')]
        elif severity == 'severe':
            follow_up_plan["instructions"] = [follow_up_info.get('severe_cases', 'inpatient monitoring')]
        
        return follow_up_plan
    
    def generate_discharge_criteria(self, condition_id: str, severity: str) -> List[str]:
        """Generate discharge criteria based on guidelines."""
        guideline = self.get_guideline_for_condition(condition_id)
        if not guideline:
            return ["Stable vital signs", "Improved symptoms", "Adequate oral intake"]
        
        treatment_algorithm = guideline.get('decision_tree', {}).get('treatment_algorithm', {})
        discharge_criteria = treatment_algorithm.get(severity, {}).get('discharge_criteria', [])
        
        if isinstance(discharge_criteria, list):
            return discharge_criteria
        else:
            return ["Stable vital signs", "Improved symptoms"]
    
    def generate_safety_netting(self, condition_id: str, severity: str) -> Dict[str, Any]:
        """Generate safety netting advice."""
        guideline = self.get_guideline_for_condition(condition_id)
        if not guideline:
            return {
                "advice": "Return if symptoms worsen",
                "warning_signs": ["Increased difficulty breathing", "High fever", "Poor feeding"]
            }
        
        treatment_algorithm = guideline.get('decision_tree', {}).get('treatment_algorithm', {})
        safety_netting = treatment_algorithm.get(severity, {}).get('safety_netting', 'return if worsening')
        
        monitoring_info = guideline.get('monitoring', {})
        deterioration_signs = monitoring_info.get('deterioration_signs', [])
        
        return {
            "advice": safety_netting,
            "warning_signs": deterioration_signs
        }
    
    def generate_comprehensive_plan(
        self, 
        condition_id: str, 
        severity: str, 
        patient_data: Dict[str, Any], 
        calculated_doses: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive treatment plan."""
        
        # Get condition data
        condition_data = self.conditions.get(condition_id)
        if not condition_data:
            return {"error": f"Condition '{condition_id}' not found"}
        
        # Generate plan components
        immediate_actions = self.generate_immediate_actions(condition_id, severity)
        monitoring_plan = self.generate_monitoring_plan(condition_id, severity)
        follow_up_plan = self.generate_follow_up_plan(condition_id, severity)
        discharge_criteria = self.generate_discharge_criteria(condition_id, severity)
        safety_netting = self.generate_safety_netting(condition_id, severity)
        
        # Build comprehensive plan
        plan = {
            "condition": condition_data.get('name', condition_id),
            "condition_id": condition_id,
            "severity": severity,
            "patient_summary": {
                "age": patient_data.get('patient_data', {}).get('age'),
                "weight": patient_data.get('patient_data', {}).get('weight'),
                "symptoms": patient_data.get('symptoms', [])
            },
            "immediate_actions": immediate_actions,
            "medications": calculated_doses or [],
            "monitoring": monitoring_plan,
            "discharge_criteria": discharge_criteria,
            "follow_up": follow_up_plan,
            "safety_netting": safety_netting,
            "red_flags": condition_data.get('red_flags', []),
            "clinical_pearls": condition_data.get('clinical_pearls', []),
            "differential_diagnosis": condition_data.get('differential_diagnosis', [])
        }
        
        # Add guideline information
        guideline = self.get_guideline_for_condition(condition_id)
        if guideline:
            plan["guideline_info"] = {
                "name": guideline.get('name'),
                "version": guideline.get('version'),
                "source": guideline.get('source'),
                "last_updated": guideline.get('last_updated')
            }
        
        return plan


# Convenience function for MCP server
async def generate_comprehensive_treatment_plan(
    condition_id: str, 
    severity: str, 
    patient_data: Dict[str, Any], 
    calculated_doses: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate comprehensive treatment plan."""
    try:
        planner = TreatmentPlanGenerator()
        plan = planner.generate_comprehensive_plan(condition_id, severity, patient_data, calculated_doses)
        
        return {
            "success": True,
            "treatment_plan": plan
        }
        
    except Exception as e:
        logger.error(f"Error generating treatment plan: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }