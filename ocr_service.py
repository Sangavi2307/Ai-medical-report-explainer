
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

        # Enlarge small images to improve OCR
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

        # Try two OCR layouts
        results = []
        for mode in (6, 11):
            text = pytesseract.image_to_string(
                image,
                config=f"--oem 3 --psm {mode}"
            )
            if text.strip():
                results.append(text.strip())

        uploaded_file.seek(0)

        if not results:
            return ""

        return max(results, key=len)

    except Exception as error:
        uploaded_file.seek(0)
        raise RuntimeError(
            f"Image OCR failed: {error}"
        ) from error
