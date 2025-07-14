import json
import logging
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def check_data_files() -> dict:
    """
    Check if required data files are accessible.
    
    Returns:
        dict: Status of data files
    """
    data_status = {}
    
    # Check if running in Lambda environment
    if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        # In Lambda, use DATA_PATH environment variable
        data_path = os.environ.get('DATA_PATH', '/opt/data/')
        data_dir = Path(data_path)
    else:
        # Local development
        data_dir = Path(__file__).parent.parent / 'mcp_server' / 'data'
    
    conditions_file = data_dir / 'conditions.json'
    guidelines_file = data_dir / 'guidelines.json'
    
    data_status['conditions_file'] = {
        'path': str(conditions_file),
        'exists': conditions_file.exists(),
        'size': conditions_file.stat().st_size if conditions_file.exists() else 0
    }
    
    data_status['guidelines_file'] = {
        'path': str(guidelines_file),
        'exists': guidelines_file.exists(),
        'size': guidelines_file.stat().st_size if guidelines_file.exists() else 0
    }
    
    return data_status

def check_environment() -> dict:
    """
    Check environment configuration.
    
    Returns:
        dict: Environment status
    """
    env_status = {}
    
    # Check required environment variables
    required_vars = ['API_KEY']
    optional_vars = ['AWS_REGION', 'LOG_LEVEL', 'ENVIRONMENT']
    
    env_status['required'] = {}
    for var in required_vars:
        env_status['required'][var] = {
            'set': var in os.environ,
            'length': len(os.environ.get(var, ''))
        }
    
    env_status['optional'] = {}
    for var in optional_vars:
        env_status['optional'][var] = {
            'set': var in os.environ,
            'value': os.environ.get(var, 'not_set')
        }
    
    return env_status

def handler(event, context):
    """
    Comprehensive health check endpoint that validates:
    - Service availability
    - Data file accessibility
    - Environment configuration
    - MCP server module availability
    """
    logger.info("Health check requested")
    
    health_status = {
        'status': 'healthy',
        'service': 'heidi-api',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'request_id': context.aws_request_id if context else 'local',
        'environment': os.environ.get('ENVIRONMENT', 'unknown')
    }
    
    # Check data files
    try:
        data_status = check_data_files()
        health_status['data_files'] = data_status
        
        # Check if any critical data files are missing
        if not data_status['conditions_file']['exists']:
            health_status['status'] = 'degraded'
            health_status['warnings'] = health_status.get('warnings', [])
            health_status['warnings'].append('Conditions data file not found')
            
    except Exception as e:
        logger.error(f"Error checking data files: {e}")
        health_status['status'] = 'degraded'
        health_status['errors'] = health_status.get('errors', [])
        health_status['errors'].append(f'Data file check failed: {str(e)}')
    
    # Check environment
    try:
        env_status = check_environment()
        health_status['environment_config'] = env_status
        
        # Check if API key is configured
        if not env_status['required']['API_KEY']['set']:
            health_status['status'] = 'degraded'
            health_status['warnings'] = health_status.get('warnings', [])
            health_status['warnings'].append('API_KEY not configured')
            
    except Exception as e:
        logger.error(f"Error checking environment: {e}")
        health_status['status'] = 'degraded'
        health_status['errors'] = health_status.get('errors', [])
        health_status['errors'].append(f'Environment check failed: {str(e)}')
    
    # Check MCP server availability
    try:
        import sys
        backend_path = Path(__file__).parent.parent
        sys.path.insert(0, str(backend_path))
        
        from mcp_server.server import parse_clinical_note
        health_status['mcp_server'] = {
            'available': True,
            'module_path': str(backend_path / 'mcp_server')
        }
    except ImportError as e:
        logger.warning(f"MCP server module not available: {e}")
        health_status['mcp_server'] = {
            'available': False,
            'error': str(e)
        }
        health_status['status'] = 'degraded'
        health_status['warnings'] = health_status.get('warnings', [])
        health_status['warnings'].append('MCP server module not available')
    
    # Determine final status code
    status_code = 200 if health_status['status'] == 'healthy' else 503
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        },
        'body': json.dumps(health_status, indent=2)
    }