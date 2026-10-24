
import streamlit as st
import pandas as pd
import hashlib
import html
import re

from extractor import extract_text_from_pdf
from ocr_service import (
    extract_text_from_image,
    extract_text_from_scanned_pdf,
)
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import explain_report
from report_generator import generate_pdf_report


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MediLens | Medical Report Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# PROFESSIONAL MEDICAL THEME
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #102A43;
    --navy-light: #183F5C;
    --teal: #078B91;
    --teal-dark: #066B73;
    --mint: #E6F8F5;
    --background: #F3F7FC;
    --border: #DCE7F1;
    --muted: #71849A;
    --ink: #19334D;
    --white: #FFFFFF;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 90% 5%, #E4F5FC 0, transparent 25%),
        var(--background);
    color: var(--ink);
}

.block-container {
    max-width: 1450px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif;
    color: var(--navy);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102A43, #123D58 75%, #08283F);
    border-right: 1px solid #294D68;
}

[data-testid="stSidebar"] * {
    color: #EDF7FF;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #C1D6E7;
}

[data-testid="stSidebar"] hr {
    border-color: #36556D;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #B9D1E4;
}

/* Logo */

.medilens-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 18px;
}

.medilens-logo-mark {
    width: 49px;
    height: 49px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 16px;
    color: white;
    font-size: 29px;
    font-weight: 800;
    background: linear-gradient(145deg, #32DDD0, #078B91);
    box-shadow: 0 9px 20px rgba(4, 196, 190, .23);
}

.medilens-logo-name {
    font-family: 'Manrope', sans-serif;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -1px;
    color: white;
}

.medilens-logo-subtitle {
    color: #B9D7E8;
    font-size: 9px;
    letter-spacing: 1.2px;
}

/* Welcome */

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 18px;
    padding: 0 3px;
}

.topbar-label {
    color: #648099;
    font-size: 12px;
}

.topbar-title {
    color: var(--navy);
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 23px;
}

/* Hero */

.hero {
    position: relative;
    overflow: hidden;
    padding: 32px;
    border: 1px solid #C6EAF6;
    border-radius: 24px;
    color: white;
    background: linear-gradient(115deg, #E3F8FF, #D8F0FF 53%, #EDF9FF);
    box-shadow: 0 16px 35px rgba(24, 89, 125, .11);
    margin-bottom: 25px;
}

.hero::before {
    content: "";
    position: absolute;
    width: 240px;
    height: 240px;
    right: 20%;
    top: -130px;
    border-radius: 50%;
    background: rgba(255,255,255,.48);
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 690px;
}

.hero-badge {
    display: inline-block;
    background: #C6F1F0;
    color: #086B73;
    border-radius: 100px;
    padding: 6px 12px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .3px;
}

.hero h1 {
    color: #103B62;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(28px, 3vw, 42px);
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -1.2px;
    margin: 15px 0 12px;
}

.hero p {
    color: #476C8D;
    font-size: 14px;
    line-height: 1.8;
    max-width: 650px;
}

.hero-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 17px;
}

.hero-pill {
    display: inline-block;
    border: 1px solid #B7DDEB;
    background: rgba(255,255,255,.68);
    color: #1B5C7C;
    padding: 7px 11px;
    border-radius: 100px;
    font-size: 10px;
    font-weight: 700;
}

/* 3D Medical illustration */

