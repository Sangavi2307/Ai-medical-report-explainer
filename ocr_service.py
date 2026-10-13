
import io

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def extract_text_from_image(uploaded_file):
    try:
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()

        if not image_bytes:
            raise ValueError("The uploaded image is empty.")

        image = Image.open(io.BytesIO(image_bytes))
        image.load()
        image = ImageOps.exif_transpose(image).convert("RGB")

        # Enlarge small images for improved OCR.
        if image.width < 1600:
            scale = 1600 / image.width
            image = image.resize(
                (1600, max(1, int(image.height * scale))),
                Image.Resampling.LANCZOS,
            )

        processed = ImageOps.grayscale(image)
        processed = ImageOps.autocontrast(processed)
        processed = ImageEnhance.Contrast(processed).enhance(2)
        processed = processed.filter(ImageFilter.SHARPEN)

        candidates = []
        for page_mode in (6, 11):
            text = pytesseract.image_to_string(
                processed,
                config=f"--oem 3 --psm {page_mode}",
            )
            if text and text.strip():
                candidates.append(text.strip())

        extracted_text = max(candidates, key=len, default="")
        uploaded_file.seek(0)

        if not extracted_text:
            raise ValueError(
                "No text was detected. Try a clearer, higher-resolution image."
            )

        return extracted_text

    except Exception as error:
        uploaded_file.seek(0)
        raise RuntimeError(
            f"Image text extraction failed: {error}"
        ) from error
      
