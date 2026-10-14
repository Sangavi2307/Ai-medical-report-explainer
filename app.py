
import re
from datetime import datetime

import pandas as pd
import streamlit as st

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report
from report_generator import generate_pdf_report
from ai_explainer import ai_explain_report


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
# PROFESSIONAL DESIGN
# =========================================================

st.markdown(
    """
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: Inter, sans-serif;
    }

    .stApp {
        background: #f4f7fc;
        color: #243b53;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #102344, #1b3761);
    }

    [data-testid="stSidebar"] * {
        color: #f3f7ff;
    }

    .main .block-container {
        max-width: 1450px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(115deg, #ffffff, #e8f3ff);
        border: 1px solid #dce8f8;
        border-radius: 18px;
        padding: 26px;
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
        background: #ffffff;
        border: 1px solid #e1eaf5;
        border-radius: 15px;
        padding: 18px;
        min-height: 125px;
        box-shadow: 0 3px 12px rgba(25, 55, 90, 0.04);
    }

    .metric-label {
        color: #64748b;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .metric-value {
        color: #17365e;
        font-size: 25px;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .metric-note {
        color: #718096;
        font-size: 12px;
        margin-top: 8px;
    }

    .section-card {
        background: white;
        border: 1px solid #e1eaf5;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .section-heading {
        color: #17365e;
        font-size: 19px;
        font-weight: 750;
        margin-bottom: 12px;
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
    """,
    unsafe_allow_html=True,
)


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
    """Extract a field only when a matching label exists."""
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


