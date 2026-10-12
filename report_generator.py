
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd


def create_pdf_report(results_df, ai_summary):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=letter
    )

    styles = getSampleStyleSheet()
    content = []

    content.append(
        Paragraph("AI Medical Report Explainer", styles["Title"])
    )
    content.append(Spacer(1, 12))

    content.append(
        Paragraph("Laboratory Results", styles["Heading2"])
    )
    content.append(Spacer(1, 8))

    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        table_data = [
            [str(column) for column in results_df.columns]
        ]

        for _, row in results_df.iterrows():
            table_data.append([
                str(value) for value in row.tolist()
            ])

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        content.append(table)
    else:
        content.append(
            Paragraph("No laboratory results available.", styles["BodyText"])
        )

    content.append(Spacer(1, 16))
    content.append(
        Paragraph("AI Explanation", styles["Heading2"])
    )
    content.append(Spacer(1, 8))

    summary = str(ai_summary or "No AI explanation available.")
    for line in summary.splitlines():
        content.append(
            Paragraph(line or " ", styles["BodyText"])
        )
        content.append(Spacer(1, 4))

    content.append(Spacer(1, 12))
    content.append(
        Paragraph(
            "Educational information only. Not a medical diagnosis "
            "or a substitute for advice from a qualified healthcare professional.",
            styles["Italic"]
        )
    )

    document.build(content)
    buffer.seek(0)

    return buffer.getvalue()
