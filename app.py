import streamlit as st

st.set_page_config(
    page_title="Upload Test"
)

st.title("📄 PDF Upload Test")

uploaded_file = st.file_uploader(
    "Choose a PDF",
    type=["pdf"]
)

if uploaded_file is not None:
    st.success("✅ Upload successful!")
    st.write("File:", uploaded_file.name)
    st.write("Size:", uploaded_file.size)
