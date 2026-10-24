
import io
import re
import html
import streamlit as st
import pandas as pd

# Existing project modules
from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report
from ai_explainer import explain_report
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
# MEDILENS DARK 3D THEME + ANIMATIONS
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #07111f;
    --panel: #10243a;
    --teal: #19e0d0;
    --blue: #168ba5;
    --text: #edf8ff;
    --muted: #a6bdd0;
}

.stApp {
    background:
        radial-gradient(ellipse at 85% 0%, #123b50 0%, transparent 35%),
        radial-gradient(ellipse at 0% 50%, #0a2338 0%, transparent 45%),
        linear-gradient(140deg, #050c17, #091827 60%, #07111f);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1250px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b2033, #07111f);
    border-right: 1px solid #19384c;
}

[data-testid="stSidebar"] * {
    color: #eaf7ff;
}

/* Animations */
@keyframes float3d {
    0%, 100% { transform: translateY(0) rotateY(-4deg); }
    50% { transform: translateY(-10px) rotateY(4deg); }
}

@keyframes glow {
    0%, 100% {
        box-shadow: 0 0 12px rgba(25,224,208,.12);
    }
    50% {
        box-shadow: 0 0 28px rgba(25,224,208,.40);
    }
}

@keyframes appear {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0%, 100% { opacity: .65; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.06); }
}

/* Header */
.hero {
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 30px;
    border-radius: 25px;
    border: 1px solid rgba(25,224,208,.30);
    background: linear-gradient(130deg, #12364d, #0b1b2e 70%);
    box-shadow: 0 20px 45px rgba(0,0,0,.32);
    animation: appear .8s ease-out;
}

.hero::after {
    content: "✚";
    position: absolute;
    right: 30px;
    top: -22px;
    font-size: 150px;
    color: rgba(25,224,208,.07);
    transform: rotate(12deg);
    pointer-events: none;
}

.logo3d {
    flex-shrink: 0;
    width: 82px;
    height: 82px;
    border-radius: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 53px;
    font-weight: 800;
    color: white;
    background: linear-gradient(145deg, #34f7e4, #087b99);
    box-shadow:
        8px 8px 18px #040b13,
        inset 3px 3px 7px rgba(255,255,255,.35);
    animation: float3d 4s ease-in-out infinite, glow 3s infinite;
}

.hero-title {
    font-size: clamp(32px, 5vw, 49px);
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -1.5px;
    color: #ffffff;
}

.hero-title span {
    color: var(--teal);
}

.hero-description {
    color: #bad0df;
    font-size: 15px;
    line-height: 1.8;
    margin-top: 10px;
    max-width: 650px;
}

.eyebrow {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 3px;
    color: var(--teal);
    margin-bottom: 8px;
}

/* Medical illustration */
.visual-panel {
    margin-top: 22px;
    position: relative;
    overflow: hidden;
    border-radius: 22px;
    border: 1px solid rgba(25,224,208,.25);
    background: linear-gradient(140deg, #112d44, #081522);
    box-shadow: 0 15px 35px rgba(0,0,0,.28);
    animation: appear 1s ease-out;
}

.visual-panel img {
    display: block;
    width: 100%;
    height: 250px;
    object-fit: cover;
    opacity: .84;
    transition: transform .5s ease, opacity .5s ease;
}

.visual-panel img:hover {
    transform: scale(1.035);
    opacity: 1;
}

.visual-label {
    padding: 13px 18px;
    color: #b7d0e1;
    font-size: 12px;
    letter-spacing: .5px;
}

/* 3D cards */
.feature-card {
    min-height: 155px;
    padding: 20px;
    border-radius: 19px;
    background: linear-gradient(145deg, #142f47, #091725);
    border: 1px solid rgba(100,183,205,.20);
    box-shadow: 7px 9px 20px rgba(0,0,0,.25);
    transition: transform .3s ease, box-shadow .3s ease;
    animation: appear .8s ease-out;
}

.feature-card:hover {
    transform: translateY(-7px) perspective(700px) rotateX(2deg);
    box-shadow: 0 15px 30px rgba(25,224,208,.15);
    border-color: rgba(25,224,208,.55);
}

.feature-icon {
    font-size: 32px;
    margin-bottom: 10px;
    animation: pulse 3s infinite;
}

.feature-title {
    font-size: 16px;
    font-weight: 750;
    color: #f3fbff;
}

.feature-text {
    font-size: 12px;
    line-height: 1.7;
    color: #a8bfd1;
    margin-top: 7px;
}

/* Section heading */
.section-heading {
    font-size: 23px;
    font-weight: 800;
    color: #f0fbff;
    margin-top: 30px;
    margin-bottom: 12px;
}

/* Upload area */
[data-testid="stFileUploader"] {
    border: 1px dashed #19bcb7;
    border-radius: 17px;
    background: rgba(11,35,52,.75);
    padding: 12px;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(110deg, #20e3d2, #128aa6);
    color: #04131d;
    border: none;
    border-radius: 12px;
    font-weight: 800;
    transition: all .25s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(25,224,208,.25);
    color: white;
}

/* Metrics */
[data-testid="stMetric"] {
    padding: 17px;
    border-radius: 16px;
    border: 1px solid rgba(25,224,208,.22);
    background: linear-gradient(145deg, #122c43, #091725);
    box-shadow: 5px 7px 17px rgba(0,0,0,.20);
}

[data-testid="stMetricLabel"] {
    color: #b8d0df;
}

[data-testid="stMetricValue"] {
    color: #20e3d2;
}

/* Expanders and data */
[data-testid="stExpander"] {
    border: 1px solid #24465b;
    border-radius: 14px;
    background: rgba(12,32,49,.70);
}

[data-testid="stDataFrame"] {
    border: 1px solid #24465b;
    border-radius: 13px;
    overflow: hidden;
}

p, label, li {
    color: #dcebf5;
}

.small-note {
    font-size: 12px;
    line-height: 1.7;
    color: #a9bfd0;
}

.footer {
    margin-top: 35px;
    padding: 20px;
    text-align: center;
    color: #90aabd;
    border-top: 1px solid #1a3649;
    font-size: 12px;
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}

@media (max-width: 600px) {
    .hero { padding: 20px; gap: 15px; }
    .logo3d { width: 60px; height: 60px; font-size: 38px; }
    .visual-panel img { height: 180px; }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:12px 0 22px;">
        <div style="font-size:48px;">🩺</div>
        <div style="font-size:24px;font-weight:800;color:#19e0d0;">
            MediLens
        </div>
        <div style="font-size:11px;color:#9eb8cb;letter-spacing:2px;">
            MEDICAL REPORT EXPLAINER
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Navigation")
    page = st.radio(
        "Choose a section",
        ["Home & Report Analysis", "About MediLens"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### Supported uploads")
    st.write("📄 PDF medical reports")
    st.write("🖼️ JPG, JPEG and PNG images")

    st.markdown("---")
    st.caption("Educational support only — not a medical diagnosis.")


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <div class="logo3d">+</div>
    <div>
        <div class="eyebrow">SMART HEALTH • CLEARER INSIGHTS</div>
        <div class="hero-title">Medi<span>Lens</span></div>
        <div class="hero-description">
            Your medical report, explained more clearly.
            Upload a laboratory report to organize results,
            review reference ranges, and explore educational explanations.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Medical photo
st.markdown("""
<div class="visual-panel">
    <img
        src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1400&q=85"
        alt="Healthcare professionals working with medical information">
    <div class="visual-label">
        ✦ MEDICAL TECHNOLOGY &nbsp; • &nbsp;
        LABORATORY INSIGHTS &nbsp; • &nbsp; PATIENT EDUCATION
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# FEATURE CARDS
# =========================================================

st.markdown('<div class="section-heading">Your health information, organized</div>',
            unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🧬</div>
        <div class="feature-title">Report Analysis</div>
        <div class="feature-text">
            Extract and organize test values from a supported report.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔬</div>
        <div class="feature-title">Laboratory Insights</div>
        <div class="feature-text">
            Review reported values alongside available reference ranges.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🩺</div>
        <div class="feature-title">Health Education</div>
        <div class="feature-text">
            Explore general explanations and prepare questions for your clinician.
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# ABOUT PAGE
# =========================================================

if page == "About MediLens":
    st.markdown('<div class="section-heading">About MediLens</div>',
                unsafe_allow_html=True)

    st.write("""
    MediLens is an educational application designed to help users
    organize information found in medical laboratory reports.

    **Features**
    - PDF and image upload
    - Text extraction and OCR support
    - Laboratory result analysis
    - Reference-range review
    - Educational explanations
    - Laboratory result visualization
    - PDF report export
    """)

    st.warning(
        "MediLens is not a substitute for a doctor. "
        "Extraction and interpretation can be inaccurate. "
        "Always verify the original report with a qualified healthcare professional."
    )

    st.stop()


# =========================================================
# REPORT UPLOAD
# =========================================================

st.markdown('<div class="section-heading">📄 Upload your medical report</div>',
            unsafe_allow_html=True)

st.write("Choose a PDF or an image of your medical report.")

uploaded_file = st.file_uploader(
    "Select your report",
    type=["pdf", "png", "jpg", "jpeg"],
    key="medical_report_upload"
)

analyze_button = st.button(
    "🔍 Analyze Medical Report",
    type="primary",
    use_container_width=True
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def find_column(dataframe, possible_names):
    """Find a column without depending on capitalization."""
    if dataframe is None or dataframe.empty:
        return None

    normalized = {
        str(column).strip().lower().replace("_", " "): column
        for column in dataframe.columns
    }

    for name in possible_names:
        key = name.strip().lower().replace("_", " ")
        if key in normalized:
            return normalized[key]

    for normalized_name, original_name in normalized.items():
        for name in possible_names:
            key = name.strip().lower().replace("_", " ")
            if key in normalized_name or normalized_name in key:
                return original_name

    return None


def get_status_column(dataframe):
    return find_column(
        dataframe,
        ["status", "result status", "interpretation", "condition"]
    )


def safe_number(value):
    """Convert a simple numeric lab value into a number."""
    if pd.isna(value):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    # Remove common separators and extract the first numeric value.
    value_text = str(value).replace(",", "")
    match = re.search(r"[-+]?\d*\.?\d+", value_text)

    if not match:
        return None

    try:
        return float(match.group())
    except (TypeError, ValueError):
        return None


def get_patient_fields(report_text):
    """
    Extract basic patient details only if the existing module supports it.
    Otherwise, use an empty dictionary.
    """
    try:
        from ai_explainer import extract_patient_fields
        result = extract_patient_fields(report_text)
        return result if isinstance(result, dict) else {}
    except (ImportError, AttributeError, TypeError, ValueError):
        return {}


def get_explanation(report_text, results, patient):
    """Call the existing educational explanation module."""
    return explain_report(
        report_text=report_text,
        results_df=results,
        patient_fields=patient
    )


# =========================================================
# PROCESS UPLOAD
# =========================================================

if analyze_button:
    if uploaded_file is None:
        st.warning("Please upload a medical report first.")

    else:
        report_text = ""

        try:
            with st.spinner("Reading your report..."):
                file_bytes = uploaded_file.getvalue()
                extension = uploaded_file.name.lower().rsplit(".", 1)[-1]

                if extension == "pdf":
                    try:
                        # First try ordinary PDF text extraction.
                        report_text = extract_text_from_pdf(
                            io.BytesIO(file_bytes)
                        )
                    except Exception:
                        report_text = ""

                    # Scanned PDFs may not contain selectable text.
                    if not report_text or not report_text.strip():
                        try:
                            from extractor import extract_text_from_scanned_pdf
                            report_text = extract_text_from_scanned_pdf(
                                io.BytesIO(file_bytes)
                            )
                        except (ImportError, AttributeError):
                            try:
                                from ocr_service import extract_text_from_pdf
                                report_text = extract_text_from_pdf(
                                    io.BytesIO(file_bytes)
                                )
                            except (ImportError, AttributeError):
                                report_text = ""

                else:
                    # Image OCR is provided by the existing project module.
                    report_text = extract_text_from_image(
                        io.BytesIO(file_bytes)
                    )

            if not report_text or not str(report_text).strip():
                st.error(
                    "No readable text was extracted. "
                    "Try a clearer image or a PDF with selectable text. "
                    "Scanned PDFs require a working OCR function."
                )
                st.stop()

            with st.spinner("Analyzing laboratory results..."):
                results = analyze_report(report_text)

            if not isinstance(results, pd.DataFrame):
                results = pd.DataFrame(results)

            patient = get_patient_fields(report_text)

            # Keep the result available across Streamlit reruns.
            st.session_state["medilens_report_text"] = report_text
            st.session_state["medilens_results"] = results
            st.session_state["medilens_patient"] = patient
            st.session_state["medilens_filename"] = uploaded_file.name

        except Exception as error:
            st.error("The report could not be processed.")
            st.code(str(error))
            st.info(
                "Check that extractor.py, ocr_service.py, analyzer.py, "
                "ai_explainer.py and report_generator.py contain the "
                "functions imported by this app."
            )


# =========================================================
# SHOW ANALYSIS RESULTS
# =========================================================

if "medilens_results" in st.session_state:
    results = st.session_state["medilens_results"]
    report_text = st.session_state["medilens_report_text"]
    patient = st.session_state["medilens_patient"]

    st.markdown('<div class="section-heading">📊 Report overview</div>',
                unsafe_allow_html=True)

    st.caption(
        "File: " + str(st.session_state.get("medilens_filename", "Report"))
    )

    # Patient details
    if patient:
        with st.expander("👤 Patient details extracted from report"):
            for key, value in patient.items():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

    # Status counts
    status_column = get_status_column(results)

    below_count = 0
    above_count = 0
    within_count = 0
    urgent_count = 0

    if status_column is not None:
        status_values = results[status_column].astype(str).str.lower()

        below_count = int(
            status_values.str.contains(
                r"below|low", regex=True, na=False
            ).sum()
        )

        above_count = int(
            status_values.str.contains(
                r"above|high|elevated", regex=True, na=False
            ).sum()
        )

        within_count = int(
            status_values.str.contains(
                r"within|normal|in range", regex=True, na=False
            ).sum()
        )

        urgent_count = int(
            status_values.str.contains(
                r"critical|urgent", regex=True, na=False
            ).sum()
        )

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Tests found", len(results))
    m2.metric("Below range", below_count)
    m3.metric("Above range", above_count)
    m4.metric("Within range", within_count)

    if urgent_count:
        st.warning(
            f"{urgent_count} result(s) are marked critical or urgent "
            "by the analyzer. Contact a healthcare professional promptly "
            "and follow the original report's instructions."
        )

    # Table
    st.markdown('<div class="section-heading">🧪 Laboratory findings</div>',
                unsafe_allow_html=True)

    if results.empty:
        st.warning(
            "No structured laboratory findings were detected. "
            "Check the extracted report text below."
        )
    else:
        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True
        )

    # =====================================================
    # COMBINED GRAPH
    # =====================================================

    st.markdown('<div class="section-heading">📈 Lab results visualization</div>',
                unsafe_allow_html=True)

    test_column = find_column(
        results,
        ["test", "test name", "parameter", "test_name",
         "lab test", "investigation", "name"]
    )

    value_column = find_column(
        results,
        ["result", "value", "test result", "numeric value",
         "observed value", "reading"]
    )

    if test_column is not None and value_column is not None:
        chart_data = results[[test_column, value_column]].copy()

        chart_data.columns = ["Test", "Original value"]
        chart_data["Numeric value"] = chart_data["Original value"].apply(
            safe_number
        )
        chart_data = chart_data.dropna(subset=["Numeric value"])

        if not chart_data.empty:
            chart_data["Test"] = chart_data["Test"].astype(str)

            st.bar_chart(
                chart_data.set_index("Test")["Numeric value"],
                color="#19e0d0",
                height=400,
                use_container_width=True
            )

            st.caption(
                "The graph displays numeric values extracted from the report. "
                "Tests may use different units and reference ranges, so bar "
                "heights should not be interpreted as a direct comparison "
                "of medical importance."
            )

            with st.expander("View graph values"):
                st.dataframe(
                    chart_data[["Test", "Original value"]],
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info(
                "No numeric test values were recognized for the graph. "
                "The table above still displays the analyzer's findings."
            )
    else:
        st.info(
            "The graph needs a test-name column and a numeric result column. "
            "Your analyzer's column names were not recognized automatically. "
            "The findings table above remains available."
        )

    # =====================================================
    # EDUCATIONAL EXPLANATION
    # =====================================================

    st.markdown(
        '<div class="section-heading">🤖 Educational explanation</div>',
        unsafe_allow_html=True
    )

    if st.button("✨ Generate report explanation", use_container_width=True):
        try:
            with st.spinner("Preparing educational explanations..."):
                explanation = get_explanation(
                    report_text,
                    results,
                    patient
                )

            st.session_state["medilens_explanation"] = explanation

        except Exception as error:
            st.error("Could not generate the explanation.")
            st.code(str(error))

    if "medilens_explanation" in st.session_state:
        explanation = st.session_state["medilens_explanation"]

        if isinstance(explanation, dict):
            summary = explanation.get(
                "summary",
                explanation.get("overall_summary", "")
            )

            if isinstance(summary, dict):
                summary = summary.get(
                    "text",
                    summary.get("message", str(summary))
                )

            if summary:
                st.markdown("#### 🩺 Summary")
                st.write(summary)

            test_explanations = explanation.get(
                "test_explanations",
                explanation.get("explanations", [])
            )

            if isinstance(test_explanations, dict):
                test_explanations = [
                    {"test": key, "explanation": value}
                    for key, value in test_explanations.items()
                ]

            if isinstance(test_explanations, list):
                st.markdown("#### 🔬 Individual test explanations")

                for item in test_explanations:
                    if isinstance(item, dict):
                        title = item.get(
                            "test",
                            item.get("test_name", "Test explanation")
                        )
                        body = item.get(
                            "explanation",
                            item.get("description", item.get("meaning", ""))
                        )

                        with st.expander(str(title)):
                            st.write(body)

                            for key in [
                                "status", "possible_causes",
                                "causes", "follow_up",
                                "recommendation", "notes"
                            ]:
                                if key in item and item[key]:
                                    st.write(
                                        f"**{key.replace('_', ' ').title()}:**"
                                    )
                                    value = item[key]
                                    if isinstance(value, list):
                                        for entry in value:
                                            st.write(f"- {entry}")
                                    else:
                                        st.write(value)

            for key in [
                "general_notes",
                "follow_up",
                "recommendations",
                "disclaimer"
            ]:
                if explanation.get(key):
                    st.markdown(
                        f"#### {key.replace('_', ' ').title()}"
                    )
                    value = explanation[key]

                    if isinstance(value, list):
                        for entry in value:
                            st.write(f"- {entry}")
                    else:
                        st.write(value)

        elif isinstance(explanation, str):
            st.markdown(explanation)

        else:
            st.write(explanation)

    # =====================================================
    # EXTRACTED TEXT
    # =====================================================

    with st.expander("🔎 Verify extracted report text"):
        st.caption(
            "Check the extracted text against the original report. "
            "OCR can misread numbers, units, names and reference ranges."
        )
        st.text_area(
            "Extracted text",
            value=str(report_text),
            height=300,
            disabled=True,
            key="medilens_extracted_text"
        )

    # =====================================================
    # PDF EXPORT
    # =====================================================

    st.markdown('<div class="section-heading">📥 Export report</div>',
                unsafe_allow_html=True)

    if st.button("Create downloadable PDF report"):
        try:
            pdf_result = generate_pdf_report(
                report_text=report_text,
                results_df=results,
                explanation=st.session_state.get(
                    "medilens_explanation", {}
                )
            )

            if isinstance(pdf_result, bytes):
                pdf_bytes = pdf_result
            elif isinstance(pdf_result, bytearray):
                pdf_bytes = bytes(pdf_result)
            elif hasattr(pdf_result, "getvalue"):
                pdf_bytes = pdf_result.getvalue()
            else:
                pdf_bytes = None

            if pdf_bytes:
                st.session_state["medilens_pdf"] = pdf_bytes
            else:
                st.warning(
                    "The PDF generator did not return PDF bytes. "
                    "Check its function's return value."
                )

        except Exception as error:
            st.error("PDF export failed.")
            st.code(str(error))

    if "medilens_pdf" in st.session_state:
        st.download_button(
            "⬇️ Download PDF",
            data=st.session_state["medilens_pdf"],
            file_name="MediLens_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# =========================================================
# DISCLAIMER + FOOTER
# =========================================================

st.markdown("---")

st.warning(
    "Medical disclaimer: MediLens provides educational information only. "
    "It does not diagnose diseases, replace professional medical advice, "
    "or determine treatment. Automated text extraction and analysis may "
    "be incorrect. Verify every result, unit and reference range against "
    "the original report and consult a qualified healthcare professional."
)

st.markdown("""
<div class="footer">
    <div style="font-size:22px;margin-bottom:8px;">🩺</div>
    <strong style="color:#19e0d0;">MediLens</strong>
    <br>
    Medical Report Explainer • Built for patient education
    <br><br>
    Your report. Clearer information. Better questions for your clinician.
</div>
""", unsafe_allow_html=True)

