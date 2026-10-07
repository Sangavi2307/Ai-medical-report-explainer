import streamlit as st
from extractor import extract_text_from_pdf
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from ocr_service import extract_text_from_image
from report_generator import generate_report

st.set_page_config(page_title="AI Medical Report Explainer", page_icon="🩺", layout="wide")

st.markdown("""
<style>
.stApp{background:#f5f8fc}
.block-container{max-width:1150px;padding:28px}
[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none}
.hero{background:linear-gradient(135deg,#0b3b66,#168dca);padding:32px;border-radius:24px;color:white;margin-bottom:25px}
.hero h1{color:white!important;font-size:34px;margin:5px 0}
.hero p{color:#e8f6ff!important;line-height:1.7}
.badge{display:inline-block;padding:6px 11px;margin:8px 5px 0 0;border-radius:20px;background:#ffffff1f;color:white;font-size:11px}
.section-title{color:#123e63;font-size:23px;font-weight:800;margin:28px 0 5px}
.section-subtitle{color:#75899a;font-size:13px;margin-bottom:14px}
.step,.card,.metric,.result{background:white;border:1px solid #dfe8ef;border-radius:17px;padding:18px;box-shadow:0 5px 18px #143c5910}
.step{text-align:center;min-height:135px}
.circle{width:36px;height:36px;border-radius:50%;background:#e8f4fb;color:#116aa7;font-weight:800;display:flex;align-items:center;justify-content:center;margin:auto}
.icon{font-size:23px;margin-top:7px}.step-title{color:#173f62;font-weight:700}.step-text{color:#788b9d;font-size:11px;margin-top:4px}
.upload{background:white;border:1px solid #dce7f0;border-radius:19px;padding:20px}
.metric{text-align:center}.metric-icon{font-size:21px}.metric-label{color:#77899a;font-size:11px}.metric-value{font-size:27px;font-weight:800}
.blue{color:#116aa7}.green{color:#159557}.orange{color:#d88b08}.red{color:#d44242}
.result{margin-bottom:13px}.result-head{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap}
.test{color:#123e63;font-size:17px;font-weight:800}.muted{color:#8292a0;font-size:11px}
.result hr{border:0;border-top:1px solid #e8eef3;margin:14px 0}
.label{color:#8292a0;font-size:10px;font-weight:700}.value{color:#123e63;font-size:20px;font-weight:800;margin-top:4px}.range{color:#123e63;font-size:14px;font-weight:700;margin-top:7px}
.disclaimer{background:#fff9e9;border:1px solid #f1dfaa;border-left:5px solid #e3a41a;border-radius:14px;padding:18px;color:#6b5725;font-size:12px;line-height:1.7;margin-top:25px}
.footer{text-align:center;color:#8393a1;font-size:11px;padding:28px}
.stButton>button{width:100%;min-height:48px;border:0;border-radius:11px;background:linear-gradient(135deg,#116aa7,#168dca);color:white!important;font-weight:700}
[data-testid="stFileUploader"]{background:#f9fcff;border:2px dashed #91bfd9;border-radius:15px}
@media(max-width:700px){.block-container{padding:15px}.hero{padding:24px 19px}.hero h1{font-size:27px}.step{margin-bottom:10px}.metric{margin-bottom:9px}.result{padding:15px}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<div style="font-size:12px;font-weight:700;letter-spacing:1.5px;color:#bde9ff">SMART • SIMPLE • EDUCATIONAL</div>
<h1>🩺 AI Medical Report Explainer</h1>
<p>Upload a laboratory report and understand the reported test values through clear, simple and educational AI explanations.</p>
<span class="badge">🔒 Privacy Focused</span>
<span class="badge">🤖 AI Assisted</span>
<span class="badge">📊 Easy to Understand</span>
<span class="badge">📄 PDF Export</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">📋 How It Works</div><div class="section-subtitle">Four simple steps from report upload to educational explanation.</div>', unsafe_allow_html=True)

steps = [
    ("1","📄","Upload Report","Choose a PDF or clear image."),
    ("2","🔎","Extract Text","Read text directly or use OCR."),
    ("3","🧪","Analyze Results","Identify values and ranges."),
    ("4","🤖","Explain Results","Generate an educational explanation.")
]
cols = st.columns(4)
for col, item in zip(cols, steps):
    n, icon, title, desc = item
    with col:
        st.markdown(f'<div class="step"><div class="circle">{n}</div><div class="icon">{icon}</div><div class="step-title">{title}</div><div class="step-text">{desc}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">📄 Upload Medical Report</div><div class="section-subtitle">Supported formats: PDF, JPG, JPEG and PNG.</div>', unsafe_allow_html=True)
st.markdown('<div class="upload"><b style="color:#123e63">Choose your report</b><br><span style="color:#728699;font-size:13px">Use a clear, readable image for better OCR results.</span></div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a PDF or image file", type=["pdf","jpg","jpeg","png"], label_visibility="collapsed")

if uploaded_file is not None:
    st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
    filename = uploaded_file.name.lower()

    try:
        if filename.endswith(".pdf"):
            with st.spinner("📄 Reading your PDF report..."):
                extracted_text = extract_text_from_pdf(uploaded_file)
        else:
            with st.spinner("🔎 Reading text from your image..."):
                extracted_text = extract_text_from_image(uploaded_file)

        if not extracted_text or not extracted_text.strip():
            st.error("❌ No readable text was found in this file.")
            st.info("Try a clearer report image, or if this is a scanned PDF, upload the page as JPG or PNG.")
        else:
            st.markdown('<div class="section-title">📋 Extracted Report</div><div class="section-subtitle">Review the text detected from your uploaded document.</div>', unsafe_allow_html=True)
            with st.expander("👁️ View extracted report text"):
                st.text_area("Extracted text", extracted_text, height=280, label_visibility="collapsed")

            if st.button("🔍 Analyze Medical Report", use_container_width=True):
                with st.spinner("🔬 Analyzing laboratory results..."):
                    results = analyze_report(extracted_text)

                if results.empty:
                    st.warning("⚠️ No laboratory test results were detected.")
                    st.info("The text was extracted, but laboratory values could not be identified in the expected format.")
                else:
                    total = len(results)
                    within = len(results[results["Status"] == "Within Range"])
                    below = len(results[results["Status"] == "Below Range"])
                    above = len(results[results["Status"] == "Above Range"])

                    st.markdown('<div class="section-title">📊 Laboratory Results Dashboard</div><div class="section-subtitle">Quick overview of the detected laboratory values.</div>', unsafe_allow_html=True)

                    metric_data = [
                        ("🧪","Total Tests",total,"blue"),
                        ("🟢","Within Range",within,"green"),
                        ("🟠","Below Range",below,"orange"),
                        ("🔴","Above Range",above,"red")
                    ]
                    metric_cols = st.columns(4)
                    for col, item in zip(metric_cols, metric_data):
                        icon, label, value, cls = item
                        with col:
                            st.markdown(f'<div class="metric"><div class="metric-icon">{icon}</div><div class="metric-label">{label}</div><div class="metric-value {cls}">{value}</div></div>', unsafe_allow_html=True)

                    st.markdown('<div class="section-title">🧪 Detailed Laboratory Results</div><div class="section-subtitle">Individual test results extracted from the report.</div>', unsafe_allow_html=True)

                    for _, row in results.iterrows():
                        test = str(row["Test"])
                        result = str(row["Result"])
                        unit = str(row["Unit"])
                        ref = str(row["Reference Range"])
                        status = str(row["Status"])

                        if status == "Within Range":
                            icon, cls = "🟢", "green"
                        elif status == "Below Range":
                            icon, cls = "🟠", "orange"
                        elif status == "Above Range":
                            icon, cls = "🔴", "red"
                        else:
                            icon, cls = "⚪", "blue"

                        st.markdown(f"""
<div class="result">
<div class="result-head">
<div><div class="test">🧪 {test}</div><div class="muted">Laboratory Test</div></div>
<div class="muted"><span class="{cls}">{icon} {status}</span></div>
</div>
<hr>
<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px">
<div><div class="label">RESULT</div><div class="value">{result}</div><div class="muted">{unit}</div></div>
<div><div class="label">REFERENCE RANGE</div><div class="range">{ref}</div></div>
<div><div class="label">STATUS</div><div class="range {cls}">{icon} {status}</div></div>
</div>
</div>
""", unsafe_allow_html=True)

                    with st.expander("📋 View results as a table"):
                        st.dataframe(results, use_container_width=True, hide_index=True)

                    summary = f"The report contains {total} laboratory test(s). "
                    if within:
                        summary += f"{within} result(s) are within the reference range shown on the report. "
                    if below:
                        summary += f"{below} result(s) are below the reference range shown on the report. "
                    if above:
                        summary += f"{above} result(s) are above the reference range shown on the report."

                    st.markdown('<div class="section-title">📌 Result Summary</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="card"><b style="color:#153f62">Analysis Overview</b><div style="color:#718496;font-size:13px;line-height:1.7;margin-top:5px">{summary}</div></div>', unsafe_allow_html=True)

                    st.markdown('<div class="section-title">🤖 AI Educational Explanation</div><div class="section-subtitle">General educational information based only on the extracted report text.</div>', unsafe_allow_html=True)

                    with st.spinner("🤖 Preparing educational explanation..."):
                        ai_summary = ai_explain_report(extracted_text)

                    safe_ai = (str(ai_summary)
                               .replace("&","&amp;")
                               .replace("<","&lt;")
                               .replace(">","&gt;")
                               .replace("\n","<br>"))

                    st.markdown(f'<div class="card" style="border-left:5px solid #18a15a"><b style="color:#153f62">🧠 Explanation</b><div style="color:#718496;font-size:13px;line-height:1.7;margin-top:6px">{safe_ai}</div></div>', unsafe_allow_html=True)

                    st.markdown('<div class="section-title">📥 Download Report</div><div class="section-subtitle">Save the results and educational explanation as a PDF.</div>', unsafe_allow_html=True)

                    try:
                        pdf_report = generate_report(results, ai_summary)
                        st.download_button("📥 Download PDF Report", data=pdf_report, file_name="medical_report_explanation.pdf", mime="application/pdf", use_container_width=True)
                    except Exception as pdf_error:
                        st.error("❌ Could not generate the PDF.")
                        st.code(str(pdf_error))

                    st.markdown("""
<div class="disclaimer">
<b>⚠️ Important Medical Disclaimer</b><br><br>
This application provides informational and educational explanations only. It does not provide a medical diagnosis or treatment.
<br><br>
Laboratory results should be interpreted by a qualified healthcare professional together with symptoms, medical history, medications and other relevant clinical information.
<br><br>
Reference ranges can vary between laboratories. OCR and extracted text can also contain errors. Always verify important values against the original report.
</div>
""", unsafe_allow_html=True)

    except Exception as error:
        st.error("❌ Could not process the uploaded file.")
        st.code(str(error))

st.markdown('<div class="footer">🩺 <b>AI Medical Report Explainer</b><br>Educational Use Only • Not a Substitute for Professional Medical Evaluation</div>', unsafe_allow_html=True)

