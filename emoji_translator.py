from mastodon import Mastodon
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv, find_dotenv
import os
import json
from moby_dick_parser import MobyDickParser

class EmojiTranslator:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.file_path = './data/moby-dick-lowercase.txt'
        self.toot_storage_file = 'data/toot_storage.json'
        self.user = "@mobydick@botsin.space"
        self.mastodon_instance_url = 'https://social.vivaldi.net'
        self.toot_fragment_1 = "        -- Herman Melville (h/t @mobydick@botsin.space)"
        self.mastodon_client_id = os.getenv('MASTODON_CLIENT_ID')
        self.mastodon_client_secret = os.getenv('MASTODON_CLIENT_SECRET')
        self.mastodon_access_token = os.getenv('MASTODON_ACCESS_TOKEN')
        self.openai_access_token = os.getenv('OPENAI_ACCESS_TOKEN')
        self.translate_service_url = "https://api.openai.com/v1/chat/completions"
        self.toot_storage = self.load_toot_storage(self.toot_storage_file)
        self.most_recent_toot_id = None
        self.api = Mastodon(
            client_id=self.mastodon_client_id,
            client_secret=self.mastodon_client_secret,
            access_token=self.mastodon_access_token,
            api_base_url=self.mastodon_instance_url
        )

    # ... [move the method definitions (e.g., `load_toot_storage`, `save_toot_storage`, etc.) here] ...

    def run(self):
        mobydick = self.api.account_search(self.user, following=True)[0]
        toots = self.api.account_statuses(mobydick.id, limit=1, since_id=self.most_recent_toot_id)
        if toots:
            # ... [most of the procedural steps from the script] ...
            
            # For methods that were formerly functions, adjust the call to use self, e.g.:
            # emoji_toot = self.translate_to_emoji(self.translate_service_url, self.openai_access_token, toot)

if __name__ == '__main__':
    translator = EmojiTranslator()
    translator.run()