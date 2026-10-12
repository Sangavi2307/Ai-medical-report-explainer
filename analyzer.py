
import re
import pandas as pd


# ==================================================
# REGULAR EXPRESSIONS
# ==================================================

NUMBER = r"\d[\d,]*(?:\.\d+)?"

RANGE_PATTERN = re.compile(
    rf"({NUMBER})\s*(?:-|–|—|to)\s*({NUMBER})",
    re.IGNORECASE,
)

RESULT_NUMBER_PATTERN = re.compile(
    rf"(?<![\d.])({NUMBER})(?![\d.])"
)


# ==================================================
# TEST NAME ALIASES
# ==================================================

TEST_ALIASES = {
    "Hemoglobin": [
        "hemoglobin",
        "haemoglobin",
        "hb",
    ],
    "WBC Count": [
        "white blood cell count",
        "total leukocyte count",
        "total leucocyte count",
        "wbc count",
        "tlc",
        "wbc",
    ],
    "Platelets": [
        "platelet count",
        "platelets",
        "platelet",
        "plt",
    ],
    "Fasting Blood Sugar": [
        "fasting blood sugar",
        "fasting blood glucose",
        "fasting glucose",
        "fbs",
    ],
    "Random Blood Sugar": [
        "random blood sugar",
        "random glucose",
        "rbs",
    ],
    "Postprandial Blood Sugar": [
        "postprandial blood sugar",
        "pp blood sugar",
        "ppbs",
    ],
    "Total Cholesterol": [
        "total cholesterol",
        "cholesterol",
    ],
    "Triglycerides": [
        "triglycerides",
        "triglyceride",
    ],
    "HDL Cholesterol": [
        "hdl cholesterol",
        "hdl",
    ],
    "LDL Cholesterol": [
        "ldl cholesterol",
        "ldl",
    ],
    "Creatinine": [
        "serum creatinine",
        "creatinine",
    ],
    "Urea": [
        "blood urea",
        "serum urea",
        "urea",
    ],
    "Hemoglobin A1c": [
        "hemoglobin a1c",
        "haemoglobin a1c",
        "hba1c",
    ],
}


# ==================================================
# TEXT NORMALIZATION
# ==================================================

