#!/usr/bin/env bash
python3 -m venv mastodon_mobydick_emoji
#
## Activate the virtual environment
source mastodon_mobydick_emoji/bin/activate
#
## Install the necessary Python libraries
pip install Mastodon.py python-dotenv

# When you're done, you can deactivate the virtual environment
deactivate