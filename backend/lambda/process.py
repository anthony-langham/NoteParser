import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Process clinical notes and return treatment recommendations
    """
    logger.info(f"Processing clinical note: {event}")
    
    try:
        # Parse the request body
        if event.get('body'):
            body = json.loads(event['body'])
        else:
            body = event
        
        clinical_note = body.get('clinical_note', '')
        
        # Placeholder response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            },
            'body': json.dumps({
                'message': 'Clinical note processed successfully',
                'input': clinical_note,
                'recommendations': [
                    {
                        'condition': 'Croup',
                        'treatment': 'Prednisolone 1mg/kg (max 20mg)',
                        'notes': 'Single dose, consider nebulized budesonide if severe'
                    }
                ]
            })
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing clinical note: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }