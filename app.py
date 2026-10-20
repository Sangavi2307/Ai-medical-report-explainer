
import hashlib
import streamlit as st
import pandas as pd

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image, extract_text_from_scanned_pdf
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import explain_report
from report_generator import generate_pdf_report


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MediLens AI | Medical Report Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# MODERN AI WEBSITE DESIGN
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #070b14;
    --panel: #101725;
    --panel2: #141e30;
    --border: #253248;
    --text: #f3f7ff;
    --muted: #9baac0;
    --teal: #48e4c2;
    --blue: #6b91ff;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, #102c35 0%, transparent 35%),
        radial-gradient(ellipse at 95% 5%, #171b3c 0%, transparent 30%),
        var(--bg);
    color: var(--text);
}

#MainMenu, footer, header {
    visibility: hidden;
}

[data-testid="stSidebar"] {
    display: none;
}

.block-container {
    max-width: 1240px;
    padding: 1.5rem 4% 3rem 4%;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: -0.5px;
    color: var(--text);
}

p, li, label {
    color: #c3cde0;
}

.brand {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: var(--text);
    line-height: 1.1;
}

.brand span {
    color: var(--teal);
}

.brand-caption {
    color: var(--muted);
    font-size: 12px;
    margin-top: 7px;
}

.eyebrow {
    color: var(--teal);
    text-transform: uppercase;
    letter-spacing: 2px;
    font-size: 11px;
    font-weight: 700;
}

.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(125deg, #101d2d, #132a38 55%, #18213b);
    border: 1px solid #2a4654;
    border-radius: 28px;
    padding: 48px 40px;
    margin: 30px 0 24px 0;
}

.hero h1 {
    font-size: clamp(34px, 5vw, 58px);
    line-height: 1.12;
    margin: 16px 0;
}

.hero h1 span {
    color: var(--teal);
}

.hero p {
    color: #b4c4d9;
    font-size: 16px;
    line-height: 1.8;
    max-width: 650px;
}

.section-label {
    color: var(--teal);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
}

