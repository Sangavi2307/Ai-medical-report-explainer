
def ai_explain_report(results, patient_fields=None, report_text=""):
    patient_fields = patient_fields or {}

    parts = [
        "MEDILENS — REPORT EXPLANATION",
        "=" * 34,
        "",
        "PATIENT DETAILS",
    ]

    for key, value in patient_fields.items():
        parts.append(f"{key}: {value}")

    parts.extend(["", "LABORATORY FINDINGS"])

    if results is None or results.empty:
        parts.extend([
            "No supported laboratory results were identified.",
            "The report may use an unfamiliar layout, test name, "
            "or image quality may have affected text extraction.",
            "Check the extracted text and verify the original report.",
        ])
    else:
        for _, row in results.iterrows():
            test = str(row.get("Test", "Unknown test"))
            value = row.get("Result", "Unknown")
            unit = str(row.get("Unit", "") or "")
            reference = str(row.get("Reference Range", "") or "")
            status = str(row.get("Status", "Not evaluated"))

            parts.extend([
                "",
                f"{test}",
                f"Extracted result: {value} {unit}".strip(),
                f"Reference range: {reference or 'Not identified'}",
                f"Comparison: {status}",
            ])

            if status == "Within stated range":
                parts.append(
                    "The extracted value falls within the reference "
                    "range identified by the program. This alone does "
                    "not establish that a person is healthy."
                )
            elif status == "Below stated range":
                parts.append(
                    "The extracted value is below the identified range. "
                    "Its significance depends on the person's clinical "
                    "context and should be reviewed by a healthcare professional."
                )
            elif status == "Above stated range":
                parts.append(
                    "The extracted value is above the identified range. "
                    "Its significance depends on the person's clinical "
                    "context and should be reviewed by a healthcare professional."
                )
            else:
                parts.append(
                    "The program could not identify a reliable reference "
                    "range, so it cannot safely classify this value as normal "
                    "or abnormal."
                )

    parts.extend([
        "",
        "LIMITATIONS",
        "These findings are based on automatically extracted text. "
        "OCR may misread decimal points, units, labels, or reference ranges. "
        "The application may not recognize every test or laboratory format.",
        "",
        "MEDICAL NOTICE",
        "This tool is for educational information only. It does not provide "
        "a diagnosis, prescribe treatment, or replace professional medical advice. "
        "Verify values against the original report and consult a qualified "
        "healthcare professional.",
    ])

    return "\n".join(parts)
