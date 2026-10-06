import re
import pandas as pd


def analyze_report(text):

    results = []

    lines = [
        re.sub(r"\s+", " ", line.strip())
        for line in text.splitlines()
        if line.strip()
    ]

    skip_words = {
        "patient information",
        "patient name",
        "age / gender",
        "patient id",
        "date of visit",
        "consulting doctor",
        "clinical details",
        "chief complaint",
        "duration",
        "temperature",
        "blood pressure",
        "pulse rate",
        "laboratory results",
        "test",
        "result",
        "reference range",
        "assessment",
        "advice"
    }

    i = 0

    while i < len(lines):

        line = lines[i]

        if line.lower() in skip_words:
            i += 1
            continue

        if i + 2 < len(lines):

            test_name = line
            result_line = lines[i + 1]
            reference_line = lines[i + 2]

            result_match = re.match(
                r"^([\d,]+(?:\.\d+)?)\s*"
                r"(lakh|[a-zA-Zµμ/%]+(?:/[a-zA-Zµμ]+)?)$",
                result_line,
                re.IGNORECASE
            )

            range_match = re.match(
                r"^([\d,.]+)\s*[-–]\s*([\d,.]+)"
                r"\s*[a-zA-Zµμ/%]*(?:/[a-zA-Zµμ]+)?$",
                reference_line
            )

            less_match = re.match(
                r"^<\s*([\d,.]+)",
                reference_line
            )

            if result_match and (range_match or less_match):

                value_text = result_match.group(1).replace(",", "")
                unit = result_match.group(2)

                try:
                    value = float(value_text)
                except ValueError:
                    i += 1
                    continue

                if range_match:

                    low = float(
                        range_match.group(1).replace(",", "")
                    )

                    high = float(
                        range_match.group(2).replace(",", "")
                    )

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
                        "Reference Range": f"{low:g} - {high:g}",
                        "Status": status
                    })

                    i += 3
                    continue

                if less_match:

                    high = float(
                        less_match.group(1).replace(",", "")
                    )

                    if value < high:
                        status = "Within Range"
                    else:
                        status = "Above Range"

                    results.append({
                        "Test": test_name,
                        "Result": value,
                        "Unit": unit,
                        "Reference Range": f"< {high:g}",
                        "Status": status
                    })

                    i += 3
                    continue

        i += 1

    if results:

        dataframe = pd.DataFrame(results)

        dataframe = dataframe.drop_duplicates(
            subset=["Test"],
            keep="first"
        )

        return dataframe

    return pd.DataFrame(
        columns=[
            "Test",
            "Result",
            "Unit",
            "Reference Range",
            "Status"
        ]
    )
    
