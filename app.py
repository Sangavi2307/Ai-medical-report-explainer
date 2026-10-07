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
    initial_sidebar_state="collapsed",
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

/* ---------- HERO ---------- */
.hero {
    background: linear-gradient(135deg, #0b3b66 0%, #116aa7 55%, #168dca 100%);
    border-radius: 26px;
    padding: 34px 38px;
    color: white;
    box-shadow: 0 14px 40px rgba(11,59,102,.18);
    margin-bottom: 26px;
    position: relative;
    overflow: hidden;
}

.hero:after {
    content: "✚";
    position: absolute;
    right: 35px;
    top: 12px;
    font-size: 120px;
    font-weight: 800;
    color: rgba(255,255,255,.06);
}

.hero-kicker {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #bde9ff !important;
    margin-bottom: 9px;
}

.hero-title {
    font-size: 34px;
    line-height: 1.15;
    font-weight: 800;
    color: #ffffff !important;
    margin: 0;
}

.hero-subtitle {
    max-width: 720px;
    color: #e9f6ff !important;
    font-size: 15px;
    line-height: 1.7;
    margin-top: 12px;
}

.badge-row {
    margin-top: 18px;
}

.badge {
    display: inline-block;
    padding: 7px 12px;
    margin: 0 7px 7px 0;
    border-radius: 30px;
    color: #ffffff !important;
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.2);
    font-size: 11px;
    font-weight: 600;
}

/* ---------- SECTION ---------- */
.section {
    margin-top: 30px;
    margin-bottom: 13px;
}

.section-title {
    color: #103c63;
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 3px;
}

.section-subtitle {
    color: #74879a;
    font-size: 13px;
    line-height: 1.6;
}

