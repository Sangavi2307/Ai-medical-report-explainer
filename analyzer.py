
import re
import pandas as pd

COLUMNS = ["Test", "Result", "Unit", "Reference Range", "Status"]

def extract_patient_fields(text):
    fields = {
        "Patient Name": "",
        "Age": "",
        "Gender": "",
        "Patient ID": "",
        "Date of Visit": "",
    }

    patterns = {
        "Patient Name": r"(?im)^\s*Patient Name\s*[:\-]\s*(.+)$",
        "Age": r"(?im)^\s*Age\s*[:\-]\s*(\d{1,3}\s*(?:years?|yrs?)?)",
        "Gender": r"(?im)^\s*(?:Gender|Sex)\s*[:\-]\s*([A-Za-z]+)",
        "Patient ID": r"(?im)^\s*Patient ID\s*[:\-]\s*(.+)$",
        "Date of Visit": r"(?im)^\s*Date of Visit\s*[:\-]\s*(.+)$",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            fields[key] = match.group(1).strip()

    return fields


def analyze_report(report_text):
    rows = []

    if not isinstance(report_text, str):
        return pd.DataFrame(columns=COLUMNS)

    # Accept simple lines such as:
    # Hemoglobin 13.2 g/dL 12-16
    # Hemoglobin: 13.2 g/dL (12-16)
    pattern = re.compile(
        r"^\s*"
        r"([A-Za-z][A-Za-z0-9 ()/%_-]{1,45}?)"
        r"\s*[:=]?\s+"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)"
        r"\s*"
        r"([A-Za-zµμ/%^0-9.]+)?"
        r"(?:\s+"
        r"[\(\[]?\s*"
        r"([0-9]+(?:\.[0-9]+)?\s*[-–]\s*[0-9]+(?:\.[0-9]+)?)"
        r"\s*[\)\]]?)?"
        r"\s*$"
    )

    for line in report_text.splitlines():
        line = line.strip()
        if not line:
            continue

        match = pattern.match(line)
        if not match:
            continue

        test = match.group(1).strip().rstrip(":=")
        value = match.group(2).replace(",", "")
        unit = (match.group(3) or "").strip()
        reference = (match.group(4) or "").strip()

        # Exclude obvious patient metadata from laboratory results.
        if test.lower() in {
            "age", "patient id", "date", "date of visit",
            "patient name", "gender", "sex"
        }:
            continue

        rows.append({
            "Test": test,
            "Result": value,
            "Unit": unit or "Not extracted",
            "Reference Range": reference or "Not extracted",
            "Status": "Not evaluated",
        })

    return pd.DataFrame(rows, columns=COLUMNS)
