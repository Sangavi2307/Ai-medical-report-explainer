
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import pytesseract
import pymupdf
import io


def extract_text_from_image(uploaded_file):
    if uploaded_file is None:
        return ""

    uploaded_file.seek(0)
    image = Image.open(uploaded_file).convert("RGB")

    # Improve readability before OCR.
    image = ImageOps.grayscale(image)
    image = ImageEnhance.Contrast(image).enhance(1.7)
    image = image.filter(ImageFilter.SHARPEN)

    return pytesseract.image_to_string(
        image,
        config="--psm 6"
    ).strip()


def extract_text_from_scanned_pdf(uploaded_file):
    if uploaded_file is None:
        return ""

    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()
    page_texts = []

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
        for page in pdf:
            # Render page to an image for OCR.
            pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
            image_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            image = ImageOps.grayscale(image)
            image = ImageEnhance.Contrast(image).enhance(1.7)

            text = pytesseract.image_to_string(
                image,
                config="--psm 6"
            )
            page_texts.append(text)

    return "\n".join(page_texts).strip()
