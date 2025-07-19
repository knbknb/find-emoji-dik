import unittest
import os
from static_fileparser import StaticFileParser

class TestStaticFileParser(unittest.TestCase):
    def setUp(self):
        self.test_file = 'data/test_static.txt'
        with open(self.test_file, 'w') as f:
            f.write('First paragraph.\n\nSecond paragraph.\n\nThird.')

    def tearDown(self):
        os.remove(self.test_file)

    def test_snippet_count(self):
        parser = StaticFileParser(self.test_file)
        self.assertEqual(len(parser.snippets), 3)

    def test_random_snippet_returns_value(self):
        parser = StaticFileParser(self.test_file)
        snippet = parser.get_random_snippet()
        self.assertIn(snippet, parser.snippets)

if __name__ == '__main__':
    unittest.main()
