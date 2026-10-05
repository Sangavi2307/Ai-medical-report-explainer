import streamlit as st

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
    type=["pdf", "jpg", "jpeg", "png"]
)

if uploaded_file is not None:

    st.success(
        f"✅ File uploaded successfully: {uploaded_file.name}"
    )

    st.write("File type:", uploaded_file.type)

    st.write(
        "The next step will extract the information "
        "from this report."
    )
