
import io
import html

import pandas as pd
import streamlit as st
import pymupdf

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from report_generator import generate_pdf_report


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
    "Upload a medical laboratory report to extract test results "
    "and understand them in simple language."
)

st.info(
    "Educational use only. This application does not diagnose "
    "diseases, prescribe treatment, or replace a healthcare professional."
)


# --------------------------------------------------
# EXTRACT TEXT FROM PDF, INCLUDING SCANNED PDFs
# --------------------------------------------------

def extract_text_from_uploaded_pdf(uploaded_file):
    """Extract selectable text and use OCR if the PDF is scanned."""

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

    pages_text = []

    try:
        for page in document:
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False,
            )

            image_file = io.BytesIO(
                pixmap.tobytes("png")
            )

            page_text = extract_text_from_image(image_file)

            if page_text and page_text.strip():
                pages_text.append(page_text.strip())
    finally:
        document.close()

    return "\n\n".join(pages_text)


# --------------------------------------------------
# STANDARDIZE ANALYZER OUTPUT
# --------------------------------------------------

def prepare_results(raw_results):
    """Ensure results have the expected columns."""

    columns = [
        "Test",
        "Result",
        "Unit",
        "Reference Range",
        "Status",
    ]

    if isinstance(raw_results, pd.DataFrame):
        results_df = raw_results.copy()
    elif isinstance(raw_results, list):
        results_df = pd.DataFrame(raw_results)
    else:
        results_df = pd.DataFrame()

    if results_df.empty:
        return pd.DataFrame(columns=columns)

    results_df.columns = [
        str(column).strip()
        for column in results_df.columns
    ]

    for column in columns:
        if column not in results_df.columns:
            results_df[column] = ""

    return results_df[columns]


# --------------------------------------------------
# REPORT QUALITY CHECK
# --------------------------------------------------

def check_report_quality(report_text, results_df):
    """Check whether usable report text and test results exist."""

    if not report_text or not report_text.strip():
        st.error(
            "No readable text was extracted. "
            "Try a clearer image or a different PDF."
        )
        return False

    st.success(
        f"Extracted {len(report_text)} characters of report text."
    )

    if results_df.empty:
        st.warning(
            "No supported laboratory results were detected. "
            "Review the extracted text or upload a clearer report."
        )
        return False

    missing_values = (
        results_df["Result"].astype(str).str.strip().eq("")
        | results_df["Reference Range"].astype(str).str.strip().eq("")
    )

    if missing_values.any():
        st.warning(
            "Some detected tests have missing results or reference "
            "ranges. Review those entries carefully."
        )

    st.info(
        "Extraction quality checks cannot guarantee accuracy. "
        "Compare the extracted values with the original report."
    )

    return True


# --------------------------------------------------
# SUMMARY DASHBOARD
# --------------------------------------------------

