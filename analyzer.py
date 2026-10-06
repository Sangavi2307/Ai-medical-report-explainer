import re
import pandas as pd


def analyze_report(text):

    results = []

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Remove extra spaces
        line = re.sub(r"\s+", " ", line)

        # Pattern:
        # Hemoglobin 12.8 g/dL 12.0 - 15.5
        pattern = re.search(
            r"^(.+?)\s+"
            r"([\d,]+(?:\.\d+)?)\s+"
            r"([a-zA-Z/%µμ]+)"
            r"\s+"
            r"(?:(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)"
            r"|<\s*(\d+(?:\.\d+)?))"
            r"\s*$",
            line
        )

        if not pattern:
            continue

        test_name = pattern.group(1).strip()

        value = float(
            pattern.group(2).replace(",", "")
        )

        unit = pattern.group(3)

        low = pattern.group(4)
        high = pattern.group(5)
        upper_limit = pattern.group(6)

        # Normal reference range
        if low is not None and high is not None:

            low = float(low)
            high = float(high)

            if value < low:
                status = "Below Range"

            elif value > high:
                status = "Above Range"

            else:
                status = "Within Range"

            reference_range = f"{low:g} - {high:g}"

        # Reference such as < 200
        elif upper_limit is not None:

            upper_limit = float(upper_limit)

            if value < upper_limit:
                status = "Within Range"

            else:
                status = "Above Range"

            reference_range = f"< {upper_limit:g}"

        else:
            continue

        results.append({
            "Test": test_name,
            "Result": value,
            "Unit": unit,
            "Reference Range": reference_range,
            "Status": status
        })

    return pd.DataFrame(results)