/* ---------- HOW IT WORKS ---------- */
.step-card {
    background: #ffffff;
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
    margin: 0 auto 8px;
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

/* ---------- UPLOAD ---------- */
.upload-card {
    background: #ffffff;
    border: 1px solid #dce7f0;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 7px 22px rgba(20,60,90,.06);
}

.upload-heading {
    color: #123e63;
    font-size: 18px;
    font-weight: 750;
}

.upload-description {
    color: #728699;
    font-size: 13px;
    line-height: 1.6;
    margin: 5px 0 12px;
}

[data-testid="stFileUploader"] {
    background: #f9fcff !important;
    border: 2px dashed #91bfd9 !important;
    border-radius: 16px !important;
    padding: 5px !important;
}

[data-testid="stFileUploader"] section {
    padding: 12px !important;
}

/* ---------- BUTTON ---------- */
.stButton > button {
    width: 100%;
    min-height: 48px;
    border: 0;
    border-radius: 12px;
    background: linear-gradient(135deg, #116aa7, #168dca);
    color: #ffffff !important;
    font-weight: 700;
    box-shadow: 0 6px 18px rgba(17,106,167,.18);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #0d5b91, #1179ad);
    color: #ffffff !important;
}

/* ---------- CARDS ---------- */
.info-card {
    background: #ffffff;
    border: 1px solid #dfe8ef;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 5px 18px rgba(20,60,90,.05);
}

.info-card-blue {
    border-left: 5px solid #168dca;
}

.info-card-green {
    border-left: 5px solid #18a15a;
}

.info-card-orange {
    border-left: 5px solid #e6a21a;
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
    margin-top: 4px;
}

/* ---------- METRICS ---------- */
.metric-card {
    background: #ffffff;
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
    margin-top: 3px;
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

/* ---------- TABLE ---------- */
[data-testid="stDataFrame"] {
    border: 1px solid #dce7ef;
    border-radius: 14px;
    overflow: hidden;
}

/* ---------- DISCLAIMER ---------- */
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
    font-weight: 800;
    font-size: 14px;
}

/* ---------- FOOTER ---------- */
.footer {
    text-align: center;
    color: #8393a1;
    font-size: 11px;
    line-height: 1.7;
    padding: 30px 0 5px;
}

/* ---------- MOBILE ---------- */
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

    .upload-card,
    .info-card {
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
    <div class="hero-kicker">Smart • Simple • Educational</div>
    <div class="hero-title">🩺 AI Medical Report Explainer</div>
    <div class="hero-subtitle">
        Upload a laboratory report and understand the reported test values
        through clear, beginner-friendly educational explanations.
    </div>
    <div class="badge-row">
        <span class="badge">🔒 Privacy Focused</span>
        <span class="badge">🤖 AI Assisted</span>
        <span class="badge">📊 Easy to Understand</span>
        <span class="badge">📄 PDF Export</span>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================
# HOW IT WORKS
# =========================
st.markdown("""
<div class="section">
    <div class="section-title">📋 How It Works</div>
    <div class="section-subtitle">
        A simple four-step process from report upload to educational explanation.
    </div>
</div>
""", unsafe_allow_html=True)

steps = [
    ("1", "📄", "Upload Report", "Choose a PDF or clear report image."),
    ("2", "🔎", "Extract Text", "Read text directly or use OCR."),
    ("3", "🧪", "Analyze Results", "Identify test values and ranges."),
    ("4", "🤖", "Explain Results", "Generate a simple AI explanation."),
]

cols = st.columns(4)

for col, step in zip(cols, steps):
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
            unsafe_allow_html=True,
        )


# =========================
# UPLOAD
# =========================
st.markdown("""
<div class="section">
    <div class="section-title">📄 Upload Medical Report</div>
    <div class="section-subtitle">
        Supported formats: PDF, JPG, JPEG and PNG.
        Use a clear, readable image for better OCR results.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="upload-card">
    <div class="upload-heading">Choose your report</div>
    <div class="upload-description">
        Your file will be processed to extract laboratory information.
        Scanned documents and images may require OCR.
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose a PDF or image file",
    type=["pdf", "jpg", "jpeg", "png"],
    label_visibility="collapsed",
)


# =========================
# PROCESS FILE
# =========================
if uploaded_file is not None:

    st.success(f"✅ File uploaded successfully: {uploaded_file.name}")

    file_name = uploaded_file.name.lower()

    try:

        if file_name.endswith(".pdf"):
            with st.spinner("📄 Reading your PDF report..."):
                extracted_text = extract_text_from_pdf(uploaded_file)
        else:
            with st.spinner("🔎 Reading text from your image..."):
                extracted_text = extract_text_from_image(uploaded_file)

        if not extracted_text or not extracted_text.strip():

            st.error("❌ No readable text was found in this file.")

            if file_name.endswith(".pdf"):
                st.info(
                    "This PDF may be scanned or image-based. "
                    "Try uploading the report as JPG or PNG."
                )
            else:
                st.info(
                    "Try a clearer image with good lighting, "
                    "straight alignment and readable text."
                )

        else:

            # =========================
            # EXTRACTED TEXT
            # =========================
            st.markdown("""
<div class="section">
    <div class="section-title">📋 Extracted Report</div>
    <div class="section-subtitle">
        Review the text detected from your uploaded document before analysis.
    </div>
</div>
""", unsafe_allow_html=True)

            with st.expander("👁️ View extracted report text"):

                st.text_area(
                    "Extracted text",
                    extracted_text,
                    height=300,
                    label_visibility="collapsed",
                )

            st.markdown("<br>", unsafe_allow_html=True)

            analyze_clicked = st.button(
                "🔍 Analyze Medical Report",
                use_container_width=True,
            )

            if analyze_clicked:

                # =========================
                # ANALYSIS
                # =========================
                with st.spinner("🔬 Analyzing laboratory results..."):
                    results = analyze_report(extracted_text)

                if results.empty:

                    st.warning("⚠️ No laboratory test results were detected.")

                    st.markdown("""
<div class="info-card info-card-orange">
    <div class="card-heading">Why might this happen?</div>
    <div class="card-body">
        The report text was extracted, but the application could not
        identify laboratory test values in the expected format.
        Check the extracted text or try uploading a clearer report.
    </div>
</div>
""", unsafe_allow_html=True)

                else:

                    # =========================
                    # METRICS
                    # =========================
                    total = len(results)
                    within = len(
                        results[results["Status"] == "Within Range"]
                    )
                    below = len(
                        results[results["Status"] == "Below Range"]
                    )
                    above = len(
                        results[results["Status"] == "Above Range"]
                    )

                    st.markdown("""
<div class="section">
    <div class="section-title">📊 Laboratory Results</div>
    <div class="section-subtitle">
        A quick overview of the laboratory values detected from the report.
    </div>
</div>
""", unsafe_allow_html=True)

                    metrics = [
                        ("🧪", "Total Tests", total, "blue"),
                        ("🟢", "Within Range", within, "green"),
                        ("🟠", "Below Range", below, "orange"),
                        ("🔴", "Above Range", above, "red"),
                    ]

                    metric_cols = st.columns(4)

                    for col, metric in zip(metric_cols, metrics):

                        icon, label, value, color = metric

                        with col:

                            st.markdown(
                                f"""
<div class="metric-card">
    <div class="metric-icon">{icon}</div>
    <div class="metric-label">{label}</div>
    <div class="metric-value {color}">{value}</div>
</div>
""",
                                unsafe_allow_html=True,
                            )

                    # =========================
                    # TABLE
                    # =========================
                    st.markdown("""
<div class="section">
    <div class="section-title">🧪 Detailed Results</div>
    <div class="section-subtitle">
        These values are extracted from the uploaded report.
    </div>
</div>
""", unsafe_allow_html=True)

                    st.dataframe(
                        results,
                        use_container_width=True,
                        hide_index=True,
                    )

                    # =========================
                    # SUMMARY
                    # =========================
                    summary = (
                        f"The report contains {total} laboratory test(s). "
                    )

                    if within:
                        summary += (
                            f"{within} result(s) are within the "
                            "reference range shown on the report. "
                        )

                    if below:
                        summary += (
                            f"{below} result(s) are below the "
                            "reference range shown on the report. "
                        )

                    if above:
                        summary += (
                            f"{above} result(s) are above the "
                            "reference range shown on the report."
                        )

                    st.markdown("""
<div class="section">
    <div class="section-title">📌 Result Summary</div>
    <div class="section-subtitle">
        A simple overview of the detected laboratory results.
    </div>
</div>
""", unsafe_allow_html=True)

                    st.markdown(
                        f"""
<div class="info-card info-card-blue">
    <div class="card-heading">Analysis Overview</div>
    <div class="card-body">{summary}</div>
</div>
""",
                        unsafe_allow_html=True,
                    )

                    # =========================
                    # AI EXPLANATION
                    # =========================
                    st.markdown("""
<div class="section">
    <div class="section-title">🤖 AI Educational Explanation</div>
    <div class="section-subtitle">
        General educational information based only on the extracted report text.
    </div>
</div>
""", unsafe_allow_html=True)

                    with st.spinner("🤖 Preparing educational explanation..."):
                        ai_summary = ai_explain_report(extracted_text)

                    safe_ai = (
                        str(ai_summary)
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace("\n", "<br>")
                    )

                    st.markdown(
                        f"""
<div class="info-card info-card-green">
    <div class="card-heading">🧠 Explanation</div>
    <div class="card-body">
        {safe_ai}
    </div>
</div>
""",
                        unsafe_allow_html=True,
                    )

                    # =========================
                    # DOWNLOAD
                    # =========================
                    st.markdown("""
<div class="section">
    <div class="section-title">📥 Download Your Report</div>
    <div class="section-subtitle">
        Save the detected results and educational explanation as a PDF.
    </div>
</div>
""", unsafe_allow_html=True)

                    try:

                        pdf_report = generate_report(
                            results,
                            ai_summary,
                        )

                        st.markdown("""
<div class="info-card info-card-blue">
    <div class="card-heading">📄 Report Ready</div>
    <div class="card-body">
        Your laboratory results and educational explanation
        have been prepared as a downloadable PDF.
    </div>
</div>
""", unsafe_allow_html=True)

                        st.download_button(
                            "📥 Download PDF Report",
                            data=pdf_report,
                            file_name="medical_report_explanation.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )

                    except Exception as error:

                        st.error(
                            f"❌ Could not generate the PDF: {error}"
                        )

                    # =========================
                    # DISCLAIMER
                    # =========================
                    st.markdown("""
<div class="disclaimer">
    <div class="disclaimer-title">
        ⚠️ Important Medical Disclaimer
    </div>
    <br>
    This application provides informational and educational explanations only.
    It does not provide a medical diagnosis or treatment.
    <br><br>
    Laboratory results should be interpreted by a qualified healthcare
    professional together with symptoms, medical history, medications and
    other relevant clinical information.
    <br><br>
    Reference ranges can vary between laboratories. OCR and extracted text
    can also contain errors, so always verify important values against the
    original report.
</div>
""", unsafe_allow_html=True)

    except Exception as error:

        st.error("❌ Could not process the uploaded file.")
        st.code(str(error))


# =========================
# FOOTER
# =========================
st.markdown("""
<div class="footer">
    🩺 <b>AI Medical Report Explainer</b>
    <br>
    Educational Use Only • Not a Substitute for Professional Medical Evaluation
</div>
""", unsafe_allow_html=True)
