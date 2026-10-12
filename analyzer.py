
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
# SUPPORTED LABORATORY TESTS
# ==================================================

TEST_ALIASES = {
    "Hemoglobin": ["hemoglobin", "haemoglobin", "hb"],
    "WBC Count": [
        "white blood cell count",
        "total leukocyte count",
        "total leucocyte count",
        "wbc count",
        "tlc",
        "wbc",
    ],
    "Platelets": ["platelet count", "platelets", "platelet", "plt"],
    "Fasting Blood Sugar": [
        "fasting blood sugar",
        "fasting blood glucose",
        "fasting glucose",
        "fbs",
    ],
    "Random Blood Sugar": ["random blood sugar", "random glucose", "rbs"],
    "Postprandial Blood Sugar": [
        "postprandial blood sugar",
        "pp blood sugar",
        "ppbs",
    ],
    "Total Cholesterol": ["total cholesterol", "cholesterol"],
    "Triglycerides": ["triglycerides", "triglyceride"],
    "HDL Cholesterol": ["hdl cholesterol", "hdl"],
    "LDL Cholesterol": ["ldl cholesterol", "ldl"],
    "Creatinine": ["serum creatinine", "creatinine"],
    "Urea": ["blood urea", "serum urea", "urea"],
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
        "μ": "u",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

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
# IDENTIFY TEST NAME
# ==================================================

def identify_test(line):
    """Identify a supported test at the start of a line."""
    normalized = normalize_text(line).lower().strip()
    normalized = re.sub(r"^[\W_]+", "", normalized)

    aliases = sorted(
        [
            (alias.lower(), standard_name)
            for standard_name, names in TEST_ALIASES.items()
            for alias in names
        ],
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for alias, standard_name in aliases:
        pattern = rf"^{re.escape(alias)}(?![a-z])"

        if re.search(pattern, normalized):
            return standard_name

    return None


def remove_test_name(line, test_name):
    """Remove the recognized test name from a line."""
    normalized = normalize_text(line).strip()

    aliases = sorted(
        TEST_ALIASES.get(test_name, []),
        key=len,
        reverse=True,
    )

    for alias in aliases:
        pattern = (
            rf"^\s*{re.escape(alias)}"
            rf"(?![a-z])\s*[:=]?\s*"
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
# PARSE NUMERIC RESULT
# ==================================================

def parse_result_line(line):
    """
    Extract the first number from a result-only text segment.

    Reference ranges are removed first to avoid confusing their
    limits with the actual result.
    """
    line = normalize_text(line).strip()

    if not line:
        return None

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

    # Text after the value may contain a unit or other columns.
    trailing = cleaned[match.end():].strip(" :;()|")

    unit_match = re.match(
        r"^([a-zA-Zµμ/%]+(?:\s*/\s*[a-zA-Zµμ]+)?)",
        trailing,
    )

    unit = unit_match.group(1).strip() if unit_match else ""

    return {
        "value": value,
        "result_text": number_text,
        "unit": unit,
    }


# ==================================================
# PARSE REFERENCE RANGE
# ==================================================

def parse_range_line(line):
    """Extract a possible lower and upper reference limit."""
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
    """Compare a result with a detected reference range."""
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

    Output columns:
        Test, Result, Unit, Reference Range, Status

    Results without a detected reference range are retained as
    Not Classified. This function does not diagnose conditions.
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

        if not test_name or test_name in seen_tests:
            continue

        result_info = None
        range_info = None

        # Inspect this line and nearby lines. Stop at another
        # recognized test so values are not assigned to the wrong test.
        for j in range(i, min(i + 5, len(lines))):
            candidate = lines[j]

            if j > i and identify_test(candidate):
                break

            if j == i:
                candidate = remove_test_name(candidate, test_name)

            if result_info is None:
                result_info = parse_result_line(candidate)

            if range_info is None:
                range_info = parse_range_line(lines[j])

            if result_info and range_info:
                break

        if result_info is None:
            continue

        if range_info:
            status = classify_result(
                result_info["value"],
                range_info["low"],
                range_info["high"],
            )
            reference_range = range_info["range_text"]
        else:
            status = "Not Classified"
            reference_range = "Not detected"

        results.append({
            "Test": test_name,
            "Result": result_info["result_text"],
            "Unit": result_info["unit"],
            "Reference Range": reference_range,
            "Status": status,
        })

        seen_tests.add(test_name)

    return pd.DataFrame(results, columns=columns)
