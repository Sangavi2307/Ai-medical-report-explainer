
import io
import re

import pandas as pd
import streamlit as st
import pymupdf

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report
from ai_explainer import ai_explain_report

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


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
    "and receive a simple educational explanation."
)

st.info(
    "Educational purpose only. This application does not diagnose "
    "diseases or replace advice from a qualified healthcare professional."
)


# --------------------------------------------------
# PDF TEXT EXTRACTION WITH OCR FALLBACK
# --------------------------------------------------

def extract_text_from_uploaded_pdf(uploaded_file):
    """Extract selectable PDF text and use OCR if necessary."""

    uploaded_file.seek(0)
    text = extract_text_from_pdf(uploaded_file)

    if text and text.strip():
        return text.strip()

    # Scanned PDF fallback: render each page and use OCR.
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

            page_text = extract_text_from_image(image_file)

            if page_text and page_text.strip():
                extracted_pages.append(page_text.strip())
    finally:
        document.close()

    return "\n\n".join(extracted_pages)


# --------------------------------------------------
# CLEAN AND VALIDATE ANALYZER OUTPUT
# --------------------------------------------------

def prepare_results(raw_results):
    """Convert analyzer output to a consistent DataFrame."""

    if isinstance(raw_results, pd.DataFrame):
        results_df = raw_results.copy()

    elif isinstance(raw_results, list):
        results_df = pd.DataFrame(raw_results)

    else:
        return pd.DataFrame(
            columns=[
                "Test",
                "Result",
                "Unit",
                "Reference Range",
                "Status",
            ]
        )

    if results_df.empty:
        return results_df

    # Normalize column names.
    results_df.columns = [
        str(column).strip() for column in results_df.columns
    ]

    # Add missing expected columns.
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

    # Show expected columns first and retain any extra columns.
    extra_columns = [
        column
        for column in results_df.columns
        if column not in expected_columns
    ]

    results_df = results_df[
        expected_columns + extra_columns
    ]

    return results_df


# --------------------------------------------------
# SUMMARY DASHBOARD
# --------------------------------------------------

def show_summary_dashboard(results_df):
    st.subheader("📊 Medical Report Summary")

    if results_df.empty:
        st.warning(
            "No laboratory test results were detected. "
            "Please check the extracted report text."
        )
        return

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

    unclassified_count = (
        len(results_df)
        - within_count
        - below_count
        - above_count
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tests", len(results_df))
    col2.metric("Within Range", within_count)
    col3.metric("Below Range", below_count)
    col4.metric("Above Range", above_count)

    if unclassified_count > 0:
        st.caption(
            f"{unclassified_count} result(s) have an unknown or "
            "unclassified status and should be checked manually."
        )

    st.caption(
        "These counts depend on the extracted data and analyzer. "
        "An out-of-range result is not automatically a diagnosis."
    )

    # Status chart.
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
# DOWNLOADABLE PDF REPORT
# --------------------------------------------------

def create_pdf_report(results_df, ai_summary):
    """Create a downloadable PDF using ReportLab."""

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()

    story = [
        Paragraph(
            "AI Medical Report Explainer",
            styles["Title"],
        ),
        Spacer(1, 10),
        Paragraph(
            "Educational summary — not a medical diagnosis",
            styles["Normal"],
        ),
        Spacer(1, 18),
        Paragraph(
            "Extracted Laboratory Results",
            styles["Heading2"],
        ),
        Spacer(1, 8),
    ]

    table_columns = [
        "Test",
        "Result",
        "Unit",
        "Reference Range",
        "Status",
    ]

    table_data = [table_columns]

    if not results_df.empty:
        for _, row in results_df.iterrows():
            table_data.append(
                [
                    str(row.get("Test", "")),
                    str(row.get("Result", "")),
                    str(row.get("Unit", "")),
                    str(row.get("Reference Range", "")),
                    str(row.get("Status", "")),
                ]
            )

    safe_table_data = []

    for row in table_data:
        safe_table_data.append(
            [
                Paragraph(
                    str(value).replace("&", "&amp;").replace(
                        "<", "&lt;"
                    ).replace(">", "&gt;"),
                    styles["BodyText"],
                )
                for value in row
            ]
        )

    results_table = Table(
        safe_table_data,
        repeatRows=1,
        colWidths=[
            1.15 * inch,
            0.8 * inch,
            0.65 * inch,
            1.15 * inch,
            1.1 * inch,
        ],
    )

    results_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#DCEAF7"),
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(results_table)
    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "AI Explanation",
            styles["Heading2"],
        )
    )
    story.append(Spacer(1, 8))

    # Escape special HTML characters in the AI text.
    escaped_summary = (
        str(ai_summary)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )

    story.append(
        Paragraph(
            escaped_summary,
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "Important: Reference ranges may vary by laboratory. "
            "OCR or extracted text may contain errors. An abnormal "
            "result does not automatically indicate a disease. "
            "Discuss actual results with a qualified healthcare "
            "professional. Do not change medicines based on this "
            "application.",
            styles["Italic"],
        )
    )

    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    help="PDF, PNG, JPG, and JPEG files are supported.",
)


