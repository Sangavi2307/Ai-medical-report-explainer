import re
import pandas as pd


HEADINGS = {
    "patient details": "Patient Details",
    "personal details": "Patient Details",
    "medical history": "Medical History",
    "clinical history": "Medical History",
    "symptoms": "Symptoms",
    "vitals": "Vital Signs",
    "vital signs": "Vital Signs",
    "laboratory results": "Laboratory Results",
    "lab results": "Laboratory Results",
    "test results": "Laboratory Results",
    "investigations": "Investigations",
    "imaging": "Imaging and Scan Findings",
    "radiology": "Imaging and Scan Findings",
    "doctor's observations": "Doctor's Observations",
    "clinical observations": "Doctor's Observations",
    "observations": "Doctor's Observations",
    "examination": "Examination",
    "medications": "Medications and Advice",
    "medication": "Medications and Advice",
    "prescription": "Medications and Advice",
    "treatment": "Treatment Information",
    "recommendations": "Recommendations",
    "advice": "Recommendations",
    "notes and next steps": "Follow-up and Next Steps",
    "follow-up": "Follow-up and Next Steps",
    "follow up": "Follow-up and Next Steps",
    "next steps": "Follow-up and Next Steps",
    "plan": "Follow-up and Next Steps",
}


FIELD_LABELS = {
    "Patient Name": ["patient name", "name"],
    "Age": ["age"],
    "Date of Birth": ["date of birth", "dob", "birth date"],
    "Gender": ["gender", "sex"],
    "Blood Pressure": ["blood pressure", "bp"],
    "Pulse": ["pulse", "heart rate"],
    "Temperature": ["temperature"],
    "Respiratory Rate": ["respiratory rate"],
    "Oxygen Saturation": ["oxygen saturation", "spo2", "sp o2"],
}


def clean_line(line):
    line = str(line).strip()
    line = re.sub(r"^[^\w]+", "", line)
    return line.strip()


def normalize_heading(line):
    return clean_line(line).lower().rstrip(":").strip()


def extract_patient_fields(lines):
    fields = {}

    aliases = [
        (label, alias)
        for label, names in FIELD_LABELS.items()
        for alias in names
    ]

    for i, line in enumerate(lines):
        cleaned = clean_line(line)

        for label, alias in aliases:
            match = re.match(
                r"^\s*" + re.escape(alias) +
                r"\s*[:\-]\s*(.*?)\s*$",
                cleaned,
                re.IGNORECASE,
            )

            if not match:
                continue

            value = match.group(1).strip()

            # Some OCR output puts a label and its value
            # on separate lines.
            if not value and i + 1 < len(lines):
                next_line = clean_line(lines[i + 1])

                next_is_label = any(
                    re.match(
                        r"^\s*" + re.escape(other_alias) + r"\s*:",
                        next_line,
                        re.IGNORECASE,
                    )
                    for _, other_alias in aliases
                )

                if not next_is_label:
                    value = next_line

            if value:
                fields[label] = value

            break

    return fields


def collect_sections(lines):
    sections = {}
    current = "General Information"

    for line in lines:
        cleaned = clean_line(line)

        if not cleaned:
            continue

        heading = normalize_heading(cleaned)

        if heading in HEADINGS:
            current = HEADINGS[heading]
            sections.setdefault(current, [])
            continue

        if heading in {
            "medical report",
            "health report",
            "general check-up report",
            "general check up report",
        }:
            sections.setdefault("General Information", []).append(cleaned)
            continue

        sections.setdefault(current, []).append(cleaned)

    return sections


def explain_laboratory_results(results_df):
    if not isinstance(results_df, pd.DataFrame) or results_df.empty:
        return (
            "No laboratory values were recognized by the current "
            "analysis rules. This does not mean that the report is "
            "normal or abnormal. Check the original report."
        )

    output = []

    for _, row in results_df.iterrows():
        test = row.get("Test", "Unknown test")
        result = row.get("Result", "Not available")
        unit = row.get("Unit", "")
        reference = row.get("Reference Range", "")
        status = row.get("Status", "Not evaluated")

        result_text = f"- **{test}:** {result}"

        if pd.notna(unit) and str(unit).strip():
            result_text += f" {unit}"

        if pd.notna(reference) and str(reference).strip():
            result_text += f" | Supplied reference range: {reference}"

        if pd.notna(status) and str(status).strip():
            result_text += f" | Program status: {status}"

        output.append(result_text)

    output.append(
        "\nReference ranges vary between laboratories and people. "
        "The program's status is a basic comparison, not a diagnosis."
    )

    return "\n".join(output)


def ai_explain_report(report_text, results_df=None):
    """
    Free rule-based report summarizer.
    No network request or paid API is used.
    """

    if not isinstance(report_text, str) or not report_text.strip():
        return (
            "# Medical Report Summary\n\n"
            "No report text is available. Upload a report or paste "
            "its text first."
        )

    lines = [
        line.strip()
        for line in report_text.splitlines()
        if line.strip()
    ]

    fields = extract_patient_fields(lines)
    sections = collect_sections(lines)

    output = [
        "# Medical Report Summary",
        "",
        "This summary organizes information found in the extracted "
        "report text using Python rules. It is not a medical diagnosis.",
        "",
    ]

    if fields:
        output.extend([
            "## Patient Details and Vital Signs",
            "",
        ])

        for label, value in fields.items():
            output.append(f"- **{label}:** {value}")

        output.append("")

    order = [
        "General Information",
        "Patient Details",
        "Medical History",
        "Symptoms",
        "Vital Signs",
        "Laboratory Results",
        "Investigations",
        "Imaging and Scan Findings",
        "Examination",
        "Doctor's Observations",
        "Medications and Advice",
        "Treatment Information",
        "Recommendations",
        "Follow-up and Next Steps",
    ]

    for section_name in order:
        values = sections.get(section_name, [])

        if not values:
            continue

        output.extend([f"## {section_name}", ""])

        for value in values:
            cleaned = clean_line(value)

            if not cleaned:
                continue

            if normalize_heading(cleaned) in HEADINGS:
                continue

            output.append(f"- {cleaned}")

        output.append("")

    # Include any additional sections without losing their content.
    for section_name, values in sections.items():
        if section_name in order or not values:
            continue

        output.extend([f"## {section_name}", ""])

        for value in values:
            output.append(f"- {clean_line(value)}")

        output.append("")

    output.extend([
        "## Laboratory Results Analysis",
        "",
        explain_laboratory_results(results_df),
        "",
        "## Text Quality Check",
        "",
    ])

    if re.search(
        r"\b(unreadable|illegible|unclear|ocr error)\b",
        report_text,
        re.IGNORECASE,
    ):
        output.append(
            "- The extracted text indicates that some information "
            "may be unclear. Verify it against the original report."
        )
    else:
        output.append(
            "- OCR can still misread numbers, names, dates, units, "
            "and medication names. Verify important details."
        )

    output.extend([
        "",
        "## Important Limitations",
        "",
        "- Information is based only on the text supplied to the program.",
        "- Missing or ambiguous values are not inferred.",
        "- A reference-range comparison does not confirm that a person "
        "is healthy or has a disease.",
        "- Medication instructions should be verified with the original "
        "prescription and a qualified healthcare professional.",
        "- This report summary is educational and does not replace "
        "professional medical advice.",
    ])

    return "\n".join(output)
