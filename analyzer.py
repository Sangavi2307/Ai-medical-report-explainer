import re
import pandas as pd


def analyze_report(text):

    results = []

    # Split extracted PDF text into lines
    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Format:
        # Test Name 12.8 g/dL 12.0 - 15.5 g/dL
        pattern = re.search(
            r"^(.+?)\s+"
            r"(\d+(?:\.\d+)?)\s+"
            r"([A-Za-z/%µ]+(?:/[A-Za-z]+)?)\s+"
            r"(\d+(?:\.\d+)?)\s*[-–]\s*"
            r"(\d+(?:\.\d+)?)\s*"
            r"([A-Za-z/%µ]+(?:/[A-Za-z]+)?)?$",
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
