
import re
import pandas as pd


TEST_ALIASES = {
    "hemoglobin": ["hemoglobin", "haemoglobin", "hb"],
    "wbc": [
        "white blood cell count", "white blood cells",
        "total leukocyte count", "total leucocyte count",
        "tlc", "wbc"
    ],
    "rbc": ["red blood cell count", "red blood cells", "rbc"],
    "platelets": ["platelet count", "platelets", "thrombocyte count"],
    "glucose": [
        "fasting blood sugar", "fasting glucose",
        "random blood sugar", "blood glucose", "glucose",
        "fbs", "rbs"
    ],
    "hba1c": ["hba1c", "glycated hemoglobin", "glycosylated hemoglobin"],
    "creatinine": ["serum creatinine", "creatinine"],
    "urea": ["blood urea nitrogen", "serum urea", "urea", "bun"],
    "total cholesterol": ["total cholesterol", "cholesterol"],
    "ldl": ["ldl cholesterol", "ldl"],
    "hdl": ["hdl cholesterol", "hdl"],
    "triglycerides": ["triglycerides", "triglyceride"],
    "sodium": ["serum sodium", "sodium"],
    "potassium": ["serum potassium", "potassium"],
    "calcium": ["serum calcium", "calcium"],
    "bilirubin": ["total bilirubin", "bilirubin"],
    "alt": ["sgpt", "alanine aminotransferase", "alt"],
    "ast": ["sgot", "aspartate aminotransferase", "ast"],
    "alp": ["alkaline phosphatase", "alp"],
    "tsh": ["thyroid stimulating hormone", "tsh"],
    "vitamin d": ["25-oh vitamin d", "vitamin d"],
    "vitamin b12": ["vitamin b12", "b12"],
    "esr": ["erythrocyte sedimentation rate", "esr"],
    "crp": ["c-reactive protein", "crp"],
    "uric acid": ["serum uric acid", "uric acid"],
    "albumin": ["serum albumin", "albumin"],
    "total protein": ["total protein"],
    "mcv": ["mean corpuscular volume", "mcv"],
    "mch": ["mean corpuscular hemoglobin", "mch"],
    "mchc": ["mean corpuscular hemoglobin concentration", "mchc"],
    "hematocrit": ["hematocrit", "packed cell volume", "pcv"],
    "neutrophils": ["neutrophils", "neutrophil"],
    "lymphocytes": ["lymphocytes", "lymphocyte"],
    "monocytes": ["monocytes", "monocyte"],
    "eosinophils": ["eosinophils", "eosinophil"],
    "basophils": ["basophils", "basophil"],
}


COLUMNS = [
    "Test", "Result", "Unit", "Reference Range", "Status"
]


def normalize_number(value):
    """Convert OCR-friendly numeric text to a float."""
    value = value.strip().replace(",", "")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def find_test_name(line):
    lower_line = line.lower()

    # Longer names first to avoid matching a short alias too early.
    all_aliases = []
    for canonical, aliases in TEST_ALIASES.items():
        for alias in aliases:
            all_aliases.append((alias, canonical))

    all_aliases.sort(key=lambda item: len(item[0]), reverse=True)

    for alias, canonical in all_aliases:
        pattern = r"(?<![a-z])" + re.escape(alias) + r"(?![a-z])"
        match = re.search(pattern, lower_line)

        if match:
            return canonical, match.start(), match.end()

    return None, -1, -1


def parse_line(line):
    """
    Parses a common lab line, for example:
    Hemoglobin 12.5 g/dL 12.0 - 15.0

    This is a heuristic parser; unusual report layouts may need adjustments.
    """
    original = re.sub(r"\s+", " ", line).strip()

    if not original or len(original) > 300:
        return None

    # Ignore lines that look like headings or patient details.
    if not re.search(r"\d", original):
        return None

    canonical, start, end = find_test_name(original)

    if canonical is None:
        return None

    # Extract numbers after the matched test name.
    remainder = original[end:].strip(" :\t-")
    numbers = list(
        re.finditer(r"(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?", remainder)
    )

    if not numbers:
        return None

    # The first numeric token is treated as the result.
    # Verify it against the original report before relying on it.
    result_match = numbers[0]
    result_text = result_match.group(0)
    result_value = normalize_number(result_text)

    if result_value is None:
        return None

    tail = remainder[result_match.end():].strip()

    # Capture a possible unit before the reference range.
    range_match = re.search(
        r"(-?\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(-?\d+(?:\.\d+)?)",
        tail,
        flags=re.IGNORECASE
    )

    if range_match:
        reference_range = (
            f"{range_match.group(1)} - {range_match.group(2)}"
        )
        unit = tail[:range_match.start()].strip(" ,;:")
    else:
        reference_range = ""
        unit = tail.split()[0].strip(" ,;:") if tail.split() else ""

    # Remove obvious reference-range units mistakenly captured as unit.
    if unit.lower() in {"-", "to", "–"}:
        unit = ""

    status = "Needs review"

    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))

        if result_value < low:
            status = "Below range"
        elif result_value > high:
            status = "Above range"
        else:
            status = "Within range"

    return {
        "Test": canonical.title(),
        "Result": result_value,
        "Unit": unit,
        "Reference Range": reference_range,
        "Status": status
    }


def analyze_report(report_text):
    if not report_text or not report_text.strip():
        return pd.DataFrame(columns=COLUMNS)

    results = []
    seen = set()

    for line in report_text.splitlines():
        row = parse_line(line)

        if row is None:
            continue

        key = (row["Test"], row["Result"], row["Unit"])

        if key not in seen:
            results.append(row)
            seen.add(key)

    return pd.DataFrame(results, columns=COLUMNS)


def extract_patient_fields(report_text):
    """Extract simple patient fields without inventing missing information."""
    text = report_text or ""

    fields = {}

    patterns = {
        "Patient Name": r"(?:patient\s*name|name)\s*[:\-]\s*([^\n]+)",
        "Age": r"\bage\s*[:\-]\s*(\d{1,3}\s*(?:years?|yrs?|months?)?)",
        "Sex": r"\b(?:sex|gender)\s*[:\-]\s*(male|female|other)",
        "Report Date": r"(?:report\s*date|collection\s*date|date)\s*[:\-]\s*([^\n]+)"
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            fields[field] = match.group(1).strip()

    return fields
