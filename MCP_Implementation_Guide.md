# MCP Implementation Guide for Clinical Decision Support

## Overview

This guide outlines how to build a Model Context Protocol (MCP) server for the Heidi clinical decision support system. The MCP server will provide tools for parsing clinical notes, querying guidelines, calculating doses, and generating treatment recommendations.

## What is MCP?

Model Context Protocol (MCP) is a standardized way to connect AI assistants with external tools and data sources. It enables:
- **Structured tool calling** - Defined interfaces for specific functions
- **Real-time data access** - Dynamic information retrieval
- **Deterministic results** - Predictable, reproducible outputs
- **Type safety** - Schema validation for inputs and outputs

## MCP vs RAG for Clinical Decision Support

### Why MCP is Better for Medical Applications:

1. **Deterministic Results** - Medical decisions need to be reproducible and auditable
2. **Structured Validation** - Medical data requires strict input/output validation
3. **Performance** - Direct tool calls are faster than semantic search
4. **Safety** - Explicit logic is safer than AI interpretation for medical calculations
5. **Transparency** - Clear reasoning chain for clinical decisions

## Architecture Overview

```
Clinical Note Input
       ↓
MCP Server (Python)
       ↓
┌─────────────────────────────────────┐
│  MCP Tools:                         │
│  • parse_clinical_note()            │
│  • identify_condition()             │
│  • get_treatment_guideline()        │
│  • calculate_medication_dose()      │
│  • check_contraindications()        │
│  • generate_treatment_plan()        │
└─────────────────────────────────────┘
       ↓
Structured Treatment Plan Output
```

## Required MCP Tools

### 1. Clinical Note Parser
**Tool:** `parse_clinical_note`
- **Input:** Unstructured clinical text
- **Output:** Structured patient data (age, weight, symptoms, assessment)
- **Purpose:** Extract key medical information from free-text notes

### 2. Condition Identifier
**Tool:** `identify_condition`
- **Input:** Symptoms, assessment, clinical context
- **Output:** Matched condition with confidence score
- **Purpose:** Map clinical presentation to specific medical conditions

### 3. Guideline Retriever
**Tool:** `get_treatment_guideline`
- **Input:** Condition name, severity level, patient demographics
- **Output:** Relevant treatment protocol and recommendations
- **Purpose:** Provide evidence-based treatment guidance

### 4. Dose Calculator
**Tool:** `calculate_medication_dose`
- **Input:** Medication name, patient weight, condition, severity
- **Output:** Calculated dose, frequency, duration, maximum limits
- **Purpose:** Compute safe, effective medication dosing

### 5. Safety Checker
**Tool:** `check_contraindications`
- **Input:** Patient data, proposed medications, conditions
- **Output:** Safety warnings, contraindications, alternative options
- **Purpose:** Ensure patient safety and identify potential issues

### 6. Treatment Plan Generator
**Tool:** `generate_treatment_plan`
- **Input:** Condition, calculated doses, guidelines, patient context
- **Output:** Comprehensive, structured treatment plan
- **Purpose:** Compile all information into actionable clinical recommendations

## Data Layer Design

### JSON Schema for Medical Data

```json
{
  "conditions": {
    "croup": {
      "name": "Croup (Laryngotracheobronchitis)",
      "aliases": ["laryngotracheobronchitis", "viral croup"],
      "severity_levels": {
        "mild": {
          "criteria": ["barky cough", "no stridor at rest"],
          "medications": ["dexamethasone"]
        },
        "moderate": {
          "criteria": ["barky cough", "stridor at rest", "mild recession"],
          "medications": ["dexamethasone", "prednisolone"]
        },
        "severe": {
          "criteria": ["stridor at rest", "significant recession", "cyanosis"],
          "medications": ["dexamethasone", "nebulized epinephrine"]
        }
      },
      "age_range": {"min": 6, "max": 72, "unit": "months"},
      "diagnostic_criteria": [
        "barky cough",
        "hoarse voice",
        "inspiratory stridor",
        "fever"
      ]
    }
  },
  "medications": {
    "dexamethasone": {
      "name": "Dexamethasone",
      "generic_name": "dexamethasone",
      "brand_names": ["Decadron", "Ozurdex"],
      "dosing": {
        "croup": {
          "dose": 0.15,
          "unit": "mg/kg",
          "route": "oral",
          "frequency": "single_dose",
          "max_dose": 10,
          "min_dose": 0.6
        }
      },
      "contraindications": [
        "active infection",
        "immunocompromised",
        "severe heart failure"
      ],
      "side_effects": ["mood changes", "increased appetite", "insomnia"]
    }
  },
  "guidelines": {
    "croup_management": {
      "condition": "croup",
      "protocol": {
        "mild": {
          "treatment": ["oral dexamethasone", "supportive care"],
          "monitoring": ["symptoms", "respiratory status"],
          "discharge_criteria": ["stable breathing", "no stridor"]
        },
        "moderate": {
          "treatment": ["oral dexamethasone", "observation"],
          "monitoring": ["oxygen saturation", "work of breathing"],
          "escalation": ["consider nebulized epinephrine"]
        },
        "severe": {
          "treatment": ["dexamethasone", "nebulized epinephrine"],
          "monitoring": ["continuous monitoring", "ABG if needed"],
          "escalation": ["ICU consultation", "intubation if needed"]
        }
      }
    }
  }
}
```

