
import pymupdf

def extract_text_from_pdf(uploaded_file):
    if uploaded_file is None:
        return ""

    uploaded_file.seek(0)
    data = uploaded_file.read()

    if not data:
        return ""

    parts = []
    with pymupdf.open(stream=data, filetype="pdf") as pdf:
        for page in pdf:
            parts.append(page.get_text("text"))

    return "\n".join(parts).strip()
