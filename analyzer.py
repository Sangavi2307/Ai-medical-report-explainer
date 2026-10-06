import re
import pandas as pd


def analyze_report(text):

    results = []

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Pattern for:
        # Hemoglobin 12.8 g/dL 12.0 - 15.5
        pattern = re.search(
            r"^(.+?)\s+"
            r"(\d+(?:\.\d+)?)\s+"
            r"([a-zA-Z/%µ]+)\s+"
            r"(\d+(?:\.\d+)?)\s*[-–]\s*"
            r"(\d+(?:\.\d+)?)\s*$",
            line
        )

        if pattern:

            test_name = pattern.group(1).strip()
            value = float(pattern.group(2))
            unit = pattern.group(3)

            low = float(pattern.group(4))
            high = float(pattern.group(5))

            if value < low:
                status = "Below Range"

            elif value > high:
                status = "Above Range"

            else:
                status = "Within Range"

            results.append({
                "Test": test_name,
                "Result": value,
                "Unit": unit,
                "Reference Range": f"{low} - {high}",
                "Status": status
            })

    return pd.DataFrame(results)
