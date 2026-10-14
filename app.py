
import io
import streamlit as st
import pandas as pd
import pymupdf
import pytesseract

from PIL import Image

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import explain_report


st.set_page_config(
    page_title="MediLens | Medical Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# -------------------- DESIGN SYSTEM --------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #08111f;
    --panel: #101d2e;
    --panel-light: #14243a;
    --border: #26374c;
    --text: #edf5ff;
    --muted: #9aacc2;
    --teal: #42dfc0;
    --blue: #75aaff;
}

.stApp {
    background:
        radial-gradient(ellipse at 10% 0%, #122b43 0%, transparent 42%),
        #08111f;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    display: none;
}

.block-container {
    max-width: 1240px;
    padding: 2rem 2rem 4rem;
}

h1, h2, h3, h4 {
    font-family: 'Manrope', sans-serif !important;
    color: var(--text) !important;
    letter-spacing: -0.4px;
}

p, label, li, .stMarkdown {
    color: #c8d6e8;
}

.brand {
    font-family: 'Manrope', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    color: #f2f8ff;
}

.brand span {
    color: var(--teal);
}

.eyebrow {
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--teal);
    font-size: 0.72rem;
    font-weight: 700;
}

.hero {
    background: linear-gradient(120deg, #142b43, #102032 70%, #103a42);
    border: 1px solid #29445a;
    border-radius: 24px;
    padding: 32px;
    margin: 20px 0 26px;
}

.hero h1 {
    font-size: clamp(2rem, 4vw, 3.2rem);
    line-height: 1.12;
    margin: 10px 0;
}

.hero p {
    max-width: 700px;
    color: #b7cadd;
    font-size: 1rem;
    line-height: 1.8;
}

.panel {
    background: rgba(16, 29, 46, 0.92);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px;
    margin: 12px 0 20px;
}

.metric-card {
    background: linear-gradient(145deg, #14253a, #101b2c);
    border: 1px solid #2b3d53;
    border-radius: 16px;
    padding: 18px;
    min-height: 112px;
}

.metric-label {
    color: #9fb2c8;
    font-size: 0.78rem;
    margin-bottom: 8px;
}

.metric-value {
    color: #f4f8ff;
    font-size: 1.35rem;
    font-weight: 700;
    overflow-wrap: anywhere;
}

.section-kicker {
    color: var(--teal);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

[data-testid="stFileUploader"] {
    background: #0e1b2b;
    border: 1px dashed #3a6275;
    border-radius: 14px;
    padding: 14px;
}

[data-testid="stDataFrame"] {
    border: 1px solid #2b3d53;
    border-radius: 12px;
    overflow: hidden;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 10px;
    font-weight: 700;
    min-height: 44px;
    border: 1px solid #3c6b79;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #1aab9b, #3acbb4);
    color: #061522;
    border: 0;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

hr {
    border-color: #25374b;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# -------------------- HEADER --------------------

st.markdown("""
<div class="brand">Medi<span>Lens</span> <span style="
font-size:0.7rem;color:#91a6be;font-weight:500;
letter-spacing:1px;">REPORT INTELLIGENCE</span></div>

<div class="hero">
    <div class="eyebrow">Medical document workspace</div>
    <h1>Understand your report.<br>One clear view.</h1>
    <p>
        Extract medical document text, review available information,
        explore recognized laboratory measurements, and read a structured
        educational explanation in one place.
    </p>
</div>
""", unsafe_allow_html=True)


# -------------------- UPLOAD WORKSPACE --------------------

st.markdown('<div class="section-kicker">01 / Upload document</div>',
            unsafe_allow_html=True)
st.subheader("Start a report review")

st.caption(
    "Supported formats: PDF, PNG, JPG, JPEG and WEBP. "
    "For best results, upload a clear, straight, well-lit document."
)

uploaded_file = st.file_uploader(
    "Choose a medical report",
    type=["pdf", "png", "jpg", "jpeg", "webp"],
    key="report_upload",
)

analyze_clicked = st.button(
    "Analyze report",
    type="primary",
    disabled=uploaded_file is None,
    use_container_width=True,
)


def extract_pdf_with_ocr(uploaded_file):
    text = extract_text_from_pdf(uploaded_file)

    if text.strip():
        return text

    # Fall back to OCR for scanned PDFs.
    uploaded_file.seek(0)
    data = uploaded_file.read()
    pages = []

    with pymupdf.open(stream=data, filetype="pdf") as pdf:
        for page in pdf:
            pix = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False,
            )
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            pages.append(
                pytesseract.image_to_string(
                    image,
                    config="--oem 3 --psm 6",
                )
            )

    return "\n\n".join(pages).strip()


if analyze_clicked and uploaded_file is not None:
    try:
        with st.spinner("Reading and organizing your document..."):
            if uploaded_file.name.lower().endswith(".pdf"):
                report_text = extract_pdf_with_ocr(uploaded_file)
            else:
                report_text = extract_text_from_image(uploaded_file)

            if not report_text.strip():
                st.error(
                    "No text was extracted. Try a clearer image "
                    "or a PDF with readable text."
                )
                st.stop()

            patient_fields = extract_patient_fields(report_text)
            results_df = analyze_report(report_text)
            explanation = explain_report(
                report_text,
                results_df,
                patient_fields,
            )

            # Store results only after successful processing.
            st.session_state["ml_text"] = report_text
            st.session_state["ml_patient"] = patient_fields
            st.session_state["ml_results"] = results_df
            st.session_state["ml_explanation"] = explanation
            st.session_state["ml_filename"] = uploaded_file.name

    except Exception as error:
        st.error(f"Document processing failed: {error}")


# -------------------- RESULTS DASHBOARD --------------------

if "ml_text" in st.session_state:
    report_text = st.session_state["ml_text"]
    patient_fields = st.session_state["ml_patient"]
    results_df = st.session_state["ml_results"]
    explanation = st.session_state["ml_explanation"]
    filename = st.session_state["ml_filename"]

    st.divider()

    st.markdown(
        '<div class="section-kicker">02 / Report overview</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Your document at a glance")
    st.caption(f"Document: {filename}")

    patient_name = patient_fields.get("Patient Name", "Not found")
    patient_date = patient_fields.get(
        "Date of Visit",
        patient_fields.get("Date of Examination", "Not found"),
    )

    cards = [
        ("DOCUMENT", "Processed"),
        ("PATIENT", patient_name),
        ("LAB RESULTS", str(len(results_df))),
        ("TEXT LENGTH", f"{len(report_text):,} characters"),
    ]

    cols = st.columns(4)

    for col, (label, value) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    # -------------------- PATIENT INFORMATION --------------------

    st.markdown(
        '<div class="section-kicker">03 / Patient information</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Extracted details")

    detail_cols = st.columns(3)

    for index, (label, value) in enumerate(patient_fields.items()):
        with detail_cols[index % 3]:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="font-size:1rem">
                        {value}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("")

    # -------------------- LABORATORY RESULTS --------------------

    st.markdown(
        '<div class="section-kicker">04 / Measurements</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Laboratory results")

    if results_df.empty:
        st.info(
            "No supported laboratory measurements were recognized. "
            "This may be a medical note, examination report, or "
            "a laboratory table that the current parser cannot read. "
            "No sample values have been inserted."
        )
    else:
        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Automated status comparisons depend on extracted values "
            "and ranges. Confirm them against the original document."
        )

        chart_data = results_df.copy()
        chart_data["Result"] = pd.to_numeric(
            chart_data["Result"],
            errors="coerce",
        )
        chart_data = chart_data.dropna(subset=["Result"])

        if not chart_data.empty:
            st.subheader("Result visualization")
            st.bar_chart(
                chart_data.set_index("Test")[["Result"]],
                use_container_width=True,
            )
            st.caption(
                "Results may use different units and scales. "
                "The chart is a numeric overview, not a clinical comparison."
            )

        st.download_button(
            "Download laboratory table (CSV)",
            data=results_df.to_csv(index=False).encode("utf-8"),
            file_name="medilens_laboratory_results.csv",
            mime="text/csv",
        )

    # -------------------- EXTRACTED TEXT --------------------

    st.markdown(
        '<div class="section-kicker">05 / Source document</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Extracted text")

    st.warning(
        "OCR may misread names, dates, measurements and medical terms. "
        "The text below is not a verified transcription."
    )

    with st.expander("Review the complete extracted text", expanded=False):
        st.text_area(
            "Extracted document",
            value=report_text,
            height=320,
            disabled=True,
            label_visibility="collapsed",
        )

    # -------------------- PROFESSIONAL EXPLANATION --------------------

    st.markdown(
        '<div class="section-kicker">06 / Explanation</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Detailed report explanation")

    st.markdown(
        """
        <div class="panel">
            <p style="margin:0;color:#9aacc2;">
                STRUCTURED EDUCATIONAL REVIEW
            </p>
            <p style="margin-top:8px;color:#eaf5ff;">
                The sections below summarize the information detected
                in your document. They do not establish a diagnosis.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(explanation)

    # -------------------- EXPORT --------------------

    st.markdown(
        '<div class="section-kicker">07 / Export</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Keep a copy of this review")

    export_text = (
        f"MediLens - Educational Report Review\n"
        f"Source file: {filename}\n\n"
        f"EXTRACTED TEXT\n\n{report_text}\n\n"
        f"STRUCTURED EXPLANATION\n\n{explanation}\n\n"
        "NOTICE: This is an automated educational summary, not a "
        "diagnosis, treatment recommendation, or fitness-for-work decision."
    )

    st.download_button(
        "Download full review (TXT)",
        data=export_text.encode("utf-8"),
        file_name="medilens_report_review.txt",
        mime="text/plain",
        use_container_width=True,
    )

    if not results_df.empty:
        st.download_button(
            "Download results (CSV)",
            data=results_df.to_csv(index=False).encode("utf-8"),
            file_name="medilens_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.divider()

    st.caption(
        "MediLens is an educational prototype. It can make extraction "
        "and parsing errors and is not a substitute for professional "
        "medical assessment. Avoid uploading identifiable medical "
        "documents unless you are comfortable with the service's "
        "data-handling arrangements."
    )

else:
    st.markdown(
        """
        <div class="panel">
            <h3>Your report workspace is ready</h3>
            <p>
                Upload a document to see extracted information, supported
                laboratory results, visualizations and a structured explanation.
            </p>
            <p style="color:#42dfc0;">
                PDF and image formats supported
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
