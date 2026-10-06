import re
import pandas as pd


def analyze_report(text):

    results = []
    lines = text.splitlines()

    i = 0

    while i < len(lines):

        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # Clean extra spaces
        line = re.sub(r"\s+", " ", line)

        # -------------------------------------------------
        # FORMAT 1
        # Test: 12.8 g/dL
        # Reference Range: 12.0 - 15.5
        # -------------------------------------------------

        test_match = re.match(
            r"^(.+?):\s*"
            r"([\d,]+(?:\.\d+)?)\s+"
            r"([a-zA-Z/%µμ]+(?:/[a-zA-Z]+)?)\s*$",
            line
        )

        if test_match and i + 1 < len(lines):

            test_name = test_match.group(1).strip()

            try:
                value = float(
                    test_match.group(2).replace(",", "")
                )
            except ValueError:
                i += 1
                continue

            unit = test_match.group(3)

            next_line = re.sub(
                r"\s+",
                " ",
                lines[i + 1].strip()
            )

            reference_match = re.match(
                r"^Reference Range:\s*"
                r"(\d+(?:\.\d+)?)\s*[-–]\s*"
                r"(\d+(?:\.\d+)?)\s*$",
                next_line,
                re.IGNORECASE
            )

            less_than_match = re.match(
                r"^Reference Range:\s*<\s*"
                r"(\d+(?:\.\d+)?)\s*$",
                next_line,
                re.IGNORECASE
            )

            if reference_match:

                low = float(reference_match.group(1))
                high = float(reference_match.group(2))

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

                i += 2
                continue

            elif less_than_match:

                high = float(
                    less_than_match.group(1)
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

                i += 2
                continue

        # -------------------------------------------------
        # FORMAT 2
        # Hemoglobin 12.8 g/dL 12.0 - 15.5
        # -------------------------------------------------

        normal_match = re.match(
            r"^(.+?)\s+"
            r"([\d,]+(?:\.\d+)?)\s+"
            r"([a-zA-Z/%µμ]+(?:/[a-zA-Z]+)?)\s+"
            r"(\d+(?:\.\d+)?)\s*[-–]\s*"
            r"(\d+(?:\.\d+)?)$",
            line
        )

        if normal_match:

            test_name = normal_match.group(1).strip()

            value = float(
                normal_match.group(2).replace(",", "")
            )

            unit = normal_match.group(3)

            low = float(normal_match.group(4))
            high = float(normal_match.group(5))

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

        # -------------------------------------------------
        # FORMAT 3
        # Total Cholesterol 185 mg/dL < 200
        # -------------------------------------------------

        less_match = re.match(
            r"^(.+?)\s+"
            r"([\d,]+(?:\.\d+)?)\s+"
            r"([a-zA-Z/%µμ]+(?:/[a-zA-Z]+)?)\s+"
            r"<\s*(\d+(?:\.\d+)?)$",
            line
        )

        if less_match:

            test_name = less_match.group(1).strip()

            value = float(
                less_match.group(2).replace(",", "")
            )

            unit = less_match.group(3)

            high = float(less_match.group(4))

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

        i += 1

    # Remove duplicate tests
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
