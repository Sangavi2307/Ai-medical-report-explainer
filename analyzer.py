
import re
import pandas as pd


def analyze_report(report_text):
    results = []

    if not report_text:
        return pd.DataFrame(
            columns=[
                "Test",
                "Result",
                "Unit",
                "Reference Range",
                "Status"
            ]
        )

    for line in report_text.splitlines():
        line = line.strip()

        if not line:
            continue

        match = re.match(
            r"^([A-Za-z][A-Za-z0-9 ()/%_-]{1,50}?)\s*[:=]\s*(-?\d+(?:\.\d+)?)\s*([A-Za-z/%µμ]*)",
            line
        )

        if match:
            test_name = match.group(1).strip()
            result_value = match.group(2).strip()
            unit = match.group(3).strip()

            results.append({
                "Test": test_name,
                "Result": result_value,
                "Unit": unit,
                "Reference Range": "Not extracted",
                "Status": "Not evaluated"
            })

    return pd.DataFrame(
        results,
        columns=[
            "Test",
            "Result",
            "Unit",
            "Reference Range",
            "Status"
        ]
    )
