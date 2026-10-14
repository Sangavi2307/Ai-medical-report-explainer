
import streamlit as st
import pandas as pd

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report


st.set_page_config(
    page_title="MediLens | Medical Report Explainer",
    page_icon="🩺",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #f4f7fb;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.main-title {
    color: #12304a;
    font-size: 36px;
    font-weight: 700;
}
.subtitle {
    color: #526579;
    font-size: 16px;
}
.info-card {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e0e7ef;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🩺 MediLens</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Medical Report Explainer</div>',
    unsafe_allow_html=True
)

st.write(
    "Upload an individual medical report to extract its text "
    "and review any laboratory results the app can recognize."
)

st.warning(
    "Educational use only. This app does not diagnose conditions "
    "or replace advice from a qualified healthcare professional."
)

if "report_text" not in st.session_state:
    st.session_state.report_text = ""

if "results_df" not in st.session_state:
    st.session_state.results_df = pd.DataFrame()

if "report_name" not in st.session_state:
    st.session_state.report_name = ""

st.subheader("Upload your report")

uploaded_file = st.file_uploader(
    "Choose a PDF or image",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    if st.button("Analyze this report", type="primary"):
        try:
            with st.spinner("Reading your report..."):
                file_name = uploaded_file.name.lower()

                if file_name.endswith(".pdf"):
                    report_text = extract_text_from_pdf(uploaded_file)
                else:
                    report_text = extract_text_from_image(uploaded_file)

                if not report_text or not report_text.strip():
                    st.error(
                        "No readable text was found. "
                        "Try a clearer image or a text-based PDF."
                    )
                    st.stop()

                results = analyze_report(report_text)

                st.session_state.report_text = report_text
                st.session_state.report_name = uploaded_file.name

                if isinstance(results, pd.DataFrame):
                    st.session_state.results_df = results
                else:
                    st.session_state.results_df = pd.DataFrame(results)

            st.success("Report text extracted successfully.")

        except Exception as error:
            st.error("The report could not be processed.")
            st.code(str(error))

if st.session_state.report_text:
    st.divider()
    st.subheader("Report overview")

    st.markdown(
        f"**Uploaded file:** {st.session_state.report_name}"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Characters extracted",
            len(st.session_state.report_text)
        )

    with col2:
        st.metric(
            "Recognized results",
            len(st.session_state.results_df)
        )

    st.subheader("Laboratory results")

    if not st.session_state.results_df.empty:
        st.dataframe(
            st.session_state.results_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(
            "No laboratory result lines were recognized. "
            "The report text is available below for review."
        )

    st.subheader("Extracted report text")
    st.text_area(
        "Text extracted from this uploaded report",
        value=st.session_state.report_text,
        height=300
    )

    st.download_button(
        "Download extracted text",
        data=st.session_state.report_text,
        file_name="extracted_report.txt",
        mime="text/plain"
    )

    st.caption(
        "Only the currently uploaded report is processed in this session. "
        "Extraction and result recognition may be incomplete."
    )
