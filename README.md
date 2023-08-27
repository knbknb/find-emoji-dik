# find-emoji-dik

Use LLM APis to translate sentence fragments from novel Moby Dick into emojis, and Post tit to the Mastodon API

Simple Command-Line Script for Bash/Linux

## Call and Expected Output

### CLI Call

    ./emojis-mobydick.py 

### Expected Output (Example)

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