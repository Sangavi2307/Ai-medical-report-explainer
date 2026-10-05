import streamlit as st

st.set_page_config(
    page_title="PDF Upload Test",
    page_icon="📄"
)

st.title("📄 PDF Upload Test")

uploaded_file = st.file_uploader(
    "Upload any PDF",
    type=["pdf"]
)

if uploaded_file is not None:
    st.success("✅ PDF uploaded successfully!")

    st.write("File name:", uploaded_file.name)
    st.write("File size:", uploaded_file.size, "bytes")

    pdf_bytes = uploaded_file.getvalue()

    st.write("PDF received:", len(pdf_bytes), "bytes")
