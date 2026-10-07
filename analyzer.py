import re
import pandas as pd


# =========================================================
# MEDICAL REPORT ANALYZER
# Works with PDF extracted text + OCR text
# =========================================================


# ---------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------

def analyze_report(text):

    if not text or not text.strip():

        return empty_dataframe()


    # -----------------------------------------------------
    # Clean the extracted PDF/OCR text
    # -----------------------------------------------------

    lines = clean_lines(text)

    if not lines:

        return empty_dataframe()


    results = []


    # -----------------------------------------------------
    # 1. Normalize common OCR mistakes
    # -----------------------------------------------------

    normalized_lines = []

    for line in lines:

        normalized_lines.append(
            normalize_ocr_text(line)
        )


    # -----------------------------------------------------
    # 2. Detect results from separate lines
    #
    # Example:
    #
    # Hemoglobin
    # 13.2 g/dL
    # 12-16 g/dL
    # -----------------------------------------------------

    results.extend(
        parse_separate_line_results(
            normalized_lines
        )
    )


    # -----------------------------------------------------
    # 3. Detect results where everything is on one line
    #
    # Example:
    #
    # Hemoglobin 13.2 g/dL 12-16 g/dL
    # -----------------------------------------------------

    results.extend(
        parse_same_line_results(
            normalized_lines
        )
    )


    # -----------------------------------------------------
    # 4. Detect "Reference Range" format
    #
    # Example:
    #
    # Hemoglobin 13.2 g/dL
    # Reference Range: 12-16 g/dL
    # -----------------------------------------------------

    results.extend(
        parse_reference_range_format(
            normalized_lines
        )
    )


    # -----------------------------------------------------
    # 5. Special handling for platelet/lakh values
    #
    # Example:
    #
    # Platelets
    # 2.45 lakh/uL
    # 1.5-4.5 lakh/uL
    # -----------------------------------------------------

    results.extend(
        parse_platelet_results(
            normalized_lines
        )
    )


    # -----------------------------------------------------
    # 6. Remove invalid results
    # -----------------------------------------------------

    results = [
        result
        for result in results
        if valid_result(result)
    ]


    # -----------------------------------------------------
    # 7. Remove duplicates
    # -----------------------------------------------------

    if not results:

        return empty_dataframe()


    dataframe = pd.DataFrame(results)


    # Normalize test names

    dataframe["Test"] = (
        dataframe["Test"]
        .astype(str)
        .str.strip()
    )


    # Remove duplicate tests

    dataframe = dataframe.drop_duplicates(
        subset=["Test"],
        keep="first"
    )


    # -----------------------------------------------------
    # 8. Final column order
    # -----------------------------------------------------

    dataframe = dataframe[
        [
            "Test",
            "Result",
            "Unit",
            "Reference Range",
            "Status"
        ]
    ]


    return dataframe.reset_index(drop=True)


# =========================================================
# CLEAN LINES
# =========================================================

def clean_lines(text):

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # Replace repeated spaces

        line = re.sub(
            r"\s+",
            " ",
            line
        )

        # Normalize different dash characters

        line = line.replace("–", "-")
        line = line.replace("—", "-")
        line = line.replace("−", "-")

        lines.append(line)


    return lines


# =========================================================
# OCR NORMALIZATION
# =========================================================

def normalize_ocr_text(line):

    # Common OCR unit mistakes

    replacements = {

        "gid": "g/dL",
        "gld": "g/dL",
        "g/dl": "g/dL",

        "mg/dl": "mg/dL",
        "mgldl": "mg/dL",

        "ug/ml": "µg/mL",
        "ug/mL": "µg/mL",

        "/ul": "/µL",
        "/uL": "/µL",
        "/UL": "/µL",

        "ul": "µL",
        "uL": "µL",
        "UL": "µL",

        "lakh/ul": "lakh/µL",
        "lakh/uL": "lakh/µL",
        "lakh/UL": "lakh/µL",

        "lakhiL": "lakh/µL",
        "lakhuL": "lakh/µL",

        "mmol/l": "mmol/L",
        "umol/l": "µmol/L",

        "ng/ml": "ng/mL",
        "pg/ml": "pg/mL",

    }


    for old, new in replacements.items():

        line = line.replace(
            old,
            new
        )


    # OCR sometimes adds brackets around numbers

    line = re.sub(
        r"[\[\]]",
        "",
        line
    )


    return line


# =========================================================
# EMPTY DATAFRAME
# =========================================================

def empty_dataframe():

    return pd.DataFrame(
        columns=[
            "Test",
            "Result",
            "Unit",
            "Reference Range",
            "Status"
        ]
    )


# =========================================================
# TEST NAME FILTER
# =========================================================

