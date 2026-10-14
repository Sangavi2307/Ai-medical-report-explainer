
import re
import pandas as pd


# ---------------- REPORT HEADINGS ----------------

HEADINGS = [
    "patient details",
    "patient information",
    "patient name",
    "age",
    "gender",
    "sex",
    "clinical history",
    "medical history",
    "diagnosis",
    "investigation",
    "laboratory results",
    "lab results",
    "test results",
    "complete blood count",
    "biochemistry",
    "haematology",
    "hematology",
    "impression",
    "conclusion",
    "recommendation",
]


# ---------------- CLEAN TEXT ----------------

def clean_line(line):
    """Remove unnecessary spaces from a line."""
    if not isinstance(line, str):
        return ""
    return re.sub(r"\s+", " ", line).strip()


# ---------------- PATIENT DETAILS ----------------

def extract_patient_fields(report_text):
    """Extract basic patient details when explicitly present."""
    fields = {}

    if not isinstance(report_text, str):
        return fields

    patterns = {
        "Patient Name": r"(?im)^\s*(?:patient name|name)\s*[:\-]\s*(.+)$",
        "Age": r"(?im)^\s*age\s*[:\-]\s*(.+)$",
        "Gender": r"(?im)^\s*(?:gender|sex)\s*[:\-]\s*(.+)$",
        "Report Date": r"(?im)^\s*(?:report date|date)\s*[:\-]\s*(.+)$",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, report_text)
        if match:
            fields[field] = clean_line(match.group(1))

    return fields


# ---------------- ANALYZE LAB RESULTS ----------------

def analyze_report(report_text):
    """
    Extract simple laboratory results from the supplied report text.

    Supported example:
    Hemoglobin: 13.5 g/dL

    Values are not medically classified unless reliable reference
    ranges and suitable interpretation rules are provided.
    """

    columns = [
        "Test",
        "Result",
        "Unit",
        "Reference Range",
        "Status",
    ]

    if not isinstance(report_text, str) or not report_text.strip():
        return pd.DataFrame(columns=columns)

    rows = []
    seen_tests = set()

    pattern = re.compile(
        r"^\s*"
        r"([A-Za-z][A-Za-z0-9 ()/%_.-]{1,60}?)"
        r"\s*:\s*"
        r"(-?\d+(?:\.\d+)?)"
        r"\s*"
        r"([A-Za-z/%]+)?"
        r"\s*$"
    )

    for line in report_text.splitlines():
        line = clean_line(line)
        match = pattern.match(line)

        if not match:
            continue

        test_name = clean_line(match.group(1))
        result_text = match.group(2)
        unit = match.group(3) or ""

        # Avoid repeating the same test name.
        test_key = test_name.casefold()
        if test_key in seen_tests:
            continue

        seen_tests.add(test_key)

        try:
            result = float(result_text)
        except ValueError:
            continue

        rows.append({
            "Test": test_name,
            "Result": result,
            "Unit": unit,
            "Reference Range": "Not provided",
            "Status": "Not evaluated",
        })

    return pd.DataFrame(rows, columns=columns)


# ---------------- SECTION EXTRACTION ----------------

def collect_sections(report_text):
    """Group text under simple report headings."""
    sections = {}

    if not isinstance(report_text, str):
        return sections

    current_section = "General"
    sections[current_section] = []

    for line in report_text.splitlines():
        cleaned = clean_line(line)

        if not cleaned:
            continue

        heading = cleaned.rstrip(":").strip()

        if heading.casefold() in HEADINGS:
            current_section = heading
            sections.setdefault(current_section, [])
        else:
            sections.setdefault(current_section, []).append(cleaned)

    return {
        name: "\n".join(lines)
        for name, lines in sections.items()
        if lines
    }


# ---------------- RULE-BASED EXPLANATION ----------------

def explain_laboratory_results(results_df):
    """Describe extracted fields without making a diagnosis."""
    if not isinstance(results_df, pd.DataFrame) or results_df.empty:
        return (
            "No structured laboratory results were detected. "
            "The report may use a table or a format that this "
            "basic text parser does not support."
        )

    explanations = []

    for _, row in results_df.iterrows():
        test = row.get("Test", "Unknown test")
        result = row.get("Result", "Unavailable")
        unit = row.get("Unit", "")
        reference = row.get("Reference Range", "Not provided")
        status = row.get("Status", "Not evaluated")

        value_text = f"{result} {unit}".strip()

        explanations.append(
            f"- **{test}:** {value_text}. "
            f"Reference range: {reference}. "
            f"Status: {status}."
        )

    return "\n".join(explanations)


# ---------------- COMPLETE REPORT SUMMARY ----------------

def get_report_summary(report_text):
    """Create a basic summary of the current report."""
    if not isinstance(report_text, str) or not report_text.strip():
        return "No readable text was found in the report."

    patient_fields = extract_patient_fields(report_text)
    results_df = analyze_report(report_text)

    summary = ["## Report Summary", ""]

    if patient_fields:
        summary.append("### Extracted Patient Details")
        for field, value in patient_fields.items():
            summary.append(f"- **{field}:** {value}")
        summary.append("")

    summary.append("### Laboratory Results")
    summary.append(explain_laboratory_results(results_df))
    summary.extend([
        "",
        "This summary is educational only and is not a diagnosis. "
        "Please confirm results and interpretation with a qualified "
        "healthcare professional."
    ])

    return "\n".join(summary)
