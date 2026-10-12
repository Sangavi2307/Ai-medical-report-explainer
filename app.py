
import io
import re

import pandas as pd
import pymupdf
import streamlit as st

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from report_generator import create_pdf_report


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .hero {
        padding: 1.5rem;
        border-radius: 16px;
        background: linear-gradient(120deg, #e8f4ff, #f4f0ff);
        margin-bottom: 1.2rem;
    }

    .hero h1 {
        color: #173b65;
        margin-bottom: 0.4rem;
    }

    .hero p {
        color: #334155;
        margin-bottom: 0;
    }

    .safety-note {
        padding: 0.9rem 1rem;
        border-left: 4px solid #e6a23c;
        background: #fff8e8;
        border-radius: 6px;
        color: #59421a;
        margin-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# 2. SIDEBAR
# ==================================================

with st.sidebar:
    st.title("🩺 Report Assistant")
    st.caption("AI-powered educational report summaries")

    st.divider()

    st.markdown("### How to use")
    st.markdown(
        """
        1. Upload a report.
        2. Select **Analyze Report**.
        3. Review detected results.
        4. Read the educational explanation.
        5. Download a PDF summary.
        """
    )

    st.divider()

    st.markdown("### Supported files")
    st.write("PDF, PNG, JPG and JPEG")

    st.markdown("### Upload limit")
    st.write("10 MB per file")

    st.divider()

    st.caption(
        "Use fictional or de-identified reports while testing. "
        "Do not upload private patient information."
    )


# ==================================================
# 3. APPLICATION HEADER
# ==================================================

st.markdown(
    """
    <div class="hero">
        <h1>🩺 AI Medical Report Explainer</h1>
        <p>
            Understand detected laboratory results through
            readable summaries and educational explanations.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="safety-note">
        <strong>Important medical notice:</strong>
        This application is for educational purposes only.
        It cannot diagnose diseases, recommend treatment,
        or replace a qualified healthcare professional.
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# 4. SESSION RESET
# ==================================================

if st.button("🗑️ Clear current analysis"):
    for key in [
        "report_text",
        "results_df",
        "quality_ok",
        "quality_message",
        "ai_summary",
    ]:
        st.session_state.pop(key, None)

    st.rerun()


# ==================================================
# 5. PDF TEXT EXTRACTION WITH OCR FALLBACK
# ==================================================

def extract_text_from_uploaded_pdf(uploaded_file):
    """Extract PDF text and use OCR if selectable text is absent."""

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


# ==================================================
# 6. STANDARDIZE LABORATORY RESULTS
# ==================================================

def prepare_results(results):
    """Convert analyzer output into a consistent table."""

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


# ==================================================
# 7. REPORT QUALITY CHECK
# ==================================================

def check_report_quality(report_text, results_df):
    """Check whether readable text and results were detected."""

    if not report_text or not report_text.strip():
        return False, (
            "No readable text was extracted. "
            "Try a clearer image or PDF."
        )

    if results_df.empty:
        return False, (
            "Text was extracted, but no supported laboratory "
            "results were detected. Review the extracted text."
        )

    return True, "Text and laboratory results were detected."


# ==================================================
# 8. RESULTS DASHBOARD
# ==================================================

def show_summary_dashboard(results_df):
    """Display detected status counts and a chart."""

    if results_df.empty:
        st.warning("No structured laboratory results are available.")
        return

    status_values = (
        results_df["Status"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    normal_count = int(
        status_values.str.contains(
            r"within range|normal",
            regex=True,
        ).sum()
    )

    low_count = int(
        status_values.str.contains(
            r"below|low",
            regex=True,
        ).sum()
    )

    high_count = int(
        status_values.str.contains(
            r"above|high",
            regex=True,
        ).sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Tests detected", len(results_df))
    col2.metric("Within range", normal_count)
    col3.metric("Below range", low_count)
    col4.metric("Above range", high_count)

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

    st.markdown("#### Detected result status")
    st.bar_chart(chart_data.set_index("Category"))


# ==================================================
# 9. FILE UPLOAD
# ==================================================

st.subheader("📤 Upload your report")

uploaded_file = st.file_uploader(
    "Choose a medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    max_upload_size=10,
    help="PDF, PNG, JPG or JPEG. Maximum size: 10 MB.",
    key="medical_report_uploader",
)

if uploaded_file is not None:

    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb > 10:
        st.error("The file exceeds the 10 MB limit.")

    else:
        st.success(
            f"File selected: {uploaded_file.name} "
            f"({file_size_mb:.2f} MB)"
        )

        st.caption(
            "Only upload reports you are authorized to process."
        )

        analyze_button = st.button(
            "🔍 Analyze Report",
            type="primary",
            use_container_width=True,
        )

        if analyze_button:

            # ------------------------------------------
            # Extract text
            # ------------------------------------------

            try:
                with st.spinner("Extracting report text..."):

                    file_name = uploaded_file.name.lower()
                    uploaded_file.seek(0)

                    if file_name.endswith(".pdf"):
                        report_text = extract_text_from_uploaded_pdf(
                            uploaded_file
                        )
                    else:
                        report_text = extract_text_from_image(
                            uploaded_file
                        )

                if not report_text or not report_text.strip():
                    st.error(
                        "No readable text was found. "
                        "Please try a clearer report."
                    )

                else:

                    # ----------------------------------
                    # Analyze detected results
                    # ----------------------------------

                    with st.spinner(
                        "Analyzing laboratory results..."
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

                    # Remove the previous AI explanation.
                    st.session_state.pop("ai_summary", None)

                    # ----------------------------------
                    # Generate educational explanation
                    # ----------------------------------

                    if quality_ok:
                        try:
                            with st.spinner(
                                "Generating educational explanation..."
                            ):
                                ai_summary = ai_explain_report(
                                    report_text
                                )

                            if ai_summary:
                                st.session_state["ai_summary"] = (
                                    ai_summary
                                )
                            else:
                                st.warning(
                                    "No AI explanation was returned."
                                )

                        except Exception:
                            st.warning(
                                "The report was analyzed, but the "
                                "AI explanation could not be generated. "
                                "Please try again later."
                            )

                    st.success("Report analysis completed.")

            except Exception:
                st.error(
                    "Unable to process this file. Check the file "
                    "and try again with a valid report."
                )


# ==================================================
# 10. DISPLAY ANALYSIS
# ==================================================

if "report_text" in st.session_state:

    st.divider()

    st.subheader("📋 Analysis Results")

    quality_message = st.session_state.get(
        "quality_message",
        "",
    )

    st.info(quality_message)

    with st.expander("📄 View extracted report text"):
        st.text(st.session_state["report_text"])

    results_df = st.session_state["results_df"]

    st.markdown("### 🧪 Detected Laboratory Results")

    if not results_df.empty:

        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True,
        )

        show_summary_dashboard(results_df)

        st.caption(
            "Detected values and statuses may be incorrect if "
            "the report was scanned poorly or parsed incorrectly. "
            "Verify all results against the original report."
        )

    else:
        st.warning(
            "No structured laboratory results were detected."
        )

    # ----------------------------------------------
    # AI explanation
    # ----------------------------------------------

    st.divider()
    st.subheader("🤖 Educational AI Explanation")

    if "ai_summary" in st.session_state:
        st.markdown(st.session_state["ai_summary"])

        st.caption(
            "AI-generated explanations can contain errors. "
            "Do not use them to make medical decisions."
        )

    else:
        st.info(
            "An AI explanation is not available for this report."
        )

    # ----------------------------------------------
    # PDF summary download
    # ----------------------------------------------

    st.divider()
    st.subheader("📥 Download Summary")

    if not results_df.empty:

        try:
            pdf_bytes = create_pdf_report(
                results_df,
                st.session_state.get("ai_summary", ""),
            )

            if pdf_bytes:
                st.download_button(
                    label="⬇️ Download PDF Summary",
                    data=pdf_bytes,
                    file_name="medical_report_summary.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.warning(
                    "The PDF generator returned an empty result."
                )

        except Exception:
            st.error(
                "Unable to generate the PDF summary. "
                "Please try again later."
            )

    else:
        st.caption(
            "A PDF summary requires detected structured results."
        )


# ==================================================
# 11. FOOTER
# ==================================================

st.divider()

st.caption(
    "AI Medical Report Explainer | Educational use only | "
    "Not a substitute for professional medical advice."
)
