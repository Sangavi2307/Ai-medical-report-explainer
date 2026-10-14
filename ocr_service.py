import io

import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import pymupdf


def _ocr_image(image):
    image = ImageOps.grayscale(image)
    image = ImageEnhance.Contrast(image).enhance(1.5)
    return pytesseract.image_to_string(image, config="--psm 6").strip()


def extract_text_from_image(uploaded_file):
    if uploaded_file is None:
        return ""

    uploaded_file.seek(0)
    content = uploaded_file.read()

    if not content:
        return ""

    with Image.open(io.BytesIO(content)) as image:
        return _ocr_image(image.copy())


def extract_text_from_scanned_pdf(uploaded_file):
    if uploaded_file is None:
        return ""

    uploaded_file.seek(0)
    content = uploaded_file.read()

    if not content:
        return ""

    extracted_pages = []

    with pymupdf.open(stream=content, filetype="pdf") as document:
        for page in document:
            text = page.get_text("text").strip()

            # Use OCR when a page contains little or no selectable text.
            if len(text) < 20:
                pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
                image_bytes = pixmap.tobytes("png")

                with Image.open(io.BytesIO(image_bytes)) as image:
                    text = _ocr_image(image.copy())

            extracted_pages.append(text)

    return "\n\n".join(extracted_pages).strip()
