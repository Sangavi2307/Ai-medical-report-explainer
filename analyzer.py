
"""
analyzer.py
Conservative laboratory report analyzer for the
AI Medical Report Explainer application.

Important:
- Does not diagnose diseases.
- Does not invent missing values or reference ranges.
- Does not automatically correct decimal/OCR errors.
- Marks ambiguous results for manual review.
"""

import re
from typing import Any


# Common names and abbreviations found in laboratory reports.
TEST_ALIASES = {
    "Hemoglobin": [
        "hemoglobin", "haemoglobin", "hb", "hgb"
    ],
    "WBC": [
        "wbc", "white blood cell count", "white blood cells",
        "total leukocyte count", "total leucocyte count", "tlc"
    ],
    "RBC": [
        "rbc", "red blood cell count", "red blood cells",
        "erythrocyte count"
    ],
    "Platelets": [
        "platelet count", "platelets", "plt"
    ],
    "Hematocrit": [
        "hematocrit", "haematocrit", "hct", "pcv",
        "packed cell volume"
    ],
    "MCV": [
        "mcv", "mean corpuscular volume"
    ],
    "MCH": [
        "mch", "mean corpuscular hemoglobin",
        "mean corpuscular haemoglobin"
    ],
    "MCHC": [
        "mchc", "mean corpuscular hemoglobin concentration",
        "mean corpuscular haemoglobin concentration"
    ],
    "RDW": [
        "rdw", "red cell distribution width"
    ],
    "Neutrophils": [
        "neutrophils", "neutrophil"
    ],
    "Lymphocytes": [
        "lymphocytes", "lymphocyte"
    ],
    "Eosinophils": [
        "eosinophils", "eosinophil"
    ],
    "Monocytes": [
        "monocytes", "monocyte"
    ],
    "Basophils": [
        "basophils", "basophil"
    ],
    "Fasting Glucose": [
        "fasting blood glucose", "fasting glucose",
        "fasting blood sugar", "fbs"
    ],
    "Random Glucose": [
        "random blood glucose", "random glucose",
        "random blood sugar", "rbs"
    ],
    "HbA1c": [
        "hba1c", "glycated hemoglobin",
        "glycosylated hemoglobin"
    ],
    "Creatinine": [
        "creatinine", "serum creatinine"
    ],
    "Urea": [
        "blood urea", "serum urea", "urea"
    ],
    "BUN": [
        "bun", "blood urea nitrogen"
    ],
    "Uric Acid": [
        "uric acid", "serum uric acid"
    ],
    "Total Cholesterol": [
        "total cholesterol", "cholesterol total"
    ],
    "HDL Cholesterol": [
        "hdl cholesterol", "hdl-c", "hdl"
    ],
    "LDL Cholesterol": [
        "ldl cholesterol", "ldl-c", "ldl"
    ],
    "Triglycerides": [
        "triglycerides", "triglyceride", "tg"
    ],
    "Total Bilirubin": [
        "total bilirubin", "bilirubin total"
    ],
    "Direct Bilirubin": [
        "direct bilirubin", "bilirubin direct"
    ],
    "AST": [
        "ast", "sgot", "aspartate aminotransferase"
    ],
    "ALT": [
        "alt", "sgpt", "alanine aminotransferase"
    ],
    "ALP": [
        "alp", "alkaline phosphatase"
    ],
    "Total Protein": [
        "total protein", "serum total protein"
    ],
    "Albumin": [
        "albumin", "serum albumin"
    ],
    "Globulin": [
        "globulin", "serum globulin"
    ],
    "Calcium": [
        "calcium", "serum calcium"
    ],
    "Sodium": [
        "sodium", "serum sodium", "na"
    ],
    "Potassium": [
        "potassium", "serum potassium", "k"
    ],
    "Chloride": [
        "chloride", "serum chloride"
    ],
    "TSH": [
        "tsh", "thyroid stimulating hormone",
        "thyroid-stimulating hormone"
    ],
    "T3": [
        "total t3", "free t3", "triiodothyronine"
    ],
    "T4": [
        "total t4", "free t4", "thyroxine"
    ],
    "Vitamin D": [
        "25-oh vitamin d", "25 oh vitamin d",
        "vitamin d", "25-hydroxy vitamin d"
    ],
    "Vitamin B12": [
        "vitamin b12", "vit b12", "cobalamin"
    ],
    "Ferritin": [
        "ferritin", "serum ferritin"
    ],
    "CRP": [
        "crp", "c-reactive protein", "c reactive protein"
    ],
    "ESR": [
        "esr", "erythrocyte sedimentation rate"
    ],
    "Iron": [
        "serum iron", "iron"
    ],
}


