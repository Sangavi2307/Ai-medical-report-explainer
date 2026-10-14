
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

SECTION_ORDER = [
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


def clean_line(line):
    """Remove surrounding whitespace and common OCR bullet symbols."""
    line = str(line).strip()
    line = re.sub(r"^[^\w]+", "", line)
    return line.strip()


def normalize_heading(line):
    return clean_line(line).lower().rstrip(":").strip()


def extract_patient_fields(lines):
    """Extract only explicitly labeled patient details and vital signs."""
    fields = {}

    aliases = [
        (label, alias)
        for label, names in FIELD_LABELS.items()
        for alias in names
    ]

    for i, line in enumerate(lines):
        cleaned = clean_line(line)

        for label, alias in aliases:
            pattern = (
                r"^\s*" + re.escape(alias) +
                r"\s*[:\-]\s*(.*?)\s*$"
            )
            match = re.match(pattern, cleaned, re.IGNORECASE)

            if not match:
                continue

            value = match.group(1).strip()

            # Read the next line only when the value is on a separate line.
            if not value and i + 1 < len(lines):
                next_line = clean_line(lines[i + 1])

                next_is_label = any(
                    re.match(
                        r"^\s*" + re.escape(other_alias) +
                        r"\s*[:\-]",
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
    """Group extracted report text under recognized headings."""
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
    """Describe values and statuses supplied by the existing analyzer."""
    if not isinstance(results_df, pd.DataFrame) or results_df.empty:
        return (
            "No laboratory values were recognized by the current "
            "analysis rules. This does not mean the report is normal "
            "or abnormal. Check the original report."
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
            result_text += f" | Reference range: {reference}"

        if pd.notna(status) and str(status).strip():
            result_text += f" | Program status: {status}"

        output.append(result_text)

    output.append(
        "\nReference ranges vary by laboratory and individual. "
        "The program's status is a basic comparison, not a diagnosis."
    )

    return "\n".join(output)


def ai_explain_report(report_text, results_df=None):
    """
    Free, rule-based report summarizer.

    No network request or paid AI API is used.
    The function summarizes only the text supplied to it.
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

    for section_name in SECTION_ORDER:
        values = sections.get(section_name, [])

        if not values:
            continue

        output.extend([f"## {section_name}", ""])

        for value in values:
            cleaned = clean_line(value)

            if cleaned:
                output.append(f"- {cleaned}")

        output.append("")

    # Preserve other sections instead of silently discarding their text.
    for section_name, values in sections.items():
        if section_name in SECTION_ORDER or not values:
            continue

        output.extend([f"## {section_name}", ""])

        for value in values:
            cleaned = clean_line(value)

            if cleaned:
                output.append(f"- {cleaned}")

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
            "- Some extracted information may be unclear. "
            "Verify it against the original report."
        )
    else:
        output.append(
            "- OCR can misread numbers, names, dates, units, and "
            "medication names. Verify important details."
        )

    output.extend([
        "",
        "## Important Limitations",
        "",
        "- This summary uses only the text supplied to the program.",
        "- Missing or ambiguous values are not inferred.",
        "- A reference-range comparison cannot determine overall health.",
        "- Verify medication instructions against the original prescription.",
        "- Consult a qualified healthcare professional for interpretation.",
        "- This educational tool does not replace professional medical advice.",
    ])

    return "\n".join(output)
