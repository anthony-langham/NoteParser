import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Health check endpoint
    """
    logger.info("Health check requested")
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({
            'status': 'healthy',
            'service': 'heidi-api',
            'version': '1.0.0',
            'timestamp': context.aws_request_id if context else 'local'
        })
    }