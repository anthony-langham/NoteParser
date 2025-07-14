#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location("process", "lambda/process.py")
process_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(process_module)
handler = process_module.handler
import json

# Test event that simulates API Gateway request
test_event = {
    'body': json.dumps({
        'clinical_note': '''
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
'''
    }),
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
    print('Lambda Handler Result:')
    print(json.dumps(result, indent=2))