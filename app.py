
import io
from datetime import datetime
from xml.sax.saxutils import escape

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from extractor import extract_text_from_pdf
from ocr_service import (
    extract_text_from_image,
    extract_text_from_scanned_pdf,
)
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import explain_report


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="MediLens | Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==================================================
# PROFESSIONAL UI
# ==================================================

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 5% 0%, #15354a 0%, transparent 32%),
        linear-gradient(135deg, #07111f, #0d2034 60%, #10243a);
    color: #edf5ff;
}
.block-container {
    max-width: 1250px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    color: #56e0c1 !important;
}
p, label, li {
    color: #edf5ff;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #152f46, #102338);
    border: 1px solid #2b5068;
    padding: 18px;
    border-radius: 16px;
}
[data-testid="stMetricLabel"] {
    color: #b3c8d9 !important;
}
[data-testid="stMetricValue"] {
    color: #56e0c1 !important;
}
.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(90deg, #56e0c1, #20bfa9);
    color: #07111f;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    min-height: 44px;
}
[data-testid="stFileUploader"] {
    background: #10263b;
    border: 1px dashed #3b7187;
    border-radius: 16px;
    padding: 12px;
}
div[data-testid="stExpander"] {
    background: #102338;
    border: 1px solid #2b5068;
    border-radius: 13px;
}
.medi-hero {
    background: linear-gradient(120deg, #173c50, #10243a);
    border: 1px solid #2b6575;
    border-radius: 22px;
    padding: 28px;
    margin-bottom: 22px;
}
.medi-kicker {
    color: #56e0c1;
    font-size: .78rem;
    letter-spacing: .16em;
    font-weight: 800;
}
.medi-title {
    font-size: 2.6rem;
    font-weight: 850;
    color: #f4fbff;
    margin: 5px 0;
}
.medi-sub {
    color: #c3d5e4;
    font-size: 1.05rem;
}
.medi-chip {
    display: inline-block;
    padding: 5px 10px;
    margin: 8px 5px 0 0;
    border: 1px solid #35647a;
    border-radius: 999px;
    color: #c6fff2;
    font-size: .78rem;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# HELPERS
# ==================================================

def safe_text(value, default="Not provided"):
    if value is None:
        return default

    text = str(value).strip()

    if not text or text.lower() in {"nan", "none"}:
        return default

    return text


def pdf_text(value):
    """Escape text before placing it inside a PDF paragraph."""
    return escape(safe_text(value, ""))


def normalize_status(status):
    status = str(status or "").strip().lower()

    if status in {
        "within range", "normal", "within normal range"
    }:
        return "normal"

    if status in {
        "below range", "low", "below normal"
    }:
        return "low"

    if status in {
        "above range", "high", "above normal"
    }:
        return "high"

    return "review"


def create_complete_pdf(
    file_name,
    patient_fields,
    results_df,
    explanation,
):
    """Create a downloadable PDF containing the full report analysis."""

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title="MediLens Complete Report Analysis",
        author="MediLens",
    )

    navy = colors.HexColor("#10243A")
    teal = colors.HexColor("#159E8B")
    pale = colors.HexColor("#EAF7F5")
    light = colors.HexColor("#F2F5F8")
    dark = colors.HexColor("#25384A")
    border = colors.HexColor("#CBD7E0")

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="MediTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        textColor=navy,
        alignment=TA_CENTER,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name="MediSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=dark,
        alignment=TA_CENTER,
        spaceAfter=16,
    ))

    styles.add(ParagraphStyle(
        name="MediSection",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        textColor=teal,
        spaceBefore=12,
        spaceAfter=7,
    ))

    styles.add(ParagraphStyle(
        name="MediBody",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=12,
        textColor=dark,
        spaceAfter=5,
        splitLongWords=True,
    ))

    styles.add(ParagraphStyle(
        name="MediCell",
        parent=styles["BodyText"],
        fontSize=7,
        leading=9,
        textColor=dark,
        splitLongWords=True,
    ))

    story = [
        Paragraph("MediLens", styles["MediTitle"]),
        Paragraph(
            "Complete Medical Report Analysis",
            styles["MediSubtitle"],
        ),
        Paragraph(
            f"<b>Uploaded file:</b> {pdf_text(file_name)}<br/>"
            f"<b>Generated:</b> "
            f"{datetime.now().strftime('%d %b %Y, %I:%M %p')}",
            styles["MediBody"],
        ),
        Paragraph("Important Notice", styles["MediSection"]),
        Paragraph(
            "This document provides educational explanations of extracted "
            "laboratory results. It is not a diagnosis or treatment plan. "
            "Automated extraction may make mistakes. Verify all values and "
            "reference ranges against the original medical report.",
            styles["MediBody"],
        ),
    ]

    # Patient / report information
    if patient_fields:
        story.append(
            Paragraph("Report Information", styles["MediSection"])
        )

        patient_data = [[
            Paragraph("<b>Field</b>", styles["MediCell"]),
            Paragraph("<b>Detected information</b>", styles["MediCell"]),
        ]]

        for field, value in patient_fields.items():
            patient_data.append([
                Paragraph(pdf_text(field), styles["MediCell"]),
                Paragraph(pdf_text(value), styles["MediCell"]),
            ])

        table = Table(
            patient_data,
            colWidths=[48 * mm, 120 * mm],
            repeatRows=1,
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), pale),
            ("GRID", (0, 0), (-1, -1), .4, border),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        story.append(table)

    # Summary
    story.append(
        Paragraph("Analysis Summary", styles["MediSection"])
    )

    story.append(
        Paragraph(
            pdf_text(explanation.get("summary", "Summary unavailable.")),
            styles["MediBody"],
        )
    )

    # Complete results table
    if not results_df.empty:
        story.append(
            Paragraph("Laboratory Results", styles["MediSection"])
        )

        preferred_columns = [
            "Test",
            "Result",
            "Unit",
            "Reference Range",
            "Status",
        ]

        columns = [
            column for column in preferred_columns
            if column in results_df.columns
        ]

        if not columns:
            columns = list(results_df.columns[:5])

        table_data = [[
            Paragraph(f"<b>{pdf_text(column)}</b>", styles["MediCell"])
            for column in columns
        ]]

        for _, row in results_df[columns].fillna("").iterrows():
            table_data.append([
                Paragraph(pdf_text(row[column]), styles["MediCell"])
                for column in columns
            ])

        available_width = A4[0] - 32 * mm
        column_width = available_width / max(len(columns), 1)

        table = Table(
            table_data,
            colWidths=[column_width] * len(columns),
            repeatRows=1,
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), pale),
            ("GRID", (0, 0), (-1, -1), .35, border),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        story.append(table)

    # Detailed explanation for each test
    detailed_results = explanation.get("results", [])

    if detailed_results:
        story.append(
            Paragraph("Detailed Test Explanations", styles["MediSection"])
        )

        for item in detailed_results:
            story.append(
                Paragraph(
                    pdf_text(item.get("Test", "Unknown test")),
                    styles["Heading3"],
                )
            )

            fields = [
                ("Result", item.get("Result")),
                ("Reference range", item.get("Reference Range")),
                ("Status", item.get("Status")),
                ("What it measures", item.get("Meaning")),
                ("Why it matters", item.get("Importance")),
                (
                    "Understanding the result",
                    item.get("Interpretation", item.get("Explanation")),
                ),
            ]

            for label, value in fields:
                if value is not None and str(value).strip():
                    story.append(
                        Paragraph(
                            f"<b>{label}:</b> {pdf_text(value)}",
                            styles["MediBody"],
                        )
                    )

            causes = item.get("Possible Causes", [])

            if causes:
                story.append(
                    Paragraph(
                        "<b>Possible explanations to discuss with a "
                        "healthcare professional:</b>",
                        styles["MediBody"],
                    )
                )

                for cause in causes:
                    story.append(
                        Paragraph(
                            f"&#8226; {pdf_text(cause)}",
                            styles["MediBody"],
                        )
                    )

            follow_up = item.get("Follow-up")

            if follow_up:
                story.append(
                    Paragraph(
                        f"<b>Possible follow-up:</b> {pdf_text(follow_up)}",
                        styles["MediBody"],
                    )
                )

            story.append(Spacer(1, 7))

    # General notes
    notes = explanation.get("general_notes", [])

    if notes:
        story.append(
            Paragraph("Important Notes", styles["MediSection"])
        )

        for note in notes:
            story.append(
                Paragraph(
                    f"&#8226; {pdf_text(note)}",
                    styles["MediBody"],
                )
            )

    def draw_footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(border)
        canvas.line(
            16 * mm, 13 * mm,
            A4[0] - 16 * mm, 13 * mm,
        )
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(dark)
        canvas.drawString(
            16 * mm, 8 * mm,
            "MediLens | Educational report",
        )
        canvas.drawRightString(
            A4[0] - 16 * mm, 8 * mm,
            f"Page {document.page}",
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=draw_footer,
        onLaterPages=draw_footer,
    )

    buffer.seek(0)
    return buffer.getvalue()