def normalize_text(text):
    """Normalize common OCR characters and spacing."""

    text = str(text or "")

    replacements = {
        "\u00a0": " ",
        "−": "-",
        "–": "-",
        "—": "-",
        "µ": "u",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize common OCR confusion in words only where
    # possible; do not globally replace letters in numbers.
    return text


def clean_lines(report_text):
    """Return normalized, non-empty report lines."""

    text = normalize_text(report_text)

    return [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]


# ==================================================
# IDENTIFY LABORATORY TESTS
# ==================================================

def identify_test(line):
    """Identify a supported laboratory test."""

    normalized = normalize_text(line).lower().strip()
    normalized = re.sub(r"^[\W_]+", "", normalized)

    aliases = []

    for standard_name, names in TEST_ALIASES.items():
        for alias in names:
            aliases.append((alias, standard_name))

    # Match the longest aliases first.
    aliases.sort(key=lambda item: len(item[0]), reverse=True)

    for alias, standard_name in aliases:
        pattern = rf"^{re.escape(alias)}(?:\b|(?=\s|:))"

        if re.match(pattern, normalized):
            return standard_name

    return None


def remove_test_name(line, test_name):
    """Remove the test name from the beginning of a line."""

    normalized = normalize_text(line).strip()

    aliases = sorted(
        TEST_ALIASES.get(test_name, []),
        key=len,
        reverse=True,
    )

    for alias in aliases:
        pattern = (
            rf"^\s*{re.escape(alias)}\b\s*[:=]?\s*"
        )

        updated = re.sub(
            pattern,
            "",
            normalized,
            count=1,
            flags=re.IGNORECASE,
        )

        if updated != normalized:
            return updated.strip()

    return normalized


# ==================================================
# PARSE NUMERIC RESULT AND UNIT
# ==================================================

def parse_result_line(line):
    """
    Extract the first result number and its trailing unit.

    Example:
        13.2 g/dL 12-16
    Result:
        value = 13.2
        unit = g/dL
    """

    line = normalize_text(line).strip()

    if not line:
        return None

    # Remove reference ranges before extracting the result.
    # This prevents the range limits being mistaken for results.
    cleaned = RANGE_PATTERN.sub(" ", line)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    match = RESULT_NUMBER_PATTERN.search(cleaned)

    if not match:
        return None

    number_text = match.group(1)

    try:
        value = float(number_text.replace(",", ""))
    except ValueError:
        return None

    # Remove the extracted number and keep the trailing unit.
    unit = cleaned[match.end():].strip(" :;()")

    # Avoid treating another number as a unit.
    if re.match(r"^\d", unit):
        unit = ""

    return {
        "value": value,
        "result_text": number_text,
        "unit": unit,
    }


# ==================================================
# PARSE REFERENCE RANGE
# ==================================================

def parse_range_line(line):
    """Extract a lower and upper reference limit."""

    line = normalize_text(line)

    match = RANGE_PATTERN.search(line)

    if not match:
        return None

    try:
        low = float(match.group(1).replace(",", ""))
        high = float(match.group(2).replace(",", ""))
    except ValueError:
        return None

    if low > high:
        return None

    return {
        "low": low,
        "high": high,
        "range_text": match.group(0).strip(),
    }


# ==================================================
# CLASSIFY RESULT
# ==================================================

def classify_result(value, low, high):
    """Compare a result with the detected reference range."""

    if value < low:
        return "Below Range"

    if value > high:
        return "Above Range"

    return "Within Range"


# ==================================================
# MAIN REPORT ANALYZER
# ==================================================

def analyze_report(report_text):
    """
    Extract supported laboratory results from report text.

    Returns a Pandas DataFrame with:
        Test
        Result
        Unit
        Reference Range
        Status

    A result without a detected reference range is retained
    as Not Classified. No missing reference range is invented.
    """

    columns = [
        "Test",
        "Result",
        "Unit",
        "Reference Range",
        "Status",
    ]

    if report_text is None or not str(report_text).strip():
        return pd.DataFrame(columns=columns)

    lines = clean_lines(report_text)

    results = []
    seen_tests = set()

    for i, line in enumerate(lines):

        test_name = identify_test(line)

        if not test_name:
            continue

        if test_name in seen_tests:
            continue

        result_info = None
        range_info = None

        # Search the current line and the next four lines.
        # Stop when a different laboratory test is encountered.
        for j in range(i, min(i + 5, len(lines))):

            candidate = lines[j]

            if j > i and identify_test(candidate):
                break

            if j == i:
                candidate_for_result = remove_test_name(
                    candidate,
                    test_name,
                )
            else:
                candidate_for_result = candidate

            # Look for the result.
            if result_info is None:
                result_info = parse_result_line(
                    candidate_for_result
                )

            # Look for the reference range in the original line.
            if range_info is None:
                range_info = parse_range_line(candidate)

            if result_info and range_info:
                break

        # No numerical result: skip this test.
        if result_info is None:
            continue

        # Classify only when the report provides a detectable range.
        if range_info is not None:
            status = classify_result(
                result_info["value"],
                range_info["low"],
                range_info["high"],
            )

            reference_range = range_info["range_text"]

        else:
            status = "Not Classified"
            reference_range = "Not detected"

        unit = result_info["unit"]

        # Display the micro-litre symbol where applicable.
        unit = re.sub(
            r"(?i)/uL\b",
            "/µL",
            unit,
        )

        results.append({
            "Test": test_name,
            "Result": result_info["result_text"],
            "Unit": unit,
            "Reference Range": reference_range,
            "Status": status,
        })

        seen_tests.add(test_name)

    return pd.DataFrame(results, columns=columns)
