
import re
import pandas as pd

COLUMNS = ["Test", "Result", "Unit", "Reference Range", "Status"]

KNOWN_TESTS = [
    "hemoglobin", "haemoglobin", "wbc", "white blood cell",
    "rbc", "red blood cell", "platelet", "platelets",
    "fasting blood sugar", "blood sugar", "glucose",
    "total cholesterol", "hdl cholesterol", "ldl cholesterol",
    "triglycerides", "creatinine", "urea", "bilirubin",
    "sodium", "potassium", "calcium", "albumin", "protein",
    "hematocrit", "haematocrit", "mcv", "mch", "mchc",
    "neutrophils", "lymphocytes", "eosinophils", "monocytes",
    "tsh", "alt", "ast", "esr", "crp", "hba1c",
]


def extract_patient_fields(text):
    fields = {
        "Patient Name": "",
        "Age": "",
        "Gender": "",
        "Patient ID": "",
        "Report Date": "",
    }

    patterns = {
        "Patient Name": r"(?im)^\s*(?:patient name|name)\s*[:\-]\s*(.+)$",
        "Age": r"(?im)^\s*age\s*[:\-]\s*(\d{1,3}\s*(?:years?|yrs?)?)",
        "Gender": r"(?im)^\s*(?:gender|sex)\s*[:\-]\s*([A-Za-z]+)",
        "Patient ID": r"(?im)^\s*(?:patient id|patient no)\s*[:\-]\s*(.+)$",
        "Report Date": r"(?im)^\s*(?:report date|date of report|collection date)\s*[:\-]\s*(.+)$",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            fields[key] = match.group(1).strip()

    return fields


def analyze_report(report_text):
    if not isinstance(report_text, str) or not report_text.strip():
        return pd.DataFrame(columns=COLUMNS)

    rows = []
    seen = set()

    for line in report_text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue

        lower = line.lower()

        # Prefer recognized laboratory test names to avoid treating
        # every number in a medical report as a laboratory result.
        test_name = next(
            (name for name in KNOWN_TESTS if name in lower),
            None,
        )

        if test_name is None:
            continue

        # Find numeric values on the same line, including decimal values.
        # Avoid assuming which number is the result if no result is present.
        matches = list(re.finditer(
            r"(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?",
            line,
        ))

        if not matches:
            continue

        # Locate the matched test name in the original line.
        test_match = re.search(re.escape(test_name), line, re.IGNORECASE)
        if not test_match:
            continue

        tail = line[test_match.end():].strip(" :-=\t")

        # The first numeric value after the test name is a best-effort
        # result candidate. Some formats need a table-aware parser.
        result_match = re.search(
            r"[-+]?\d[\d,]*(?:\.\d+)?",
            tail,
        )
        if not result_match:
            continue

        result = result_match.group(0).replace(",", "")
        after_result = tail[result_match.end():].strip()

        unit_match = re.match(
            r"([A-Za-zµμ/%^]+(?:/[A-Za-zµμ]+)?|%|[xX]\s*10\^?\d+)",
            after_result,
        )
        unit = unit_match.group(1).strip() if unit_match else "Not extracted"

        range_match = re.search(
            r"(\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?)",
            after_result,
        )
        reference = range_match.group(1) if range_match else "Not extracted"

        # Keep one result per test and line; avoid duplicated extraction.
        key = (test_name, result, unit)
        if key in seen:
            continue
        seen.add(key)

        rows.append({
            "Test": test_name.title(),
            "Result": result,
            "Unit": unit,
            "Reference Range": reference,
            "Status": "Not evaluated",
        })

    return pd.DataFrame(rows, columns=COLUMNS)
