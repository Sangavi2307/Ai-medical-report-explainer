
import re
import pandas as pd


TEST_ALIASES = {
    "Hemoglobin": [
        r"\bhemoglobin\b", r"\bhaemoglobin\b", r"\bhb\b"
    ],
    "WBC": [
        r"\bwhite blood cells?\b", r"\bwhite blood cell count\b",
        r"\bwbc\b", r"\btotal leukocyte count\b", r"\btlc\b"
    ],
    "Platelets": [
        r"\bplatelet count\b", r"\bplatelets\b", r"\bplt\b"
    ],
    "RBC": [
        r"\bred blood cells?\b", r"\brbc\b",
        r"\bred blood cell count\b"
    ],
    "Fasting Glucose": [
        r"\bfasting blood sugar\b", r"\bfasting glucose\b",
        r"\bfbs\b", r"\bfbg\b"
    ],
    "Random Glucose": [
        r"\brandom blood sugar\b", r"\brandom glucose\b",
        r"\brbs\b"
    ],
    "HbA1c": [
        r"\bhba1c\b", r"\bglycated hemoglobin\b",
        r"\bglycosylated hemoglobin\b"
    ],
    "Total Cholesterol": [
        r"\btotal cholesterol\b", r"\bcholesterol\b"
    ],
    "Creatinine": [
        r"\bserum creatinine\b", r"\bcreatinine\b"
    ],
    "Urea": [
        r"\bblood urea\b", r"\bserum urea\b", r"\burea\b"
    ],
    "TSH": [
        r"\bthyroid stimulating hormone\b", r"\btsh\b"
    ],
    "Vitamin D": [
        r"\b25[- ]?oh vitamin d\b", r"\bvitamin d\b"
    ],
    "Vitamin B12": [
        r"\bvitamin b12\b", r"\bcobalamin\b"
    ],
}


def _to_number(value):
    """Convert a recognized numeric string into a number."""
    try:
        return float(value.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def _find_test(line):
    """Return the recognized test name, if any."""
    for test_name, patterns in TEST_ALIASES.items():
        for pattern in patterns:
            if re.search(pattern, line, flags=re.IGNORECASE):
                return test_name
    return None


def _find_range(line):
    """Find ranges such as 12-16, 12.0 - 16.0 or 70 to 100."""
    match = re.search(
        r"(?<!\d)(\d[\d,]*(?:\.\d+)?)\s*"
        r"(?:-|–|—|\bto\b)\s*"
        r"(\d[\d,]*(?:\.\d+)?)(?!\d)",
        line,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    low = _to_number(match.group(1))
    high = _to_number(match.group(2))

    if low is None or high is None or low > high:
        return None

    return low, high


def _find_result(line, test_name):
    """
    Find a plausible numeric result after a test name.
    Does not interpret dates or reference-range numbers as results
    when a clearer value is available.
    """
    patterns = TEST_ALIASES[test_name]
    name_match = None

    for pattern in patterns:
        name_match = re.search(pattern, line, flags=re.IGNORECASE)
        if name_match:
            break

    if not name_match:
        return None

    remainder = line[name_match.end():]

    # Remove reference range before searching for the result.
    range_match = re.search(
        r"(?<!\d)\d[\d,]*(?:\.\d+)?\s*"
        r"(?:-|–|—|\bto\b)\s*"
        r"\d[\d,]*(?:\.\d+)?",
        remainder,
        flags=re.IGNORECASE,
    )
    if range_match:
        remainder = remainder[:range_match.start()] + " " + remainder[range_match.end():]

    # Skip separators and common unit labels where possible.
    remainder = re.sub(r"^\s*[:=|]\s*", " ", remainder)
    remainder = re.sub(
        r"^\s*(?:mg/dl|g/dl|g/l|mmol/l|u/l|iu/l|"
        r"cells?/ul|cells?/µl|million/µl|%|fl|pg)\b",
        " ",
        remainder,
        flags=re.IGNORECASE,
    )

    number = re.search(r"(?<![\w/])[-+]?\d[\d,]*(?:\.\d+)?", remainder)
    if number:
        return number.group(0).replace(",", "")

    # Fallback for formats such as "Hemoglobin 13.2 g/dL".
    number = re.search(
        r"[:=|]\s*([-+]?\d[\d,]*(?:\.\d+)?)",
        line[name_match.end():],
    )
    return number.group(1).replace(",", "") if number else None


def analyze_report(report_text):
    """
    Analyze extracted report text.
    Returns a DataFrame with consistent columns for app.py.
    """
    columns = ["Test", "Result", "Unit", "Reference Range", "Status"]

    if not isinstance(report_text, str) or not report_text.strip():
        return pd.DataFrame(columns=columns)

    results = []
    seen = set()

    for original_line in report_text.splitlines():
        line = re.sub(r"\s+", " ", original_line).strip()
        if not line:
            continue

        test_name = _find_test(line)
        if not test_name:
            continue

        result_text = _find_result(line, test_name)
        if result_text is None:
            continue

        value = _to_number(result_text)
        if value is None:
            continue

        # Get the reference range only from the same line.
        reference_range = _find_range(line)

        # Attempt to capture a common unit from the line.
        unit_match = re.search(
            r"\b(mg/dL|g/dL|g/L|mmol/L|IU/L|U/L|"
            r"cells?/µL|cells?/uL|million/µL|mIU/L|ng/mL|pg/mL|%)\b",
            line,
            flags=re.IGNORECASE,
        )
        unit = unit_match.group(1) if unit_match else ""

        if reference_range:
            low, high = reference_range
            range_text = f"{low:g} - {high:g}"
            if value < low:
                status = "Below range"
            elif value > high:
                status = "Above range"
            else:
                status = "Within range"
        else:
            range_text = "Not found in extracted line"
            status = "Needs reference range"

        key = (test_name, value)
        if key in seen:
            continue
        seen.add(key)

        results.append({
            "Test": test_name,
            "Result": value,
            "Unit": unit,
            "Reference Range": range_text,
            "Status": status,
        })

    return pd.DataFrame(results, columns=columns)
    
