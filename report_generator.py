
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

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    story = [
        Paragraph("MediLens - Medical Report Summary", styles["Title"]),
        Spacer(1, 8),
        Paragraph("Source file: " + escape(str(report_name)), styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Extracted Patient Details", styles["Heading2"]),
    ]

    for key, value in patient_fields.items():
        story.append(
            Paragraph(
                f"<b>{escape(str(key))}:</b> "
                f"{escape(str(value or 'Not extracted'))}",
                styles["Normal"],
            )
        )

    story.extend([
        Spacer(1, 12),
        Paragraph("Laboratory Results", styles["Heading2"]),
    ])

    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        data = [list(results_df.columns)]

        for _, row in results_df.iterrows():
            data.append([
                escape(str(value))[:120]
                for value in row.tolist()
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#123B55")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCD6DF")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(table)
    else:
        story.append(
            Paragraph("No supported results were recognized.", styles["Normal"])
        )

    story.extend([
        Spacer(1, 14),
        Paragraph("Educational Explanation", styles["Heading2"]),
    ])

    for paragraph in str(summary).split("\n\n"):
        safe_paragraph = escape(paragraph).replace("\n", "<br/>")
        story.append(Paragraph(safe_paragraph, styles["Normal"]))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Educational use only. Not a diagnosis or treatment recommendation. "
        "Consult a qualified healthcare professional.",
        styles["Italic"],
    ))

    doc.build(story)
    return buffer.getvalue()
