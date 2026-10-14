
import streamlit as st
import pandas as pd

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import explain_report
from report_generator import generate_pdf_report

st.set_page_config(
    page_title="MediLens | Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
)

st.markdown("""
<style>
.stApp { background:#0d111b; color:#f4f6fa; }
.block-container { max-width:1200px; padding-top:1.5rem; }
.hero {
    background:linear-gradient(120deg,#14283d,#075d68);
    padding:25px; border-radius:15px; margin-bottom:20px;
}
.hero h1 {color:white; margin:0;}
.hero p {color:#d8edf0;}
div[data-testid="stMetric"] {
    background:#191f2c; border:1px solid #303849;
    padding:15px; border-radius:12px;
}
h1,h2,h3 {color:#f4f6fa;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🩺 MediLens</h1>
<p>AI Medical Report Explainer · Upload, analyze and understand</p>
</div>
""", unsafe_allow_html=True)

st.warning(
    "Educational use only. This application does not diagnose conditions "
    "or replace a healthcare professional."
)

uploaded = st.file_uploader(
    "📄 Upload your medical report (PDF or image)",
    type=["pdf", "png", "jpg", "jpeg"],
)

if "report_signature" not in st.session_state:
    st.session_state.report_signature = None
if "report_text" not in st.session_state:
    st.session_state.report_text = ""
if "report_name" not in st.session_state:
    st.session_state.report_name = ""
if "results_df" not in st.session_state:
    st.session_state.results_df = pd.DataFrame()
if "patient_fields" not in st.session_state:
    st.session_state.patient_fields = {}
if "explanation" not in st.session_state:
    st.session_state.explanation = ""

if uploaded is not None:
    signature = (uploaded.name, uploaded.size)

    if st.session_state.report_signature != signature:
        st.session_state.report_signature = signature
        st.session_state.report_text = ""
        st.session_state.report_name = ""
        st.session_state.results_df = pd.DataFrame()
        st.session_state.patient_fields = {}
        st.session_state.explanation = ""

    if st.button("🔎 Analyze Report", type="primary", use_container_width=True):
        try:
            with st.spinner("Extracting and analyzing this report..."):
                if uploaded.name.lower().endswith(".pdf"):
                    text = extract_text_from_pdf(uploaded)
                else:
                    text = extract_text_from_image(uploaded)

                if not text.strip():
                    st.error(
                        "No text could be extracted. If this is a scanned PDF, "
                        "OCR must be applied to its pages."
                    )
                else:
                    df = analyze_report(text)
                    patient = extract_patient_fields(text)
                    explanation = explain_report(text, df, patient)

                    st.session_state.report_text = text
                    st.session_state.report_name = uploaded.name
                    st.session_state.results_df = df
                    st.session_state.patient_fields = patient
                    st.session_state.explanation = explanation
                    st.success("Report processed. Review the sections below.")

        except Exception as error:
            st.error("Report processing failed.")
            st.code(f"{type(error).__name__}: {error}")

if st.session_state.report_text:
    text = st.session_state.report_text
    df = st.session_state.results_df
    patient = st.session_state.patient_fields

    st.divider()
    st.header("📄 Uploaded Report")
    st.write(f"**File:** {st.session_state.report_name}")

    with st.expander("View extracted report text", expanded=True):
        st.text_area(
            "Extracted text",
            value=text,
            height=220,
            disabled=True,
        )

    st.divider()
    st.header("👤 Patient Details")
    detail_cols = st.columns(4)
    for col, (key, value) in zip(detail_cols, patient.items()):
        col.metric(key, value or "Not extracted")

    st.divider()
    st.header("🔬 Laboratory Results Analysis")

    a, b = st.columns(2)
    a.metric("Recognized tests", len(df))
    b.metric("Report characters", len(text))

    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(
            "Results are extracted from report text. Confirm the values, "
            "units, and reference ranges against the original report."
        )
    else:
        st.error(
            "No supported laboratory results were recognized. Check the "
            "extracted text above. The report may use a table or layout that "
            "needs a more specialized parser."
        )

    st.divider()
    st.header("📊 Laboratory Results Graph")

    if not df.empty:
        chart = df[["Test", "Result", "Unit"]].copy()
        chart["Numeric Result"] = pd.to_numeric(
            chart["Result"].astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        )
        chart = chart.dropna(subset=["Numeric Result"])

        if not chart.empty:
            st.bar_chart(chart.set_index("Test")["Numeric Result"])
            st.dataframe(
                chart[["Test", "Numeric Result", "Unit"]],
                use_container_width=True,
                hide_index=True,
            )
            st.caption(
                "The chart shows extracted numbers, not medical severity. "
                "Different tests and units should not be compared directly."
            )
        else:
            st.info("No numeric results were available to graph.")

    st.divider()
    st.header("✨ AI Explanation")
    st.markdown(st.session_state.explanation)

    st.divider()
    st.header("📥 Download Report")

    st.download_button(
        "Download extracted text",
        data=text,
        file_name="extracted_report.txt",
        mime="text/plain",
    )

    if st.button("Prepare PDF Summary"):
        try:
            pdf = generate_pdf_report(
                st.session_state.report_name,
                patient,
                df,
                st.session_state.explanation,
            )
            st.download_button(
                "Download PDF Summary",
                data=pdf,
                file_name="medilens_summary.pdf",
                mime="application/pdf",
            )
        except Exception as error:
            st.error(f"PDF creation failed: {error}")

else:
    st.info("Upload a report above and select Analyze Report to see all results here.")

st.divider()
st.caption(
    "MediLens is an educational prototype. It may miss results or extract "
    "values incorrectly. Consult a qualified healthcare professional."
)
