
import pymupdf


def extract_text_from_pdf(uploaded_file):
    if uploaded_file is None:
        return ""

    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()

    if not pdf_bytes:
        return ""

    extracted_pages = []

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
        for page in pdf:
            extracted_pages.append(page.get_text("text"))

    return "\n".join(extracted_pages).strip()
