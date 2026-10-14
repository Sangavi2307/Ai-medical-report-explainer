
import re
import pandas as pd


COLUMNS = ["Test", "Result", "Unit", "Reference Range", "Status"]


def extract_patient_fields(report_text):
    fields = {
        "Patient Name": "",
        "Age": "",
        "Gender": "",
        "Report Date": "",
    }

    patterns = {
        "Patient Name": [
            r"(?im)^\s*(?:patient name|name)\s*[:\-]\s*(.+?)\s*$"
        ],
        "Age": [
            r"(?im)^\s*age\s*[:\-]\s*(\d{1,3})\s*(?:years?|yrs?)?\s*$"
        ],
        "Gender": [
            r"(?im)^\s*(?:gender|sex)\s*[:\-]\s*(male|female|other)\s*$"
        ],
        "Report Date": [
            r"(?im)^\s*(?:report date|date of report|collection date)\s*[:\-]\s*(.+?)\s*$"
        ],
    }

    for field, regexes in patterns.items():
        for pattern in regexes:
            match = re.search(pattern, report_text)
            if match:
                value = match.group(1).strip()
                # Avoid treating generic report headings as patient names.
                if field == "Patient Name" and value.lower() in {
                    "report", "medical report", "lab report"
                }:
                    continue
                fields[field] = value
                break

    return fields


def analyze_report(report_text):
    results = []

    if not isinstance(report_text, str) or not report_text.strip():
        return pd.DataFrame(columns=COLUMNS)

    for line in report_text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Example: Hemoglobin: 13.5 g/dL (12.0-16.0)
        match = re.match(
            r"^([A-Za-z][A-Za-z0-9 ()/%_-]{1,50}?)\s*[:=]\s*"
            r"(-?\d+(?:\.\d+)?)\s*"
            r"([A-Za-z/%µμ^0-9.]*)"
            r"(?:\s*[\(\[]\s*"
            r"([0-9.]+\s*[-–]\s*[0-9.]+)\s*[\)\]])?\s*$",
            line,
        )

        if not match:
            continue

        test_name = match.group(1).strip()
        result = match.group(2).strip()
        unit = match.group(3).strip()
        reference_range = match.group(4)

        results.append({
            "Test": test_name,
            "Result": result,
            "Unit": unit or "Not extracted",
            "Reference Range": reference_range or "Not extracted",
            "Status": "Not evaluated",
        })

    return pd.DataFrame(results, columns=COLUMNS)
