
import re
import pandas as pd

TEST_PATTERNS = {
    "Hemoglobin": r"hemoglobin|haemoglobin|\bhb\b",
    "WBC": r"white blood cell|wbc|total leukocyte count",
    "Platelet Count": r"platelet count|platelets",
    "Fasting Blood Sugar": r"fasting blood sugar|fasting glucose",
    "Blood Sugar": r"blood glucose|random blood sugar",
    "Creatinine": r"creatinine",
    "Urea": r"\burea\b",
    "Total Cholesterol": r"total cholesterol",
}

def analyze_report(text):
    results = []

    if not text:
        return pd.DataFrame(
            columns=["Test", "Value", "Unit", "Status"]
        )

    for line in text.splitlines():
        line_lower = line.lower()

        matched_test = None

        for test, pattern in TEST_PATTERNS.items():
            if re.search(pattern, line_lower):
                matched_test = test
                break

        if not matched_test:
            continue

        match = re.search(
            r"(-?\d+(?:,\d{3})*(?:\.\d+)?)\s*"
            r"(mg/dl|g/dl|mmol/l|cells/u[lL]|/u[lL]|%)?",
            line,
            re.IGNORECASE,
        )

        if match:
            value = float(match.group(1).replace(",", ""))
            unit = match.group(2) or ""

            results.append({
                "Test": matched_test,
                "Value": value,
                "Unit": unit,
                "Status": "Needs reference range"
            })

    return pd.DataFrame(results)
    
