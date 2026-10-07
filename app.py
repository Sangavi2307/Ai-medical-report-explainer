import streamlit as st
from extractor import extract_text_from_pdf
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from ocr_service import extract_text_from_image
from report_generator import generate_report

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f5f8fc;
}

.block-container {
    max-width: 1180px;
    padding: 28px 28px 45px;
}

[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none;
}

/* HERO */
.hero {
    background: linear-gradient(135deg, #0b3b66, #116aa7, #168dca);
    border-radius: 26px;
    padding: 34px 38px;
    margin-bottom: 28px;
    box-shadow: 0 14px 40px rgba(11,59,102,.18);
}

.hero-kicker {
    color: #bde9ff !important;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.hero-title {
    color: white !important;
    font-size: 34px;
    font-weight: 800;
    margin-top: 8px;
}

.hero-subtitle {
    color: #e9f6ff !important;
    font-size: 15px;
    line-height: 1.7;
    max-width: 760px;
    margin-top: 10px;
}

.badge {
    display: inline-block;
    padding: 7px 12px;
    margin: 16px 6px 0 0;
    border-radius: 30px;
    color: white !important;
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.2);
    font-size: 11px;
    font-weight: 600;
}

/* SECTIONS */
.section {
    margin-top: 30px;
    margin-bottom: 13px;
}

.section-title {
    color: #103c63;
    font-size: 22px;
    font-weight: 800;
}

.section-subtitle {
    color: #74879a;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 3px;
}

/* STEPS */
.step-card {
    background: white;
    border: 1px solid #e0e9f1;
    border-radius: 18px;
    padding: 18px 14px;
    min-height: 145px;
    text-align: center;
    box-shadow: 0 5px 18px rgba(20,60,90,.05);
}

.step-circle {
    width: 38px;
    height: 38px;
    margin: auto;
    border-radius: 50%;
    background: #e9f5fc;
    color: #116aa7;
    font-size: 14px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
}

.step-icon {
    font-size: 23px;
    margin-top: 8px;
}

.step-title {
    color: #173f62;
    font-size: 14px;
    font-weight: 700;
    margin-top: 5px;
}

.step-text {
    color: #788b9d;
    font-size: 11px;
    line-height: 1.5;
    margin-top: 4px;
}

/* UPLOAD */
.upload-card {
    background: white;
    border: 1px solid #dce7f0;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 7px 22px rgba(20,60,90,.06);
}

.upload-heading {
    color: #123e63;
    font-size: 18px;
    font-weight: 700;
}

.upload-description {
    color: #728699;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 5px;
}

[data-testid="stFileUploader"] {
    background: #f9fcff !important;
    border: 2px dashed #91bfd9 !important;
    border-radius: 16px !important;
}

