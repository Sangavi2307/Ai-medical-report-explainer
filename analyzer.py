
"""
analyzer.py
Conservative laboratory report analyzer for the
AI Medical Report Explainer application.

- Extracts patient information from common report layouts.
- Supports laboratory rows with numeric and text results.
- Preserves extracted reference ranges and reported statuses.
- Does not diagnose diseases or invent missing values.
- Marks ambiguous results for manual review.
"""

import re
from typing import Any


TEST_ALIASES = {
    "Hemoglobin": [
        "hemoglobin", "haemoglobin", "hemaglobin", "haemaglobin",
        "hemoglobin (hb)", "haemoglobin (hb)", "hb", "hgb"
    ],
    "WBC": [
        "total wbc count", "wbc count", "white blood cell count",
        "white blood cells", "total leukocyte count",
        "total leucocyte count", "tlc", "wbc"
    ],
    "RBC": [
        "red blood cell count", "red blood cells",
        "erythrocyte count", "rbc"
    ],
    "Platelets": ["platelet count", "platelets", "plt"],
    "Hematocrit": [
        "hematocrit", "haematocrit", "hct", "pcv",
        "packed cell volume"
    ],
    "MCV": ["mean corpuscular volume", "mcv"],
    "MCH": [
        "mean corpuscular hemoglobin", "mean corpuscular haemoglobin",
        "mch"
    ],
    "MCHC": [
        "mean corpuscular hemoglobin concentration",
        "mean corpuscular haemoglobin concentration", "mchc"
    ],
    "RDW": ["red cell distribution width", "rdw"],
    "Neutrophils": ["neutrophils", "neutrophil"],
    "Lymphocytes": ["lymphocytes", "lymphocyte"],
    "Eosinophils": ["eosinophils", "eosinophil"],
    "Monocytes": ["monocytes", "monocyte"],
    "Basophils": ["basophils", "basophil"],
    "Fasting Glucose": [
        "fasting plasma glucose", "fasting blood sugar",
        "fasting blood glucose", "fasting glucose", "fbs"
    ],
    "Random Glucose": [
        "random plasma glucose", "random blood glucose",
        "random blood sugar", "random glucose", "rbs"
    ],
    "HbA1c": [
        "hba1c", "hb a1c", "glycated hemoglobin",
        "glycosylated hemoglobin"
    ],
    "Creatinine": ["serum creatinine", "creatinine"],
    "Urea": ["blood urea", "serum urea", "urea"],
    "BUN": ["blood urea nitrogen", "bun"],
    "Uric Acid": ["serum uric acid", "uric acid"],
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
    "Albumin": ["serum albumin", "albumin"],
    "Globulin": ["serum globulin", "globulin"],
    "Calcium": ["serum calcium", "calcium"],
    "Sodium": ["serum sodium", "sodium"],
    "Potassium": ["serum potassium", "potassium"],
    "Chloride": ["serum chloride", "chloride"],
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
    "Ferritin": ["serum ferritin", "ferritin"],
    "CRP": ["c-reactive protein", "c reactive protein", "crp"],
    "ESR": ["erythrocyte sedimentation rate", "esr"],
    "Iron": ["serum iron", "iron"],
    "Appearance": ["appearance"],
    "Pus Cells": ["pus cells", "pus cell"],
    "Urine Protein": ["urine protein", "protein"],
    "Bacteria": ["bacteria", "bacterial count"],
}


NUMBER = r"[<>≤≥]?\s*-?\d[\d,]*(?:\.\d+)?"

RANGE_RE = re.compile(
    rf"(?<![\w/])(?:"
    rf"{NUMBER}\s*(?:-|–|—|to)\s*{NUMBER}"
    rf"|[<>≤≥]\s*\d[\d,]*(?:\.\d+)?"
    rf"|(?:less than|greater than|up to|at least|below|above)"
    rf"\s*\d[\d,]*(?:\.\d+)?"
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
    r"iu/l|u/l|ul|miu/l|uiu/ml|ng/ml|ng/dl|pg/ml|pg/dl|"
    r"pmol/l|nmol/l|mmol/mol|%"
    r"|fl|pg|cells/cumm|cells/mm3|cells/µl|cells/ul|"
    r"million/cumm|million/µl|million/ul|"
    r"lakh/cumm|lakhs/cumm|"
    r"10\^?\s*\d+\s*/\s*[a-zµ0-9]+"
    r")(?!\w)",
    re.IGNORECASE,
)


