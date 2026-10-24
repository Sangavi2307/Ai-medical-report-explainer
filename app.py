
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
# PROFESSIONAL DARK MEDICAL THEME
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #0B1728;
    --panel: #112238;
    --teal: #12CFC3;
    --blue: #4AA8FF;
    --border: #263D53;
    --muted: #A0B3C8;
    --ink: #EDF5FF;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 80% 0%, #16344A 0%, transparent 40%),
        #07111F;
    color: var(--ink);
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

h1, h2, h3, p, label {
    color: var(--ink);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102238, #091421);
    border-right: 1px solid #263D53;
}

[data-testid="stSidebar"] * {
    color: #EAF2FA;
}

[data-testid="stSidebar"] hr {
    border-color: #33475D;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 36px;
    border-radius: 24px;
    border: 1px solid #28606F;
    background: linear-gradient(120deg, #102238, #104B59 65%, #087F83);
    box-shadow: 0 18px 45px rgba(0,0,0,.3);
    margin-bottom: 30px;
}

.hero h1 {
    color: #FFFFFF;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(30px, 4vw, 45px);
    font-weight: 800;
    letter-spacing: -1.2px;
    margin: 12px 0;
}

.hero p {
    color: #D4E8F2;
    max-width: 760px;
    line-height: 1.8;
    font-size: 15px;
}

.eyebrow {
    color: #7DF5E5;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
}

.hero-pill {
    display: inline-block;
    border: 1px solid #5598A6;
    color: #E0FFFA;
    padding: 7px 12px;
    border-radius: 30px;
    font-size: 11px;
    margin: 5px 4px 0 0;
}

.medical-logo {
    width: 64px;
    height: 64px;
    border-radius: 19px;
    background: linear-gradient(145deg, #20E1D0, #087F8C);
    color: #06202D;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    font-weight: 800;
    box-shadow: 0 10px 25px rgba(18,207,195,.25);
    border: 1px solid #75F7E9;
}

.section-heading {
    font-family: 'Manrope', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #EDF5FF;
    margin-top: 25px;
    margin-bottom: 5px;
}

.section-caption {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 18px;
}

.panel {
    background: linear-gradient(145deg, #142840, #0D1B2D);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 16px;
    box-shadow: 0 12px 28px rgba(0,0,0,.22);
    transition: transform .2s ease, border-color .2s ease;
}

.panel:hover {
    transform: translateY(-2px);
    border-color: #168C91;
}

.panel-title {
    color: #F0F7FF;
    font-size: 16px;
    font-weight: 800;
    margin-bottom: 8px;
}

.panel-description {
    color: #A0B3C8;
    font-size: 13px;
    line-height: 1.8;
}

.kpi {
    background: linear-gradient(145deg, #152A42, #0D1B2D);
    border: 1px solid #263D53;
    border-radius: 16px;
    padding: 18px;
    min-height: 120px;
    box-shadow: 0 10px 24px rgba(0,0,0,.2);
    transition: transform .2s ease, box-shadow .2s ease;
}

.kpi:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 30px rgba(18,207,195,.12);
}

.kpi-label {
    color: #A0B3C8;
    font-size: 12px;
    font-weight: 600;
}

.kpi-value {
    color: #12CFC3;
    font-family: 'Manrope', sans-serif;
    font-size: 30px;
    font-weight: 800;
    margin-top: 8px;
}

.kpi-note {
    color: #8FA5BC;
    font-size: 11px;
    margin-top: 3px;
}

.status-box {
    background: #102E32;
    border: 1px solid #1B6564;
    border-radius: 13px;
    padding: 16px;
    color: #A9F3E8;
    font-size: 13px;
    line-height: 1.8;
}

.warning-box {
    background: #332817;
    border: 1px solid #745B2E;
    border-radius: 13px;
    padding: 16px;
    color: #FFE4A9;
    font-size: 13px;
    line-height: 1.8;
}

.disclaimer {
    background: #292519;
    border-left: 4px solid #E5B84F;
    border-radius: 9px;
    padding: 17px;
    color: #FFE6AC;
    font-size: 12px;
    line-height: 1.8;
}

div[data-testid="stFileUploader"] {
    background: #102238;
    border: 1px dashed #347C91;
    border-radius: 14px;
    padding: 12px;
}

div[data-testid="stMetric"] {
    background: #112238;
    border: 1px solid #263D53;
    padding: 15px;
    border-radius: 14px;
}

div[data-testid="stExpander"] {
    background: #102238;
    border: 1px solid #263D53;
    border-radius: 13px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #263D53;
    border-radius: 12px;
    overflow: hidden;
}

.stButton button, .stDownloadButton button {
    border-radius: 11px;
    font-weight: 700;
    min-height: 44px;
    border: 1px solid #247C83;
    transition: all .2s ease;
}

.stButton button:hover, .stDownloadButton button:hover {
    border-color: #12CFC3;
    box-shadow: 0 5px 18px rgba(18,207,195,.15);
}

div[data-baseweb="select"] > div {
    background-color: #102238;
    border-color: #344A61;
}

input, textarea {
    color: #EDF5FF !important;
}

hr {
    border-color: #263D53;
}

footer {
    visibility: hidden;
}

@media (max-width: 700px) {
    .hero { padding: 23px; }
    .panel { padding: 16px; }
    .kpi { padding: 13px; }
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
            <div class="kpi-label">{safe_text(label)}</div>
            <div class="kpi-value">{safe_text(value)}</div>
            <div class="kpi-note">{safe_text(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def find_column(df, candidates):
    normalized_columns = {
        str(col).strip().lower().replace("_", " "): col
        for col in df.columns
    }

    for candidate in candidates:
        if candidate in normalized_columns:
            return normalized_columns[candidate]

    return None


def get_status_column(df):
    return find_column(df, ["status", "result status", "flag"])


def get_counts(df):
    status_col = get_status_column(df)

    if status_col is None:
        return 0, 0, 0, 0

    status = df[status_col].fillna("").astype(str).str.lower()

    urgent = status.str.contains(
        r"urgent|critical", regex=True
    ).sum()

    low = status.str.contains(
        r"\b(below|low|decreased)\b", regex=True
    ).sum()

    high = status.str.contains(
        r"\b(above|high|elevated|increased)\b", regex=True
    ).sum()

    normal = status.str.contains(
        r"\b(within range|normal|normal range)\b", regex=True
    ).sum()

    return int(urgent), int(low), int(high), int(normal)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown("""
    <div style="padding:10px 0 22px;">
        <div class="medical-logo">✚</div>
        <div style="font-size:27px;font-weight:800;margin-top:13px;">
            MediLens
        </div>
        <div style="font-size:10px;color:#A0B3C8;letter-spacing:1.5px;">
            MEDICAL REPORT INTELLIGENCE
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("**YOUR WORKSPACE**")
    st.caption("01  Report analysis")
    st.caption("02  Laboratory dashboard")
    st.caption("03  Clinical insights")
    st.caption("04  PDF export")

    st.divider()

    st.markdown("**SUPPORTED FILES**")
    st.caption("PDF · JPG · JPEG · PNG")

    st.divider()

    st.markdown("**WORKFLOW**")
    st.caption("Extract → Structure → Review → Export")

    st.divider()
    st.caption("MediLens · Educational support only")


# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero">
    <div style="display:flex;gap:20px;align-items:center;flex-wrap:wrap;">
        <div class="medical-logo">✚</div>
        <div>
            <div class="eyebrow">AI-ASSISTED HEALTHCARE TECHNOLOGY</div>
            <h1>Medical Report Intelligence</h1>
        </div>
    </div>
    <p>
        Understand laboratory reports through structured results,
        a combined visual dashboard, and educational explanations.
        Review every extracted value against the original report.
    </p>
    <span class="hero-pill">REPORT ANALYSIS</span>
    <span class="hero-pill">VISUAL DASHBOARD</span>
    <span class="hero-pill">EDUCATIONAL INSIGHTS</span>
</div>
""", unsafe_allow_html=True)


# =========================================================
# UPLOAD WORKSPACE
# =========================================================

section(
    "01  Report workspace",
    "Upload one patient's medical report to start a new analysis.",
)

left, right = st.columns([1.5, 1], gap="large")

with left:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">📄 Upload medical report</div>
        <div class="panel-description">
            Import a laboratory report as a PDF or image.
            A clear, readable file generally improves text extraction.
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a report",
        type=["pdf", "jpg", "jpeg", "png"],
        key="medilens_upload",
    )

with right:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">✦ Analysis features</div>
        <div class="panel-description">
            • Patient information extraction<br>
            • Laboratory result structuring<br>
            • Abnormal value identification<br>
            • One combined results graph<br>
            • Educational explanations<br>
            • Downloadable PDF report
        </div>
    </div>
    """, unsafe_allow_html=True)


if not uploaded_file:
    st.markdown("""
    <div class="status-box">
        <b>✦ Your workspace is ready</b><br>
        Upload a report to display the patient overview,
        laboratory findings, graph, and educational explanations.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
        <b>Medical disclaimer</b><br>
        MediLens can make extraction and interpretation errors.
        It does not establish a confirmed diagnosis or replace
        professional medical care.
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# FILE PROCESSING
# =========================================================

file_hash = hashlib.sha256(uploaded_file.getvalue()).hexdigest()

if st.session_state.get("report_hash") != file_hash:
    st.session_state["report_hash"] = file_hash
    st.session_state.pop("report_data", None)
    st.session_state.pop("report_insights", None)
    st.session_state.pop("report_pdf", None)


st.markdown("<br>", unsafe_allow_html=True)

if st.button(
    "✦ Run medical report analysis",
    type="primary",
    use_container_width=True,
):
    try:
        with st.spinner("Extracting text from your report..."):
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
                "Not enough text could be extracted. "
                "Upload a clearer report or check OCR configuration."
            )
            st.stop()

        with st.spinner("Structuring laboratory results..."):
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
            "Check function names in extractor.py, ocr_service.py, "
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
    cols = st.columns(min(3, len(fields)))

    for index, (key, value) in enumerate(fields):
        with cols[index % len(cols)]:
            st.markdown(
                f"""
                <div class="panel">
                    <div class="kpi-label">
                        {safe_text(str(key).replace("_", " ").title())}
                    </div>
                    <div style="font-size:17px;font-weight:800;
                                color:#EDF5FF;margin-top:10px;">
                        {safe_text(value)[:120]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.info(
        "Patient details could not be confidently extracted. "
        "Verify the original report."
    )


# =========================================================
# LABORATORY DASHBOARD
# =========================================================

section(
    "03  Laboratory dashboard",
    "Review extracted results and their analyzer status.",
)

if results.empty:
    st.warning(
        "No structured laboratory values were detected. "
        "Check the test patterns in analyzer.py."
    )
else:
    urgent_count, low_count, high_count, normal_count = get_counts(results)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        kpi_card("Tests identified", len(results), "Extracted records")

    with c2:
        kpi_card("Urgent review", urgent_count, "Check promptly")

    with c3:
        kpi_card("Below range", low_count, "Analyzer flags")

    with c4:
        kpi_card("Above range", high_count, "Analyzer flags")

    with c5:
        kpi_card("Within range", normal_count, "Analyzer flags")

    st.markdown("<br>", unsafe_allow_html=True)

    status_col = get_status_column(results)

    if status_col:
        statuses = results[status_col].fillna("").astype(str).str.lower()

        selected_filter = st.selectbox(
            "Filter findings",
            [
                "All findings",
                "Urgent review",
                "Below range",
                "Above range",
                "Within range",
            ],
        )

        if selected_filter == "Urgent review":
            view = results[
                statuses.str.contains(r"urgent|critical", regex=True)
            ]
        elif selected_filter == "Below range":
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
                    r"\b(within range|normal|normal range)\b", regex=True
                )
            ]
        else:
            view = results

        st.dataframe(
            view,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# ONE COMBINED NUMERICAL GRAPH
# =========================================================

section(
    "04  Visual laboratory analysis",
    "All detected numeric results appear together in one graph.",
)

name_col = find_column(
    results,
    [
        "test", "test name", "parameter", "lab test",
        "investigation", "test parameter",
    ],
) if not results.empty else None

value_col = find_column(
    results,
    [
        "result", "value", "test result",
        "result value", "observed value",
    ],
) if not results.empty else None

if not results.empty and name_col is not None and value_col is not None:
    graph_df = results[[name_col, value_col]].copy()
    graph_df.columns = ["Test", "Original result"]

    graph_df["Numeric value"] = pd.to_numeric(
        graph_df["Original result"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"([-+]?\d*\.?\d+)")[0],
        errors="coerce",
    )

    graph_df = graph_df.dropna(subset=["Numeric value"])
    graph_df = graph_df.drop_duplicates(subset=["Test"]).head(30)

    if not graph_df.empty:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">📊 Combined laboratory results</div>
            <div class="panel-description">
                Each bar shows one numeric result extracted from the report.
                The graph is intended for visual exploration.
            </div>
        </div>
        """, unsafe_allow_html=True)

        chart_data = graph_df.set_index("Test")[["Numeric value"]]

        st.bar_chart(
            chart_data,
            y="Numeric value",
            color="#12CFC3",
            height=440,
            use_container_width=True,
        )

        with st.expander("View the values used in the graph"):
            st.dataframe(
                graph_df,
                use_container_width=True,
                hide_index=True,
            )

        st.caption(
            "Clinical note: different tests may use different units and "
            "scales. Bar height alone does not indicate normality or severity. "
            "Use the reference range for each individual test."
        )
    else:
        st.info("No numeric results were detected for the graph.")
else:
    st.info(
        "A graph requires identifiable test-name and result columns. "
        "Check the column names returned by analyzer.py."
    )


# =========================================================
# CLINICAL INSIGHTS
# =========================================================

section(
    "05  Educational clinical insights",
    "Review the explanation for each extracted result.",
)

st.markdown("""
<div class="panel">
    <div class="panel-title">✦ Report interpretation</div>
    <div class="panel-description">
        These explanations support understanding of the report.
        They are not a diagnosis and must be checked against the original report.
    </div>
</div>
""", unsafe_allow_html=True)

if st.button(
    "Generate clinical insights",
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
        else:
            st.error("The explanation function returned an unexpected format.")

    except Exception as error:
        st.error("Unable to generate clinical insights.")
        st.exception(error)


insights_data = st.session_state.get("report_insights")

if insights_data and insights_data.get("hash") == file_hash:
    insights = insights_data.get("text", {})

    section("Overall summary")
    summary = insights.get("summary", "No summary is available.")

    if isinstance(summary, dict):
        for key, value in summary.items():
            st.markdown(
                f"**{safe_text(str(key).replace('_', ' ').title())}:** "
                f"{safe_text(value)}"
            )
    else:
        st.write(summary)

    section("Individual test explanations")
    explanations = insights.get("results", [])

    if explanations:
        for index, item in enumerate(explanations, start=1):
            if not isinstance(item, dict):
                continue

            test_name = str(item.get("Test", f"Test {index}"))

            with st.expander(
                f"🧪 {test_name}",
                expanded=(index == 1),
            ):
                st.write("**Result:**", item.get("Result", "Not available"))
                st.write(
                    "**Reference range:**",
                    item.get("Reference Range", "Not available"),
                )
                st.write("**Status:**", item.get("Status", "Needs review"))
                st.write("**Meaning:**", item.get("Meaning", "Not available"))
                st.write(
                    "**Importance:**",
                    item.get("Importance", "Not available"),
                )
                st.write(
                    "**Interpretation:**",
                    item.get("Interpretation", "Not available"),
                )

                causes = item.get("Possible Causes", [])
                st.write("**Possible causes:**")
                if isinstance(causes, list):
                    if causes:
                        for cause in causes:
                            st.markdown(f"- {cause}")
                    else:
                        st.write(
                            "No cause list is available. This does not mean "
                            "the result has no possible causes."
                        )
                else:
                    st.write(causes or "Not available")

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
            "Check ai_explainer.py and the extracted results."
        )

    section("Important notes")
    notes = insights.get("general_notes", [])

    if notes:
        for note in notes:
            st.markdown(f"- {note}")
    else:
        st.markdown(
            "- Verify extracted values against the original report.\n"
            "- Reference ranges vary between laboratories.\n"
            "- Discuss uncertain results with a healthcare professional."
        )

    st.warning(
        "Do not use these explanations alone to diagnose a condition "
        "or change medication."
    )
else:
    st.info(
        "Select 'Generate clinical insights' to display the explanations."
    )


# =========================================================
# VERIFY SOURCE TEXT
# =========================================================

with st.expander("Verify extracted source text"):
    st.write(
        "Compare extracted text against the original report to identify "
        "OCR errors, missing values, units, or reference ranges."
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
    "06  Export report",
    "Create a downloadable PDF copy of the analysis.",
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
        "Download MediLens report",
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
    MediLens provides educational support for understanding medical reports.
    Extracted values and explanations can be incomplete or inaccurate and
    do not constitute a confirmed diagnosis. Consult a qualified healthcare
    professional for interpretation and treatment decisions.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;color:#8FA5BC;font-size:11px;padding:24px;">
    ✚ MEDILENS · MEDICAL REPORT INTELLIGENCE
</div>
""", unsafe_allow_html=True)