/* BUTTON */
.stButton > button {
    width: 100%;
    min-height: 48px;
    border: 0;
    border-radius: 12px;
    background: linear-gradient(135deg, #116aa7, #168dca);
    color: white !important;
    font-weight: 700;
}

/* CARDS */
.info-card {
    background: white;
    border: 1px solid #dfe8ef;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 5px 18px rgba(20,60,90,.05);
}

.card-blue {
    border-left: 5px solid #168dca;
}

.card-green {
    border-left: 5px solid #18a15a;
}

.card-orange {
    border-left: 5px solid #e3a41a;
}

.card-heading {
    color: #153f62;
    font-size: 16px;
    font-weight: 750;
}

.card-body {
    color: #718496;
    font-size: 13px;
    line-height: 1.7;
    margin-top: 5px;
}

/* METRICS */
.metric-card {
    background: white;
    border: 1px solid #dfe8ef;
    border-radius: 17px;
    padding: 16px 10px;
    text-align: center;
    box-shadow: 0 5px 18px rgba(20,60,90,.05);
}

.metric-icon {
    font-size: 20px;
}

.metric-label {
    color: #77899a;
    font-size: 11px;
}

.metric-value {
    font-size: 27px;
    font-weight: 800;
    margin-top: 2px;
}

.blue { color: #116aa7; }
.green { color: #159557; }
.orange { color: #d88b08; }
.red { color: #d44242; }

/* RESULT CARD */
.result-card {
    background: white;
    border: 1px solid #dfe8ef;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 5px 18px rgba(20,60,90,.05);
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.test-name {
    color: #123e63;
    font-size: 17px;
    font-weight: 800;
}

.test-type {
    color: #8292a0;
    font-size: 11px;
    margin-top: 3px;
}

.status-pill {
    padding: 7px 12px;
    border-radius: 20px;
    background: #f3f7fa;
    font-size: 12px;
    font-weight: 700;
}

.result-line {
    border: 0;
    border-top: 1px solid #e8eef3;
    margin: 15px 0;
}

.result-label {
    color: #8292a0;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .5px;
}

.result-value {
    color: #123e63;
    font-size: 20px;
    font-weight: 800;
    margin-top: 5px;
}

.result-small {
    color: #7a8c9d;
    font-size: 11px;
    margin-top: 2px;
}

.result-range {
    color: #123e63;
    font-size: 15px;
    font-weight: 700;
    margin-top: 8px;
}

/* DISCLAIMER */
.disclaimer {
    background: #fff9e9;
    border: 1px solid #f1dfaa;
    border-left: 5px solid #e3a41a;
    border-radius: 15px;
    padding: 18px 20px;
    color: #6b5725;
    font-size: 12px;
    line-height: 1.7;
    margin-top: 25px;
}

.disclaimer-title {
    color: #795c17;
    font-size: 14px;
    font-weight: 800;
}

/* FOOTER */
.footer {
    text-align: center;
    color: #8393a1;
    font-size: 11px;
    line-height: 1.7;
    padding: 30px 0 5px;
}

/* MOBILE */
@media (max-width: 700px) {
    .block-container {
        padding: 18px 14px 35px;
    }

    .hero {
        padding: 25px 21px;
        border-radius: 21px;
    }

    .hero-title {
        font-size: 27px;
    }

    .hero-subtitle {
        font-size: 13px;
    }

    .section-title {
        font-size: 20px;
    }

    .step-card {
        margin-bottom: 10px;
        min-height: 0;
    }

    .metric-card {
        margin-bottom: 9px;
    }

    .result-card {
        padding: 16px;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================
# HERO
# =========================
st.markdown("""
<div class="hero">
    <div class="hero-kicker">SMART • SIMPLE • EDUCATIONAL</div>

    <div class="hero-title">
        🩺 AI Medical Report Explainer
    </div>

    <div class="hero-subtitle">
        Upload a laboratory report and understand the reported
        test values through clear, simple and educational AI explanations.
    </div>

    <span class="badge">🔒 Privacy Focused</span>
    <span class="badge">🤖 AI Assisted</span>
    <span class="badge">📊 Easy to Understand</span>
    <span class="badge">📄 PDF Export</span>
</div>
""", unsafe_allow_html=True)


# =========================
# HOW IT WORKS
# =========================
st.markdown("""
<div class="section">
    <div class="section-title">📋 How It Works</div>
    <div class="section-subtitle">
        Four simple steps from report upload to educational explanation.
    </div>
</div>
""", unsafe_allow_html=True)

steps = [
    ("1", "📄", "Upload Report", "Choose a PDF or clear report image."),
    ("2", "🔎", "Extract Text", "Read text directly or use OCR."),
    ("3", "🧪", "Analyze Results", "Identify test values and ranges."),
    ("4", "🤖", "Explain Results", "Generate a simple AI explanation.")
]

step_cols = st.columns(4)

for col, step in zip(step_cols, steps):
    number, icon, title, description = step

    with col:
        st.markdown(
            f"""
<div class="step-card">
    <div class="step-circle">{number}</div>
    <div class="step-icon">{icon}</div>
    <div class="step-title">{title}</div>
    <div class="step-text">{description}</div>
</div>
""",
            unsafe_allow_html=True
        )


# =========================
# UPLOAD
# =========================
st.markdown("""
<div class="section">
    <div class="section-title">📄 Upload Medical Report</div>
    <div class="section-subtitle">
        Supported formats: PDF, JPG, JPEG and PNG.
        Use a clear and readable image for better OCR results.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="upload-card">
    <div class="upload-heading">Choose your report</div>
    <div class="upload-description">
        Upload a laboratory report. Scanned documents and images
        are processed using OCR.
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a PDF or image file",
    type=["pdf", "jpg", "jpeg", "png"],
    label_visibility="collapsed"
)


# =========================
# FILE PROCESSING
# =========================
if uploaded_file is not None:

    st.success(
        f"✅ File uploaded successfully: {uploaded_file.name}"
    )

    file_name = uploaded_file.name.lower()

    try:

        if file_name.endswith(".pdf"):

            with st.spinner("📄 Reading your PDF report..."):
                extracted_text = extract_text_from_pdf(
                    uploaded_file
                )

        else:

            with st.spinner("🔎 Reading text from your image..."):
                extracted_text = extract_text_from_image(
                    uploaded_file
                )

        # =========================
        # TEXT CHECK
        # =========================
        if not extracted_text or not extracted_text.strip():

            st.error(
                "❌ No readable text was found in this file."
            )

            if file_name.endswith(".pdf"):

                st.info(
                    "This PDF may be scanned or image-based. "
                    "Try uploading the report as JPG or PNG."
                )

            else:

                st.info(
                    "Try a clearer image with readable text."
                )

        else:

            # =========================
            # EXTRACTED TEXT
            # =========================
            st.markdown("""
<div class="section">
    <div class="section-title">📋 Extracted Report</div>
    <div class="section-subtitle">
        Review the text detected from your uploaded document.
    </div>
</div>
""", unsafe_allow_html=True)

            with st.expander(
                "👁️ View extracted report text"
            ):

                st.text_area(
                    "Extracted text",
                    extracted_text,
                    height=300,
                    label_visibility="collapsed"
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # =========================
            # ANALYZE BUTTON
            # =========================
            analyze_clicked = st.button(
                "🔍 Analyze Medical Report",
                use_container_width=True
            )

            if analyze_clicked:

                # =========================
                # ANALYZE
                # =========================
                with st.spinner(
                    "🔬 Analyzing laboratory results..."
                ):

                    results = analyze_report(
                        extracted_text
                    )

                # =========================
                # NO RESULTS
                # =========================
                if results.empty:

                    st.warning(
                        "⚠️ No laboratory test results were detected."
                    )

                    st.markdown("""
<div class="info-card card-orange">
    <div class="card-heading">
        Why might this happen?
    </div>

    <div class="card-body">
        The report text was extracted, but laboratory
        values could not be identified in the expected format.
        Check the extracted text or try a clearer report.
    </div>
</div>
""", unsafe_allow_html=True)

                else:

                    # =========================
                    # COUNTS
                    # =========================
                    total = len(results)

                    within = len(
                        results[
                            results["Status"] == "Within Range"
                        ]
                    )

                    below = len(
                        results[
                            results["Status"] == "Below Range"
                        ]
                    )

                    above = len(
                        results[
                            results["Status"] == "Above Range"
                        ]
                    )

                    # =========================
                    # DASHBOARD
                    # =========================
                    st.markdown("""
<div class="section">
    <div class="section-title">
        📊 Laboratory Results Dashboard
    </div>

    <div class="section-subtitle">
        Quick overview of the laboratory values detected
        from the uploaded report.
    </div>
</div>
""", unsafe_allow_html=True)

                    metrics = [
                        ("🧪", "Total Tests", total, "blue"),
                        ("🟢", "Within Range", within, "green"),
                        ("🟠", "Below Range", below, "orange"),
                        ("🔴", "Above Range", above, "red")
                    ]

                    metric_cols = st.columns(4)

                    for col, metric in zip(
                        metric_cols,
                        metrics
                    ):

                        icon, label, value, color = metric

                        with col:

                            st.markdown(
                                f"""
<div class="metric-card">

    <div class="metric-icon">
        {icon}
    </div>

    <div class="metric-label">
        {label}
    </div>

    <div class="metric-value {color}">
        {value}
    </div>

</div>
""",
                                unsafe_allow_html=True
                            )

                    # =========================
                    # PROFESSIONAL RESULT CARDS
                    # =========================
                    st.markdown("""
<div class="section">
    <div class="section-title">
        🧪 Detailed Laboratory Results
    </div>

    <div class="section-subtitle">
        Individual test results extracted from the report.
    </div>
</div>
""", unsafe_allow_html=True)

                    for _, row in results.iterrows():

                        test_name = str(row["Test"])
                        result_value = str(row["Result"])
                        unit = str(row["Unit"])
                        reference_range = str(
                            row["Reference Range"]
                        )
                        status = str(row["Status"])

                        if status == "Within Range":

                            status_icon = "🟢"
                            status_color = "green"

                        elif status == "Below Range":

                            status_icon = "🟠"
                            status_color = "orange"

                        elif status == "Above Range":

                            status_icon = "🔴"
                            status_color = "red"

                        else:

                            status_icon = "⚪"
                            status_color = "blue"

                        st.markdown(
                            f"""
<div class="result-card">

    <div class="result-header">

        <div>
            <div class="test-name">
                🧪 {test_name}
            </div>

            <div class="test-type">
                Laboratory Test
            </div>
        </div>

        <div class="status-pill">
            <span class="{status_color}">
                {status_icon} {status}
            </span>
        </div>

    </div>

    <hr class="result-line">

    <div style="
        display:grid;
        grid-template-columns:
        repeat(3, minmax(0, 1fr));
        gap:16px;
    ">

        <div>

            <div class="result-label">
                RESULT
            </div>

            <div class="result-value">
                {result_value}
            </div>

            <div class="result-small">
                {unit}
            </div>

        </div>

        <div>

            <div class="result-label">
                REFERENCE RANGE
            </div>

            <div class="result-range">
                {reference_range}
            </div>

        </div>

        <div>

            <div class="result-label">
                STATUS
            </div>

            <div class="result-range {status_color}">
                {status_icon} {status}
            </div>

        </div>

    </div>

</div>
""",
                            unsafe_allow_html=True
                        )

                    # =========================
                    # TABLE
                    # =========================
                    with st.expander(
                        "📋 View results as a table"
                    ):

                        st.dataframe(
                            results,
                            use_container_width=True,
                            hide_index=True
                        )

                    # =========================
                    # SUMMARY
                    # =========================
                    summary = (
                        f"The report contains {total} "
                        f"laboratory test(s). "
                    )

                    if within:

                        summary += (
                            f"{within} result(s) are within "
                            "the reference range shown on "
                            "the report. "
                        )

                    if below:

                        summary += (
                            f"{below} result(s) are below "
                            "the reference range shown on "
                            "the report. "
                        )

                    if above:

                        summary += (
                            f"{above} result(s) are above "
                            "the reference range shown on "
                            "the report."
                        )

                    st.markdown("""
<div class="section">
    <div class="section-title">
        📌 Result Summary
    </div>

    <div class="section-subtitle">
        A simple overview of the detected laboratory results.
    </div>
</div>
""", unsafe_allow_html=True)

                    st.markdown(
                        f"""
<div class="info-card card-blue">

    <div class="card-heading">
        Analysis Overview
    </div>

    <div class="card-body">
        {summary}
    </div>

</div>
""",
                        unsafe_allow_html=True
                    )

                    # =========================
                    # AI EXPLANATION
                    # =========================
                    st.markdown("""
<div class="section">
    <div class="section-title">
        🤖 AI Educational Explanation
    </div>

    <div class="section-subtitle">
        General educational information based only on
        the extracted report text.
    </div>
</div>
""", unsafe_allow_html=True)

                    with st.spinner(
                        "🤖 Preparing educational explanation..."
                    ):
