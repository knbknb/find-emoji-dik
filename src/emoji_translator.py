from mastodon import Mastodon
from bs4 import BeautifulSoup
from moby_dick_parser import MobyDickParser

# from dotenv
from dotenv import load_dotenv, find_dotenv
import os
import requests
import json
from datetime import datetime, timedelta
import re  # added for attribution splitting

class EmojiTranslator:
    def __init__(self):
        self.literature_accounts = [
            {
                "user": "@mobydick@mastodon.art",
                "author": "Herman Melville",
                "work": "Moby Dick",
                "source_file": "./data/moby-dick-lowercase.txt",
                "attribution": None
            },
            # {
            #     "user": "@SamuelPepys@mastodon.social",
            #     "author": "Samuel Pepys",
            #     "work": "The Diary",
            #     "source_file": None
            # },
            {
                "user": "@anarchistquotes@todon.eu",
                "author": "Anarchist Quotes",
                "work": "Various",
                "source_file": None,
                "attribution": None
            },
            {
                "user": "@ShakespeareQuotes@botsin.space",
                "author": "William Shakespeare",
                "work": "Collected Works",
                "source_file": None,
                "attribution": None
            }
        ]
        load_dotenv(find_dotenv())
        self.file_path = './data/moby-dick-lowercase.txt'
        self.toot_storage_file = 'data/toot_storage.json'
        self.user = "@mobydick@mastodon.art" # will be overwritten
        self.mastodon_instance_url = 'https://social.vivaldi.net'
        self.mastodon_client_id = os.getenv('MASTODON_CLIENT_ID')
        self.mastodon_client_secret = os.getenv('MASTODON_CLIENT_SECRET')
        self.mastodon_access_token = os.getenv('MASTODON_ACCESS_TOKEN')
        self.openai_access_token = os.getenv('OPENAI_ACCESS_TOKEN')
        self.n_words = 4  # trying to match this many words of a @mobydick toot in book
                
        self.translate_service_url = "https://api.openai.com/v1/chat/completions"
        self.attribution = None

    def last_n_words(self, s, n=5) :
        '''Return the last n words from a toot/string, removing the period at the end if present.'''
        words = s.split()
        if len(words) <= n:
            result = s
        else:
            result = ' '.join(words[-n:])
        result = result.rstrip('.')
        return result

    def split_attribution(self, text):
        """Split trailing attribution line starting with '--' from the text."""
        lines = text.splitlines()
        if len(lines) > 1:
            last = lines[-1].strip()
            if re.match(r"^--\s*", last):
                return "\n".join(lines[:-1]), last
        return text, ""

    def load_toot_storage(self, file_path):
        """Load toot storage from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # convert from old format if necessary
                for k, v in list(data.items()):
                    if isinstance(v, str):
                        data[k] = {
                            "emoji": v,
                            "date": "1970-01-01T00:00:00"
                        }
                return data
        except FileNotFoundError:
            return {}

    def save_toot_storage(self, file_path, storage):
        """Save toot storage to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(storage, f, indent=2)

    def should_post(self, storage, toot, interval_days=120):
        """Return True if toot should be posted based on interval."""
        entry = storage.get(toot)
        if not entry:
            return True
        try:
            last = datetime.fromisoformat(entry.get("date", "1970-01-01T00:00:00"))
        except ValueError:
            return True
        return datetime.now() - last > timedelta(days=interval_days)

    def call_api_for_emoji_translation(self, url, openai_access_token, text):
        """Make an API call to translate text to emojis."""

        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": "translate the following text into emojis: '%s'. I need only the emojis, on a single line. Do not respond with text."
                }
            ],
            "temperature": 1, # 1-maximum creativity
            "top_p": 1,
            "n": 1,
            "stream": False,
            "max_tokens": 450,
            "presence_penalty": 0,
            "frequency_penalty": 0
        }
        payload['messages'][0]['content'] = payload['messages'][0]['content'] % text

        payload_json = json.dumps(payload)
        headers = {
            "Authorization": "Bearer %s",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        headers['Authorization'] = headers['Authorization'] % openai_access_token
        response = requests.request("POST", url, headers=headers, data=payload_json)

        return response

    def translate_to_emoji(self, url, openai_access_token="openai_access_token", text="🐳"):
        """Translate text to emojis and store the result in toot_storage."""
        # extract and store any trailing attribution before calling API
        main_text, extratext = self.split_attribution(text)
        self.attribution = extratext
        # call API with cleaned main text
        response = self.call_api_for_emoji_translation(url, openai_access_token, main_text)
        emoji_text = response.json()['choices'][0]['message']['content']
        return emoji_text

    def run(self, config):
        # Create a dictionary to serve as the persistent storage for the toots:
        toot_storage = {}
        
        # Create API object
        api = Mastodon(
            client_id=config.mastodon_client_id,
            client_secret=config.mastodon_client_secret,
            access_token=config.mastodon_access_token,
            api_base_url=config.mastodon_instance_url
        )
        if config.dry_run:
            print(api.retrieve_mastodon_version())

        # if the command-line has a "toot" argument with any string, use that,
        # otherwise fetch the most recent toot
        toot_storage = self.load_toot_storage(config.toot_storage_file)
        if config.toot:
            toots = [config.toot]
            fragment = config.toot

        else:
            for account in self.literature_accounts:
                user = account['user']
                author = account['author']
                work = account['work']
                source_file = account['source_file']
                
                # Fetch account info
                account_info = api.account_search(user, following=True)[0]
                
                toots = api.account_statuses(account_info.id, limit=1)
                if config.dry_run:
                    print(f"########## {user} toot: {toots[0]} #########")
                if not toots:
                    continue
                    
                most_recent_toot = toots[0]
                text = most_recent_toot.content
                soup = BeautifulSoup(text, 'html.parser')
                fragment = soup.get_text()

                toot = fragment
                if not self.should_post(toot_storage, toot, interval_days=120):
                    if config.dry_run:
                        print(f"########## Skipping toot from {user}; posted recently #########")
                    continue
                    
                # Citation based on account
                citation = f"        -- {author} (h/t {user})"
                
                # If source file exists, try to find the fragment in it
                chapter_info = ""
                if source_file:
                    fragment = self.last_n_words(fragment.lower(), self.n_words)
                    parser = MobyDickParser(source_file)
                    chapter_num, chapter_title, paragraph_num, sentence_num = parser.find_fragment(fragment)
                    print(f"Last {self.n_words} words: {fragment}")
                    if chapter_num:
                        print(f"Found in {work}!")
                        chapter_info = f"\n({work} - Chapter {chapter_num}: \"{chapter_title}\", Paragraph {paragraph_num}, Sentence {sentence_num})"

                # Translate and post
                if toot in toot_storage:
                    emoji_toot = toot_storage[toot]['emoji']
                else:
                    (emoji_toot, extratext) = self.translate_to_emoji(
                        self.translate_service_url,
                        config.openai_access_token,
                        toot + self.attribution if self.attribution else ""
                    )

                if not config.dry_run:
                    toot_storage[toot] = {
                        'emoji': emoji_toot,
                        'date': datetime.now().isoformat()
                    }
                    self.save_toot_storage(config.toot_storage_file, toot_storage)
                
                # Format the final toot
                emoji_toot = f"{toot}:\n{emoji_toot}\n{citation}{chapter_info}"
                    
                if emoji_toot and not config.dry_run:
                    print(emoji_toot)
                    api.toot(emoji_toot)
                elif config.dry_run:
                    print(emoji_toot)
                    print(f"######### Dry run, not posting emoji_toot from {user} to Mastodon #########")
                else:
                    print("No emoji toot found. OpenAI API call failed?")
        # Wait for a while before polling again
        #time.sleep(60)        

