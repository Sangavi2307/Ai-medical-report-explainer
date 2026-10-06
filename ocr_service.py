from PIL import Image, ImageEnhance, ImageFilter
import pytesseract


def extract_text_from_image(uploaded_file):

    uploaded_file.seek(0)

    image = Image.open(uploaded_file)

    # Convert to RGB
    image = image.convert("RGB")

    # Increase image size for better OCR
    width, height = image.size

    image = image.resize(
        (width * 2, height * 2)
    )

    # Convert to grayscale
    image = image.convert("L")

    # Improve contrast
    image = ImageEnhance.Contrast(image).enhance(2.0)

    # Sharpen text
    image = image.filter(
        ImageFilter.SHARPEN
    )

    # OCR configuration
    custom_config = r"--oem 3 --psm 6"

    text = pytesseract.image_to_string(
        image,
        config=custom_config
    )

    return text
