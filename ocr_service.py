
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import pytesseract
import io


def extract_text_from_image(uploaded_file):
    try:
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()

        if not image_bytes:
            raise ValueError("The uploaded image is empty.")

        image = Image.open(io.BytesIO(image_bytes))
        image.load()
        image = ImageOps.exif_transpose(image).convert("RGB")

        # Improve image readability for OCR
        if image.width < 1600:
            scale = 1600 / image.width
            image = image.resize(
                (1600, int(image.height * scale)),
                Image.Resampling.LANCZOS
            )

        image = ImageOps.grayscale(image)
        image = ImageOps.autocontrast(image)
        image = ImageEnhance.Contrast(image).enhance(2)
        image = image.filter(ImageFilter.SHARPEN)

        text = pytesseract.image_to_string(
            image,
            config="--oem 3 --psm 6"
        )

        uploaded_file.seek(0)

        if not text.strip():
            raise ValueError(
                "OCR returned no text. Try a clear, straight image "
                "with readable printed text."
            )

        return text.strip()

    except Exception as error:
        uploaded_file.seek(0)
        raise RuntimeError(
            f"Image text extraction failed: {error}"
        ) from error
