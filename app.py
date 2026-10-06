import streamlit as st
from extractor import extract_text_from_pdf
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from ocr_service import extract_text_from_image
from analyzer import analyze_report


st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide"
)


st.title("🩺 AI Medical Report Explainer")

st.write(
    "Upload a medical report in PDF or image format "
    "and analyze the test results."
)

st.info(
    "⚠️ Educational purpose only. "
    "This application does not provide diagnosis or treatment."
)


uploaded_file = st.file_uploader(
    "📄 Choose a medical report",
    type=["pdf", "png", "jpg", "jpeg"]
)


if uploaded_file:

    st.success(
        f"✅ File uploaded: {uploaded_file.name}"
    )

    # ---------------------------------
    # PDF
    # ---------------------------------

    if uploaded_file.type == "application/pdf":

        with st.spinner("📄 Extracting text from PDF..."):

            extracted_text = extract_text_from_pdf(
                uploaded_file
            )

    # ---------------------------------
    # IMAGE
    # ---------------------------------

    else:

        with st.spinner("🖼️ Reading image using OCR..."):

            extracted_text = extract_text_from_image(
                uploaded_file
            )


    # ---------------------------------
    # SHOW EXTRACTED TEXT
    # ---------------------------------

    st.subheader("📄 Extracted Text")

    if extracted_text.strip():

        st.text_area(
            "Text extracted from your report:",
            extracted_text,
            height=300
        )

    else:

        st.warning(
            "⚠️ No text could be extracted from this report."
        )


    # ---------------------------------
    # ANALYZE
    # ---------------------------------

    if st.button("🔍 Analyze Report"):

        with st.spinner("🔎 Analyzing laboratory results..."):

            results = analyze_report(
                extracted_text
            )


        if not results.empty:

            st.subheader("📊 Medical Test Analysis")

            st.dataframe(
                results,
                use_container_width=True
            )


            # Count statuses
            below = len(
                results[
                    results["Status"] == "Below Range"
                ]
            )

            within = len(
                results[
                    results["Status"] == "Within Range"
                ]
            )

            above = len(
                results[
                    results["Status"] == "Above Range"
                ]
            )


            col1, col2, col3 = st.columns(3)


            col1.metric(
                "🟢 Within Range",
                within
            )


            col2.metric(
                "🟡 Below Range",
                below
            )


            col3.metric(
                "🔴 Above Range",
                above
            )


        else:

            st.warning(
                "⚠️ No laboratory test results were detected."
            )

            st.info(
                "Please make sure the report contains "
                "test values and reference ranges."
        )
