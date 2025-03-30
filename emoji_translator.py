from mastodon import Mastodon
from bs4 import BeautifulSoup
from moby_dick_parser import MobyDickParser

from dotenv import load_dotenv, find_dotenv
import os
import requests
import json
import logging

class EmojiTranslator:
    def __init__(self):
        self.literature_accounts = [
            {
                "user": "@mobydick@mastodon.art",
                "author": "Herman Melville",
                "work": "Moby Dick",
                "source_file": "./data/moby-dick-lowercase.txt"
            },
            {
                "user": "@SamuelPepys@mastodon.social",
                "author": "Samuel Pepys",
                "work": "The Diary",
                "source_file": None
            }
        ]
        load_dotenv(find_dotenv())
        load_dotenv(find_dotenv())
        self.file_path = './data/moby-dick-lowercase.txt'
        self.toot_storage_file = 'data/toot_storage.json'
        self.user = "@mobydick@mastodon.art"
        self.mastodon_instance_url = 'https://social.vivaldi.net'
        self.toot_fragment_1 = "        -- Herman Melville (h/t @mobydick@mastodon.art)"
        self.mastodon_client_id = os.getenv('MASTODON_CLIENT_ID')
        self.mastodon_client_secret = os.getenv('MASTODON_CLIENT_SECRET')
        self.mastodon_access_token = os.getenv('MASTODON_ACCESS_TOKEN')
        self.openai_access_token = os.getenv('OPENAI_ACCESS_TOKEN')
        self.n_words = 4  # trying to match this many words of a @mobydick toot in book
                
        self.translate_service_url = "https://api.openai.com/v1/chat/completions"
        self.most_recent_toot_id = None
        self.api = Mastodon(
            client_id=self.mastodon_client_id,
            client_secret=self.mastodon_client_secret,
            access_token=self.mastodon_access_token,
            api_base_url=self.mastodon_instance_url
        )

    def last_n_words(self, s, n=5) :
        '''Return the last n words from a toot/string, removing the period at the end if present.'''
        words = s.split()
        if len(words) <= n:
            return s
        else:
            s = ' '.join(words[-n:])
            s = s.replace('.', '')
            return s

    def load_toot_storage(self, file_path):
        """Load toot storage from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_toot_storage(self, file_path, storage):
        """Save toot storage to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(storage, f)

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
            "temperature": 1,
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
        response = self.call_api_for_emoji_translation(url, openai_access_token, text)
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
                
                toots = api.account_statuses(account_info.id, limit=1, since_id=None)
                
                if not toots:
                    continue
                    
                most_recent_toot = toots[0]
                text = most_recent_toot.content
                soup = BeautifulSoup(text, 'html.parser')
                fragment = soup.get_text()

                toot = fragment
                if toot in toot_storage and config.dry_run:
                    print(f"########## Toot from {user} already in storage. Skipping. #########")
                    continue
                elif toot in toot_storage:
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
                emoji_toot = self.translate_to_emoji(self.translate_service_url, config.openai_access_token, toot)
                
                if not config.dry_run:
                    toot_storage[toot] = emoji_toot
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

if __name__ == '__main__':
    translator = EmojiTranslator()
    translator.run()