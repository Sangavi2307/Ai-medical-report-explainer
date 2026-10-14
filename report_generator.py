
from io import BytesIO
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_pdf_report(report_name, patient_fields, results_df, summary):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("MediLens Report Summary", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Source file: {escape(str(report_name))}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Extracted Patient Details", styles["Heading2"]))

    for key, value in patient_fields.items():
        safe_value = escape(str(value or "Not extracted"))
        story.append(
            Paragraph(f"<b>{escape(str(key))}:</b> {safe_value}", styles["Normal"])
        )

    story.append(Spacer(1, 12))
    story.append(Paragraph("Laboratory Results", styles["Heading2"]))

    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        headers = list(results_df.columns)
        table_data = [headers]

        for _, row in results_df.iterrows():
            table_data.append([
                escape(str(row[column]))[:150]
                for column in headers
            ])

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#123B55")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5DFE8")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
    else:
        story.append(
            Paragraph("No supported result lines were recognized.", styles["Normal"])
        )

    story.append(Spacer(1, 12))
    story.append(Paragraph("Educational Summary", styles["Heading2"]))

    for paragraph in str(summary).split("\n\n"):
        story.append(Paragraph(escape(paragraph), styles["Normal"]))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Educational use only. This document is not a diagnosis or treatment "
        "recommendation. Consult a qualified healthcare professional.",
        styles["Italic"],
    ))

    document.build(story)
    return buffer.getvalue()
