from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from io import BytesIO


def generate_report(results, ai_summary):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    story = []

    # -----------------------------------------
    # TITLE
    # -----------------------------------------

    story.append(
        Paragraph(
            "AI Medical Report Explainer",
            title_style
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Laboratory Results Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 10))

    # -----------------------------------------
    # RESULTS TABLE
    # -----------------------------------------

    table_data = [
        [
            "Test",
            "Result",
            "Unit",
            "Reference Range",
            "Status"
        ]
    ]

    for _, row in results.iterrows():

        table_data.append([
            str(row["Test"]),
            str(row["Result"]),
            str(row["Unit"]),
            str(row["Reference Range"]),
            str(row["Status"])
        ])

    table = Table(
        table_data,
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.black
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            )
        ])
    )

    story.append(table)

    story.append(Spacer(1, 20))

    # -----------------------------------------
    # AI EXPLANATION
    # -----------------------------------------

    story.append(
        Paragraph(
            "AI Educational Explanation",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 10))

    # Convert AI markdown-style headings
    # into readable PDF paragraphs

    for line in ai_summary.split("\n"):

        line = line.strip()

        if not line:
            story.append(Spacer(1, 6))
            continue

        line = line.replace(
            "### ",
            ""
        )

        line = line.replace(
            "**",
            ""
        )

        story.append(
            Paragraph(
                line,
                styles["BodyText"]
            )
        )

        story.append(
            Spacer(1, 4)
        )

    # -----------------------------------------
    # DISCLAIMER
    # -----------------------------------------

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "<b>Important Medical Disclaimer</b>",
            styles["Heading3"]
        )
    )

    story.append(Spacer(1, 5))

    story.append(
        Paragraph(
            "This report provides informational and "
            "educational explanations only. It does not "
            "provide a medical diagnosis or treatment. "
            "Laboratory results should be interpreted by "
            "a qualified healthcare professional in the "
            "appropriate clinical context.",
            styles["BodyText"]
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer
