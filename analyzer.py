import re
import pandas as pd


def analyze_report(text):

    results = []

    # ---------------------------------------------
    # CLEAN TEXT
    # ---------------------------------------------

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        line = re.sub(r"\s+", " ", line)

        line = line.replace("–", "-")
        line = line.replace("—", "-")
        line = line.replace("−", "-")

        lines.append(line)


    # ---------------------------------------------
    # SKIP HEADINGS
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
    # NUMBER
    # ---------------------------------------------

    number = r"[\d,.]+"


    # ---------------------------------------------
    # NORMAL UNITS
    # ---------------------------------------------

    unit = (
        r"(?:"
        r"g/dL|mg/dL|mg/L|g/L|"
        r"/µL|/uL|/UL|"
        r"µL|uL|UL|"
        r"mmol/L|µmol/L|"
        r"ng/mL|pg/mL|"
        r"%|bpm"
        r")"
    )


    # ---------------------------------------------
    # PATTERN 1
    #
    # Hemoglobin 13.2 g/dL 12-16 g/dL
    # ---------------------------------------------

    full_text = " ".join(lines)

    pattern = re.compile(

        rf"([A-Za-z][A-Za-z0-9 ()/%-]{{2,40}})"
        rf"\s+"
        rf"({number})\s*"
        rf"({unit})"
        rf"\s+"
        rf"({number})\s*-\s*"
        rf"({number})"
        rf"\s*({unit})?",

        re.IGNORECASE
    )


    for match in pattern.finditer(full_text):

        test_name = match.group(1).strip()

        if test_name.lower() in skip_words:
            continue

        value = float(
            match.group(2).replace(",", "")
        )

        result_unit = match.group(3)

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
            "Unit": result_unit,
            "Reference Range": f"{low:g} - {high:g}",
            "Status": status
        })


    # ---------------------------------------------
    # PATTERN 2
    #
    # Platelets 2.45 lakh/uL 1.5-4.5 lakh/uL
    #
    # Also handles OCR:
    # 2.45 lakhiL 15-45 lakh/ul
    # ---------------------------------------------

    platelet_pattern = re.compile(

        rf"(Platelets?)"
        rf"\s*"
        rf"[\[\(]?"
        rf"({number})"
        rf"\s*"
        rf"(?:lakh|lakhiL|lakhuL|lakh)"
        rf"\s*(?:/|)"
        rf"(?:µL|uL|ul|iL|IL)?"
        rf"\s*"
        rf""
        rf"({number})"
        rf"\s*-\s*"
        rf"({number})"
        rf"\s*"
        rf"(?:lakh|lakhiL|lakhuL|lakh)"
        rf"\s*(?:/|)"
        rf"(?:µL|uL|ul|iL|IL)?",

        re.IGNORECASE
    )


    for match in platelet_pattern.finditer(full_text):

        test_name = "Platelets"

        value = float(
            match.group(2).replace(",", "")
        )

        low = float(
            match.group(3).replace(",", "")
        )

        high = float(
            match.group(4).replace(",", "")
        )

        # OCR may read 1.5 as 15.
        # If reference values are 15-45,
        # convert them to 1.5-4.5.
        if low >= 10 and high >= 10:

            low = low / 10
            high = high / 10

        if value < low:

            status = "Below Range"

        elif value > high:

            status = "Above Range"

        else:

            status = "Within Range"


        results.append({

            "Test": test_name,

            "Result": value,

            "Unit": "lakh/µL",

            "Reference Range":
                f"{low:g} - {high:g} lakh/µL",

            "Status": status

        })


    # ---------------------------------------------
    # PATTERN 3
    #
    # Separate lines:
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

                rf"^({number})\s*({unit})$",

                result_line,

                re.IGNORECASE
            )


            range_match = re.match(

                rf"^({number})\s*-\s*({number})"
                rf"\s*({unit})?$",

                reference_line,

                re.IGNORECASE
            )


            if result_match and range_match:

                value = float(
                    result_match.group(1).replace(",", "")
                )

                result_unit = result_match.group(2)

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

                    "Unit": result_unit,

                    "Reference Range":
                        f"{low:g} - {high:g}",

                    "Status": status

                })


        i += 1


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
