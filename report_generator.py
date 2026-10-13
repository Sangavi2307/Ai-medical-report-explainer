
from io import BytesIO
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_pdf_report(report_text, results_df=None, ai_explanation=""):
    output = BytesIO()

    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    story = [
        Paragraph("AI Medical Report Explainer", styles["Title"]),
        Spacer(1, 5 * mm),
        Paragraph(
            "Educational summary only. Not a diagnosis or a substitute "
            "for professional medical advice.",
            styles["Normal"],
        ),
        Spacer(1, 5 * mm),
    ]

    if results_df is not None and not results_df.empty:
        story.append(Paragraph("Recognized Laboratory Results", styles["Heading2"]))

        safe_df = results_df.fillna("").astype(str)
        table_data = [list(safe_df.columns)] + safe_df.values.tolist()

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#163A5F")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.extend([table, Spacer(1, 5 * mm)])
    else:
        story.append(
            Paragraph(
                "No structured laboratory results were recognized.",
                styles["Normal"],
            )
        )

    if ai_explanation:
        story.append(Paragraph("AI Explanation", styles["Heading2"]))
        safe_explanation = escape(str(ai_explanation)).replace("\n", "<br/>")
        story.append(Paragraph(safe_explanation, styles["BodyText"]))
        story.append(Spacer(1, 5 * mm))

    if report_text:
        story.append(Paragraph("Extracted Report Text", styles["Heading2"]))
        safe_text = escape(report_text[:12000]).replace("\n", "<br/>")
        story.append(Paragraph(safe_text, styles["BodyText"]))

    doc.build(story)
    output.seek(0)
    return output.getvalue()
        
