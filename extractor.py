
import pymupdf


def extract_text_from_pdf(uploaded_file):
    """Extract embedded text from a PDF uploaded to Streamlit."""
    try:
        uploaded_file.seek(0)
        pdf_bytes = uploaded_file.read()

        if not pdf_bytes:
            return ""

        text_parts = []

        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
            for page in pdf:
                page_text = page.get_text("text")
                if page_text:
                    text_parts.append(page_text)

        return "\n".join(text_parts).strip()

    except Exception as exc:
        raise RuntimeError(
            f"Could not read the PDF: {type(exc).__name__}"
        ) from exc
