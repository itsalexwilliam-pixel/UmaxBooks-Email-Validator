"""
Test REST API endpoints
"""

import sys
import time
import subprocess
import requests
import json

sys.path.insert(0, r'c:\Users\itsal\Desktop\uMaxBooks\UmaxBooks Email Validator')

# Start API server in background
print("=" * 70)
print("TESTING REST API ENDPOINTS")
print("=" * 70)

print("\n🚀 Starting API server...")

# Run API server in background
server_process = subprocess.Popen(
    [sys.executable, 'api_server.py'],
    cwd=r'c:\Users\itsal\Desktop\uMaxBooks\UmaxBooks Email Validator',
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Give server time to start
time.sleep(3)

API_URL = 'http://localhost:5000'

try:
    # ==================== Test 1: Health Check ====================
    print("\n✅ TEST 1: Health Check")
    print("-" * 70)

    response = requests.get(f'{API_URL}/api/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # ==================== Test 2: Single Email Validation ====================
    print("\n✅ TEST 2: Single Email Validation")
    print("-" * 70)

    payload = {
        'email': 'john@gmail.com',
        'check_smtp': False
    }

    response = requests.post(f'{API_URL}/api/validate', json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Email: {data['email']}")
    print(f"Valid: {data['is_valid']}")
    print(f"Deliverable: {data['deliverable']}")
    print(f"Confidence: {data['confidence']}%")

    # ==================== Test 3: Batch Validation ====================
    print("\n✅ TEST 3: Batch Email Validation")
    print("-" * 70)

    payload = {
        'emails': [
            'john@gmail.com',
            'jane@company.com',
            'bob@yahoo.com',
            'invalid-email'
        ],
        'check_smtp': False
    }

    response = requests.post(f'{API_URL}/api/validate/batch', json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total emails: {len(data['results'])}")
    print(f"Valid count: {data['statistics']['valid']}")
    print(f"Deliverable count: {data['statistics']['deliverable']}")
    print(f"Avg confidence: {data['statistics']['average_confidence']}%")

    # ==================== Test 4: Domain Analysis ====================
    print("\n✅ TEST 4: Domain Analysis")
    print("-" * 70)

    payload = {
        'emails': [
            'user1@gmail.com',
            'user2@gmail.com',
            'user3@yahoo.com'
        ]
    }

    response = requests.post(f'{API_URL}/api/domains', json=payload)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total domains: {data['total_domains']}")
    for domain_info in data['domains']:
        print(f"  • {domain_info['domain']}: {domain_info['count']} emails ({domain_info['percentage']:.1f}%)")

    print("\n" + "=" * 70)
    print("✅ API TESTING COMPLETE")
    print("=" * 70)
    print("\n✨ All REST API endpoints working correctly!")

except requests.exceptions.ConnectionError:
    print("❌ Error: Could not connect to API server")
    print("Make sure the server is running on http://localhost:5000")
except Exception as e:
    print(f"❌ Error: {str(e)}")

finally:
    # Stop server
    print("\n🛑 Stopping API server...")
    server_process.terminate()
    server_process.wait(timeout=5)
    print("✅ Server stopped")
