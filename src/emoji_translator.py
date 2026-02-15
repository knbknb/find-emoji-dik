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
from app_config import AppConfig

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
    def __init__(self, config: AppConfig):
        self.config = config
        self.literature_accounts: List[LiteratureAccount] = [
            # LiteratureAccount(
                # user="@mobydick@mastodon.art",
                # author="Herman Melville",
                # work="Moby Dick",
                # source_file="./data/moby-dick-lowercase.txt",
                # attribution=None,
            # ),
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

    def call_api_for_emoji_translation_openai(self, openai_access_token, text, model=None):
        """Use OpenAI Python SDK Responses API to translate text to emojis."""
        from openai import OpenAI

        model = model or self.config.openai_model
        client = OpenAI(api_key=openai_access_token)

        message_template = """<task>
                        translate the following text into emojis.
                        I need only the emojis, on a single line.

                        Do not respond with text, except for the emojis and punctuation characters. 
                        Respond with a stream of emojis, do not break them up with spaces or newlines.  
                        Do not include any text, explanation, or commentary, just the emojis.
                        Try to insert original punctuation (commas, full stops, dashes etc.) 
                        from the original text back into the emoji output,
                        at the appropriate positions.
                        
                        If the stream of emojis is larger than 100 emojis, truncate it by taking the first 70 emojis, insert a #...',
                        then append the last 30 emojis, so that the final output is not too long 
                        but still contains the beginning and end of the emoji translation.
                    </task>
                    <text>%s</text>
                    """

        request_args = {
            "model": model,
            "input": message_template % text,
            "top_p": 1,
            "max_output_tokens": 3000,
            "reasoning" : {"effort": "minimal"}
        }

        return client.responses.create(**request_args)

    def translate_to_emoji_openai(self, openai_access_token="openai_access_token", text="🐳"):
        """Translate text to emojis using OpenAI Python SDK Responses API."""
        main_text, extratext = self.split_attribution(text)
        self.attribution = extratext

        try:
            response = self.call_api_for_emoji_translation_openai(
                openai_access_token,
                main_text,
                model=self.config.openai_model,
            )
        except Exception as e:
            # API/network error: return empty emoji text so caller can handle it
            print(f"OpenAI API error: {e}")
            return "(Translation error)", extratext

        # Prefer the SDK convenience attribute when available
        emoji_text = (getattr(response, "output_text", "") or "").strip()

        return emoji_text, extratext

    def run(self, config: AppConfig):
        # Create a dictionary to serve as the persistent storage for the toots:
        toot_storage = {}
        
        # Create API object
        api = Mastodon(
            client_id=config.mastodon_client_id,
            client_secret=config.mastodon_client_secret,
            access_token=config.mastodon_access_token,
            api_base_url=str(config.mastodon_instance_url),
            user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
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
                    fragment = self.last_n_words(fragment.lower(), self.config.n_words)
                    parser = MobyDickParser(source_file)
                    chapter_num, chapter_title, paragraph_num, sentence_num = parser.find_fragment(fragment)
                    print(f"Last {self.config.n_words} words: {fragment}")
                    if chapter_num:
                        print(f"Found in {work}!")
                        chapter_info = f"\n({work} - Chapter {chapter_num}: \"{chapter_title}\", Paragraph {paragraph_num}, Sentence {sentence_num})"

                # Translate and post
                if clean_toot in toot_storage:
                    emoji_toot = toot_storage[clean_toot]['emoji']
                    extratext = ""
                else:
                    if not config.openai_access_token:
                        raise ValueError("OpenAI access token is required; set OPENAI_ACCESS_TOKEN env or pass --openai-token")
                    emoji_toot, extratext = self.translate_to_emoji_openai(
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

