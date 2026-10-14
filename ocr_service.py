
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import pytesseract
import io


def extract_text_from_image(uploaded_file):
    if uploaded_file is None:
        return ""

    try:
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()

        if not image_bytes:
            return ""

        image = Image.open(io.BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")

        # Enlarge small images to improve character recognition.
        if image.width < 1600:
            scale = 1600 / image.width
            image = image.resize(
                (1600, int(image.height * scale))
            )

        # Improve contrast and reduce minor noise.
        image = ImageOps.grayscale(image)
        image = ImageOps.autocontrast(image)
        image = ImageEnhance.Contrast(image).enhance(1.5)
        image = image.filter(ImageFilter.SHARPEN)

        # Page segmentation mode 6 works well for many text documents.
        text = pytesseract.image_to_string(
            image,
            config="--oem 3 --psm 6"
        )

        return text.strip()

    except Exception as error:
        raise ValueError(
            f"Could not extract text from this image: {error}"
        ) from error
