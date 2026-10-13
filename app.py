
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from extractor import extract_text_from_pdf
from analyzer import analyze_report
from report_generator import create_pdf_report
import io

st.set_page_config(
    page_title="MediLens | Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- PROFESSIONAL UI ----------------

st.markdown("""
<style>
.block-container {
    max-width: 1440px;
    padding-top: 1.5rem;
}
[data-testid="stAppViewContainer"] {
    background: #f6f8fb;
}
[data-testid="stSidebar"] {
    background: #ffffff;
}
.hero {
    padding: 28px;
    border-radius: 18px;
    color: white;
    background: linear-gradient(115deg, #12304a, #176b87, #2b8d9c);
    margin-bottom: 24px;
}
.hero h1 {
    color: white;
    font-size: 2rem;
}
.hero p {
    color: #e5f3f8;
}
.metric-card {
    background: white;
    border: 1px solid #e4eaf2;
    border-radius: 14px;
    padding: 18px;
    min-height: 100px;
}
.metric-label {
    color: #64748b;
    font-size: 14px;
}
.metric-value {
    color: #14243a;
    font-size: 30px;
    font-weight: 750;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("## 🩺 MediLens")
    st.caption("Medical Report Education Dashboard")

    page = st.radio(
        "Navigation",
        ["Dashboard", "How It Works", "Privacy & Safety"]
    )

    st.divider()
    st.markdown("**Supported format:** PDF only")
    st.caption("Always verify extracted values against the original report.")

if page == "How It Works":
    st.title("How MediLens works")
    st.markdown("""
    1. Upload a medical report in PDF format.
    2. Extract readable text from the PDF.
    3. Detect supported laboratory test results.
    4. Review the dashboard and graph.
    5. Download the extracted results or summary report.

    This is a rule-based prototype. It may not recognize every laboratory format.
    """)
    st.stop()

if page == "Privacy & Safety":
    st.title("Privacy & Safety")
    st.markdown("""
    - Upload only reports you are authorized to use.
    - Verify every result against the original PDF.
    - A status of **Not assessed** means the app could not safely determine a status.
    - This application does not diagnose conditions or recommend treatment.
    - Consult a qualified healthcare professional for medical interpretation.
    """)
    st.stop()

# ---------------- MAIN DASHBOARD ----------------

st.markdown("""
<div class="hero">
    <h1>Medical Report Explainer</h1>
    <p>Upload a PDF laboratory report to review detected results and download a summary.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("📄 Upload Medical Report")
    uploaded_pdf = st.file_uploader(
        "Choose your PDF report",
        type=["pdf"],
        accept_multiple_files=False
    )

with col2:
    st.subheader("Before uploading")
    st.info(
        "For best results, use a clear PDF containing selectable text. "
        "Scanned PDFs require OCR support."
    )

if uploaded_pdf is None:
    st.info("Upload a PDF to display your dashboard.")
    st.stop()

if uploaded_pdf.size > 15 * 1024 * 1024:
    st.error("File exceeds 15 MB. Please upload a smaller PDF.")
    st.stop()

# ---------------- EXTRACT PDF TEXT ----------------

try:
    with st.spinner("Reading your PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_pdf)
except Exception as error:
    st.error(f"Could not read the PDF: {error}")
    st.stop()

if not extracted_text.strip():
    st.error("No readable text was found in this PDF.")
    st.warning(
        "If this is a scanned PDF, OCR support must be added before "
        "the app can read it."
    )
    st.stop()

with st.expander("🔍 Review Extracted Text"):
    st.text_area(
        "Extracted text — verify against your original PDF",
        extracted_text,
        height=220
    )

# ---------------- ANALYZE RESULTS ----------------

try:
    results = analyze_report(extracted_text)
except Exception as error:
    st.error(f"Could not analyze the extracted text: {error}")
    st.stop()

if results.empty:
    st.warning("No supported laboratory results were recognized.")
    st.info(
        "The PDF text was extracted, but the analyzer may not recognize "
        "this report's layout. Review the extracted text above."
    )

    st.download_button(
        "⬇️ Download Extracted Text",
        data=extracted_text.encode("utf-8"),
        file_name="extracted_medical_report.txt",
        mime="text/plain"
    )
    st.stop()

# ---------------- DASHBOARD METRICS ----------------

status = results["Status"].fillna("Not assessed")

total = len(results)
assessed = int(
    status.isin(
        ["Within range", "Below range", "Above range"]
    ).sum()
)
below = int((status == "Below range").sum())
above = int((status == "Above range").sum())
not_assessed = int((status == "Not assessed").sum())

st.divider()
st.subheader("📊 Results Overview")

m1, m2, m3, m4 = st.columns(4)

metrics = [
    (m1, "Detected Results", total),
    (m2, "Assessed Results", assessed),
    (m3, "Below Range", below),
    (m4, "Above Range", above),
]

for column, label, value in metrics:
    with column:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

if not_assessed:
    st.caption(
        f"{not_assessed} result(s) could not be assessed reliably."
    )

# ---------------- RESULTS TABLE ----------------

st.divider()
tab1, tab2, tab3 = st.tabs(
    ["📋 Results", "📈 Dashboard Graph", "⬇️ Downloads"]
)

with tab1:
    st.subheader("Detected Laboratory Results")
    st.dataframe(
        results,
        use_container_width=True,
        hide_index=True
    )
    st.caption(
        "Automated extraction may be inaccurate. Verify test names, "
        "values, units, and reference ranges against the original PDF."
    )

# ---------------- GRAPH ----------------

chart_png = None

with tab2:
    st.subheader("Laboratory Result Status")

    status_counts = status.value_counts().reindex(
        [
            "Within range",
            "Below range",
            "Above range",
            "Not assessed"
        ],
        fill_value=0
    )

    fig, ax = plt.subplots(figsize=(9, 4))

    bars = ax.bar(
        status_counts.index,
        status_counts.values
    )

    ax.set_ylabel("Number of Results")
    ax.set_title("Distribution of Detected Result Statuses")
    ax.grid(axis="y", alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.bar_label(bars, padding=3)

    plt.xticks(rotation=10)
    fig.tight_layout()

    st.pyplot(fig, use_container_width=True)

    buffer = io.BytesIO()
    fig.savefig(
        buffer,
        format="png",
        dpi=180,
        bbox_inches="tight"
    )
    chart_png = buffer.getvalue()
    plt.close(fig)

    st.download_button(
        "⬇️ Download Graph (PNG)",
        data=chart_png,
        file_name="lab_result_status_graph.png",
        mime="image/png"
    )

    st.caption(
        "This graph compares result-status counts, not the numeric values "
        "of different tests, which may use different units."
    )

# ---------------- DOWNLOADS ----------------

with tab3:
    st.subheader("Download Your Results")

    csv_data = results.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "⬇️ Download Results (CSV)",
        data=csv_data,
        file_name="medical_report_results.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.download_button(
        "⬇️ Download Extracted Text (TXT)",
        data=extracted_text.encode("utf-8"),
        file_name="extracted_medical_report.txt",
        mime="text/plain",
        use_container_width=True
    )

    try:
        pdf_data = create_pdf_report(
            results=results,
            extracted_text=extracted_text,
            chart_png=chart_png,
            generated_at=datetime.now().strftime(
                "%d %b %Y, %I:%M %p"
            )
        )

        st.download_button(
            "⬇️ Download Summary Report (PDF)",
            data=pdf_data,
            file_name="medical_report_summary.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

    except Exception as error:
        st.error(f"PDF report generation failed: {error}")

# ---------------- DISCLAIMER ----------------

st.divider()
st.warning(
    "Educational use only. This application does not diagnose, treat, "
    "or replace advice from a qualified healthcare professional."
)