# A conservative numeric pattern. Commas are allowed in numbers.
NUMBER = r"[<>≤≥]?\s*-?\d[\d,]*(?:\.\d+)?"

# Examples: 12-16, 12.0 - 15.5, < 200, >= 40
RANGE_RE = re.compile(
    rf"(?<!\w)(?:"
    rf"{NUMBER}\s*(?:-|–|—|to)\s*{NUMBER}"
    rf"|[<>≤≥]\s*\d[\d,]*(?:\.\d+)?"
    rf"|(?:less than|greater than|up to|at least)\s*"
    rf"\d[\d,]*(?:\.\d+)?"
    rf")",
    re.IGNORECASE,
)

VALUE_RE = re.compile(
    rf"(?<![\w/])({NUMBER})(?![\w/])",
    re.IGNORECASE,
)

UNIT_RE = re.compile(
    r"\b("
    r"mg/dl|mg/l|g/dl|g/l|mmol/l|umol/l|µmol/l|"
    r"iu/l|u/l|miu/l|uiu/ml|ng/ml|ng/dl|pg/ml|pg/dl|"
    r"pmol/l|nmol/l|mmol/mol|%"
    r"|fl|pg|cells/cumm|cells/mm3|cells/µl|cells/ul|"
    r"million/cumm|million/µl|million/ul|"
    r"lakh/cumm|lakhs/cumm|"
    r"10\^?\s*\d+\s*/\s*[a-zµ0-9]+"
    r")\b",
    re.IGNORECASE,
)


def _clean_number(value: str) -> str:
    """Normalize only digit-grouping commas, never decimal points."""
    value = value.strip().replace(" ", "")
    value = value.replace(",", "")
    return value


def _to_float(value: str):
    """Convert an ordinary numeric result to float; limits stay as text."""
    cleaned = _clean_number(value)
    if cleaned.startswith(("<", ">", "≤", "≥")):
        return None
    try:
        return float(cleaned)
    except (TypeError, ValueError):
        return None


def _normalize_text(text: str) -> str:
    """Normalize common OCR spacing while preserving decimal points."""
    text = str(text or "")
    text = text.replace("\x00", " ")
    text = text.replace("\u00a0", " ")
    text = text.replace("≤", "<=")
    text = text.replace("≥", ">=")
    text = text.replace("−", "-")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = re.sub(r"[ \t]+", " ", text)
    return text


def _find_test(line: str):
    """Return the best matching test name and matched alias."""
    lowered = line.lower()

    matches = []

    for canonical, aliases in TEST_ALIASES.items():
        for alias in aliases:
            # Require word boundaries so, for example, "na" does not
            # match arbitrary letters inside another word.
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
            match = re.search(pattern, lowered, re.IGNORECASE)
            if match:
                matches.append(
                    (len(alias), match.start(), canonical, alias, match)
                )

    if not matches:
        return None

    # Prefer the longest alias, avoiding short aliases taking precedence.
    matches.sort(key=lambda item: (-item[0], item[1]))
    _, _, canonical, alias, match = matches[0]
    return canonical, alias, match


def _extract_range(line: str, test_match):
    """Extract a reference range only from the current row."""
    candidates = []

    for match in RANGE_RE.finditer(line):
        # Do not treat the result value itself as a reference range.
        candidates.append((match.start(), match.end(), match.group(0).strip()))

    if not candidates:
        return None

    # Prefer a range appearing after the test name.
    after = [item for item in candidates if item[0] >= test_match.end()]
    if after:
        return after[0][2]

    # A range before the test name can be a table-layout artifact.
    # Do not guess which test it belongs to.
    return None


def _extract_value(line: str, test_match, reference_range):
    """
    Extract a result from the same line as the test.

    A value that is indistinguishable from the reference range is not
    guessed. Range numbers are excluded from candidate result numbers.
    """
    ranges = list(RANGE_RE.finditer(line))
    excluded_spans = [(m.start(), m.end()) for m in ranges]

    candidates = []

    for match in VALUE_RE.finditer(line):
        start, end = match.span()

        # Skip numbers inside a detected reference range.
        if any(start < r_end and end > r_start
               for r_start, r_end in excluded_spans):
            continue

        # Skip numbers that occur before the test label.
        if start < test_match.end():
            continue

        raw = match.group(1).strip()
        candidates.append((start, end, raw))

    if not candidates:
        return None, "Result not confidently detected"

    # The first numeric item after the test label is often the result,
    # but dates/IDs can also occur. Require a reasonable position.
    start, end, raw = candidates[0]

    between = line[test_match.end():start].strip(" :|=\t")
    if len(between) > 35:
        return None, "Result position is ambiguous"

    # If the result is followed by a recognized unit, keep the raw value.
    # Do not scale or "repair" it.
    return raw, None


