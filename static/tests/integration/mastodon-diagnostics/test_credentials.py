#!/usr/bin/env python3
"""Test Mastodon credentials"""

import os
from dotenv import load_dotenv
from mastodon import Mastodon

load_dotenv()

client_id = os.getenv('MASTODON_CLIENT_ID')
client_secret = os.getenv('MASTODON_CLIENT_SECRET')
access_token = os.getenv('MASTODON_ACCESS_TOKEN')

print("Testing Mastodon credentials...")
print(f"Client ID: {client_id[:20]}... (length: {len(client_id)})")
print(f"Access token: {access_token[:20]}... (length: {len(access_token)})")

# Check for quotes in values
if client_id.startswith("'") or client_id.startswith('"'):
    print("\n⚠️  WARNING: Credentials contain quotes! Remove quotes from .env file")
    print(f"   First char of client_id: {repr(client_id[0])}")
    print(f"   Last char of client_id: {repr(client_id[-1])}")


try:
    # Initialize Mastodon instance
    mastodon = Mastodon(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token,
        api_base_url='https://social.vivaldi.net',
        user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
    )
    
    # Test 1: Get verified credentials (minimal permission required)
    print("\n1. Testing basic auth (get current user)...")
    user = mastodon.me()
    print(f"   ✓ Success! Current user: {user['username']}")
    
    # Test 2: Try account_search
    print("\n2. Testing account_search...")
    try:
        result = mastodon.account_search('mastodon', following=True)
        print(f"   ✓ Success! Found {len(result)} results")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        print("   Note: This endpoint may require 'read:search' scope")
    
except Exception as e:
    print(f"\n✗ Authentication failed: {e}")
    print("\nPossible causes:")
    print("- Token expired or revoked")
    print("- Wrong instance URL (check api_base_url)")
    print("- Token created with insufficient scopes")
