
from PIL import Image, ImageOps, ImageEnhance
import pytesseract


def extract_text_from_image(uploaded_file):
    if uploaded_file is None:
        return ""

    uploaded_file.seek(0)

    with Image.open(uploaded_file) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        image = ImageOps.grayscale(image)
        image = ImageEnhance.Contrast(image).enhance(1.5)

        text = pytesseract.image_to_string(image, config="--psm 6")

    return text.strip()
