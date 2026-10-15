
import io
import re

import pandas as pd
import streamlit as st

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import explain_report


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MediLens | Medical Report Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# CLINICAL NAVY + MEDICAL TEAL DESIGN
# =========================================================

st.markdown(
    """
    <style>
    :root {
        --clinical-navy: #16324F;
        --deep-navy: #10263D;
        --medical-teal: #0F9D91;
        --teal-dark: #087F78;
        --pale-blue: #EAF4FB;
        --page-bg: #F4F8FC;
        --white: #FFFFFF;
        --text: #25384A;
        --muted: #6B7C8F;
        --border: #DCE6EF;
        --normal: #198754;
        --warning: #D99000;
        --alert: #C83E4D;
    }

    .stApp {
        background-color: var(--page-bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(244, 248, 252, 0.95);
    }

    .block-container {
        max-width: 1440px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: var(--clinical-navy) !important;
        font-weight: 750 !important;
    }

    p, label, li {
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background: var(--deep-navy);
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    /* Brand header */
    .brand-row {
        display: flex;
        align-items: center;
        gap: 13px;
        margin-bottom: 20px;
    }

    .brand-icon {
        width: 52px;
        height: 52px;
        border-radius: 15px;
        background: var(--medical-teal);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 27px;
        font-weight: bold;
    }

    .brand-title {
        color: var(--clinical-navy);
        font-size: 27px;
        font-weight: 800;
        line-height: 1.2;
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: 13px;
        margin-top: 3px;
    }

    /* Hero banner */
    .hero {
        background: linear-gradient(
            115deg,
            #10263D 0%,
            #163E5A 58%,
            #087F78 100%
        );
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 28px rgba(16, 38, 61, 0.12);
    }

    .hero h1 {
        color: white !important;
        font-size: 31px;
        margin: 0 0 10px 0;
    }

    .hero p {
        color: #E0F2F1;
        font-size: 15px;
        margin: 0;
        line-height: 1.7;
    }

    .hero-tag {
        display: inline-block;
        padding: 6px 11px;
        border: 1px solid rgba(255,255,255,0.28);
        background: rgba(255,255,255,0.09);
        border-radius: 30px;
        color: #FFFFFF;
        font-size: 12px;
        margin-bottom: 13px;
    }

    /* Section heading */
    .section-title {
        font-size: 21px;
        font-weight: 800;
        color: var(--clinical-navy);
        margin: 24px 0 5px 0;
    }

    .section-subtitle {
        color: var(--muted);
        font-size: 13px;
        margin-bottom: 15px;
    }

    /* Cards */
    .panel {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 3px 12px rgba(22, 50, 79, 0.035);
    }

    .panel-title {
        color: var(--clinical-navy);
        font-size: 17px;
        font-weight: 750;
        margin-bottom: 8px;
    }

    .panel-text {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.6;
    }

    /* Status labels */
    .status {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 7px;
        font-size: 12px;
        font-weight: 750;
    }

    .status-normal {
        color: #146C43;
        background: #DDF4E7;
    }

    .status-high {
        color: #8A5700;
        background: #FFF0C2;
    }

    .status-low {
        color: #9E2634;
        background: #FCE3E6;
    }

    .status-other {
        color: #38566F;
        background: #E5EFF7;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        background: var(--medical-teal);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        min-height: 43px;
        transition: 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: var(--teal-dark);
        color: white;
        border: none;
    }

    /* Upload area */
    [data-testid="stFileUploader"] {
        background: white;
        border: 1px dashed #9CB9C9;
        border-radius: 13px;
        padding: 12px;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 17px;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    [data-testid="stMetricValue"] {
        color: var(--clinical-navy);
        font-weight: 800;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid var(--border);
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--muted);
        font-weight: 650;
    }

    .stTabs [aria-selected="true"] {
        color: var(--teal-dark) !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
        margin-bottom: 8px;
    }

    /* Footer */
    .footer {
        margin-top: 35px;
        padding: 22px 0;
        border-top: 1px solid var(--border);
        text-align: center;
        color: var(--muted);
        font-size: 12px;
        line-height: 1.8;
    }

    .disclaimer {
        background: #FFF7E6;
        border: 1px solid #F1D69A;
        color: #76530C;
        padding: 14px 16px;
        border-radius: 12px;
        font-size: 12px;
        line-height: 1.7;
        margin-top: 18px;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }

        .hero {
            padding: 22px;
        }

        .hero h1 {
            font-size: 25px;
        }

        .brand-title {
            font-size: 23px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_text(value):
    """Convert missing or invalid values into readable text."""
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    return str(value).strip()


def normalize_status(value):
    """Normalize common result status labels."""
    status = safe_text(value).lower()

    if any(word in status for word in [
        "normal", "within range", "within normal", "in range"
    ]):
        return "Normal"

    if any(word in status for word in [
        "high", "above", "elevated", "increased"
    ]):
        return "High"

    if any(word in status for word in [
        "low", "below", "decreased"
    ]):
        return "Low"

    if any(word in status for word in [
        "critical", "abnormal", "positive", "negative"
    ]):
        return status.title()

    return "Not specified"


def normalize_dataframe(data):
    """Convert analyzer output into a consistent table format."""
    if isinstance(data, pd.DataFrame):
        df = data.copy()

    elif isinstance(data, list):
        df = pd.DataFrame(data)

    elif isinstance(data, dict):
        df = pd.DataFrame(data)

    else:
        return pd.DataFrame(
            columns=[
                "Test", "Result", "Unit",
                "Reference Range", "Status"
            ]
        )

    if df.empty:
        return pd.DataFrame(
            columns=[
                "Test", "Result", "Unit",
                "Reference Range", "Status"
            ]
        )

    # Map common column-name variations.
    aliases = {
        "test": "Test",
        "test name": "Test",
        "parameter": "Test",
        "investigation": "Test",
        "result": "Result",
        "value": "Result",
        "observed value": "Result",
        "unit": "Unit",
        "reference range": "Reference Range",
        "normal range": "Reference Range",
        "ref range": "Reference Range",
        "range": "Reference Range",
        "status": "Status",
        "flag": "Status",
        "interpretation": "Status",
    }

    rename_map = {}

    for column in df.columns:
        key = str(column).strip().lower()
        if key in aliases:
            rename_map[column] = aliases[key]

    df = df.rename(columns=rename_map)

    # Avoid duplicate column names after renaming.
    df = df.loc[:, ~df.columns.duplicated()]

    required_columns = [
        "Test", "Result", "Unit", "Reference Range", "Status"
    ]

    for column in required_columns:
        if column not in df.columns:
            df[column] = ""

    df = df[required_columns].copy()

    for column in required_columns:
        df[column] = df[column].apply(safe_text)

    # Remove empty rows.
    df = df[
        (df["Test"] != "") |
        (df["Result"] != "")
    ].reset_index(drop=True)

    df["Status"] = df["Status"].apply(normalize_status)

    return df


def extract_report_text(uploaded_file):
    """Extract text from a PDF or image using existing project modules."""
    filename = uploaded_file.name.lower()
    extracted_text = ""

    if filename.endswith(".pdf"):
        try:
            uploaded_file.seek(0)
            extracted_text = extract_text_from_pdf(uploaded_file)
        except Exception:
            extracted_text = ""

        # If a PDF has no selectable text, try the optional OCR function.
        if not safe_text(extracted_text):
            try:
                from ocr_service import extract_text_from_scanned_pdf

                uploaded_file.seek(0)
                extracted_text = extract_text_from_scanned_pdf(
                    uploaded_file
                )
            except ImportError:
                pass
            except Exception:
                pass

    elif filename.endswith((".png", ".jpg", ".jpeg", ".webp")):
        try:
            uploaded_file.seek(0)
            extracted_text = extract_text_from_image(uploaded_file)
        except Exception as error:
            st.error(f"Image text extraction failed: {error}")
            return ""

    return safe_text(extracted_text)


def get_patient_info(report_text):
    """Read patient fields without inventing missing personal information."""
    try:
        info = extract_patient_fields(report_text)
        if isinstance(info, dict):
            return info
    except Exception:
        pass

    return {}


def create_csv(df):
    """Create a downloadable CSV from this report's results."""
    return df.to_csv(index=False).encode("utf-8-sig")


def create_pdf(patient_info, results_df):
    """Create a simple PDF summary of this report."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )

        output = io.BytesIO()

        document = SimpleDocTemplate(
            output,
            pagesize=A4,
            rightMargin=32,
            leftMargin=32,
            topMargin=32,
            bottomMargin=32,
        )

        styles = getSampleStyleSheet()
        story = []

        story.append(
            Paragraph(
                "MediLens - Medical Report Summary",
                styles["Title"],
            )
        )
        story.append(Spacer(1, 12))

        for key, value in patient_info.items():
            value = safe_text(value)
            if value:
                story.append(
                    Paragraph(
                        f"<b>{safe_text(key)}:</b> {value}",
                        styles["BodyText"],
                    )
                )

        story.append(Spacer(1, 14))

        table_data = [
            [
                "Test",
                "Result",
                "Unit",
                "Reference Range",
                "Status",
            ]
        ]

        for _, row in results_df.iterrows():
            table_data.append([
                safe_text(row["Test"]),
                safe_text(row["Result"]),
                safe_text(row["Unit"]),
                safe_text(row["Reference Range"]),
                safe_text(row["Status"]),
            ])

        table = Table(
            table_data,
            repeatRows=1,
            colWidths=[105, 70, 45, 105, 75],
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#16324F"),
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DCE6EF")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                    colors.white,
                    colors.HexColor("#F4F8FC"),
                ]),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ])
        )

        story.append(table)
        story.append(Spacer(1, 18))
        story.append(
            Paragraph(
                "Educational information only. This document does not "
                "provide a diagnosis or replace advice from a qualified "
                "healthcare professional.",
                styles["BodyText"],
            )
        )

        document.build(story)
        output.seek(0)
        return output.getvalue()

    except Exception as error:
        st.error(f"Could not create PDF: {error}")
        return None


def display_status(status):
    """Display a colored, readable status label."""
    status = normalize_status(status)

    if status == "Normal":
        css_class = "status-normal"
    elif status == "High":
        css_class = "status-high"
    elif status == "Low":
        css_class = "status-low"
    else:
        css_class = "status-other"

    st.markdown(
        f'<span class="status {css_class}">{status}</span>',
        unsafe_allow_html=True,
    )


def safe_explanation(report_text):
    """Get the rule-based explanation for this uploaded report."""
    try:
        result = explain_report(report_text)
        if isinstance(result, dict):
            return result
    except Exception as error:
        st.warning(f"Detailed explanation could not be generated: {error}")

    return {}


# =========================================================
# BRAND HEADER
# =========================================================

st.markdown(
    """
    <div class="brand-row">
        <div class="brand-icon">✚</div>
        <div>
            <div class="brand-title">MediLens</div>
            <div class="brand-subtitle">
                AI Medical Report Explainer · Understand your report clearly
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HERO BANNER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <span class="hero-tag">PATIENT-CENTRED REPORT INSIGHTS</span>
        <h1>Your medical report, made easier to understand.</h1>
        <p>
            Upload one medical report to extract its text, review detected
            test results, and read simple explanations. Your dashboard
            analyses the report you upload in this session.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# UPLOAD SECTION
# =========================================================

st.markdown(
    '<div class="section-title">Upload your report</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Supported formats: PDF, PNG, JPG, JPEG and WEBP. '
    'Use a clear, readable report.'
    '</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choose one medical report",
    type=["pdf", "png", "jpg", "jpeg", "webp"],
    accept_multiple_files=False,
    help="Upload only the report you want to analyse.",
)


# =========================================================
# ANALYSE THE CURRENT UPLOAD ONLY
# =========================================================

if uploaded_file is None:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Welcome to MediLens</div>
            <div class="panel-text">
                Your dashboard is ready. Upload a report above to view
                the patient details detected in that file, test results,
                charts, and explanations.
                <br><br>
                No report is analysed until you upload one.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="disclaimer">
            <b>Important:</b> MediLens is an educational report-explanation
            tool. It is not a diagnostic system and must not be used to
            make treatment decisions.
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    # Read only the currently uploaded file.
    with st.spinner("Reading the uploaded report..."):
        report_text = extract_report_text(uploaded_file)

    if not report_text:
        st.error(
            "No readable text was extracted from this file. "
            "Try a clearer image or a text-based PDF. "
            "Scanned PDF support also requires working OCR configuration."
        )
        st.stop()

    # Analyse only the text extracted from this uploaded report.
    with st.spinner("Analysing this report..."):
        try:
            raw_results = analyze_report(report_text)
            results_df = normalize_dataframe(raw_results)
        except Exception as error:
            st.error(f"Report analysis failed: {error}")
            st.stop()

        patient_info = get_patient_info(report_text)
        explanation_data = safe_explanation(report_text)

    # -----------------------------------------------------
    # PATIENT / REPORT INFORMATION
    # -----------------------------------------------------

    st.markdown(
        '<div class="section-title">Report overview</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Information extracted from the currently uploaded file.'
        '</div>',
        unsafe_allow_html=True,
    )

    patient_name = (
        patient_info.get("Patient Name")
        or patient_info.get("Name")
        or patient_info.get("patient")
        or "Not detected"
    )

    patient_age = (
        patient_info.get("Age")
        or patient_info.get("Patient Age")
        or "Not detected"
    )

    patient_gender = (
        patient_info.get("Gender")
        or patient_info.get("Sex")
        or "Not detected"
    )

    report_date = (
        patient_info.get("Report Date")
        or patient_info.get("Date")
        or "Not detected"
    )

    patient_col1, patient_col2 = st.columns(2)

    with patient_col1:
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-title">Patient information</div>
                <div class="panel-text">
                    <b>Name:</b> {safe_text(patient_name)}<br>
                    <b>Age:</b> {safe_text(patient_age)}<br>
                    <b>Gender:</b> {safe_text(patient_gender)}<br>
                    <b>Report date:</b> {safe_text(report_date)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with patient_col2:
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-title">Uploaded file</div>
                <div class="panel-text">
                    <b>File name:</b> {safe_text(uploaded_file.name)}<br>
                    <b>File type:</b> {safe_text(uploaded_file.type)}<br>
                    <b>Extracted characters:</b> {len(report_text):,}<br>
                    <b>Detected test rows:</b> {len(results_df)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    normal_count = int((results_df["Status"] == "Normal").sum())
    high_count = int((results_df["Status"] == "High").sum())
    low_count = int((results_df["Status"] == "Low").sum())
    other_count = len(results_df) - normal_count - high_count - low_count

    st.markdown(
        '<div class="section-title">Clinical snapshot</div>',
        unsafe_allow_html=True,
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric("Detected tests", len(results_df))
    metric2.metric("Within range", normal_count)
    metric3.metric("High results", high_count)
    metric4.metric("Low results", low_count)

    if results_df.empty:
        st.warning(
            "Text was extracted, but no structured test results were "
            "detected. Review the extracted text below. The parser may "
            "need additional rules for this report format."
        )

    # -----------------------------------------------------
    # MAIN DASHBOARD TABS
    # -----------------------------------------------------

    tab_results, tab_analytics, tab_explanations, tab_downloads = st.tabs(
        [
            "📋 Results",
            "📊 Analytics",
            "🩺 Explanations",
            "⬇️ Downloads",
        ]
    )

    # =====================================================
    # TAB 1: RESULTS
    # =====================================================

    with tab_results:
        st.markdown(
            '<div class="section-title">Detected test results</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-subtitle">'
            'These rows are generated from the currently uploaded report. '
            'Check units and reference ranges against the original document.'
            '</div>',
            unsafe_allow_html=True,
        )

        if not results_df.empty:
            filter_options = [
                "All results",
                "Normal",
                "High",
                "Low",
                "Not specified",
            ]

            selected_filter = st.selectbox(
                "Filter results by status",
                options=filter_options,
            )

            if selected_filter == "All results":
                filtered_df = results_df.copy()
            else:
                filtered_df = results_df[
                    results_df["Status"] == selected_filter
                ].copy()

            search_term = st.text_input(
                "Search test name",
                placeholder="Example: glucose, haemoglobin...",
            )

            if search_term:
                filtered_df = filtered_df[
                    filtered_df["Test"].str.contains(
                        search_term,
                        case=False,
                        na=False,
                    )
                ]

            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                f"Showing {len(filtered_df)} of {len(results_df)} "
                "detected rows."
            )

        else:
            st.info(
                "There are no structured results to display yet."
            )

    # =====================================================
    # TAB 2: ANALYTICS
    # =====================================================

    with tab_analytics:
        st.markdown(
            '<div class="section-title">Result analytics</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-subtitle">'
            'A status summary of the results detected in this report.'
            '</div>',
            unsafe_allow_html=True,
        )

        if not results_df.empty:
            chart_data = pd.DataFrame({
                "Status": [
                    "Normal",
                    "High",
                    "Low",
                    "Other / unspecified",
                ],
                "Count": [
                    normal_count,
                    high_count,
                    low_count,
                    other_count,
                ],
            })

            chart_data = chart_data[chart_data["Count"] > 0]

            if not chart_data.empty:
                chart_col1, chart_col2 = st.columns([1, 1])

                with chart_col1:
                    st.markdown(
                        '<div class="panel-title">Status distribution</div>',
                        unsafe_allow_html=True,
                    )
                    st.bar_chart(
                        chart_data.set_index("Status"),
                        color="#0F9D91",
                    )

                with chart_col2:
                    st.markdown(
                        '<div class="panel-title">Result summary</div>',
                        unsafe_allow_html=True,
                    )
                    st.dataframe(
                        chart_data,
                        use_container_width=True,
                        hide_index=True,
                    )

            st.info(
                "Status counts depend on the analyzer's classification. "
                "They are not a diagnosis or a measure of overall health."
            )

        else:
            st.info(
                "Analytics will appear when structured test results "
                "are detected."
            )

    # =====================================================
    # TAB 3: EXPLANATIONS
    # =====================================================

    with tab_explanations:
        st.markdown(
            '<div class="section-title">Understand your results</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Plain-language explanations from the project’s built-in '
            'medical information rules.'
            '</div>',
            unsafe_allow_html=True,
        )

        summary = safe_text(explanation_data.get("summary"))

        if summary:
            st.markdown(
                f"""
                <div class="panel">
                    <div class="panel-title">Report summary</div>
                    <div class="panel-text">{summary}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        detailed_results = explanation_data.get("results", [])

        if isinstance(detailed_results, pd.DataFrame):
            detailed_results = detailed_results.to_dict("records")

        if isinstance(detailed_results, list) and detailed_results:
            for index, item in enumerate(detailed_results, start=1):
                if not isinstance(item, dict):
                    continue

                test_name = (
                    item.get("Test")
                    or item.get("test")
                    or f"Test {index}"
                )

                result_value = (
                    item.get("Result")
                    or item.get("result")
                    or "Not detected"
                )

                status_value = (
                    item.get("Status")
                    or item.get("status")
                    or "Not specified"
                )

                with st.expander(
                    f"{test_name} — {result_value}",
                    expanded=False,
                ):
                    st.write("**Status**")
                    display_status(status_value)

                    fields_to_show = [
                        ("Reference Range", "Reference Range"),
                        ("Meaning", "Meaning"),
                        ("Importance", "Importance"),
                        ("Interpretation", "Interpretation"),
                        ("Possible Causes", "Possible Causes"),
                        ("Follow-up", "Follow-up"),
                    ]

                    for field_key, label in fields_to_show:
                        field_value = safe_text(
                            item.get(field_key)
                            or item.get(field_key.lower())
                        )

                        if field_value:
                            st.markdown(f"**{label}**")
                            st.write(field_value)

        elif not results_df.empty:
            st.info(
                "Detailed explanations were not returned for these rows. "
                "The detected results are still available in the Results tab."
            )

            for _, row in results_df.iterrows():
                with st.expander(
                    f"{row['Test']} — {row['Result']}",
                    expanded=False,
                ):
                    st.write(f"**Unit:** {row['Unit'] or 'Not specified'}")
                    st.write(
                        "**Reference range:** "
                        f"{row['Reference Range'] or 'Not specified'}"
                    )
                    st.write("**Status:**")
                    display_status(row["Status"])

        general_notes = explanation_data.get("general_notes", [])

        if isinstance(general_notes, str):
            general_notes = [general_notes]

        if isinstance(general_notes, list) and general_notes:
            st.markdown("#### General notes")

            for note in general_notes:
                if safe_text(note):
                    st.markdown(f"- {safe_text(note)}")

        if not summary and not detailed_results and not general_notes:
            st.info(
                "No detailed explanation was produced for this report. "
                "Review the detected results and extracted text."
            )

    # =====================================================
    # TAB 4: DOWNLOADS
    # =====================================================

    with tab_downloads:
        st.markdown(
            '<div class="section-title">Export this report analysis</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Download the detected results from the currently uploaded file.'
            '</div>',
            unsafe_allow_html=True,
        )

        if not results_df.empty:
            st.download_button(
                label="⬇️ Download results as CSV",
                data=create_csv(results_df),
                file_name="medilens_report_results.csv",
                mime="text/csv",
                use_container_width=True,
            )

            pdf_bytes = create_pdf(patient_info, results_df)

            if pdf_bytes:
                st.download_button(
                    label="⬇️ Download summary as PDF",
                    data=pdf_bytes,
                    file_name="medilens_report_summary.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

        else:
            st.info(
                "There are no structured test rows to export. "
                "Check the extracted text below."
            )

    # -----------------------------------------------------
    # EXTRACTED SOURCE TEXT
    # -----------------------------------------------------

    with st.expander("View extracted text from this upload"):
        st.caption(
            "Use this section to check whether OCR or PDF extraction "
            "read the report correctly."
        )
        st.text_area(
            "Extracted report text",
            value=report_text,
            height=300,
            disabled=True,
        )

    # -----------------------------------------------------
    # MEDICAL DISCLAIMER
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="disclaimer">
            <b>Medical information notice</b><br>
            MediLens is an educational tool that helps explain information
            extracted from a medical report. It may misread scanned text,
            miss tests, or classify results incorrectly. Reference ranges
            can vary by laboratory, age, sex, and clinical context.
            This application does not diagnose disease or recommend
            treatment. Consult a qualified healthcare professional for
            interpretation and medical decisions.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        <b style="color:#16324F;">MediLens</b>
        · Clinical Navy & Medical Teal Dashboard<br>
        Designed to make medical reports easier to understand.<br>
        Educational use only · Not a substitute for professional medical care
    </div>
    """,
    unsafe_allow_html=True,
)
```
