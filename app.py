
import io
import pandas as pd
import streamlit as st

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import ai_explain_report


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="MediLens | Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# CUSTOM UI
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #08111F;
    color: #EDF5FF;
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3, h4, p, label {
    color: #EDF5FF;
}
.hero {
    padding: 30px;
    border: 1px solid #25445A;
    border-radius: 20px;
    background: linear-gradient(130deg, #102238, #0B3038);
    margin-bottom: 24px;
}
.hero .eyebrow {
    color: #65E6D1;
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 2px;
}
.hero h1 {
    font-size: 2.35rem;
    margin-bottom: 8px;
}
.hero p {
    color: #B9C9D9;
    font-size: 1rem;
}
.panel {
    background: #101D2C;
    border: 1px solid #20374A;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
}
div[data-testid="stMetric"] {
    background: #101D2C;
    border: 1px solid #20374A;
    border-radius: 12px;
    padding: 15px;
}
div[data-testid="stMetricLabel"] {
    color: #B9C9D9;
}
.stButton > button {
    background: #16B8A6;
    color: #06151C;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    min-height: 44px;
}
.stButton > button:hover {
    background: #65E6D1;
    color: #06151C;
}
[data-testid="stFileUploader"] {
    background: #101D2C;
    border: 1px dashed #2C6672;
    border-radius: 12px;
    padding: 14px;
}
div[data-testid="stAlert"] {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="eyebrow">MEDILENS • REPORT INSIGHTS</div>
    <h1>🩺 AI Medical Report Explainer</h1>
    <p>
        Upload a medical report image or PDF to extract text,
        identify supported laboratory values, and review
        a plain-English explanation.
    </p>
</div>
""", unsafe_allow_html=True)

st.info(
    "Educational use only. This application does not diagnose "
    "medical conditions or replace professional medical advice."
)


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    help="Upload a clear JPG, JPEG, PNG, or PDF report.",
)

analyze_button = st.button(
    "🔍 Analyze My Report",
    use_container_width=True,
)


# --------------------------------------------------
# TEXT EXTRACTION
# --------------------------------------------------

if analyze_button:

    if uploaded_file is None:
        st.warning("Please upload a medical report first.")
        st.stop()

    extracted_text = ""

    try:
        file_name = uploaded_file.name.lower()
        file_type = uploaded_file.type or ""

        with st.spinner("Extracting report text..."):

            # PDF: extract embedded text first.
            if (
                file_type == "application/pdf"
                or file_name.endswith(".pdf")
            ):
                extracted_text = extract_text_from_pdf(
                    uploaded_file
                )

                # Scanned PDF: use OCR if no embedded text exists.
                if not extracted_text.strip():
                    import pymupdf
                    import pytesseract
                    from PIL import Image

                    uploaded_file.seek(0)
                    pdf_bytes = uploaded_file.read()
                    page_texts = []

                    with pymupdf.open(
                        stream=pdf_bytes,
                        filetype="pdf",
                    ) as pdf:

                        for page in pdf:
                            pix = page.get_pixmap(
                                matrix=pymupdf.Matrix(2, 2),
                                alpha=False,
                            )

                            image = Image.open(
                                io.BytesIO(pix.tobytes("png"))
                            )

                            text = pytesseract.image_to_string(
                                image,
                                config="--oem 3 --psm 6",
                            )

                            page_texts.append(text)

                    extracted_text = "\n".join(
                        page_texts
                    ).strip()

            # Image: always use OCR.
            else:
                extracted_text = extract_text_from_image(
                    uploaded_file
                )

        if not extracted_text.strip():
            st.error(
                "No text could be extracted. Try a clearer image "
                "or a PDF with readable text."
            )
            st.stop()

        # --------------------------------------------------
        # ANALYZE THE EXTRACTED TEXT
        # --------------------------------------------------

        with st.spinner("Analyzing supported laboratory results..."):

            results = analyze_report(extracted_text)

            patient_fields = extract_patient_fields(
                extracted_text
            )

            explanation = ai_explain_report(
                results,
                patient_fields,
                extracted_text,
            )

        # Store results so Streamlit reruns preserve the report.
        st.session_state["report_text"] = extracted_text
        st.session_state["report_results"] = results
        st.session_state["patient_fields"] = patient_fields
        st.session_state["report_explanation"] = explanation
        st.session_state["report_filename"] = uploaded_file.name

        st.success("Text extraction and analysis finished.")

    except Exception as error:
        st.error(f"Unable to process this report: {error}")
        st.info(
            "Check that all required Python packages are installed "
            "and that the imports match your repository filenames."
        )
        st.stop()


# --------------------------------------------------
# DISPLAY THE RESULTS
# --------------------------------------------------

if "report_text" in st.session_state:

    report_text = st.session_state["report_text"]
    results = st.session_state["report_results"]
    patient_fields = st.session_state["patient_fields"]
    explanation = st.session_state["report_explanation"]

    st.divider()

    # --------------------------------------------------
    # SUMMARY CARDS
    # --------------------------------------------------

    st.header("📊 Report Summary")

    total_tests = len(results)

    within_count = 0
    below_count = 0
    above_count = 0
    unknown_count = 0

    if not results.empty:
        statuses = results["Status"].astype(str)

        within_count = int(
            statuses.str.contains(
                "Within", case=False, na=False
            ).sum()
        )

        below_count = int(
            statuses.str.contains(
                "Below", case=False, na=False
            ).sum()
        )

        above_count = int(
            statuses.str.contains(
                "Above", case=False, na=False
            ).sum()
        )

        unknown_count = total_tests - (
            within_count + below_count + above_count
        )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Tests Identified", total_tests)
    c2.metric("Within Stated Range", within_count)
    c3.metric("Below / Above", below_count + above_count)
    c4.metric("Unclassified", unknown_count)

    st.caption(
        "These are automated text-based comparisons, not a diagnosis. "
        "Incorrect OCR or reference ranges can produce incorrect results."
    )

    # --------------------------------------------------
    # PATIENT DETAILS
    # --------------------------------------------------

    st.header("👤 Patient Information")

    patient_columns = st.columns(2)

    for index, (field, value) in enumerate(
        patient_fields.items()
    ):
        with patient_columns[index % 2]:
            st.markdown(
                f'<div class="panel"><strong>{field}</strong><br>'
                f'{value}</div>',
                unsafe_allow_html=True,
            )

    # --------------------------------------------------
    # LABORATORY TABLE
    # --------------------------------------------------

    st.header("🧪 Laboratory Results")

    if results.empty:

        st.warning(
            "No supported laboratory tests were recognized. "
            "The text may have been extracted successfully, but "
            "the report layout or test names may not be supported."
        )

        st.write(
            "Open the extracted text section below to check whether "
            "the test names, values, and ranges were read correctly."
        )

    else:

        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True,
        )

        # --------------------------------------------------
        # RESULT GRAPH
        # --------------------------------------------------

        numeric_results = results.copy()

        numeric_results["Result"] = pd.to_numeric(
            numeric_results["Result"],
            errors="coerce",
        )

        chart_data = numeric_results.dropna(
            subset=["Result"]
        )

        if not chart_data.empty:

            st.subheader("📈 Extracted Result Values")

            chart_data = chart_data.set_index("Test")[[
                "Result"
            ]]

            st.bar_chart(chart_data)

            st.caption(
                "Different laboratory tests may use different units "
                "and scales. The graph does not indicate severity."
            )

    # --------------------------------------------------
    # EXPLANATION
    # --------------------------------------------------

    st.header("💡 Report Explanation")

    st.markdown(
        '<div class="panel">',
        unsafe_allow_html=True,
    )

    st.text(explanation)

    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------
    # EXTRACTED TEXT
    # --------------------------------------------------

    st.header("📄 Extracted Report Text")

    st.caption(
        "Verify this text against the uploaded report. "
        "OCR can misread decimal points, units, and test names."
    )

    with st.expander(
        "View extracted text",
        expanded=False,
    ):
        st.text(report_text)

    # --------------------------------------------------
    # DOWNLOADS
    # --------------------------------------------------

    st.header("⬇️ Download Results")

    download_col1, download_col2 = st.columns(2)

    csv_data = results.to_csv(
        index=False
    ).encode("utf-8")

    with download_col1:
        st.download_button(
            "Download Laboratory Results (CSV)",
            data=csv_data,
            file_name="medical_report_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with download_col2:
        st.download_button(
            "Download Explanation (TXT)",
            data=explanation.encode("utf-8"),
            file_name="medical_report_explanation.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.caption(
        "Privacy reminder: medical reports contain sensitive personal "
        "information. Upload only documents you are authorized to use."
    )

else:

    # --------------------------------------------------
    # EMPTY STATE
    # --------------------------------------------------

    st.markdown("""
    <div class="panel">
        <h3>✨ How MediLens works</h3>
        <p>1. Upload a PDF or medical report image.</p>
        <p>2. Extract text from the document.</p>
        <p>3. Identify laboratory tests supported by the analyzer.</p>
        <p>4. Review the explanation and download the results.</p>
    </div>
    """, unsafe_allow_html=True)
