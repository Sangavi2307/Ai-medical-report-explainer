
import re
import pandas as pd


COLUMNS = [
    "Test",
    "Result",
    "Unit",
    "Reference Range",
    "Status",
]


TESTS = [
    ("Hemoglobin", r"hemoglobin|haemoglobin|\bHb\b"),
    ("WBC Count", r"WBC(?:\s+Count)?|white blood cells?"),
    ("Platelets", r"platelet(?:s)?(?:\s+count)?"),
    ("Fasting Blood Sugar", r"fasting blood sugar|fasting glucose|\bFBS\b"),
    ("Random Blood Sugar", r"random blood sugar|random glucose|\bRBS\b"),
    ("RBC Count", r"RBC(?:\s+Count)?|red blood cells?"),
    ("Creatinine", r"\bcreatinine\b"),
    ("Urea", r"\burea\b"),
    ("Total Cholesterol", r"total cholesterol"),
    ("Sodium", r"\bsodium\b"),
    ("Potassium", r"\bpotassium\b"),
    ("TSH", r"\bTSH\b"),
    ("HbA1c", r"\bHbA1c\b"),
]


def extract_patient_fields(report_text):
    fields = {
        "Patient Name": "Not found",
        "Age / Gender": "Not found",
        "Patient ID": "Not found",
        "Date of Visit": "Not found",
        "Physician": "Not found",
    }

    patterns = {
        "Patient Name": r"Patient Name\s*:?\s*([^\n]+)",
        "Age / Gender": r"(?:Age\s*/\s*Gender|Age|Gender)\s*:?\s*([^\n]+)",
        "Patient ID": r"Patient ID\s*:?\s*([^\n]+)",
        "Date of Visit": r"(?:Date of Visit|Date of Examination)\s*:?\s*([^\n]+)",
        "Physician": r"(?:Physician|Consulting Doctor)\s*:?\s*([^\n]+)",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, report_text, re.IGNORECASE)

        if match:
            value = match.group(1).strip(" :\t")
            if value:
                fields[field] = value

    return fields


def analyze_report(report_text):
    if not report_text or not report_text.strip():
        return pd.DataFrame(columns=COLUMNS)

    text = report_text.replace("\r", "\n")
    text = text.replace("\u00a0", " ")
    text = text.replace("–", "-").replace("—", "-")

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]

    results = []
    seen = set()

    for index, line in enumerate(lines):
        for test_name, test_pattern in TESTS:
            if not re.search(test_pattern, line, re.IGNORECASE):
                continue

            if test_name in seen:
                continue

            # Read only a small group of nearby lines to limit
            # accidental matching with unrelated tests.
            block_lines = lines[index:index + 4]
            block = " ".join(block_lines)

            # Remove the test name before looking for numeric values.
            cleaned = re.sub(
                test_pattern,
                " ",
                block,
                count=1,
                flags=re.IGNORECASE,
            )

            # If the line is a table heading rather than a result,
            # move on.
            if re.search(
                r"\b(reference range|normal range|laboratory results)\b",
                line,
                re.IGNORECASE,
            ):
                continue

            # Find a reference range such as 12-16 or 70-100.
            range_match = re.search(
                r"(?<![\d.])(\d[\d,]*(?:\.\d+)?)\s*-\s*"
                r"(\d[\d,]*(?:\.\d+)?)(?![\d.])",
                cleaned,
            )

            reference_range = ""
            low = high = None

            if range_match:
                low = float(range_match.group(1).replace(",", ""))
                high = float(range_match.group(2).replace(",", ""))
                reference_range = range_match.group(0)

                cleaned = (
                    cleaned[:range_match.start()]
                    + " "
                    + cleaned[range_match.end():]
                )

            # Extract a result only when a numeric value is present.
            number_match = re.search(
                r"(?<![\w.])\d[\d,]*(?:\.\d+)?",
                cleaned,
            )

            if not number_match:
                continue

            value_text = number_match.group(0)
            value = float(value_text.replace(",", ""))

            # A detected range alone must not be treated as a result.
            if low is not None and value in (low, high):
                continue

            unit = ""
            unit_match = re.search(
                r"(?:lakh\s*/\s*µ?L|cells?\s*/\s*µ?L|"
                r"/\s*µ?L|mg\s*/\s*dL|g\s*/\s*dL|"
                r"mmol\s*/\s*L|mIU\s*/\s*L|%)",
                block,
                re.IGNORECASE,
            )

            if unit_match:
                unit = unit_match.group(0)

            if low is None:
                status = "Range not recognized"
            elif low <= value <= high:
                status = "Within Range"
            elif value < low:
                status = "Below Range"
            else:
                status = "Above Range"

            results.append({
                "Test": test_name,
                "Result": value,
                "Unit": unit,
                "Reference Range": reference_range,
                "Status": status,
            })

            seen.add(test_name)
            break

    return pd.DataFrame(results, columns=COLUMNS)