def show_summary_dashboard(results_df):
    st.subheader("📊 Medical Report Summary")

    statuses = (
        results_df["Status"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    within_count = int(
        statuses.str.contains(
            r"within\s*range|normal",
            regex=True,
            na=False,
        ).sum()
    )

    below_count = int(
        statuses.str.contains(
            r"below|low",
            regex=True,
            na=False,
        ).sum()
    )

    above_count = int(
        statuses.str.contains(
            r"above|high",
            regex=True,
            na=False,
        ).sum()
    )

    classified_count = (
        within_count + below_count + above_count
    )

    unclassified_count = (
        len(results_df) - classified_count
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tests", len(results_df))
    col2.metric("Within Range", within_count)
    col3.metric("Below Range", below_count)
    col4.metric("Above Range", above_count)

    if unclassified_count:
        st.caption(
            f"{unclassified_count} test(s) have an unclassified "
            "status. Check these results manually."
        )

    st.caption(
        "Counts reflect the analyzer's extracted classifications, "
        "not a medical diagnosis."
    )

    chart_data = pd.DataFrame(
        {
            "Category": [
                "Within Range",
                "Below Range",
                "Above Range",
                "Unclassified",
            ],
            "Count": [
                within_count,
                below_count,
                above_count,
                unclassified_count,
            ],
        }
    )

    chart_data = chart_data[
        chart_data["Count"] > 0
    ]

    if not chart_data.empty:
        st.bar_chart(
            chart_data.set_index("Category")
        )


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    help="Supported formats: PDF, PNG, JPG, and JPEG.",
)


# --------------------------------------------------
# PROCESS REPORT
# --------------------------------------------------

if uploaded_file is not None:

    st.write(f"Selected file: **{uploaded_file.name}**")

    if st.button(
        "Analyze Medical Report",
        type="primary",
    ):

        # Clear previous report results.
        for key in [
            "report_text",
            "results_df",
            "ai_summary",
            "report_name",
        ]:
            st.session_state.pop(key, None)

        with st.spinner("Extracting report text..."):
            try:
                if uploaded_file.name.lower().endswith(".pdf"):
                    report_text = extract_text_from_uploaded_pdf(
                        uploaded_file
                    )
                else:
                    report_text = extract_text_from_image(
                        uploaded_file
                    )

            except Exception:
                st.error(
                    "Text extraction failed. Check the file format "
                    "and OCR configuration, then try again."
                )
                st.stop()

        if not report_text or not report_text.strip():
            st.error(
                "No readable text was detected. "
                "Please try a clearer report."
            )
            st.stop()

        with st.spinner("Analyzing laboratory results..."):
            try:
                raw_results = analyze_report(report_text)
                results_df = prepare_results(raw_results)

            except Exception:
                st.error(
                    "Laboratory analysis failed. "
                    "Please check analyzer.py and the application logs."
                )
                st.stop()

        # Save report data.
        st.session_state["report_text"] = report_text
        st.session_state["results_df"] = results_df
        st.session_state["report_name"] = uploaded_file.name

        # Quality check before requesting an AI explanation.
        quality_ok = check_report_quality(
            report_text,
            results_df,
        )

        if quality_ok:
            with st.spinner("Generating AI explanation..."):
                try:
                    ai_summary = ai_explain_report(
                        report_text
                    )

                    if not ai_summary:
                        ai_summary = (
                            "The AI explanation is unavailable. "
                            "Please review the extracted values "
                            "with a healthcare professional."
                        )

                except Exception:
                    ai_summary = (
                        "The AI explanation could not be generated. "
                        "Please review the extracted values manually."
                    )

            st.session_state["ai_summary"] = ai_summary

        else:
            st.session_state["ai_summary"] = (
                "An AI explanation was not generated because "
                "the report did not pass the basic quality check."
            )


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

if "report_text" in st.session_state:

    report_text = st.session_state["report_text"]

    results_df = st.session_state["results_df"]

    ai_summary = st.session_state.get(
        "ai_summary",
        "No explanation is available.",
    )

    report_name = st.session_state.get(
        "report_name",
        "medical_report",
    )

    st.divider()

    with st.expander("🔍 Review Extracted Report Text"):
        st.text_area(
            "Extracted text — check for OCR errors",
            value=report_text,
            height=250,
            disabled=True,
        )

    st.subheader("🧪 Laboratory Test Results")

    if not results_df.empty:

        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True,
        )

        show_summary_dashboard(results_df)

        st.divider()

        st.subheader("🤖 AI Explanation")
        st.markdown(ai_summary)

        st.divider()

        st.subheader("📄 Download Explained Report")

        try:
            # This assumes your existing report_generator.py
            # defines generate_pdf_report(results_df, ai_summary).
            pdf_bytes = generate_pdf_report(
                results_df,
                ai_summary,
            )

            if hasattr(pdf_bytes, "getvalue"):
                pdf_bytes = pdf_bytes.getvalue()

            safe_name = (
                report_name.rsplit(".", 1)[0]
                .replace(" ", "_")
            )

            st.download_button(
                label="⬇️ Download Explained Report (PDF)",
                data=pdf_bytes,
                file_name=f"{safe_name}_explanation.pdf",
                mime="application/pdf",
            )

        except Exception:
            st.warning(
                "PDF generation failed. Check the function name "
                "and return value in report_generator.py."
            )

    else:
        st.warning(
            "No structured laboratory results were detected. "
            "Review the extracted text before continuing."
        )

    st.caption(
        "Medical safety: Results can be misread during extraction. "
        "Reference ranges vary by laboratory. An abnormal result "
        "does not automatically indicate disease. Discuss actual "
        "results with a qualified healthcare professional."
    )
