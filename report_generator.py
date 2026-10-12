
from io import BytesIO

import pandas as pd
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


def create_pdf_report(results_df, ai_summary):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#156082"),
        spaceAfter=12,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        leading=14,
        spaceAfter=6,
        wordWrap="CJK",
    )

    story = []

    story.append(
        Paragraph("AI Medical Report Explainer", title_style)
    )
    story.append(
        Paragraph(
            "Educational explanation of uploaded medical report",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 8 * mm))

    story.append(
        Paragraph("Laboratory Results", styles["Heading2"])
    )
    story.append(Spacer(1, 3 * mm))

    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        table_data = [
            [
                Paragraph(str(column), styles["BodyText"])
                for column in results_df.columns
            ]
        ]

        for _, row in results_df.iterrows():
            table_data.append([
                Paragraph(str(value), body_style)
                for value in row.tolist()
            ])

        column_count = len(results_df.columns)
        available_width = A4[0] - 30 * mm
        column_widths = [available_width / column_count] * column_count

        table = Table(
            table_data,
            colWidths=column_widths,
            repeatRows=1,
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#DDEBF7")),
            ("TEXTCOLOR", (0, 0), (-1, 0),
             colors.HexColor("#17365D")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        story.append(table)
    else:
        story.append(
            Paragraph("No laboratory results were detected.",
                      body_style)
        )

    story.append(Spacer(1, 8 * mm))
    story.append(
        Paragraph("AI Explanation", styles["Heading2"])
    )
    story.append(Spacer(1, 3 * mm))

    summary = str(ai_summary or "No AI explanation is available.")

    for line in summary.splitlines():
        # Escape special HTML characters in the AI-generated text.
        from xml.sax.saxutils import escape

        story.append(
            Paragraph(escape(line) if line.strip() else " ", body_style)
        )

    story.append(Spacer(1, 8 * mm))
    story.append(
        Paragraph(
            "<b>Important:</b> This report is for educational "
            "purposes only. It is not a medical diagnosis or a "
            "substitute for advice from a qualified healthcare "
            "professional.",
            body_style,
        )
    )

    document.build(story)
    buffer.seek(0)

    return buffer.getvalue()
