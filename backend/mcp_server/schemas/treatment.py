from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class RouteOfAdministration(str, Enum):
    """Routes of medication administration."""
    ORAL = "oral"
    INTRAVENOUS = "intravenous"
    INTRAMUSCULAR = "intramuscular"
    SUBCUTANEOUS = "subcutaneous"
    TOPICAL = "topical"
    INHALATION = "inhalation"
    NEBULIZATION = "nebulization"


class DosageFrequency(str, Enum):
    """Dosing frequency options."""
    SINGLE_DOSE = "single_dose"
    DAILY = "daily"
    BID = "bid"  # twice daily
    TID = "tid"  # three times daily
    QID = "qid"  # four times daily
    PRN = "prn"  # as needed


class DoseCalculation(BaseModel):
    """Calculated medication dose."""
    medication: str = Field(description="Medication name")
    condition: str = Field(description="Medical condition")
    patient_weight: float = Field(description="Patient weight in kg")
    dose_per_kg: float = Field(description="Dose per kg body weight")
    calculated_dose: float = Field(description="Calculated dose before limits")
    final_dose: float = Field(description="Final dose after applying limits")
    unit: str = Field(description="Dose unit (mg, mcg, etc.)")
    route: RouteOfAdministration = Field(description="Route of administration")
    frequency: DosageFrequency = Field(description="Dosing frequency")
    duration: Optional[str] = Field(None, description="Treatment duration")
    max_dose: Optional[float] = Field(None, description="Maximum allowed dose")
    min_dose: Optional[float] = Field(None, description="Minimum allowed dose")
    dosing_rationale: str = Field(description="Explanation of dose calculation")
    
    @validator('patient_weight')
    def validate_weight(cls, v):
        if v <= 0:
            raise ValueError('Patient weight must be positive')
        return v
    
    @validator('final_dose')
    def validate_final_dose(cls, v):
        if v <= 0:
            raise ValueError('Final dose must be positive')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "medication": "dexamethasone",
                "condition": "croup",
                "patient_weight": 14.2,
                "dose_per_kg": 0.15,
                "calculated_dose": 2.13,
                "final_dose": 2.13,
                "unit": "mg",
                "route": "oral",
                "frequency": "single_dose",
                "duration": "1 day",
                "max_dose": 10.0,
                "dosing_rationale": "Calculated at 0.15 mg/kg for 14.2kg patient"
            }
        }


class MonitoringParameter(BaseModel):
    """Patient monitoring parameter."""
    parameter: str = Field(description="Parameter to monitor")
    frequency: str = Field(description="Monitoring frequency")
    target_range: Optional[str] = Field(None, description="Target range or value")
    action_if_abnormal: Optional[str] = Field(None, description="Action if parameter is abnormal")
    
    class Config:
        schema_extra = {
            "example": {
                "parameter": "Oxygen saturation",
                "frequency": "Continuous",
                "target_range": ">95%",
                "action_if_abnormal": "Provide supplemental oxygen"
            }
        }


class FollowUpInstruction(BaseModel):
    """Follow-up instruction."""
    timeframe: str = Field(description="When to follow up")
    instruction: str = Field(description="Follow-up instruction")
    urgency: str = Field(description="Urgency level")
    provider: Optional[str] = Field(None, description="Which provider to follow up with")
    
    class Config:
        schema_extra = {
            "example": {
                "timeframe": "24-48 hours",
                "instruction": "Return if symptoms worsen or fever persists",
                "urgency": "routine",
                "provider": "primary care physician"
            }
        }


class TreatmentPlan(BaseModel):
    """Comprehensive treatment plan."""
    condition: str = Field(description="Primary condition")
    severity: str = Field(description="Condition severity")
    patient_summary: Dict[str, Any] = Field(description="Patient summary data")
    medications: List[DoseCalculation] = Field(default_factory=list, description="Prescribed medications")
    monitoring: List[MonitoringParameter] = Field(default_factory=list, description="Monitoring parameters")
    follow_up: List[FollowUpInstruction] = Field(default_factory=list, description="Follow-up instructions")
    red_flags: List[str] = Field(default_factory=list, description="Red flag symptoms")
    clinical_pearls: List[str] = Field(default_factory=list, description="Clinical pearls")
    non_pharmacological: List[str] = Field(default_factory=list, description="Non-drug interventions")
    discharge_criteria: List[str] = Field(default_factory=list, description="Discharge criteria")
    escalation_criteria: List[str] = Field(default_factory=list, description="When to escalate care")
    
    class Config:
        schema_extra = {
            "example": {
                "condition": "Croup (Laryngotracheobronchitis)",
                "severity": "moderate",
                "patient_summary": {
                    "age": 3,
                    "weight": 14.2,
                    "symptoms": ["barky cough", "hoarse voice", "stridor"]
                },
                "medications": [
                    {
                        "medication": "dexamethasone",
                        "final_dose": 2.13,
                        "unit": "mg",
                        "route": "oral",
                        "frequency": "single_dose"
                    }
                ],
                "monitoring": [
                    {
                        "parameter": "Respiratory status",
                        "frequency": "Every 15 minutes x 4",
                        "target_range": "No stridor at rest"
                    }
                ],
                "follow_up": [
                    {
                        "timeframe": "24-48 hours",
                        "instruction": "Return if symptoms worsen",
                        "urgency": "routine"
                    }
                ],
                "red_flags": ["Cyanosis", "Drooling", "Toxic appearance"],
                "clinical_pearls": ["Viral etiology in most cases", "Supportive care important"],
                "non_pharmacological": ["Humidified air", "Calm environment"],
                "discharge_criteria": ["Stable breathing", "No stridor at rest"],
                "escalation_criteria": ["Persistent stridor", "Oxygen saturation <92%"]
            }
        }


class SafetyAlert(BaseModel):
    """Safety alert or contraindication."""
    alert_type: str = Field(description="Type of safety alert")
    severity: str = Field(description="Alert severity level")
    message: str = Field(description="Alert message")
    recommendation: str = Field(description="Recommended action")
    
    class Config:
        schema_extra = {
            "example": {
                "alert_type": "contraindication",
                "severity": "high",
                "message": "Patient has known allergy to dexamethasone",
                "recommendation": "Consider alternative corticosteroid"
            }
        }


class TreatmentResponse(BaseModel):
    """Complete treatment response with safety checks."""
    success: bool = Field(description="Whether treatment plan generation succeeded")
    treatment_plan: Optional[TreatmentPlan] = Field(None, description="Generated treatment plan")
    safety_alerts: List[SafetyAlert] = Field(default_factory=list, description="Safety alerts")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "treatment_plan": {
                    "condition": "Croup (Laryngotracheobronchitis)",
                    "severity": "moderate",
                    "medications": [
                        {
                            "medication": "dexamethasone",
                            "final_dose": 2.13,
                            "unit": "mg",
                            "route": "oral"
                        }
                    ]
                },
                "safety_alerts": [],
                "errors": [],
                "warnings": []
            }
        }