import json
import logging
import os
import sys
from pathlib import Path

# Add the mcp_server to Python path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

try:
    from mcp_server.server import (
        parse_clinical_note,
        identify_condition,
        calculate_medication_dose,
        generate_treatment_plan
    )
except ImportError as e:
    print(f"Warning: MCP server import failed: {e}")
    parse_clinical_note = None
    identify_condition = None
    calculate_medication_dose = None
    generate_treatment_plan = None

logger = logging.getLogger()
logger.setLevel(logging.INFO)

async def process_clinical_note_async(clinical_note: str):
    """
    Process clinical note using MCP server tools asynchronously.
    """
    try:
        # Step 1: Parse clinical note
        parsed_data = await parse_clinical_note(clinical_note)
        if not parsed_data.get('success'):
            return {
                'success': False,
                'error': 'Failed to parse clinical note',
                'details': parsed_data
            }
        
        patient_data = parsed_data['patient_data']
        
        # Step 2: Identify condition
        symptoms = parsed_data.get('symptoms', [])
        assessment = parsed_data.get('assessment', '')
        patient_age = patient_data.get('age')
        
        condition_result = await identify_condition(symptoms, assessment, patient_age)
        if not condition_result.get('success') or not condition_result.get('top_match'):
            return {
                'success': False,
                'error': 'No matching condition found',
                'parsed_data': parsed_data,
                'condition_matches': condition_result
            }
        
        top_condition = condition_result['top_match']
        condition_name = top_condition['condition_name']
        
        # Step 3: Calculate medication doses if weight is available
        calculated_doses = []
        patient_weight = patient_data.get('weight')
        
        if patient_weight:
            # Load condition data to get medications
            from mcp_server.server import load_json_data, CONDITIONS_FILE
            conditions = load_json_data(CONDITIONS_FILE)
            
            condition_id = top_condition['condition_id']
            if condition_id in conditions:
                medications = conditions[condition_id].get('medications', {})
                
                # Calculate doses for first-line medications
                for med_name in medications.get('first_line', {}).keys():
                    try:
                        dose_result = await calculate_medication_dose(
                            med_name, condition_name, patient_weight
                        )
                        if dose_result.get('success'):
                            calculated_doses.append(dose_result)
                    except Exception as e:
                        logger.warning(f"Failed to calculate dose for {med_name}: {e}")
        
        # Step 4: Generate treatment plan
        severity = patient_data.get('severity', 'moderate')
        treatment_plan = await generate_treatment_plan(
            condition_name, severity, patient_data, calculated_doses
        )
        
        return {
            'success': True,
            'patient_data': patient_data,
            'condition': {
                'name': condition_name,
                'confidence': top_condition.get('confidence_score', 0),
                'matched_symptoms': top_condition.get('matched_symptoms', [])
            },
            'calculated_doses': calculated_doses,
            'treatment_plan': treatment_plan,
            'recommendations': {
                'primary_medication': calculated_doses[0] if calculated_doses else None,
                'monitoring': treatment_plan.get('monitoring', 'Follow standard protocols'),
                'follow_up': treatment_plan.get('follow_up', 'As clinically indicated')
            }
        }
        
    except Exception as e:
        logger.error(f"Error in clinical note processing pipeline: {e}")
        return {
            'success': False,
            'error': 'Processing pipeline error',
            'message': str(e)
        }

def process_clinical_note_sync(clinical_note: str):
    """
    Synchronous wrapper for the async processing function.
    """
    import asyncio
    
    try:
        # Create a new event loop for the Lambda function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(process_clinical_note_async(clinical_note))
        
        loop.close()
        return result
        
    except Exception as e:
        logger.error(f"Error in sync wrapper: {e}")
        return {
            'success': False,
            'error': 'Sync wrapper error',
            'message': str(e)
        }

def handler(event, context):
    """
    Process clinical notes and return treatment recommendations using MCP server tools.
    """
    logger.info(f"Processing clinical note request")
    
    # Handle preflight OPTIONS requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key, X-Api-Key',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    try:
        # Parse the request body
        if event.get('body'):
            body = json.loads(event['body'])
        else:
            body = event
        
        clinical_note = body.get('clinical_note', '')
        
        if not clinical_note.strip():
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key, X-Api-Key',
                },
                'body': json.dumps({
                    'error': 'Bad Request',
                    'message': 'clinical_note is required and cannot be empty'
                })
            }
        
        # Check if MCP server tools are available
        if not parse_clinical_note:
            # Fallback to placeholder response if MCP tools not available
            logger.warning("MCP server tools not available, using placeholder response")
            response_data = {
                'success': True,
                'message': 'Clinical note processed (placeholder)',
                'input': clinical_note[:100] + '...' if len(clinical_note) > 100 else clinical_note,
                'recommendations': [
                    {
                        'condition': 'Croup',
                        'treatment': 'Prednisolone 1mg/kg (max 20mg)',
                        'notes': 'Single dose, consider nebulized budesonide if severe'
                    }
                ]
            }
        else:
            # Use MCP server tools for processing
            response_data = process_clinical_note_sync(clinical_note)
        
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key, X-Api-Key',
            },
            'body': json.dumps(response_data)
        }
        
        return response
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {e}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key, X-Api-Key',
            },
            'body': json.dumps({
                'error': 'Bad Request',
                'message': 'Invalid JSON in request body'
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing clinical note: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key, X-Api-Key',
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }