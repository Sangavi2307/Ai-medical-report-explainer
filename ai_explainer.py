import re
import pandas as pd


def ai_explain_report(report_text, results_df=None):
    if not report_text or not report_text.strip():
        return "No report text is available."

    lines = [line.strip() for line in report_text.splitlines() if line.strip()]
    text = "\n".join(lines)

    output = [
        "# Medical Report Summary",
        "",
        "This summary organizes extracted report text using Python rules. "
        "It is not a medical diagnosis.",
        "",
    ]

    # Read only labels that appear with their values on the same line.
    # Avoid guessing when OCR has put a label and value on separate lines.
    patterns = {
        "Patient name": r"(?im)^\s*Name\s*:\s*(\S.*)$",
        "Date of birth": r"(?im)^\s*(?:DOB|Date of birth)\s*:\s*(\S.*)$",
        "Age": r"(?im)^\s*Age\s*:\s*(\S.*)$",
        "Gender": r"(?im)^\s*(?:Gender|Sex)\s*:\s*(\S.*)$",
        "Blood pressure": r"(?im)^\s*(?:Blood pressure|BP)\s*:\s*(\S.*)$",
        "Pulse": r"(?im)^\s*(?:Pulse|Heart rate)\s*:\s*(\S.*)$",
        "Temperature": r"(?im)^\s*Temperature\s*:\s*(\S.*)$",
        "Respiratory rate": r"(?im)^\s*Respiratory rate\s*:\s*(\S.*)$",
        "Oxygen saturation": r"(?im)^\s*(?:SpO2|Oxygen saturation)\s*:\s*(\S.*)$",
    }

    details = {}
    for label, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            details[label] = match.group(1).strip()

    if details:
        output.extend(["## Patient Details and Vital Signs", ""])
        for label, value in details.items():
            output.append(f"- **{label}:** {value}")
        output.append("")

    # Section headings and their common variations.
    headings = {
        "patient details": "Patient details",
        "personal details": "Patient details",
        "medical history": "Medical history and symptoms",
        "clinical history": "Medical history and symptoms",
        "symptoms": "Medical history and symptoms",
        "vitals": "Vital signs",
        "vital signs": "Vital signs",
        "laboratory results": "Laboratory results",
        "lab results": "Laboratory results",
        "test results": "Laboratory results",
        "investigations": "Laboratory results",
        "imaging": "Imaging and scan findings",
        "radiology": "Imaging and scan findings",
        "scan findings": "Imaging and scan findings",
        "doctor's observations": "Doctor's observations",
        "clinical observations": "Doctor's observations",
        "observations": "Doctor's observations",
        "notes and next steps": "Follow-up instructions",
        "next steps": "Follow-up instructions",
        "follow-up": "Follow-up instructions",
        "follow up": "Follow-up instructions",
        "medications": "Medications and advice",
        "medication": "Medications and advice",
        "prescription": "Medications and advice",
        "recommendations": "Medications and advice",
        "advice": "Medications and advice",
        "treatment": "Medications and advice",
    }

    sections = {}
    current_section = "General report information"

    for line in lines:
        clean = re.sub(r"^[^A-Za-z0-9]+", "", line).strip()
        normalized = re.sub(r"[:\s]+$", "", clean.lower()).strip()

        if normalized in headings:
            current_section = headings[normalized]
            continue

        if re.fullmatch(r"general check-up report", normalized):
            current_section = "General report information"
            sections.setdefault(current_section, []).append(clean)
            continue

        sections.setdefault(current_section, []).append(clean)

    # Remove empty values and labels whose values were placed on another line.
    for label in ("Patient details", "Medical history and symptoms",
                  "Vital signs", "Laboratory results",
                  "Imaging and scan findings", "Doctor's observations",
                  "Medications and advice", "Follow-up instructions",
                  "General report information"):
        values = sections.get(label, [])
        if values:
            output.extend([f"## {label}", ""])
            for value in values:
                if value and not re.fullmatch(
                    r"(?:Name|DOB|Date of birth|Age|Gender|Sex)\s*:",
                    value,
                    re.IGNORECASE,
                ):
                    output.append(f"- {value}")
            output.append("")

    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        output.extend([
            "## Recognized Laboratory Results",
            "",
            results_df.to_string(index=False),
            "",
            "Reference ranges vary by laboratory and patient factors. "
            "Discuss results with a qualified healthcare professional.",
            "",
        ])
    else:
        output.extend([
            "## Laboratory Results",
            "",
            "No laboratory values were recognized by the current rules. "
            "This does not mean that the report is normal or abnormal.",
            "",
        ])

    output.extend([
        "## Important Limitations",
        "",
        "- Some values may be missing or incorrectly extracted by OCR.",
        "- Patient details should be verified against the original report.",
        "- Medication names and instructions must be checked with the prescriber.",
        "- This summary does not diagnose disease or recommend treatment.",
    ])

    return "\n".join(output)
