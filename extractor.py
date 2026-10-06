import pymupdf
import pytesseract
from PIL import Image


def extract_text_from_pdf(uploaded_file):
    uploaded_file.seek(0)

    pdf_bytes = uploaded_file.read()

    document = pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    text = ""

    for page in document:
        text += page.get_text() + "\n"

    document.close()

    return text


def extract_text_from_image(uploaded_file):
    uploaded_file.seek(0)

    image = Image.open(uploaded_file)

    text = pytesseract.image_to_string(image)

    return text
