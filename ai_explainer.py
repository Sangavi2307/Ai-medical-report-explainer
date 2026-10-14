
import pandas as pd

TEST_INFO = {
    "hemoglobin": (
        "Hemoglobin is a protein in red blood cells that carries oxygen."
    ),
    "wbc": (
        "White blood cells help the body respond to infections and other conditions."
    ),
    "white blood cell": (
        "White blood cells help the body respond to infections and other conditions."
    ),
    "platelet": (
        "Platelets help blood clot. The result needs to be interpreted using "
        "the correct unit and laboratory reference range."
    ),
    "glucose": (
        "Glucose is sugar in the blood. Fasting status and the laboratory's "
        "reference range affect interpretation."
    ),
    "blood sugar": (
        "Blood sugar measures glucose in the blood. Fasting status matters."
    ),
    "cholesterol": (
        "Cholesterol is a blood lipid used to assess aspects of cardiovascular risk."
    ),
}


def explain_report(report_text, results_df, patient_fields):
    sections = []

    sections.append("### Explanation")
    sections.append(
        "The following information is an educational description of the "
        "recognized text, not a diagnosis."
    )

    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        for _, row in results_df.iterrows():
            test = str(row.get("Test", "Unknown test"))
            result = str(row.get("Result", "Not extracted"))
            unit = str(row.get("Unit", "Not extracted"))
            reference = str(row.get("Reference Range", "Not extracted"))

            info = "No test-specific explanation is available in this version."
            test_lower = test.lower()

            for key, description in TEST_INFO.items():
                if key in test_lower:
                    info = description
                    break

            sections.append(f"#### {test}")
            sections.append(f"- **Result:** {result} {unit}")
            sections.append(f"- **Reference range:** {reference}")

            if reference == "Not extracted" or unit == "Not extracted":
                sections.append(
                    "- **Status:** Cannot be reliably evaluated because "
                    "the unit or reference range was not extracted."
                )
            else:
                sections.append(
                    "- **Status:** Not medically evaluated by this application."
                )

            sections.append(f"- **What this test measures:** {info}")

    else:
        sections.append(
            "No supported laboratory result lines were recognized. "
            "This does not mean the report contains no results."
        )

    sections.append("### Overall Summary")
    sections.append(
        f"The application processed {len(report_text)} characters of extracted "
        "text. Verify all values, units, patient details, and reference ranges "
        "against the original report."
    )

    sections.append("### Important Note")
    sections.append(
        "OCR and text extraction can introduce errors. Reference ranges vary "
        "between laboratories, and a result cannot be interpreted from a number "
        "alone. Discuss actual medical results with a qualified healthcare "
        "professional."
    )

    return "\n\n".join(sections)
