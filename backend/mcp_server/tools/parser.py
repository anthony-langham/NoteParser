"""
Clinical note parsing tools for extracting structured data from unstructured text.
"""

import re
import logging
from typing import Dict, List, Optional, Any
from ..schemas.patient import PatientData, VitalSigns, ClinicalNote, ParsedClinicalNote

logger = logging.getLogger(__name__)


class ClinicalNoteParser:
    """Parser for clinical notes with pattern matching and data extraction."""
    
    def __init__(self):
        self.symptom_patterns = [
            r'barky cough',
            r'hoarse voice',
            r'stridor',
            r'fever',
            r'recession',
            r'work of breathing',
            r'wheeze',
            r'cough',
            r'sore throat',
            r'runny nose',
            r'congestion',
            r'difficulty breathing',
            r'shortness of breath',
            r'chest pain',
            r'fatigue',
            r'headache',
            r'nausea',
            r'vomiting',
            r'diarrhea',
            r'abdominal pain'
        ]
    
    def extract_demographics(self, text: str) -> PatientData:
        """Extract patient demographic information."""
        demographics = {}
        
        # Age extraction - multiple patterns
        age_patterns = [
            r'Age:\s*(\d+)\s*years?',
            r'(\d+)\s*years?\s*old',
            r'(\d+)\s*yo',
            r'Age\s*(\d+)'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                demographics['age'] = int(match.group(1))
                break
        
        # Weight extraction
        weight_patterns = [
            r'Weight:\s*(\d+\.?\d*)\s*kg',
            r'(\d+\.?\d*)\s*kg',
            r'Wt:\s*(\d+\.?\d*)\s*kg'
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                demographics['weight'] = float(match.group(1))
                break
        
        # Height extraction
        height_patterns = [
            r'Height:\s*(\d+\.?\d*)\s*cm',
            r'(\d+\.?\d*)\s*cm',
            r'Ht:\s*(\d+\.?\d*)\s*cm'
        ]
        
        for pattern in height_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                demographics['height'] = float(match.group(1))
                break
        
        # DOB extraction
        dob_patterns = [
            r'DOB:\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'Date of birth:\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'Born:\s*(\d{1,2}/\d{1,2}/\d{4})'
        ]
        
        for pattern in dob_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                demographics['dob'] = match.group(1)
                break
        
        # Gender extraction
        gender_patterns = [
            r'Gender:\s*(male|female|M|F)',
            r'Sex:\s*(male|female|M|F)',
            r'\b(male|female|M|F)\b'
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                gender = match.group(1).lower()
                if gender in ['m', 'male']:
                    demographics['gender'] = 'male'
                elif gender in ['f', 'female']:
                    demographics['gender'] = 'female'
                break
        
        return PatientData(**demographics)
    
    def extract_vital_signs(self, text: str) -> VitalSigns:
        """Extract vital signs from clinical text."""
        vitals = {}
        
        # Temperature patterns
        temp_patterns = [
            r'T\s*(\d+\.?\d*)[°C]?',
            r'Temp:\s*(\d+\.?\d*)[°C]?',
            r'Temperature:\s*(\d+\.?\d*)[°C]?',
            r'(\d+\.?\d*)[°C]'
        ]
        
        for pattern in temp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vitals['temperature'] = float(match.group(1))
                break
        
        # Heart rate patterns
        hr_patterns = [
            r'HR\s*(\d+)',
            r'Heart rate:\s*(\d+)',
            r'Pulse:\s*(\d+)',
            r'(\d+)\s*bpm'
        ]
        
        for pattern in hr_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vitals['heart_rate'] = int(match.group(1))
                break
        
        # Respiratory rate patterns
        rr_patterns = [
            r'RR\s*(\d+)',
            r'Respiratory rate:\s*(\d+)',
            r'Resp:\s*(\d+)',
            r'(\d+)\s*breaths/min'
        ]
        
        for pattern in rr_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vitals['respiratory_rate'] = int(match.group(1))
                break
        
        # Blood pressure patterns
        bp_patterns = [
            r'BP\s*(\d+/\d+)',
            r'Blood pressure:\s*(\d+/\d+)',
            r'(\d+/\d+)\s*mmHg'
        ]
        
        for pattern in bp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vitals['blood_pressure'] = match.group(1)
                break
        
        # Oxygen saturation patterns
        spo2_patterns = [
            r'O2\s*sat:\s*(\d+)%?',
            r'SpO2:\s*(\d+)%?',
            r'Oxygen saturation:\s*(\d+)%?',
            r'(\d+)%\s*oxygen'
        ]
        
        for pattern in spo2_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vitals['oxygen_saturation'] = float(match.group(1))
                break
        
        return VitalSigns(**vitals)
    
    def extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms from clinical text."""
        symptoms = []
        
        # Check for each symptom pattern
        for pattern in self.symptom_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Clean up the pattern for display
                symptom = pattern.replace(r'\\b', '').replace(r'\\', '')
                if symptom not in symptoms:
                    symptoms.append(symptom)
        
        return symptoms
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract structured sections from clinical note."""
        sections = {}
        
        # Common section patterns
        section_patterns = {
            'presenting_complaint': [
                r'Presenting complaint:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)',
                r'Chief complaint:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)',
                r'CC:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)'
            ],
            'history': [
                r'History:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)',
                r'HPI:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)',
                r'History of present illness:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)'
            ],
            'examination': [
                r'Examination:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)',
                r'Physical exam:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)',
                r'PE:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)'
            ],
            'assessment': [
                r'Assessment:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)',
                r'Diagnosis:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)',
                r'Impression:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)'
            ],
            'plan': [
                r'Plan:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)',
                r'Treatment:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)',
                r'Management:?\s*(.+?)(?=\n\n|\n[A-Z][a-z]+:|\Z)'
            ]
        }
        
        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    sections[section_name] = match.group(1).strip()
                    break
        
        return sections
    
    def parse(self, clinical_note: str) -> ParsedClinicalNote:
        """Parse clinical note and return structured data."""
        errors = []
        
        try:
            # Extract demographics
            patient_data = self.extract_demographics(clinical_note)
            
            # Extract vital signs
            vitals = self.extract_vital_signs(clinical_note)
            
            # Extract symptoms
            symptoms = self.extract_symptoms(clinical_note)
            
            # Extract sections
            sections = self.extract_sections(clinical_note)
            
            # Create clinical note object
            clinical_note_obj = ClinicalNote(
                patient_data=patient_data,
                symptoms=symptoms,
                vitals=vitals,
                assessment=sections.get('assessment', ''),
                presenting_complaint=sections.get('presenting_complaint'),
                history=sections.get('history'),
                examination=sections.get('examination'),
                plan=sections.get('plan')
            )
            
            return ParsedClinicalNote(
                success=True,
                data=clinical_note_obj,
                errors=errors,
                raw_text=clinical_note
            )
            
        except Exception as e:
            logger.error(f"Error parsing clinical note: {str(e)}")
            errors.append(f"Parsing error: {str(e)}")
            
            return ParsedClinicalNote(
                success=False,
                data=None,
                errors=errors,
                raw_text=clinical_note
            )


# Convenience function for MCP server
async def parse_clinical_note(clinical_note: str) -> Dict[str, Any]:
    """Parse clinical note and return structured data."""
    parser = ClinicalNoteParser()
    result = parser.parse(clinical_note)
    
    if result.success:
        return {
            'patient_data': result.data.patient_data.dict(),
            'symptoms': result.data.symptoms,
            'assessment': result.data.assessment,
            'vitals': result.data.vitals.dict(),
            'presenting_complaint': result.data.presenting_complaint,
            'history': result.data.history,
            'examination': result.data.examination,
            'plan': result.data.plan
        }
    else:
        return {
            'error': 'Failed to parse clinical note',
            'errors': result.errors
        }