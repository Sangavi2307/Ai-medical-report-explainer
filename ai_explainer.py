import re
import pandas as pd

HEADINGS = {
"patient details": "Patient Details",
"personal details": "Patient Details",
"medical history": "Medical History and Symptoms",
"clinical history": "Medical History and Symptoms",
"symptoms": "Medical History and Symptoms",
"vitals": "Vital Signs",
"vital signs": "Vital Signs",
"laboratory results": "Laboratory Results",
"lab results": "Laboratory Results",
"test results": "Laboratory Results",
"investigations": "Laboratory Results",
"imaging": "Imaging and Scan Findings",
"radiology": "Imaging and Scan Findings",
"scan findings": "Imaging and Scan Findings",
"doctor's observations": "Doctor's Observations",
"clinical observations": "Doctor's Observations",
"observations": "Doctor's Observations",
"examination": "Doctor's Observations",
"notes and next steps": "Follow-up and Next Steps",
"next steps": "Follow-up and Next Steps",
"follow-up": "Follow-up and Next Steps",
"follow up": "Follow-up and Next Steps",
"plan": "Follow-up and Next Steps",
"medications": "Medications and Advice",
"medication": "Medications and Advice",
"prescription": "Medications and Advice",
"recommendations": "Medications and Advice",
"advice": "Medications and Advice",
"treatment": "Medications and Advice",
}

FIELD_LABELS = {
"Patient name": ("name", "patient name"),
"Date of birth": ("dob", "date of birth", "birth date"),
"Age": ("age",),
"Gender": ("gender", "sex"),
"Blood pressure": ("blood pressure", "bp"),
"Pulse": ("pulse", "heart rate"),
"Temperature": ("temperature",),
"Respiratory rate": ("respiratory rate", "respiratory rt"),
"Oxygen saturation": ("spo2", "oxygen saturation"),
}

def clean_line(line):
line = line.strip()
line = re.sub(r"^[^\w]+", "", line)
return line.strip()

def normalize_heading(line):
line = clean_line(line).lower()
line = re.sub(r"[:\s]+$", "", line)
return line.strip()

def extract_labeled_fields(lines):
"""
Extract label/value pairs whether they are on the same line
or on consecutive lines. Do not infer missing values.
"""
found = {}

for index, original_line in enumerate(lines):
    line = clean_line(original_line)

    for field_name, aliases in FIELD_LABELS.items():
        for alias in aliases:
            pattern = (
                r"^\s*" + re.escape(alias) +
                r"\s*[:\-]\s*(.*?)\s*$"
            )
            match = re.match(pattern, line, re.IGNORECASE)

            if match:
                value = match.group(1).strip()

                if not value and index + 1 < len(lines):
                    next_line = clean_line(lines[index + 1])

                    # Do not use another label as this field's value.
                    next_is_label = any(
                        re.match(
                            r"^\s*" + re.escape(a) + r"\s*:",
                            next_line,
                            re.IGNORECASE,
                        )
                        for aliases2 in FIELD_LABELS.values()
                        for a in aliases2
                    )

                    if not next_is_label:
                        value = next_line

                if value:
                    found[field_name] = value
                break

return found

def collect_sections(lines):
sections = {}
current_section = "General Report Information"

for original_line in lines:
    line = clean_line(original_line)

    if not line:
        continue

    heading = normalize_heading(line)

    if heading in HEADINGS:
        current_section = HEADINGS[heading]
        sections.setdefault(current_section, [])
        continue

    if heading in {
        "general check-up report",
        "medical report",
        "health report",
    }:
        sections.setdefault(
            "General Report Information", []
        ).append(line)
        continue

    sections.setdefault(current_section, []).append(line)

return sections

def explain_laboratory_results(results_df):
if not isinstance(results_df, pd.DataFrame) or results_df.empty:
return (
"No laboratory values were recognized by the current "
"patterns. This does not mean that the report is normal "
"or abnormal. Check the original report."
)

output = []
for _, row in results_df.iterrows():
    output.append(
        "- " + "; ".join(
            f"{column}: {row[column]}"
            for column in results_df.columns
            if pd.notna(row[column])
        )
    )

output.append(
    "\nReview each result using the reference range and units "
    "printed by the laboratory. This program does not diagnose "
    "conditions."
)

return "\n".join(output)

def ai_explain_report(report_text, results_df=None):
"""
Free rule-based medical report summary.
No OpenAI API key or paid API request is used.
"""

if not report_text or not report_text.strip():
    return "No report text is available. Upload a report or paste its text."

lines = [
    line.strip()
    for line in report_text.splitlines()
    if line.strip()
]

details = extract_labeled_fields(lines)
sections = collect_sections(lines)

output = [
    "# Medical Report Summary",
    "",
    "This summary is generated using Python rules from the "
    "extracted text. It is not an AI diagnosis.",
    "",
]

if details:
    output.extend(["## Recognized Patient Details and Vital Signs", ""])
    for label, value in details.items():
        output.append(f"- **{label}:** {value}")
    output.append("")

preferred_order = [
    "General Report Information",
    "Patient Details",
    "Medical History and Symptoms",
    "Vital Signs",
    "Laboratory Results",
    "Imaging and Scan Findings",
    "Doctor's Observations",
    "Medications and Advice",
    "Follow-up and Next Steps",
]

# Avoid repeating patient/vital lines already shown in the
# recognized-details section.
for section_name in preferred_order:
    values = sections.get(section_name, [])

    if not values:
        continue

    output.extend([f"## {section_name}", ""])

    for value in values:
        cleaned = clean_line(value)

        if not cleaned:
            continue

        # Skip headings accidentally retained by OCR.
        if normalize_heading(cleaned) in HEADINGS:
            continue

        output.append(f"- {cleaned}")

    output.append("")

# Include any additional sections not listed above.
for section_name, values in sections.items():
    if section_name in preferred_order or not values:
        continue

    output.extend([f"## {section_name}", ""])
    output.extend(f"- {clean_line(value)}" for value in values)
    output.append("")

output.extend([
    "## Laboratory Results Review",
    "",
    explain_laboratory_results(results_df),
    "",
])

# Give a quality notice when extracted text suggests OCR trouble.
if re.search(
    r"\b(?:unreadable|illegible|unclear|ocr error)\b",
    report_text,
    re.IGNORECASE,
):
    output.extend([
        "## Text Quality Notice",
        "",
        "Some content may be unclear. Compare it with the original report.",
        "",
    ])

output.extend([
    "## Important Limitations",
    "",
    "- Values are copied from extracted text and may contain OCR errors.",
    "- Missing or ambiguous information is not guessed.",
    "- Confirm names, dates, ages, units, and medication instructions "
    "against the original report.",
    "- This summary cannot determine whether a person has a disease.",
    "- Ask a qualified healthcare professional to interpret the report.",
])

return "\n".join(output)