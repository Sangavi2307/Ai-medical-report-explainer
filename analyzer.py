import re
import pandas as pd


def analyze_report(text):

    results = []

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        # Example:
        # Hemoglobin 12.8 g/dL 12.0 - 15.5

        pattern = (
            r"(.+?)\s+"
            r"(\d+(?:\.\d+)?)\s+"
            r"([a-zA-Z/%µ]+)\s+"
            r"(\d+(?:\.\d+)?)\s*[-–]\s*"
            r"(\d+(?:\.\d+)?)"
        )

        match = re.search(pattern, line)

        if match:

            test_name = match.group(1).strip()
            value = float(match.group(2))
            unit = match.group(3)

            low = float(match.group(4))
            high = float(match.group(5))

            # Compare result with reference range

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
