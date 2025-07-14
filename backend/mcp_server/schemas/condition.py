from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class SeverityLevel(str, Enum):
    """Condition severity levels."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class AgeGroup(str, Enum):
    """Age group classifications."""
    PEDIATRIC = "pediatric"
    ADULT = "adult"
    GERIATRIC = "geriatric"


class Symptoms(BaseModel):
    """Symptom classification."""
    primary: List[str] = Field(default_factory=list, description="Primary symptoms")
    secondary: List[str] = Field(default_factory=list, description="Secondary symptoms")
    
    class Config:
        schema_extra = {
            "example": {
                "primary": ["barky cough", "hoarse voice", "stridor"],
                "secondary": ["fever", "runny nose", "fatigue"]
            }
        }


class SeverityScale(BaseModel):
    """Severity assessment criteria."""
    criteria: List[str] = Field(description="Criteria for this severity level")
    score_range: Optional[Dict[str, int]] = Field(None, description="Score range if applicable")
    
    class Config:
        schema_extra = {
            "example": {
                "criteria": ["barky cough", "no stridor at rest", "normal oxygen saturation"],
                "score_range": {"min": 0, "max": 3}
            }
        }


class MedicationDosing(BaseModel):
    """Medication dosing information."""
    dose_mg_per_kg: float = Field(description="Dose in mg per kg body weight")
    max_dose_mg: Optional[float] = Field(None, description="Maximum dose in mg")
    min_dose_mg: Optional[float] = Field(None, description="Minimum dose in mg")
    route: str = Field(description="Route of administration")
    frequency: str = Field(description="Dosing frequency")
    duration: Optional[str] = Field(None, description="Treatment duration")
    age_restrictions: Optional[str] = Field(None, description="Age-based restrictions")
    contraindications: List[str] = Field(default_factory=list, description="Contraindications")
    
    @validator('dose_mg_per_kg')
    def validate_dose(cls, v):
        if v <= 0:
            raise ValueError('Dose must be positive')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "dose_mg_per_kg": 0.15,
                "max_dose_mg": 10.0,
                "min_dose_mg": 0.6,
                "route": "oral",
                "frequency": "single_dose",
                "duration": "1 day",
                "contraindications": ["active infection", "immunocompromised"]
            }
        }


class MedicationLine(BaseModel):
    """Medication treatment line (first-line, second-line, etc.)."""
    medications: Dict[str, MedicationDosing] = Field(
        default_factory=dict,
        description="Medications in this treatment line"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "medications": {
                    "dexamethasone": {
                        "dose_mg_per_kg": 0.15,
                        "max_dose_mg": 10.0,
                        "route": "oral",
                        "frequency": "single_dose"
                    }
                }
            }
        }


class TreatmentMedications(BaseModel):
    """Complete medication treatment options."""
    first_line: Optional[Dict[str, MedicationDosing]] = Field(None, description="First-line medications")
    second_line: Optional[Dict[str, MedicationDosing]] = Field(None, description="Second-line medications")
    rescue: Optional[Dict[str, MedicationDosing]] = Field(None, description="Rescue medications")
    
    class Config:
        schema_extra = {
            "example": {
                "first_line": {
                    "dexamethasone": {
                        "dose_mg_per_kg": 0.15,
                        "max_dose_mg": 10.0,
                        "route": "oral",
                        "frequency": "single_dose"
                    }
                },
                "second_line": {
                    "prednisolone": {
                        "dose_mg_per_kg": 1.0,
                        "max_dose_mg": 40.0,
                        "route": "oral",
                        "frequency": "daily"
                    }
                }
            }
        }


class Condition(BaseModel):
    """Medical condition data structure."""
    name: str = Field(description="Human-readable condition name")
    description: str = Field(description="Clinical description")
    icd_codes: List[str] = Field(default_factory=list, description="ICD-10 codes")
    age_groups: List[AgeGroup] = Field(default_factory=list, description="Applicable age groups")
    symptoms: Symptoms = Field(default_factory=Symptoms, description="Symptom classification")
    severity_scales: Dict[SeverityLevel, SeverityScale] = Field(
        default_factory=dict,
        description="Severity assessment scales"
    )
    medications: TreatmentMedications = Field(
        default_factory=TreatmentMedications,
        description="Treatment medications"
    )
    clinical_pearls: List[str] = Field(default_factory=list, description="Clinical pearls")
    red_flags: List[str] = Field(default_factory=list, description="Red flag symptoms")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Croup (Laryngotracheobronchitis)",
                "description": "Viral infection of the upper respiratory tract",
                "icd_codes": ["J05.0"],
                "age_groups": ["pediatric"],
                "symptoms": {
                    "primary": ["barky cough", "hoarse voice", "stridor"],
                    "secondary": ["fever", "runny nose"]
                },
                "severity_scales": {
                    "mild": {"criteria": ["barky cough", "no stridor at rest"]},
                    "moderate": {"criteria": ["barky cough", "stridor at rest", "mild recession"]},
                    "severe": {"criteria": ["stridor at rest", "significant recession", "cyanosis"]}
                },
                "medications": {
                    "first_line": {
                        "dexamethasone": {
                            "dose_mg_per_kg": 0.15,
                            "max_dose_mg": 10.0,
                            "route": "oral",
                            "frequency": "single_dose"
                        }
                    }
                },
                "clinical_pearls": ["Viral etiology in most cases", "Supportive care important"],
                "red_flags": ["Cyanosis", "Drooling", "Toxic appearance"]
            }
        }


class ConditionMatch(BaseModel):
    """Result of condition identification."""
    condition_id: str = Field(description="Condition identifier")
    condition_name: str = Field(description="Human-readable condition name")
    confidence_score: float = Field(description="Confidence score (0-1)")
    matched_symptoms: List[str] = Field(default_factory=list, description="Symptoms that matched")
    severity_assessment: Optional[SeverityLevel] = Field(None, description="Assessed severity")
    
    @validator('confidence_score')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence score must be between 0 and 1')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "condition_id": "croup",
                "condition_name": "Croup (Laryngotracheobronchitis)",
                "confidence_score": 0.85,
                "matched_symptoms": ["barky cough", "hoarse voice", "stridor"],
                "severity_assessment": "moderate"
            }
        }


class ConditionIdentificationResult(BaseModel):
    """Result of condition identification process."""
    matches: List[ConditionMatch] = Field(default_factory=list, description="All condition matches")
    top_match: Optional[ConditionMatch] = Field(None, description="Best condition match")
    differential_diagnosis: List[str] = Field(default_factory=list, description="Differential diagnoses")
    
    class Config:
        schema_extra = {
            "example": {
                "matches": [
                    {
                        "condition_id": "croup",
                        "condition_name": "Croup (Laryngotracheobronchitis)",
                        "confidence_score": 0.85,
                        "matched_symptoms": ["barky cough", "hoarse voice", "stridor"]
                    }
                ],
                "top_match": {
                    "condition_id": "croup",
                    "condition_name": "Croup (Laryngotracheobronchitis)",
                    "confidence_score": 0.85
                },
                "differential_diagnosis": ["Epiglottitis", "Bacterial tracheitis"]
            }
        }