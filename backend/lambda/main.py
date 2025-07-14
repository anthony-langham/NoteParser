import json
import logging
import os
from typing import Dict, Any

# Import our Lambda modules
from .auth import authenticate_request
from .cors import extract_origin, add_cors_to_response, handle_preflight
from .health import handler as health_handler
from .process import handler as process_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def route_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main router for Lambda requests. Routes to appropriate handlers based on path.
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        Dict: Lambda response
    """
    try:
        # Extract request information
        path = event.get('path', event.get('rawPath', '/'))
        method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        origin = extract_origin(event)
        
        logger.info(f"Routing request: {method} {path}")
        
        # Handle CORS preflight for all routes
        if method == 'OPTIONS':
            return handle_preflight(event)
        
        # Route to appropriate handler
        if path == '/health' or path == '/api/health':
            # Health check doesn't require authentication
            response = health_handler(event, context)
            
        elif path == '/process' or path == '/api/process':
            # Clinical note processing requires authentication
            auth_result = authenticate_request(event)
            if not auth_result['success']:
                response = auth_result['response']
            else:
                response = process_handler(event, context)
                
        elif path == '/auth' or path == '/api/auth':
            # Authentication test endpoint
            auth_result = authenticate_request(event)
            if not auth_result['success']:
                response = auth_result['response']
            else:
                response = {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'message': 'Authentication successful',
                        'authenticated': True
                    })
                }
                
        else:
            # Unknown route
            response = {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Not Found',
                    'message': f'Route not found: {method} {path}',
                    'available_routes': [
                        'GET /health',
                        'POST /process',
                        'GET /auth'
                    ]
                })
            }
        
        # Add CORS headers to response
        response = add_cors_to_response(response, origin)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in request router: {e}")
        
        error_response = {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred while routing the request'
            })
        }
        
        return add_cors_to_response(error_response, extract_origin(event))

def handler(event, context):
    """
    Main Lambda handler entry point.
    """
    return route_request(event, context)