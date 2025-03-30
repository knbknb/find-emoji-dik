import unittest
import os
from moby_dick_parser import MobyDickParser  # Assuming moby_dick_parser.py is in the same directory

class TestMobyDickParser(unittest.TestCase):

    def setUp(self):
        # Create a dummy file for testing
        self.test_file_content = """CHAPTER 1. Loomings

Call me Ishmael. Some years ago--never mind how long precisely--having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world. It is a way I have of driving off the spleen and regulating the circulation.

CHAPTER 2. The Carpet-Bag

Stowing my bag in the coach, I went to the inn.

CHAPTER 3. The Spouter-Inn

Entering that gable-ended Spouter-Inn, you found yourself in a wide, low, straggling entry with old-fashioned wainscots, reminding one of the bulwarks of some condemned old craft.

"""
        self.test_file_path = "test_moby_dick.txt"
        with open(self.test_file_path, "w") as f:
            f.write(self.test_file_content)
        
        self.parser = MobyDickParser(self.test_file_path)

    def tearDown(self):
        # Remove the dummy file after testing
        os.remove(self.test_file_path)

    def test_parse_into_chapters(self):
        chapters = self.parser.parse_into_chapters()
        self.assertEqual(len(chapters), 3)
        self.assertEqual(chapters[0][0], "1. Loomings")
        self.assertTrue("Call me Ishmael" in chapters[0][1])
        self.assertEqual(chapters[1][0], "2. The Carpet-Bag")
        self.assertTrue("Stowing my bag" in chapters[1][1])
        self.assertEqual(chapters[2][0], "3. The Spouter-Inn")
        self.assertTrue("Entering that gable-ended" in chapters[2][1])

    def test_parse_into_paragraphs(self):
        paragraphs_per_chapter = self.parser.parse_into_paragraphs()
        self.assertEqual(len(paragraphs_per_chapter), 3)
        self.assertEqual(len(paragraphs_per_chapter[0]), 1)
        self.assertEqual(len(paragraphs_per_chapter[1]), 1)
        self.assertEqual(len(paragraphs_per_chapter[2]), 1)
        self.assertTrue("Call me Ishmael" in paragraphs_per_chapter[0][0])
        self.assertTrue("Stowing my bag" in paragraphs_per_chapter[1][0])
        self.assertTrue("Entering that gable-ended" in paragraphs_per_chapter[2][0])

    def test_parse_into_sentences(self):
        sentences_per_chapter_paragraph = self.parser.parse_into_sentences()
        self.assertEqual(len(sentences_per_chapter_paragraph), 3)
        self.assertEqual(len(sentences_per_chapter_paragraph[0]), 1)
        self.assertEqual(len(sentences_per_chapter_paragraph[1]), 1)
        self.assertEqual(len(sentences_per_chapter_paragraph[2]), 1)
        self.assertEqual(len(sentences_per_chapter_paragraph[0][0]), 3)
        self.assertEqual(len(sentences_per_chapter_paragraph[1][0]), 1)
        self.assertEqual(len(sentences_per_chapter_paragraph[2][0]), 1)
        self.assertEqual(sentences_per_chapter_paragraph[0][0][0], "Call me Ishmael")
        self.assertEqual(sentences_per_chapter_paragraph[0][0][1], "Some years ago--never mind how long precisely--having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world")
        self.assertEqual(sentences_per_chapter_paragraph[1][0][0], "Stowing my bag in the coach, I went to the inn")
        self.assertEqual(sentences_per_chapter_paragraph[2][0][0], "Entering that gable-ended Spouter-Inn, you found yourself in a wide, low, straggling entry with old-fashioned wainscots, reminding one of the bulwarks of some condemned old craft")

    def test_find_fragment_found(self):
        chapter_num, chapter_title, paragraph_num, sentence_num = self.parser.find_fragment("Call me Ishmael")
        self.assertEqual(chapter_num, 1)
        self.assertEqual(chapter_title, "Loomings")
        self.assertEqual(paragraph_num, 1)
        self.assertEqual(sentence_num, 1)

    def test_find_fragment_not_found(self):
        chapter_num, chapter_title, paragraph_num, sentence_num = self.parser.find_fragment("This fragment is not in the text")
        self.assertIsNone(chapter_num)
        self.assertIsNone(chapter_title)
        self.assertIsNone(paragraph_num)
        self.assertIsNone(sentence_num)

    def test_find_fragment_in_second_chapter(self):
        chapter_num, chapter_title, paragraph_num, sentence_num = self.parser.find_fragment("Stowing my bag")
        self.assertEqual(chapter_num, 2)
        self.assertEqual(chapter_title, "The Carpet-Bag")
        self.assertEqual(paragraph_num, 1)
        self.assertEqual(sentence_num, 1)

    def test_find_fragment_in_third_chapter(self):
        chapter_num, chapter_title, paragraph_num, sentence_num = self.parser.find_fragment("Entering that gable-ended")
        self.assertEqual(chapter_num, 3)
        self.assertEqual(chapter_title, "The Spouter-Inn")
        self.assertEqual(paragraph_num, 1)
        self.assertEqual(sentence_num, 1)

if __name__ == '__main__':
    unittest.main()
