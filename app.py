
import io

import pandas as pd
import streamlit as st

from extractor import extract_text_from_pdf
from ocr_service import (
    extract_text_from_image,
    extract_text_from_scanned_pdf
)
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import explain_report
from report_generator import generate_pdf_report


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="MediLens | Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ---------------- PAGE DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background: #0b1220;
    color: #edf4f8;
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero {
    padding: 28px;
    border-radius: 18px;
    background: linear-gradient(120deg, #102b3a, #123d4a);
    border: 1px solid #235366;
    margin-bottom: 24px;
}
.hero h1 {
    color: #66e3d1;
    margin-bottom: 8px;
}
.hero p {
    color: #d0e5ed;
    font-size: 1rem;
}
.section {
    border: 1px solid #26394c;
    background: #111c2c;
    border-radius: 14px;
    padding: 18px;
    margin: 14px 0;
}
div[data-testid="stMetric"] {
    background: #111c2c;
    border: 1px solid #26394c;
    padding: 14px;
    border-radius: 12px;
}
.stButton button, .stDownloadButton button {
    border-radius: 9px;
    font-weight: 600;
}
.small-note {
    color: #a9bacb;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>🩺 MediLens</h1>
    <p><b>AI Medical Report Explainer</b></p>
    <p>
        Upload a medical report to extract its text, organize laboratory
        values, view a graph, and read educational explanations.
    </p>
</div>
""", unsafe_allow_html=True)

st.info(
    "Educational use only. This application does not diagnose diseases "
    "or recommend treatment. Always verify extracted results against the original report."
)


# ---------------- UPLOAD ----------------

st.markdown("## 1. Upload your medical report")

uploaded_file = st.file_uploader(
    "Choose a PDF or image file",
    type=["pdf", "png", "jpg", "jpeg"],
    help="Supports text-based PDFs, scanned PDFs, and common image formats."
)

analyze_button = st.button(
    "🔍 Analyze Report",
    type="primary",
    use_container_width=True
)


# ---------------- ANALYSIS ----------------

if analyze_button:
    if uploaded_file is None:
        st.warning("Please upload a PDF or image first.")
    else:
        try:
            with st.spinner("Extracting report text..."):
                file_name = uploaded_file.name
                suffix = file_name.lower().rsplit(".", 1)[-1]

                if suffix == "pdf":
                    report_text = extract_text_from_pdf(uploaded_file)

                    # If PDF contains little or no selectable text, try OCR.
                    if len(report_text.strip()) < 30:
                        report_text = extract_text_from_scanned_pdf(uploaded_file)

                else:
                    report_text = extract_text_from_image(uploaded_file)

            if not report_text.strip():
                st.error(
                    "No readable text was extracted. Try a clearer image or PDF."
                )
                st.stop()

            with st.spinner("Analyzing extracted report..."):
                results_df = analyze_report(report_text)
                patient_fields = extract_patient_fields(report_text)

                explanation = explain_report(
                    report_text=report_text,
                    results_df=results_df,
                    patient_fields=patient_fields
                )

            # Save current analysis for the download buttons and reruns.
            st.session_state["report_text"] = report_text
            st.session_state["results_df"] = results_df
            st.session_state["patient_fields"] = patient_fields
            st.session_state["explanation"] = explanation
            st.session_state["report_name"] = file_name

        except Exception as exc:
            st.error("The report could not be processed.")
            st.exception(exc)


# ---------------- DISPLAY RESULTS ----------------

if "report_text" in st.session_state:
    report_text = st.session_state["report_text"]
    results_df = st.session_state["results_df"]
    patient_fields = st.session_state["patient_fields"]
    explanation = st.session_state["explanation"]
    report_name = st.session_state["report_name"]

    st.divider()
    st.markdown("## 2. Analysis overview")

    total_tests = len(results_df)

    if total_tests:
        above_count = results_df["Status"].eq("Above range").sum()
        below_count = results_df["Status"].eq("Below range").sum()
        within_count = results_df["Status"].eq("Within range").sum()
        review_count = total_tests - above_count - below_count - within_count
    else:
        above_count = below_count = within_count = review_count = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Tests extracted", total_tests)
    col2.metric("Within range", int(within_count))
    col3.metric("Above range", int(above_count))
    col4.metric("Below range", int(below_count))

    if review_count:
        st.warning(
            f"{review_count} result(s) need manual review because a reference "
            "range or status could not be reliably identified."
        )

    # ---------------- PATIENT DETAILS ----------------

    st.markdown("## 3. Patient details")

    if patient_fields:
        patient_cols = st.columns(2)
        for index, (key, value) in enumerate(patient_fields.items()):
            patient_cols[index % 2].write(f"**{key}:** {value}")
    else:
        st.caption(
            "Patient details were not confidently identified in the extracted text."
        )

    # ---------------- EXTRACTED TEXT ----------------

    st.markdown("## 4. Extracted report text")

    with st.expander("View extracted text", expanded=False):
        st.text_area(
            "Extracted text",
            value=report_text,
            height=300,
            disabled=True
        )

    # ---------------- RESULTS TABLE ----------------

    st.markdown("## 5. Laboratory results")

    if not results_df.empty:
        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True
        )

        csv_bytes = results_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇️ Download results as CSV",
            data=csv_bytes,
            file_name="medilens_results.csv",
            mime="text/csv"
        )
    else:
        st.warning(
            "No laboratory rows were detected. The extracted text is shown above, "
            "but this report's layout may not match the current parser. "
            "Do not rely on an empty table as proof that the report contains no results."
        )

    # ---------------- GRAPH ----------------

    st.markdown("## 6. Laboratory result graph")

    if not results_df.empty:
        numeric_df = results_df.copy()
        numeric_df["Numeric Result"] = pd.to_numeric(
            numeric_df["Result"],
            errors="coerce"
        )
        chart_df = numeric_df.dropna(subset=["Numeric Result"])

        if not chart_df.empty:
            chart_df = chart_df.set_index("Test")[["Numeric Result"]]
            st.bar_chart(chart_df)
            st.caption(
                "The graph compares reported numeric values. Different tests use "
                "different units and scales, so bar heights should not be compared "
                "across different test types."
            )
        else:
            st.info("No numeric results were available to plot.")
    else:
        st.info("The graph will appear when laboratory results are extracted.")

    # ---------------- EXPLANATION ----------------

    st.markdown("## 7. Detailed medical report explanation")
    st.markdown(explanation)

    # ---------------- PDF DOWNLOAD ----------------

    st.markdown("## 8. Download your report")

    try:
        pdf_bytes = generate_pdf_report(
            report_name=report_name,
            patient_fields=patient_fields,
            results_df=results_df,
            summary=explanation
        )

        st.download_button(
            "⬇️ Download complete report as PDF",
            data=pdf_bytes,
            file_name="medilens_report_explanation.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    except Exception as exc:
        st.error("PDF generation failed.")
        st.exception(exc)

    st.caption(
        "Please compare every extracted value and reference range with the original report."
    )
