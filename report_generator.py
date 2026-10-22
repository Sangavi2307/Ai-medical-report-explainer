
from io import BytesIO
from xml.sax.saxutils import escape

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)

# --------------------------------------------------
# MEDILENS BRAND COLORS
# --------------------------------------------------

NAVY = colors.HexColor("#14283F")
TEAL = colors.HexColor("#087E8B")
LIGHT_TEAL = colors.HexColor("#EAF6F6")
LIGHT_GREY = colors.HexColor("#F3F6F9")
DARK_GREY = colors.HexColor("#526173")
BORDER = colors.HexColor("#DCE4EB")
WHITE = colors.white


def safe_text(value):
    """Safely convert values into PDF-compatible text."""
    if value is None:
        return ""

    if isinstance(value, float) and pd.isna(value):
        return ""

    if isinstance(value, (dict, list, tuple)):
        return format_summary(value)

    return escape(str(value)).replace("\n", "<br/>")


def format_summary(value, level=0):
    """
    Convert dictionaries, lists and ordinary text into
    readable paragraphs instead of raw Python objects.
    """
    parts = []

    if isinstance(value, dict):
        for key, item in value.items():
            if item is None or item == "":
                continue

            heading = escape(str(key).replace("_", " ").title())

            if isinstance(item, dict):
                parts.append(
                    f"<b>{heading}</b>"
                )
                parts.append(format_summary(item, level + 1))

            elif isinstance(item, (list, tuple)):
                parts.append(f"<b>{heading}</b>")
                parts.append(format_summary(item, level + 1))

            else:
                parts.append(
                    f"<b>{heading}:</b> {safe_text(item)}"
                )

    elif isinstance(value, (list, tuple)):
        for item in value:
            if item is None or item == "":
                continue

            if isinstance(item, (dict, list, tuple)):
                parts.append(format_summary(item, level + 1))
            else:
                parts.append(
                    f"&bull;&nbsp; {safe_text(item)}"
                )

    else:
        text = str(value).strip()

        if text:
            # Preserve paragraph breaks from plain-text summaries.
            for block in text.split("\n\n"):
                block = block.strip()
                if block:
                    parts.append(
                        escape(block).replace("\n", "<br/>")
                    )

    return "<br/><br/>".join(parts)


