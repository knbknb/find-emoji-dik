#!/usr/bin/env python3
"""Quick test of the new moby_paragraph feature."""

import sys
sys.path.insert(0, 'src')

from moby_dick_parser import MobyDickParser

# Test the parser
parser = MobyDickParser('data/moby-dick-lowercase.txt')

# Get a random paragraph
paragraph_data = parser.get_random_paragraph()

if paragraph_data:
    print("Random paragraph selected:")
    print(f"Chapter {paragraph_data['chapter_num']}: {paragraph_data['chapter_title']}")
    print(f"Paragraph {paragraph_data['paragraph_num']}")
    print(f"\nOriginal text ({len(paragraph_data['text'])} chars):")
    print(paragraph_data['text'][:200] + "..." if len(paragraph_data['text']) > 200 else paragraph_data['text'])
    
    # Extract interesting fragment
    fragment = parser.extract_interesting_fragment(paragraph_data['text'])
    print(f"\nExtracted fragment ({len(fragment)} chars):")
    print(fragment)
else:
    print("Error: Could not extract paragraph")
