#!/usr/bin/env python3
"""Test with custom user agent"""

import os
from dotenv import load_dotenv
from mastodon import Mastodon

load_dotenv()

access_token = os.getenv('MASTODON_ACCESS_TOKEN')
base_url = 'https://social.vivaldi.net'

print("Test 1: Default user agent (mastodonpy)")
try:
    api = Mastodon(
        access_token=access_token,
        api_base_url=base_url
    )
    user = api.me()
    print(f"   ✓ Success: {user['username']}\n")
except Exception as e:
    print(f"   ✗ Failed: {e}\n")

print("Test 2: Custom user agent (Mozilla)")
try:
    api = Mastodon(
        access_token=access_token,
        api_base_url=base_url,
        user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0'
    )
    user = api.me()
    print(f"   ✓ Success: {user['username']}\n")
except Exception as e:
    print(f"   ✗ Failed: {e}\n")