def get_result_counts(df):
    """Count statuses only when they are explicitly provided."""
    if not isinstance(df, pd.DataFrame) or df.empty:
        return 0, 0, 0, 0

    total = len(df)

    if "Status" not in df.columns:
        return total, 0, 0, total

    status = (
        df["Status"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    normal_labels = {
        "normal",
        "within range",
        "within normal range",
    }

    abnormal_labels = {
        "high",
        "low",
        "above range",
        "below range",
        "abnormal",
    }

    normal = int(status.isin(normal_labels).sum())
    abnormal = int(status.isin(abnormal_labels).sum())
    unclassified = total - normal - abnormal

    return total, normal, abnormal, unclassified


def render_laboratory_table(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        st.info(
            "No laboratory values were recognized. "
            "This does not mean the report is normal. "
            "Check the extracted text and original report."
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


def reset_current_report():
    st.session_state.report_text = ""
    st.session_state.results_df = pd.DataFrame()
    st.session_state.ai_explanation = ""
    st.session_state.report_name = ""
    st.session_state.processed_at = ""


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.markdown("# 🩺 MediLens")
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
    )

    st.divider()

    st.markdown("### About MediLens")
    st.caption(
        "Organizes information extracted from a medical report "
        "to make it easier to review."
    )

    if st.button("🗑 Clear current report", use_container_width=True):
        reset_current_report()
        st.rerun()

    st.divider()
    st.caption("Version 2.1 · Educational use only")


# =========================================================
# ACTIVE REPORT DATA
# =========================================================

report_text = st.session_state.report_text
results_df = st.session_state.results_df
explanation = st.session_state.ai_explanation


# =========================================================
# UPLOAD REPORT PAGE
# =========================================================

if page == "Upload Report":

    st.markdown(
        """
        <div class="hero">
            <h1>Upload Medical Report</h1>
            <p>Upload a PDF or image, or paste your report text.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="info-banner">
            Supported formats: PDF, PNG, JPG and JPEG.
            Upload only reports you are authorized to use.
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a medical report",
        type=["pdf", "png", "jpg", "jpeg"],
        key="medical_report_upload",
    )

    pasted_text = st.text_area(
        "Or paste report text",
        height=200,
        placeholder=(
            "Paste patient details, laboratory tests, results, "
            "units and reference ranges here..."
        ),
        key="medical_report_pasted_text",
    )

    st.caption(
        "Uploading a new report replaces the active report."
    )

    if st.button(
        "Analyze this report",
        type="primary",
        use_container_width=True,
    ):

        new_report_text = ""
        new_report_name = ""

        # Prefer the selected file if both inputs are provided.
        if uploaded_file is not None:
            new_report_name = uploaded_file.name
            file_name = uploaded_file.name.lower()

            try:
                with st.spinner("Reading your medical report..."):
                    if file_name.endswith(".pdf"):
                        new_report_text = extract_text_from_pdf(
                            uploaded_file
                        )
                    else:
                        new_report_text = extract_text_from_image(
                            uploaded_file
                        )

            except Exception as error:
                st.error(f"Could not read the file: {error}")

        elif pasted_text.strip():
            new_report_text = pasted_text.strip()
            new_report_name = "Pasted report"

        else:
            st.error("Please upload a report or paste its text.")

        if new_report_text and new_report_text.strip():

            new_report_text = new_report_text.strip()

            if new_report_text.startswith(
                "No selectable text was found"
            ):
                st.error(
                    "No selectable text was found in this PDF. "
                    "Try a clearer image or paste the report text."
                )

            else:
                # Clear previous results before analyzing new content.
                reset_current_report()

                st.session_state.report_text = new_report_text
                st.session_state.report_name = new_report_name
                st.session_state.processed_at = datetime.now().strftime(
                    "%d %b %Y, %I:%M %p"
                )

                try:
                    with st.spinner("Analyzing this report..."):
                        lab_results = analyze_report(new_report_text)

                    if isinstance(lab_results, pd.DataFrame):
                        st.session_state.results_df = lab_results
                    else:
                        st.warning(
                            "The report was read, but the analyzer "
                            "did not return a DataFrame."
                        )

                except Exception as error:
                    st.warning(
                        "The report was read, but laboratory analysis "
                        f"could not finish: {error}"
                    )

                st.success(
                    "Report processed. Open Dashboard to review it."
                )
                st.rerun()


# =========================================================
# DASHBOARD PAGE
# =========================================================

elif page == "Dashboard":

    if not report_text:
        st.markdown(
            """
            <div class="hero">
                <h1>Welcome to MediLens 🩺</h1>
                <p>Your medical report information, organized in one place.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            "Upload a report to populate your dashboard. "
            "No sample patient data is shown."
        )

        if st.button("＋ Upload your first report", type="primary"):
            st.session_state["open_upload"] = True
            st.rerun()

    else:
        patient_name = find_patient_value(
            report_text,
            [r"patient name", r"name"],
        )
        age = find_patient_value(report_text, [r"age"])
        gender = find_patient_value(
            report_text,
            [r"gender", r"sex"],
        )

        total, normal, abnormal, unclassified = get_result_counts(
            results_df
        )

        st.markdown(
            """
            <div class="hero">
                <h1>Medical Report Dashboard</h1>
                <p>Review information extracted from your active report.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            f"Report: {st.session_state.report_name or 'Current report'}"
            f" · Processed: {st.session_state.processed_at or 'Not recorded'}"
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card(
                "PATIENT",
                safe_text(patient_name)[:24],
                "Extracted from report",
            )

        with c2:
            metric_card(
                "AGE",
                safe_text(age)[:18],
                "As written in report",
            )

        with c3:
            metric_card(
                "GENDER",
                safe_text(gender)[:18],
                "As written in report",
            )

        with c4:
            metric_card(
                "LAB RESULTS",
                total,
                "Recognized test rows",
            )

        st.markdown("### Report Overview")

        left, right = st.columns([1.5, 1])

        with left:
            st.markdown(
                """
                <div class="section-card">
                    <div class="section-heading">
                        📋 Report Status
                    </div>
                """,
                unsafe_allow_html=True,
            )

            st.write(
                "**Source:**",
                st.session_state.report_name or "Pasted text",
            )
            st.write("**Text extracted:** Yes")
            st.write(
                "**Laboratory analysis:**",
                "Results recognized" if total
                else "No recognized laboratory results",
            )
            st.write(
                "**Explanation:**",
                "Generated" if explanation else "Not generated yet",
            )

            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown(
                """
                <div class="section-card">
                    <div class="section-heading">
                        ⚡ Quick Actions
                    </div>
                """,
                unsafe_allow_html=True,
            )

            st.write(
                "Use the sidebar to open laboratory results, "
                "report summary, or extracted text."
            )

            st.markdown(
                """
                <div class="small-muted">
                    Verify patient details, dates, units, and ranges
                    against the original document.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### Laboratory Snapshot")

        if isinstance(results_df, pd.DataFrame) and not results_df.empty:
            render_laboratory_table(results_df.head(8))
        else:
            st.info(
                "No laboratory results are available yet. "
                "The report may still contain useful information."
            )

        st.markdown(
            """
            <div class="info-banner">
                <b>Important:</b> MediLens organizes extracted
                information for educational purposes. It does not
                diagnose diseases or recommend treatment.
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# LABORATORY RESULTS PAGE
# =========================================================

elif page == "Laboratory Results":

    st.markdown(
        """
        <div class="hero">
            <h1>Laboratory Results</h1>
            <p>Review recognized test values and supplied reference ranges.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not report_text:
        st.info("Upload a report first to view laboratory results.")

    elif isinstance(results_df, pd.DataFrame) and not results_df.empty:
        total, normal, abnormal, unclassified = get_result_counts(
            results_df
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card("TOTAL RESULTS", total, "Recognized rows")

        with c2:
            metric_card("WITHIN RANGE", normal, "Status supplied by analyzer")

        with c3:
            metric_card("OUTSIDE RANGE", abnormal, "Verify with a clinician")

        render_laboratory_table(results_df)

        if "Test" in results_df.columns and "Result" in results_df.columns:
            chart_df = results_df.copy()
            chart_df["Result"] = pd.to_numeric(
                chart_df["Result"],
                errors="coerce",
            )
            chart_df = chart_df.dropna(subset=["Result"])

            if not chart_df.empty:
                st.markdown("### Reported Numeric Values")

                st.caption(
                    "Different tests and units are not directly comparable. "
                    "This chart displays reported numbers, not a severity score."
                )

                # Only display a chart for a manageable number of rows.
                chart_df = chart_df.head(20).set_index("Test")
                st.bar_chart(chart_df["Result"])

    elif report_text:
        st.info(
            "No laboratory values were recognized. Check the extracted "
            "text. Your analyzer may need additional rules for this report."
        )


# =========================================================
# REPORT SUMMARY PAGE
# =========================================================

elif page == "Report Summary":

    st.markdown(
        """
        <div class="hero">
            <h1>Complete Report Summary</h1>
            <p>Organize the information extracted from your report.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not report_text:
        st.info("Upload a report first to generate its summary.")

    else:
        st.info(
            "This feature uses your existing explanation module. "
            "It does not require paid AI API credits if that module "
            "uses local rules."
        )

        if st.button(
            "Generate report explanation",
            type="primary",
        ):
            try:
                with st.spinner("Organizing report information..."):
                    result = ai_explain_report(
                        report_text,
                        results_df,
                    )

                st.session_state.ai_explanation = (
                    str(result)
                    if result
                    else "No explanation was returned."
                )

            except Exception as error:
                st.error(
                    f"Could not generate the explanation: {error}"
                )

        if st.session_state.ai_explanation:
            st.markdown(st.session_state.ai_explanation)

            st.download_button(
                "⬇ Download explanation (Markdown)",
                data=st.session_state.ai_explanation,
                file_name="medical_report_explanation.md",
                mime="text/markdown",
            )

   