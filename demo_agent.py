#!/usr/bin/env python3
"""
Heidi Clinical Decision Support - 20-line Agent Demo
Demonstrates complete clinical workflow: parse → identify → dose → plan
"""

import asyncio
import json
import sys
from backend.mcp_server.server import parse_clinical_note, identify_condition, calculate_medication_dose, generate_treatment_plan

async def main():
    """Minimal demo of complete clinical decision support workflow."""
    
    # Sample clinical note (Jack T. croup case from CLAUDE.md)
    clinical_note = """
    Patient: Jack T.
    DOB: 12/03/2022
    Age: 3 years
    Weight: 14.2 kg
    
    Presenting complaint:
    Jack presented with a 2-day history of barky cough, hoarse voice, and low-grade fever. 
    Symptoms worsened overnight, with increased work of breathing and stridor noted at rest this morning.
    
    Assessment:
    Jack presents with classic features of moderate croup (laryngotracheobronchitis), likely viral in origin.
    """
    
    try:
        # Step 1: Parse clinical note
        parsed = await parse_clinical_note(clinical_note)
        print("✅ PARSED:", json.dumps(parsed, indent=2))
        
        # Step 2: Identify condition
        symptoms = parsed['patient_data']['symptoms']
        assessment = parsed['patient_data']['assessment']
        age = parsed['patient_data']['age']
        condition_result = await identify_condition(symptoms, assessment, age)
        condition = condition_result['top_match']['condition_id']
        print("✅ CONDITION:", condition)
        
        # Step 3: Calculate medication dose
        weight = parsed['patient_data']['weight']
        dose_result = await calculate_medication_dose('dexamethasone', condition, weight, 'moderate')
        print("✅ DOSE:", f"{dose_result['final_dose']}mg {dose_result['medication']}")
        
        # Step 4: Generate treatment plan
        treatment_plan = await generate_treatment_plan(condition, 'moderate', parsed['patient_data'], [dose_result])
        print("✅ TREATMENT PLAN:", json.dumps(treatment_plan, indent=2))
        
    except Exception as e:
        print("❌ ERROR:", str(e))

if __name__ == "__main__":
    asyncio.run(main())