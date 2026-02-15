#!/usr/bin/env python3
"""Test Mastodon API with raw HTTP requests"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv('MASTODON_ACCESS_TOKEN')
base_url = 'https://social.vivaldi.net'

print("Testing raw API calls...")
print(f"Instance: {base_url}")
print(f"Token (first 20): {access_token[:20]}...")
print(f"Token length: {len(access_token)}")
print()

# Test 1: GET /api/v1/instance (no auth required)
print("1. Testing public endpoint (instance info)...")
try:
    response = requests.get(f'{base_url}/api/v1/instance')
    print(f"   Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"   ✓ Instance: {data.get('title', 'Unknown')}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print()

# Test 2: GET /api/v1/accounts/verify_credentials (requires auth)
print("2. Testing authenticated endpoint (verify_credentials)...")
headers = {
    'Authorization': f'Bearer {access_token}'
}
try:
    response = requests.get(
        f'{base_url}/api/v1/accounts/verify_credentials',
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    
    if response.ok:
        data = response.json()
        print(f"   ✓ Username: {data.get('username', 'Unknown')}")
    else:
        print(f"   ✗ Response body: {response.text}")
        print(f"   Headers sent: {headers}")
except Exception as e:
    print(f"   ✗ Error: {e}")
