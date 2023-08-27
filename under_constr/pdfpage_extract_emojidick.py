# extract emojis from a PDF, from embedded PNGs
# PDF is Emoji Dick
# knb 2023
import fitz
import io
import os
import subprocess
import re

from PIL import Image

image_dir = './data/images/'
# Create the directory if it doesn't exist
os.makedirs(image_dir, exist_ok=True)

def extract_images_fitz(pdf_path):
    images = []
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        for img_index in doc.get_page_images(page_num):
            xref = img_index[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            images.append(image)
    return images


# Function to save images as PNG files in the specified directory
def save_images_to_png(images, directory):
    file_paths = []
    for idx, image in enumerate(images):
        file_path = os.path.join(directory, f"emoji_{idx}.png")
        image.save(file_path, format="PNG")
        file_paths.append(file_path)
    return file_paths

chapter = input("Please enter Chapter number to search for: ")

# pdfgrep -pi "Chapter.*99" data/emojidick.pdf  | cut -d: -f1
pdf_path = './data/emojidick.pdf'

chapter_rx = 'C\sh\sa\sp\st\se\sr ' + chapter

# Run pdfgrep command and capture output
pdfgrep_page = subprocess.check_output(['pdfgrep', '-Ppi', chapter_rx, pdf_path])

# Split output by colon and get first field
pdfgrep_lines = pdfgrep_page.decode().split('\n')
pdfgrep_page_f = [line.split(':')[0] for line in pdfgrep_lines]
pdfgrep_page_f = int(pdfgrep_page_f[0])
pdfgrep_page_l = pdfgrep_page_f + 6
print([chapter, pdfgrep_page_f, pdfgrep_page_l])

output_file = f"data/emojidick_ch{chapter}p{pdfgrep_page_f}-p{pdfgrep_page_l}-%d.pdf"
pdfgrep_page_pdf = subprocess.check_output(['pdfseparate', 
                                            '-f', str(pdfgrep_page_f), 
                                            '-l', str(pdfgrep_page_l), 
                                            'data/emojidick.pdf', 
                                            output_file])





# Extracting images using the fitz library
images_fitz = extract_images_fitz(pdf_path)

# Saving the images extracted from the target page as PNG files
saved_image_paths = save_images_to_png(images_fitz, image_dir)

# Displaying the first few images (if any) to confirm they are emojis
print(images_fitz[:5]) if images_fitz else "No images found."

#"NEEZES)--bless my soul, it won't let me speak!!is is what an old fellow gets now for working in dead lumber.Saw a live tree, and you don't get this dust; amputate a live bone, and you don't get it (SNEEZES). Come, come,you old Smut, there, bear a hand, and let's have that ferule and buckle-screw; I'll be ready for them presently.%',"