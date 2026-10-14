
import re
import pandas as pd


def extract_patient_fields(report_text):
    """Extract basic patient information from report text."""
    fields = {
        "Patient Name": "Not found",
        "Age / Gender": "Not found",
        "Patient ID": "Not found",
        "Date of Visit": "Not found",
        "Consulting Doctor": "Not found",
    }

    patterns = {
        "Patient Name": r"Patient Name\s*:?\s*\n?\s*([^\n]+)",
        "Age / Gender": r"Age\s*/\s*Gender\s*:?\s*\n?\s*([^\n]+)",
        "Patient ID": r"Patient ID\s*:?\s*\n?\s*([^\n]+)",
        "Date of Visit": r"Date of Visit\s*:?\s*\n?\s*([^\n]+)",
        "Consulting Doctor": r"Consulting Doctor\s*:?\s*\n?\s*([^\n]+)",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, report_text, re.IGNORECASE)
        if match:
            fields[field] = match.group(1).strip()

    return fields


def analyze_report(report_text):
    """
    Extract laboratory results from text where test names, values,
    and reference ranges may appear on separate lines.
    """

    columns = [
        "Test",
        "Result",
        "Unit",
        "Reference Range",
        "Status",
    ]

    if not report_text or not report_text.strip():
        return pd.DataFrame(columns=columns)

    text = report_text.replace("\r", "\n")
    text = text.replace("\u00a0", " ")
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"[ \t]+", " ", text)

    # Recognized names and common variations.
    test_patterns = [
        ("Hemoglobin", r"\b(?:hemoglobin|haemoglobin|hb)\b"),
        ("WBC Count", r"\b(?:wbc(?:\s+count)?|white blood cell(?:s)?(?: count)?)\b"),
        ("Platelets", r"\b(?:platelets?|platelet count)\b"),
        ("Fasting Blood Sugar", r"\b(?:fasting blood sugar|fasting glucose|fbs)\b"),
        ("Random Blood Sugar", r"\b(?:random blood sugar|random glucose|rbs)\b"),
        ("Total Cholesterol", r"\btotal cholesterol\b"),
        ("Creatinine", r"\bcreatinine\b"),
        ("Urea", r"\burea\b"),
        ("RBC Count", r"\b(?:rbc(?:\s+count)?|red blood cell(?:s)?(?: count)?)\b"),
        ("Hematocrit", r"\b(?:hematocrit|haematocrit|pcv)\b"),
        ("TSH", r"\btsh\b"),
        ("HbA1c", r"\bhba1c\b"),
        ("Sodium", r"\bsodium\b"),
        ("Potassium", r"\bpotassium\b"),
    ]

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    results = []

    def find_range(value):
        """Find a numeric reference range such as 12-16 or 70-100."""
        match = re.search(
            r"(?<![\d.])(\d+(?:,\d{3})*(?:\.\d+)?)"
            r"\s*(?:-|to)\s*"
            r"(\d+(?:,\d{3})*(?:\.\d+)?)(?![\d.])",
            value,
            re.IGNORECASE,
        )
        if match:
            return (
                float(match.group(1).replace(",", "")),
                float(match.group(2).replace(",", "")),
                match.group(0),
            )
        return None

    def parse_number(value):
        match = re.search(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", value)
        if not match:
            return None
        try:
            return float(match.group(0).replace(",", ""))
        except ValueError:
            return None

    for index, line in enumerate(lines):
        matched_test = None

        for test_name, pattern in test_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                matched_test = (test_name, pattern)
                break

        if not matched_test:
            continue

        test_name, test_pattern = matched_test

        # Collect nearby lines because some reports split table cells
        # into separate lines during PDF text extraction.
        block = " ".join(lines[index:index + 5])

        # Remove the test label so its name is not mistaken for a value.
        block_without_name = re.sub(
            test_pattern, " ", block, count=1, flags=re.IGNORECASE
        )

        # Find the first result value after the test label.
        result_value = parse_number(block_without_name)

        if result_value is None:
            continue

        # Avoid accidentally interpreting a reference-range number
        # as the result when no actual result can be found.
        range_match = find_range(block_without_name)
        if range_match and result_value == range_match[0]:
            continue

        # Extract a likely unit from the text around the result.
        unit = ""
        unit_patterns = [
            r"lakh\s*/\s*[µμu]?L",
            r"cells?\s*/\s*[µμu]?L",
            r"/\s*[µμu]?L",
            r"mg\s*/\s*dL",
            r"g\s*/\s*dL",
            r"mIU\s*/\s*L",
            r"mmol\s*/\s*L",
            r"%"
        ]

        for pattern in unit_patterns:
            unit_match = re.search(pattern, block, re.IGNORECASE)
            if unit_match:
                unit = unit_match.group(0)
                break

        # Determine status only when a range is found.
        status = "Range not recognized"
        reference_range = ""

        if range_match:
            low, high, reference_range = range_match

            if low <= result_value <= high:
                status = "Within Range"
            elif result_value < low:
                status = "Below Range"
            else:
                status = "Above Range"

        # Prevent duplicate test entries.
        if any(row["Test"] == test_name for row in results):
            continue

        results.append({
            "Test": test_name,
            "Result": result_value,
            "Unit": unit,
            "Reference Range": reference_range,
            "Status": status,
        })

    return pd.DataFrame(results, columns=columns)