def _status(value_text, reference_range):
    """Compare a numeric result with a clearly numeric two-sided range."""
    if not value_text:
        return "Needs review"

    value = _to_float(value_text)
    if value is None:
        # Results such as <5 or >100 are preserved, not guessed.
        return "Needs review"

    if not reference_range:
        return "Reference range unavailable"

    range_match = re.fullmatch(
        rf"\s*({NUMBER})\s*(?:-|to)\s*({NUMBER})\s*",
        reference_range,
        re.IGNORECASE,
    )

    if not range_match:
        return "Needs review"

    low = _to_float(range_match.group(1))
    high = _to_float(range_match.group(2))

    if low is None or high is None or low > high:
        return "Needs review"

    if value < low:
        return "Below range"
    if value > high:
        return "Above range"
    return "Within range"


def _unit_for_line(line: str, value_text: str):
    """Find a unit in the current test row only."""
    if not value_text:
        return ""

    match = UNIT_RE.search(line)
    return match.group(0) if match else ""


def analyze_report(extracted_text: str) -> list[dict[str, Any]]:
    """
    Analyze extracted PDF/OCR text.

    Returns a list of dictionaries for display in Streamlit.
    Unknown tests are not invented. Ambiguous rows are skipped rather
    than assigned incorrect values.
    """
    if not extracted_text or not str(extracted_text).strip():
        return []

    text = _normalize_text(extracted_text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    results = []
    seen = set()

    for line in lines:
        found = _find_test(line)
        if not found:
            continue

        canonical, alias, test_match = found

        # Do not parse a test when the label appears inside a long
        # paragraph. Lab rows are usually short and structured.
        if len(line) > 300:
            continue

        reference_range = _extract_range(line, test_match)
        value_text, value_error = _extract_value(
            line, test_match, reference_range
        )

        # Avoid creating false test results from a test name alone.
        if value_text is None:
            continue

        unit = _unit_for_line(line, value_text)
        status = _status(value_text, reference_range)

        key = (canonical.lower(), value_text, reference_range or "", unit.lower())
        if key in seen:
            continue
        seen.add(key)

        results.append({
            "test": canonical,
            "result": value_text,
            "unit": unit,
            "reference_range": reference_range or "Not provided",
            "status": status,
            "meaning": (
                f"{canonical} is a laboratory measurement. "
                "Its meaning depends on the laboratory method and clinical context."
            ),
            "interpretation": (
                "This result was compared only with the reference range "
                "detected on the same extracted line. It is not a diagnosis."
                if status in ("Below range", "Above range", "Within range")
                else
                "The value or reference range could not be safely interpreted "
                "from the extracted text. Check the original report."
            ),
            "source_line": line,
            "needs_review": status in (
                "Needs review",
                "Reference range unavailable",
            ),
        })

    return results


def extract_patient_fields(extracted_text: str) -> dict[str, str]:
    """Extract a few common patient fields without guessing."""
    text = _normalize_text(extracted_text)

    fields = {
        "patient_name": "",
        "age": "",
        "gender": "",
        "report_date": "",
    }

    name_match = re.search(
        r"(?im)^\s*(?:patient\s*name|name\s*of\s*patient|patient)\s*"
        r"[:\-]\s*([A-Za-z][A-Za-z .'-]{1,80})\s*$",
        text,
    )
    if name_match:
        fields["patient_name"] = name_match.group(1).strip()

    age_match = re.search(
        r"(?i)\b(?:age)\s*[:\-]?\s*(\d{1,3})\s*(?:years?|yrs?)?\b",
        text,
    )
    if age_match:
        fields["age"] = age_match.group(1)

    gender_match = re.search(
        r"(?i)\b(?:gender|sex)\s*[:\-]\s*(male|female|other)\b",
        text,
    )
    if gender_match:
        fields["gender"] = gender_match.group(1).capitalize()

    date_match = re.search(
        r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
        r"\d{4}-\d{2}-\d{2})\b",
        text,
    )
    if date_match:
        fields["report_date"] = date_match.group(1)

    return fields
