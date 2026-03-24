import requests
import json

data = {
    'full_name': 'Test User New',
    'username': 'testuser888',
    'email': 'testuser888@example.com',
    'password': 'TestPassword123'
}

try:
    response = requests.post('http://localhost:8000/api/v1/auth/register', json=data)
    print('Status:', response.status_code)
    print('Response:', json.dumps(response.json(), indent=2))
except Exception as e:
    print('Error:', str(e))
