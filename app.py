
import io
import pandas as pd
import streamlit as st

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import explain_report


st.set_page_config(
    page_title="MediLens | Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
)

st.markdown("""
<style>
.stApp {
    background: #08111f;
    color: #edf5ff;
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3, p, label {
    color: #edf5ff;
}
.hero {
    padding: 28px;
    border: 1px solid #1c3b50;
    border-radius: 18px;
    background: linear-gradient(135deg, #102238, #0b3038);
    margin-bottom: 24px;
}
.hero small {
    color: #65e6d1;
    letter-spacing: 2px;
    font-weight: 700;
}
.hero h1 {
    margin-bottom: 8px;
    font-size: 2.35rem;
}
.hero p {
    color: #b9c9d9;
}
.panel {
    padding: 20px;
    border: 1px solid #20374a;
    border-radius: 14px;
    background: #101d2c;
    margin-bottom: 18px;
}
div[data-testid="stMetric"] {
    background: #101d2c;
    border: 1px solid #20374a;
    padding: 15px;
    border-radius: 12px;
}
div[data-testid="stMetricLabel"] {
    color: #b9c9d9;
}
.stButton > button {
    background: #16b8a6;
    color: #06151c;
    border: 0;
    border-radius: 9px;
    font-weight: 700;
    min-height: 42px;
}
.stButton > button:hover {
    background: #65e6d1;
    color: #06151c;
}
[data-testid="stFileUploader"] {
    background: #101d2c;
    border: 1px dashed #2c6672;
    border-radius: 12px;
    padding: 14px;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <small>MEDILENS • REPORT INSIGHTS</small>
    <h1>🩺 AI Medical Report Explainer</h1>
    <p>
        Upload a medical report image or PDF to extract text,
        organize laboratory values, and understand the extracted results.
    </p>
</div>
""", unsafe_allow_html=True)

st.info(
    "Educational use only. This tool does not diagnose conditions "
    "or replace advice from a qualified healthcare professional."
)

uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    help="Supported formats: PDF, PNG, JPG, JPEG",
)

analyze_button = st.button(
    "Analyze My Report",
    use_container_width=True,
)

if analyze_button:
    if uploaded_file is None:
        st.warning("Please upload a PDF or image first.")
        st.stop()

    extracted_text = ""

    try:
        file_type = uploaded_file.type or ""
        file_name = uploaded_file.name.lower()

        with st.spinner("Reading your report..."):
            if (
                file_type == "application/pdf"
                or file_name.endswith(".pdf")
            ):
                extracted_text = extract_text_from_pdf(uploaded_file)

                # Scanned PDFs may not contain selectable text.
                if not extracted_text.strip():
                    uploaded_file.seek(0)
                    import pymupdf
                    import pytesseract
                    from PIL import Image

                    pdf_bytes = uploaded_file.read()
                    image_text = []

                    with pymupdf.open(
                        stream=pdf_bytes,
                        filetype="pdf"
                    ) as pdf:
                        for page in pdf:
                            pix = page.get_pixmap(
                                matrix=pymupdf.Matrix(2, 2),
                                alpha=False,
                            )
                            image = Image.open(
                                io.BytesIO(pix.tobytes("png"))
                            )
                            page_text = pytesseract.image_to_string(
                                image,
                                config="--oem 3 --psm 6",
                            )
                            image_text.append(page_text)

                    extracted_text = "\n".join(image_text).strip()
            else:
                # IMPORTANT: image uploads use OCR here.
                extracted_text = extract_text_from_image(uploaded_file)

        if not extracted_text.strip():
            st.error(
                "No text could be read. Try a clearer, straight image "
                "with good lighting, or a text-based PDF."
            )
            st.stop()

        # Both PDF and image text go through the same analyzer.
        results = analyze_report(extracted_text)
        patient_fields = extract_patient_fields(extracted_text)
        explanation = explain_report(results, patient_fields)

        st.session_state["report_text"] = extracted_text
        st.session_state["report_results"] = results
        st.session_state["patient_fields"] = patient_fields
        st.session_state["report_explanation"] = explanation
        st.session_state["report_filename"] = uploaded_file.name

    except Exception as error:
        st.error(f"Could not process this report: {error}")
        st.caption(
            "If this is an image, check that OCR dependencies are installed "
            "in requirements.txt and packages.txt."
        )
        st.stop()


if "report_text" in st.session_state:
    report_text = st.session_state["report_text"]
    results = st.session_state["report_results"]
    patient_fields = st.session_state["patient_fields"]
    explanation = st.session_state["report_explanation"]

    st.divider()
    st.header("📊 Report Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Tests Identified", len(results))

    with col2:
        within_count = (
            int((results["Status"] == "Within Range").sum())
            if not results.empty else 0
        )
        st.metric("Within Extracted Range", within_count)

    with col3:
        flagged_count = (
            int(results["Status"].isin(
                ["Below Range", "Above Range"]
            ).sum())
            if not results.empty else 0
        )
        st.metric("Outside Extracted Range", flagged_count)

    st.caption(
        "These counts describe automated comparisons only. "
        "They are not a medical assessment."
    )

    st.header("👤 Patient Information")

    patient_cols = st.columns(2)

    for index, (field, value) in enumerate(patient_fields.items()):
        with patient_cols[index % 2]:
            st.markdown(f"**{field}**")
            st.write(value)

    st.header("🧪 Laboratory Results")

    if results.empty:
        st.warning(
            "Text was extracted, but no supported laboratory tests "
            "were recognized. Check the extracted text below. "
            "Different report layouts may need additional parsing rules."
        )
    else:
        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True,
        )

        numeric_results = results.copy()
        numeric_results["Result"] = pd.to_numeric(
            numeric_results["Result"],
            errors="coerce",
        )
        chart_data = numeric_results.dropna(
            subset=["Result"]
        ).set_index("Test")[["Result"]]

        if not chart_data.empty:
            st.subheader("Extracted Result Values")
            st.bar_chart(chart_data)

            st.caption(
                "Values can use different units and scales. "
                "The chart is a visual summary, not a comparison "
                "of medical severity."
            )

    st.header("💡 Explanation")

    st.text(explanation)

    st.header("📄 Extracted Text")
    st.caption(
        "Check this text to verify that OCR read your image or PDF correctly."
    )

    with st.expander("View extracted report text", expanded=False):
        st.text(report_text)

    safe_results = results.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Laboratory Results (CSV)",
        data=safe_results,
        file_name="medical_report_results.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.download_button(
        "Download Explanation (TXT)",
        data=explanation.encode("utf-8"),
        file_name="medical_report_explanation.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.caption(
        "Privacy reminder: medical reports contain sensitive information. "
        "Only upload reports you are authorized to use."
    )
else:
    st.markdown("""
    <div class="panel">
        <h3>How it works</h3>
        <p>1. Upload a PDF or a clear report image.</p>
        <p>2. The app extracts text using PDF reading or image OCR.</p>
        <p>3. Supported lab values are matched with extracted ranges.</p>
        <p>4. Review the results and verify them against the original report.</p>
    </div>
    """, unsafe_allow_html=True)
