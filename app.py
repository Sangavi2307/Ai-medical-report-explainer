
import streamlit as st
import pandas as pd

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report
from ai_explainer import ai_explain_report


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>
    .main {
        background-color: #f6f9fc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .hero {
        padding: 28px;
        border-radius: 18px;
        background: linear-gradient(120deg, #103b66, #1976a8);
        color: white;
        margin-bottom: 24px;
    }

    .hero h1 {
        color: white;
        margin-bottom: 8px;
    }

    .hero p {
        color: #e6f4ff;
        font-size: 16px;
    }

    .section-title {
        color: #103b66;
        font-size: 23px;
        font-weight: 700;
        margin-top: 22px;
    }

    .notice {
        padding: 14px;
        border-radius: 10px;
        background: #fff8e7;
        border: 1px solid #f1d58a;
        color: #664d03;
        margin-top: 12px;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e5eaf0;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("## 🩺 MedReport AI")
    st.caption("Medical report understanding assistant")
    st.divider()

    st.markdown("### How to use")
    st.write("1. Upload a report.")
    st.write("2. Extract the report text.")
    st.write("3. Review detected laboratory results.")
    st.write("4. Read the AI-generated explanation.")

    st.divider()
    st.caption("Educational support only — not a medical diagnosis.")


# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>AI Medical Report Explainer</h1>
    <p>
        Understand your medical report with extracted text,
        laboratory result analysis, and simple-language explanations.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------- SAFETY NOTICE ----------------

st.warning(
    "This tool provides educational information only. "
    "It cannot diagnose a medical condition or recommend treatment. "
    "Consult a qualified healthcare professional about your results."
)


# ---------------- FILE UPLOAD ----------------

st.markdown(
    '<div class="section-title">1. Upload your medical report</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Choose a PDF or image file",
    type=["pdf", "png", "jpg", "jpeg"],
    help="Supported formats: PDF, PNG, JPG and JPEG.",
)

if uploaded_file is None:
    st.info("Upload a report to begin.")
    st.stop()


# ---------------- EXTRACT TEXT ----------------

st.markdown(
    '<div class="section-title">2. Extract report text</div>',
    unsafe_allow_html=True,
)

file_type = uploaded_file.name.rsplit(".", 1)[-1].lower()

extracted_text = ""

try:
    with st.spinner("Reading your report..."):
        if file_type == "pdf":
            extracted_text = extract_text_from_pdf(uploaded_file)
        else:
            extracted_text = extract_text_from_image(uploaded_file)

    if extracted_text is None:
        extracted_text = ""
    else:
        extracted_text = str(extracted_text).strip()

except Exception as error:
    st.error("Unable to extract text from this file.")
    st.caption(f"Technical details: {error}")
    st.info(
        "Check the PDF/image extraction functions and try another file."
    )
    st.stop()


# ---------------- DEBUG VIEW ----------------

with st.expander("Debug: Extracted Report Text", expanded=True):
    if extracted_text:
        st.text_area(
            "Text extracted from your file",
            value=extracted_text,
            height=250,
            disabled=True,
        )
        st.caption(
            f"Extracted approximately {len(extracted_text)} characters."
        )
    else:
        st.error("No text was extracted from this file.")
        st.write(
            "A scanned PDF may need OCR. Check whether the image is clear "
            "and whether the PDF extraction function supports your file."
        )


if not extracted_text:
    st.stop()


# ---------------- ANALYZE RESULTS ----------------

st.markdown(
    '<div class="section-title">3. Laboratory result analysis</div>',
    unsafe_allow_html=True,
)

try:
    with st.spinner("Analyzing detected laboratory results..."):
        results_df = analyze_report(extracted_text)

except Exception as error:
    st.error("The report analysis failed.")
    st.caption(f"Technical details: {error}")
    st.stop()


if results_df is None:
    results_df = pd.DataFrame()

if not isinstance(results_df, pd.DataFrame):
    results_df = pd.DataFrame(results_df)


if results_df.empty:
    st.warning(
        "No supported laboratory results were detected. "
        "Open the extracted-text section above to check what was read."
    )
    st.write(
        "If the test names or numbers are missing or incorrectly arranged, "
        "the extraction or analyzer rules may need adjustment."
    )

else:
    total_tests = len(results_df)

    if "Status" in results_df.columns:
        below_count = int(
            (results_df["Status"] == "Below Range").sum()
        )
        above_count = int(
            (results_df["Status"] == "Above Range").sum()
        )
        within_count = int(
            (results_df["Status"] == "Within Range").sum()
        )
    else:
        below_count = 0
        above_count = 0
        within_count = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Tests detected", total_tests)
    col2.metric("Within range", within_count)
    col3.metric("Below range", below_count)
    col4.metric("Above range", above_count)

    st.dataframe(
        results_df,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Statuses are based only on reference ranges detected in the "
        "report. A missing or incorrectly extracted range may affect "
        "classification."
    )


# ---------------- AI EXPLANATION ----------------

st.markdown(
    '<div class="section-title">4. AI report explanation</div>',
    unsafe_allow_html=True,
)

st.write(
    "Generate a plain-language explanation of the extracted report text."
)

if st.button("✨ Explain My Report", type="primary", use_container_width=True):
    try:
        with st.spinner("Preparing your explanation..."):
            explanation = ai_explain_report(extracted_text)

        if explanation:
            st.markdown("### Your report explanation")
            st.markdown(str(explanation))
        else:
            st.warning(
                "The AI service returned an empty explanation. "
                "Check your API configuration."
            )

    except Exception as error:
        st.error("Unable to generate the AI explanation.")
        st.caption(f"Technical details: {error}")
        st.info(
            "Check ai_explainer.py, your API key configuration, "
            "and the required packages."
        )


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "AI Medical Report Explainer | Educational use only. "
    "Always discuss medical results with a qualified healthcare professional."
    )
