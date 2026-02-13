#!/usr/bin/env python3
"""Test different Mastodon initialization methods"""

import os
from dotenv import load_dotenv
from mastodon import Mastodon

load_dotenv()

client_id = os.getenv('MASTODON_CLIENT_ID')
client_secret = os.getenv('MASTODON_CLIENT_SECRET')
access_token = os.getenv('MASTODON_ACCESS_TOKEN')
base_url = 'https://social.vivaldi.net'

print("Test 1: With client_id, client_secret, and access_token")
try:
    api = Mastodon(
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token,
        api_base_url=base_url
    )
    user = api.me()
    print(f"   ✓ Success: {user['username']}\n")
except Exception as e:
    print(f"   ✗ Failed: {e}\n")

print("Test 2: With ONLY access_token (no client credentials)")
try:
    api = Mastodon(
        access_token=access_token,
        api_base_url=base_url
    )
    user = api.me()
    print(f"   ✓ Success: {user['username']}\n")
except Exception as e:
    print(f"   ✗ Failed: {e}\n")