## Implementation Requirements

### Technology Stack
- **Language:** Python 3.9+
- **MCP Framework:** `mcp` Python package
- **Data Validation:** Pydantic for schema validation
- **JSON Processing:** Built-in `json` module
- **Testing:** pytest for unit tests
- **Logging:** Python `logging` module

### Dependencies
```python
# requirements.txt
mcp>=1.0.0
pydantic>=2.0.0
pytest>=7.0.0
python-dateutil>=2.8.0
```

### Project Structure
```
heidi/
├── mcp_server/
│   ├── __init__.py
│   ├── server.py              # Main MCP server
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── parser.py          # Clinical note parsing
│   │   ├── condition.py       # Condition identification
│   │   ├── guideline.py       # Guideline retrieval
│   │   ├── dosing.py          # Dose calculations
│   │   ├── safety.py          # Contraindication checking
│   │   └── planner.py         # Treatment plan generation
│   ├── data/
│   │   ├── conditions.json    # Medical conditions data
│   │   ├── medications.json   # Medication database
│   │   └── guidelines.json    # Treatment protocols
│   └── schemas/
│       ├── patient.py         # Patient data models
│       ├── condition.py       # Condition models
│       └── treatment.py       # Treatment models
├── tests/
│   ├── test_parser.py
│   ├── test_dosing.py
│   └── test_integration.py
├── requirements.txt
└── README.md
```

## MCP Server Implementation

### 1. Server Setup
```python
# mcp_server/server.py
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
from .tools import (
    parse_clinical_note,
    identify_condition,
    get_treatment_guideline,
    calculate_medication_dose,
    check_contraindications,
    generate_treatment_plan
)

app = Server("heidi-clinical-decision-support")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="parse_clinical_note",
            description="Parse clinical note and extract structured patient data",
            inputSchema={
                "type": "object",
                "properties": {
                    "clinical_note": {"type": "string"}
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
                    "symptoms": {"type": "array", "items": {"type": "string"}},
                    "assessment": {"type": "string"},
                    "patient_age": {"type": "number"}
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
                    "medication": {"type": "string"},
                    "condition": {"type": "string"},
                    "patient_weight": {"type": "number"},
                    "severity": {"type": "string"}
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
                    "condition": {"type": "string"},
                    "severity": {"type": "string"},
                    "patient_data": {"type": "object"},
                    "calculated_doses": {"type": "array"}
                },
                "required": ["condition", "severity", "patient_data"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "parse_clinical_note":
        result = await parse_clinical_note(arguments["clinical_note"])
        return [TextContent(type="text", text=str(result))]
    
    elif name == "identify_condition":
        result = await identify_condition(
            arguments["symptoms"],
            arguments["assessment"],
            arguments.get("patient_age")
        )
        return [TextContent(type="text", text=str(result))]
    
    elif name == "calculate_medication_dose":
        result = await calculate_medication_dose(
            arguments["medication"],
            arguments["condition"],
            arguments["patient_weight"],
            arguments.get("severity", "moderate")
        )
        return [TextContent(type="text", text=str(result))]
    
    elif name == "generate_treatment_plan":
        result = await generate_treatment_plan(
            arguments["condition"],
            arguments["severity"],
            arguments["patient_data"],
            arguments.get("calculated_doses", [])
        )
        return [TextContent(type="text", text=str(result))]
    
    else:
        raise ValueError(f"Unknown tool: {name}")
```

### 2. Clinical Note Parser
```python
# mcp_server/tools/parser.py
import re
from typing import Dict, Optional, List
from ..schemas.patient import PatientData

async def parse_clinical_note(clinical_note: str) -> Dict:
    """Parse clinical note and extract structured patient data."""
    
    # Extract patient demographics
    patient_data = {}
    
    # Age extraction
    age_match = re.search(r'Age:\s*(\d+)\s*years?', clinical_note, re.IGNORECASE)
    if age_match:
        patient_data['age'] = int(age_match.group(1))
    
    # Weight extraction
    weight_match = re.search(r'Weight:\s*(\d+\.?\d*)\s*kg', clinical_note, re.IGNORECASE)
    if weight_match:
        patient_data['weight'] = float(weight_match.group(1))
    
    # DOB extraction
    dob_match = re.search(r'DOB:\s*(\d{1,2}/\d{1,2}/\d{4})', clinical_note, re.IGNORECASE)
    if dob_match:
        patient_data['dob'] = dob_match.group(1)
    
    # Symptom extraction
    symptoms = []
    symptom_patterns = [
        r'barky cough',
        r'hoarse voice',
        r'stridor',
        r'fever',
        r'recession',
        r'work of breathing'
    ]
    
    for pattern in symptom_patterns:
        if re.search(pattern, clinical_note, re.IGNORECASE):
            symptoms.append(pattern.replace(r'\\', ''))
    
    # Assessment extraction
    assessment_match = re.search(r'Assessment:\s*(.+?)(?=\n\n|\nPlan:|\Z)', clinical_note, re.IGNORECASE | re.DOTALL)
    assessment = assessment_match.group(1).strip() if assessment_match else ""
    
    # Vital signs extraction
    vitals = {}
    temp_match = re.search(r'T\s*(\d+\.?\d*)[°C]?', clinical_note)
    if temp_match:
        vitals['temperature'] = float(temp_match.group(1))
    
    hr_match = re.search(r'HR\s*(\d+)', clinical_note)
    if hr_match:
        vitals['heart_rate'] = int(hr_match.group(1))
    
    return {
        'patient_data': patient_data,
        'symptoms': symptoms,
        'assessment': assessment,
        'vitals': vitals
    }
```