# --------------------------------------------------
# PROCESS THE UPLOADED REPORT
# --------------------------------------------------

if uploaded_file is not None:

    st.success(
        f"File uploaded: {uploaded_file.name}"
    )

    if st.button(
        "Analyze Medical Report",
        type="primary",
    ):

        with st.spinner(
            "Extracting report text..."
        ):

            try:
                if uploaded_file.name.lower().endswith(".pdf"):
                    report_text = extract_text_from_uploaded_pdf(
                        uploaded_file
                    )
                else:
                    report_text = extract_text_from_image(
                        uploaded_file
                    )

            except Exception as error:
                st.error(
                    "Unable to extract text from this file."
                )
                st.exception(error)
                st.stop()

        if not report_text or not report_text.strip():
            st.error(
                "No readable text was detected. Try a clearer "
                "image or a higher-quality PDF."
            )
            st.stop()

        # Store extracted text for review.
        st.session_state["report_text"] = report_text

        with st.spinner(
            "Analyzing laboratory results..."
        ):

            try:
                raw_results = analyze_report(report_text)
                results_df = prepare_results(raw_results)

            except Exception as error:
                st.error(
                    "The report text was extracted, but "
                    "laboratory analysis failed."
                )
                st.exception(error)
                st.stop()

        st.session_state["results_df"] = results_df

        with st.spinner(
            "Preparing the educational AI explanation..."
        ):

            try:
                ai_summary = ai_explain_report(report_text)

            except Exception as error:
                ai_summary = (
                    "The AI explanation could not be generated. "
                    "Please review the extracted results manually."
                )
                st.warning(
                    f"AI explanation unavailable: {error}"
                )

        st.session_state["ai_summary"] = ai_summary


# --------------------------------------------------
# DISPLAY ANALYSIS RESULTS
# --------------------------------------------------

if "report_text" in st.session_state:

    report_text = st.session_state["report_text"]

    results_df = st.session_state.get(
        "results_df",
        pd.DataFrame(),
    )

    ai_summary = st.session_state.get(
        "ai_summary",
        "No AI explanation is available.",
    )

    st.divider()

    with st.expander("🔍 View Extracted Report Text"):
        st.text_area(
            "Extracted text (check for OCR errors)",
            value=report_text,
            height=250,
            disabled=True,
        )

    st.subheader("🧪 Extracted Test Results")

    if not results_df.empty:
        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True,
        )

        show_summary_dashboard(results_df)

    else:
        st.warning(
            "No structured test results were detected. "
            "The extracted text is available above for review."
        )

    st.divider()

    st.subheader("🤖 AI Explanation")

    st.markdown(ai_summary)

    st.divider()

    st.subheader("📄 Download Your Report")

    try:
        pdf_bytes = create_pdf_report(
            results_df,
            ai_summary,
        )

        st.download_button(
            label="⬇️ Download Explained Report (PDF)",
            data=pdf_bytes,
            file_name="medical_report_explanation.pdf",
            mime="application/pdf",
        )

    except Exception as error:
        st.error(
            "Unable to generate the downloadable PDF."
        )
        st.exception(error)

    st.caption(
        "Privacy reminder: Upload only reports you are authorized "
        "to use. Review the extracted values carefully before "
        "relying on the explanation."
    )
