
import streamlit as st
import pandas as pd

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
    background: #0b1220;
    color: #eef4ff;
}
[data-testid="stHeader"] {
    background: transparent;
}
.block-container {
    max-width: 1150px;
    padding-top: 2rem;
}
h1, h2, h3 {
    color: #f1f7ff;
}
p, label, li {
    color: #c8d5e7;
}
div[data-testid="stMetric"] {
    background: #111e30;
    border: 1px solid #263b50;
    padding: 15px;
    border-radius: 12px;
}
div[data-testid="stFileUploader"] {
    background: #111e30;
    border-radius: 12px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)


st.title("🩺 MediLens")
st.caption("AI Medical Report Explainer · Educational use only")

st.info(
    "Upload a medical report as a PDF or image. "
    "The app extracts text and looks for supported laboratory results. "
    "Please verify OCR output against the original document."
)

uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg", "webp"],
)

if uploaded_file is not None:
    st.write(f"**Uploaded file:** {uploaded_file.name}")

    if st.button("Analyze Report", type="primary"):
        with st.spinner("Extracting and analyzing your report..."):
            try:
                extension = uploaded_file.name.lower()

                if extension.endswith(".pdf"):
                    report_text = extract_text_from_pdf(uploaded_file)

                    # A scanned PDF may have no selectable text.
                    # OCR each page if normal extraction returns nothing.
                    if not report_text.strip():
                        import pymupdf
                        from PIL import Image
                        import io
                        import pytesseract

                        uploaded_file.seek(0)
                        pdf_bytes = uploaded_file.read()
                        page_texts = []

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
                                page_texts.append(
                                    pytesseract.image_to_string(
                                        image,
                                        config="--oem 3 --psm 6"
                                    )
                                )

                        report_text = "\n".join(page_texts).strip()
                else:
                    report_text = extract_text_from_image(uploaded_file)

                if not report_text:
                    st.error(
                        "No text could be extracted. Try a clearer, "
                        "well-lit image or a text-based PDF."
                    )
                    st.stop()

                patient_fields = extract_patient_fields(report_text)
                results_df = analyze_report(report_text)
                explanation = explain_report(
                    report_text,
                    results_df,
                    patient_fields,
                )

                st.session_state["report_text"] = report_text
                st.session_state["patient_fields"] = patient_fields
                st.session_state["results_df"] = results_df
                st.session_state["explanation"] = explanation

            except Exception as error:
                st.error(f"Could not analyze this file: {error}")


if "report_text" in st.session_state:
    report_text = st.session_state["report_text"]
    patient_fields = st.session_state["patient_fields"]
    results_df = st.session_state["results_df"]
    explanation = st.session_state["explanation"]

    st.divider()
    st.header("1. Extracted Report Text")

    with st.expander("View extracted text", expanded=True):
        st.text_area(
            "OCR / PDF text",
            value=report_text,
            height=260,
            disabled=True,
        )

    st.header("2. Patient Information")

    patient_items = list(patient_fields.items())

    for start in range(0, len(patient_items), 3):
        group = patient_items[start:start + 3]
        cols = st.columns(len(group))

        for col, (label, value) in zip(cols, group):
            with col:
                st.metric(label, value or "Not found")

    st.header("3. Laboratory Results")

    if results_df.empty:
        st.info(
            "No supported laboratory results were detected. "
            "This document may be a medical note or leave report, "
            "or its laboratory layout may not be supported. "
            "The extracted text and explanation are still available."
        )
    else:
        st.dataframe(results_df, use_container_width=True)

        numeric_df = results_df.copy()
        numeric_df["Result"] = pd.to_numeric(
            numeric_df["Result"],
            errors="coerce",
        )
        numeric_df = numeric_df.dropna(subset=["Result"])

        if not numeric_df.empty:
            st.subheader("Result Overview")
            chart_df = numeric_df.set_index("Test")[["Result"]]
            st.bar_chart(chart_df)

        csv_data = results_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download laboratory results (CSV)",
            data=csv_data,
            file_name="medilens_results.csv",
            mime="text/csv",
        )

    st.header("4. Report Explanation")
    st.markdown(explanation)

    st.download_button(
        "Download extracted report text",
        data=report_text.encode("utf-8"),
        file_name="extracted_report.txt",
        mime="text/plain",
    )

    st.divider()
    st.caption(
        "MediLens is an educational tool, not a medical device. "
        "OCR and automatic parsing may be inaccurate. It does not "
        "diagnose conditions or determine fitness for work. "
        "Consult a qualified healthcare professional."
    )
