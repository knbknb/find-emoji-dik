<!-- markdownlint-disable MD046 -->
# find-emoji-dik

Simple Command-Line Script for Bash/Linux.

The Python script `emojis-mobydick.py` will fetch the most recent toot from bot-account [@mobydick@botsin.space](https://social.vivaldi.net/@mobydick@botsin.space).

Then the script uses the GPT Large Language Model (LLM) to translate sentence fragments from the novel "Moby Dick" (posted by above-mentioned bot) into Emojis, and post that string of emojis as a new toot to the Mastodon API.

_This little Python project served to refresh my Python skills. It was also instructive for learning-by-doing LLM APIs._

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

Check your account if this was really published to your timeline.
