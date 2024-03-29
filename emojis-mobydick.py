#!/usr/bin/env python3
# Query the mobydick bot on Mastodon for the most recent toot,
# find the last 4 words in the toot,
# search the book for the fragment,
# translate the toot into emojis using the OpenAI API,
# post the emoji toot on Mastodon. also post the citation from the book.
# write it to a file for later reference. write it to the console.
# Optionally read in a toot from the command line.
#
# Needs:
#    - a mastodon account, an OpenAI account
#    - API keys+secret for mastodon, API key for OpenAI
#    - the mastodon account should follow the mobydick bot
#    - a local copy of the book "Moby Dick" in a text file

# pip install wheel bs4 requests python-dotenv Mastodon.py 
from mastodon import Mastodon
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv, find_dotenv
import os
import json
from moby_dick_parser import MobyDickParser
import argparse

# Load .env file with API keys and credentials
load_dotenv(find_dotenv())

##### 
#  Some constants needed in various places inside code
#####

#
toot_fragment_1 = "        -- Herman Melville (h/t @mobydick@botsin.space)"

translate_service_url = "https://api.openai.com/v1/chat/completions"
##### 
#  End constants 
#####


def main(config):
    # Create a dictionary to serve as the persistent storage for the toots:
    toot_storage = {}
    
    # Create API object
    api = Mastodon(
        client_id=config.mastodon_client_id,
        client_secret=config.mastodon_client_secret,
        access_token=config.mastodon_access_token,
        api_base_url=config.mastodon_instance_url
    )

    def last_n_words(s, n=5) :
        '''Return the last n words from a toot/string, removing the period at the end if present.'''
        words = s.split()
        if len(words) <= n:
            return s
        else:
            s = ' '.join(words[-n:])
            s = s.replace('.', '')
            return s

    def load_toot_storage(file_path):
        """Load toot storage from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_toot_storage(file_path, storage):
        """Save toot storage to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(storage, f)

    def call_api_for_emoji_translation(url, openai_access_token, text):
        """Make an API call to translate text to emojis."""
        payload = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "user",
                    "content": "translate the following text into emojis: '%s'"
                }
            ],
            "temperature": 1,
            "top_p": 1,
            "n": 1,
            "stream": False,
            "max_tokens": 250,
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

    def translate_to_emoji(url, openai_access_token="openai_access_token", text="🐳"):
        """Translate text to emojis and store the result in toot_storage."""
        if text in toot_storage:
            return toot_storage[text]
        
        response = call_api_for_emoji_translation(url, openai_access_token, text)
        emoji_text = response.json()['choices'][0]['message']['content']
        
        toot_storage[text] = emoji_text
        save_toot_storage(config.toot_storage_file, toot_storage)
        
        return emoji_text


    # Fetch the most recent toots from the '@mobydick' user.
    # It is a user we already follow, thus the search is faster.
    mobydick = api.account_search(config.user, following=True)[0]

    toot_storage = load_toot_storage(config.toot_storage_file)
    toots = api.account_statuses(mobydick.id, limit=1, since_id=None)
    if toots:
        most_recent_toot = toots[0]
        # Fetch the text of the toot
        text = most_recent_toot.content
        # strip the html tag(s), if present, e.g. <p>
        soup = BeautifulSoup(text, 'html.parser')
        fragment = soup.get_text()
        # find the fragment in the book stored locally
        toot = fragment
        print(toot)
        # fragment = 'stubb and flask mounted on them'
        n_words = 4
        fragment = last_n_words(fragment.lower(), n_words)
        parser = MobyDickParser(config.file_path)
        print(f"Last {n_words} words: {fragment}")
        chapter_num, chapter_title, paragraph_num, sentence_num = parser.find_fragment(fragment)
        print(f"Chapter {chapter_num}:{chapter_title}, Paragraph {paragraph_num}, Sentence {sentence_num}")
        # Translate the toot into emojis
        emoji_toot = translate_to_emoji(translate_service_url, config.openai_access_token, toot) 
        # if found in book, add the citation
        emoji_toot = toot + ":\n" + emoji_toot + "\n" + toot_fragment_1
        # print(emoji_toot)
        if chapter_num:
            print("Found in book!")
            emoji_toot = f"{emoji_toot}\n(Chapter {chapter_num}: \"{chapter_title}\", Paragraph {paragraph_num}, Sentence {sentence_num})"
        # Post the emoji toot
        if emoji_toot:
            print(emoji_toot)
            #print("posted")
            api.toot(emoji_toot)
        else:
            print("No emoji toot found.")
    # Wait for a while before polling again
    #time.sleep(60)

def parse_command_line_args():
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(description='All arguments are optional.')
        parser.add_argument('-f', '--file', type=str, help='Path to the Moby Dick book file')
        parser.add_argument('-u', '--user', type=str, help='Mastodon user to fetch toots from')
        parser.add_argument('-i', '--instance', type=str, help='Mastodon instance URL')
        parser.add_argument('-c', '--client-id', type=str, help='Mastodon client ID')
        parser.add_argument('-s', '--client-secret', type=str, help='Mastodon client secret')
        parser.add_argument('-a', '--access-token', type=str, help='Mastodon access token')
        parser.add_argument('-o', '--openai-token', type=str, help='OpenAI access token')
        # ignored in main() for now: --toot : TODO
        parser.add_argument('-t', '--toot', type=str, help='The @mobydick toot to search for in the book')
        
        args = parser.parse_args()
        return args

def create_config(args):
    # Set the file path (local copy of the book Moby Dick)
    file_path = args.file                       if args.file else './data/moby-dick-lowercase.txt'
    
    # Define the user we want to fetch toots from. 
    # Assume we follow this user on Mastodon:
    user = args.user                            if args.user else "@mobydick@botsin.space"
    
    # Set the Mastodon instance URL
    mastodon_instance_url = args.instance       if args.instance else 'https://social.vivaldi.net'
    
    # Set the Mastodon API keys
    mastodon_client_id = args.client_id         if args.client_id     else os.getenv('MASTODON_CLIENT_ID')
    mastodon_client_secret = args.client_secret if args.client_secret else os.getenv('MASTODON_CLIENT_SECRET')
    mastodon_access_token = args.access_token   if args.access_token  else os.getenv('MASTODON_ACCESS_TOKEN')
    
    # Set the OpenAI access token
    openai_access_token = args.openai_token     if args.openai_token  else os.getenv('OPENAI_ACCESS_TOKEN')

    toot = args.toot                            if args.toot else None
    toot_storage_file = 'data/toot_storage.json'
    
    class Config:
        def __init__(self, **entries):
            self.__dict__.update(entries)
    
    config_dict = {
        'file_path': file_path,
        'toot_storage_file': toot_storage_file,
        'user': user,
        'mastodon_instance_url': mastodon_instance_url,
        'mastodon_client_id': mastodon_client_id,
        'mastodon_client_secret': mastodon_client_secret,
        'mastodon_access_token': mastodon_access_token,
        'openai_access_token': openai_access_token,
        'toot': toot,
    }
    config = Config(**config_dict)
    return config
            
if __name__ == "__main__":
    args = parse_command_line_args()
    config = create_config(args)
    main(config)