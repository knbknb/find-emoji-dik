from mastodon import Mastodon
from dotenv import load_dotenv, find_dotenv
import os

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

    def run(self):
        mobydick = self.api.account_search(self.user, following=True)[0]
        self.api.account_statuses(mobydick.id, limit=1, since_id=self.most_recent_toot_id)
        
if __name__ == '__main__':
    translator = EmojiTranslator()
    translator.run()