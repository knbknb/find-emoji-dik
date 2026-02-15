#!/usr/bin/env python3
"""Debug what HTTP requests the Mastodon library is making"""

import os
import logging
from dotenv import load_dotenv
from mastodon import Mastodon

# Enable HTTP debug logging
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

# Setup logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

load_dotenv()

access_token = os.getenv('MASTODON_ACCESS_TOKEN')
base_url = 'https://social.vivaldi.net'

print("=" * 60)
print("Testing Mastodon library with debug logging...")
print("=" * 60)

try:
    api = Mastodon(
        access_token=access_token,
        api_base_url=base_url
    )
    user = api.me()
    print(f"\n✓ Success: {user['username']}")
except Exception as e:
    print(f"\n✗ Failed: {e}")