.medical-art {
    position: relative;
    min-height: 225px;
    display: flex;
    align-items: center;
    justify-content: center;
    perspective: 900px;
    border: 1px solid #CDEBF7;
    border-radius: 22px;
    overflow: hidden;
    margin-bottom: 23px;
    background:
        radial-gradient(circle at 50% 45%, #FFFFFF 0, #D8F5FF 38%, #C4E9F8 72%, #E6F4FF 100%);
}

.medical-art::before,
.medical-art::after {
    content: "";
    position: absolute;
    border-radius: 50%;
    border: 1px solid rgba(21, 144, 174, .16);
}

.medical-art::before {
    width: 250px;
    height: 250px;
}

.medical-art::after {
    width: 190px;
    height: 190px;
}

.medical-art-card {
    position: relative;
    z-index: 2;
    width: 130px;
    height: 164px;
    border: 1px solid white;
    border-radius: 19px;
    background: linear-gradient(145deg, #FFFFFF, #E9F7FF);
    box-shadow: 13px 19px 30px rgba(22, 91, 130, .22);
    transform: rotateY(-12deg) rotateX(5deg);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    animation: medilensFloat 4s ease-in-out infinite;
}

.medical-art-cross {
    width: 60px;
    height: 60px;
    display: grid;
    place-items: center;
    border-radius: 18px;
    color: white;
    font-size: 36px;
    font-weight: 800;
    background: linear-gradient(145deg, #23D1CE, #078B91);
    box-shadow: 0 10px 20px rgba(8, 127, 140, .28);
}

.medical-art-line {
    height: 7px;
    width: 78px;
    border-radius: 20px;
    background: #C7E5F3;
}

.medical-art-shield {
    position: absolute;
    z-index: 3;
    right: 17%;
    bottom: 18%;
    font-size: 49px;
    filter: drop-shadow(0 10px 8px rgba(8, 100, 130, .23));
    animation: shieldFloat 5s ease-in-out infinite;
}

.medical-art-plus {
    position: absolute;
    z-index: 1;
    left: 17%;
    top: 15%;
    font-size: 38px;
    font-weight: 800;
    color: #078DAD;
    text-shadow: 0 8px 12px rgba(8, 100, 130, .15);
}

@keyframes medilensFloat {
    0%, 100% {
        transform: translateY(0) rotateY(-12deg) rotateX(5deg);
    }
    50% {
        transform: translateY(-8px) rotateY(-8deg) rotateX(5deg);
    }
}

@keyframes shieldFloat {
    0%, 100% { transform: translateY(0) rotate(4deg); }
    50% { transform: translateY(-7px) rotate(-4deg); }
}

/* Section headings */

.section-heading {
    font-family: 'Manrope', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: var(--navy);
    margin-top: 22px;
    margin-bottom: 4px;
}

.section-caption {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 17px;
}

/* Cards */

.panel {
    background: rgba(255,255,255,.96);
    border: 1px solid var(--border);
    border-radius: 17px;
    padding: 21px;
    margin-bottom: 15px;
    box-shadow: 0 7px 22px rgba(23, 56, 86, .045);
    transition: transform .25s ease, box-shadow .25s ease;
}

.panel:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 30px rgba(23, 56, 86, .10);
}

.panel-title {
    color: var(--navy);
    font-size: 16px;
    font-weight: 800;
    margin-bottom: 7px;
}

.panel-description {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.75;
}

.kpi {
    background: white;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 17px;
    min-height: 112px;
    box-shadow: 0 7px 22px rgba(23, 56, 86, .045);
    transition: transform .25s ease, box-shadow .25s ease;
}

.kpi:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 28px rgba(23, 56, 86, .10);
}

.kpi-label {
    color: var(--muted);
    font-size: 12px;
    font-weight: 600;
}

.kpi-value {
    color: var(--navy);
    font-family: 'Manrope', sans-serif;
    font-size: 29px;
    font-weight: 800;
    margin-top: 8px;
}

.kpi-note {
    color: var(--muted);
    font-size: 11px;
    margin-top: 2px;
}

/* Status cards */

.status-box {
    background: #E8F8F5;
    border: 1px solid #C6EAE4;
    border-radius: 13px;
    padding: 16px;
    color: #17645D;
    font-size: 13px;
    line-height: 1.8;
}

.warning-box {
    background: #FFF7E8;
    border: 1px solid #F2DDAE;
    border-radius: 13px;
    padding: 16px;
    color: #78591A;
    font-size: 13px;
    line-height: 1.8;
}

.disclaimer {
    background: #FFF8E8;
    border: 1px solid #F3DDA9;
    border-left: 4px solid #D9A441;
    border-radius: 10px;
    padding: 17px;
    color: #674D1B;
    font-size: 12px;
    line-height: 1.8;
}

.insight-card {
    border: 1px solid #CBE9F5;
    border-radius: 15px;
    padding: 19px;
    background: linear-gradient(135deg, #F1FBFF, #FFFFFF);
    margin-bottom: 14px;
}

/* Inputs */

div[data-testid="stFileUploader"] {
    background: white;
    border: 1px dashed #9BC9DA;
    border-radius: 14px;
    padding: 12px;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid var(--border);
    padding: 15px;
    border-radius: 14px;
}

.stButton button, .stDownloadButton button {
    border-radius: 11px;
    font-weight: 700;
    min-height: 43px;
    transition: transform .2s ease, box-shadow .2s ease;
}

.stButton button:hover, .stDownloadButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 7px 16px rgba(8, 127, 140, .13);
}

div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

div[data-testid="stExpander"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 13px;
    margin-bottom: 9px;
}

footer {
    visibility: hidden;
}

@media (prefers-reduced-motion: reduce) {
    .medical-art-card, .medical-art-shield {
        animation: none;
    }

    .panel, .kpi, .stButton button, .stDownloadButton button {
        transition: none;
    }
}

@media (max-width: 700px) {
    .hero { padding: 22px; }
    .panel { padding: 15px; }
    .medical-art { min-height: 185px; }
    .medical-art-shield { right: 8%; }
    .medical-art-plus { left: 8%; }
    .topbar-title { font-size: 19px; }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# REUSABLE HELPERS
# =========================================================

def section(title, caption=""):
    st.markdown(
        f'<div class="section-heading">{html.escape(str(title))}</div>',
        unsafe_allow_html=True,
    )
    if caption:
        st.markdown(
            f'<div class="section-caption">{html.escape(str(caption))}</div>',
            unsafe_allow_html=True,
        )


def safe_text(value):
    if value is None:
        return "Not available"
    return html.escape(str(value))


def kpi_card(label, value, note):
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-label">{safe_text(label)}</div>
            <div class="kpi-value">{safe_text(value)}</div>
            <div class="kpi-note">{safe_text(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_status_column(df):
    for col in df.columns:
        if str(col).strip().lower() == "status":
            return col
    return None


def get_counts(df):
    status_col = get_status_column(df)

    if status_col is None:
        return 0, 0, 0, 0

    status = df[status_col].fillna("").astype(str).str.lower()

    low = status.str.contains(
        r"\b(below|low|decreased)\b", regex=True
    ).sum()

    high = status.str.contains(
        r"\b(above|high|elevated|increased)\b", regex=True
    ).sum()

    normal = status.str.contains(
        r"\b(within range|normal|normal range)\b", regex=True
    ).sum()

    urgent = status.str.contains(
        r"\b(urgent|critical)\b", regex=True
    ).sum()

    return int(low), int(high), int(normal), int(urgent)


def find_column(df, candidates):
    """Find a column by matching its normalized name."""
    normalized = {
        str(col).strip().lower().replace("_", " "): col
        for col in df.columns
    }

    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]

    return None


def make_numeric_chart_data(df):
    """
    Build chart data only from identifiable test and result columns.
    The numeric chart is for visualization, not clinical classification.
    """
    name_col = find_column(
        df,
        [
            "test",
            "test name",
            "parameter",
            "lab test",
            "investigation",
            "test parameter",
        ],
    )

    value_col = find_column(
        df,
        [
            "result",
            "value",
            "test result",
            "result value",
            "observed value",
        ],
    )

    if name_col is None or value_col is None:
        return pd.DataFrame()

    chart_data = df[[name_col, value_col]].copy()
    chart_data.columns = ["Test", "Result"]

    chart_data["Test"] = chart_data["Test"].astype(str)

    # Extract the first numeric value from a result such as "7.8 %".
    chart_data["Numeric value"] = pd.to_numeric(
        chart_data["Result"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"([-+]?\d*\.?\d+)")[0],
        errors="coerce",
    )

    chart_data = chart_data.dropna(subset=["Numeric value"])
    chart_data = chart_data.drop_duplicates(subset=["Test"])

    return chart_data.head(20)


def render_status_badge(status):
    status_text = str(status or "Needs review").strip().lower()

    if "urgent" in status_text or "critical" in status_text:
        return "🔴 Needs urgent review"

    if any(word in status_text for word in ["above", "high", "elevated"]):
        return "🟠 Above range"

    if any(word in status_text for word in ["below", "low", "decreased"]):
        return "🔵 Below range"

    if any(word in status_text for word in ["within", "normal"]):
        return "🟢 Within range"

    return "⚪ Needs review"


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("""
    <div class="medilens-logo">
        <div class="medilens-logo-mark">✚</div>
        <div>
            <div class="medilens-logo-name">MediLens</div>
            <div class="medilens-logo-subtitle">MEDICAL INTELLIGENCE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("**WORKSPACE**")
    st.markdown("◉  Report analysis")
    st.markdown("◈  Clinical findings")
    st.markdown("▤  Report export")

    st.divider()

    st.markdown("**SUPPORTED FORMATS**")
    st.caption("PDF · JPG · JPEG · PNG")

    st.divider()

    st.markdown("**ANALYSIS PROCESS**")
    st.caption("01  Extract report")
    st.caption("02  Structure findings")
    st.caption("03  Review explanations")
    st.caption("04  Export report")

    st.divider()

    st.caption("MediLens · Clinical Intelligence")


# =========================================================
# TOP BAR
# =========================================================

st.markdown("""
<div class="topbar">
    <div>
        <div class="topbar-label">WELCOME TO MEDILENS</div>
        <div class="topbar-title">Your Medical Report Workspace</div>
        <div class="topbar-label">
            Clearer explanations from your uploaded laboratory reports
        </div>
    </div>
    <div style="font-size:32px;">🩺</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# HERO SECTION
# =========================================================

hero_left, hero_right = st.columns([1.6, 1], gap="large")

with hero_left:
    st.markdown("""
    <div class="hero">
        <div class="hero-content">
            <span class="hero-badge">TRUSTED · INFORMATIVE · PATIENT-FRIENDLY</span>
            <h1>Turn Medical Reports<br>Into Clear Insights</h1>
            <p>
                Understand laboratory results through structured findings,
                easy-to-read graphs, and educational explanations.
                Keep your original report available for verification.
            </p>
            <div class="hero-pills">
                <span class="hero-pill">REPORT ANALYSIS</span>
                <span class="hero-pill">VISUAL GRAPHS</span>
                <span class="hero-pill">PDF EXPORT</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with hero_right:
    st.markdown("""
    <div class="medical-art">
        <div class="medical-art-plus">✚</div>
        <div class="medical-art-card">
            <div class="medical-art-cross">✚</div>
            <div class="medical-art-line"></div>
            <div class="medical-art-line" style="width:62px;"></div>
            <div class="medical-art-line" style="width:72px;"></div>
        </div>
        <div class="medical-art-shield">🛡️</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# REPORT UPLOAD
# =========================================================

section(
    "01  Report workspace",
    "Upload one patient's report to begin a new analysis.",
)

left, right = st.columns([1.45, 1], gap="large")

with left:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">📄 Upload medical report</div>
        <div class="panel-description">
            Import a laboratory report as a PDF or image.
            Clear, readable files generally provide better extraction results.
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a medical report",
        type=["pdf", "jpg", "jpeg", "png"],
        key="medilens_upload",
    )

with right:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">✨ Analysis capabilities</div>
        <div class="panel-description">
            🧾 Patient information extraction<br>
            🧪 Laboratory result structuring<br>
            📊 Visual result summaries<br>
            🔎 Abnormal-value identification<br>
            💡 Educational explanations<br>
            📥 Downloadable PDF report
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# EMPTY WORKSPACE
# =========================================================

if not uploaded_file:
    st.markdown("""
    <div class="status-box">
        <b>✓ Your workspace is ready</b><br>
        Upload a report above to display the patient overview,
        laboratory findings, graphs, and educational explanations.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
        <b>Medical disclaimer</b><br>
        MediLens supports understanding medical reports. Its findings
        may be incomplete or inaccurate and do not establish a diagnosis.
        Consult a qualified healthcare professional for clinical decisions.
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# FILE HASH AND SESSION STATE
# =========================================================

file_hash = hashlib.sha256(
    uploaded_file.getvalue()
).hexdigest()

if st.session_state.get("report_hash") != file_hash:
    st.session_state["report_hash"] = file_hash

    st.session_state.pop("report_data", None)
    st.session_state.pop("report_insights", None)
    st.session_state.pop("report_pdf", None)


# =========================================================
# FILE PROCESSING
# =========================================================

if st.button(
    "🔍  Run medical report analysis",
    type="primary",
    use_container_width=True,
):
    try:
        with st.spinner("Extracting text from the uploaded report..."):
            if uploaded_file.type == "application/pdf":
                uploaded_file.seek(0)
                report_text = extract_text_from_pdf(uploaded_file)

                if not report_text or len(report_text.strip()) < 20:
                    uploaded_file.seek(0)
                    report_text = extract_text_from_scanned_pdf(
                        uploaded_file
                    )
            else:
                uploaded_file.seek(0)
                report_text = extract_text_from_image(uploaded_file)

        if not report_text or len(report_text.strip()) < 20:
            st.error(
                "Not enough text was extracted. Try a clearer report "
                "or check your OCR configuration."
            )
            st.stop()

        with st.spinner("Structuring laboratory results..."):
            results = analyze_report(report_text)
            patient = extract_patient_fields(report_text)

        if results is None:
            results = pd.DataFrame()
        elif not isinstance(results, pd.DataFrame):
            results = pd.DataFrame(results)

        if not isinstance(patient, dict):
            patient = {}

        st.session_state["report_data"] = {
            "hash": file_hash,
            "filename": uploaded_file.name,
            "text": report_text,
            "results": results,
            "patient": patient,
        }

        st.session_state.pop("report_insights", None)
        st.session_state.pop("report_pdf", None)

        st.success("Report extraction and analysis completed.")

    except Exception as error:
        st.error("Report analysis failed.")
        st.caption(
            "Check the function names in extractor.py, ocr_service.py, "
            "and analyzer.py."
        )
        st.exception(error)


# =========================================================
# LOAD PROCESSED REPORT
# =========================================================

data = st.session_state.get("report_data")

if not data or data.get("hash") != file_hash:
    st.info("Run the analysis to view the report dashboard.")
    st.stop()

report_text = data["text"]
results = data["results"]
patient = data["patient"]


# =========================================================
# PATIENT OVERVIEW
# =========================================================

section(
    "02  Patient overview",
    "Information extracted from the uploaded report.",
)

if patient:
    fields = list(patient.items())[:6]
    columns = st.columns(min(3, len(fields)))

    for index, (key, value) in enumerate(fields):
        with columns[index % len(columns)]:
            st.markdown(
                f"""
                <div class="panel">
                    <div class="kpi-label">
                        {safe_text(str(key).replace('_', ' ').title())}
                    </div>
                    <div style="
                        font-size:17px;
                        font-weight:800;
                        color:#102A43;
                        margin-top:10px;
                        overflow-wrap:anywhere;">
                        {safe_text(value)[:120]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.info(
        "Patient details could not be confidently extracted. "
        "Review the original report before interpreting results."
    )


# =========================================================
# LABORATORY FINDINGS
# =========================================================

section(
    "03  Laboratory findings",
    "Review the structured values extracted from this report.",
)

if results.empty:
    st.warning(
        "No structured laboratory values were detected. "
        "The analyzer may need additional test-pattern support."
    )

else:
    low_count, high_count, normal_count, urgent_count = get_counts(results)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card(
            "Tests identified",
            len(results),
            "Extracted records",
        )

    with c2:
        kpi_card(
            "Below range",
            low_count,
            "Analyzer classification",
        )

    with c3:
        kpi_card(
            "Above range",
            high_count,
            "Analyzer classification",
        )

    with c4:
        kpi_card(
            "Within range",
            normal_count,
            "Analyzer classification",
        )

    if urgent_count:
        st.error(
            f"{urgent_count} result(s) were marked for urgent review "
            "by the analyzer. Verify the original report and seek "
            "appropriate medical advice promptly."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    status_col = get_status_column(results)

    if status_col:
        status_values = results[status_col].fillna("").astype(str).str.lower()

        selected_filter = st.selectbox(
            "Filter laboratory findings",
            [
                "All findings",
                "Below range",
                "Above range",
                "Within range",
                "Needs review",
            ],
        )

        if selected_filter == "Below range":
            mask = status_values.str.contains(
                r"\b(below|low|decreased)\b", regex=True
            )
            view = results[mask]

        elif selected_filter == "Above range":
            mask = status_values.str.contains(
                r"\b(above|high|elevated|increased)\b", regex=True
            )
            view = results[mask]

        elif selected_filter == "Within range":
            mask = status_values.str.contains(
                r"\b(within range|normal|normal range)\b", regex=True
            )
            view = results[mask]

        elif selected_filter == "Needs review":
            mask = status_values.str.contains(
                r"\b(needs review|urgent|critical|unknown)\b",
                regex=True,
            )
            view = results[mask]

        else:
            view = results

    else:
        view = results

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# INTERACTIVE LABORATORY GRAPH
# =========================================================

section(
    "Visual laboratory dashboard",
    "Explore the numerical results extracted from the uploaded report.",
)

chart_data = make_numeric_chart_data(results)

if not chart_data.empty:
    test_options = chart_data["Test"].tolist()

    selected_test = st.selectbox(
        "Select a laboratory test",
        test_options,
        key="medilens_chart_test",
    )

    selected_row = chart_data[
        chart_data["Test"] == selected_test
    ].iloc[0]

    result_col = find_column(
        results,
        [
            "result",
            "value",
            "test result",
            "result value",
            "observed value",
        ],
    )

    unit_text = ""

    if result_col:
        raw_result = str(selected_row["Result"])
        unit_match = re.search(
            r"^\s*[-+]?\d*\.?\d+\s*(.*)$",
            raw_result,
        )

        if unit_match:
            unit_text = unit_match.group(1).strip()

    chart_left, chart_right = st.columns([1.6, 1], gap="large")

    with chart_left:
        st.markdown(
            '<div class="panel-title">Selected test result</div>',
            unsafe_allow_html=True,
        )

        st.metric(
            label=selected_test,
            value=f"{selected_row['Numeric value']:g} {unit_text}".strip(),
        )

        # A single-test graph avoids comparing unlike units together.
        st.bar_chart(
            pd.DataFrame(
                {
                    "Result": [
                        float(selected_row["Numeric value"])
                    ]
                },
                index=[selected_test],
            ),
            y="Result",
            use_container_width=True,
        )

    with chart_right:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">How to read this graph</div>
            <div class="panel-description">
                • The bar represents the extracted numerical result.<br><br>
                • Check the result's unit and reference range in the table.<br><br>
                • Each laboratory test may use a different scale.<br><br>
                • The graph alone cannot determine whether a result is healthy.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.caption(
        "This graph visualizes the extracted value only. "
        "It does not calculate a clinical reference interval or diagnosis."
    )

else:
    st.info(
        "A graph could not be created because recognizable test-name "
        "and numerical-result columns were not found. Review the table "
        "and your analyzer's output column names."
    )


# =========================================================
# CLINICAL INSIGHTS
# =========================================================

section(
    "04  Clinical insights",
    "Read educational explanations for each detected laboratory result.",
)

st.markdown("""
<div class="panel">
    <div class="panel-title">💡 Report interpretation</div>
    <div class="panel-description">
        Generate an overall summary and individual test explanations.
        Always verify extracted results against the original report.
    </div>
</div>
""", unsafe_allow_html=True)

if st.button(
    "✨  Generate clinical insights",
    key="generate_clinical_insights",
    use_container_width=True,
):
    try:
        with st.spinner("Preparing educational explanations..."):
            insights = explain_report(
                report_text=report_text,
                results_df=results,
                patient_fields=patient,
            )

        if isinstance(insights, dict):
            st.session_state["report_insights"] = {
                "hash": file_hash,
                "text": insights,
            }
            st.session_state.pop("report_pdf", None)

            st.success("Clinical explanations are ready.")

        else:
            st.error(
                "The explanation function returned an unexpected format."
            )

    except Exception as error:
        st.error("Unable to generate clinical insights.")
        st.exception(error)


# =========================================================
# DISPLAY INSIGHTS
# =========================================================

insights_data = st.session_state.get("report_insights")

if insights_data and insights_data.get("hash") == file_hash:
    insights = insights_data.get("text", {})

    if not isinstance(insights, dict):
        insights = {}

    # Overall summary
    section("Overall summary")

    summary = insights.get("summary", "No summary is available.")

    if isinstance(summary, dict):
        for key, value in summary.items():
            st.write(f"**{key}:**", value)
    else:
        st.markdown(
            f'<div class="insight-card">{safe_text(summary)}</div>',
            unsafe_allow_html=True,
        )

    # Individual test explanations
    section("Individual test explanations")

    explanations = insights.get("results", [])

    if explanations:
        for index, item in enumerate(explanations, start=1):
            if not isinstance(item, dict):
                continue

            test_name = item.get("Test", f"Test {index}")
            result_value = item.get("Result", "Not available")
            reference_range = item.get("Reference Range", "Not available")
            status = item.get("Status", "Needs review")

            with st.expander(
                f"{render_status_badge(status)}  |  {test_name}",
                expanded=(index == 1),
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Result**")
                    st.write(result_value)

                with col2:
                    st.markdown("**Reference range**")
                    st.write(reference_range)

                st.markdown("**Meaning**")
                st.write(item.get("Meaning", "Not available"))

                st.markdown("**Importance**")
                st.write(item.get("Importance", "Not available"))

                st.markdown("**Interpretation**")
                st.write(item.get("Interpretation", "Not available"))

                st.markdown("**Possible causes**")
                possible_causes = item.get(
                    "Possible Causes",
                    "Not available",
                )

                if isinstance(possible_causes, (list, tuple)):
                    if possible_causes:
                        for cause in possible_causes:
                            st.markdown(f"- {cause}")
                    else:
                        st.write(
                            "No cause information was returned for this test."
                        )
                else:
                    st.write(possible_causes)

                st.markdown("**Follow-up**")
                st.write(
                    item.get(
                        "Follow-up",
                        "Discuss the result with a healthcare professional.",
                    )
                )

    else:
        st.warning(
            "No individual explanations were returned. "
            "Check ai_explainer.py and the extracted results."
        )

    # General notes
    section("Important notes")

    notes = insights.get("general_notes", [])

    if isinstance(notes, (list, tuple)) and notes:
        for note in notes:
            st.markdown(f"- {note}")
    else:
        st.markdown(
            "- Verify extracted values against the original report.\n"
            "- Reference ranges can vary between laboratories.\n"
            "- Consult a qualified healthcare professional."
        )

    st.warning(
        "Do not use these explanations alone to diagnose a condition "
        "or change medication."
    )

else:
    st.info(
        "Select 'Generate clinical insights' to display the report explanation."
    )


# =========================================================
# SOURCE VERIFICATION
# =========================================================

with st.expander("🔎 Verify extracted source text"):
    st.write(
        "Compare this text with the original file to identify possible "
        "OCR errors, missing values, units, and reference ranges."
    )

    st.text_area(
        "Extracted report text",
        value=report_text,
        height=260,
        disabled=True,
    )


# =========================================================
# PDF EXPORT
# =========================================================

section(
    "05  Export report",
    "Create a downloadable copy of the analysis.",
)

if st.button(
    "📄  Generate PDF report",
    use_container_width=True,
):
    try:
        summary = "Clinical insights have not been generated."

        if insights_data and insights_data.get("hash") == file_hash:
            summary = insights_data["text"]

        pdf_bytes = generate_pdf_report(
            data["filename"],
            patient,
            results,
            summary,
        )

        st.session_state["report_pdf"] = {
            "hash": file_hash,
            "bytes": pdf_bytes,
        }

        st.success("PDF report generated.")

    except Exception as error:
        st.error("PDF generation failed.")
        st.exception(error)


# =========================================================
# DOWNLOAD
# =========================================================

pdf_data = st.session_state.get("report_pdf")

if pdf_data and pdf_data.get("hash") == file_hash:
    st.download_button(
        "⬇️  Download MediLens analysis",
        data=pdf_data["bytes"],
        file_name="MediLens_Clinical_Report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer">
    <b>Medical disclaimer</b><br>
    MediLens provides educational medical report analysis.
    Extracted values and explanations may be incomplete or inaccurate
    and do not constitute a confirmed diagnosis. Verify all findings
    against the original report and consult a qualified healthcare
    professional for interpretation and treatment decisions.
    Seek urgent medical care for potentially serious symptoms.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    text-align:center;
    color:#718096;
    font-size:11px;
    padding:24px 10px 10px;
">
    <span style="color:#078B91;font-size:18px;">✚</span>
    <b> MEDILENS </b> · MEDICAL REPORT INTELLIGENCE
    <br><br>
    Educational support for understanding medical reports
</div>
""", unsafe_allow_html=True)
