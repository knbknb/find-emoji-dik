<!-- markdownlint-disable MD046 -->
# find-emoji-dik

### Repository Overview

_find-emoji-dik_ is a Python project that fetches short text fragments from literature-themed Mastodon accounts or from text files in the `data/` directory, converts those fragments into emojis using an LLM API, and posts the emoji responses back to Mastodon.

_Why? This funny little Python project served to refresh my Python skills. I'm learning  AI-supported coding and  interacting with LLM APIs. Learning by doing._

This README explains the purpose and provides examples of expected output, requirements, and shell commands for invocation.

### Technical Overview

Simple Command-Line Script for Bash/Linux/Python.

The main script is `emojis-mobydick.py`. The script will fetch the most recent toot from bot-account [@mobydick@mastodon.art](https://social.vivaldi.net/@mobydick@botsin.space) and from other literature accounts.

Then the script uses a Large Language Model (LLM) to translate sentence fragments from the novel "Moby Dick" (posted by above-mentioned bot) into Emojis, and post that string of emojis as a new toot to the Mastodon Social Network via its REST API, using a `.env` file for API credentials.

## Call and Expected Output

### CLI Call

    workon mastodon  # my virtualenv, created with virtualenvwrapper
    ./src/emojis-mobydick.py

(Read toots from Mastodon, parse most recent toot; post fragment to LLM API, let LLM translate to Emojis, process LLM response, post fragment+Emojis to own account)

You can fetch a random snippet from a text file stored in `data/` with:

    ./src/emojis-mobydick.py --data-file path/to/mark-twain-from-gutenberg.txt --signature "Mark Twain"

(Read random snippet from text file, let LLM translate to Emojis, process LLM response, post fragment+Emojis to own account)

In order to avoid duplicate posts, the script will check if the text fragment is already present in the local cache file `data/toot-storage.json`. If it is, the script will skip posting that fragment.

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

#### Sideeffect: Post toot to Mastodon

I you have configured an account on the Mastodon social network, a toot with this text will be posted to your account:

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
- the Mastodon account should follow the mobydick bot
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

Take a look at the files in the `static/` directory of this repo, e.g., to see how to create a Virtualenv.

## TODO

- ~~Keep refactoring the code, e.g., to make it more modular.~~
- ~~Make it a script that polls mastodon account of the @mobydick  bot account every n minutes, and posts new toots to our account.~~
  - ~~Make sure it doesn't post the same toot several times.~~
  - ~~Clearly handle edge-case when a text fragment was not found in the book (e.g. when punctuation or whitespace differences are interfering)~~
  - Properly reply to the original toot, so that the thread is kept intact.
- ~~Read from other literature accounts.~~
- ~~Include some literary works as static files that are read from the filesystem.~~
- Rewrite this script with other LLMs, ~~with other books, with other literature bots~~.
- Translate whole books into emojis, and post them to some social networks.
- Rewrite this such that it uses an agentic architecture, e.g. with a central agent that distributes tasks to worker agents, posting even more emojified quotes to all social networks.

## Tests

(under construction).
Test with pytest, e.g.,  
`pytest-3 unittest_mobydick_strings.py`  
or  
`python -m unittest discover -s tests -p 'test_*.py'`

## Obsolete

I've looked at the original emojidick community project, but that book is available only as a PDF with emojis  concatenated into larger images. There is some code left for parsing the PDF, but I'll delete it later.
