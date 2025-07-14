#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server.tools.parser import ClinicalNoteParser

# Sample clinical note from CLAUDE.md
sample_note = """
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

async def test_parser():
    """Test the clinical note parser with sample data."""
    print("Testing Clinical Note Parser")
    print("=" * 50)
    
    # Create parser instance
    parser = ClinicalNoteParser()
    
    # Parse the clinical note
    result = parser.parse(sample_note)
    
    # Display results
    print(f"Parse Success: {result.success}")
    print(f"Errors: {result.errors}")
    
    if result.success and result.data:
        print("\nPatient Data:")
        print(f"  Age: {result.data.patient_data.age}")
        print(f"  Weight: {result.data.patient_data.weight}")
        print(f"  DOB: {result.data.patient_data.dob}")
        print(f"  Gender: {result.data.patient_data.gender}")
        
        print(f"\nSymptoms ({len(result.data.symptoms)}):")
        for symptom in result.data.symptoms:
            print(f"  - {symptom}")
        
        print(f"\nAssessment:")
        print(f"  {result.data.assessment}")
        
        print(f"\nPresenting Complaint:")
        print(f"  {result.data.presenting_complaint}")
        
        print(f"\nPlan:")
        print(f"  {result.data.plan}")
        
        print(f"\nVital Signs:")
        print(f"  Temperature: {result.data.vitals.temperature}")
        print(f"  Heart Rate: {result.data.vitals.heart_rate}")
        print(f"  Respiratory Rate: {result.data.vitals.respiratory_rate}")
        print(f"  Blood Pressure: {result.data.vitals.blood_pressure}")
        print(f"  Oxygen Saturation: {result.data.vitals.oxygen_saturation}")
    
    # Test the convenience function
    print("\n" + "=" * 50)
    print("Testing Convenience Function")
    print("=" * 50)
    
    from mcp_server.tools.parser import parse_clinical_note
    convenience_result = await parse_clinical_note(sample_note)
    
    print("Convenience function result:")
    import json
    print(json.dumps(convenience_result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_parser())