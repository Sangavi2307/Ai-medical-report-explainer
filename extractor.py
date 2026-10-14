import pymupdf


def extract_text_from_pdf(uploaded_file):
    if uploaded_file is None:
        return ""

    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()

    if not pdf_bytes:
        return ""

    pages = []

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        for page in document:
            pages.append(page.get_text("text") or "")

    return "\n".join(pages).strip()


def extract_text_from_pdf_bytes(pdf_bytes):
    if not pdf_bytes:
        return ""

    pages = []

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        for page in document:
            pages.append(page.get_text("text") or "")

    return "\n".join(pages).strip()