def is_valid_test_name(name):

    if not name:
        return False


    name = name.strip()


    if len(name) < 2:
        return False


    lower = name.lower()


    ignored = {

        "test",
        "result",
        "results",
        "reference",
        "reference range",
        "normal range",
        "ref range",

        "laboratory",
        "laboratory results",
        "laboratory test results",

        "patient",
        "patient information",
        "patient name",
        "patient id",

        "age",
        "age / gender",
        "age/gender",

        "date",
        "date of visit",

        "doctor",
        "consulting doctor",

        "clinical details",
        "chief complaint",
        "duration",

        "temperature",
        "blood pressure",
        "pulse",
        "pulse rate",

        "assessment",
        "advice",

        "sample medical report",

    }


    if lower in ignored:
        return False


    # Do not accept lines containing only numbers

    if re.fullmatch(
        r"[\d\s.,/%:-]+",
        name
    ):
        return False


    return True


# =========================================================
# NUMBER
# =========================================================

NUMBER = r"\d+(?:,\d{3})*(?:\.\d+)?"


# =========================================================
# UNIT
# =========================================================

UNIT = (
    r"(?:"
    r"g/dL|"
    r"mg/dL|"
    r"mg/L|"
    r"g/L|"
    r"mmol/L|"
    r"µmol/L|"
    r"ng/mL|"
    r"pg/mL|"
    r"µg/mL|"
    r"lakh/µL|"
    r"/µL|"
    r"µL|"
    r"%|"
    r"bpm"
    r")"
)


# =========================================================
# CONVERT NUMBER
# =========================================================

def number_to_float(value):

    value = value.replace(
        ",",
        ""
    )

    try:

        return float(value)

    except ValueError:

        return None


# =========================================================
# STATUS
# =========================================================

def calculate_status(
    value,
    low=None,
    high=None,
    operator=None
):

    if operator == "<":

        if value < high:
            return "Within Range"

        return "Above Range"


    if operator == ">":

        if value > low:
            return "Within Range"

        return "Below Range"


    if low is not None and high is not None:

        if value < low:
            return "Below Range"

        if value > high:
            return "Above Range"

        return "Within Range"


    return "Unknown"


# =========================================================
# SEPARATE-LINE RESULTS
# =========================================================

def parse_separate_line_results(lines):

    results = []


    for i in range(len(lines) - 2):

        test_name = lines[i].strip()

        if not is_valid_test_name(test_name):
            continue


        result_line = lines[i + 1].strip()

        reference_line = lines[i + 2].strip()


        # -------------------------------------------------
        # Normal result
        #
        # 13.2 g/dL
        # -------------------------------------------------

        result_match = re.fullmatch(

            rf"({NUMBER})\s*({UNIT})",

            result_line,

            re.IGNORECASE
        )


        if not result_match:
            continue


        value = number_to_float(
            result_match.group(1)
        )

        unit = result_match.group(2)


        if value is None:
            continue


        # -------------------------------------------------
        # Normal range
        #
        # 12-16 g/dL
        # -------------------------------------------------

        range_match = re.fullmatch(

            rf"({NUMBER})\s*-\s*({NUMBER})"
            rf"(?:\s*({UNIT}))?",

            reference_line,

            re.IGNORECASE
        )


        if range_match:

            low = number_to_float(
                range_match.group(1)
            )

            high = number_to_float(
                range_match.group(2)
            )


            if low is None or high is None:
                continue


            status = calculate_status(
                value,
                low,
                high
            )


            results.append({

                "Test": clean_test_name(
                    test_name
                ),

                "Result": value,

                "Unit": unit,

                "Reference Range":
                    f"{low:g} - {high:g}",

                "Status": status

            })


            continue


        # -------------------------------------------------
        # Less-than reference
        #
        # < 5 mg/dL
        # -------------------------------------------------

        less_match = re.fullmatch(

            rf"<\s*({NUMBER})"
            rf"(?:\s*({UNIT}))?",

            reference_line,

            re.IGNORECASE
        )


        if less_match:

            high = number_to_float(
                less_match.group(1)
            )


            if high is None:
                continue


            status = calculate_status(
                value,
                high=high,
                operator="<"
            )


            results.append({

                "Test": clean_test_name(
                    test_name
                ),

                "Result": value,

                "Unit": unit,

                "Reference Range":
                    f"< {high:g}",

                "Status": status

            })


    return results


# =========================================================
# SAME-LINE RESULTS
# =========================================================

