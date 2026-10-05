import streamlit as st

st.set_page_config(
    page_title="Upload Test",
    page_icon="📄"
)

st.title("📄 PDF Upload Test")

st.write("Testing Streamlit file upload...")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    accept_multiple_files=False
)

if uploaded_file:
    st.success("✅ Upload successful!")
    st.write("File name:", uploaded_file.name)
    st.write("File type:", uploaded_file.type)
    st.write("File size:", uploaded_file.size)
