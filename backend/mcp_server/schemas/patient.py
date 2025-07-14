from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class VitalSigns(BaseModel):
    """Vital signs data structure."""
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    heart_rate: Optional[int] = Field(None, description="Heart rate in BPM")
    respiratory_rate: Optional[int] = Field(None, description="Respiratory rate per minute")
    blood_pressure: Optional[str] = Field(None, description="Blood pressure (systolic/diastolic)")
    oxygen_saturation: Optional[float] = Field(None, description="Oxygen saturation percentage")


class PatientData(BaseModel):
    """Patient demographic and clinical data."""
    age: Optional[int] = Field(None, description="Patient age in years")
    weight: Optional[float] = Field(None, description="Patient weight in kg")
    height: Optional[float] = Field(None, description="Patient height in cm")
    dob: Optional[str] = Field(None, description="Date of birth (DD/MM/YYYY)")
    gender: Optional[str] = Field(None, description="Patient gender")
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError('Age must be between 0 and 150 years')
        return v
    
    @validator('weight')
    def validate_weight(cls, v):
        if v is not None and (v < 0.5 or v > 500):
            raise ValueError('Weight must be between 0.5 and 500 kg')
        return v


class ClinicalNote(BaseModel):
    """Structured clinical note data."""
    patient_data: PatientData
    symptoms: List[str] = Field(default_factory=list, description="List of symptoms")
    assessment: str = Field("", description="Clinical assessment text")
    vitals: VitalSigns = Field(default_factory=VitalSigns, description="Vital signs")
    presenting_complaint: Optional[str] = Field(None, description="Presenting complaint")
    history: Optional[str] = Field(None, description="Medical history")
    examination: Optional[str] = Field(None, description="Physical examination findings")
    plan: Optional[str] = Field(None, description="Treatment plan")
    
    class Config:
        schema_extra = {
            "example": {
                "patient_data": {
                    "age": 3,
                    "weight": 14.2,
                    "dob": "12/03/2022"
                },
                "symptoms": ["barky cough", "hoarse voice", "stridor"],
                "assessment": "Moderate croup (laryngotracheobronchitis)",
                "vitals": {
                    "temperature": 38.2,
                    "heart_rate": 110
                },
                "presenting_complaint": "2-day history of barky cough and fever",
                "examination": "Stridor at rest, mild intercostal recession"
            }
        }


class ParsedClinicalNote(BaseModel):
    """Result of clinical note parsing."""
    success: bool = Field(description="Whether parsing was successful")
    data: Optional[ClinicalNote] = Field(None, description="Parsed clinical data")
    errors: List[str] = Field(default_factory=list, description="Parsing errors")
    raw_text: str = Field(description="Original clinical note text")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "patient_data": {"age": 3, "weight": 14.2},
                    "symptoms": ["barky cough", "hoarse voice"],
                    "assessment": "Moderate croup"
                },
                "errors": [],
                "raw_text": "Patient: Jack T. Age: 3 years..."
            }
        }