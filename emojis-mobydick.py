#!/usr/bin/env python3
# Query the mobydick bot on Mastodon for the most recent toot,
# find the last 4 words in the toot,
# search the book for the fragment,
# translate the toot into emojis using the OpenAI API,
# post the emoji toot on Mastodon. also post the citation from the book.
# write it to a file for later reference. write it to the console.
# Optionally read in a toot from the command line.
# Optionally set --dry-run flag to avoid posting to Mastodon.

# Needs:
#    - a mastodon account, an OpenAI account
#    - API keys+secret for mastodon, API key for OpenAI
#    - the mastodon account should follow the mobydick bot
#    - a local copy of the book "Moby Dick" in a text file; coverted to lowercase
#    - A venv that can resolve the Mastodon.py library

# pip install wheel bs4 requests python-dotenv Mastodon.py 

from dotenv import load_dotenv, find_dotenv
import os
import argparse
from emoji_translator import EmojiTranslator # loads moby_dick_parser

# Load .env file with API keys and credentials
load_dotenv(find_dotenv())

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
        parser.add_argument('-t', '--toot', type=str, help='The @mobydick toot to search for in the book')
        parser.add_argument('-d', '--dry-run', action='store_true', default=False, help='Do NOT really post the toot to mastodon network')
        
        args = parser.parse_args()
        return args

def create_config(args):
    # Set the file path (local copy of the book Moby Dick)
    file_path = args.file                       if args.file else './data/moby-dick-lowercase.txt'
    
    # Define the user we want to fetch toots from. 
    # Assume we follow this user on Mastodon:
    user = args.user                            if args.user else "@mobydick@mastodon.art"
    
    # Set the Mastodon instance URL
    mastodon_instance_url = args.instance       if args.instance else 'https://social.vivaldi.net'
    
    # Set the Mastodon API keys
    mastodon_client_id = args.client_id         if args.client_id     else os.getenv('MASTODON_CLIENT_ID')
    mastodon_client_secret = args.client_secret if args.client_secret else os.getenv('MASTODON_CLIENT_SECRET')
    mastodon_access_token = args.access_token   if args.access_token  else os.getenv('MASTODON_ACCESS_TOKEN')
    
    # Set the OpenAI access token
    openai_access_token = args.openai_token     if args.openai_token  else os.getenv('OPENAI_ACCESS_TOKEN')

    toot = args.toot                            if args.toot else None
    dry_run = args.dry_run                      if args.dry_run else False
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
        'dry_run': dry_run
    }
    config = Config(**config_dict)
    return config
            
if __name__ == "__main__":
    args = parse_command_line_args()
    config = create_config(args)
    translator = EmojiTranslator()
    translator.run(config)