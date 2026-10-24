
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


TEST_ALIASES = {
    "Hemoglobin": ["hemoglobin", "haemoglobin", "hb", "hgb"],
    "WBC": [
        "wbc", "white blood cell count", "white blood cells",
        "total leukocyte count", "total leucocyte count", "tlc"
    ],
    "RBC": [
        "rbc", "red blood cell count", "red blood cells",
        "erythrocyte count"
    ],
    "Platelets": ["platelet count", "platelets", "plt"],
    "Hematocrit": [
        "hematocrit", "haematocrit", "hct", "pcv",
        "packed cell volume"
    ],
    "MCV": ["mcv", "mean corpuscular volume"],
    "MCH": [
        "mch", "mean corpuscular hemoglobin",
        "mean corpuscular haemoglobin"
    ],
    "MCHC": [
        "mchc", "mean corpuscular hemoglobin concentration",
        "mean corpuscular haemoglobin concentration"
    ],
    "RDW": ["rdw", "red cell distribution width"],
    "Neutrophils": ["neutrophils", "neutrophil"],
    "Lymphocytes": ["lymphocytes", "lymphocyte"],
    "Eosinophils": ["eosinophils", "eosinophil"],
    "Monocytes": ["monocytes", "monocyte"],
    "Basophils": ["basophils", "basophil"],
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
    "Creatinine": ["creatinine", "serum creatinine"],
    "Urea": ["blood urea", "serum urea", "urea"],
    "BUN": ["bun", "blood urea nitrogen"],
    "Uric Acid": ["uric acid", "serum uric acid"],
    "Total Cholesterol": ["total cholesterol", "cholesterol total"],
    "HDL Cholesterol": ["hdl cholesterol", "hdl-c", "hdl"],
    "LDL Cholesterol": ["ldl cholesterol", "ldl-c", "ldl"],
    "Triglycerides": ["triglycerides", "triglyceride", "tg"],
    "Total Bilirubin": ["total bilirubin", "bilirubin total"],
    "Direct Bilirubin": ["direct bilirubin", "bilirubin direct"],
    "AST": ["aspartate aminotransferase", "sgot", "ast"],
    "ALT": ["alanine aminotransferase", "sgpt", "alt"],
    "ALP": ["alkaline phosphatase", "alp"],
    "Total Protein": ["total protein", "serum total protein"],
    "Albumin": ["albumin", "serum albumin"],
    "Globulin": ["globulin", "serum globulin"],
    "Calcium": ["calcium", "serum calcium"],
    "Sodium": ["sodium", "serum sodium"],
    "Potassium": ["potassium", "serum potassium"],
    "Chloride": ["chloride", "serum chloride"],
    "TSH": [
        "thyroid stimulating hormone",
        "thyroid-stimulating hormone", "tsh"
    ],
    "T3": ["total t3", "free t3", "triiodothyronine"],
    "T4": ["total t4", "free t4", "thyroxine"],
    "Vitamin D": [
        "25-oh vitamin d", "25 oh vitamin d",
        "25-hydroxy vitamin d", "vitamin d"
    ],
    "Vitamin B12": ["vitamin b12", "vit b12", "cobalamin"],
    "Ferritin": ["ferritin", "serum ferritin"],
    "CRP": ["c-reactive protein", "c reactive protein", "crp"],
    "ESR": ["erythrocyte sedimentation rate", "esr"],
    "Iron": ["serum iron", "iron"],
}


NUMBER = r"[<>≤≥]?\s*-?\d[\d,]*(?:\.\d+)?"

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
    r"(?<!\w)("
    r"mg/dl|mg/l|g/dl|g/l|mmol/l|umol/l|µmol/l|"
    r"iu/l|u/l|miu/l|uiu/ml|ng/ml|ng/dl|pg/ml|pg/dl|"
    r"pmol/l|nmol/l|mmol/mol|%"
    r"|fl|pg|cells/cumm|cells/mm3|cells/µl|cells/ul|"
    r"million/cumm|million/µl|million/ul|"
    r"lakh/cumm|lakhs/cumm|"
    r"10\^?\s*\d+\s*/\s*[a-zµ0-9]+"
    r")(?!\w)",
    re.IGNORECASE,
)


def _clean_number(value: str) -> str:
    return value.strip().replace(" ", "").replace(",", "")


def _to_float(value: str):
    cleaned = _clean_number(value)
    if cleaned.startswith(("<", ">", "≤", "≥")):
        return None

    try:
        return float(cleaned)
    except (TypeError, ValueError):
        return None


def _normalize_text(text: str) -> str:
    text = str(text or "")
    text = text.replace("\x00", " ")
    text = text.replace("\u00a0", " ")
    text = text.replace("−", "-")
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = re.sub(r"[ \t]+", " ", text)
    return text


def _find_test(line: str):
    """Return the longest matching test alias."""
    matches = []
    lowered = line.lower()

    for canonical, aliases in TEST_ALIASES.items():
        for alias in aliases:
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
            match = re.search(pattern, lowered, re.IGNORECASE)

            if match:
                matches.append(
                    (len(alias), match.start(), canonical, alias, match)
                )

    if not matches:
        return None

    matches.sort(key=lambda item: (-item[0], item[1]))
    _, _, canonical, alias, match = matches[0]

    return canonical, alias, match


