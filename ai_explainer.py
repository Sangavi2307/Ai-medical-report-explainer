import re
import pandas as pd


def ai_explain_report(report_text, results_df=None):
    """
    Create a rule-based explanation of a medical report.
    Does not use an external AI API.
    """

    if not report_text or not report_text.strip():
        return "No report text is available. Please upload or paste a report."

    text = report_text.strip()
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    sections = {
        "Patient details": [],
        "Medical history and symptoms": [],
        "Vital signs": [],
        "Laboratory results": [],
        "Imaging and scan findings": [],
        "Doctor's observations": [],
        "Medications and advice": [],
        "Follow-up instructions": [],
        "Other report information": [],
    }

    # Identify section headings in the report.
    current_section = "Other report information"

    heading_map = {
        "patient details": "Patient details",
        "personal details": "Patient details",
        "medical history": "Medical history and symptoms",
        "symptoms": "Medical history and symptoms",
        "clinical history": "Medical history and symptoms",
        "vitals": "Vital signs",
        "vital signs": "Vital signs",
        "laboratory results": "Laboratory results",
        "lab results": "Laboratory results",
        "investigations": "Laboratory results",
        "blood test": "Laboratory results",
        "test results": "Laboratory results",
        "radiology": "Imaging and scan findings",
        "imaging": "Imaging and scan findings",
        "scan findings": "Imaging and scan findings",
        "doctor's observations": "Doctor's observations",
        "clinical observations": "Doctor's observations",
        "observations": "Doctor's observations",
        "assessment": "Doctor's observations",
        "medications": "Medications and advice",
        "medication": "Medications and advice",
        "prescription": "Medications and advice",
        "treatment": "Medications and advice",
        "advice": "Medications and advice",
        "recommendations": "Medications and advice",
        "next steps": "Follow-up instructions",
        "follow-up": "Follow-up instructions",
        "follow up": "Follow-up instructions",
        "plan": "Follow-up instructions",
    }

    for line in lines:
        normalized = re.sub(r"[:\s]+$", "", line.lower()).strip()

        if normalized in heading_map:
            current_section = heading_map[normalized]
            continue

        sections[current_section].append(line)

    # Recognize common patient details and vital signs.
    detail_patterns = {
        "Patient name": r"\bname\s*[:\-]\s*(.+)",
        "Age": r"\bage\s*[:\-]\s*(\d+\s*(?:years?|yrs?)?)",
        "Date of birth": r"\b(?:dob|date of birth)\s*[:\-]\s*(.+)",
        "Gender": r"\b(?:gender|sex)\s*[:\-]\s*(.+)",
        "Blood pressure": r"\b(?:blood pressure|bp)\s*[:\-]?\s*([^\n]+)",
        "Pulse": r"\b(?:pulse|heart rate)\s*[:\-]?\s*([^\n]+)",
        "Temperature": r"\btemperature\s*[:\-]?\s*([^\n]+)",
        "Respiratory rate": r"\brespiratory rate\s*[:\-]?\s*([^\n]+)",
        "Oxygen saturation": r"\b(?:spo2|oxygen saturation)\s*[:\-]?\s*([^\n]+)",
    }

    found_details = {}

    for label, pattern in detail_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if value:
                found_details[label] = value

    # Build a readable report summary.
    output = [
        "# Medical Report Summary",
        "",
        "This summary is generated using Python rules and extracted text. "
        "It is not an AI-generated medical interpretation or a diagnosis.",
        "",
    ]

    if found_details:
        output.extend(["## Recognized Patient Details and Vitals", ""])
        for label, value in found_details.items():
            output.append(f"- **{label}:** {value}")
        output.append("")

    # Display report sections that contain text.
    for section_name, section_lines in sections.items():
        if section_lines:
            output.append(f"## {section_name}")
            output.append("")

            for line in section_lines:
                output.append(f"- {line}")

            output.append("")

    # Include recognized laboratory analysis when available.
    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        output.extend([
            "## Recognized Laboratory Results",
            "",
            results_df.to_string(index=False),
            "",
            "Compare values only with the reference ranges supplied by "
            "the reporting laboratory. This program does not independently "
            "diagnose or determine the clinical significance of results.",
            "",
        ])
    else:
        output.extend([
            "## Laboratory Results",
            "",
            "No laboratory values were identified by the current test-name "
            "patterns. This does not mean the report is normal or abnormal. "
            "Check the extracted text and the original report.",
            "",
        ])

    # Highlight possible OCR issues without guessing missing information.
    if re.search(r"\b(?:unclear|illegible|unreadable|ocr error)\b", text, re.I):
        output.extend([
            "## Text Quality Notice",
            "",
            "The extracted text may contain unclear or unreadable content. "
            "Check the original report before relying on this summary.",
            "",
        ])

    output.extend([
        "## Important Limitations",
        "",
        "- This summary organizes text; it does not diagnose a condition.",
        "- Missing information has not been inferred.",
        "- OCR may misread names, numbers, units, and medical terms.",
        "- Medication instructions must be verified with the prescribing clinician.",
        "- Ask a qualified healthcare professional to interpret the report "
        "in the context of symptoms and medical history.",
    ])

    return "\n".join(output)
