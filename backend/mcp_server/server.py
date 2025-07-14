#!/usr/bin/env python3

import asyncio
import json
import logging
from typing import Dict, Any, List
from mcp.server import Server
from mcp.types import Tool, TextContent
from pathlib import Path

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
    """Load JSON data from file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Data file not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return {}


async def parse_clinical_note(clinical_note: str) -> Dict[str, Any]:
    """Parse clinical note and extract structured patient data."""
    from .tools.parser import parse_clinical_note as comprehensive_parse
    return await comprehensive_parse(clinical_note)


async def identify_condition(symptoms: List[str], assessment: str, patient_age: int = None) -> Dict[str, Any]:
    """Identify medical condition from symptoms and assessment."""
    conditions = load_json_data(CONDITIONS_FILE)
    
    if not conditions:
        return {"error": "Conditions data not available"}
    
    # Simple condition matching based on symptoms and assessment
    matches = []
    
    for condition_id, condition_data in conditions.items():
        score = 0
        
        # Check symptoms match
        primary_symptoms = condition_data.get('symptoms', {}).get('primary', [])
        for symptom in symptoms:
            if any(symptom.lower() in primary_symptom.lower() for primary_symptom in primary_symptoms):
                score += 2
        
        # Check assessment match
        if assessment and condition_data.get('name', '').lower() in assessment.lower():
            score += 3
        
        # Age group check
        if patient_age and 'age_groups' in condition_data:
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
                'matched_symptoms': [s for s in symptoms if any(s.lower() in ps.lower() for ps in primary_symptoms)]
            })
    
    # Sort by confidence score
    matches.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    return {
        'matches': matches,
        'top_match': matches[0] if matches else None
    }


async def calculate_medication_dose(
    medication: str, 
    condition: str, 
    patient_weight: float, 
    severity: str = "moderate"
) -> Dict[str, Any]:
    """Calculate weight-based medication dose."""
    conditions = load_json_data(CONDITIONS_FILE)
    
    if not conditions:
        return {"error": "Conditions data not available"}
    
    # Find condition
    condition_data = None
    for cond_id, cond_data in conditions.items():
        if cond_id == condition or cond_data.get('name', '').lower() == condition.lower():
            condition_data = cond_data
            break
    
    if not condition_data:
        return {"error": f"Condition '{condition}' not found"}
    
    # Find medication in condition
    medications = condition_data.get('medications', {})
    medication_data = None
    
    for med_line in ['first_line', 'second_line']:
        if med_line in medications and medication in medications[med_line]:
            medication_data = medications[med_line][medication]
            break
    
    if not medication_data:
        return {"error": f"Medication '{medication}' not found for condition '{condition}'"}
    
    # Calculate dose
    dose_per_kg = medication_data.get('dose_mg_per_kg', 0)
    calculated_dose = dose_per_kg * patient_weight
    
    # Apply limits
    max_dose = medication_data.get('max_dose_mg', float('inf'))
    min_dose = medication_data.get('min_dose_mg', 0)
    
    final_dose = min(max(calculated_dose, min_dose), max_dose)
    
    return {
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
        "dosing_rationale": f"Calculated at {dose_per_kg} mg/kg for {patient_weight}kg patient"
    }


async def generate_treatment_plan(
    condition: str, 
    severity: str, 
    patient_data: Dict[str, Any], 
    calculated_doses: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate comprehensive treatment plan."""
    conditions = load_json_data(CONDITIONS_FILE)
    guidelines = load_json_data(GUIDELINES_FILE)
    
    if not conditions:
        return {"error": "Conditions data not available"}
    
    # Find condition
    condition_data = None
    for cond_id, cond_data in conditions.items():
        if cond_id == condition or cond_data.get('name', '').lower() == condition.lower():
            condition_data = cond_data
            break
    
    if not condition_data:
        return {"error": f"Condition '{condition}' not found"}
    
    # Generate treatment plan
    plan = {
        "condition": condition_data.get('name', condition),
        "severity": severity,
        "patient_summary": {
            "age": patient_data.get('patient_data', {}).get('age'),
            "weight": patient_data.get('patient_data', {}).get('weight'),
            "symptoms": patient_data.get('symptoms', [])
        },
        "medications": calculated_doses or [],
        "monitoring": [],
        "follow_up": [],
        "red_flags": condition_data.get('red_flags', []),
        "clinical_pearls": condition_data.get('clinical_pearls', [])
    }
    
    return plan


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
    """Handle tool calls."""
    try:
        if name == "parse_clinical_note":
            result = await parse_clinical_note(arguments["clinical_note"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "identify_condition":
            result = await identify_condition(
                arguments["symptoms"],
                arguments["assessment"],
                arguments.get("patient_age")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "calculate_medication_dose":
            result = await calculate_medication_dose(
                arguments["medication"],
                arguments["condition"],
                arguments["patient_weight"],
                arguments.get("severity", "moderate")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "generate_treatment_plan":
            result = await generate_treatment_plan(
                arguments["condition"],
                arguments["severity"],
                arguments["patient_data"],
                arguments.get("calculated_doses", [])
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


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