def _extract_range(line: str, test_match):
    candidates = list(RANGE_RE.finditer(line))

    after = [
        match for match in candidates
        if match.start() >= test_match.end()
    ]

    if after:
        return after[0].group(0).strip()

    return None


def _extract_value(line: str, test_match, reference_range):
    """Extract a value after the test label, excluding range numbers."""
    excluded_spans = [
        match.span() for match in RANGE_RE.finditer(line)
    ]

    candidates = []

    for match in VALUE_RE.finditer(line):
        start, end = match.span()

        if start < test_match.end():
            continue

        if any(
            start < range_end and end > range_start
            for range_start, range_end in excluded_spans
        ):
            continue

        candidates.append((start, end, match.group(1).strip()))

    if not candidates:
        return None, "Result not confidently detected"

    start, _, raw = candidates[0]

    between = line[test_match.end():start].strip(" :|=\t")
    if len(between) > 35:
        return None, "Result position is ambiguous"

    return raw, None


def _status(value_text, reference_range):
    if not value_text:
        return "Needs review"

    value = _to_float(value_text)
    if value is None:
        return "Needs review"

    if not reference_range:
        return "Reference range unavailable"

    match = re.fullmatch(
        rf"\s*({NUMBER})\s*(?:-|to)\s*({NUMBER})\s*",
        reference_range,
        re.IGNORECASE,
    )

    if not match:
        return "Needs review"

    low = _to_float(match.group(1))
    high = _to_float(match.group(2))

    if low is None or high is None or low > high:
        return "Needs review"

    if value < low:
        return "Below range"
    if value > high:
        return "Above range"

    return "Within range"


def _unit_for_line(line: str, value_text: str):
    if not value_text:
        return ""

    match = UNIT_RE.search(line)
    return match.group(1).strip() if match else ""


def analyze_report(extracted_text: str) -> list[dict[str, Any]]:
    """
    Analyze report text conservatively.

    Supports a test name, result and range on the same line, and
    attempts a limited multi-line fallback when a label is isolated.
    """
    if not extracted_text or not str(extracted_text).strip():
        return []

    text = _normalize_text(extracted_text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    results = []
    seen = set()

    for index, line in enumerate(lines):
        found = _find_test(line)
        source_line = line

        # Limited fallback for PDFs where a test name is on one line
        # and its numeric result/range appears on the next line.
        if found and not VALUE_RE.search(line):
            next_line = lines[index + 1] if index + 1 < len(lines) else ""
            if next_line and len(next_line) < 200:
                combined = f"{line} {next_line}"
                combined_found = _find_test(combined)

                if combined_found:
                    line = combined
                    source_line = combined
                    found = combined_found

        if not found or len(line) > 300:
            continue

        canonical, alias, test_match = found
        reference_range = _extract_range(line, test_match)
        value_text, _ = _extract_value(
            line, test_match, reference_range
        )

        if value_text is None:
            continue

        unit = _unit_for_line(line, value_text)
        status = _status(value_text, reference_range)

        key = (
            canonical.lower(),
            value_text,
            reference_range or "",
            unit.lower(),
        )
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
                "Compared with the reference range detected in the extracted text. "
                "This is not a diagnosis."
                if status in ("Below range", "Above range", "Within range")
                else
                "The result or reference range could not be safely classified. "
                "Check the original report."
            ),
            "source_line": source_line,
            "needs_review": status in (
                "Needs review",
                "Reference range unavailable",
            ),
        })

    return results


def extract_patient_fields(extracted_text: str) -> dict[str, str]:
    """
    Extract common patient fields from labels and simple report layouts.
    Returns only fields found in the extracted text.
    """
    text = _normalize_text(extracted_text)
    fields = {}

    def first_match(patterns):
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = re.sub(r"\s+", " ", match.group(1)).strip(" :-|")
                if value:
                    return value
        return ""

    # Handles labels such as:
    # Patient Name: Sangavi
    # Name: Sangavi
    # Patient: Sangavi
    name = first_match([
        r"^\s*(?:patient\s*name|name\s*of\s*patient|patient)\s*[:\-]\s*([^\n|]+)",
        r"^\s*name\s*[:\-]\s*([^\n|]+)",
    ])

    # Handles Age: 22, Age: 22 years, Patient Age: 22
    age = first_match([
        r"^\s*(?:patient\s*)?age\s*[:\-]\s*(\d{1,3})(?:\s*(?:years?|yrs?))?\b",
        r"\bAge\s*[:\-]\s*(\d{1,3})\s*(?:years?|yrs?)\b",
    ])

    gender = first_match([
        r"^\s*(?:gender|sex)\s*[:\-]\s*(male|female|other)\b",
    ])

    report_date = first_match([
        r"^\s*report\s*date\s*[:\-]\s*([^\n|]+)",
        r"^\s*date\s*of\s*(?:visit|collection|report)\s*[:\-]\s*([^\n|]+)",
        r"^\s*collection\s*date\s*[:\-]\s*([^\n|]+)",
        r"^\s*date\s*[:\-]\s*([^\n|]+)",
    ])

    if name:
        fields["patient_name"] = name
    if age:
        fields["age"] = age
    if gender:
        fields["gender"] = gender.capitalize()
    if report_date:
        fields["report_date"] = report_date

    return fields
