from PIL import Image
import pytesseract


def extract_text_from_image(uploaded_file):

    uploaded_file.seek(0)

    image = Image.open(uploaded_file)

    text = pytesseract.image_to_string(image)

    return text
