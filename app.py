
import io
import re
import pandas as pd
import streamlit as st
import pymupdf
from PIL import Image

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import ai_explain_report


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="MediLens | AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07111f 0%, #0b192b 55%, #102438 100%);
    color: #eef5ff;
}
[data-testid="stHeader"] {
    background: rgba(7, 17, 31, 0.92);
}
.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero {
    padding: 30px;
    border: 1px solid #24465c;
    border-radius: 22px;
    background: linear-gradient(120deg, #10263a, #123a46);
    margin-bottom: 24px;
}
.hero h1 {
    color: #f3f8ff;
    font-size: 2.4rem;
    margin-bottom: 8px;
}
.hero p {
    color: #b7cedd;
    font-size: 1.05rem;
}
.section-card {
    background: #102236;
    border: 1px solid #263f55;
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
}
.small-muted {
    color: #aec3d4;
    font-size: 0.9rem;
}
div[data-testid="stMetric"] {
    background: #10263a;
    border: 1px solid #27475b;
    padding: 16px;
    border-radius: 14px;
}
div[data-testid="stMetricLabel"] {
    color: #b7cedd;
}
div[data-testid="stMetricValue"] {
    color: #62e0cc;
}
.stButton > button {
    background: #27c5b4;
    color: #061923;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    min-height: 44px;
}
.stButton > button:hover {
    background: #61e6d7;
    color: #061923;
}
div[data-testid="stFileUploader"] {
    background: #102236;
    border: 1px dashed #3d7586;
    padding: 16px;
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>🩺 MediLens</h1>
    <p><b>AI Medical Report Explainer</b></p>
    <p>
        Upload a laboratory report to extract available information,
        review detected results, and receive an educational explanation.
    </p>
</div>
""", unsafe_allow_html=True)

st.info(
    "Educational use only. MediLens does not diagnose diseases or "
    "replace advice from a qualified healthcare professional."
)


# ---------------- SESSION STATE ----------------

if "report_data" not in st.session_state:
    st.session_state.report_data = None


# ---------------- HELPER FUNCTIONS ----------------

def extract_scanned_pdf(uploaded_file):
    """Use OCR on scanned PDF pages when embedded text is unavailable."""
    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()

    pages_text = []

    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
        for page in pdf:
            pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
            image_bytes = pix.tobytes("png")

            with Image.open(io.BytesIO(image_bytes)) as image:
                pages_text.append(
                    extract_text_from_image(io.BytesIO(image_bytes))
                )

    return "\n\n".join(pages_text).strip()


def result_to_number(value):
    """Convert a displayed lab result to a number when possible."""
    if value is None:
        return None

    cleaned = re.sub(r"^[<>≤≥]\s*", "", str(value))
    cleaned = cleaned.replace(",", "").strip()

    try:
        return float(cleaned)
    except ValueError:
        return None


# ---------------- UPLOAD ----------------

st.markdown("## 1. Upload your report")

uploaded_file = st.file_uploader(
    "Choose a medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    help="PDF, PNG, JPG, and JPEG files are supported."
)

if uploaded_file:
    st.caption(
        f"Selected file: {uploaded_file.name} "
        f"({uploaded_file.size / 1024:.1f} KB)"
    )

    if st.button("Extract and analyze report", use_container_width=True):
        try:
            with st.spinner("Reading your report..."):
                if uploaded_file.name.lower().endswith(".pdf"):
                    extracted_text = extract_text_from_pdf(uploaded_file)

                    if len(extracted_text.strip()) < 20:
                        with st.spinner("Scanned PDF detected. Running OCR..."):
                            extracted_text = extract_scanned_pdf(uploaded_file)
                else:
                    extracted_text = extract_text_from_image(uploaded_file)

                if not extracted_text.strip():
                    st.session_state.report_data = None
                    st.error(
                        "No readable text was found. Try a clearer image "
                        "or a PDF with better scan quality."
                    )
                else:
                    patient_fields = extract_patient_fields(extracted_text)
                    results = analyze_report(extracted_text)

                    with st.spinner("Preparing educational explanation..."):
                        explanation = ai_explain_report(
                            results=results,
                            patient_fields=patient_fields,
                            report_text=extracted_text
                        )

                    st.session_state.report_data = {
                        "filename": uploaded_file.name,
                        "text": extracted_text,
                        "patient_fields": patient_fields,
                        "results": results,
                        "explanation": explanation
                    }

                    st.success("Report extraction completed.")

        except Exception as exc:
            st.error(
                "The report could not be processed. "
                f"Error type: {type(exc).__name__}"
            )


# ---------------- RESULTS ----------------

data = st.session_state.report_data

if data:
    results = data["results"]
    patient_fields = data["patient_fields"]
    explanation = data["explanation"]
    extracted_text = data["text"]

    st.divider()
    st.markdown("## 2. Report overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Detected tests", len(results))

    with col2:
        flagged_count = (
            results["Status"].isin([
                "Below detected range",
                "Above detected range"
            ]).sum()
            if not results.empty else 0
        )
        st.metric("Range flags detected", int(flagged_count))

    with col3:
        st.metric("File type", data["filename"].split(".")[-1].upper())

    st.markdown("## 3. Patient information")

    patient_columns = st.columns(2)

    fields_list = list(patient_fields.items())

    for index, (field, value) in enumerate(fields_list):
        with patient_columns[index % 2]:
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="small-muted">{field}</div>
                    <h4>{value if value else "Not detected"}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("## 4. Detected laboratory results")

    if results.empty:
        st.warning(
            "No supported laboratory values were confidently detected. "
            "This does not mean that the report contains no results. "
            "Review the extracted text below and check the original report."
        )
    else:
        st.caption(
            "Please verify each value, unit, and range against the original "
            "report. Automated extraction can make mistakes."
        )

        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True
        )

        chart_data = results.copy()
        chart_data["Numeric Result"] = chart_data["Result"].apply(
            result_to_number
        )
        chart_data = chart_data.dropna(subset=["Numeric Result"])

        if not chart_data.empty:
            st.markdown("### Numeric results chart")
            st.caption(
                "This chart compares raw numbers only. Different tests may "
                "use different units and scales, so heights must not be "
                "compared across different tests as if they were equivalent."
            )

            chart_data = chart_data.set_index("Test")
            st.bar_chart(chart_data["Numeric Result"])

    st.markdown("## 5. Educational explanation")

    st.markdown(explanation)

    st.markdown("## 6. Extracted report text")

    with st.expander("View the text extracted from your report"):
        st.text(extracted_text)

    st.markdown("## 7. Download results")

    download_col1, download_col2 = st.columns(2)

    with download_col1:
        csv_data = results.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download results as CSV",
            data=csv_data,
            file_name="medilens_results.csv",
            mime="text/csv",
            use_container_width=True
        )

    with download_col2:
        report_text = (
            "MediLens - AI Medical Report Explainer\n"
            "Educational use only; not a diagnosis.\n\n"
            f"Source file: {data['filename']}\n\n"
            "PATIENT INFORMATION\n"
            + "\n".join(
                f"{key}: {value or 'Not detected'}"
                for key, value in patient_fields.items()
            )
            + "\n\nDETECTED RESULTS\n"
            + (
                results.to_string(index=False)
                if not results.empty
                else "No supported results confidently detected."
            )
            + "\n\nEDUCATIONAL EXPLANATION\n"
            + explanation
            + "\n\nEXTRACTED TEXT\n"
            + extracted_text
        )

        st.download_button(
            "Download summary as TXT",
            data=report_text.encode("utf-8"),
            file_name="medilens_report_summary.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.warning(
        "Medical reports contain sensitive personal information. "
        "Only upload reports you are authorized to use, and handle "
        "downloaded files securely."
    )
