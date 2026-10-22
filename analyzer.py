
import re
import pandas as pd


# =========================================================
# SUPPORTED LAB TESTS AND COMMON ALIASES
# =========================================================

TEST_ALIASES = {
    "Fasting Blood Sugar": [
        "fasting blood sugar", "fasting glucose", "fbs"
    ],
    "Random Blood Sugar": [
        "random blood sugar", "random glucose", "rbs"
    ],
    "Hemoglobin": [
        "hemoglobin", "haemoglobin", "hb"
    ],
    "WBC Count": [
        "wbc count", "white blood cell count",
        "white blood cells", "wbc"
    ],
    "Platelets": [
        "platelet count", "platelets", "thrombocyte count"
    ],
    "RBC Count": [
        "rbc count", "red blood cell count", "rbc"
    ],
    "HbA1c": [
        "hba1c", "hb a1c", "glycated hemoglobin",
        "glycosylated hemoglobin"
    ],
    "Creatinine": [
        "serum creatinine", "creatinine"
    ],
    "Urea": [
        "blood urea", "serum urea", "urea"
    ],
    "Total Cholesterol": [
        "total cholesterol", "cholesterol"
    ],
    "LDL Cholesterol": [
        "ldl cholesterol", "ldl"
    ],
    "HDL Cholesterol": [
        "hdl cholesterol", "hdl"
    ],
    "Triglycerides": [
        "triglycerides", "triglyceride"
    ],
    "Sodium": [
        "serum sodium", "sodium"
    ],
    "Potassium": [
        "serum potassium", "potassium"
    ],
    "Calcium": [
        "serum calcium", "calcium"
    ],
    "Bilirubin": [
        "total bilirubin", "bilirubin"
    ],
    "ALT": [
        "sgpt", "alanine aminotransferase", "alt"
    ],
    "AST": [
        "sgot", "aspartate aminotransferase", "ast"
    ],
    "TSH": [
        "thyroid stimulating hormone", "tsh"
    ],
    "Vitamin D": [
        "25-oh vitamin d", "vitamin d"
    ],
    "Vitamin B12": [
        "vitamin b12", "b12"
    ],
    "ESR": [
        "erythrocyte sedimentation rate", "esr"
    ],
    "CRP": [
        "c-reactive protein", "crp"
    ],
    "Uric Acid": [
        "serum uric acid", "uric acid"
    ],
    "Albumin": [
        "serum albumin", "albumin"
    ],
    "Total Protein": [
        "total protein"
    ],
    "MCV": [
        "mean corpuscular volume", "mcv"
    ],
    "MCH": [
        "mean corpuscular hemoglobin", "mch"
    ],
    "MCHC": [
        "mean corpuscular hemoglobin concentration", "mchc"
    ],
    "Hematocrit": [
        "hematocrit", "packed cell volume", "pcv"
    ],
}


# =========================================================
# REGULAR EXPRESSIONS
# =========================================================

NUMBER_PATTERN = re.compile(
    r"(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?"
)

RANGE_PATTERN = re.compile(
    r"(?<![\w.])"
    r"([-+]?\d[\d,]*(?:\.\d+)?)"
    r"\s*(?:-|–|—|to)\s*"
    r"([-+]?\d[\d,]*(?:\.\d+)?)"
    r"(?![\d.])",
    re.IGNORECASE,
)

UNIT_PATTERN = re.compile(
    r"(%|g/dl|g/l|mg/dl|mg/l|mmol/l|"
    r"µmol/l|umol/l|ng/ml|pg/ml|"
    r"u/l|iu/l|miu/l|10\^?3/?[µu]?l|"
    r"10\^?6/?[µu]?l|cells/?[µu]?l|"
    r"fl|pg|fL|mL|ml|bpm|mm/hr|mm/h)",
    re.IGNORECASE,
)


def to_number(value):
    """Convert a numeric string into a float safely."""
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def extract_numbers(text):
    """Return numbers and their positions in text."""
    found = []

    for match in NUMBER_PATTERN.finditer(str(text)):
        value = to_number(match.group())

        if value is not None:
            found.append((value, match.start(), match.end()))

    return found


def parse_range(text):
    """Find a numeric reference interval without confusing it with the result."""
    match = RANGE_PATTERN.search(str(text))

    if not match:
        return None

    low = to_number(match.group(1))
    high = to_number(match.group(2))

    if low is None or high is None or low > high:
        return None

    return low, high, match.group(0)


def find_test(line):
    """Identify a known laboratory test in a line."""
    normalized = str(line).lower()

    # Prefer longer aliases before shorter aliases.
    aliases = []

    for canonical, names in TEST_ALIASES.items():
        for alias in names:
            aliases.append((canonical, alias))

    aliases.sort(key=lambda item: len(item[1]), reverse=True)

    for canonical, alias in aliases:
        pattern = (
            r"(?<![a-z])"
            + re.escape(alias)
            + r"(?![a-z])"
        )

        if re.search(pattern, normalized, re.IGNORECASE):
            return canonical, alias

    return None, None


def extract_unit(text):
    """Extract a recognizable laboratory unit."""
    match = UNIT_PATTERN.search(str(text))

    if match:
        return match.group(0)

    return ""


# =========================================================
# STATUS CLASSIFICATION
# =========================================================

