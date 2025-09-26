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
from typing import Optional, List
from pydantic import BaseModel, field_validator

class LiteratureAccount(BaseModel):
    user: str
    author: str
    work: str
    source_file: Optional[str] = None
    attribution: Optional[str] = None

    @field_validator('user')
    @classmethod
    def validate_user(cls, v: str) -> str:
        # very light validation: must look like an account reference
        # e.g. @name@instance.tld
        if not v.startswith('@') or '@' not in v[1:]:
            raise ValueError("user must be a Mastodon-style handle like @name@instance")
        return v

class EmojiTranslator:
    def __init__(self):
        self.literature_accounts: List[LiteratureAccount] = [
            LiteratureAccount(
                user="@mobydick@mastodon.art",
                author="Herman Melville",
                work="Moby Dick",
                source_file="./data/moby-dick-lowercase.txt",
                attribution=None,
            ),
            # LiteratureAccount(
            #     user="@SamuelPepys@mastodon.social",
            #     author="Samuel Pepys",
            #     work="The Diary",
            #     source_file=None,
            # ),
            LiteratureAccount(
                user="@anarchistquotes@todon.eu",
                author="Anarchist Quotes",
                work="Various",
                source_file=None,
                attribution=None,
            ),
            LiteratureAccount(
                user="@ShakespeareQuotes@universeodon.com",
                author="William Shakespeare",
                work="Collected Works",
                source_file=None,
                attribution=None,
            ),
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
        #self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-5-nano')  # default model
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o')  # default model
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
        """Split trailing attribution line starting with '--' from the text.

        Hashtags within the attribution line are removed before returning.
        Trailing lines that consist solely of hashtags are stripped prior to
        processing so they don't interfere with attribution detection.
        """
        lines = text.splitlines()
        while lines and re.match(r"^\s*(#[^\s]+\s*)+$", lines[-1]):
            lines.pop()
        if lines:
            last = lines[-1].strip()
            if re.match(r"^--\s*", last):
                cleaned = re.sub(r"\s*#[^\s]+", "", last).rstrip()
                return "\n".join(lines[:-1]), cleaned
        return "\n".join(lines), ""

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

    def call_api_for_emoji_translation(self, url, openai_access_token, text, model=None):
        """Make an API call to translate text to emojis. Automatically omits
        temperature when using gpt-5 models (gpt-5-nano) which don't accept it.
        """
        model = model or self.openai_model

        # message template for chat completion
        message_template = """<task>
                        translate the following text into emojis:
                        I need only the emojis, on a single line.
                        Do not respond with text.
                        Still keep original punctuation in the emoji output.
                        Do not include any zero-width joiner characters in the output.
                    </task>
                    <text>%s</text>
                    """

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": message_template % text
                }
            ],
            "top_p": 1,
            "n": 1,
            "stream": False,
            "max_tokens": 1000
        }

        # gpt-5 family (e.g. gpt-5-nano) does not accept temperature; only add temperature
        # and penalties for models that support them.
        if not model.startswith("gpt-5"):
            payload["temperature"] = 0.95
            payload["presence_penalty"] = 0
            payload["frequency_penalty"] = 0

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
        # call API with cleaned main text and configured model
        response = self.call_api_for_emoji_translation(url, openai_access_token, main_text, model=self.openai_model)

        # robust parsing of various response shapes to avoid KeyErrors
        emoji_text = ""
        try:
            resp_json = response.json()
        except Exception:
            resp_json = {}

        if isinstance(resp_json, dict):
            choices = resp_json.get('choices')
            if choices and isinstance(choices, list) and len(choices) > 0:
                first = choices[0]
                # typical chat completion shape
                if isinstance(first.get('message'), dict):
                    emoji_text = first['message'].get('content', '') or ''
                else:
                    # fallback to text field
                    emoji_text = first.get('text', '') or ''
            else:
                # other possible shapes
                emoji_text = resp_json.get('text', '') or resp_json.get('content', '') or ''
        elif isinstance(resp_json, str):
            emoji_text = resp_json

        emoji_text = (emoji_text or "").strip()
        return emoji_text, extratext

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
                user = account.user
                author = account.author
                work = account.work
                source_file = account.source_file
                
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
                clean_toot, _ = self.split_attribution(toot)
                clean_toot = re.sub(r"\s*#[^\s]+", "", clean_toot).rstrip()
                if not self.should_post(toot_storage, clean_toot, interval_days=120):
                    if config.dry_run:
                        print(f"########## Skipping toot from {user}; posted recently #########")
                    continue
                
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
                if clean_toot in toot_storage:
                    emoji_toot = toot_storage[clean_toot]['emoji']
                    extratext = ""
                else:
                    emoji_toot, extratext = self.translate_to_emoji(
                        self.translate_service_url,
                        config.openai_access_token,
                        clean_toot,
                    )
                # replace ALL unicode char \u200d (zero-width-joiner) with empty string
                emoji_toot = re.sub(r'\u200d', '', emoji_toot).strip()
                
                if extratext and user == "@mobydick@mastodon.art":
                    attribution_line = f"\n-- {author} (h/t {user})"
                elif extratext:
                    attribution_line = f"{extratext} (h/t {user})"
                else:
                    attribution_line = f"-- {author} (h/t {user})"

                if not config.dry_run:
                    toot_storage[clean_toot] = {
                        'emoji': emoji_toot,
                        'date': datetime.now().isoformat()
                    }
                    self.save_toot_storage(config.toot_storage_file, toot_storage)

                # Format the final toot
                emoji_toot = f"{clean_toot}\n{attribution_line}\n{emoji_toot}{chapter_info}"
                    
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

