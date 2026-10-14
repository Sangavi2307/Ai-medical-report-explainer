
import pymupdf


def extract_text_from_pdf(uploaded_file):
    if uploaded_file is None:
        return ""

    try:
        uploaded_file.seek(0)
        pdf_bytes = uploaded_file.read()

        if not pdf_bytes:
            return ""

        text_parts = []

        with pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        ) as pdf:
            for page in pdf:
                text_parts.append(page.get_text("text"))

        return "\n".join(text_parts).strip()

    except Exception as error:
        raise ValueError(
            f"Could not read this PDF: {error}"
        ) from error
