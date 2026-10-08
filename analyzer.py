import re
import pandas as pd


# =========================================================
# MEDICAL REPORT ANALYZER
# =========================================================

NUMBER = r"\d+(?:,\d{3})*(?:\.\d+)?"

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
# CLEAN LINES
# =========================================================

def clean_lines(text):

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        line = re.sub(
            r"\s+",
            " ",
            line
        )

        line = line.replace("–", "-")
        line = line.replace("—", "-")
        line = line.replace("−", "-")

        lines.append(line)

    return lines


# =========================================================
# OCR NORMALIZATION
# =========================================================

def normalize_ocr_text(line):

    line = line.strip()

    # g/dL
    line = re.sub(
        r"(?i)\bg\s*/\s*dl\b",
        "g/dL",
        line
    )

    line = re.sub(
        r"(?i)\bgld\b",
        "g/dL",
        line
    )

    line = re.sub(
        r"(?i)\bgid\b",
        "g/dL",
        line
    )

    # mg/dL
    line = re.sub(
        r"(?i)mg\s*/\s*dl",
        "mg/dL",
        line
    )

    line = re.sub(
        r"(?i)mgldl",
        "mg/dL",
        line
    )

    # Other units
    line = re.sub(
        r"(?i)ug\s*/\s*ml",
        "µg/mL",
        line
    )

    line = re.sub(
        r"(?i)ng\s*/\s*ml",
        "ng/mL",
        line
    )

    line = re.sub(
        r"(?i)pg\s*/\s*ml",
        "pg/mL",
        line
    )

    line = re.sub(
        r"(?i)mmol\s*/\s*l",
        "mmol/L",
        line
    )

    line = re.sub(
        r"(?i)umol\s*/\s*l",
        "µmol/L",
        line
    )

    # /uL and /ul
    line = re.sub(
        r"(?i)/\s*u[lI]\b",
        "/µL",
        line
    )

    # lakh/uL
    line = re.sub(
        r"(?i)lakh\s*/\s*u[lI]\b",
        "lakh/µL",
        line
    )

    # OCR sometimes reads /µL as "ful."
    line = re.sub(
        r"(?i)\bful\.?\b",
        "/µL",
        line
    )

    # Remove square brackets
    line = line.replace("[", "")
    line = line.replace("]", "")

    return line


# =========================================================
# VALID TEST NAME
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

    if re.fullmatch(
        r"[\d\s.,/%:-]+",
        name
    ):
        return False

    return True


# =========================================================
# NUMBER CONVERSION
# =========================================================

def number_to_float(value):

    try:

        return float(
            str(value).replace(",", "")
        )

    except (ValueError, TypeError):

        return None


# =========================================================
# STATUS
# =========================================================

def calculate_status(
    value,
    low=None,
    high=None
):

    if low is None or high is None:
        return "Unknown"

    if value < low:
        return "Below Range"

    if value > high:
        return "Above Range"

    return "Within Range"


# =========================================================
# CLEAN TEST NAME
# =========================================================

def clean_test_name(name):

    name = name.strip()

    name = name.rstrip(":")

    name = re.sub(
        r"^[^A-Za-z]+",
        "",
        name
    )

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name.strip()


# =========================================================
# ADD RESULT
# =========================================================

def add_result(
    results,
    test,
    value,
    unit,
    low,
    high
):

    test = clean_test_name(test)

    if not is_valid_test_name(test):
        return

    if value is None:
        return

    if low is None or high is None:
        return

    status = calculate_status(
        value,
        low,
        high
    )

    if status == "Unknown":
        return

    results.append({
        "Test": test,
        "Result": value,
        "Unit": unit,
        "Reference Range": f"{low:g} - {high:g}",
        "Status": status
    })


# =========================================================
# 1. SEPARATE LINE FORMAT
#
# Hemoglobin
# 13.2 g/dL
# 12-16 g/dL
# =========================================================

def parse_separate_line_results(lines):

    results = []

    for i in range(len(lines) - 2):

        test_name = lines[i]

        result_line = lines[i + 1]

        reference_line = lines[i + 2]

        if not is_valid_test_name(test_name):
            continue

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

        range_match = re.fullmatch(
            rf"({NUMBER})\s*-\s*"
            rf"({NUMBER})"
            rf"(?:\s*({UNIT}))?",
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

        add_result(
            results,
            test_name,
            value,
            unit,
            low,
            high
        )

    return results


# =========================================================
# 2. SAME LINE FORMAT
#
# Hemoglobin 13.2 g/dL 12-16 g/dL
# =========================================================

def parse_same_line_results(lines):

    results = []

    pattern = re.compile(
        rf"^(.+?)\s+"
        rf"({NUMBER})\s*"
        rf"({UNIT})\s+"
        rf"({NUMBER})\s*-\s*"
        rf"({NUMBER})"
        rf"(?:\s*({UNIT}))?$",
        re.IGNORECASE
    )

    for line in lines:

        match = pattern.match(line)

        if not match:
            continue

        test_name = match.group(1)

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

        add_result(
            results,
            test_name,
            value,
            unit,
            low,
            high
        )

    return results


# =========================================================
# 3. REFERENCE RANGE FORMAT
#
# Hemoglobin 13.2 g/dL
# Reference Range: 12-16 g/dL
# =========================================================

def parse_reference_range_format(lines):

    results = []

    result_pattern = re.compile(
        rf"^(.+?)\s+"
        rf"({NUMBER})\s*"
        rf"({UNIT})$",
        re.IGNORECASE
    )

    reference_pattern = re.compile(
        rf"(?:reference range|normal range|ref range)"
        rf"\s*:?\s*"
        rf"({NUMBER})\s*-\s*"
        rf"({NUMBER})",
        re.IGNORECASE
    )

    for i in range(len(lines) - 1):

        match = result_pattern.match(
            lines[i]
        )

        if not match:
            continue

        test_name = match.group(1)

        value = number_to_float(
            match.group(2)
        )

        unit = match.group(3)

        reference_match = reference_pattern.search(
            lines[i + 1]
        )

        if not reference_match:
            continue

        low = number_to_float(
            reference_match.group(1)
        )

        high = number_to_float(
            reference_match.group(2)
        )

        add_result(
            results,
            test_name,
            value,
            unit,
            low,
            high
        )

    return results


# =========================================================
# 4. PLATELET FORMAT
#
# Platelets
# 2.45 lakh/µL
# 1.5-4.5 lakh/µL
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

        test_name = lines[i].lower().strip()

        if test_name not in platelet_names:
            continue

        result_match = re.search(
            rf"({NUMBER})\s*"
            rf"lakh\s*/?\s*µ?l",
            lines[i + 1],
            re.
