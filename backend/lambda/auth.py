import json
import logging
import os
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def validate_api_key(api_key: str) -> bool:
    """
    Validate API key against environment variable.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    expected_key = os.environ.get('API_KEY')
    
    if not expected_key:
        logger.warning("API_KEY environment variable not set")
        return False
    
    return api_key == expected_key

def extract_api_key(event: Dict[str, Any]) -> str:
    """
    Extract API key from request headers.
    
    Args:
        event: Lambda event object
        
    Returns:
        str: API key if found, empty string otherwise
    """
    headers = event.get('headers', {})
    
    # Check Authorization header (Bearer token)
    auth_header = headers.get('Authorization', headers.get('authorization', ''))
    if auth_header.startswith('Bearer '):
        return auth_header[7:]  # Remove 'Bearer ' prefix
    
    # Check x-api-key header
    api_key = headers.get('x-api-key', headers.get('X-API-Key', ''))
    if api_key:
        return api_key
    
    # Check query parameters
    query_params = event.get('queryStringParameters') or {}
    api_key = query_params.get('api_key', '')
    if api_key:
        return api_key
    
    return ''

def create_auth_response(message: str, status_code: int = 401) -> Dict[str, Any]:
    """
    Create standardized authentication response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        
    Returns:
        Dict: Lambda response object
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key',
        },
        'body': json.dumps({
            'error': 'Authentication failed',
            'message': message
        })
    }

def authenticate_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Authenticate incoming request and return appropriate response.
    
    Args:
        event: Lambda event object
        
    Returns:
        Dict: Authentication result with 'success' and optional 'response'
    """
    # Skip authentication for OPTIONS requests (CORS preflight)
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'success': True,
            'response': {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key',
                },
                'body': ''
            }
        }
    
    # Extract API key from request
    api_key = extract_api_key(event)
    
    if not api_key:
        logger.warning("No API key provided in request")
        return {
            'success': False,
            'response': create_auth_response("API key is required")
        }
    
    # Validate API key
    if not validate_api_key(api_key):
        logger.warning(f"Invalid API key provided: {api_key[:8]}...")
        return {
            'success': False,
            'response': create_auth_response("Invalid API key")
        }
    
    logger.info("Request authenticated successfully")
    return {'success': True}

def handler(event, context):
    """
    Standalone authentication handler for testing.
    """
    logger.info("Authentication handler called")
    
    auth_result = authenticate_request(event)
    
    if not auth_result['success']:
        return auth_result['response']
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({
            'message': 'Authentication successful',
            'authenticated': True
        })
    }