import streamlit as st

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺"
)

st.title("🩺 AI Medical Report Explainer")

st.write("Upload a medical report for testing.")

st.subheader("📄 Upload Medical Report")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)

if uploaded_file:
    st.success("✅ PDF uploaded successfully!")

    st.write("File name:", uploaded_file.name)
    st.write("File size:", uploaded_file.size, "bytes")
