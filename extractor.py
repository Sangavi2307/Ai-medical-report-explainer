
import pymupdf


def extract_text_from_pdf(uploaded_file):
    try:
        uploaded_file.seek(0)
        pdf_bytes = uploaded_file.read()

        if not pdf_bytes:
            raise ValueError("The uploaded PDF is empty.")

        text_parts = []

        with pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        ) as document:
            for page in document:
                page_text = page.get_text("text")
                if page_text.strip():
                    text_parts.append(page_text.strip())

        uploaded_file.seek(0)
        return "\n\n".join(text_parts)

    except Exception as error:
        uploaded_file.seek(0)
        raise RuntimeError(
            f"PDF text extraction failed: {error}"
        ) from error
