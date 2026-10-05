import streamlit as st

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺"
)

st.title("🩺 AI Medical Report Explainer")

st.info(
    "This application provides educational information "
    "and does not replace professional medical advice."
)

st.subheader("📄 Upload Your Medical Report")

uploaded_file = st.file_uploader(
    "Choose a PDF medical report",
    type=["pdf"]
)

if uploaded_file is not None:

    st.success(f"✅ Uploaded: {uploaded_file.name}")

    st.write("File size:", uploaded_file.size, "bytes")

    if st.button("🔍 Analyze Report"):
        st.write("The report is ready for analysis.")
