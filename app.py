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
.stApp { background:#f4f8fc; }
.block-container { max-width:1100px; padding-top:1.5rem; }

[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display:none; }

.hero {
    background:linear-gradient(135deg,#0d3b66,#1683c4);
    padding:30px;
    border-radius:22px;
    margin-bottom:25px;
    box-shadow:0 8px 25px rgba(13,59,102,.18);
}
.hero-title {
    color:white !important;
    font-size:34px;
    font-weight:800;
}
.hero-subtitle {
    color:#eaf6ff !important;
    font-size:16px;
    line-height:1.6;
    margin-top:8px;
}
.badge {
    display:inline-block;
    color:white !important;
    background:rgba(255,255,255,.15);
    border:1px solid rgba(255,255,255,.2);
    border-radius:20px;
    padding:6px 11px;
    margin:15px 6px 0 0;
    font-size:12px;
}
.section-title {
    color:#123b63;
    font-size:24px;
    font-weight:800;
    margin:28px 0 12px;
}
.section-text {
    color:#718294;
    font-size:14px;
    margin-bottom:15px;
}
.step {
    background:white;
    border:1px solid #e0e9f1;
    border-radius:17px;
    padding:18px 12px;
    min-height:155px;
    text-align:center;
    box-shadow:0 4px 15px rgba(24,63,95,.06);
}
.step-number {
    width:38px;
    height:38px;
    margin:auto;
    border-radius:50%;
    background:#e8f3fb;
    color:#1261a0;
    font-weight:800;
    display:flex;
    align-items:center;
    justify-content:center;
}
.step-icon { font-size:25px; margin-top:7px; }
.step-title { color:#123b63; font-weight:750; margin-top:5px; }
.step-text { color:#718294; font-size:12px; line-height:1.5; margin-top:5px; }

.upload-card,.card {
    background:white;
    border:1px solid #dce7f0;
    border-radius:17px;
    padding:20px;
    box-shadow:0 4px 15px rgba(24,63,95,.06);
}
.upload-title,.card-title {
    color:#123b63;
    font-size:18px;
    font-weight:750;
}
.upload-text,.card-text {
    color:#687b8d;
    font-size:14px;
    line-height:1.7;
    margin-top:5px;
}
[data-testid="stFileUploader"] {
    background:#f9fcff !important;
    border:2px dashed #8dbbd8 !important;
    border-radius:15px !important;
}
.stButton > button {
    width:100%;
    min-height:48px;
    border:0;
    border-radius:11px;
    background:linear-gradient(135deg,#1261a0,#1683c4);
    color:white !important;
    font-weight:750;
}
.metric {
    background:white;
    border:1px solid #e0e8f0;
    border-radius:16px;
    padding:17px 8px;
    text-align:center;
    box-shadow:0 4px 15px rgba(24,63,95,.06);
}
.metric-icon { font-size:22px; }
.metric-label { color:#718294; font-size:12px; margin-top:4px; }
.metric-value { font-size:28px; font-weight:800; }
.blue { color:#1261a0; }
.green { color:#159447; }
.orange { color:#df8700; }
.red { color:#d53d3d; }
.ai-card { border-left:5px solid #1261a0; }
.summary-card { border-left:5px solid #1683c4; }
.download-card { background:#edf7ff; border-color:#cce7f8; }
.disclaimer {
    background:#fff8e8;
    border-left:5px solid #e6a21a;
    border-radius:13px;
    padding:18px;
    margin-top:25px;
    color:#69531e;
    line-height:1.7;
}
.footer {
    text-align:center;
    color:#7a8b9b;
    font-size:12px;
    padding:25px 0;
}
@media(max-width:700px) {
    .block-container { padding-left:1rem; padding-right:1rem; }
    .hero { padding:23px 19px; }
    .hero-title { font-size:27px; }
    .section-title { font-size:21px; }
    .step { min-height:auto; margin-bottom:10px; }
    .metric { margin-bottom:10px; }
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="hero">
    <div class="hero-title">🩺 AI Medical Report Explainer</div>
    <div class="hero-subtitle">
        Understand laboratory reports with clear, simple and educational AI explanations.
    </div>
    <span class="badge">🔒 Privacy Focused</span>
    <span class="badge">🤖 AI Assisted</span>
    <span class="badge">📊 Easy to Understand</span>
</div>
""", unsafe_allow_html=True)

# How it works
st.markdown('<div class="section-title">📋 How It Works</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-text">Four simple steps from report upload to educational explanation.</div>',
    unsafe_allow_html=True
)

steps = [
    ("1", "📄", "Upload Report", "Upload a PDF or image."),
    ("2", "🔎", "Extract Text", "Read report text or use OCR."),
    ("3", "🧪", "Analyze Results", "Identify laboratory values."),
    ("4", "🤖", "AI Explanation", "Get an educational explanation.")
]

cols = st.columns(4)
for col, step in zip(cols, steps):
    number, icon, title, description = step
    with col:
        st.markdown(
            f"""
<div class="step">
    <div class="step-number">{number}</div>
    <div class="step-icon">{icon}</div>
    <div class="step-title">{title}</div>
    <div class="step-text">{description}</div>
</div>
""",
            unsafe_allow_html=True
        )

# Upload
st.markdown('<div class="section-title">📄 Upload Medical Report</div>', unsafe_allow_html=True)
st.markdown(
    """
<div class="upload-card">
    <div class="upload-title">Choose your report</div>
    <div class="upload-text">
        Supported formats: PDF, JPG, JPEG and PNG.
        For OCR, use a clear and readable image.
    </div>
</div>
""",
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Choose a PDF or image file",
    type=["pdf", "jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

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
                st.info("This PDF may be scanned or image-based. Try uploading the report as JPG or PNG.")
            else:
                st.info("Try a clearer image with readable text.")
        else:
            st.markdown('<div class="section-title">📋 Extracted Report</div>', unsafe_allow_html=True)

            with st.expander("View extracted report text"):
                st.text_area(
                    "Extracted text",
                    extracted_text,
                    height=300,
                    label_visibility="collapsed"
                )

            analyze_clicked = st.button(
                "🔍 Analyze Medical Report",
                use_container_width=True
            )

            if analyze_clicked:
                with st.spinner("🔬 Analyzing laboratory results..."):
                    results = analyze_report(extracted_text)

                if results.empty:
                    st.warning("⚠️ No laboratory test results were detected.")
                    st.info(
                        "The report text was extracted, but laboratory values could not be identified. "
                        "Check the extracted text or try a clearer report."
                    )
                else:
                    total = len(results)
                    within = len(results[results["Status"] == "Within Range"])
                    below = len(results[results["Status"] == "Below Range"])
                    above = len(results[results["Status"] == "Above Range"])

                    st.markdown(
                        '<div class="section-title">📊 Laboratory Results Dashboard</div>',
                        unsafe_allow_html=True
                    )

                    metrics = [
                        ("🧪", "Total Tests", total, "blue"),
                        ("🟢", "Within Range", within, "green"),
                        ("🟠", "Below Range", below, "orange"),
                        ("🔴", "Above Range", above, "red")
                    ]

                    metric_cols = st.columns(4)
                    for col, metric in zip(metric_cols, metrics):
                        icon, label, value, color = metric
                        with col:
                            st.markdown(
                                f"""
<div class="metric">
    <div class="metric-icon">{icon}</div>
    <div class="metric-label">{label}</div>
    <div class="metric-value {color}">{value}</div>
</div>
""",
                                unsafe_allow_html=True
                            )

                    st.markdown(
                        '<div class="section-title">🧪 Detailed Laboratory Results</div>',
                        unsafe_allow_html=True
                    )
                    st.dataframe(
                        results,
                        use_container_width=True,
                        hide_index=True
                    )

                    summary = f"The report contains {total} laboratory test(s). "
                    if within:
                        summary += f"{within} result(s) are within the reference range shown on the report. "
                    if below:
                        summary += f"{below} result(s) are below the reference range shown on the report. "
                    if above:
                        summary += f"{above} result(s) are above the reference range shown on the report."

                    st.markdown(
                        '<div class="section-title">📌 Result Summary</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"""
<div class="card summary-card">
    <div class="card-title">Analysis Overview</div>
    <div class="card-text">{summary}</div>
</div>
""",
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        '<div class="section-title">🤖 AI Educational Explanation</div>',
                        unsafe_allow_html=True
                    )

                    with st.spinner("🤖 Preparing educational explanation..."):
                        ai_summary = ai_explain_report(extracted_text)

                    safe_ai = (
                        ai_summary
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace("\n", "<br>")
                    )

                    st.markdown(
                        f"""
<div class="card ai-card">
    {safe_ai}
</div>
""",
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        '<div class="section-title">📥 Download Report</div>',
                        unsafe_allow_html=True
                    )

                    try:
                        pdf_report = generate_report(results, ai_summary)

                        st.markdown(
                            """
<div class="card download-card">
    <div class="card-title">📄 Your report is ready</div>
    <div class="card-text">
        Download the laboratory results and educational explanation as a PDF.
    </div>
</div>
""",
                            unsafe_allow_html=True
                        )

                        st.download_button(
                            "📥 Download PDF Report",
                            data=pdf_report,
                            file_name="medical_report_explanation.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as error:
                        st.error(f"❌ Could not generate PDF: {error}")

                    st.markdown(
                        """
<div class="disclaimer">
    <b>⚠️ Important Medical Disclaimer</b>
    <br><br>
    This application provides informational and educational explanations only.
    It does not provide a medical diagnosis or treatment.
    <br><br>
    Laboratory results should be interpreted by a qualified healthcare professional
    together with symptoms, medical history, medications and other clinical information.
    <br><br>
    Reference ranges may vary between laboratories, and OCR or extracted text can sometimes contain errors.
</div>
""",
                        unsafe_allow_html=True
                    )

    except Exception as error:
        st.error("❌ Could not process the uploaded file.")
        st.code(str(error))

# Footer
st.markdown(
    """
<div class="footer">
    🩺 AI Medical Report Explainer
    <br>
    Educational Use Only • Not a Substitute for Professional Medical Evaluation
</div>
""",
    unsafe_allow_html=True
                    )

