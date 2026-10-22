
import streamlit as st
import pandas as pd
import hashlib
import html

from extractor import extract_text_from_pdf
from ocr_service import (
    extract_text_from_image,
    extract_text_from_scanned_pdf,
)
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import explain_report
from report_generator import generate_pdf_report


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MediLens | Clinical Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# PROFESSIONAL THEME
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #12243A;
    --teal: #087F8C;
    --mint: #E9F7F5;
    --bg: #F4F7FB;
    --border: #E1E8F0;
    --muted: #718096;
    --ink: #192B42;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: var(--bg);
    color: var(--ink);
}

.block-container {
    max-width: 1320px;
    padding-top: 1.7rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: var(--navy);
}

[data-testid="stSidebar"] * {
    color: #EAF2FA;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #B8C8D9;
}

[data-testid="stSidebar"] hr {
    border-color: #33475D;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 36px;
    border-radius: 22px;
    color: white;
    background: linear-gradient(120deg, #12243A 0%, #15566C 65%, #087F8C 100%);
    margin-bottom: 28px;
}

.hero h1 {
    color: #FFFFFF;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(30px, 4vw, 44px);
    font-weight: 800;
    letter-spacing: -1.2px;
    margin: 10px 0;
}

.hero p {
    color: #DDEFF4;
    max-width: 720px;
    font-size: 15px;
    line-height: 1.8;
}

.eyebrow {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #9CE9DF;
}

.hero-pill {
    display: inline-block;
    border: 1px solid #5EA9B3;
    color: #DFF9F6;
    padding: 6px 12px;
    border-radius: 100px;
    font-size: 11px;
    margin-top: 8px;
}

.section-heading {
    font-family: 'Manrope', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: var(--navy);
    margin-top: 20px;
    margin-bottom: 4px;
}

.section-caption {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 17px;
}

.panel {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 17px;
    padding: 22px;
    margin-bottom: 16px;
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
    line-height: 1.7;
}

.kpi {
    background: white;
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 17px;
    min-height: 110px;
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

.status-box {
    background: #E9F7F5;
    border: 1px solid #C6EAE4;
    border-radius: 12px;
    padding: 15px;
    color: #17645D;
    font-size: 13px;
    line-height: 1.7;
}

.warning-box {
    background: #FFF7E8;
    border: 1px solid #F2DDAE;
    border-radius: 12px;
    padding: 15px;
    color: #78591A;
    font-size: 13px;
    line-height: 1.7;
}

.disclaimer {
    background: #FFF8E8;
    border-left: 4px solid #D9A441;
    border-radius: 8px;
    padding: 17px;
    color: #674D1B;
    font-size: 12px;
    line-height: 1.8;
}

div[data-testid="stFileUploader"] {
    background: white;
    border: 1px dashed #A8C5D4;
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
    border-radius: 10px;
    font-weight: 700;
    min-height: 43px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

footer {
    visibility: hidden;
}

@media (max-width: 700px) {
    .hero { padding: 24px; }
    .panel { padding: 16px; }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# REUSABLE UI HELPERS
# =========================================================

def section(title, caption=""):
    st.markdown(
        f'<div class="section-heading">{html.escape(title)}</div>',
        unsafe_allow_html=True,
    )
    if caption:
        st.markdown(
            f'<div class="section-caption">{html.escape(caption)}</div>',
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
            <div class="kpi-label">{html.escape(str(label))}</div>
            <div class="kpi-value">{html.escape(str(value))}</div>
            <div class="kpi-note">{html.escape(str(note))}</div>
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
        return 0, 0, 0

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

    return int(low), int(high), int(normal)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 20px;">
        <div style="font-size:28px;font-weight:800;color:white;">
            ✚ MediLens
        </div>
        <div style="font-size:11px;color:#B8C8D9;letter-spacing:1px;">
            CLINICAL INTELLIGENCE
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
    st.caption("02  Analyze findings")
    st.caption("03  Review interpretation")
    st.caption("04  Export report")

    st.divider()
    st.caption("MediLens · Clinical Intelligence")


# =========================================================
# HERO HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <div class="eyebrow">AI-POWERED HEALTHCARE TECHNOLOGY</div>
    <h1>Medical Report Intelligence</h1>
    <p>
        Transform medical reports into structured findings, potential
        condition indicators, and clinically relevant insights through
        AI-assisted report analysis.
    </p>
    <span class="hero-pill">REPORT ANALYSIS</span>
    &nbsp;
    <span class="hero-pill">HEALTH ASSESSMENT</span>
    &nbsp;
    <span class="hero-pill">CLINICAL INSIGHTS</span>
</div>
""", unsafe_allow_html=True)


# =========================================================
# REPORT UPLOAD
# =========================================================

section(
    "01  Report workspace",
    "Upload one patient's report to start a new analysis.",
)

left, right = st.columns([1.55, 1], gap="large")

with left:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">Upload medical report</div>
        <div class="panel-description">
            Import a laboratory report as a PDF or image.
            Use a clear, readable file for the best extraction results.
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose report file",
        type=["pdf", "jpg", "jpeg", "png"],
        key="medilens_upload",
    )

with right:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">Analysis capabilities</div>
        <div class="panel-description">
            • Patient information extraction<br>
            • Laboratory result structuring<br>
            • Abnormal value identification<br>
            • Potential condition assessment<br>
            • Clinical interpretation and PDF export
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# FILE PROCESSING
# =========================================================

if not uploaded_file:
    st.markdown("""
    <div class="status-box">
        <b>Ready for report upload</b><br>
        Your analysis workspace will appear after a medical report is uploaded.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
        <b>Medical disclaimer</b><br>
        MediLens findings may be incomplete or inaccurate. AI-assisted
        interpretation does not establish a confirmed diagnosis.
        Consult a qualified healthcare professional to confirm findings
        and determine appropriate treatment.
    </div>
    """, unsafe_allow_html=True)

    st.stop()


file_hash = hashlib.sha256(uploaded_file.getvalue()).hexdigest()

if st.session_state.get("report_hash") != file_hash:
    st.session_state["report_hash"] = file_hash
    st.session_state.pop("report_data", None)
    st.session_state.pop("report_insights", None)
    st.session_state.pop("report_pdf", None)

st.markdown("<br>", unsafe_allow_html=True)

if st.button(
    "Run medical report analysis",
    type="primary",
    use_container_width=True,
):
    try:
        with st.spinner("Extracting the uploaded report..."):
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
                "Not enough text was extracted. Upload a clearer report "
                "or check the OCR configuration."
            )
            st.stop()

        with st.spinner("Structuring medical test results..."):
            results = analyze_report(report_text)
            patient = extract_patient_fields(report_text)

        if results is None:
            results = pd.DataFrame()
        elif not isinstance(results, pd.DataFrame):
            results = pd.DataFrame(results)

        st.session_state["report_data"] = {
            "hash": file_hash,
            "filename": uploaded_file.name,
            "text": report_text,
            "results": results,
            "patient": patient if isinstance(patient, dict) else {},
        }

    except Exception as error:
        st.error("Report analysis failed.")
        st.caption(
            "Check the function names in extractor.py, ocr_service.py, "
            "and analyzer.py."
        )
        st.exception(error)


data = st.session_state.get("report_data")

if not data or data.get("hash") != file_hash:
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
    cols = st.columns(min(3, max(1, len(fields))))

    for index, (key, value) in enumerate(fields):
        with cols[index % len(cols)]:
            st.markdown(
                f"""
                <div class="panel">
                    <div class="kpi-label">{safe_text(str(key).replace('_', ' ').title())}</div>
                    <div style="font-size:17px;font-weight:800;color:#12243A;margin-top:10px;">
                        {safe_text(value)[:120]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.info(
        "Patient details could not be confidently extracted. "
        "Review the original report before interpreting the results."
    )


# =========================================================
# RESULTS DASHBOARD
# =========================================================

section(
    "03  Laboratory findings",
    "Structured results extracted from this report.",
)

if results.empty:
    st.warning(
        "No structured laboratory values were detected. "
        "The analyzer may need additional test-pattern support."
    )
else:
    low_count, high_count, normal_count = get_counts(results)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        kpi_card("Tests identified", len(results), "Extracted records")

    with c2:
        kpi_card("Below range", low_count, "Flagged by analyzer")

    with c3:
        kpi_card("Above range", high_count, "Flagged by analyzer")

    with c4:
        kpi_card("Within range", normal_count, "Flagged by analyzer")

    st.markdown("<br>", unsafe_allow_html=True)

    status_col = get_status_column(results)

    if status_col:
        statuses = results[status_col].fillna("").astype(str).str.lower()

        filter_options = ["All findings", "Below range", "Above range", "Within range"]

        selected_filter = st.selectbox(
            "Filter laboratory findings",
            filter_options,
        )

        if selected_filter == "Below range":
            view = results[
                statuses.str.contains(r"\b(below|low|decreased)\b", regex=True)
            ]
        elif selected_filter == "Above range":
            view = results[
                statuses.str.contains(r"\b(above|high|elevated|increased)\b", regex=True)
            ]
        elif selected_filter == "Within range":
            view = results[
                statuses.str.contains(r"\b(within range|normal|normal range)\b", regex=True)
            ]
        else:
            view = results

        st.dataframe(view, use_container_width=True, hide_index=True)
    else:
        st.dataframe(results, use_container_width=True, hide_index=True)


# =========================================================
# CLINICAL INSIGHTS
# =========================================================

section(
    "04  Clinical insights",
    "Generate an interpretation from the actual uploaded report.",
)

st.markdown("""
<div class="panel">
    <div class="panel-title">Potential condition assessment</div>
    <div class="panel-description">
        The interpretation engine should explain relevant abnormalities,
        associated possible conditions, limitations, and appropriate
        follow-up. A possible condition is not a confirmed diagnosis.
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("Generate clinical insights", use_container_width=True):
    try:
        with st.spinner("Generating report interpretation..."):
            insights = explain_report(report_text, results, patient)

        st.session_state["report_insights"] = {
            "hash": file_hash,
            "text": insights,
        }

        st.session_state.pop("report_pdf", None)

    except Exception as error:
        st.error("Unable to generate clinical insights.")
        st.exception(error)

insights_data = st.session_state.get("report_insights")

if insights_data and insights_data.get("hash") == file_hash:
    insights = insights_data["text"]

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    if isinstance(insights, dict):
        for heading, content in insights.items():
            st.markdown(f"**{safe_text(heading)}**")
            st.write(content)
    elif isinstance(insights, list):
        for item in insights:
            st.write(item)
    else:
        st.markdown(str(insights))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="warning-box">
        AI-generated condition assessments require clinical interpretation.
        Do not use this result alone to start, stop, or change medication.
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SOURCE VERIFICATION
# =========================================================

with st.expander("Verify extracted source text"):
    st.write(
        "Compare the extracted text with the original file to check for "
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

if st.button("Generate PDF report", use_container_width=True):
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

    except Exception as error:
        st.error("PDF generation failed.")
        st.exception(error)

pdf_data = st.session_state.get("report_pdf")

if pdf_data and pdf_data.get("hash") == file_hash:
    st.download_button(
        "Download MediLens analysis",
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
    MediLens provides AI-assisted medical report analysis and potential
    condition assessment. Findings may be incomplete or inaccurate and
    do not constitute a confirmed diagnosis. Consult a qualified
    healthcare professional to confirm findings and determine appropriate
    treatment. Seek urgent medical care for potentially serious symptoms.
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align:center;color:#718096;font-size:11px;padding:22px;'>"
    "MEDILENS · AI-POWERED MEDICAL REPORT INTELLIGENCE"
    "</div>",
    unsafe_allow_html=True,
)
