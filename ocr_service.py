
from PIL import Image, ImageOps
import pytesseract


def extract_text_from_image(uploaded_file):
    """Extract text from a medical report image using Tesseract OCR."""
    try:
        uploaded_file.seek(0)

        with Image.open(uploaded_file) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")

            # Enlarge small images to help OCR.
            if image.width < 1200:
                scale = 1200 / image.width
                new_size = (
                    1200,
                    max(1, int(image.height * scale))
                )
                image = image.resize(new_size)

            text = pytesseract.image_to_string(
                image,
                config="--psm 6"
            )

        return text.strip()

    except Exception as exc:
        raise RuntimeError(
            f"Could not read the image: {type(exc).__name__}"
        ) from exc
