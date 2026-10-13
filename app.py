import pandas as pd
import streamlit as st

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from report_generator import generate_pdf_report


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MediLens | Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# PROFESSIONAL UI
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f5f8fc;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102344 0%, #172f54 100%);
}

[data-testid="stSidebar"] * {
    color: #f3f7ff;
}

[data-testid="stSidebar"] .stRadio label {
    padding: 8px 4px;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

.hero {
    background: linear-gradient(115deg, #ffffff, #eaf4ff);
    border: 1px solid #dce8f8;
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 22px;
}

.hero h1 {
    color: #142b4e;
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 8px;
}

.hero p {
    color: #64748b;
    margin-bottom: 0;
}

.metric-card {
    background: white;
    border: 1px solid #e1eaf5;
    border-radius: 15px;
    padding: 20px;
    min-height: 125px;
    box-shadow: 0 3px 12px rgba(25, 55, 90, 0.035);
}

.metric-label {
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 12px;
}

.metric-value {
    color: #17365e;
    font-size: 27px;
    font-weight: 800;
}

.metric-note {
    color: #64748b;
    font-size: 12px;
    margin-top: 8px;
}

.section-card {
    background: white;
    border: 1px solid #e1eaf5;
    border-radius: 15px;
    padding: 22px;
    margin-bottom: 16px;
}

.section-heading {
    color: #17365e;
    font-size: 20px;
    font-weight: 750;
    margin-bottom: 14px;
}

.info-banner {
    background: #eaf4ff;
    border: 1px solid #cfe4ff;
    color: #234c7a;
    padding: 15px;
    border-radius: 12px;
    margin: 12px 0;
}

.small-muted {
    color: #718096;
    font-size: 12px;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 10px;
    font-weight: 600;
    min-height: 42px;
}

div[data-testid="stFileUploader"] {
    background: white;
    border: 1px dashed #a7bedc;
    padding: 12px;
    border-radius: 12px;
}

hr {
    border-color: #e2eaf4;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "report_text": "",
    "results_df": pd.DataFrame(),
    "ai_explanation": "",
    "report_name": "",
    "processed_at": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_text(value):
    if value is None:
        return ""
    return str(value).strip()


def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def find_patient_value(report_text, labels):
    """Find a patient field without assuming missing information."""
    for line in report_text.splitlines():
        for label in labels:
            match = re.match(
                rf"^\s*{label}\s*[:\-]\s*(.*?)\s*$",
                line,
                re.IGNORECASE,
            )
            if match and match.group(1).strip():
                return match.group(1).strip()

    return "Not identified"


def render_laboratory_table(df):
    if df is None or df.empty:
        st.info(
            "No laboratory values were recognized in this report. "
            "This does not mean that the report is normal. "
            "Check the extracted text and the original report."
        )
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "⬇ Download laboratory results (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="laboratory_results.csv",
        mime="text/csv",
        key="download_lab_csv",
    )


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.markdown("## 🩺 MediLens")
    st.caption("Medical Report Explainer")
    st.divider()

    page = st.radio(
        "MAIN MENU",
        [
            "Dashboard",
            "Upload Report",
            "Laboratory Results",
            "Report Summary",
            "Extracted Text",
        ],
        label_visibility="visible",
    )

    st.divider()

    st.markdown("### About MediLens")
    st.caption(
        "A report-reading assistant that organizes extracted "
        "medical information for easier review."
    )

    st.markdown("---")
    st.caption("Version 2.0 · Educational use only")


# =========================================================
# EMPTY STATE
# =========================================================

report_text = st.session_state.report_text
results_df = st.session_state.results_df
explanation = st.session_state.ai_explanation

if not report_text and page != "Upload Report":
    st.markdown("""
    <div class="hero">
        <h1>Welcome to MediLens 🩺</h1>
        <p>Your medical report information, organized in one place.</p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "Start by uploading a medical report or pasting its text. "
        "Your dashboard will show information from that report only."
    )

    if st.button("＋ Upload your first report", type="primary"):
        st.session_state["open_upload"] = True
        st.rerun()


# =========================================================
# UPLOAD REPORT PAGE
# =========================================================

if page == "Upload Report":

    st.markdown("""
    <div class="hero">
        <h1>Upload Medical Report</h1>
        <p>Import a PDF or image, or paste extracted report text.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="info-banner">Supported files: PDF, PNG, JPG and JPEG. '
        'For privacy, upload only reports you are authorized to use.</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a report",
        type=["pdf", "png", "jpg", "jpeg"],
        key="medical_report_upload",
    )

    pasted_text = st.text_area(
        "Or paste report text",
        height=220,
        placeholder=(
            "Paste the report text here, including test names, "
            "results, units and reference ranges..."
        ),
        key="medical_report_pasted_text",
    )

    st.caption(
        "Uploading a new report replaces the active report in this session."
    )

    if st.button("Analyze this report", type="primary",
                 use_container_width=True):

        new_report_text = ""
        new_report_name = "Pasted report"

        if pasted_text.strip():
            new_report_text = pasted_text.strip()

        elif uploaded_file is not None:
            new_report_name = uploaded_file.name
            file_name = uploaded_file.name.lower()

            try:
                with st.spinner("Reading your report..."):
                    if file_name.endswith(".pdf"):
                        new_report_text = extract_text_from_pdf(uploaded_file)
                    else:
                        new_report_text = extract_text_from_image(uploaded_file)

            except Exception as error:
                st.error(f"Could not read the file: {error}")

        else:
            st.error("Upload a report or paste its text first.")

        if new_report_text and new_report_text.strip():

            if new_report_text.startswith("No selectable text was found"):
                st.error(
                    "No selectable text was found in this PDF. "
                    "Try a clearer scanned image or paste the text."
                )

            else:
                # Reset all old results before storing a new report.
                st.session_state.report_text = new_report_text.strip()
                st.session_state.results_df = pd.DataFrame()
                st.session_state.ai_explanation = ""
                st.session_state.report_name = new_report_name
                st.session_state.processed_at = datetime.now().strftime(
                    "%d %b %Y, %I:%M %p"
                )

                try:
                    lab_results = analyze_report(
                        st.session_state.report_text
                    )

                    if isinstance(lab_results, pd.DataFrame):
                        st.session_state.results_df = lab_results
                except Exception as error:
                    st.warning(
                        "The report was read, but laboratory analysis "
                        f"could not finish: {error}"
                    )

                st.success("Report processed. Open Dashboard to review it.")

                st.rerun()


# =========================================================
# DASHBOARD PAGE
# =========================================================

elif page == "Dashboard" and report_text:

    patient_name = find_patient_value(
        report_text,
        [r"patient name", r"name"],
    )
    age = find_patient_value(report_text, [r"age"])
    gender = find_patient_value(report_text, [r"gender", r"sex"])

    st.markdown("""
    <div class="hero">
        <h1>Medical Report Dashboard</h1>
        <p>Review the information extracted from your active report.</p>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        f"Report: {st.session_state.report_name or 'Current report'}"
        f" · Processed: {st.session_state.processed_at or 'Not recorded'}"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("PATIENT", patient_name[:24], "Extracted from report")

    with c2:
        metric_card("AGE", age[:18], "As written in the report")

    with c3:
        metric_card("GENDER", gender[:18], "As written in the report")

    with c4:
        lab_count = (
            len(results_df)
            if isinstance(results_df, pd.DataFrame)
            else 0
        )
        metric_card("LAB RESULTS", str(lab_count), "Recognized test rows")

    st.markdown("### Report Overview")

    left, right = st.columns([1.6, 1])

    with left:
        st.markdown(
            '<div class="section-card">'
            '<div class="section-heading">📋 Report Status</div>',
            unsafe_allow_html=True,
        )

        st.write("**Source:**", st.session_state.report_name or "Pasted text")
        st.write("**Text extracted:** Yes")
        st.write(
            "**Laboratory analysis:**",
            "Results found" if lab_count else "No recognized lab results",
        )
        st.write(
            "**Explanation:**",
            "Generated" if explanation else "Not generated yet",
        )

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            '<div class="section-card">'
            '<div class="section-heading">🔎 Quick Actions</div>',
            unsafe_allow_html=True,
        )

        st.write("Use the sidebar to explore your report.")

        st.markdown(
            '<div class="small-muted">Tip: verify extracted names, dates, '
            'medication instructions, units and reference ranges.</div>',
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Laboratory Snapshot")

    if not results_df.empty:
        render_laboratory_table(results_df.head(8))
    else:
        st.info(
            "No laboratory results to display yet. "
            "The report may still contain useful history and observations."
        )

    st.markdown(
        '<div class="info-banner"><b>Important:</b> This application '
        'organizes extracted information for educational purposes. '
        'It does not diagnose a disease or recommend treatment.</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# LABORATORY RESULTS PAGE
# =========================================================

elif page == "Laboratory Results" and report_text:

    st.markdown("""
    <div class="hero">
        <h1>Laboratory Results</h1>
        <p>Review recognized test results, units and supplied ranges.</p>
    </div>
    """, unsafe_allow_html=True)

    if not results_df.empty:

        render_laboratory_table(results_df)

        if "Test" in results_df.columns and "Result" in results_df.columns:
            chart_df = results_df.copy()
            chart_df["Result"] = pd.to_numeric(
                chart_df["Result"], errors="coerce"
            )
            chart_df = chart_df.dropna(subset=["Result"])

            if not chart_df.empty:
                st.markdown("### Result Values")

                st.caption(
                    "Values with different units or test types are not "
                    "directly comparable. This chart shows reported numbers, "
                    "not a medical severity score."
                )

                chart_df = chart_df.set_index("Test")
                st.bar_chart(chart_df["Result"])

    else:
        st.info(
            "No laboratory values were recognized. Check the extracted "
            "text in the Extracted Text page. If the report contains a "
            "laboratory table, its layout may need additional parsing rules."
        )


# =========================================================
# REPORT SUMMARY PAGE
# =========================================================

elif page == "Report Summary" and report_text:

    st.markdown("""
    <div class="hero">
        <h1>Complete Report Summary</h1>
        <p>Generate a structured explanation using the free local rules.</p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "This version uses your existing rule-based summarizer and does "
        "not require paid AI API credits."
    )

    if st.button("Generate report explanation", type="primary"):

        with st.spinner("Organizing report information..."):
            try:
                result = ai_explain_report(report_text, results_df)

                st.session_state.ai_explanation = (
                    str(result) if result else "No explanation was returned."
                )

            except Exception as error:
                st.error(f"Could not generate the explanation: {error}")

    if st.session_state.ai_explanation:
        st.markdown(st.session_state.ai_explanation)

        st.download_button(
            "⬇ Download explanation (Markdown)",
            data=st.session_state.ai_explanation,
            file_name="medical_report_explanation.md",
            mime="text/markdown",
        )

    st.divider()
    st.markdown("### Download Complete PDF Summary")

    try:
        pdf_bytes = generate_pdf_report(
            report_text=report_text,
            results_df=results_df,
            ai_explanation=st.session_state.ai_explanation,
        )

        st.download_button(
            "⬇ Download report summary (PDF)",
            data=pdf_bytes,
            file_name="medical_report_summary.pdf",
            mime="application/pdf",
        )

    except Exception as error:
        st.error(f"PDF generation failed: {error}")


# =========================================================
# EXTRACTED TEXT PAGE
# =========================================================

elif page == "Extracted Text" and report_text:

    st.markdown("""
    <div class="hero">
        <h1>Extracted Report Text</h1>
        <p>Inspect the text that was read from your PDF or image.</p>
    </div>
    """, unsafe_allow_html=True)

    st.text_area(
        "Extracted content",
        value=report_text,
        height=450,
        disabled=True,
        key="extracted_report_text_view",
    )

    st.download_button(
        "⬇ Download extracted text",
        data=report_text,
        file_name="extracted_report.txt",
        mime="text/plain",
    )

    st.caption(
        "OCR may misread characters, numbers, dates, units or medication "
        "names. Compare important details with the original document."
    )
