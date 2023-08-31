#!/usr/bin/env python3
from mastodon import Mastodon
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv, find_dotenv
import os
import json
from moby_dick_parser import MobyDickParser

# Load .env file with API keys and credentials
load_dotenv(find_dotenv())

##### 
#  Some constants needed in various places inside code
#####
file_path = './data/moby-dick-lowercase.txt'
toot_storage_file = 'data/toot_storage.json'
# Define the user we want to fetch toots from. 
# Assume we follow this user on Mastodon:
user = "@mobydick@botsin.space"
# Fetch the most recent toot ID
mastodon_instance_url = 'https://social.vivaldi.net'
toot_fragment_1 = "        -- Herman Melville (h/t @mobydick@botsin.space)"

# Define Mastodon API keys, for posting and polling the mobydick account's toots
mastodon_client_id = os.getenv('MASTODON_CLIENT_ID')
mastodon_client_secret = os.getenv('MASTODON_CLIENT_SECRET')
mastodon_access_token = os.getenv('MASTODON_ACCESS_TOKEN')
# Define OpenAI API keys, for translation
openai_access_token = os.getenv('OPENAI_ACCESS_TOKEN')
translate_service_url = "https://api.openai.com/v1/chat/completions"
##### 
#  End constants 
#####



# Create a dictionary to serve as the persistent storage for the toots:
toot_storage = {}
most_recent_toot_id = None
 
# Create API object
api = Mastodon(
    client_id=mastodon_client_id,
    client_secret=mastodon_client_secret,
    access_token=mastodon_access_token,
    api_base_url=mastodon_instance_url
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


toot_storage = load_toot_storage(toot_storage_file)

def translate_to_emoji(url, openai_access_token = "openai_access_token", text = "🐳"):
    """Translate text to emojis and store the result in toot_storage."""
    # It should take a string of text and return a string of emojis
    # Example:
    # They say that men who have seen the world, thereby become quite at ease in manner, quite self-possessed in company.
    if text in toot_storage:
        return toot_storage[text]
    payload = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "user",
                "content": "translate the following text into emojis: '%s"
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
        "Accept" : "application/json"
    }
    headers['Authorization'] = headers['Authorization'] % openai_access_token
    response = requests.request("POST", url, headers=headers, data=payload_json)
    
    emoji_text = response.json()['choices'][0]['message']['content']
    toot_storage[text] = emoji_text
    save_toot_storage(toot_storage_file, toot_storage)
    
    return emoji_text 


# Fetch the most recent toots from the '@mobydick' user
mobydick = api.account_search(user, following=True)[0]

toots = api.account_statuses(mobydick.id, limit=1, since_id=most_recent_toot_id)
if toots:
    most_recent_toot = toots[0]
    most_recent_toot_id = most_recent_toot.id
    # Fetch the text of the toot
    text = most_recent_toot.content
    # strip the html tag(s)
    soup = BeautifulSoup(text, 'html.parser')
    fragment = soup.get_text()
    # find the fragment in the book
    toot = fragment
    print(toot)
    # fragment = 'stubb and flask mounted on them'
    n_words = 4
    fragment = last_n_words(fragment.lower(), n_words)
    parser = MobyDickParser(file_path)
    print(f"Last {n_words} words: {fragment}")
    chapter_num, chapter_title, paragraph_num, sentence_num = parser.find_fragment(fragment)
    print(f"Chapter {chapter_num}:{chapter_title}, Paragraph {paragraph_num}, Sentence {sentence_num}")
    # Translate the toot into emojis
    emoji_toot = translate_to_emoji(translate_service_url, openai_access_token, toot) 
    # if found in book, add the citation
    emoji_toot = toot + ":\n" + emoji_toot + "\n" + toot_fragment_1
    # print(emoji_toot)
    if chapter_num:
        print("Found in book!")
        emoji_toot = f"{emoji_toot}\n(Chapter {chapter_num}: \"{chapter_title}\", Paragraph {paragraph_num}, Sentence {sentence_num})"
    # Post the emoji toot
    if emoji_toot:
        print(emoji_toot)
        api.toot(emoji_toot)
    else:
        print("No emoji toot found.")
# Wait for a while before polling again
#time.sleep(60)
