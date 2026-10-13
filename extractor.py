
import pymupdf


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract selectable text from a PDF uploaded through Streamlit."""

    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    if not pdf_bytes:
        raise ValueError("The uploaded PDF is empty.")

    if not pdf_bytes.startswith(b"%PDF"):
        raise ValueError("The uploaded file is not a valid PDF.")

    text_parts = []

    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    ) as document:

        if document.needs_pass:
            raise ValueError(
                "This PDF is password-protected. Upload an unlocked copy."
            )

        for page in document:
            page_text = page.get_text("text")

            if page_text.strip():
                text_parts.append(page_text.strip())

    return "\n\n".join(text_parts).strip()
