<!-- markdownlint-disable MD046 -->
# find-emoji-dik

Simple Command-Line Script for Bash/Linux.

The Python script `emojis-mobydick.py` will fetch the most recent toot from bot-account [@mobydick@botsin.space](https://social.vivaldi.net/@mobydick@botsin.space).

Then the script uses the GPT Large Language Model (LLM) to translate sentence fragments from the novel "Moby Dick" (posted by above-mentioned bot) into Emojis, and post that string of emojis as a new toot to the Mastodon API.

_This funny little Python project served to refresh my Python skills. I'm learning to interact with LLM APIs, learning by doing._

## Call and Expected Output

### CLI Call

    ./emojis-mobydick.py 

(Read toots from Mastodon, parse most recent toot; post fragment to LLM API, let LLM translate to Emojis, process LLM response, post fragment+Emojis to own account)

### Expected Output (Example)

Shell output

```text

  Last 4 words: whale was the symbol
  Chapter 42:The Whiteness of The Whale., Paragraph 31, Sentence 4
  Found in book!
  
  And of all these things the Albino whale was the symbol.:
  🔱🧩🎭📩⚪🐋🔣🎴
        -- Herman Melville (h/t @mobydick@botsin.space)
  (Chapter 42: "The Whiteness of The Whale.", Paragraph 31, Sentence 4)
```

#### Sideeffect: Post toot to Mastodon

I you have configured an account on the Mastodon social network, a toot with this text will be posted to your account:

```text
  And of all these things the Albino whale was the symbol.:
  🔱🧩🎭📩⚪🐋🔣🎴
        -- Herman Melville (h/t @mobydick@botsin.space)
  (Chapter 42: "The Whiteness of The Whale.", Paragraph 31, Sentence 4)
```

Note that it is a bit shorter than the shell output.
Check your account if this was really published to your timeline.

## Requirements

- a Mastodon account, an OpenAI account
- API keys+secret for Mastodon, API key for OpenAI
- the Mastodon account should follow the mobydick bot
- a local copy of the book "Moby Dick" in a text file
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

- Keep refactoring the code, e.g., to make it more modular.
- Make it a script that polls mastodon account of the @mobydick  bot account every n minutes, and posts new toots to our account.
  - Make sure it doesn't post the same toot several times.
  - Clearly handle edge-case when a text fragment was not found in the book (e.g. when punctuation or whitespace differences are interfering)
  - Properly reply to the original toot, so that the thread is kept intact.
- Rewrite this script with other LLMs, with other books, with other bots.
- Translate the whole book into emojis, and post it to all social networks.