.panel {
    background: linear-gradient(145deg, #111b2b, #0e1624);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 23px;
    min-height: 155px;
}

.panel h3 {
    font-size: 18px;
    margin: 12px 0 7px 0;
}

.panel p {
    font-size: 13px;
    color: var(--muted);
    line-height: 1.7;
}

.icon-box {
    background: #183c3d;
    color: var(--teal);
    border: 1px solid #285b57;
    border-radius: 12px;
    width: 43px;
    height: 43px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 21px;
}

.status-note {
    background: #101d2a;
    border: 1px solid #2b4852;
    padding: 16px;
    border-radius: 14px;
    color: #c7d9e7;
    font-size: 13px;
    line-height: 1.7;
}

.disclaimer {
    background: #241f18;
    border: 1px solid #6c5631;
    color: #f3dba6;
    border-radius: 14px;
    padding: 16px;
    font-size: 13px;
    line-height: 1.7;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #141f30, #101725);
    border: 1px solid #29364c;
    padding: 19px;
    border-radius: 17px;
}

div[data-testid="stMetricLabel"] {
    color: #a9b8cd;
}

div[data-testid="stMetricValue"] {
    color: var(--teal);
    font-family: 'Space Grotesk', sans-serif;
}

div[data-testid="stFileUploader"] {
    background: #101725;
    border: 1px dashed #427a78;
    border-radius: 17px;
    padding: 14px;
}

.stButton button, .stDownloadButton button {
    border-radius: 11px;
    min-height: 43px;
    font-weight: 600;
    border: 1px solid #34445c;
    transition: 0.2s ease;
}

.stButton button[kind="primary"] {
    background: var(--teal);
    color: #07111a;
    border: none;
}

.stButton button:hover, .stDownloadButton button:hover {
    border-color: var(--teal);
}

div[data-testid="stDataFrame"] {
    border: 1px solid #29364c;
    border-radius: 14px;
    overflow: hidden;
}

.stTextArea textarea {
    background: #0b1220;
    color: #d9e7f7;
    border: 1px solid #2a3b53;
    border-radius: 12px;
}

hr {
    border-color: #27354a;
}

.footer {
    text-align: center;
    color: #8392a9;
    font-size: 12px;
    line-height: 2;
    border-top: 1px solid #243047;
    margin-top: 45px;
    padding-top: 23px;
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

@media (max-width: 700px) {
    .hero {
        padding: 28px 22px;
    }
    .block-container {
        padding: 1rem 5% 2rem 5%;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "ml_page": "Home",
    "ml_analysis": None,
    "ml_explanation": None,
    "ml_file_hash": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# NAVIGATION HELPERS
# =========================================================

def navigate(page):
    st.session_state.ml_page = page


def clear_analysis():
    st.session_state.ml_analysis = None
    st.session_state.ml_explanation = None
    st.session_state.ml_file_hash = None


# =========================================================
# HEADER
# =========================================================

header_left, header_right = st.columns([2.5, 3])

with header_left:
    st.markdown("""
    <div class="brand">MediLens<span>.</span></div>
    <div class="brand-caption">MEDICAL REPORT INTELLIGENCE</div>
    """, unsafe_allow_html=True)

with header_right:
    nav1, nav2, nav3 = st.columns(3)

    if nav1.button("⌂  Home", use_container_width=True):
        navigate("Home")
        st.rerun()

    if nav2.button("✳  Workspace", use_container_width=True):
        navigate("Workspace")
        st.rerun()

    if nav3.button("ⓘ  About", use_container_width=True):
        navigate("About")
        st.rerun()


# =========================================================
# REPORT EXTRACTION
# =========================================================

def extract_report_text(uploaded_file):
    """Extract text only from the selected upload."""

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


def status_counts(results):
    """Count statuses returned by the existing analyzer."""

    if results is None or results.empty or "Status" not in results.columns:
        return 0, 0, 0

    statuses = results["Status"].fillna("").astype(str).str.lower()

    below = statuses.str.contains(
        r"below|low|decreased", regex=True
    ).sum()

    above = statuses.str.contains(
        r"above|high|increased", regex=True
    ).sum()

    within = statuses.str.contains(
        r"within|normal|reference range", regex=True
    ).sum()

    return int(below), int(within), int(above)


def numeric_chart_data(results):
    """Prepare numeric results for a chart."""

    if results is None or results.empty:
        return pd.DataFrame()

    if not {"Test", "Result"}.issubset(results.columns):
        return pd.DataFrame()

    chart = results[["Test", "Result"]].copy()

    chart["Result"] = (
        chart["Result"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"([-+]?\d*\.?\d+)")[0]
    )

    chart["Result"] = pd.to_numeric(
        chart["Result"], errors="coerce"
    )

    chart = chart.dropna(subset=["Result"])
    return chart


# =========================================================
# HOME PAGE
# =========================================================

if st.session_state.ml_page == "Home":

    st.markdown("""
    <div class="hero">
        <div class="eyebrow">✦ YOUR PERSONAL REPORT EXPLORER</div>
        <h1>Medical reports.<br><span>More understandable.</span></h1>
        <p>
        Explore extracted laboratory results, organize important values,
        and read educational explanations in one clean workspace.
        </p>
    </div>
    """, unsafe_allow_html=True)

    start_col, info_col = st.columns([1.3, 2.7])

    with start_col:
        if st.button(
            "✳  Open Analysis Workspace",
            type="primary",
            use_container_width=True,
        ):
            navigate("Workspace")
            st.rerun()

    with info_col:
        st.markdown(
            '<div class="status-note">🔒 Upload one report at a time. '
            'Review extracted values against the original document.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("### Built for clearer understanding")
    st.write("A simple workflow for exploring the information in your report.")

    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown("""
        <div class="panel">
            <div class="icon-box">📄</div>
            <h3>Upload a report</h3>
            <p>Read supported PDF documents and medical report images.</p>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="panel">
            <div class="icon-box">⌁</div>
            <h3>Explore the results</h3>
            <p>Review detected values, reference ranges, and reported statuses.</p>
        </div>
        """, unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div class="panel">
            <div class="icon-box">✧</div>
            <h3>Understand the report</h3>
            <p>View educational explanations and download a report summary.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
        <b>Medical safety notice</b><br>
        MediLens is an educational student project, not a diagnostic service.
        Extraction and result classification can be inaccurate or incomplete.
        Verify values with the original report and consult a qualified
        healthcare professional about medical concerns.
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# ANALYSIS WORKSPACE
# =========================================================

elif st.session_state.ml_page == "Workspace":

    st.markdown('<div class="eyebrow">YOUR PRIVATE WORKSPACE</div>',
                unsafe_allow_html=True)

    st.title("Report analysis")
    st.write(
        "Upload a report, extract its text, and explore the results "
        "detected by your existing analyzer."
    )

    uploaded_file = st.file_uploader(
        "Choose a medical report",
        type=["pdf", "png", "jpg", "jpeg"],
        help="PDF, PNG, JPG or JPEG. Maximum 10 MB.",
        key="ml_report_upload",
    )

    current_hash = None

    if uploaded_file is not None:
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("This file exceeds the 10 MB upload limit.")
        else:
            file_bytes = uploaded_file.getvalue()
            current_hash = hashlib.sha256(file_bytes).hexdigest()

            st.markdown(
                f'<div class="status-note">📎 Selected file: '
                f'<b>{uploaded_file.name}</b></div>',
                unsafe_allow_html=True,
            )

            # Never display the previous report's results for a new upload.
            if (
                st.session_state.ml_file_hash is not None
                and current_hash != st.session_state.ml_file_hash
            ):
                clear_analysis()

            if st.button(
                "✦  Analyze Selected Report",
                type="primary",
                use_container_width=True,
            ):
                clear_analysis()

                try:
                    with st.spinner("Extracting text from your report..."):
                        uploaded_file.seek(0)
                        report_text = extract_report_text(uploaded_file)

                    if not report_text or len(report_text.strip()) < 10:
                        st.error(
                            "Readable text was not detected. Try a clearer "
                            "image or a text-based PDF."
                        )
                    else:
                        with st.spinner("Organizing detected results..."):
                            results = analyze_report(report_text)
                            patient = extract_patient_fields(report_text)

                        st.session_state.ml_analysis = {
                            "filename": uploaded_file.name,
                            "text": report_text,
                            "results": results,
                            "patient": patient,
                        }

                        st.session_state.ml_file_hash = current_hash
                        st.rerun()

                except Exception as error:
                    st.error("The selected report could not be processed.")
                    st.code(str(error))

    analysis = st.session_state.ml_analysis

    # Only display results when the selected file matches the analyzed file.
    if (
        analysis is not None
        and current_hash is not None
        and current_hash == st.session_state.ml_file_hash
    ):
        report_text = analysis["text"]
        results = analysis["results"]
        patient = analysis["patient"]
        filename = analysis["filename"]

        st.divider()

        st.markdown('<div class="eyebrow">ANALYSIS RESULTS</div>',
                    unsafe_allow_html=True)

        st.subheader("Report overview")
        st.caption(f"Source file: {filename}")

        if patient:
            with st.expander("View details detected in the report"):
                st.json(patient, expanded=False)

        below, within, above = status_counts(results)

        c1, c2, c3 = st.columns(3)
        c1.metric("Below range", below)
        c2.metric("Within range", within)
        c3.metric("Above range", above)

        st.markdown("### Detected laboratory results")

        if results is not None and not results.empty:
            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "↓ Download CSV",
                data=results.to_csv(index=False).encode("utf-8"),
                file_name="medilens_results.csv",
                mime="text/csv",
                use_container_width=True,
            )

            chart = numeric_chart_data(results)

            if not chart.empty:
                st.markdown("### Result visualization")
                st.caption(
                    "This chart displays numeric values only. Different "
                    "tests may use different units, so compare each result "
                    "with its own reference range."
                )

                st.bar_chart(chart.set_index("Test"))

        else:
            st.info(
                "No structured test results were detected. You can inspect "
                "the extracted text below."
            )

        st.divider()
        st.markdown("### Educational explanation")

        if st.button("✧ Generate explanation", use_container_width=True):
            try:
                with st.spinner("Preparing an explanation..."):
                    explanation = explain_report(
                        report_text,
                        results,
                        patient,
                    )
                    st.session_state.ml_explanation = explanation

            except Exception as error:
                st.error("The explanation could not be generated.")
                st.code(str(error))

        explanation = st.session_state.ml_explanation

        if explanation:
            if isinstance(explanation, str):
                st.markdown(explanation)
            else:
                st.write(explanation)

        with st.expander("Inspect extracted text"):
            st.text_area(
                "Text extracted from the selected report",
                value=report_text,
                height=280,
                disabled=True,
            )

        st.markdown("### Export your summary")

        try:
            summary = (
                f"Detected rows: {len(results)}. "
                f"Below range: {below}; within range: {within}; "
                f"above range: {above}."
            )

            pdf_data = generate_pdf_report(
                filename,
                patient,
                results,
                summary,
            )

            if pdf_data:
                st.download_button(
                    "↓ Download PDF summary",
                    data=pdf_data,
                    file_name="medilens_summary.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

        except Exception as error:
            st.warning("The PDF summary could not be created.")
            st.code(str(error))

        st.markdown("""
        <div class="disclaimer">
        <b>Important:</b> The counts represent classifications produced by
        the existing analyzer, not a medical diagnosis. Verify extracted
        values and reference ranges against the original document.
        </div>
        """, unsafe_allow_html=True)

        if st.button("Clear current analysis"):
            clear_analysis()
            st.rerun()

    elif analysis is not None and uploaded_file is None:
        st.info("Upload the report again to view its analysis.")


# =========================================================
# ABOUT PAGE
# =========================================================

elif st.session_state.ml_page == "About":

    st.markdown('<div class="eyebrow">ABOUT THE PROJECT</div>',
                unsafe_allow_html=True)

    st.title("About MediLens")
    st.write(
        "MediLens is an educational application designed to make "
        "medical report information easier to explore."
    )

    st.markdown("### Project features")

    st.markdown("""
    - PDF and image text extraction
    - Structured laboratory result display
    - Status summaries and numeric charts
    - Educational explanations
    - CSV and PDF downloads
    """)

    st.markdown("### Limitations")

    st.markdown("""
    Text extraction may miss values. The analyzer may incorrectly identify
    tests or reference ranges. An explanation is only as reliable as the
    extracted text and underlying analysis rules.
    """)

    st.markdown("""
    <div class="disclaimer">
    MediLens cannot diagnose a condition, recommend treatment, or replace
    professional medical advice. Use fictional sample reports when testing
    the app, and take care with sensitive health information.
    </div>
    """, unsafe_allow_html=True)


# ================