def classify_result(test_name, result, reference_range, unit=""):
    """
    Classify against a parsed laboratory reference interval.
    HbA1c thresholds are educational screening categories only.
    """
    if result is None:
        return "Needs review"

    value = to_number(result)

    if value is None:
        return "Needs review"

    # Do not guess a reference interval for an ordinary test.
    if reference_range:
        if isinstance(reference_range, (tuple, list)):
            if len(reference_range) < 2:
                return "Needs review"

            low = to_number(reference_range[0])
            high = to_number(reference_range[1])
        else:
            parsed = parse_range(reference_range)

            if not parsed:
                return "Needs review"

            low, high, _ = parsed

        if low is None or high is None or low > high:
            return "Needs review"

        if value < low:
            return "Below range"

        if value > high:
            return "Above range"

        return "Within range"

    # Only use common screening thresholds for HbA1c.
    if str(test_name).strip().lower() == "hba1c":
        if "%" not in str(unit):
            return "Needs review"

        if value < 5.7:
            return "Below diabetes screening threshold"
        elif value < 6.5:
            return "Prediabetes screening range"
        else:
            return "Above diabetes screening threshold"

    return "Needs review"


# =========================================================
# REPORT LINE PARSING
# =========================================================

def parse_test_line(line, extra_line=""):
    """
    Parse one test from a report line and, if needed, its next line.
    Avoid using reference-range numbers as the measured result.
    """
    canonical, alias = find_test(line)

    if not canonical:
        return None

    # Remove the test name from the beginning of the line when possible.
    alias_pattern = re.compile(
        r"(?<![a-z])" + re.escape(alias) + r"(?![a-z])",
        re.IGNORECASE,
    )

    alias_match = alias_pattern.search(line)

    remainder = (
        line[alias_match.end():]
        if alias_match
        else line
    )

    # A range can be printed on the next line in some reports.
    combined = remainder

    if extra_line:
        combined += " " + extra_line

    range_info = parse_range(combined)

    if range_info:
        low, high, range_text = range_info
        range_match = RANGE_PATTERN.search(combined)

        before_range = (
            combined[:range_match.start()]
            if range_match
            else combined
        )

        numbers_before = extract_numbers(before_range)

        # Ignore numbers that are part of a test name.
        if numbers_before:
            result_value = numbers_before[0][0]
        else:
            after_range = (
                combined[range_match.end():]
                if range_match
                else ""
            )
            numbers_after = extract_numbers(after_range)
            result_value = (
                numbers_after[0][0]
                if numbers_after
                else None
            )

        reference_range = (low, high, range_text)
    else:
        range_text = ""
        reference_range = None

        numbers = extract_numbers(remainder)

        # If no result is on this line, try the next line.
        if not numbers and extra_line:
            numbers = extract_numbers(extra_line)

        result_value = numbers[0][0] if numbers else None

    if result_value is None:
        return None

    unit = extract_unit(combined)

    # The result must not be silently assigned a normal status
    # when the range is absent or ambiguous.
    status = classify_result(
        canonical,
        result_value,
        reference_range,
        unit,
    )

    return {
        "Test": canonical,
        "Result": result_value,
        "Unit": unit,
        "Reference Range": range_text,
        "Status": status,
    }


# =========================================================
# ANALYZE REPORT
# =========================================================

def analyze_report(report_text):
    """
    Convert extracted report text into a DataFrame.

    Note:
    OCR and line parsing can still be imperfect. Verify every
    extracted result against the original report.
    """
    if not report_text or not str(report_text).strip():
        return pd.DataFrame(
            columns=[
                "Test",
                "Result",
                "Unit",
                "Reference Range",
                "Status",
            ]
        )

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in str(report_text).splitlines()
        if line.strip()
    ]

    results = []
    seen_tests = set()

    for index, line in enumerate(lines):
        next_line = (
            lines[index + 1]
            if index + 1 < len(lines)
            else ""
        )

        parsed = parse_test_line(line, next_line)

        if not parsed:
            continue

        test_name = parsed["Test"]

        # Keep the first occurrence of each test to avoid duplicates.
        if test_name in seen_tests:
            continue

        seen_tests.add(test_name)
        results.append(parsed)

    return pd.DataFrame(
        results,
        columns=[
            "Test",
            "Result",
            "Unit",
            "Reference Range",
            "Status",
        ],
    )


# =========================================================
# EXTRACT PATIENT FIELDS
# =========================================================

def extract_patient_fields(report_text):
    """Extract common patient information when it is explicitly present."""
    fields = {}

    if not report_text:
        return fields

    text = str(report_text)

    patterns = {
        "patient_name": [
            r"(?:patient\s*name|name)\s*[:\-]\s*([^\n\r]+)",
        ],
        "age": [
            r"\bage\s*[:\-]\s*(\d{1,3})\s*(?:years?|yrs?)?\b",
        ],
        "gender": [
            r"\b(?:gender|sex)\s*[:\-]\s*(male|female|other)\b",
        ],
        "report_date": [
            r"(?:report\s*date|collection\s*date|date)\s*[:\-]\s*"
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        ],
        "patient_id": [
            r"(?:patient\s*id|patient\s*no|mrn|registration\s*no)"
            r"\s*[:\-]\s*([A-Za-z0-9\-\/]+)",
        ],
    }

    for field_name, expressions in patterns.items():
        for pattern in expressions:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE | re.MULTILINE,
            )

            if match:
                value = match.group(1).strip()

                # Avoid storing a long line as a patient's name.
                if field_name == "patient_name":
                    value = value.splitlines()[0][:100].strip()

                fields[field_name] = value
                break

    return fields