# ==================================================
# HEADER
# ==================================================

st.markdown("""
<div class="medi-hero">
    <div class="medi-kicker">PERSONAL HEALTH REPORT INSIGHTS</div>
    <div class="medi-title">🩺 MediLens</div>
    <div class="medi-sub">
        Turn your laboratory report into a clear, organized summary.
    </div>
    <div>
        <span class="medi-chip">PDF & image OCR</span>
        <span class="medi-chip">Lab analysis</span>
        <span class="medi-chip">Detailed explanations</span>
        <span class="medi-chip">PDF & CSV downloads</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.warning(
    "Educational use only. This application does not diagnose conditions "
    "or recommend treatment. Always verify extracted values against the "
    "original report."
)


# ==================================================
# UPLOAD
# ==================================================

st.subheader("1. Upload your medical report")

uploaded_file = st.file_uploader(
    "Choose a PDF, PNG, JPG, or JPEG file",
    type=["pdf", "png", "jpg", "jpeg"],
    key="medical_report_upload",
)

if uploaded_file is None:
    st.info("Upload a report to begin.")
    st.stop()


# ==================================================
# EXTRACT REPORT TEXT
# ==================================================

report_text = ""
results_df = pd.DataFrame()
patient_fields = {}
explanation = None

try:
    with st.spinner("Reading your uploaded report..."):
        file_name = uploaded_file.name.lower()

        if file_name.endswith(".pdf"):
            report_text = extract_text_from_pdf(uploaded_file)

            if not report_text or not report_text.strip():
                uploaded_file.seek(0)
                report_text = extract_text_from_scanned_pdf(
                    uploaded_file
                )
        else:
            report_text = extract_text_from_image(uploaded_file)

except Exception as error:
    st.error("Unable to read the uploaded file.")
    st.exception(error)
    st.stop()


if not report_text or not report_text.strip():
    st.error(
        "No readable text was found. Try a clearer image or a text-based PDF."
    )
    st.stop()

st.success(f"Report text extracted: {uploaded_file.name}")

with st.expander("Preview extracted report text"):
    st.text(report_text)


# ==================================================
# ANALYZE THE CURRENT REPORT
# ==================================================

try:
    with st.spinner("Analyzing the uploaded report..."):
        results_df = analyze_report(report_text)
        patient_fields = extract_patient_fields(report_text)

except Exception as error:
    st.error("The report was read, but analysis failed.")
    st.exception(error)
    st.stop()

if not isinstance(results_df, pd.DataFrame):
    st.error("The analyzer did not return a pandas DataFrame.")
    st.stop()


# ==================================================
# PREPARE EXPLANATIONS
# ==================================================

try:
    with st.spinner("Preparing detailed explanations..."):
        explanation = explain_report(
            report_text=report_text,
            results_df=results_df,
            patient_fields=patient_fields,
        )

except Exception as error:
    st.error("Could not prepare report explanations.")
    st.exception(error)
    st.stop()


# ==================================================
# DASHBOARD
# ==================================================

st.divider()
st.subheader("2. Analysis overview")

if "Status" in results_df.columns:
    status = results_df["Status"].astype(str).str.lower()
else:
    status = pd.Series(["unknown"] * len(results_df))

normal_count = int(
    status.isin([
        "within range", "normal", "within normal range"
    ]).sum()
)

low_count = int(
    status.isin(["below range", "low", "below normal"]).sum()
)

high_count = int(
    status.isin(["above range", "high", "above normal"]).sum()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Tests detected", len(results_df))
col2.metric("Within range", normal_count)
col3.metric("Below range", low_count)
col4.metric("Above range", high_count)

st.info(explanation.get("summary", "Summary unavailable."))


# ==================================================
# PATIENT INFORMATION
# ==================================================

with st.expander("📋 Detected report information"):
    if patient_fields:
        for field, value in patient_fields.items():
            st.write(f"**{field}:** {value}")
    else:
        st.write("Patient information was not detected.")


# ==================================================
# LAB RESULTS
# ==================================================

st.divider()
st.subheader("3. Laboratory results")

if results_df.empty:
    st.warning("No laboratory results were detected.")
else:
    search_term = st.text_input(
        "Search laboratory tests",
        placeholder="Search by test name...",
    )

    display_df = results_df.copy()

    if search_term and "Test" in display_df.columns:
        display_df = display_df[
            display_df["Test"].astype(str).str.contains(
                search_term,
                case=False,
                na=False,
            )
        ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="⬇️ Download laboratory results (CSV)",
        data=results_df.to_csv(index=False).encode("utf-8"),
        file_name="MediLens_Laboratory_Results.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if {"Test", "Result"}.issubset(results_df.columns):
        chart_df = results_df.copy()

        chart_df["Result"] = pd.to_numeric(
            chart_df["Result"]
            .astype(str)
            .str.replace(",", "", regex=False),
            errors="coerce",
        )

        chart_df = chart_df.dropna(subset=["Result"])

        if not chart_df.empty:
            st.subheader("4. Results visualization")
            st.bar_chart(chart_df.set_index("Test")[["Result"]])

            st.caption(
                "Different tests may use different units and scales. "
                "Compare each result with its own reference range."
            )


# ==================================================
# DETAILED EXPLANATIONS
# ==================================================

st.divider()
st.subheader("5. Detailed report explanations")

detailed_results = explanation.get("results", [])

if detailed_results:
    for item in detailed_results:
        test_name = safe_text(item.get("Test"), "Unknown test")
        test_status = safe_text(item.get("Status"), "Needs review")

        with st.expander(f"🔎 {test_name} · {test_status}"):
            st.markdown("#### Result details")
            st.write("**Result:**", safe_text(item.get("Result")))
            st.write(
                "**Reference range:**",
                safe_text(item.get("Reference Range")),
            )
            st.write("**Status:**", test_status)

            st.markdown("#### What this test measures")
            st.write(safe_text(item.get("Meaning")))

            if item.get("Importance"):
                st.markdown("#### Why this test matters")
                st.write(item["Importance"])

            st.markdown("#### Understanding the result")
            st.write(
                safe_text(
                    item.get(
                        "Interpretation",
                        item.get("Explanation"),
                    )
                )
            )

            causes = item.get("Possible Causes", [])

            if causes:
                st.markdown(
                    "#### Possible explanations to discuss with a clinician"
                )
                for cause in causes:
                    st.markdown(f"- {cause}")

            if item.get("Follow-up"):
                st.markdown("#### Possible follow-up")
                st.write(item["Follow-up"])

else:
    st.warning("No extracted results are available to explain.")


# ==================================================
# DOWNLOAD COMPLETE REPORT ANALYSIS
# ==================================================

st.divider()
st.subheader("6. Download complete report analysis")

st.write(
    "Export the current analysis as a formatted PDF, including detected "
    "patient information, summary counts, laboratory results, detailed "
    "explanations, possible causes, follow-up notes, and disclaimers."
)

try:
    complete_pdf = create_complete_pdf(
        file_name=uploaded_file.name,
        patient_fields=patient_fields,
        results_df=results_df,
        explanation=explanation,
    )

    st.download_button(
        label="📄 Download complete analysis as PDF",
        data=complete_pdf,
        file_name="MediLens_Complete_Report_Analysis.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

except Exception as error:
    st.error("Could not generate the complete PDF report.")
    st.exception(error)


# ==================================================
# IMPORTANT NOTES / FOOTER
# ==================================================

with st.expander("Important notes"):
    for note in explanation.get("general_notes", []):
        st.markdown(f"- {note}")

st.divider()
st.caption(
    "MediLens | Educational project | Not a substitute for professional "
    "medical advice. Verify all extracted values against the original report."
)
