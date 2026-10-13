
import pymupdf


def extract_text_from_pdf(uploaded_file):
    try:
        uploaded_file.seek(0)
        pdf_bytes = uploaded_file.read()

        if not pdf_bytes:
            raise ValueError("The uploaded PDF is empty.")

        pages_text = []

        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
            for page in document:
                pages_text.append(page.get_text("text"))

        extracted_text = "\n".join(pages_text).strip()
        uploaded_file.seek(0)

        if not extracted_text:
            return (
                "No selectable text was found in this PDF. "
                "It may be scanned; upload its page as an image or add "
                "scanned-PDF OCR support."
            )

        return extracted_text

    except Exception as error:
        uploaded_file.seek(0)
        raise RuntimeError(
            f"PDF text extraction failed: {error}"
        ) from error
        
