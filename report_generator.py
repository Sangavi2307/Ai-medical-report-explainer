
from io import BytesIO
from xml.sax.saxutils import escape

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
    KeepTogether
)


def generate_pdf_report(
    report_name,
    patient_fields,
    results_df,
    summary
):
    output = BytesIO()

    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="MediLensTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#087E8B"),
        spaceAfter=12
    ))

    story = [
        Paragraph("MediLens", styles["MediLensTitle"]),
        Paragraph("Medical Report Explanation", styles["Heading2"]),
        Paragraph(
            escape(str(report_name or "Uploaded report")),
            styles["Normal"]
        ),
        Spacer(1, 10)
    ]

    if patient_fields:
        story.append(Paragraph("Patient Details", styles["Heading2"]))

        for key, value in patient_fields.items():
            if value is not None and str(value).strip():
                story.append(Paragraph(
                    f"<b>{escape(str(key))}:</b> "
                    f"{escape(str(value))}",
                    styles["Normal"]
                ))

        story.append(Spacer(1, 10))

    story.append(Paragraph("Laboratory Results", styles["Heading2"]))

    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        columns = [
            "Test", "Result", "Unit", "Reference Range", "Status"
        ]
        data = [[Paragraph(f"<b>{c}</b>", styles["BodyText"]) for c in columns]]

        for _, row in results_df.iterrows():
            data.append([
                Paragraph(escape(str(row.get(col, "") or "")), styles["BodyText"])
                for col in columns
            ])

        table = Table(
            data,
            repeatRows=1,
            colWidths=[35*mm, 20*mm, 20*mm, 35*mm, 35*mm]
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#087E8B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5)
        ]))

        story.append(table)
    else:
        story.append(Paragraph(
            "No laboratory results could be reliably extracted.",
            styles["Normal"]
        ))

    story.append(Spacer(1, 14))
    story.append(Paragraph("Detailed Explanation", styles["Heading2"]))

    for block in str(summary or "").split("\n\n"):
        safe_block = escape(block).replace("\n", "<br/>")
        if safe_block.strip():
            story.append(KeepTogether([
                Paragraph(safe_block, styles["BodyText"]),
                Spacer(1, 7)
            ]))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Important:</b> This report is for educational purposes only. "
        "It does not provide a diagnosis or replace professional medical advice.",
        styles["Italic"]
    ))

    doc.build(story)
    return output.getvalue()
