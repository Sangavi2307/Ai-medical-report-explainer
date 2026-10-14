
def explain_report(results, patient_fields=None):
    patient_fields = patient_fields or {}

    lines = [
        "MEDICAL REPORT EXPLANATION",
        "=" * 30,
        "",
        "PATIENT INFORMATION",
    ]

    for key, value in patient_fields.items():
        lines.append(f"{key}: {value}")

    lines.extend([
        "",
        "LABORATORY RESULTS",
    ])

    if results is None or results.empty:
        lines.extend([
            "No laboratory results could be identified.",
            "Check the extracted text and upload a clearer report.",
        ])
    else:
        for _, row in results.iterrows():
            test = row.get("Test", "Unknown test")
            result = row.get("Result", "")
            unit = row.get("Unit", "")
            reference = row.get("Reference Range", "")
            status = row.get("Status", "")

            lines.append(
                f"{test}: {result} {unit}. "
                f"Reference range: {reference or 'not identified'}. "
                f"Status: {status}."
            )

            if status == "Within Range":
                lines.append(
                    "The extracted value is within the reference range "
                    "shown in the report."
                )
            elif status == "Below Range":
                lines.append(
                    "The extracted value is below the identified range. "
                    "Discuss it with a qualified healthcare professional."
                )
            elif status == "Above Range":
                lines.append(
                    "The extracted value is above the identified range. "
                    "Discuss it with a qualified healthcare professional."
                )
            else:
                lines.append(
                    "The reference range could not be reliably identified. "
                    "Verify the original report."
                )

    lines.extend([
        "",
        "IMPORTANT NOTICE",
        "This explanation is based only on text extracted from the uploaded "
        "document. OCR can make mistakes, and reference ranges vary by "
        "laboratory and patient. Verify all values against the original "
        "report and consult a qualified healthcare professional.",
        "This application does not diagnose or recommend treatment.",
    ])

    return "\n".join(lines)
