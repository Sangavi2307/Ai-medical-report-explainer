
import io
import html

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


def create_pdf_report(results_df, ai_summary):
    """
    Generate a PDF containing extracted laboratory results
    and the AI-generated educational explanation.

    Returns PDF data as bytes.
    """

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "AI Medical Report Explainer",
            styles["Title"],
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "Educational Explanation of Laboratory Results",
            styles["Heading2"],
        )
    )

    story.append(Spacer(1, 10))

    story.append(
        Paragraph(
            "This report is for educational purposes only. "
            "It does not provide a medical diagnosis or treatment.",
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 18))

    # Laboratory results table
    story.append(
        Paragraph(
            "Laboratory Test Results",
            styles["Heading2"],
        )
    )

    story.append(Spacer(1, 8))

    columns = [
        "Test",
        "Result",
        "Unit",
        "Reference Range",
        "Status",
    ]

    table_data = [columns]

    if results_df is not None and not results_df.empty:
        for _, row in results_df.iterrows():
            table_data.append([
                str(row.get("Test", "")),
                str(row.get("Result", "")),
                str(row.get("Unit", "")),
                str(row.get("Reference Range", "")),
                str(row.get("Status", "")),
            ])

    # Escape text so special characters cannot break PDF markup.
    safe_table_data = []

    for row in table_data:
        safe_table_data.append([
            Paragraph(
                html.escape(value),
                styles["BodyText"],
            )
            for value in row
        ])

    results_table = Table(
        safe_table_data,
        colWidths=[
            1.1 * inch,
            0.75 * inch,
            0.65 * inch,
            1.25 * inch,
            1.0 * inch,
        ],
        repeatRows=1,
    )

    results_table.setStyle(
        TableStyle([
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
        ])
    )

    story.append(results_table)

    story.append(Spacer(1, 20))

    # AI explanation
    story.append(
        Paragraph(
            "AI Explanation",
            styles["Heading2"],
        )
    )

    story.append(Spacer(1, 8))

    summary_text = html.escape(
        str(ai_summary or "No AI explanation available.")
    )

    # Preserve line breaks in the explanation.
    summary_text = summary_text.replace("\n", "<br/>")

    story.append(
        Paragraph(
            summary_text,
            styles["BodyText"],
        )
    )

    story.append(Spacer(1, 20))

    # Medical safety disclaimer
    story.append(
        Paragraph(
            "<b>Important Medical Disclaimer</b>",
            styles["Heading3"],
        )
    )

    story.append(
        Paragraph(
            "Laboratory reference ranges vary between laboratories. "
            "An abnormal result does not automatically indicate a "
            "disease. Extracted text may contain OCR errors. Review "
            "the original report and discuss results with a qualified "
            "healthcare professional. Do not change medicines based "
            "on this educational report.",
            styles["BodyText"],
        )
    )

    document.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
