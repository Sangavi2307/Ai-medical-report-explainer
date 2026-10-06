import re
import pandas as pd


def analyze_report(text):

    results = []

    # Clean OCR/PDF text
    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:

            line = re.sub(r"\s+", " ", line)

            # Normalize different dash characters
            line = line.replace("—", "-")
            line = line.replace("–", "-")

            lines.append(line)

    skip_words = {
        "patient information",
        "patient name",
        "age / gender",
        "age/gender",
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
        "laboratory test results",
        "test",
        "result",
        "reference range",
        "reference",
        "assessment",
        "advice"
    }

    # -------------------------------------------------
    # Pattern 1
    # Test
    # 13.2 g/dL
    # 12-16 g/dL
    # -------------------------------------------------

    i = 0

    while i < len(lines):

        test_name = lines[i]

        if test_name.lower() in skip_words:
            i += 1
            continue

        if i + 2 < len(lines):

            result_line = lines[i + 1]
            reference_line = lines[i + 2]

            result_match = re.match(
                r"^([\d,]+(?:\.\d+)?)\s*"
                r"([a-zA-Zµμ/%]+(?:/[a-zA-Zµμ]+)?)$",
                result_line,
                re.IGNORECASE
            )

            range_match = re.match(
                r"^([\d,.]+)\s*-\s*([\d,.]+)"
                r"\s*([a-zA-Zµμ/%]+(?:/[a-zA-Zµμ]+)?)?$",
                reference_line,
                re.IGNORECASE
            )

            less_match = re.match(
                r"^<\s*([\d,.]+)"
                r"\s*([a-zA-Zµμ/%]+(?:/[a-zA-Zµμ]+)?)?$",
                reference_line,
                re.IGNORECASE
            )

            if result_match and (range_match or less_match):

                value = float(
                    result_match.group(1).replace(",", "")
                )

                unit = result_match.group(2)

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
                        "Reference Range":
                            f"{low:g} - {high:g}",
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
                        "Reference Range":
                            f"< {high:g}",
                        "Status": status
                    })

                    i += 3
                    continue

        i += 1

    # -------------------------------------------------
    # Pattern 2
    # Test: Hemoglobin 13.2 g/dL
    # Reference Range: 12-16 g/dL
    # -------------------------------------------------

    full_text = " ".join(lines)

    pattern = re.compile(
        r"([A-Za-z][A-Za-z0-9 ()/%-]{2,40})"
        r"\s*:?\s*"
        r"([\d,]+(?:\.\d+)?)\s*"
        r"([a-zA-Zµμ/%]+(?:/[a-zA-Zµμ]+)?)"
        r"\s*(?:Reference Range|Normal Range|Ref Range)"
        r"\s*:?\s*"
        r"([\d,.]+)\s*-\s*([\d,.]+)",
        re.IGNORECASE
    )

    for match in pattern.finditer(full_text):

        test_name = match.group(1).strip()

        if test_name.lower() in skip_words:
            continue

        value = float(
            match.group(2).replace(",", "")
        )

        unit = match.group(3)

        low = float(
            match.group(4).replace(",", "")
        )

        high = float(
            match.group(5).replace(",", "")
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
            "Reference Range":
                f"{low:g} - {high:g}",
            "Status": status
        })

    # -------------------------------------------------
    # Remove duplicate tests
    # -------------------------------------------------

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
