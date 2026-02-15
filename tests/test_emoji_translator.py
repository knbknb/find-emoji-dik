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
            return {"output": [{"content": [{"type": "output_text", "text": "😀"}]}]}
    return Resp()
mock_requests.request = fake_request  # type: ignore[attr-defined]
sys.modules.setdefault("requests", mock_requests)

# Provide a minimal mock for openai SDK used by emoji_translator
mock_openai = types.ModuleType("openai")

class DummyOpenAIResponse:
    def __init__(self, output_text="😀"):
        self.output_text = output_text

    def model_dump(self):
        return {
            "output": [
                {"content": [{"type": "output_text", "text": self.output_text}]}
            ]
        }


class DummyResponsesAPI:
    def create(self, **kwargs):
        return DummyOpenAIResponse(output_text="😀")


class DummyOpenAI:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.responses = DummyResponsesAPI()


mock_openai.OpenAI = DummyOpenAI  # type: ignore[attr-defined]
sys.modules.setdefault("openai", mock_openai)

# Minimal shim for pydantic so tests don't require the real package
shim_pydantic = types.ModuleType("pydantic")
class _BaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
def _model_validator(mode=None):
    def decorator(fn):
        return fn
    return decorator
def _Field(**kwargs):
    return kwargs.get("default")
shim_pydantic.BaseModel = _BaseModel  # type: ignore[attr-defined]
shim_pydantic.model_validator = _model_validator  # type: ignore[attr-defined]
shim_pydantic.field_validator = _model_validator  # type: ignore[attr-defined]
shim_pydantic.Field = _Field  # type: ignore[attr-defined]
shim_pydantic.HttpUrl = str  # type: ignore[attr-defined]
sys.modules.setdefault("pydantic", shim_pydantic)

from emoji_translator import EmojiTranslator
from app_config import AppConfig

class TestEmojiTranslator(unittest.TestCase):
    def setUp(self):
        self.translator = EmojiTranslator(AppConfig(dry_run=True))
        self.possible_emojis = ["😊", "😀"]

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
        translator = EmojiTranslator(AppConfig(dry_run=True))
        text = "Hello world!\nThis is a test."
        main, attrib = translator.split_attribution(text)
        self.assertEqual(main, text)
        self.assertEqual(attrib, "")

    def test_split_attribution_with_attribution(self):
        translator = EmojiTranslator(AppConfig(dry_run=True))
        text = "Line one.\nLine two.\n-- Author Name"
        expected_main = "Line one.\nLine two."
        expected_attrib = "-- Author Name"
        main, attrib = translator.split_attribution(text)
        self.assertEqual(main, expected_main)
        self.assertEqual(attrib, expected_attrib)

    def test_translate_to_emoji_sets_attribution(self):
        translator = EmojiTranslator(AppConfig(dry_run=True))
        dummy_text = "Sample content.\n-- Test Author"
        # Call translate_to_emoji, which should set attribution
        translator.translate_to_emoji_openai("token123", dummy_text)
        self.assertEqual(translator.attribution, "-- Test Author")

    def test_translate_to_emoji_returns_emojis_from_responses(self):
        translator = EmojiTranslator(AppConfig(dry_run=True))
        emoji, extra = translator.translate_to_emoji_openai( "token123", "Hello world")
        self.assertIn(emoji, self.possible_emojis)
        self.assertEqual(extra, "")

if __name__ == "__main__":
    unittest.main()
