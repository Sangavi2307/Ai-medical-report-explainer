import re
import pandas as pd


def analyze_report(text):

    results = []

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Find numbers in the line
        numbers = re.findall(r"\d+(?:\.\d+)?", line)

        # Need at least 3 numbers:
        # Result + Low + High
        if len(numbers) < 3:
            continue

        try:
            value = float(numbers[0])
            low = float(numbers[-2])
            high = float(numbers[-1])
        except ValueError:
            continue

        # Check whether low < high
        if low >= high:
            continue

        # Test name
        test_name = re.sub(
            r"\d+(?:\.\d+)?",
            "",
            line,
            count=1
        ).strip()

        # Remove reference range from test name
        test_name = re.sub(
            r"\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?",
            "",
            test_name
        ).strip()

        if not test_name:
            continue

        # Find unit
        unit_match = re.search(
            r"(mg/dL|g/dL|mmol/L|U/L|IU/L|mL|min|%|pg/mL|ng/mL|cells/µL|cells/uL)",
            line,
            re.IGNORECASE
        )

        unit = unit_match.group(1) if unit_match else ""

        # Determine status
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
