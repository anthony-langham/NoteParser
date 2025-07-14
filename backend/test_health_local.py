#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location("health", "lambda/health.py")
health_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health_module)
handler = health_module.handler
import json

# Test event that simulates API Gateway request
test_event = {
    'httpMethod': 'GET',
    'headers': {
        'Content-Type': 'application/json'
    }
}

# Mock context
class MockContext:
    def __init__(self):
        self.aws_request_id = 'test-request-id'

if __name__ == "__main__":
    result = handler(test_event, MockContext())
    print('Health Check Result:')
    print(json.dumps(result, indent=2))