
import pymupdf


def extract_text_from_pdf(uploaded_file):
    if uploaded_file is None:
        return ""

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
