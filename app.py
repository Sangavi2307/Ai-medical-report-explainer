
import io
import os

import pandas as pd
import streamlit as st

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from report_generator import generate_pdf_report


st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
)

st.title("🩺 AI Medical Report Explainer")
st.caption(
    "Upload a laboratory report to extract text and review recognized results."
)

st.warning(
    "Educational use only. This app does not diagnose conditions or "
    "recommend treatment. Confirm results with a qualified healthcare professional."
)

uploaded_file = st.file_uploader(
    "Upload a medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    help="Supported formats: PDF, PNG, JPG and JPEG.",
)

pasted_text = st.text_area(
    "Or paste report text here",
    height=150,
    placeholder="Paste the text from your laboratory report...",
)

if "report_text" not in st.session_state:
    st.session_state.report_text = ""
if "results_df" not in st.session_state:
    st.session_state.results_df = pd.DataFrame()
if "ai_explanation" not in st.session_state:
    st.session_state.ai_explanation = ""

if st.button("Extract and analyze report", type="primary"):
    report_text = ""

    try:
        if uploaded_file is not None:
            file_name = uploaded_file.name.lower()

            with st.spinner("Reading your report..."):
                if file_name.endswith(".pdf"):
                    report_text = extract_text_from_pdf(uploaded_file)
                else:
                    report_text = extract_text_from_image(uploaded_file)

        elif pasted_text.strip():
            report_text = pasted_text.strip()

        else:
            st.error("Please upload a report or paste report text.")
            st.stop()

        # A PDF can contain no selectable text if it is scanned.
        if report_text.startswith("No selectable text was found"):
            st.session_state.report_text = report_text
            st.session_state.results_df = pd.DataFrame()
            st.session_state.ai_explanation = ""
            st.warning(report_text)
            st.stop()

        st.session_state.report_text = report_text
        st.session_state.results_df = analyze_report(report_text)
        st.session_state.ai_explanation = ""

    except Exception as error:
        st.error(f"Could not process this report: {error}")

report_text = st.session_state.report_text
results_df = st.session_state.results_df

if report_text:
    st.subheader("Extracted Report Text")
    st.text_area(
        "Check the text recognized from your report",
        value=report_text,
        height=250,
        disabled=True,
        key="extracted_text_display",
    )

    st.download_button(
        "Download extracted text",
        data=report_text,
        file_name="extracted_report.txt",
        mime="text/plain",
    )

    st.subheader("Laboratory Results Analysis")

    if results_df is not None and not results_df.empty:
        st.success(f"Recognized {len(results_df)} laboratory result(s).")
        st.dataframe(results_df, use_container_width=True, hide_index=True)

        csv_data = results_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download results as CSV",
            data=csv_data,
            file_name="laboratory_results.csv",
            mime="text/csv",
        )
    else:
        st.warning(
            "No laboratory results were recognized. Check the extracted text "
            "and update the test-name patterns in analyzer.py if necessary."
        )
        st.info(
            "If the extracted text is readable, the issue is likely the "
            "analyzer's pattern matching. If the text itself is incorrect, "
            "try a clearer image or improve OCR."
        )

    st.divider()
    st.subheader("AI Explanation")

    if st.button("Generate AI explanation"):
        with st.spinner("Preparing explanation..."):
            st.session_state.ai_explanation = ai_explain_report(
                report_text,
                results_df,
            )

    if st.session_state.ai_explanation:
        st.write(st.session_state.ai_explanation)

    st.divider()
    st.subheader("Download report")

    try:
        pdf_bytes = generate_pdf_report(
            report_text=report_text,
            results_df=results_df,
            ai_explanation=st.session_state.ai_explanation,
        )

        st.download_button(
            "Download summary as PDF",
            data=pdf_bytes,
            file_name="medical_report_summary.pdf",
            mime="application/pdf",
        )
    except Exception as error:
        st.error(f"Could not create PDF report: {error}")
        
