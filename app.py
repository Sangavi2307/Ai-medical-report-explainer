

import io

import pandas as pd
import pymupdf
import streamlit as st

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from report_generator import create_pdf_report


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MediExplain | Medical Report Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# PROFESSIONAL UI STYLING
# =========================================================

st.markdown(
    """
    <style>
    :root {
        --navy: #142D4E;
        --teal: #087F8C;
        --light-teal: #E7F6F5;
        --muted: #64748B;
        --surface: #FFFFFF;
        --border: #E2E8F0;
    }

    .stApp {
        background-color: #F5F8FC;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E5EAF1;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #142D4E;
    }

    h1, h2, h3 {
        color: #142D4E;
        letter-spacing: -0.4px;
    }

    p, li, label {
        color: #334155;
    }

    .brand {
        font-size: 1.15rem;
        font-weight: 800;
        color: #087F8C;
        letter-spacing: 0.3px;
    }

    .hero {
        background: linear-gradient(120deg, #142D4E 0%, #087F8C 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 1.3rem;
        color: white;
    }

    .hero h1 {
        color: white !important;
        font-size: 2.05rem;
        margin: 0.45rem 0;
    }

    .hero p {
        color: #E3F5F7 !important;
        font-size: 1rem;
        margin-bottom: 0;
    }

    .eyebrow {
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #BDEBEA;
    }

    .panel {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.15rem;
        margin-bottom: 0.8rem;
    }

    .panel-title {
        color: #142D4E;
        font-size: 1.03rem;
        font-weight: 750;
        margin-bottom: 0.35rem;
    }

    .muted {
        color: #64748B;
        font-size: 0.88rem;
    }

    .notice {
        background: #FFF8E8;
        border: 1px solid #F3DFB0;
        border-left: 4px solid #D99B26;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin: 0.8rem 0 1.2rem 0;
        color: #654B16;
        font-size: 0.88rem;
    }

    .success-note {
        background: #E9F8F1;
        border: 1px solid #C8EBDD;
        border-radius: 12px;
        padding: 1rem;
        color: #176448;
        margin-bottom: 1rem;
    }

    .metric-label {
        color: #64748B;
        font-size: 0.83rem;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        color: #142D4E;
        font-size: 1.65rem;
        font-weight: 800;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 2.8rem;
        transition: all 0.2s ease;
    }

    .stButton > button[kind="primary"] {
        background: #087F8C;
        border: 1px solid #087F8C;
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background: #066873;
        border-color: #066873;
    }

    [data-testid="stFileUploader"] {
        background: #FFFFFF;
        border: 1px dashed #A8C8D2;
        border-radius: 14px;
        padding: 0.6rem;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        overflow: hidden;
    }

    hr {
        border-color: #E2E8F0;
    }

    .footer {
        text-align: center;
        color: #64748B;
        font-size: 0.82rem;
        padding: 1.5rem 0 0.5rem 0;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.8rem 2rem 0.8rem;
        }

        .hero {
            padding: 1.3rem;
            border-radius: 14px;
        }

        .hero h1 {
            font-size: 1.55rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.markdown(
        '<div class="brand">🩺 MediExplain</div>',
        unsafe_allow_html=True,
    )

    st.caption("Medical Report Assistant")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "How It Works",
            "About & Safety",
        ],
        label_visibility="visible",
    )

    st.divider()

    st.markdown("#### Supported files")
    st.write("📄 PDF documents")
    st.write("🖼️ PNG and JPG images")

    st.markdown("#### File size")
    st.write("Maximum 10 MB per upload")

    st.divider()

    st.caption("Educational tool — not a diagnostic service.")


# =========================================================
# COMMON FUNCTIONS
# =========================================================

def extract_text_from_uploaded_pdf(uploaded_file):
    """Extract selectable PDF text and fall back to OCR."""

    uploaded_file.seek(0)
    text = extract_text_from_pdf(uploaded_file)

    if text and text.strip():
        return text.strip()

    uploaded_file.seek(0)
    pdf_bytes = uploaded_file.read()

    document = pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf",
    )

    extracted_pages = []

    try:
        for page in document:
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False,
            )

            image_bytes = pixmap.tobytes("png")
            image_file = io.BytesIO(image_bytes)
            image_file.name = "page.png"

            page_text = extract_text_from_image(image_file)
            extracted_pages.append(page_text or "")

    finally:
        document.close()

    return "\n".join(extracted_pages).strip()


def prepare_results(results):
    """Standardize analyzer output for the results table."""

    expected_columns = [
        "Test",
        "Result",
        "Unit",
        "Reference Range",
        "Status",
    ]

    if isinstance(results, pd.DataFrame):
        results_df = results.copy()

    elif isinstance(results, list):
        results_df = pd.DataFrame(results)

    else:
        results_df = pd.DataFrame()

    if results_df.empty:
        return pd.DataFrame(columns=expected_columns)

    column_mapping = {
        "test_name": "Test",
        "test": "Test",
        "result": "Result",
        "value": "Result",
        "unit": "Unit",
        "reference_range": "Reference Range",
        "normal_range": "Reference Range",
        "status": "Status",
    }

    results_df.columns = [
        column_mapping.get(
            str(column).strip().lower(),
            str(column).strip(),
        )
        for column in results_df.columns
    ]

    for column in expected_columns:
        if column not in results_df.columns:
            results_df[column] = ""

    return results_df[expected_columns]


def check_report_quality(report_text, results_df):
    """Check whether text and structured results were detected."""

    if not report_text or not report_text.strip():
        return False, "No readable text was extracted."

    if results_df.empty:
        return (
            False,
            "Text was extracted, but no supported laboratory "
            "results were detected.",
        )

    return True, "Report text and laboratory results detected."


def show_summary_dashboard(results_df):
    """Display result counts and a summary chart."""

    statuses = (
        results_df["Status"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    normal_count = int(
        statuses.str.contains(
            r"within range|normal",
            regex=True,
        ).sum()
    )

    low_count = int(
        statuses.str.contains(
            r"below|low",
            regex=True,
        ).sum()
    )

    high_count = int(
        statuses.str.contains(
            r"above|high",
            regex=True,
        ).sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        (col1, "Tests detected", len(results_df)),
        (col2, "Within range", normal_count),
        (col3, "Below range", low_count),
        (col4, "Above range", high_count),
    ]

    for column, label, value in metrics:
        with column:
            st.markdown(
                f"""
                <div class="panel">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    chart_data = pd.DataFrame(
        {
            "Category": [
                "Within range",
                "Below range",
                "Above range",
            ],
            "Count": [
                normal_count,
                low_count,
                high_count,
            ],
        }
    )

    st.markdown("#### Result overview")
    st.bar_chart(
        chart_data.set_index("Category"),
        use_container_width=True,
    )


def clear_analysis():
    """Clear the current analysis from Streamlit session state."""

    for key in [
        "report_text",
        "results_df",
        "quality_ok",
        "quality_message",
        "ai_summary",
    ]:
        st.session_state.pop(key, None)


# =========================================================
# PAGE: DASHBOARD
# =========================================================

if page == "Dashboard":

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">YOUR HEALTH INFORMATION, EXPLAINED</div>
            <h1>Understand your medical report.</h1>
            <p>
                Extract laboratory results, review detected values,
                and explore an educational explanation in one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="notice">
            <strong>Medical safety notice</strong><br>
            This tool may misread reports or produce inaccurate
            explanations. It cannot diagnose or recommend treatment.
            Verify results with the original report and consult a
            qualified healthcare professional.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # UPLOAD PANEL
    # -----------------------------------------------------

    st.markdown("### 📤 Upload a report")
    st.markdown(
        '<p class="muted">Select a PDF or image to begin your analysis.</p>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose your report",
        type=["pdf", "png", "jpg", "jpeg"],
        max_upload_size=10,
        help="Supported formats: PDF, PNG, JPG and JPEG. Maximum 10 MB.",
        key="medical_report_uploader",
    )

    if uploaded_file is not None:

        file_size_mb = uploaded_file.size / (1024 * 1024)

        if file_size_mb > 10:
            st.error("This file exceeds the 10 MB upload limit.")

        else:
            st.success(
                f"File selected: {uploaded_file.name} "
                f"({file_size_mb:.2f} MB)"
            )

            if st.button(
                "Analyze Medical Report",
                type="primary",
                use_container_width=True,
            ):

                # Reset old data before a new analysis.
                clear_analysis()

                try:
                    with st.spinner("Extracting report text..."):

                        filename = uploaded_file.name.lower()
                        uploaded_file.seek(0)

                        if filename.endswith(".pdf"):
                            report_text = (
                                extract_text_from_uploaded_pdf(
                                    uploaded_file
                                )
                            )
                        else:
                            report_text = extract_text_from_image(
                                uploaded_file
                            )

                    if not report_text or not report_text.strip():
                        st.error(
                            "No readable text was found. "
                            "Try a clearer report."
                        )

                    else:
                        with st.spinner(
                            "Analyzing detected laboratory results..."
                        ):
                            raw_results = analyze_report(report_text)
                            results_df = prepare_results(raw_results)

                        quality_ok, quality_message = (
                            check_report_quality(
                                report_text,
                                results_df,
                            )
                        )

                        st.session_state["report_text"] = report_text
                        st.session_state["results_df"] = results_df
                        st.session_state["quality_ok"] = quality_ok
                        st.session_state["quality_message"] = (
                            quality_message
                        )

                        if quality_ok:
                            try:
                                with st.spinner(
                                    "Generating AI explanation..."
                                ):
                                    summary = ai_explain_report(
                                        report_text
                                    )

                                if summary:
                                    st.session_state["ai_summary"] = (
                                        summary
                                    )

                            except Exception:
                                st.warning(
                                    "The laboratory results were "
                                    "processed, but the AI explanation "
                                    "is currently unavailable."
                                )

                        st.success("Analysis completed.")

                except Exception:
                    st.error(
                        "We could not process this report. "
                        "Please try a valid, clearer file."
                    )

    # -----------------------------------------------------
    # RESULTS AREA
    # -----------------------------------------------------

    if "report_text" in st.session_state:

        st.divider()

        st.markdown("### 📊 Your report overview")

        st.info(
            st.session_state.get(
                "quality_message",
                "Review the detected report information.",
            )
        )

        results_df = st.session_state["results_df"]

        if not results_df.empty:
            show_summary_dashboard(results_df)

            st.markdown("### 🧪 Detected laboratory results")

            st.dataframe(
                results_df,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                "Detected results may be inaccurate due to OCR "
                "or parsing errors. Verify each value and reference "
                "range against the original report."
            )

        else:
            st.warning(
                "No structured laboratory results were detected."
            )

        # -------------------------------------------------
        # AI EXPLANATION
        # -------------------------------------------------

        st.divider()
        st.markdown("### 🤖 Educational explanation")

        if "ai_summary" in st.session_state:
            st.markdown(st.session_state["ai_summary"])

            st.caption(
                "AI-generated content can be incorrect. "
                "Do not use it as a substitute for professional advice."
            )
        else:
            st.info(
                "An AI explanation is not available for this report."
            )

        # -------------------------------------------------
        # DOWNLOAD SUMMARY
        # -------------------------------------------------

        st.divider()
        st.markdown("### 📥 Download your summary")

        if not results_df.empty:
            try:
                pdf_bytes = create_pdf_report(
                    results_df,
                    st.session_state.get("ai_summary", ""),
                )

                if pdf_bytes:
                    st.download_button(
                        label="Download PDF Summary",
                        data=pdf_bytes,
                        file_name="medical_report_summary.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                else:
                    st.warning("The PDF summary is empty.")

            except Exception:
                st.error(
                    "The PDF summary could not be generated. "
                    "Please try again later."
                )

        st.button(
            "Clear current analysis",
            on_click=clear_analysis,
        )


# =========================================================
# PAGE: HOW IT WORKS
# =========================================================

elif page == "How It Works":

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">SIMPLE WORKFLOW</div>
            <h1>How it works</h1>
            <p>
                From report upload to an educational summary.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    steps = [
        (
            "01",
            "Upload",
            "Choose a supported PDF or image up to 10 MB.",
        ),
        (
            "02",
            "Extract",
            "The application attempts to read report text "
            "using PDF extraction or OCR.",
        ),
        (
            "03",
            "Analyze",
            "The existing analyzer identifies supported "
            "laboratory results.",
        ),
        (
            "04",
            "Understand",
            "An AI-generated educational explanation may "
            "be provided when analysis succeeds.",
        ),
        (
            "05",
            "Download",
            "Download a PDF summary of the detected results "
            "and available explanation.",
        ),
    ]

    for number, title, description in steps:
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-title">
                    {number} &nbsp; {title}
                </div>
                <div class="muted">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "The accuracy of extraction and analysis depends on "
        "the report quality and the capabilities of the existing "
        "backend modules."
    )


# =========================================================
# PAGE: ABOUT & SAFETY
# =========================================================

elif page == "About & Safety":

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">TRANSPARENCY FIRST</div>
            <h1>About this application</h1>
            <p>
                A software project designed to make medical
                report information easier to review.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### What this application does")

    st.write(
        "It attempts to extract text from uploaded reports, "
        "organize detected laboratory values, and provide "
        "an educational AI explanation."
    )

    st.markdown("### Important limitations")

    st.markdown(
        """
        - It is not a medical diagnostic system.
        - OCR can misread numbers, decimal points, units,
          and reference ranges.
        - The analyzer may miss results or classify them incorrectly.
        - AI explanations can contain factual errors.
        - A result marked within range does not guarantee that
          a person is healthy.
        - The application does not replace a doctor or laboratory.
        """
    )

    st.markdown("### Privacy and security")

    st.warning(
        "Do not upload reports containing real patient information "
        "unless you have verified the application's privacy, "
        "security, data-handling practices, and applicable legal "
        "requirements. Uploaded text may be sent to external AI "
        "services by the existing backend."
    )

    st.markdown("### When to seek medical care")

    st.write(
        "Contact a qualified healthcare professional to interpret "
        "your results in context. For urgent symptoms or a medical "
        "emergency, seek appropriate medical care instead of relying "
        "on this application."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        MediExplain · Educational medical report assistant<br>
        Not for diagnosis, treatment, or emergency use.
    </div>
    """,
    unsafe_allow_html=True,
)
