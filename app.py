
import streamlit as st
import pandas as pd

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image, extract_text_from_scanned_pdf
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import explain_report
from report_generator import generate_pdf_report


st.set_page_config(
    page_title="MediLens | Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============== WEBSITE STYLE ==============

st.markdown("""
<style>
.stApp {
    background: #07111f;
    color: #edf5ff;
}
#MainMenu, footer, header {
    visibility: hidden;
}
[data-testid="stSidebar"] {
    display: none;
}
.block-container {
    max-width: 1200px;
    padding: 2rem 5%;
}
.brand {
    color: #45e0c1;
    font-size: 32px;
    font-weight: 800;
}
.subtitle {
    color: #a8bfd4;
}
.hero {
    background: linear-gradient(135deg, #102b42, #164b54);
    padding: 40px;
    border-radius: 22px;
    margin: 25px 0;
    border: 1px solid #28586a;
}
.hero h1 {
    color: white;
    font-size: 38px;
}
.hero p {
    color: #d1e2ed;
    font-size: 17px;
}
.feature {
    background: #101f31;
    padding: 22px;
    border: 1px solid #263b50;
    border-radius: 16px;
    min-height: 145px;
}
.feature h3 {
    color: #45e0c1;
}
div[data-testid="stMetric"] {
    background: #101f31;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #263b50;
}
div[data-testid="stMetricValue"] {
    color: #45e0c1;
}
.stButton button, .stDownloadButton button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
}
.disclaimer {
    background: #30291a;
    color: #ffe6a6;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #75613a;
}
.footer {
    text-align: center;
    color: #8fa5ba;
    border-top: 1px solid #263b50;
    padding-top: 20px;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)


# ============== NAVIGATION ==============

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "explanation" not in st.session_state:
    st.session_state.explanation = None


# ============== HEADER ==============

left, right = st.columns([3, 2])

with left:
    st.markdown(
        '<div class="brand">🩺 MediLens.</div>'
        '<div class="subtitle">Understand your medical reports with clarity</div>',
        unsafe_allow_html=True,
    )

with right:
    a, b, c = st.columns(3)

    if a.button("Home", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()

    if b.button("Analyze", use_container_width=True):
        st.session_state.page = "Analyze"
        st.rerun()

    if c.button("About", use_container_width=True):
        st.session_state.page = "About"
        st.rerun()


# ============== FILE EXTRACTION ==============

def extract_uploaded_report(uploaded_file):
    """Read only the currently uploaded report."""

    if uploaded_file is None:
        return ""

    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        uploaded_file.seek(0)
        text = extract_text_from_pdf(uploaded_file)

        if not text or len(text.strip()) < 20:
            uploaded_file.seek(0)
            text = extract_text_from_scanned_pdf(uploaded_file)

        return text or ""

    if filename.endswith((".png", ".jpg", ".jpeg")):
        uploaded_file.seek(0)
        return extract_text_from_image(uploaded_file) or ""

    return ""


# ============== STATUS COUNTS ==============

def get_status_counts(df):

    if df is None or df.empty or "Status" not in df.columns:
        return 0, 0, 0

    status = df["Status"].fillna("").astype(str).str.lower()

    low = status.str.contains(
        r"below|low|decreased", regex=True
    ).sum()

    high = status.str.contains(
        r"above|high|increased", regex=True
    ).sum()

    normal = status.str.contains(
        r"within|normal|reference range", regex=True
    ).sum()

    return int(low), int(normal), int(high)


# ============== HOME PAGE ==============

if st.session_state.page == "Home":

    st.markdown("""
    <div class="hero">
        <h1>Your medical report,<br>made easier to understand.</h1>
        <p>
        Upload a medical report to extract available text, organize
        test results, and view educational explanations.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Analyze My Report", type="primary"):
        st.session_state.page = "Analyze"
        st.rerun()

    st.markdown("## What MediLens offers")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature">
            <h3>📄 Report Upload</h3>
            <p>Upload supported PDF and image reports.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature">
            <h3>📊 Result Overview</h3>
            <p>View detected laboratory values and their reported status.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature">
            <h3>💡 Easy Explanations</h3>
            <p>Read educational information about extracted results.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class="disclaimer">
    <b>Medical disclaimer:</b> This application is for educational use.
    It cannot diagnose medical conditions or replace professional advice.
    </div>
    """, unsafe_allow_html=True)


# ============== ANALYSIS PAGE ==============

elif st.session_state.page == "Analyze":

    st.header("🔬 Analyze Your Medical Report")
    st.write("Upload one report at a time.")

    uploaded_file = st.file_uploader(
        "Choose your report",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Maximum size: 10 MB",
        key="medical_report",
    )

    if uploaded_file is not None:

        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("File exceeds 10 MB. Please choose a smaller file.")

        else:
            st.success(f"Selected file: {uploaded_file.name}")

            if st.button("🔍 Analyze Report", type="primary"):

                # Remove old results so another report cannot display stale data.
                st.session_state.analysis = None
                st.session_state.explanation = None

                try:
                    with st.spinner("Extracting your report..."):
                        report_text = extract_uploaded_report(uploaded_file)

                    if not report_text or len(report_text.strip()) < 10:
                        st.error(
                            "No readable text found. Try a clearer image "
                            "or a text-based PDF."
                        )

                    else:
                        with st.spinner("Organizing detected results..."):
                            results_df = analyze_report(report_text)
                            patient_fields = extract_patient_fields(report_text)

                        st.session_state.analysis = {
                            "filename": uploaded_file.name,
                            "text": report_text,
                            "results": results_df,
                            "patient": patient_fields,
                        }

                        st.rerun()

                except Exception as error:
                    st.error("Could not process this report.")
                    st.code(str(error))

    # Display the current analysis only.
    analysis = st.session_state.analysis

    if analysis is not None:

        report_text = analysis["text"]
        results_df = analysis["results"]
        patient_fields = analysis["patient"]
        filename = analysis["filename"]

        st.divider()
        st.subheader("📋 Report Overview")
        st.caption(f"Uploaded file: {filename}")

        if patient_fields:
            st.write("**Details detected in the report**")
            st.json(patient_fields, expanded=False)

        low, normal, high = get_status_counts(results_df)

        m1, m2, m3 = st.columns(3)
        m1.metric("Below range", low)
        m2.metric("Within range", normal)
        m3.metric("Above range", high)

        st.subheader("🧪 Detected Test Results")

        if results_df is not None and not results_df.empty:

            st.dataframe(
                results_df,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "⬇️ Download Results CSV",
                data=results_df.to_csv(index=False).encode("utf-8"),
                file_name="medilens_results.csv",
                mime="text/csv",
            )

            if "Result" in results_df.columns and "Test" in results_df.columns:

                chart = results_df[["Test", "Result"]].copy()

                chart["Result"] = pd.to_numeric(
                    chart["Result"].astype(str).str.replace(",", ""),
                    errors="coerce",
                )

                chart = chart.dropna(subset=["Result"])

                if not chart.empty:
                    st.subheader("📊 Result Visualization")
                    st.caption(
                        "Different tests may use different units. "
                        "Compare each value with its own reference range."
                    )
                    st.bar_chart(chart.set_index("Test"))

        else:
            st.info(
                "No structured test results were detected. "
                "Check the extracted text and original report."
            )

        st.subheader("🤖 Educational Explanation")

        if st.button("Generate Explanation"):
            try:
                with st.spinner("Preparing explanation..."):
                    st.session_state.explanation = explain_report(
                        report_text,
                        results_df,
                        patient_fields,
                    )
            except Exception as error:
                st.error("Could not generate an explanation.")
                st.code(str(error))

        explanation = st.session_state.explanation

        if explanation:
            if isinstance(explanation, str):
                st.markdown(explanation)
            else:
                st.write(explanation)

        with st.expander("📄 View Extracted Text"):
            st.text_area(
                "Extracted report text",
                value=report_text,
                height=250,
                disabled=True,
            )

        st.subheader("📥 Download PDF Summary")

        try:
            summary = (
                f"Detected result rows: {len(results_df)}. "
                f"Below range: {low}; within range: {normal}; "
                f"above range: {high}."
            )

            pdf_data = generate_pdf_report(
                filename,
                patient_fields,
                results_df,
                summary,
            )

            if pdf_data:
                st.download_button(
                    "⬇️ Download PDF",
                    data=pdf_data,
                    file_name="medilens_summary.pdf",
                    mime="application/pdf",
                )

        except Exception as error:
            st.warning("PDF summary generation failed.")
            st.code(str(error))

        st.markdown("""
        <div class="disclaimer">
        <b>Important:</b> Extraction and classification can be inaccurate.
        Always verify results against the original report and consult a
        qualified healthcare professional.
        </div>
        """, unsafe_allow_html=True)

        if st.button("🗑️ Clear Current Analysis"):
            st.session_state.analysis = None
            st.session_state.explanation = None
            st.rerun()


# ============== ABOUT PAGE ==============

elif st.session_state.page == "About":

    st.header("About MediLens")

    st.write("""
    MediLens is an educational application designed to make medical
    report information easier to explore.

    **Features**
    - PDF and image text extraction
    - Laboratory result organization
    - Status summaries and charts
    - Educational explanations
    - CSV and PDF downloads

    **Limitations**

    Text extraction, test identification, and reference-range comparisons
    may be incorrect or incomplete. MediLens is not a diagnostic system.
    """)

    st.info(
        "Use fictional sample reports for testing whenever possible. "
        "Be careful with identifiable medical information."
    )


# ============== FOOTER ==============

st.markdown("""
<div class="footer">
    🩺 MediLens | AI Medical Report Explainer<br>
    Educational use only • Not a substitute for professional care
</div>
""", unsafe_allow_html=True)
