

import io

import pandas as pd
import pymupdf
import streamlit as st

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from report_generator import create_pdf_report


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
)

st.title("🩺 AI Medical Report Explainer")

st.write(
    "Upload a medical report to extract text, review "
    "detected laboratory results, and receive an "
    "educational explanation."
)

st.info(
    "Educational use only. This application does not "
    "provide a medical diagnosis or treatment. "
    "Always consult a qualified healthcare professional."
)


# --------------------------------------------------
# PDF TEXT EXTRACTION WITH OCR FALLBACK
# --------------------------------------------------

def extract_text_from_uploaded_pdf(uploaded_file):
    """Extract PDF text, using OCR if selectable text is absent."""

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


# --------------------------------------------------
# STANDARDIZE ANALYSIS RESULTS
# --------------------------------------------------

def prepare_results(results):
    """Convert analyzer output into a consistent DataFrame."""

    if isinstance(results, pd.DataFrame):
        results_df = results.copy()

    elif isinstance(results, list):
        results_df = pd.DataFrame(results)

    else:
        results_df = pd.DataFrame()

    if results_df.empty:
        return pd.DataFrame(
            columns=[
                "Test",
                "Result",
                "Unit",
                "Reference Range",
                "Status",
            ]
        )

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

    expected_columns = [
        "Test",
        "Result",
        "Unit",
        "Reference Range",
        "Status",
    ]

    for column in expected_columns:
        if column not in results_df.columns:
            results_df[column] = ""

    return results_df[expected_columns]


# --------------------------------------------------
# REPORT QUALITY CHECK
# --------------------------------------------------

def check_report_quality(report_text, results_df):
    """Check whether readable text and results were detected."""

    if not report_text or not report_text.strip():
        return False, (
            "No readable text was extracted. "
            "Try a clearer PDF or image."
        )

    if results_df.empty:
        return False, (
            "Text was extracted, but no supported laboratory "
            "results were detected. Review the extracted text "
            "or try a clearer report."
        )

    return True, "Report text and laboratory results detected."


# --------------------------------------------------
# SUMMARY DASHBOARD
# --------------------------------------------------

def show_summary_dashboard(results_df):
    """Display counts of detected result statuses."""

    st.subheader("📊 Results Summary")

    if results_df.empty:
        st.warning("No structured results are available.")
        return

    status_values = (
        results_df["Status"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    normal_count = status_values.str.contains(
        r"within range|normal",
        regex=True,
    ).sum()

    low_count = status_values.str.contains(
        r"below|low",
        regex=True,
    ).sum()

    high_count = status_values.str.contains(
        r"above|high",
        regex=True,
    ).sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Tests detected", len(results_df))
    col2.metric("Within range", int(normal_count))
    col3.metric("Below range", int(low_count))
    col4.metric("Above range", int(high_count))

    chart_data = pd.DataFrame(
        {
            "Category": [
                "Within range",
                "Below range",
                "Above range",
            ],
            "Count": [
                int(normal_count),
                int(low_count),
                int(high_count),
            ],
        }
    )

    st.bar_chart(chart_data.set_index("Category"))


# --------------------------------------------------
# FILE UPLOAD — MAXIMUM 10 MB
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    help=(
        "Supported formats: PDF, PNG, JPG, JPEG. "
        "Maximum size: 10 MB."
    ),
    max_upload_size=10,
)


# --------------------------------------------------
# PROCESS UPLOADED REPORT
# --------------------------------------------------

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("Analyze Medical Report", type="primary"):

        try:
            with st.spinner("Extracting report text..."):

                file_name = uploaded_file.name.lower()

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
                    "Please upload a clearer report."
                )
                st.stop()

            with st.spinner("Analyzing laboratory results..."):
                raw_results = analyze_report(report_text)
                results_df = prepare_results(raw_results)

            quality_ok, quality_message = check_report_quality(
                report_text,
                results_df,
            )

            st.session_state["report_text"] = report_text
            st.session_state["results_df"] = results_df
            st.session_state["quality_ok"] = quality_ok
            st.session_state["quality_message"] = quality_message

            # Clear the previous explanation.
            st.session_state.pop("ai_summary", None)

            if quality_ok:
                with st.spinner("Generating AI explanation..."):
                    ai_summary = ai_explain_report(report_text)

                st.session_state["ai_summary"] = ai_summary

            st.success("Report processing completed.")

        except Exception:
            st.error(
                "Unable to process this report. "
                "Please check the file and try again. "
                "If the problem continues, try another file."
            )


# --------------------------------------------------
# DISPLAY ANALYSIS
# --------------------------------------------------

if "report_text" in st.session_state:

    st.divider()

    with st.expander("📄 View Extracted Report Text"):
        st.text(st.session_state["report_text"])

    results_df = st.session_state["results_df"]

    st.subheader("🧪 Detected Laboratory Results")

    if not results_df.empty:

        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True,
        )

        show_summary_dashboard(results_df)

    else:
        st.warning(
            st.session_state.get(
                "quality_message",
                "No structured laboratory results were detected.",
            )
        )

    # --------------------------------------------------
    # AI EXPLANATION
    # --------------------------------------------------

    st.divider()
    st.subheader("🤖 AI Explanation")

    if "ai_summary" in st.session_state:
        st.markdown(st.session_state["ai_summary"])
    else:
        st.info(
            "An AI explanation was not generated because "
            "the report did not pass the quality check, "
            "or the explanation could not be generated."
        )

    # --------------------------------------------------
    # PDF DOWNLOAD
    # --------------------------------------------------

    st.divider()
    st.subheader("📥 Download Report")

    if not results_df.empty:

        try:
            pdf_bytes = create_pdf_report(
                results_df,
                st.session_state.get("ai_summary", ""),
            )

            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name="medical_report_summary.pdf",
                mime="application/pdf",
            )

        except Exception:
            st.error(
                "Unable to generate the PDF report. "
                "Please try again later."
            )

    else:
        st.caption(
            "The PDF summary requires detected structured results."
        )

