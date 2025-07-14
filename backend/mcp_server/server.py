#!/usr/bin/env python3

import asyncio
import json
import logging
from typing import Dict, Any, List
from mcp.server import Server
from mcp.types import Tool, TextContent
from pathlib import Path
from .utils.error_handler import (
    ErrorHandler, handle_errors, global_error_handler,
    check_data_availability, check_condition_exists, check_medication_exists,
    validate_patient_data, validate_medication_dose,
    DataError, ValidationError, BusinessLogicError, ProcessingError,
    ErrorCode, ErrorDetails
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("heidi-clinical-decision-support")

# Data file paths
DATA_DIR = Path(__file__).parent / "data"
CONDITIONS_FILE = DATA_DIR / "conditions.json"
GUIDELINES_FILE = DATA_DIR / "guidelines.json"


def load_json_data(file_path: Path) -> Dict[str, Any]:
    """Load JSON data from file with enhanced error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise DataError(ErrorDetails(
                    code=ErrorCode.DATA_FILE_CORRUPTED,
                    message=f"Data file {file_path} does not contain valid JSON object",
                    details={"file_path": str(file_path), "data_type": type(data).__name__},
                    recoverable=False
                ))
            return data
    except FileNotFoundError:
        raise DataError(ErrorDetails(
            code=ErrorCode.DATA_FILE_NOT_FOUND,
            message=f"Data file not found: {file_path}",
            details={"file_path": str(file_path)},
            recoverable=False
        ))
    except json.JSONDecodeError as e:
        raise DataError(ErrorDetails(
            code=ErrorCode.DATA_FILE_INVALID_JSON,
            message=f"Invalid JSON in {file_path}: {e}",
            details={"file_path": str(file_path), "json_error": str(e)},
            recoverable=False
        ))
    except Exception as e:
        raise DataError(ErrorDetails(
            code=ErrorCode.DATA_FILE_CORRUPTED,
            message=f"Unexpected error loading {file_path}: {e}",
            details={"file_path": str(file_path), "error": str(e)},
            recoverable=False
        ))


async def parse_clinical_note(clinical_note: str) -> Dict[str, Any]:
    """Parse clinical note and extract structured patient data."""
    from .tools.parser import parse_clinical_note as comprehensive_parse
    return await comprehensive_parse(clinical_note)


@handle_errors(global_error_handler)
async def identify_condition(symptoms: List[str], assessment: str, patient_age: int = None) -> Dict[str, Any]:
    """Identify medical condition from symptoms and assessment."""
    # Input validation
    if not symptoms and not assessment:
        raise ValidationError(ErrorDetails(
            code=ErrorCode.INSUFFICIENT_PATIENT_DATA,
            message="Either symptoms or assessment must be provided",
            details={"symptoms": symptoms, "assessment": assessment}
        ))
    
    if patient_age is not None and (patient_age < 0 or patient_age > 150):
        raise ValidationError(ErrorDetails(
            code=ErrorCode.INVALID_PATIENT_DATA,
            message="Patient age must be between 0 and 150 years",
            details={"provided_age": patient_age}
        ))
    
    # Load conditions data
    conditions = load_json_data(CONDITIONS_FILE)
    check_data_availability(conditions, "conditions")
    
    # Simple condition matching based on symptoms and assessment
    matches = []
    
    for condition_id, condition_data in conditions.items():
        score = 0
        
        # Check symptoms match
        primary_symptoms = condition_data.get('symptoms', {}).get('primary', [])
        matched_symptoms = []
        
        for symptom in symptoms:
            if any(symptom.lower() in primary_symptom.lower() for primary_symptom in primary_symptoms):
                score += 2
                matched_symptoms.append(symptom)
        
        # Check assessment match
        if assessment and condition_data.get('name', '').lower() in assessment.lower():
            score += 3
        
        # Age group check
        if patient_age is not None and 'age_groups' in condition_data:
            age_groups = condition_data['age_groups']
            if 'pediatric' in age_groups and patient_age < 18:
                score += 1
            elif 'adult' in age_groups and patient_age >= 18:
                score += 1
        
        if score > 0:
            matches.append({
                'condition_id': condition_id,
                'condition_name': condition_data.get('name', condition_id),
                'confidence_score': score,
                'matched_symptoms': matched_symptoms
            })
    
    # Sort by confidence score
    matches.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    return {
        'success': True,
        'matches': matches,
        'top_match': matches[0] if matches else None,
        'total_conditions_evaluated': len(conditions)
    }


@handle_errors(global_error_handler)
async def calculate_medication_dose(
    medication: str, 
    condition: str, 
    patient_weight: float, 
    severity: str = "moderate"
) -> Dict[str, Any]:
    """Calculate weight-based medication dose."""
    # Input validation
    if not medication or not condition:
        raise ValidationError(ErrorDetails(
            code=ErrorCode.INSUFFICIENT_PATIENT_DATA,
            message="Medication and condition must be provided",
            details={"medication": medication, "condition": condition}
        ))
    
    if patient_weight <= 0 or patient_weight > 500:
        raise ValidationError(ErrorDetails(
            code=ErrorCode.INVALID_PATIENT_DATA,
            message="Patient weight must be between 0.5 and 500 kg",
            details={"provided_weight": patient_weight}
        ))
    
    # Load conditions data
    conditions = load_json_data(CONDITIONS_FILE)
    check_data_availability(conditions, "conditions")
    
    # Find condition
    condition_data = None
    condition_id = None
    for cond_id, cond_data in conditions.items():
        if cond_id == condition or cond_data.get('name', '').lower() == condition.lower():
            condition_data = cond_data
            condition_id = cond_id
            break
    
    if not condition_data:
        check_condition_exists(condition, conditions)
    
    # Find medication in condition
    medications = condition_data.get('medications', {})
    check_medication_exists(medication, condition_id, medications)
    
    medication_data = None
    for med_line in ['first_line', 'second_line']:
        if med_line in medications and medication in medications[med_line]:
            medication_data = medications[med_line][medication]
            break
    
    # Calculate dose
    dose_per_kg = medication_data.get('dose_mg_per_kg', 0)
    if dose_per_kg <= 0:
        raise ValidationError(ErrorDetails(
            code=ErrorCode.INVALID_DOSE_CALCULATION,
            message=f"Invalid dose per kg for {medication}: {dose_per_kg}",
            details={"medication": medication, "dose_per_kg": dose_per_kg}
        ))
    
    calculated_dose = dose_per_kg * patient_weight
    
    # Apply limits
    max_dose = medication_data.get('max_dose_mg', float('inf'))
    min_dose = medication_data.get('min_dose_mg', 0)
    
    final_dose = min(max(calculated_dose, min_dose), max_dose)
    
    # Validate final dose is reasonable
    if final_dose != calculated_dose:
        logger.warning(f"Dose adjusted from {calculated_dose}mg to {final_dose}mg for {medication}")
    
    return {
        "success": True,
        "medication": medication,
        "condition": condition,
        "patient_weight": patient_weight,
        "dose_per_kg": dose_per_kg,
        "calculated_dose": calculated_dose,
        "final_dose": final_dose,
        "unit": "mg",
        "route": medication_data.get('route', 'oral'),
        "frequency": medication_data.get('frequency', 'daily'),
        "duration": medication_data.get('duration', ''),
        "max_dose": max_dose,
        "min_dose": min_dose,
        "dosing_rationale": f"Calculated at {dose_per_kg} mg/kg for {patient_weight}kg patient",
        "contraindications": medication_data.get('contraindications', []),
        "clinical_notes": medication_data.get('clinical_notes', '')
    }


@handle_errors(global_error_handler)
async def generate_treatment_plan(
    condition: str, 
    severity: str, 
    patient_data: Dict[str, Any], 
    calculated_doses: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate comprehensive treatment plan using enhanced planner."""
    # Input validation
    if not condition or not severity:
        raise ValidationError(ErrorDetails(
            code=ErrorCode.INSUFFICIENT_PATIENT_DATA,
            message="Condition and severity must be provided",
            details={"condition": condition, "severity": severity}
        ))
    
    if severity not in ['mild', 'moderate', 'severe']:
        raise ValidationError(ErrorDetails(
            code=ErrorCode.INVALID_PATIENT_DATA,
            message="Severity must be 'mild', 'moderate', or 'severe'",
            details={"provided_severity": severity}
        ))
    
    if not patient_data:
        raise ValidationError(ErrorDetails(
            code=ErrorCode.INSUFFICIENT_PATIENT_DATA,
            message="Patient data is required for treatment plan generation",
            details={"patient_data": patient_data}
        ))
    
    from .tools.treatment_planner import generate_comprehensive_treatment_plan
    
    # Convert condition name to condition_id if needed
    conditions = load_json_data(CONDITIONS_FILE)
    check_data_availability(conditions, "conditions")
    
    condition_id = condition
    
    # Find condition ID from name if needed
    if condition_id not in conditions:
        for cond_id, cond_data in conditions.items():
            if cond_data.get('name', '').lower() == condition.lower():
                condition_id = cond_id
                break
    
    # Ensure condition exists
    check_condition_exists(condition_id, conditions)
    
    result = await generate_comprehensive_treatment_plan(condition_id, severity, patient_data, calculated_doses)
    
    if result.get('success'):
        return result['treatment_plan']
    else:
        raise ProcessingError(ErrorDetails(
            code=ErrorCode.TREATMENT_PLAN_ERROR,
            message=result.get('error', 'Failed to generate treatment plan'),
            details={"condition": condition, "severity": severity}
        ))


@app.list_tools()
async def list_tools():
    """List all available MCP tools."""
    return [
        Tool(
            name="parse_clinical_note",
            description="Parse clinical note and extract structured patient data",
            inputSchema={
                "type": "object",
                "properties": {
                    "clinical_note": {"type": "string", "description": "Raw clinical note text"}
                },
                "required": ["clinical_note"]
            }
        ),
        Tool(
            name="identify_condition",
            description="Identify medical condition from symptoms and assessment",
            inputSchema={
                "type": "object",
                "properties": {
                    "symptoms": {"type": "array", "items": {"type": "string"}, "description": "List of symptoms"},
                    "assessment": {"type": "string", "description": "Clinical assessment text"},
                    "patient_age": {"type": "number", "description": "Patient age in years"}
                },
                "required": ["symptoms", "assessment"]
            }
        ),
        Tool(
            name="calculate_medication_dose",
            description="Calculate weight-based medication dose",
            inputSchema={
                "type": "object",
                "properties": {
                    "medication": {"type": "string", "description": "Medication name"},
                    "condition": {"type": "string", "description": "Medical condition"},
                    "patient_weight": {"type": "number", "description": "Patient weight in kg"},
                    "severity": {"type": "string", "description": "Condition severity level"}
                },
                "required": ["medication", "condition", "patient_weight"]
            }
        ),
        Tool(
            name="generate_treatment_plan",
            description="Generate comprehensive treatment plan",
            inputSchema={
                "type": "object",
                "properties": {
                    "condition": {"type": "string", "description": "Medical condition"},
                    "severity": {"type": "string", "description": "Condition severity"},
                    "patient_data": {"type": "object", "description": "Structured patient data"},
                    "calculated_doses": {"type": "array", "description": "List of calculated medication doses"}
                },
                "required": ["condition", "severity", "patient_data"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls with enhanced error handling."""
    try:
        if name == "parse_clinical_note":
            result = await parse_clinical_note(arguments["clinical_note"])
            
        elif name == "identify_condition":
            result = await identify_condition(
                arguments["symptoms"],
                arguments["assessment"],
                arguments.get("patient_age")
            )
            
        elif name == "calculate_medication_dose":
            result = await calculate_medication_dose(
                arguments["medication"],
                arguments["condition"],
                arguments["patient_weight"],
                arguments.get("severity", "moderate")
            )
            
        elif name == "generate_treatment_plan":
            result = await generate_treatment_plan(
                arguments["condition"],
                arguments["severity"],
                arguments["patient_data"],
                arguments.get("calculated_doses", [])
            )
            
        else:
            error_response = global_error_handler.create_error_response(
                ProcessingError(ErrorDetails(
                    code=ErrorCode.MCP_TOOL_ERROR,
                    message=f"Unknown tool: {name}",
                    details={"tool_name": name, "available_tools": ["parse_clinical_note", "identify_condition", "calculate_medication_dose", "generate_treatment_plan"]}
                ))
            )
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
        
        # Return successful result
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
    except Exception as e:
        # Handle all errors through the global error handler
        error_response = global_error_handler.handle_exception(e, {
            "tool_name": name,
            "arguments": arguments
        })
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]


def main():
    """Main entry point for the MCP server."""
    import mcp.server.stdio
    
    logger.info("Starting Heidi Clinical Decision Support MCP Server")
    
    # Check if data files exist
    if not CONDITIONS_FILE.exists():
        logger.warning(f"Conditions file not found: {CONDITIONS_FILE}")
    if not GUIDELINES_FILE.exists():
        logger.warning(f"Guidelines file not found: {GUIDELINES_FILE}")
    
    # Run the server
    mcp.server.stdio.run_server(app)


if __name__ == "__main__":
    main()