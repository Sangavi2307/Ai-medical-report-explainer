from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import pytesseract
import io


def extract_text_from_image(uploaded_file):
    try:
        uploaded_file.seek(0)

        image = Image.open(uploaded_file)
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGB")

        # Enlarge the image to improve OCR accuracy
        width, height = image.size

        if width < 2000:
            scale = min(3, 2000 / width)
            image = image.resize(
                (int(width * scale), int(height * scale))
            )

        # Improve text visibility
        image = ImageOps.grayscale(image)
        image = ImageEnhance.Contrast(image).enhance(2.0)
        image = ImageEnhance.Sharpness(image).enhance(2.0)
        image = image.filter(ImageFilter.SHARPEN)

        # Extract text using Tesseract OCR
        text = pytesseract.image_to_string(
            image,
            config="--oem 3 --psm 6"
        )

        return text.strip()

    except Exception as error:
        raise RuntimeError(
            f"Image text extraction failed: {error}"
        ) from error
    
