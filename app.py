

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
    --background: #071321;
    --surface: #10243a;
    --teal: #19d8c5;
    --text: #edf7ff;
    --muted: #a8bfd1;
    --border: #254258;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 90% 0%, #12394d 0%, transparent 35%),
        linear-gradient(145deg, #050d18, #091a2b 65%, #071321);
    color: var(--text);
}

.block-container {
    max-width: 1320px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d2033, #07111f);
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: #edf7ff;
}

[data-testid="stSidebar"] hr {
    border-color: var(--border);
}

/* ANIMATIONS */

@keyframes logoFloat {
    0%, 100% { transform: translateY(0) rotateY(-5deg); }
    50% { transform: translateY(-5px) rotateY(5deg); }
}

@keyframes logoGlow {
    0%, 100% { box-shadow: 0 0 12px #19d8c522, 4px 5px 12px #0008; }
    50% { box-shadow: 0 0 25px #19d8c555, 4px 5px 12px #0008; }
}

@keyframes appear {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

/* BRAND HEADER */

.brand-header {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 8px 0 24px;
    animation: appear .7s ease-out;
}

.brand-logo {
    width: 66px;
    height: 66px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 19px;
    background: linear-gradient(145deg, #35f1df, #087e9b);
    color: #071321;
    font-family: 'Manrope', sans-serif;
    font-size: 44px;
    font-weight: 800;
    border: 1px solid #8ff9ef;
    animation: logoFloat 4s ease-in-out infinite,
               logoGlow 3s ease-in-out infinite;
    transform-style: preserve-3d;
}

.brand-title {
    color: #f3fbff;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(27px, 3vw, 40px);
    font-weight: 800;
    letter-spacing: -1px;
    line-height: 1.2;
}

.brand-subtitle {
    color: #b7cddd;
    font-size: 14px;
    margin-top: 8px;
    line-height: 1.7;
}

.eyebrow {
    color: #67e8da;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 7px;
}

/* PROFESSIONAL MEDICAL BANNER */

.professional-banner {
    position: relative;
    height: 320px;
    overflow: hidden;
    border-radius: 18px;
    background: #0b1c2e;
    border: 1px solid #29465b;
    margin: 0 0 28px;
    box-shadow: 0 15px 35px #0005;
    animation: appear .8s ease-out;
}

.professional-banner img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center 35%;
    display: block;
    opacity: .7;
    transition: transform .5s ease;
}

.professional-banner:hover img {
    transform: scale(1.025);
}

.professional-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    padding: 35px;
    background: linear-gradient(
        90deg,
        rgba(5, 18, 32, .96) 0%,
        rgba(5, 18, 32, .80) 47%,
        rgba(5, 18, 32, .15) 100%
    );
}

.professional-label {
    color: #70e7db;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

.professional-overlay h2 {
    color: #ffffff;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(24px, 3vw, 36px);
    font-weight: 800;
    line-height: 1.25;
    max-width: 520px;
    margin: 0 0 12px;
}

.professional-overlay p {
    color: #d8e7f1;
    font-size: 14px;
    line-height: 1.7;
    max-width: 460px;
}

/* SECTION HEADINGS */

.section-heading {
    font-family: 'Manrope', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #eaf8ff;
    margin-top: 24px;
    margin-bottom: 5px;
}

.section-caption {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 17px;
}

/* PANELS */

.panel {
    background: linear-gradient(145deg, #132b42, #0a1929);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 21px;
    margin-bottom: 16px;
    box-shadow: 5px 7px 17px #0004;
    transition: transform .25s ease, border-color .25s ease;
    animation: appear .7s ease-out;
}

.panel:hover {
    transform: translateY(-3px);
    border-color: #258b8b;
}

.panel-title {
    color: #f0fbff;
    font-size: 16px;
    font-weight: 800;
    margin-bottom: 8px;
}

.panel-description {
    color: #b0c4d4;
    font-size: 13px;
    line-height: 1.8;
}

/* KPI CARDS */

.kpi {
    background: linear-gradient(145deg, #142e46, #0a1928);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px;
    min-height: 105px;
    box-shadow: 5px 7px 17px #0003;
    transition: transform .25s ease;
}

.kpi:hover {
    transform: translateY(-4px);
}

.kpi-label {
    color: #b1c7d7;
    font-size: 12px;
    font-weight: 600;
}

.kpi-value {
    color: var(--teal);
    font-family: 'Manrope', sans-serif;
    font-size: 28px;
    font-weight: 800;
    margin-top: 8px;
}

.kpi-note {
    color: #a8bfd1;
    font-size: 11px;
    margin-top: 3px;
}

/* NOTICE BOXES */

.status-box {
    background: #102f3c;
    border: 1px solid #24796f;
    border-radius: 12px;
    padding: 15px;
    color: #b7fff5;
    font-size: 13px;
    line-height: 1.7;
}

.disclaimer {
    background: #302819;
    border: 1px solid #826632;
    border-left: 4px solid #d9a441;
    border-radius: 9px;
    padding: 17px;
    color: #ffedc3;
    font-size: 12px;
    line-height: 1.8;
}

/* FILE UPLOADER */

div[data-testid="stFileUploader"] {
    background: #0c2032;
    border: 1px dashed #258b96;
    border-radius: 14px;
    padding: 12px;
}

/* STREAMLIT METRICS */

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #142e46, #0a1928);
    border: 1px solid var(--border);
    padding: 15px;
    border-radius: 14px;
}

[data-testid="stMetricLabel"] {
    color: #b1c7d7;
}

[data-testid="stMetricValue"] {
    color: var(--teal);
}

/* BUTTONS */

.stButton button,
.stDownloadButton button {
    border-radius: 9px;
    font-weight: 700;
    min-height: 43px;
    background: linear-gradient(110deg, #20dfcf, #168ca6);
    color: #071321;
    border: 0;
    transition: transform .2s ease, box-shadow .2s ease;
}

.stButton button:hover,
.stDownloadButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 7px 18px #19d8c533;
    color: #ffffff;
}

/* TABLES AND EXPANDERS */

div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

[data-testid="stExpander"] {
    background: #0d2031;
    border: 1px solid var(--border);
    border-radius: 11px;
}

p, label, li {
    color: #dcebf5;
}

footer {
    visibility: hidden;
}

@media (max-width: 600px) {
    .brand-logo {
        width: 54px;
        height: 54px;
        font-size: 36px;
    }

    .professional-banner {
        height: 280px;
    }

    .professional-overlay {
        padding: 20px;
    }

    .panel {
        padding: 16px;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# REUSABLE HELPERS
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


def find_column_by_names(df, names):
    normalized = {
        str(col).strip().lower().replace("_", " "): col
        for col in df.columns
    }

    for name in names:
        key = name.strip().lower().replace("_", " ")
        if key in normalized:
            return normalized[key]

    return None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 20px;">
        <div style="
            display:flex;
            align-items:center;
            gap:10px;
            font-size:26px;
            font-weight:800;
            color:white;">
            <span style="
                display:inline-flex;
                align-items:center;
                justify-content:center;
                width:42px;
                height:42px;
                border-radius:12px;
                color:#071321;
                background:linear-gradient(145deg,#35f1df,#087e9b);
                box-shadow:0 0 16px #19d8c533;">
                +
            </span>
            MediLens
        </div>
        <div style="
            font-size:10px;
            color:#B8C8D9;
            letter-spacing:1.5px;
            margin-top:8px;">
            CLINICAL INTELLIGENCE
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("**WORKSPACE**")
    st.caption("Report analysis")
    st.caption("Clinical findings")
    st.caption("Report export")

    st.divider()
    st.markdown("**SUPPORTED FORMATS**")
    st.caption("PDF · JPG · JPEG · PNG")

    st.divider()
    st.markdown("**ANALYSIS PROCESS**")
    st.caption("01  Extract report")
    st.caption("02  Structure findings")
    st.caption("03  Review interpretation")
    st.caption("04  Export report")

    st.divider()
    st.caption("MediLens Clinical Intelligence")


# =========================================================
# PROFESSIONAL BRAND HEADER
# =========================================================

st.markdown("""
<div class="brand-header">
    <div class="brand-logo">+</div>
    <div>
        <div class="eyebrow">AI-POWERED HEALTHCARE TECHNOLOGY</div>
        <div class="brand-title">MediLens Clinical Intelligence</div>
        <div class="brand-subtitle">
            Medical report analysis, structured laboratory findings,
            and AI-assisted educational insights.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# PROFESSIONAL MEDICAL BANNER
# =========================================================

st.markdown("""
<div class="professional-banner">
    <img
        src="https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=1600&q=90"
        alt="Doctor reviewing medical information"
    >
    <div class="professional-overlay">
        <div class="professional-label">
            CLINICAL INTELLIGENCE PLATFORM
        </div>
        <h2>Understand Your Health Reports</h2>
        <p>
            Structured laboratory findings and AI-assisted
            educational insights in one workspace.
        </p>
    </div>
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
            • Educational result interpretation<br>
            • Clinical insights and PDF export
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# NO FILE STATE
# =========================================================

if not uploaded_file:
    st.markdown("""
    <div class="status-box">
        <b>Ready for report upload</b><br>
        Your analysis workspace will appear after a medical report is uploaded.
    </div>
    <br>
    <div class="disclaimer">
        <b>Medical disclaimer</b><br>
        MediLens provides educational information only.
        AI-assisted interpretation does not establish a confirmed diagnosis.
        Consult a qualified healthcare professional to confirm findings
        and determine appropriate treatment.
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# PROCESS UPLOADED FILE
# =========================================================

file_hash = hashlib.sha256(uploaded_file.getvalue()).hexdigest()

if st.session_state.get("report_hash") != file_hash:
    st.session_state["report_hash"] = file_hash
    st.session_state.pop("report_data", None)
    st.session_state.pop("report_insights", None)
    st.session_state.pop("report_pdf", None)


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

        st.success("Report extraction completed.")

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

if patient and isinstance(patient, dict):
    fields = list(patient.items())[:6]
    cols = st.columns(min(3, max(1, len(fields))))

    for index, (key, value) in enumerate(fields):
        with cols[index % len(cols)]:
            st.markdown(
                f"""
                <div class="panel">
                    <div class="kpi-label">
                        {safe_text(str(key).replace("_", " ").title())}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Render the value separately to avoid HTML closing-tag issues.
            display_value = str(value).strip() if value is not None else ""

            if not display_value or display_value.lower() in {
                "none", "nan", "null"
            }:
                display_value = "Not found in report"

            st.markdown(
                f"""
                <div style="
                    font-size:17px;
                    font-weight:800;
                    color:#eaf8ff;
                    margin-top:-12px;
                    margin-bottom:12px;
                    padding:0 16px 16px 16px;
                    background:#10232e;
                    border-radius:0 0 12px 12px;
                    overflow-wrap:anywhere;">
                    {safe_text(display_value)[:120]}
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
# LABORATORY FINDINGS
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

    status_col = get_status_column(results)

    if status_col:
        statuses = results[status_col].fillna("").astype(str).str.lower()

        selected_filter = st.selectbox(
            "Filter laboratory findings",
            [
                "All findings",
                "Below range",
                "Above range",
                "Within range",
            ],
        )

        if selected_filter == "Below range":
            view = results[
                statuses.str.contains(
                    r"\b(below|low|decreased)\b", regex=True
                )
            ]
        elif selected_filter == "Above range":
            view = results[
                statuses.str.contains(
                    r"\b(above|high|elevated|increased)\b", regex=True
                )
            ]
        elif selected_filter == "Within range":
            view = results[
                statuses.str.contains(
                    r"\b(within range|normal|normal range)\b",
                    regex=True,
                )
            ]
        else:
            view = results

        st.dataframe(view, use_container_width=True, hide_index=True)
    else:
        st.dataframe(results, use_container_width=True, hide_index=True)


# =========================================================
# LABORATORY GRAPH
# =========================================================

section(
    "Laboratory results visualization",
    "Visualize numeric test values extracted from this report.",
)

if not results.empty:
    test_col = find_column_by_names(
        results,
        ["test", "test name", "parameter", "investigation", "name"],
    )

    value_col = find_column_by_names(
        results,
        ["result", "value", "test result", "numeric value", "observed value"],
    )

    if test_col is not None and value_col is not None:
        chart_df = results[[test_col, value_col]].copy()
        chart_df.columns = ["Test", "Original value"]

        chart_df["Numeric value"] = pd.to_numeric(
            chart_df["Original value"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.extract(r"([-+]?\d*\.?\d+)")[0],
            errors="coerce",
        )

        chart_df = chart_df.dropna(subset=["Numeric value"])

        if not chart_df.empty:
            st.bar_chart(
                chart_df.set_index("Test")["Numeric value"],
                color="#19d8c5",
                height=400,
                use_container_width=True,
            )

            st.caption(
                "Tests may use different units and reference ranges. "
                "Bar heights do not indicate relative medical severity."
            )

            with st.expander("View graph source values"):
                st.dataframe(
                    chart_df[["Test", "Original value"]],
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.info("No numeric values were recognized for the graph.")
    else:
        st.info(
            "The graph could not identify the test and result columns. "
            "Check the column names returned by analyzer.py."
        )
else:
    st.info("Analyze a report to visualize laboratory results.")


# =========================================================
# CLINICAL INSIGHTS
# =========================================================

section(
    "04  Clinical insights",
    "Review explanations generated from the uploaded report.",
)

st.markdown("""
<div class="panel">
    <div class="panel-title">Report interpretation</div>
    <div class="panel-description">
        Review the summary and individual test explanations below.
        These explanations are educational and do not confirm a diagnosis.
    </div>
</div>
""", unsafe_allow_html=True)

if st.button(
    "Generate clinical insights",
    key="generate_clinical_insights",
    use_container_width=True,
):
    try:
        with st.spinner("Preparing clinical insights..."):
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
        else:
            st.error(
                "The explanation function returned an unexpected format."
            )

    except Exception as error:
        st.error("Unable to generate clinical insights.")
        st.exception(error)


insights_data = st.session_state.get("report_insights")

if insights_data and insights_data.get("hash") == file_hash:
    insights = insights_data.get("text", {})

    section("Overall summary")
    st.write(insights.get("summary", "No summary is available."))

    section("Individual test explanations")
    explanations = insights.get("results", [])

    if explanations:
        for index, item in enumerate(explanations, start=1):
            if not isinstance(item, dict):
                continue

            with st.expander(
                str(item.get("Test", f"Test {index}")),
                expanded=(index == 1),
            ):
                st.write("**Result:**", item.get("Result", "Not available"))
                st.write(
                    "**Reference range:**",
                    item.get("Reference Range", "Not available"),
                )
                st.write("**Status:**", item.get("Status", "Needs review"))
                st.write(
                    "**Meaning:**",
                    item.get("Meaning", "Not available"),
                )
                st.write(
                    "**Importance:**",
                    item.get("Importance", "Not available"),
                )
                st.write(
                    "**Interpretation:**",
                    item.get("Interpretation", "Not available"),
                )
                st.write(
                    "**Possible causes:**",
                    item.get("Possible Causes", "Not available"),
                )
                st.write(
                    "**Follow-up:**",
                    item.get(
                        "Follow-up",
                        "Discuss the result with a healthcare professional.",
                    ),
                )
    else:
        st.warning(
            "No individual explanations were returned. "
            "Check ai_explainer.py and the extracted test results."
        )

    section("Important notes")
    notes = insights.get("general_notes", [])

    if notes:
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
        "Click 'Generate clinical insights' to display the report explanation."
    )


# =========================================================
# SOURCE VERIFICATION
# =========================================================

with st.expander("Verify extracted source text"):
    st.write(
        "Compare the extracted text with the original file to check "
        "for OCR errors, missing values, units, and reference ranges."
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
    MediLens provides educational, AI-assisted medical report analysis.
    Findings may be incomplete or inaccurate and do not constitute a
    confirmed diagnosis. Verify every extracted value against the
    original report and consult a qualified healthcare professional.
    Seek urgent medical care for potentially serious symptoms.
</div>

<div style="
    text-align:center;
    color:#8faabd;
    font-size:11px;
    padding:22px;
    letter-spacing:1px;">
    + MEDILENS · CLINICAL INTELLIGENCE
</div>
""", unsafe_allow_html=True)
