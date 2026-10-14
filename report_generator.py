from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_pdf_report(
    report_name,
    report_type,
    patient_fields,
    results_df,
    summary,
):
    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    story = [
        Paragraph("MediLens", styles["Title"]),
        Paragraph("Medical Report Summary", styles["Heading2"]),
        Spacer(1, 12),
        Paragraph(
            f"Report file: {escape(str(report_name))}",
            styles["Normal"],
        ),
        Paragraph(
            f"Detected category: {escape(str(report_type))}",
            styles["Normal"],
        ),
        Spacer(1, 8),
        Paragraph("Patient Information", styles["Heading2"]),
    ]

    for key, value in patient_fields.items():
        story.append(
            Paragraph(
                f"{escape(str(key))}: {escape(str(value))}",
                styles["Normal"],
            )
        )

    story.extend([
        Spacer(1, 10),
        Paragraph("Summary", styles["Heading2"]),
    ])

    for item in summary:
        story.append(Paragraph(escape(str(item)), styles["Normal"]))

    if results_df is not None and not results_df.empty:
        story.extend([
            Spacer(1, 10),
            Paragraph("Extracted Laboratory Results", styles["Heading2"]),
        ])

        columns = ["Test", "Result", "Unit", "Reference Range", "Status"]
        table_data = [
            [Paragraph(escape(column), styles["Normal"]) for column in columns]
        ]

        for _, row in results_df.iterrows():
            table_data.append([
                Paragraph(escape(str(row.get(column, "")),), styles["Normal"])
                for column in columns
            ])

        table = Table(
            table_data,
            colWidths=[4.1 * cm, 2 * cm, 2 * cm, 3.1 * cm, 3.8 * cm],
            repeatRows=1,
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16324F")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        story.append(table)

    story.extend([
        Spacer(1, 14),
        Paragraph("Important Disclaimer", styles["Heading2"]),
        Paragraph(
            "This document is generated from extracted text and basic rules. "
            "Extraction may be incomplete or inaccurate. It is not a diagnosis "
            "or treatment recommendation. Consult a qualified healthcare "
            "professional for interpretation.",
            styles["Normal"],
        ),
    ])

    document.build(story)
    return output.getvalue()