def parse_same_line_results(lines):

    results = []


    for line in lines:

        # ---------------------------------------------
        # Example:
        #
        # Hemoglobin 13.2 g/dL 12-16 g/dL
        # ---------------------------------------------

        pattern = re.compile(

            rf"^(.+?)\s+"
            rf"({NUMBER})\s*"
            rf"({UNIT})\s+"
            rf"({NUMBER})\s*-\s*"
            rf"({NUMBER})"
            rf"(?:\s*({UNIT}))?$",

            re.IGNORECASE
        )


        match = pattern.match(line)


        if not match:
            continue


        test_name = match.group(1).strip()


        if not is_valid_test_name(test_name):
            continue


        value = number_to_float(
            match.group(2)
        )

        unit = match.group(3)

        low = number_to_float(
            match.group(4)
        )

        high = number_to_float(
            match.group(5)
        )


        if (
            value is None
            or low is None
            or high is None
        ):
            continue


        status = calculate_status(
            value,
            low,
            high
        )


        results.append({

            "Test": clean_test_name(
                test_name
            ),

            "Result": value,

            "Unit": unit,

            "Reference Range":
                f"{low:g} - {high:g}",

            "Status": status

        })


    return results


# =========================================================
# REFERENCE RANGE FORMAT
# =========================================================

def parse_reference_range_format(lines):

    results = []


    for i in range(len(lines) - 1):

        line = lines[i]


        # ---------------------------------------------
        # Example:
        #
        # Hemoglobin 13.2 g/dL
        # Reference Range: 12-16 g/dL
        # ---------------------------------------------

        result_pattern = re.compile(

            rf"^(.+?)\s+"
            rf"({NUMBER})\s*"
            rf"({UNIT})$",

            re.IGNORECASE
        )


        result_match = result_pattern.match(
            line
        )


        if not result_match:
            continue


        test_name = result_match.group(1).strip()


        if not is_valid_test_name(test_name):
            continue


        value = number_to_float(
            result_match.group(2)
        )

        unit = result_match.group(3)


        next_line = lines[i + 1]


        reference_pattern = re.compile(

            rf"(?:reference range|normal range|ref range)"
            rf"\s*:?\s*"
            rf"({NUMBER})\s*-\s*"
            rf"({NUMBER})",

            re.IGNORECASE
        )


        reference_match = reference_pattern.search(
            next_line
        )


        if not reference_match:
            continue


        low = number_to_float(
            reference_match.group(1)
        )

        high = number_to_float(
            reference_match.group(2)
        )


        if (
            value is None
            or low is None
            or high is None
        ):
            continue


        status = calculate_status(
            value,
            low,
            high
        )


        results.append({

            "Test": clean_test_name(
                test_name
            ),

            "Result": value,

            "Unit": unit,

            "Reference Range":
                f"{low:g} - {high:g}",

            "Status": status

        })


    return results


# =========================================================
# PLATELET / LAKH FORMAT
# =========================================================

def parse_platelet_results(lines):

    results = []


    platelet_names = (
        "platelet",
        "platelets",
        "platelet count",
        "plt"
    )


    for i in range(len(lines) - 2):

        test_name = lines[i].strip().lower()


        if test_name not in platelet_names:
            continue


        result_line = lines[i + 1]

        reference_line = lines[i + 2]


        # -------------------------------------------------
        # Result:
        #
        # 2.45 lakh/µL
        # -------------------------------------------------

        result_match = re.search(

            rf"({NUMBER})\s*"
            rf"lakh\s*/?\s*µ?l",

            result_line,

            re.IGNORECASE
        )


        if not result_match:
            continue


        value = number_to_float(
            result_match.group(1)
        )


        # -------------------------------------------------
        # Reference:
        #
        # 1.5-4.5 lakh/µL
        # -------------------------------------------------

        range_match = re.search(

            rf"({NUMBER})\s*-\s*"
            rf"({NUMBER})\s*"
            rf"lakh\s*/?\s*µ?l",

            reference_line,

            re.IGNORECASE
        )


        if not range_match:
            continue


        low = number_to_float(
            range_match.group(1)
        )

        high = number_to_float(
            range_match.group(2)
        )


        if (
            value is None
            or low is None
            or high is None
        ):
            continue


        status = calculate_status(
            value,
            low,
            high
        )


        results.append({

            "Test": "Platelets",

            "Result": value,

            "Unit": "lakh/µL",

            "Reference Range":
                f"{low:g} - {high:g} lakh/µL",

            "Status": status

        })


    return results


# =========================================================
# CLEAN TEST NAME
# =========================================================

def clean_test_name(name):

    name = name.strip()


    # Remove trailing colon

    name = name.rstrip(":")


    # Remove accidental OCR punctuation

    name = re.sub(
        r"^[^A-Za-z]+",
        "",
        name
    )


    return name.strip()


# =========================================================
# VALIDATE RESULT
# =========================================================

def valid_result(result):

    required_columns = {

        "Test",
        "Result",
        "Unit",
        "Reference Range",
        "Status"

    }


    if not required_columns.issubset(
        result.keys()
    ):

        return False


    if not result["Test"]:
        return False


    if result["Result"] is None:
        return False


    if result["Status"] == "Unknown":
        return False


    return True
