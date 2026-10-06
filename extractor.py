import pymupdf

def extract_text_from_pdf(uploaded_file):

    uploaded_file.seek(0)

    pdf_bytes = uploaded_file.read()

    document = pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    text = ""

    for page in document:
        text += page.get_text()
        text += "\n"

    document.close()

    return text
