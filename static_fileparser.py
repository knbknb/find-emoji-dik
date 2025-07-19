import random

class StaticFileParser:
    """Parse a static text file and return random snippets."""
    def __init__(self, file_path):
        self.file_path = file_path
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        # Split text by blank lines
        blocks = text.split('\n\n')
        self.snippets = [block.replace('\n', ' ').strip() for block in blocks if block.strip()]

    def get_random_snippet(self):
        """Return a random snippet from the file."""
        if not self.snippets:
            return ""
        return random.choice(self.snippets)
