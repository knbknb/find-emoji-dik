import re
import random

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

    def get_random_paragraph(self):
        """Get a random paragraph from the book and its chapter information."""
        # Flatten all paragraphs with their chapter info
        all_paragraphs = []
        for chapter_num, paragraphs in enumerate(self.paragraphs_per_chapter):
            for paragraph_num, paragraph in enumerate(paragraphs):
                chapter_title = self.chapters[chapter_num][0]
                chapter_title = re.sub(r'^\d+\.\s*', '', chapter_title)
                all_paragraphs.append({
                    'text': paragraph,
                    'chapter_num': chapter_num + 1,
                    'chapter_title': chapter_title,
                    'paragraph_num': paragraph_num + 1
                })
        
        if not all_paragraphs:
            return None
        
        return random.choice(all_paragraphs)

    def extract_interesting_fragment(self, paragraph_text, max_sentences=2):
        """Extract an interesting sentence fragment from a paragraph.
        
        For longer paragraphs, extract 1-2 sentences that seem most interesting
        based on length and content. For short paragraphs, return as-is.
        """
        # Split into sentences
        sentence_delimiters = re.compile(r'([.!?])\s+')
        parts = sentence_delimiters.split(paragraph_text)
        
        # Reconstruct sentences with their punctuation
        sentences = []
        for i in range(0, len(parts) - 1, 2):
            if i + 1 < len(parts):
                sentences.append(parts[i] + parts[i + 1])
        # Add last part if it exists and wasn't paired
        if len(parts) % 2 == 1 and parts[-1].strip():
            sentences.append(parts[-1])
        
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # If paragraph is short (1-2 sentences), return as-is
        if len(sentences) <= 2:
            return paragraph_text
        
        # For longer paragraphs, find interesting sentences
        # Criteria: prefer longer sentences with interesting words
        interesting_words = [
            'whale', 'sea', 'ship', 'ocean', 'captain', 'ahab', 'moby',
            'ishmael', 'harpoon', 'voyage', 'death', 'soul', 'nature',
            'mysterious', 'strange', 'terror', 'wonder', 'deep', 'eternal'
        ]
        
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = len(sentence)  # Base score on length
            # Bonus for interesting words
            lower_sentence = sentence.lower()
            for word in interesting_words:
                if word in lower_sentence:
                    score += 50
            scored_sentences.append((score, i, sentence))
        
        # Sort by score and take top 1-2 sentences
        scored_sentences.sort(reverse=True)
        selected_sentences = scored_sentences[:max_sentences]
        
        # Sort selected sentences by their original position to maintain order
        selected_sentences.sort(key=lambda x: x[1])
        
        # Reconstruct the fragment
        fragment = ' '.join([s[2] for s in selected_sentences])
        return fragment


if __name__ == "__main__":
    file_path = './data/moby-dick-lowercase.txt'
    parser = MobyDickParser(file_path)
    
    fragment = input("Please enter a sentence fragment to search for: ")
    chapter_num, chapter_title, paragraph_num, sentence_num = parser.find_fragment(fragment)

    if chapter_num:
        print(f"Found in Chapter {chapter_num} ({chapter_title}), Paragraph {paragraph_num}, Sentence {sentence_num}")
    else:
        print("Fragment not found.")

