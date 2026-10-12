
import re
import pandas as pd


# --------------------------------------------------
# REGULAR EXPRESSIONS
# --------------------------------------------------

NUMBER = r"\d[\d,]*(?:\.\d+)?"

RANGE_PATTERN = re.compile(
    rf"({NUMBER})\s*(?:-|–|—|to)\s*({NUMBER})",
    re.IGNORECASE,
)

RESULT_PATTERN = re.compile(
    rf"^\s*({NUMBER})\s*(.*?)\s*$"
)


# --------------------------------------------------
# TEST NAME ALIASES
# --------------------------------------------------

TEST_ALIASES = {
    "Hemoglobin": [
        "hemoglobin",
        "haemoglobin",
        "hb",
    ],
    "WBC Count": [
        "wbc count",
        "white blood cell count",
        "total leukocyte count",
        "total leucocyte count",
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
        "fasting glucose",
        "fasting blood glucose",
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


# --------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------

def normalize_text(text):
    """Normalize common OCR characters and spacing."""

    text = str(text)

    text = text.replace("\u00a0", " ")
    text = text.replace("−", "-")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("µ", "u")

    return text


def clean_lines(report_text):
    """Convert report text into clean non-empty lines."""

    text = normalize_text(report_text)

    return [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]


# --------------------------------------------------
# IDENTIFY LABORATORY TESTS
# --------------------------------------------------

def identify_test(line):
    """Return the standardized test name if recognized."""

    normalized = normalize_text(line).lower().strip()
    normalized = re.sub(r"^[\W_]+", "", normalized)

    # Check longer aliases first to avoid matching a short
    # alias before a more specific test name.
    aliases = []

    for standard_name, names in TEST_ALIASES.items():
        for alias in names:
            aliases.append((alias, standard_name))

    aliases.sort(key=lambda item: len(item[0]), reverse=True)

    for alias, standard_name in aliases:
        if re.match(
            rf"^{re.escape(alias)}(?:\b|(?=\s|:))",
            normalized,
        ):
            return standard_name

    return None


def remove_test_name(line, test_name):
    """Remove a test label from the start of a line."""

    normalized = normalize_text(line).strip()

    aliases = TEST_ALIASES.get(test_name, [])
    aliases = sorted(aliases, key=len, reverse=True)

    for alias in aliases:
        pattern = rf"^\s*{re.escape(alias)}\b\s*[:=-]?\s*"

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


# --------------------------------------------------
# PARSE RESULT AND UNIT
# --------------------------------------------------

def parse_result_line(line):
    """Extract the numeric result and its unit."""

    line = normalize_text(line)

    match = RESULT_PATTERN.match(line)

    if not match:
        return None

    number_text = match.group(1)
    remainder = match.group(2).strip()

    # A result line must not be a reference-range line.
    if RANGE_PATTERN.search(line):
        return None

    try:
        value = float(number_text.replace(",", ""))
    except ValueError:
        return None

    unit = remainder.strip(" :;")

    return {
        "value": value,
        "result_text": number_text,
        "unit": unit,
    }


# --------------------------------------------------
# PARSE REFERENCE RANGE
# --------------------------------------------------

def parse_range_line(line):
    """Extract lower and upper limits from a range line."""

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

    # Preserve the original range wording and units.
    range_text = line.strip()

    return {
        "low": low,
        "high": high,
        "range_text": range_text,
    }


# --------------------------------------------------
# CLASSIFY RESULT USING THE REPORTED RANGE
# --------------------------------------------------

def classify_result(value, low, high):
    """Classify a result against the range shown in the report."""

    if value < low:
        return "Below Range"

    if value > high:
        return "Above Range"

    return "Within Range"


# --------------------------------------------------
# MAIN REPORT ANALYZER
# --------------------------------------------------

def analyze_report(report_text):
    """
    Extract recognized laboratory tests from report text.

    Returns a Pandas DataFrame with:
    Test, Result, Unit, Reference Range, Status
    """

    columns = [
        "Test",
        "Result",
        "Unit",
        "Reference Range",
        "Status",
    ]

    if not report_text or not str(report_text).strip():
        return pd.DataFrame(columns=columns)

    lines = clean_lines(report_text)
    results = []
    seen_tests = set()

    for i, line in enumerate(lines):

        test_name = identify_test(line)

        if not test_name:
            continue

        # Avoid creating multiple rows for the same test.
        if test_name in seen_tests:
            continue

        # Search the test line and the next few lines for
        # a numeric result and its reference range.
        candidate_lines = lines[i:i + 5]

        result_info = None
        range_info = None

        for candidate in candidate_lines:

            candidate_text = remove_test_name(
                candidate,
                test_name,
            )

            # Try parsing a result from this line.
            if result_info is None:
                result_info = parse_result_line(candidate_text)

            # Try parsing a reference range from this line.
            if range_info is None:
                range_info = parse_range_line(candidate_text)

            if result_info and range_info:
                break

        # A result and reference range are both required
        # for automatic status classification.
        if not result_info or not range_info:
            continue

        value = result_info["value"]
        low = range_info["low"]
        high = range_info["high"]

        status = classify_result(value, low, high)

        unit = result_info["unit"]

        # Convert common OCR-normalized units back to display form.
        unit = re.sub(
            r"(?i)/ul\b",
            "/µL",
            unit,
        )

        results.append({
            "Test": test_name,
            "Result": result_info["result_text"],
            "Unit": unit,
            "Reference Range": range_info["range_text"],
            "Status": status,
        })

        seen_tests.add(test_name)

    return pd.DataFrame(results, columns=columns)
