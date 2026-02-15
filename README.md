<!-- markdownlint-disable MD046 -->
# find-emoji-dik

### Repository Overview

_find-emoji-dik_ is a Python project that fetches short text fragments from literature-themed Mastodon accounts or from text files in the `data/` directory, converts those fragments into emojis using an LLM API, and posts the emoji responses back to Mastodon.

_Why? This funny little Python project served to refresh my Python skills. I'm learning  AI-supported coding and  interacting with LLM APIs. Learning by doing._

This README explains the purpose and provides examples of expected output, requirements, and shell commands for invocation.

### Technical Overview

Simple Command-Line Script for Bash/Linux/Python.

The main script is `emojis-mobydick.py`. The script processes toots from literature-themed Mastodon accounts or from local text files in the `data/` directory.

Then the script uses a Large Language Model (LLM) to translate sentence fragments into Emojis, and posts the fragment+emojis as a new toot to the Mastodon Social Network via its REST API, using a `.env` file for API credentials.

## Call and Expected Output

### CLI Call

    source .venv/bin/activate  # Activate the virtual environment
    ./src/emojis-mobydick.py

(Read toots from Mastodon, parse most recent toot; post fragment to LLM API, let LLM translate to Emojis, process LLM response, post fragment+Emojis to own account)

You can fetch a random snippet from a text file stored in `data/` with:

    ./src/emojis-mobydick.py --data-file path/to/mark-twain-from-gutenberg.txt --signature "Mark Twain"

(Read random snippet from text file, let LLM translate to Emojis, process LLM response, post fragment+Emojis to own account)

You can also extract a random paragraph directly from the Moby Dick text file with:

    ./src/emojis-mobydick.py --moby-paragraph

(Extract random paragraph from Moby Dick, intelligently select an interesting sentence fragment from it, let LLM translate to Emojis, post fragment+Emojis with chapter and paragraph citation to own account)

In order to avoid duplicate posts, the script will check if the text fragment is already present in the local cache file `data/toot-storage.json`. If it is, the script will skip posting that fragment.

#### Fragment Extraction Strategy

When using the `--moby-paragraph` mode, the script intelligently extracts sentence fragments:

- **Short paragraphs (1-2 sentences)**: Posted as-is without modification
- **Longer paragraphs**: The script selects the most interesting 1-2 sentences based on length and content relevance (prioritizes sentences containing words like "whale", "sea", "ahab", "voyage", "death", etc.)

### Expected Output (Example)

Shell output

```text

  Last 4 words: whale was the symbol
  Chapter 42:The Whiteness of The Whale., Paragraph 31, Sentence 4
  Found in book!

  And of all these things the Albino whale was the symbol.:
  🔱🧩🎭📩⚪🐋🔣🎴
        -- Herman Melville (h/t @mobydick@mastodon.art)
  (Chapter 42: "The Whiteness of The Whale.", Paragraph 31, Sentence 4)
```

Note: The `@mobydick@mastodon.art` bot account has blocked this scraping account, so the script now primarily uses local text files or re-toots from other literature accounts instead.

#### Sideeffect: Post toot to Mastodon

If you have configured an account on the Mastodon social network, a toot with this text will be posted to your account:

```text
  And of all these things the Albino whale was the symbol.:
  🔱🧩🎭📩⚪🐋🔣🎴
        -- Herman Melville (h/t @mobydick@mastodon.art)
  (Chapter 42: "The Whiteness of The Whale.", Paragraph 31, Sentence 4)
```

Note that it is a bit shorter than the shell output.
Check your account if this was really published to your timeline.

## Requirements

- a Mastodon account, an OpenAI account
- API keys+secret for Mastodon, API key for OpenAI
- a local copy of the book "Moby Dick" in a text file. Here, `data/moby-dick-lowercase.txt`.
- Python: see `requirements.txt` file

### .env File

Put all your API credentials (Mastodon API, LLM API) into an `.env` file in the same directory as the script. The script will read the credentials from there. The `python-dotenv` module is used to read the `.env` file.  
I didn't include my `.env` file in this repo, so you have to create your own.

The `.env` file should look like this:

```text
# .env-example
MASTODON_CLIENT_ID='eykSIrJ...'
MASTODON_CLIENT_SECRET='-regoq...'
MASTODON_ACCESS_TOKEN='O9F_-UGf...'
OPENAI_ACCESS_TOKEN='sk-bx...'
```

Or use the command line options.

### Helper Scripts

To create a new virtual environment, you can use the built-in Python venv module:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Or use the helper script in `static/create_venv_mastodonapi.sh`.

## TODO

- ~~Keep refactoring the code, e.g., to make it more modular.~~
- ~~Make it a script that polls mastodon account of the @mobydick  bot account every n minutes, and posts new toots to our account.~~
  - ~~Make sure it doesn't post the same toot several times.~~
  - ~~Clearly handle edge-case when a text fragment was not found in the book (e.g. when punctuation or whitespace differences are interfering)~~
  - ~~Properly reply to the original toot, so that the thread is kept intact. (WON'T FIX, because the original bot account has blocked this account, so we can't reply to the original toots anymore)~~
- ~~Read from other literature accounts.~~
- ~~Include some literary works as static files that are read from the filesystem.~~
- ~~Rewrite this script to use the OpenAI client library instead of direct HTTP calls to the OpenAI REST API~~
- ~~Rewrite this script such that it works with other books, with other literature bots~~.
- ~~Rewrite this script such that it works with other LLMs~~ (WON'T FIX, because of the specific prompt engineering and response parsing that is currently implemented for OpenAI's API)
- Translate whole books into emojis, and post them to some social networks.
- Rewrite this such that it uses an agentic architecture, e.g. with a central agent that distributes tasks to worker agents, posting even more emojified quotes to all social networks.

## Tests

Unit Tests with _unittest_ or _pytest_, e.g.,  

```bash
# cd into repo root directory and run all tests:`
python -m unittest discover -s tests -p 'test_*.py'

# or with pytest:
PYTHONPATH=src find-emoji-dik/.venv/bin/python -m pytest tests/
```

System tests with bash and python:

See `static/tests/integration/` for some Python scripts that you can run to test the availability of the Mastodon API, the LLM API, and to make focused use of some command line options.

## Obsolete

I've looked at the original Emoji Dick crowdsourcing project as desribed in an [Arxiv paper](https://arxiv.org/pdf/1611.02027.pdf) from 2016. However that opus is available only as a PDF Document with emojis concatenated into larger PNG images.  
The original project is not available as a Python script, and the authors have not published the code. The original project was also created before the era of LLMs, so it is not directly compatible with the current state of the art in AI-supported emoji translation.
