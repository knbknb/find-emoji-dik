import unittest
import sys
import types
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Provide a minimal mock for the mastodon module used by emoji_translator
mock_mastodon = types.ModuleType("mastodon")
mock_mastodon.Mastodon = object  # type: ignore[attr-defined]
sys.modules.setdefault("mastodon", mock_mastodon)

# Provide a minimal mock for BeautifulSoup to avoid importing bs4
mock_bs4 = types.ModuleType("bs4")
class DummyBeautifulSoup:
    def __init__(self, text, parser):
        self._text = text
    def get_text(self):
        return self._text
mock_bs4.BeautifulSoup = DummyBeautifulSoup  # type: ignore[attr-defined]
sys.modules.setdefault("bs4", mock_bs4)

# Provide a minimal mock for dotenv functions used in emoji_translator
mock_dotenv = types.ModuleType("dotenv")
def fake_load_dotenv(*args, **kwargs):
    return True
def fake_find_dotenv(*args, **kwargs):
    return ""
mock_dotenv.load_dotenv = fake_load_dotenv  # type: ignore[attr-defined]
mock_dotenv.find_dotenv = fake_find_dotenv  # type: ignore[attr-defined]
sys.modules.setdefault("dotenv", mock_dotenv)


# Provide a minimal mock for requests module used by emoji_translator
mock_requests = types.ModuleType("requests")
def fake_request(method, url, headers=None, data=None):
    class Resp:
        def json(self):
            return {"choices": [{"message": {"content": "😊"}}]}
    return Resp()
mock_requests.request = fake_request  # type: ignore[attr-defined]
sys.modules.setdefault("requests", mock_requests)

# Minimal shim for pydantic so tests don't require the real package
import types as _types2
shim_pydantic = _types2.ModuleType("pydantic")
class _BaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
def _model_validator(mode=None):
    def decorator(fn):
        return fn
    return decorator
shim_pydantic.BaseModel = _BaseModel  # type: ignore[attr-defined]
shim_pydantic.model_validator = _model_validator  # type: ignore[attr-defined]
shim_pydantic.field_validator = _model_validator  # type: ignore[attr-defined]
shim_pydantic.HttpUrl = str  # type: ignore[attr-defined]
sys.modules.setdefault("pydantic", shim_pydantic)

from emoji_translator import EmojiTranslator
from app_config import AppConfig

class TestEmojiTranslatorAttribution(unittest.TestCase):
    def setUp(self):
        self.translator = EmojiTranslator(AppConfig(dry_run=True))
        self.possible_emojis = ["😊", "😀"]

    def test_split_attribution_no_attribution(self):
        text = "Just some text\nwith multiple lines."
        main, attrib = self.translator.split_attribution(text)
        self.assertEqual(main, text)
        self.assertEqual(attrib, "")

    def test_split_attribution_with_attribution(self):
        text = "Meaningful sentence\n-- John Doe"
        main, attrib = self.translator.split_attribution(text)
        self.assertEqual(main, "Meaningful sentence")
        self.assertEqual(attrib, "-- John Doe")

    def test_split_attribution_strips_hashtags(self):
        text = "Meaningful sentence\n-- John Doe #quote #test"
        main, attrib = self.translator.split_attribution(text)
        self.assertEqual(main, "Meaningful sentence")
        self.assertEqual(attrib, "-- John Doe")

    def test_split_attribution_ignores_trailing_hashtags(self):
        text = "Meaningful sentence\n-- John Doe\n#quote #test"
        main, attrib = self.translator.split_attribution(text)
        self.assertEqual(main, "Meaningful sentence")
        self.assertEqual(attrib, "-- John Doe")

    def test_translate_to_emoji_sets_attribution_with_author(self):
        text = "Hello world\n-- Jane"
        emoji, attrib = self.translator.translate_to_emoji_openai("token123", text)
        self.assertIn(emoji, self.possible_emojis)
        self.assertEqual(attrib, "-- Jane")
        self.assertEqual(self.translator.attribution, "-- Jane")

    def test_translate_to_emoji_cleans_hashtagged_attribution(self):
        text = "Hello world\n-- Jane #tag1 #tag2"
        emoji, attrib = self.translator.translate_to_emoji_openai("token123", text)
        self.assertIn(emoji, self.possible_emojis)
        self.assertEqual(attrib, "-- Jane")
        self.assertEqual(self.translator.attribution, "-- Jane")

    def test_translate_to_emoji_ignores_trailing_hashtags(self):
        text = "Hello world\n-- Jane\n#tag1 #tag2"
        emoji, attrib = self.translator.translate_to_emoji_openai("token123", text)
        self.assertIn(emoji, self.possible_emojis)
        self.assertEqual(attrib, "-- Jane")
        self.assertEqual(self.translator.attribution, "-- Jane")

    def test_translate_to_emoji_sets_attribution_without_author(self):
        text = "Hello world"
        emoji, attrib = self.translator.translate_to_emoji_openai("token123", text)
        self.assertIn(emoji, self.possible_emojis)
        self.assertEqual(attrib, "")
        self.assertEqual(self.translator.attribution, "")

if __name__ == "__main__":
    unittest.main()
