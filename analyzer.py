import re
import pandas as pd


def analyze_report(text):

    results = []

    # ---------------------------------------------
    # CLEAN OCR / PDF TEXT
    # ---------------------------------------------

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Clean repeated spaces
        line = re.sub(r"\s+", " ", line)

        # Normalize OCR dash characters
        line = line.replace("–", "-")
        line = line.replace("—", "-")
        line = line.replace("−", "-")

        lines.append(line)


    # ---------------------------------------------
    # WORDS THAT ARE NOT TEST NAMES
    # ---------------------------------------------

    skip_words = {
        "test",
        "result",
        "reference",
        "reference range",
        "normal range",
        "ref range",
        "laboratory results",
        "laboratory test results",
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
        "assessment",
        "advice",
    }


    # ---------------------------------------------
    # UNIT PATTERN
    # ---------------------------------------------

    unit_pattern = (
        r"(?:"
        r"g/dL|mg/dL|mg/L|g/L|"
        r"/µL|/uL|/UL|"
        r"µL|uL|UL|"
        r"lakh/µL|lakh/uL|"
        r"mmol/L|µmol/L|"
        r"ng/mL|pg/mL|"
        r"%|"
        r"bpm|"
        r"°F|°C"
        r")"
    )


    # ---------------------------------------------
    # NUMBER
    # ---------------------------------------------

    number_pattern = r"[\d,.]+"


    # ---------------------------------------------
    # PATTERN 1
    #
    # Hemoglobin
    # 13.2 g/dL
    # 12-16 g/dL
    # ---------------------------------------------

    i = 0

    while i < len(lines):

        test_name = lines[i].strip()

        if test_name.lower() in skip_words:
            i += 1
            continue


        if i + 2 < len(lines):

            result_line = lines[i + 1]
            reference_line = lines[i + 2]


            result_match = re.match(
                rf"^({number_pattern})\s*({unit_pattern})$",
                result_line,
                re.IGNORECASE
            )


            range_match = re.match(
                rf"^({number_pattern})\s*-\s*"
                rf"({number_pattern})\s*({unit_pattern})?$",
                reference_line,
                re.IGNORECASE
            )


            if result_match and range_match:

                value = float(
                    result_match.group(1).replace(",", "")
                )

                unit = result_match.group(2)

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


        i += 1


    # ---------------------------------------------
    # PATTERN 2
    #
    # Hemoglobin 13.2 g/dL
    # Reference Range: 12-16 g/dL
    # ---------------------------------------------

    full_text = " ".join(lines)


    pattern = re.compile(

        rf"([A-Za-z][A-Za-z0-9 ()/%-]{{2,40}})"
        rf"\s*:?\s*"
        rf"({number_pattern})\s*"
        rf"({unit_pattern})"
        rf"\s*"
        rf"(?:Reference Range|Normal Range|Ref Range)"
        rf"\s*:?\s*"
        rf"({number_pattern})\s*-\s*"
        rf"({number_pattern})",

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


    # ---------------------------------------------
    # PATTERN 3
    #
    # Hemoglobin 13.2 g/dL 12-16 g/dL
    # ---------------------------------------------

    pattern2 = re.compile(

        rf"([A-Za-z][A-Za-z0-9 ()/%-]{{2,40}})"
        rf"\s+"
        rf"({number_pattern})\s*"
        rf"({unit_pattern})"
        rf"\s+"
        rf"({number_pattern})\s*-\s*"
        rf"({number_pattern})"
        rf"\s*({unit_pattern})?",

        re.IGNORECASE

    )


    for match in pattern2.finditer(full_text):

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


    # ---------------------------------------------
    # REMOVE DUPLICATES
    # ---------------------------------------------

    if results:

        dataframe = pd.DataFrame(results)

        dataframe = dataframe.drop_duplicates(
            subset=["Test"],
            keep="first"
        )

        return dataframe


    # ---------------------------------------------
    # EMPTY RESULT
    # ---------------------------------------------

    return pd.DataFrame(
        columns=[
            "Test",
            "Result",
            "Unit",
            "Reference Range",
            "Status"
        ]
    )
