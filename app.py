
import io
import re
from datetime import datetime

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
    page_title="MediLens | Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# PROFESSIONAL WEBSITE DESIGN
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --navy: #123047;
        --teal: #0d9488;
        --teal-light: #e6f7f5;
        --text: #203449;
        --muted: #718096;
        --border: #e5edf2;
        --background: #f5f9fc;
        --white: #ffffff;
    }

    html {
        scroll-behavior: smooth;
    }

    .stApp {
        background: var(--background);
        color: var(--text);
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(245, 249, 252, 0.96);
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .block-container {
        max-width: 1220px;
        padding-top: 1.2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        color: var(--navy) !important;
        letter-spacing: -0.5px;
    }

    p, label, li {
        font-family: 'DM Sans', sans-serif;
    }

    /* Top navigation */

    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 15px 0 20px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 28px;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-icon {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 46px;
        height: 46px;
        border-radius: 15px;
        background: var(--teal-light);
        font-size: 25px;
    }

    .brand-name {
        font-family: 'Manrope', sans-serif;
        font-size: 24px;
        font-weight: 800;
        color: var(--navy);
        line-height: 1.15;
    }

    .brand-subtitle {
        font-size: 12px;
        color: var(--muted);
        margin-top: 4px;
    }

    .nav-links {
        display: flex;
        gap: 23px;
        align-items: center;
        flex-wrap: wrap;
    }

    .nav-links a {
        color: #52677b;
        text-decoration: none;
        font-size: 14px;
        font-weight: 600;
    }

    .nav-links a:hover {
        color: var(--teal);
    }

    .privacy-pill {
        background: var(--teal-light);
        color: #087e75;
        padding: 8px 12px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 700;
        white-space: nowrap;
    }

    /* Hero */

    .hero {
        background: linear-gradient(120deg, #102e45 0%, #16465b 62%, #0d817d 100%);
        padding: 46px 42px;
        border-radius: 25px;
        margin-bottom: 28px;
        color: white;
        position: relative;
        overflow: hidden;
    }

    .hero-eyebrow {
        color: #a7eee5;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 15px;
    }

    .hero h1 {
        color: white !important;
        font-size: clamp(30px, 4vw, 47px);
        line-height: 1.16;
        max-width: 690px;
        margin: 0 0 16px;
    }

    .hero p {
        color: #d7e8ef;
        font-size: 16px;
        line-height: 1.8;
        max-width: 660px;
        margin-bottom: 0;
    }

    .hero-note {
        margin-top: 23px;
        display: inline-block;
        border: 1px solid rgba(255,255,255,.23);
        background: rgba(255,255,255,.08);
        color: #ecffff;
        border-radius: 30px;
        padding: 9px 14px;
        font-size: 12px;
    }

    /* Section headings */

    .section-heading {
        font-family: 'Manrope', sans-serif;
        font-size: 23px;
        font-weight: 800;
        color: var(--navy);
        margin: 10px 0 7px;
    }

    .section-subtitle {
        font-size: 14px;
        line-height: 1.7;
        color: var(--muted);
        margin-bottom: 19px;
    }

    /* Cards */

    .panel {
        background: white;
        border: 1px solid var(--border);
        border-radius: 19px;
        padding: 23px;
        margin-bottom: 18px;
        box-shadow: 0 5px 20px rgba(22, 55, 78, 0.025);
    }

    .metric-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 17px;
        padding: 21px;
        min-height: 126px;
    }

    .metric-label {
        color: #718096;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .metric-value {
        font-family: 'Manrope', sans-serif;
        font-size: 30px;
        font-weight: 800;
        color: var(--navy);
        line-height: 1.15;
    }

    .metric-caption {
        color: #8796a5;
        font-size: 12px;
        margin-top: 9px;
    }

    .status-normal {
        color: #087f5b;
        background: #e7f8ef;
        border-radius: 8px;
        padding: 5px 9px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }

    .status-high {
        color: #b42318;
        background: #fff0ed;
        border-radius: 8px;
        padding: 5px 9px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }

    .status-low {
        color: #9a6700;
        background: #fff7df;
        border-radius: 8px;
        padding: 5px 9px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }

    .status-unknown {
        color: #52677b;
        background: #eef2f6;
        border-radius: 8px;
        padding: 5px 9px;
        font-weight: 700;
        font-size: 12px;
        display: inline-block;
    }

    /* Streamlit inputs and buttons */

    [data-testid="stFileUploader"] {
        background: #f9fcfd;
        border: 1.5px dashed #9ccbc9;
        border-radius: 16px;
        padding: 12px;
    }

    [data-testid="stFileUploader"] section {
        background: transparent;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 11px;
        min-height: 44px;
        font-weight: 700;
        border: 1px solid #0d9488;
        transition: all 0.2s ease;
    }

    .stButton > button[kind="primary"] {
        background: #0d9488;
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background: #087e75;
        border-color: #087e75;
    }

    .stDownloadButton > button {
        background: white;
        color: #0d8179;
    }

    .stDownloadButton > button:hover {
        background: #e6f7f5;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }

    .disclaimer {
        background: #fff9e9;
        border: 1px solid #f0dfaa;
        color: #775b19;
        padding: 17px 19px;
        border-radius: 13px;
        font-size: 13px;
        line-height: 1.7;
        margin-top: 20px;
    }

    .footer {
        border-top: 1px solid var(--border);
        margin-top: 45px;
        padding-top: 22px;
        color: #7b8b99;
        text-align: center;
        font-size: 12px;
        line-height: 1.8;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .top-nav {
            align-items: flex-start;
            flex-direction: column;
        }

        .nav-links {
            gap: 14px;
        }

        .hero {
            padding: 29px 23px;
            border-radius: 18px;
        }

        .hero p {
            font-size: 14px;
        }

        .panel {
            padding: 17px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# WEBSITE HEADER
# =========================================================

st.markdown(
    """
    <div class="top-nav">
        <div class="brand">
            <div class="brand-icon">🩺</div>
            <div>
                <div class="brand-name">MediLens</div>
                <div class="brand-subtitle">Medical Report Explainer</div>
            </div>
        </div>
        <div class="nav-links">
            <a href="#home">Home</a>
            <a href="#analyze">Analyze Report</a>
            <a href="#features">Features</a>
            <a href="#about">About</a>
        </div>
        <div class="privacy-pill">✦ Built for clarity</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div id="home"></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">YOUR HEALTH, MADE CLEARER</div>
        <h1>Understand your medical reports with confidence.</h1>
        <p>
            Upload a laboratory report to organize extracted test results,
            review reference ranges, and read simple explanations in one place.
        </p>
        <div class="hero-note">
            🔒 Report analysis is provided for educational purposes
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_text(value, default="Not provided"):
    """Return a readable value without displaying Python NaN."""
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass

    value = str(value).strip()
    return value if value else default


def normalize_status(status):
    """Map status text to a consistent category."""
    value = safe_text(status, "").lower()

    if any(word in value for word in ["within range", "normal"]):
        return "normal"

    if any(word in value for word in ["below range", "low"]):
        return "low"

    if any(word in value for word in ["above range", "high"]):
        return "high"

    return "unknown"


def normalize_dataframe(data):
    """Make analyzer output safe to display."""
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        df = pd.DataFrame(data)

    # Handle common column-name variations.
    rename_map = {}

    for column in df.columns:
        key = str(column).strip().lower().replace("_", " ")

        if key in ["test", "test name", "parameter", "investigation"]:
            rename_map[column] = "Test"
        elif key in ["result", "value", "observed value"]:
            rename_map[column] = "Result"
        elif key in ["unit", "units"]:
            rename_map[column] = "Unit"
        elif key in [
            "reference range",
            "normal range",
            "ref range",
            "reference",
        ]:
            rename_map[column] = "Reference Range"
        elif key in ["status", "flag", "interpretation"]:
            rename_map[column] = "Status"

    df = df.rename(columns=rename_map)

    for column in ["Test", "Result", "Unit", "Reference Range", "Status"]:
        if column not in df.columns:
            df[column] = ""

    df = df[["Test", "Result", "Unit", "Reference Range", "Status"]]

    df["Test"] = df["Test"].fillna("").astype(str).str.strip()
    df = df[df["Test"] != ""]

    return df.reset_index(drop=True)


def get_patient_fields(report_text):
    """Extract patient information without breaking older modules."""
    try:
        fields = extract_patient_fields(report_text)
        return fields if isinstance(fields, dict) else {}
    except Exception:
        return {}


def extract_report_text(uploaded_file):
    """Use the project's existing PDF/image extraction modules."""
    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        try:
            uploaded_file.seek(0)
            text = extract_text_from_pdf(uploaded_file)
            if text and str(text).strip():
                return str(text).strip()
        except Exception:
            pass

        # If normal PDF extraction returns no text, try scanned-PDF OCR.
        try:
            from ocr_service import extract_text_from_scanned_pdf

            uploaded_file.seek(0)
            text = extract_text_from_scanned_pdf(uploaded_file)
            if text and str(text).strip():
                return str(text).strip()
        except (ImportError, AttributeError):
            pass

    else:
        uploaded_file.seek(0)
        text = extract_text_from_image(uploaded_file)
        if text and str(text).strip():
            return str(text).strip()

    return ""


def make_pdf(report, patient, results_df, detailed_results):
    """Build a downloadable PDF using ReportLab."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        KeepTogether,
    )

    output = io.BytesIO()

    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="MediLens Medical Report Summary",
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="MediLensTitle",
            parent=styles["Title"],
            textColor=colors.HexColor("#123047"),
            fontSize=22,
            leading=27,
            alignment=TA_CENTER,
            spaceAfter=5,
        )
    )

    styles.add(
        ParagraphStyle(
            name="MediLensSub",
            parent=styles["Normal"],
            textColor=colors.HexColor("#587084"),
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=16,
        )
    )

    styles.add(
        ParagraphStyle(
            name="MediLensSection",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#0d8179"),
            fontSize=13,
            leading=17,
            spaceBefore=12,
            spaceAfter=7,
        )
    )

    styles.add(
        ParagraphStyle(
            name="MediLensBody",
            parent=styles["BodyText"],
            fontSize=8.5,
            leading=12,
            spaceAfter=4,
        )
    )

    def p(value):
        # Escape user/report text before inserting it into a PDF paragraph.
        from xml.sax.saxutils import escape
        return Paragraph(escape(safe_text(value, "")), styles["MediLensBody"])

    story = [
        Paragraph("MediLens", styles["MediLensTitle"]),
        Paragraph(
            "Medical Report Explanation • Educational summary",
            styles["MediLensSub"],
        ),
        Paragraph("Report overview", styles["MediLensSection"]),
    ]

    patient_rows = [["Field", "Extracted information"]]

    for key, value in (patient or {}).items():
        if safe_text(value, ""):
            patient_rows.append([p(key), p(value)])

    if len(patient_rows) == 1:
        patient_rows.append([p("Patient details"), p("Not found in report")])

    patient_table = Table(patient_rows, colWidths=[48 * mm, 125 * mm], repeatRows=1)
    patient_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#123047")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dbe5eb")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.extend([patient_table, Spacer(1, 8), Paragraph("Test results", styles["MediLensSection"])])

    result_rows = [[
        p("Test"),
        p("Result"),
        p("Reference range"),
        p("Status"),
    ]]

    for _, row in results_df.iterrows():
        result_rows.append([
            p(row.get("Test", "")),
            p(" ".join(
                x for x in [
                    safe_text(row.get("Result", ""), ""),
                    safe_text(row.get("Unit", ""), ""),
                ] if x
            )),
            p(row.get("Reference Range", "")),
            p(row.get("Status", "")),
        ])

    if len(result_rows) == 1:
        result_rows.append([p("No results"), p(""), p(""), p("")])

    result_table = Table(
        result_rows,
        colWidths=[43 * mm, 35 * mm, 48 * mm, 47 * mm],
        repeatRows=1,
    )
    result_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d8179")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dbe5eb")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(result_table)

    story.append(Paragraph("Detailed explanations", styles["MediLensSection"]))

    for item in detailed_results:
        block = [
            Paragraph(
                safe_text(item.get("Test"), "Test"),
                styles["Heading3"],
            ),
            p("Result: " + safe_text(item.get("Result"), "")),
            p("Meaning: " + safe_text(item.get("Meaning"), "")),
            p("Importance: " + safe_text(item.get("Importance"), "")),
            p("Interpretation: " + safe_text(item.get("Interpretation"), "")),
        ]

        causes = item.get("Possible Causes", [])
        if isinstance(causes, list) and causes:
            block.append(p("Possible causes: " + "; ".join(map(str, causes))))

        block.append(p("Follow-up: " + safe_text(item.get("Follow-up"), "")))
        block.append(Spacer(1, 7))
        story.append(KeepTogether(block))

    story.extend(
        [
            Spacer(1, 10),
            Paragraph("Important notice", styles["MediLensSection"]),
            p(
                "This report is an educational explanation, not a diagnosis or "
                "treatment recommendation. Verify all extracted values against "
                "the original document. Discuss medical concerns with a qualified "
                "healthcare professional."
            ),
        ]
    )

    doc.build(story)
    output.seek(0)
    return output.getvalue()


def display_status(status):
    category = normalize_status(status)

    label = {
        "normal": "Within range",
        "low": "Below range",
        "high": "Above range",
        "unknown": "Needs review",
    }[category]

    css_class = {
        "normal": "status-normal",
        "low": "status-low",
        "high": "status-high",
        "unknown": "status-unknown",
    }[category]

    st.markdown(
        f'<span class="{css_class}">{label}</span>',
        unsafe_allow_html=True,
    )


# =========================================================
# UPLOAD SECTION
# =========================================================

st.markdown('<div id="analyze"></div>', unsafe_allow_html=True)

st.markdown(
    '<div class="section-heading">Analyze your report</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Upload a laboratory report to extract and explain its test results. '
    'Supported formats: PDF, PNG, JPG, and JPEG.'
    '</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.markdown("### 📄 Upload medical report")
    st.write(
        "Choose a report from your device. Only the uploaded document "
        "will be passed to the analyzer in this session."
    )

    uploaded_file = st.file_uploader(
        "Select your report",
        type=["pdf", "png", "jpg", "jpeg"],
        key="medical_report_upload",
        help="Upload a PDF or a clear image of a laboratory report.",
    )

    analyze_clicked = st.button(
        "✦ Analyze my report",
        type="primary",
        use_container_width=True,
        disabled=uploaded_file is None,
    )


# =========================================================
# REPORT-SPECIFIC ANALYSIS
# =========================================================

if analyze_clicked and uploaded_file is not None:
    try:
        with st.spinner("Reading your report and organizing the results..."):
            report_text = extract_report_text(uploaded_file)

            if not report_text:
                st.error(
                    "No readable text was extracted. Try a clearer image or "
                    "a text-based PDF. Scanned PDFs require the OCR function "
                    "in your existing ocr_service.py."
                )
                st.stop()

            # The analyzer receives only the text from this upload.
            raw_results = analyze_report(report_text)
            results_df = normalize_dataframe(raw_results)

            patient_fields = get_patient_fields(report_text)

            explanation = explain_report(
                report_text=report_text,
                results_df=results_df,
                patient_fields=patient_fields,
            )

            # Store only this uploaded report's output in session state.
            st.session_state["medilens_report_text"] = report_text
            st.session_state["medilens_results"] = results_df
            st.session_state["medilens_patient"] = patient_fields
            st.session_state["medilens_explanation"] = explanation
            st.session_state["medilens_filename"] = uploaded_file.name

    except Exception as exc:
        st.error(
            "We could not finish analyzing this report. Please check the "
            "report format and the extraction/analyzer modules."
        )
        st.exception(exc)


# =========================================================
# DISPLAY ANALYSIS RESULTS
# =========================================================

if "medilens_results" in st.session_state:
    results_df = st.session_state["medilens_results"]
    patient_fields = st.session_state["medilens_patient"]
    explanation = st.session_state["medilens_explanation"]
    report_text = st.session_state["medilens_report_text"]
    filename = st.session_state["medilens_filename"]

    st.markdown("---")
    st.markdown(
        '<div class="section-heading">Your report overview</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'These details are based on the text extracted from the uploaded file. '
        'Check them against the original report.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(f"Uploaded file: {filename}")

    # Patient details
    with st.container(border=True):
        st.markdown("### 👤 Patient information")

        if patient_fields:
            cols = st.columns(3)

            for index, (key, value) in enumerate(patient_fields.items()):
                with cols[index % 3]:
                    st.markdown(f"**{key}**")
                    st.write(safe_text(value))
        else:
            st.info(
                "Patient details were not identified automatically. "
                "Please refer to the original report."
            )

    # Status counts
    statuses = results_df["Status"].apply(normalize_status)

    total_tests = len(results_df)
    normal_count = int((statuses == "normal").sum())
    low_count = int((statuses == "low").sum())
    high_count = int((statuses == "high").sum())
    review_count = int((statuses == "unknown").sum())

    st.markdown("### 📊 Results at a glance")

    metric_cols = st.columns(4)

    metrics = [
        ("Total tests", total_tests, "Extracted results"),
        ("Within range", normal_count, "Marked normal"),
        ("Above range", high_count, "Marked high"),
        ("Below range", low_count, "Marked low"),
    ]

    for col, (label, value, caption) in zip(metric_cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-caption">{caption}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if review_count:
        st.info(
            f"{review_count} result(s) could not be classified reliably "
            "from the extracted text and may need manual review."
        )

    # Results table
    st.markdown("")
    st.markdown(
        '<div class="section-heading">Laboratory results</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Compare each extracted result with the reference range printed '
        'by the laboratory.'
        '</div>',
        unsafe_allow_html=True,
    )

    display_df = results_df.copy()
    display_df["Result"] = display_df.apply(
        lambda row: " ".join(
            value for value in [
                safe_text(row.get("Result", ""), ""),
                safe_text(row.get("Unit", ""), ""),
            ] if value
        ),
        axis=1,
    )

    display_df = display_df[
        ["Test", "Result", "Reference Range", "Status"]
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    # Chart: only use numeric values; never invent values for missing results.
    st.markdown(
        '<div class="section-heading">Result visualization</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'The chart includes only values that can be interpreted as numbers. '
        'Different tests may use different units, so the chart is a visual '
        'comparison rather than a clinical comparison.'
        '</div>',
        unsafe_allow_html=True,
    )

    chart_df = results_df[["Test", "Result"]].copy()

    chart_df["Numeric Result"] = chart_df["Result"].apply(
        lambda value: (
            float(re.search(r"[-+]?\d*\.?\d+", str(value)).group())
            if re.search(r"[-+]?\d*\.?\d+", str(value))
            else None
        )
    )

    chart_df = chart_df.dropna(subset=["Numeric Result"])

    if not chart_df.empty:
        chart_df = chart_df.set_index("Test")[["Numeric Result"]]
        st.bar_chart(chart_df, use_container_width=True)
    else:
        st.info(
            "No numeric test values were extracted for a chart. "
            "The results table is still available above."
        )

    # Detailed explanations
    st.markdown(
        '<div class="section-heading">Understand your results</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Review the meaning, importance, interpretation, possible causes, '
        'and follow-up notes for each extracted test.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.info(explanation.get("summary", "Report analysis is complete."))

    detailed_results = explanation.get("results", [])

    if detailed_results:
        for item in detailed_results:
            test_name = safe_text(item.get("Test"), "Laboratory test")

            with st.expander(f"🧪 {test_name}", expanded=False):
                result_col, status_col = st.columns(2)

                with result_col:
                    st.markdown("**Extracted result**")
                    st.write(safe_text(item.get("Result")))

                    st.markdown("**Reference range**")
                    st.write(safe_text(item.get("Reference Range")))

                with status_col:
                    st.markdown("**Reported status**")
                    display_status(item.get("Status"))

                st.markdown("---")
                st.markdown("**What this test measures**")
                st.write(safe_text(item.get("Meaning")))

                st.markdown("**Why it matters**")
                st.write(safe_text(item.get("Importance")))

                st.markdown("**Interpretation**")
                st.write(safe_text(item.get("Interpretation")))

                causes = item.get("Possible Causes", [])
                if isinstance(causes, list) and causes:
                    st.markdown("**Possible causes to discuss with a clinician**")
                    for cause in causes:
                        st.markdown(f"- {cause}")
                elif isinstance(causes, str) and causes.strip():
                    st.markdown("**Possible causes to discuss with a clinician**")
                    st.write(causes)

                st.markdown("**Suggested follow-up discussion**")
                st.write(safe_text(item.get("Follow-up")))
    else:
        st.warning(
            "The report text was extracted, but no test results were identified. "
            "Try a clearer document or review analyzer.py."
        )

    # Downloads
    st.markdown("---")
    st.markdown(
        '<div class="section-heading">Download your report</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        'Save the extracted results or create a PDF summary for your records.'
        '</div>',
        unsafe_allow_html=True,
    )

    csv_data = results_df.to_csv(index=False).encode("utf-8-sig")

    download_cols = st.columns(2)

    with download_cols[0]:
        st.download_button(
            "⬇ Download results (CSV)",
            data=csv_data,
            file_name="medilens_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with download_cols[1]:
        try:
            pdf_data = make_pdf(
                report_text,
                patient_fields,
                results_df,
                detailed_results,
            )

            st.download_button(
                "⬇ Download report (PDF)",
                data=pdf_data,
                file_name="medilens_report_summary.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except ImportError:
            st.warning(
                "PDF download needs ReportLab. Add reportlab to requirements.txt."
            )
        except Exception:
            st.warning(
                "The PDF could not be generated. The CSV download is still available."
            )

    # Show extracted text to help users verify OCR output.
    with st.expander("View extracted source text"):
        st.caption(
            "Verify this text against the original document, especially "
            "numbers, units, names, and reference ranges."
        )
        st.text_area(
            "Extracted text",
            value=report_text,
            height=220,
            disabled=True,
            label_visibility="collapsed",
        )

    st.markdown(
        """
        <div class="disclaimer">
            <strong>Medical information notice</strong><br>
            MediLens provides educational explanations of extracted laboratory
            results. It does not diagnose conditions, recommend treatment, or
            replace a qualified healthcare professional. Extraction errors are
            possible. Always verify results, units, and reference ranges against
            the original report and discuss concerns with your clinician.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# FEATURES AND ABOUT
# =========================================================

st.markdown('<div id="features"></div>', unsafe_allow_html=True)
st.markdown("---")

st.markdown(
    '<div class="section-heading">Designed to make reports easier to understand</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'A simple workflow to organize report information in one place.'
    '</div>',
    unsafe_allow_html=True,
)

feature_cols = st.columns(3)

features = [
    (
        "📄",
        "Simple report upload",
        "Read supported PDF and image reports using your existing extraction tools.",
    ),
    (
        "📊",
        "Clear result summaries",
        "View extracted results, reference ranges, status counts, and numeric charts.",
    ),
    (
        "📘",
        "Plain-language explanations",
        "Review built-in explanations and save your results as CSV or PDF.",
    ),
]

for col, (icon, title, description) in zip(feature_cols, features):
    with col:
        st.markdown(
            f"""
            <div class="panel">
                <div style="font-size:30px;margin-bottom:12px;">{icon}</div>
                <div style="font-size:17px;font-weight:800;color:#123047;">
                    {title}
                </div>
                <div style="font-size:13px;line-height:1.7;color:#718096;margin-top:9px;">
                    {description}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<div id="about"></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="footer">
        <strong style="color:#123047;font-size:15px;">🩺 MediLens</strong><br>
        Medical Report Explainer<br>
        Built to support understanding, not replace medical care.<br><br>
        © 2026 MediLens • Educational use only
    </div>
    """,
    unsafe_allow_html=True,
)
