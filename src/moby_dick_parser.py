import re

class MobyDickParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.chapters = self.parse_into_chapters()
        self.paragraphs_per_chapter = self.parse_into_paragraphs()
        self.sentences_per_chapter_paragraph = self.parse_into_sentences()

    def parse_into_chapters(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            raw_chapters = re.split(r'\bCHAPTER\b', text)
            chapters = []
            for raw_chapter in raw_chapters:
                lines = raw_chapter.strip().split('\n')
                title = lines[0].strip() if lines else ""
                content = '\n'.join(lines[1:]).strip()
                chapters.append((title, content))
            chapters = [chapter for chapter in chapters if chapter[1]]
        return chapters

    def parse_into_paragraphs(self):
        paragraphs_per_chapter = []
        for _, content in self.chapters:
            paragraphs = content.split('\n\n')
            paragraphs = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]
            paragraphs_per_chapter.append(paragraphs)
        return paragraphs_per_chapter

    def parse_into_sentences(self):
        sentences_per_chapter_paragraph = []
        sentence_delimiters = re.compile(r'[.!?]')
        for paragraphs in self.paragraphs_per_chapter:
            sentences_per_paragraph = []
            for paragraph in paragraphs:
                sentences = sentence_delimiters.split(paragraph)
                sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
                sentences_per_paragraph.append(sentences)
            sentences_per_chapter_paragraph.append(sentences_per_paragraph)
        return sentences_per_chapter_paragraph



    def find_fragment(self, fragment):
        for chapter_num, paragraphs in enumerate(self.sentences_per_chapter_paragraph):
            for paragraph_num, sentences in enumerate(paragraphs):
                for sentence_num, sentence in enumerate(sentences):
                    if fragment in sentence:
                        chapter_title = self.chapters[chapter_num][0]
                        chapter_title = re.sub(r'^\d+\.\s*', '', chapter_title)
                        return chapter_num + 1, chapter_title, paragraph_num + 1, sentence_num + 1
        return None, None, None, None


if __name__ == "__main__":
    file_path = './data/moby-dick-lowercase.txt'
    parser = MobyDickParser(file_path)
    
    fragment = input("Please enter a sentence fragment to search for: ")
    chapter_num, chapter_title, paragraph_num, sentence_num = parser.find_fragment(fragment)

    if chapter_num:
        print(f"Found in Chapter {chapter_num} ({chapter_title}), Paragraph {paragraph_num}, Sentence {sentence_num}")
    else:
        print("Fragment not found.")

