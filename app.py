import streamlit as st
from extractor import extract_text_from_pdf

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺"
)

st.title("🩺 AI Medical Report Explainer")

st.write(
    "Upload a medical report and get a simple educational explanation."
)

st.info(
    "This application provides educational information "
    "and does not replace professional medical advice."
)

st.subheader("📄 Upload Your Medical Report")

uploaded_file = st.file_uploader(
    "Choose a medical report",
    type=["pdf"]
)

if uploaded_file is not None:

    st.success(
        f"✅ File uploaded: {uploaded_file.name}"
    )

    extracted_text = extract_text_from_pdf(uploaded_file)

    st.subheader("📋 Extracted Report Text")

    if extracted_text.strip():

        st.text_area(
            "Report content",
            extracted_text,
            height=400
        )

    else:

        st.warning(
            "No text could be extracted from this PDF."
        )
