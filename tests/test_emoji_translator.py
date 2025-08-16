import unittest
import sys
import types
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Provide a minimal mock for the mastodon module used by emoji_translator
mock_mastodon = types.ModuleType("mastodon")
mock_mastodon.Mastodon = object
sys.modules.setdefault("mastodon", mock_mastodon)

# Provide a minimal mock for BeautifulSoup to avoid importing bs4
mock_bs4 = types.ModuleType("bs4")
class DummyBeautifulSoup:
    def __init__(self, text, parser):
        self._text = text
    def get_text(self):
        return self._text
mock_bs4.BeautifulSoup = DummyBeautifulSoup
sys.modules.setdefault("bs4", mock_bs4)

# Provide a minimal mock for dotenv functions used in emoji_translator
mock_dotenv = types.ModuleType("dotenv")
def fake_load_dotenv(*args, **kwargs):
    return True
def fake_find_dotenv(*args, **kwargs):
    return ""
mock_dotenv.load_dotenv = fake_load_dotenv
mock_dotenv.find_dotenv = fake_find_dotenv
sys.modules.setdefault("dotenv", mock_dotenv)

# Provide a minimal mock for requests module used by emoji_translator
mock_requests = types.ModuleType("requests")
def fake_request(method, url, headers=None, data=None):
    class Resp:
        def json(self):
            return {"choices": [{"message": {"content": ""}}]}
    return Resp()
mock_requests.request = fake_request
sys.modules.setdefault("requests", mock_requests)

from emoji_translator import EmojiTranslator

class TestEmojiTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = EmojiTranslator()

    def test_last_n_words_removes_trailing_period_when_short(self):
        result = self.translator.last_n_words("hello world.", n=5)
        self.assertEqual(result, "hello world")

    def test_last_n_words_longsentence(self):
        result = self.translator.last_n_words("Call me Ishmael said he.", n=4)
        self.assertEqual(result, "me Ishmael said he")

    def test_should_post_new_toot(self):
        result = self.translator.should_post({}, "hello", interval_days=120)
        self.assertTrue(result)

    def test_should_post_skip_recent(self):
        from datetime import datetime
        storage = {"hello": {"emoji": "🙂", "date": datetime.now().isoformat()}}
        result = self.translator.should_post(storage, "hello", interval_days=120)
        self.assertFalse(result)

    def test_should_post_after_interval(self):
        from datetime import datetime, timedelta
        old_date = (datetime.now() - timedelta(days=121)).isoformat()
        storage = {"hello": {"emoji": "🙂", "date": old_date}}
        result = self.translator.should_post(storage, "hello", interval_days=120)
        self.assertTrue(result)

    def test_split_attribution_no_attribution(self):
        translator = EmojiTranslator()
        text = "Hello world!\nThis is a test."
        main, attrib = translator.split_attribution(text)
        self.assertEqual(main, text)
        self.assertEqual(attrib, "")

    def test_split_attribution_with_attribution(self):
        translator = EmojiTranslator()
        text = "Line one.\nLine two.\n-- Author Name"
        expected_main = "Line one.\nLine two."
        expected_attrib = "-- Author Name"
        main, attrib = translator.split_attribution(text)
        self.assertEqual(main, expected_main)
        self.assertEqual(attrib, expected_attrib)

    def test_translate_to_emoji_sets_attribution(self):
        translator = EmojiTranslator()
        dummy_text = "Sample content.\n-- Test Author"
        # Call translate_to_emoji, which should set attribution
        translator.translate_to_emoji("http://example.com", "token123", dummy_text)
        self.assertEqual(translator.attribution, "-- Test Author")

if __name__ == "__main__":
    unittest.main()
