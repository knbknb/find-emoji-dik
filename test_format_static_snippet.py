import importlib.util
import unittest
import os

module_name = 'emojis_mobydick'
file_path = os.path.join(os.path.dirname(__file__), 'emojis-mobydick.py')
spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestFormatStaticSnippet(unittest.TestCase):
    def test_with_signature(self):
        result = module.format_static_snippet('hello', '🙂', 'Author')
        self.assertEqual(result, 'hello:\n🙂\n        -- Author')

    def test_without_signature(self):
        result = module.format_static_snippet('hello', '🙂')
        self.assertEqual(result, 'hello:\n🙂')

if __name__ == '__main__':
    unittest.main()
