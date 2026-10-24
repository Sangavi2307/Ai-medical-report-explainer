
import io
import pymupdf
from PIL import Image
import pytesseract


def _ocr_image(image):
    """Extract text from an image without changing numeric values."""
    try:
        return pytesseract.image_to_string(
            image,
            config="--psm 6"
        ).strip()
    except Exception as exc:
        raise RuntimeError(
            "Image OCR failed. Check the OCR installation."
        ) from exc


def extract_text_from_pdf(uploaded_file):
    """Extract selectable PDF text, using OCR for scanned pages."""
    if uploaded_file is None:
        return ""

    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()

    if not pdf_bytes:
        return ""

    extracted_pages = []

    try:
        with pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        ) as pdf:
            for page in pdf:
                page_text = page.get_text("text").strip()

                # Keep native text when available.
                if len(page_text) >= 30:
                    extracted_pages.append(page_text)
                    continue

                # OCR pages with little or no selectable text.
                pix = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False
                )
                image = Image.open(
                    io.BytesIO(pix.tobytes("png"))
                )
                ocr_text = _ocr_image(image)

                extracted_pages.append(
                    ocr_text if ocr_text else page_text
                )

    except Exception as exc:
        raise RuntimeError(
            "Could not read this PDF. Try a clear, unlocked PDF."
        ) from exc

    return "\n\n".join(extracted_pages).strip()


def extract_text_from_image(uploaded_file):
    """Extract text from an uploaded PNG, JPG, or other PIL-supported image."""
    if uploaded_file is None:
        return ""

    uploaded_file.seek(0)
    image_bytes = uploaded_file.read()

    if not image_bytes:
        return ""

    try:
        with Image.open(io.BytesIO(image_bytes)) as image:
            image = image.convert("RGB")
            return _ocr_image(image)
    except Exception as exc:
        raise RuntimeError(
            "Could not read this image. Try a clear PNG or JPG."
        ) from exc