def _normalize_text(text: str) -> str:
    text = str(text or "")
    text = text.replace("\x00", " ").replace("\u00a0", " ")
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")
    text = text.replace("µ", "µ")
    text = re.sub(r"[ \t]+", " ", text)
    return text


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


# ---------------------------------------------------------
# PATIENT INFORMATION
# ---------------------------------------------------------

def extract_patient_fields(extracted_text: str) -> dict[str, str]:
    fields = {
        "patient_name": "",
        "patient_id": "",
        "age": "",
        "gender": "",
        "report_date": "",
        "collection_date": "",
        "report_number": "",
    }

    text = _normalize_text(extracted_text)
    if not text.strip():
        return fields

    label = (
        r"Patient\s+Name|Name\s+of\s+Patient|"
        r"Patient\s+ID|Patient\s+Number|"
        r"Report\s+No\.?|Age\s*/\s*Gender|Age\s*/\s*Sex|"
        r"Age|Gender|Sex|Date\s+of\s+Collection|"
        r"Collection\s+Date|Date\s+of\s+Reporting|"
        r"Reporting\s+Date|Report\s+Date|Date\s+of\s+Report|"
        r"Ref\.?\s*By|Clinical\s+History|Sample\s+Type"
    )

    def get_field(pattern: str) -> str:
        match = re.search(
            rf"(?:{pattern})\s*[:+\-]?\s*(.*?)"
            rf"(?=\s+(?:{label})\s*[:+\-]|$)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return ""
        return re.sub(r"\s+", " ", match.group(1)).strip(" :+-|")

    fields["patient_name"] = get_field(
        r"Patient\s+Name|Name\s+of\s+Patient"
    )
    fields["patient_id"] = get_field(
        r"Patient\s+ID|Patient\s+Number"
    )
    fields["report_number"] = get_field(r"Report\s+No\.?")
    fields["collection_date"] = get_field(
        r"Date\s+of\s+Collection|Collection\s+Date"
    )
    fields["report_date"] = get_field(
        r"Date\s+of\s+Reporting|Reporting\s+Date|"
        r"Report\s+Date|Date\s+of\s+Report"
    )

    age_gender = get_field(r"Age\s*/\s*Gender|Age\s*/\s*Sex")
    match = re.search(
        r"\b(\d{1,3})\s*(?:years?|yrs?)?\s*[/, -]+\s*"
        r"(Male|Female|Other)\b",
        age_gender,
        re.IGNORECASE,
    )
    if match:
        fields["age"] = match.group(1)
        fields["gender"] = match.group(2).capitalize()

    if not fields["age"]:
        age = get_field(r"Age")
        match = re.search(r"\b(\d{1,3})\b", age)
        if match:
            fields["age"] = match.group(1)

    if not fields["gender"]:
        gender = get_field(r"Gender|Sex")
        match = re.search(r"\b(Male|Female|Other)\b", gender, re.I)
        if match:
            fields["gender"] = match.group(1).capitalize()

    return fields


# ---------------------------------------------------------
# LABORATORY RESULT HELPERS
# ---------------------------------------------------------

def _find_test(line: str):
    """Find the longest matching test alias at a word boundary."""
    matches = []
    for canonical, aliases in TEST_ALIASES.items():
        for alias in aliases:
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
            match = re.search(pattern, line, re.IGNORECASE)
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
    after = [m for m in candidates if m.start() >= test_match.end()]
    return after[0].group(0).strip() if after else None


def _extract_unit(line: str) -> str:
    match = UNIT_RE.search(line)
    return match.group(1).strip() if match else ""


def _reported_status(line: str) -> str:
    """Use explicit report flags when present."""
    patterns = [
        (r"\b(low|below range)\b", "Below range"),
        (r"\b(high|elevated|above range)\b", "Above range"),
        (r"\b(normal|within range|in range)\b", "Within range"),
        (r"\b(abnormal)\b", "Abnormal"),
        (r"\b(present)\b", "Present"),
    ]
    for pattern, status in patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return status
    return ""


def _status(value_text, reference_range):
    if not value_text:
        return "Needs review"

    value = _to_float(value_text)
    if value is None or not reference_range:
        return "Needs review"

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


def _extract_numeric_value(line: str, test_match, reference_range):
    """Find a likely result number after the test name."""
    range_matches = list(RANGE_RE.finditer(line))
    excluded = [m.span() for m in range_matches]
    candidates = []

    for match in VALUE_RE.finditer(line):
        start, end = match.span()
        if start < test_match.end():
            continue
        if any(start < b and end > a for a, b in excluded):
            continue
        candidates.append(match)

    if not candidates:
        return None

    return candidates[0].group(1).strip()


def _extract_text_value(line: str, test_match, reference_range):
    """
    Extract a non-numeric result such as Turbid, Many or Trace.
    Only use the text between the test name and reference range.
    """
    start = test_match.end()
    tail = line[start:].strip(" :|=+\t")

    range_match = RANGE_RE.search(tail)
    if range_match:
        tail = tail[:range_match.start()].strip(" :|=+\t")

    tail = re.sub(
        r"\b(low|high|normal|abnormal|present|elevated)\b.*$",
        "",
        tail,
        flags=re.IGNORECASE,
    ).strip(" :|=+\t")

    # Remove a recognized unit if it occurs at the end.
    tail = re.sub(
        r"\s+(?:mg/dl|mg/l|g/dl|g/l|u/l|ul|iu/l|%|"
        r"cells/cumm|cells/ul|cells/µl|/hpf)\s*$",
        "",
        tail,
        flags=re.IGNORECASE,
    ).strip()

    if not tail or VALUE_RE.search(tail):
        return None

    if len(tail) > 45:
        return None

    if re.fullmatch(r"[-–—]+", tail):
        return None

    return tail


def _make_result(
    canonical: str,
    value: str,
    unit: str,
    reference_range: str,
    status: str,
    source_line: str,
) -> dict[str, Any]:
    if status == "Needs review":
        reported = _reported_status(source_line)
        if reported:
            status = reported

    return {
        "test": canonical,
        "result": value,
        "unit": unit,
        "reference_range": reference_range or "Not provided",
        "status": status,
        "meaning": (
            f"{canonical} is a laboratory measurement. "
            "Its meaning depends on the laboratory method "
            "and clinical context."
        ),
        "interpretation": (
            "Status is based on the extracted report text or "
            "the reference range. This is not a diagnosis."
        ),
        "source_line": source_line,
        "needs_review": status in (
            "Needs review",
            "Reference range unavailable",
        ),
    }


# ---------------------------------------------------------
# LABORATORY RESULT EXTRACTION
# ---------------------------------------------------------

def analyze_report(extracted_text: str) -> list[dict[str, Any]]:
    """
    Parse laboratory rows conservatively.

    Supports:
    - Test, result, unit and range on one line.
    - OCR text with extra spaces and commas.
    - Numeric and selected text results.
    - Reported flags such as High, Low, Normal and Present.

    Ambiguous rows are skipped rather than assigned invented values.
    """
    if not extracted_text or not str(extracted_text).strip():
        return []

    text = _normalize_text(extracted_text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    results = []
    seen = set()

    for line in lines:
        if len(line) > 350:
            continue

        found = _find_test(line)
        if not found:
            continue

        canonical, alias, test_match = found

        # Skip headings and general discussion mentioning test names.
        if re.search(
            r"\b(test parameter|reference range|laboratory test report|"
            r"abnormal findings|impression|clinical history)\b",
            line,
            re.IGNORECASE,
        ):
            continue

        reference_range = _extract_range(line, test_match)
        unit = _extract_unit(line)

        value = _extract_numeric_value(
            line,
            test_match,
            reference_range,
        )

        if value is None:
            value = _extract_text_value(
                line,
                test_match,
                reference_range,
            )

        if value is None:
            continue

        # If the line has a numeric result but no range, do not
        # accidentally treat another number as a reference range.
        if reference_range:
            status = _status(value, reference_range)
        else:
            status = "Reference range unavailable"

        reported = _reported_status(line)
        if reported:
            status = reported

        key = (
            canonical.lower(),
            value.lower(),
            (reference_range or "").lower(),
            unit.lower(),
        )
        if key in seen:
            continue
        seen.add(key)

        results.append(
            _make_result(
                canonical=canonical,
                value=value,
                unit=unit,
                reference_range=reference_range or "",
                status=status,
                source_line=line,
            )
        )

    return results