### 3. Dose Calculator
```python
# mcp_server/tools/dosing.py
import json
from typing import Dict, Optional
from ..schemas.treatment import DoseCalculation

async def calculate_medication_dose(
    medication: str, 
    condition: str, 
    patient_weight: float, 
    severity: str = "moderate"
) -> Dict:
    """Calculate weight-based medication dose."""
    
    # Load medication data
    with open('mcp_server/data/medications.json', 'r') as f:
        medications = json.load(f)
    
    if medication not in medications:
        return {"error": f"Medication '{medication}' not found"}
    
    med_data = medications[medication]
    
    if condition not in med_data.get("dosing", {}):
        return {"error": f"No dosing information for {medication} in {condition}"}
    
    dosing_info = med_data["dosing"][condition]
    
    # Calculate dose
    dose_per_kg = dosing_info["dose"]
    calculated_dose = dose_per_kg * patient_weight
    
    # Apply limits
    max_dose = dosing_info.get("max_dose", float('inf'))
    min_dose = dosing_info.get("min_dose", 0)
    
    final_dose = min(max(calculated_dose, min_dose), max_dose)
    
    return {
        "medication": medication,
        "condition": condition,
        "patient_weight": patient_weight,
        "dose_per_kg": dose_per_kg,
        "calculated_dose": calculated_dose,
        "final_dose": final_dose,
        "unit": dosing_info["unit"],
        "route": dosing_info["route"],
        "frequency": dosing_info["frequency"],
        "max_dose": max_dose,
        "dosing_rationale": f"Calculated at {dose_per_kg} {dosing_info['unit']} for {patient_weight}kg patient"
    }
```

## Testing Strategy

### Unit Tests
```python
# tests/test_dosing.py
import pytest
from mcp_server.tools.dosing import calculate_medication_dose

@pytest.mark.asyncio
async def test_dexamethasone_dosing():
    result = await calculate_medication_dose(
        medication="dexamethasone",
        condition="croup",
        patient_weight=14.2,
        severity="moderate"
    )
    
    assert result["final_dose"] == 2.13  # 0.15 * 14.2
    assert result["unit"] == "mg/kg"
    assert result["route"] == "oral"
    assert result["frequency"] == "single_dose"

@pytest.mark.asyncio
async def test_dose_limits():
    # Test maximum dose limit
    result = await calculate_medication_dose(
        medication="dexamethasone",
        condition="croup",
        patient_weight=100,  # Would exceed max dose
        severity="moderate"
    )
    
    assert result["final_dose"] == 10  # Maximum dose
    assert result["calculated_dose"] == 15  # Original calculation
```

## Deployment and Usage

### Running the MCP Server
```bash
# Install dependencies
pip install -r requirements.txt

# Start MCP server
python -m mcp_server.server
```

### Integration with Claude
```python
# Example usage in Claude Code
import mcp

# Connect to MCP server
client = mcp.Client("heidi-clinical-decision-support")

# Parse clinical note
parsed_data = await client.call_tool(
    "parse_clinical_note",
    {"clinical_note": clinical_note_text}
)

# Calculate dose
dose_result = await client.call_tool(
    "calculate_medication_dose",
    {
        "medication": "dexamethasone",
        "condition": "croup",
        "patient_weight": 14.2,
        "severity": "moderate"
    }
)

# Generate treatment plan
treatment_plan = await client.call_tool(
    "generate_treatment_plan",
    {
        "condition": "croup",
        "severity": "moderate",
        "patient_data": parsed_data,
        "calculated_doses": [dose_result]
    }
)
```

## Next Steps

1. **Implement base MCP server structure**
2. **Create JSON data files for conditions and medications**
3. **Build and test individual tools**
4. **Create integration tests with sample clinical notes**
5. **Add error handling and validation**
6. **Deploy and test with Claude Code**

This MCP-only approach provides a clean, deterministic, and medically safe foundation for clinical decision support while maintaining the flexibility to extend with additional tools as needed.