def generate_pdf_report(
    report_name,
    patient_fields,
    results_df,
    summary,
):
    """Generate a professionally formatted MediLens PDF report."""

    output = BytesIO()

    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=16 * mm,
        bottomMargin=17 * mm,
        title="MediLens Medical Report",
        author="MediLens",
    )

    # --------------------------------------------------
    # TEXT STYLES
    # --------------------------------------------------

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="BrandTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=30,
        textColor=TEAL,
        alignment=TA_LEFT,
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        name="BrandSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=DARK_GREY,
        spaceAfter=5,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=NAVY,
        spaceBefore=12,
        spaceAfter=7,
        keepWithNext=True,
    ))

    styles.add(ParagraphStyle(
        name="BodyCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=NAVY,
        spaceAfter=4,
        wordWrap="LTR",
    ))

    styles.add(ParagraphStyle(
        name="TableCell",
        parent=styles["BodyText"],
        fontSize=7.5,
        leading=10,
        textColor=NAVY,
        wordWrap="LTR",
    ))

    styles.add(ParagraphStyle(
        name="TableHeader",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=WHITE,
        wordWrap="LTR",
    ))

    styles.add(ParagraphStyle(
        name="SmallNote",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=DARK_GREY,
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        name="Disclaimer",
        parent=styles["BodyText"],
        fontSize=8,
        leading=12,
        textColor=NAVY,
    ))

    story = []

    # --------------------------------------------------
    # REPORT HEADER
    # --------------------------------------------------

    report_title = escape(
        str(report_name or "Uploaded medical report")
    )

    header = Table(
        [[
            [
                Paragraph("MediLens", styles["BrandTitle"]),
                Paragraph(
                    "AI-POWERED MEDICAL REPORT INTELLIGENCE",
                    styles["BrandSubtitle"],
                ),
            ],
            Paragraph(
                "<b>REPORT</b><br/>"
                "Extracted findings",
                styles["SmallNote"],
            ),
        ]],
        colWidths=[125 * mm, 55 * mm],
    )

    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
        ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(header)
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "Medical Report Summary",
        styles["SectionHeading"],
    ))

    story.append(Paragraph(
        f"<b>Source report:</b> {report_title}",
        styles["BodyCustom"],
    ))

    story.append(Paragraph(
        "This document summarizes information extracted from "
        "the uploaded report. Extraction accuracy depends on "
        "the quality and readability of the source.",
        styles["SmallNote"],
    ))

    story.append(HRFlowable(
        width="100%",
        thickness=0.8,
        color=BORDER,
        spaceBefore=4,
        spaceAfter=5,
    ))

    # --------------------------------------------------
    # PATIENT DETAILS
    # --------------------------------------------------

    if isinstance(patient_fields, dict) and patient_fields:
        story.append(Paragraph(
            "Patient Details",
            styles["SectionHeading"],
        ))

        patient_data = []

        for key, value in patient_fields.items():
            if value is None or not str(value).strip():
                continue

            patient_data.append([
                Paragraph(
                    f"<b>{escape(str(key))}</b>",
                    styles["TableCell"],
                ),
                Paragraph(
                    safe_text(value),
                    styles["TableCell"],
                ),
            ])

        if patient_data:
            patient_table = Table(
                patient_data,
                colWidths=[48 * mm, 132 * mm],
                hAlign="LEFT",
            )

            patient_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_GREY),
                ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))

            story.append(patient_table)

    # --------------------------------------------------
    # LABORATORY RESULTS
    # --------------------------------------------------

    story.append(Paragraph(
        "Laboratory Results",
        styles["SectionHeading"],
    ))

    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        columns = [
            "Test",
            "Result",
            "Unit",
            "Reference Range",
            "Status",
        ]

        # Include only columns available in the DataFrame.
        available = [
            col for col in columns if col in results_df.columns
        ]

        table_data = [[
            Paragraph(escape(col), styles["TableHeader"])
            for col in available
        ]]

        for _, row in results_df.iterrows():
            row_data = []

            for col in available:
                value = row.get(col, "")

                if value is None or (
                    isinstance(value, float) and pd.isna(value)
                ):
                    value = ""

                row_data.append(
                    Paragraph(safe_text(value), styles["TableCell"])
                )

            table_data.append(row_data)

        # Total table width: 180 mm, matching A4 content width.
        widths_by_column = {
            "Test": 39 * mm,
            "Result": 23 * mm,
            "Unit": 25 * mm,
            "Reference Range": 45 * mm,
            "Status": 48 * mm,
        }

        result_table = Table(
            table_data,
            colWidths=[
                widths_by_column[col] for col in available
            ],
            repeatRows=1,
            hAlign="LEFT",
        )

        table_style = [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]

        for row_number in range(1, len(table_data)):
            table_style.append((
                "BACKGROUND",
                (0, row_number),
                (-1, row_number),
                WHITE if row_number % 2 else LIGHT_GREY,
            ))

        if "Status" in available:
            status_col = available.index("Status")

            for row_number, (_, row) in enumerate(
                results_df.iterrows(), start=1
            ):
                status = str(row.get("Status", "")).lower()

                if status == "within range":
                    bg = colors.HexColor("#E8F6ED")
                elif status in ("below range", "above range"):
                    bg = colors.HexColor("#FFF0E8")
                else:
                    bg = colors.HexColor("#FFF7DD")

                table_style.append((
                    "BACKGROUND",
                    (status_col, row_number),
                    (status_col, row_number),
                    bg,
                ))

        result_table.setStyle(TableStyle(table_style))
        story.append(result_table)

        story.append(Spacer(1, 6))

        story.append(Paragraph(
            "Status labels are based on the extracted values and "
            "reference ranges. Results marked 'Needs review' or "
            "values that appear inconsistent must be checked against "
            "the original laboratory report.",
            styles["SmallNote"],
        ))

    else:
        story.append(Paragraph(
            "No laboratory results could be reliably extracted. "
            "Please review the original report or upload a clearer copy.",
            styles["BodyCustom"],
        ))

    # --------------------------------------------------
    # CLINICAL / AI SUMMARY
    # --------------------------------------------------

    story.append(Paragraph(
        "Report Explanation",
        styles["SectionHeading"],
    ))

    if isinstance(summary, dict):
        # Render known sections first, followed by any remaining fields.
        preferred_order = [
            "summary",
            "results",
            "general_notes",
            "patient",
        ]

        ordered_keys = [
            key for key in preferred_order if key in summary
        ]

        ordered_keys += [
            key for key in summary if key not in ordered_keys
        ]

        for key in ordered_keys:
            value = summary.get(key)

            if value is None or value == "":
                continue

            heading = escape(str(key).replace("_", " ").title())

            if isinstance(value, dict):
                story.append(Paragraph(
                    heading,
                    styles["SectionHeading"],
                ))

                for subkey, subvalue in value.items():
                    if subvalue is None or subvalue == "":
                        continue

                    story.append(Paragraph(
                        f"<b>{escape(str(subkey).replace('_', ' ').title())}:</b> "
                        f"{safe_text(subvalue)}",
                        styles["BodyCustom"],
                    ))

            elif isinstance(value, (list, tuple)):
                story.append(Paragraph(
                    heading,
                    styles["SectionHeading"],
                ))

                for item in value:
                    if item is None or item == "":
                        continue

                    story.append(Paragraph(
                        f"&bull;&nbsp; {safe_text(item)}",
                        styles["BodyCustom"],
                    ))

            else:
                story.append(Paragraph(
                    heading,
                    styles["SectionHeading"],
                ))

                story.append(Paragraph(
                    safe_text(value),
                    styles["BodyCustom"],
                ))

    else:
        summary_text = str(summary or "").strip()

        if summary_text:
            for block in summary_text.split("\n\n"):
                block = block.strip()

                if block:
                    story.append(Paragraph(
                        safe_text(block),
                        styles["BodyCustom"],
                    ))
        else:
            story.append(Paragraph(
                "No additional explanation was provided.",
                styles["BodyCustom"],
            ))

    # --------------------------------------------------
    # DISCLAIMER
    # --------------------------------------------------

    story.append(Spacer(1, 12))

    disclaimer = Table(
        [[
            Paragraph(
                "<b>Medical Disclaimer</b><br/>"
                "This report is an AI-assisted summary of extracted "
                "information and is not a confirmed medical diagnosis. "
                "OCR and automated interpretation may contain errors. "
                "Verify all results with the original report and consult "
                "a qualified healthcare professional for clinical "
                "interpretation and treatment decisions.",
                styles["Disclaimer"],
            )
        ]],
        colWidths=[180 * mm],
    )

    disclaimer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_TEAL),
        ("BOX", (0, 0), (-1, -1), 0.6, TEAL),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(disclaimer)

    def draw_footer(canvas, document):
        canvas.saveState()

        canvas.setStrokeColor(BORDER)
        canvas.line(
            15 * mm,
            12 * mm,
            A4[0] - 15 * mm,
            12 * mm,
        )

        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(DARK_GREY)

        canvas.drawString(
            15 * mm,
            7 * mm,
            "MediLens | Medical Report Intelligence",
        )

        canvas.drawRightString(
            A4[0] - 15 * mm,
            7 * mm,
            f"Page {document.page}",
        )

        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=draw_footer,
        onLaterPages=draw_footer,
    )

    return output.getvalue()
