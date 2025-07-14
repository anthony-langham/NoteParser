import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_cors_headers(origin: str = None) -> Dict[str, str]:
    """
    Get CORS headers with appropriate origin validation.
    
    Args:
        origin: The Origin header from the request
        
    Returns:
        Dict: CORS headers
    """
    # Allowed origins (can be made configurable via environment)
    allowed_origins = [
        'https://heidimcp.uk',
        'https://www.heidimcp.uk',
        'http://localhost:3000',
        'http://localhost:5173',  # Vite dev server
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173'
    ]
    
    # Determine which origin to allow
    if origin and origin in allowed_origins:
        allowed_origin = origin
    else:
        # Default to wildcard for development, or first allowed origin for production
        allowed_origin = '*'
    
    return {
        'Access-Control-Allow-Origin': allowed_origin,
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, x-api-key, X-API-Key',
        'Access-Control-Allow-Credentials': 'false',
        'Access-Control-Max-Age': '86400'  # 24 hours
    }

def create_cors_response(status_code: int = 200, body: Any = None, origin: str = None) -> Dict[str, Any]:
    """
    Create a response with proper CORS headers.
    
    Args:
        status_code: HTTP status code
        body: Response body (will be JSON-encoded if not string)
        origin: Origin header from request
        
    Returns:
        Dict: Lambda response with CORS headers
    """
    headers = {
        'Content-Type': 'application/json',
        **get_cors_headers(origin)
    }
    
    # Handle body encoding
    if body is None:
        response_body = ''
    elif isinstance(body, str):
        response_body = body
    else:
        response_body = json.dumps(body)
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': response_body
    }

def handle_preflight(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle CORS preflight OPTIONS requests.
    
    Args:
        event: Lambda event object
        
    Returns:
        Dict: Preflight response
    """
    origin = event.get('headers', {}).get('Origin', event.get('headers', {}).get('origin'))
    
    logger.info(f"Handling CORS preflight request from origin: {origin}")
    
    return create_cors_response(200, '', origin)

def add_cors_to_response(response: Dict[str, Any], origin: str = None) -> Dict[str, Any]:
    """
    Add CORS headers to an existing response.
    
    Args:
        response: Existing Lambda response
        origin: Origin header from request
        
    Returns:
        Dict: Response with CORS headers added
    """
    if 'headers' not in response:
        response['headers'] = {}
    
    # Add CORS headers
    cors_headers = get_cors_headers(origin)
    response['headers'].update(cors_headers)
    
    return response

def extract_origin(event: Dict[str, Any]) -> str:
    """
    Extract origin from request headers.
    
    Args:
        event: Lambda event object
        
    Returns:
        str: Origin header value or None
    """
    headers = event.get('headers', {})
    return headers.get('Origin', headers.get('origin'))

def handler(event, context):
    """
    Standalone CORS handler for testing.
    """
    logger.info("CORS handler called")
    
    # Handle preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return handle_preflight(event)
    
    # For other requests, just return CORS-enabled response
    origin = extract_origin(event)
    
    return create_cors_response(200, {
        'message': 'CORS test endpoint',
        'method': event.get('httpMethod', 'UNKNOWN'),
        'origin': origin,
        'cors_enabled': True
    }, origin)