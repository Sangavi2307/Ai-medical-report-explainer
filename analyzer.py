
"""
analyzer.py
Conservative laboratory report analyzer for the
AI Medical Report Explainer application.

Important:
- Does not diagnose diseases.
- Does not invent missing values or reference ranges.
- Does not automatically correct decimal/OCR errors.
- Marks ambiguous results for manual review.
- Extracts patient details from common report layouts.
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
        "fasting plasma glucose", "fasting blood glucose",
        "fasting glucose", "fasting blood sugar", "fbs"
    ],
    "Random Glucose": [
        "random plasma glucose", "random blood glucose",
        "random glucose", "random blood sugar", "rbs"
    ],
    "HbA1c": [
        "hba1c", "hb a1c", "glycated hemoglobin",
        "glycosylated hemoglobin"
    ],
    "Creatinine": ["serum creatinine", "creatinine"],
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
    rf"|(?:less than|greater than|up to|at least|below|above)\s*"
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


# ---------------------------------------------------------
# PATIENT INFORMATION EXTRACTION
# ---------------------------------------------------------

def extract_patient_fields(extracted_text: str) -> dict[str, str]:
    """
    Extract patient details when labels and values appear
    either on the same line or on separate lines.

    Example:
        Patient Name
        Ananya Sharma (fictional)
        Patient ID
        ML-TEST-104
        Age / Sex
        45 years / Female
        Report Date
        22 October 2026
    """
    text = _normalize_text(extracted_text)
    lines = [line.strip() for line in text.splitlines()]
    fields: dict[str, str] = {}

    label_pattern = (
        r"patient\s+name|name\s+of\s+patient|name|"
        r"patient\s+id|patient\s+number|id|"
        r"age\s*/\s*sex|age|gender|sex|"
        r"report\s+date|date\s+of\s+report|"
        r"date\s+of\s+visit|date\s+of\s+collection|"
        r"collection\s+date|date|"
        r"referring\s+doctor|doctor|specimen|"
        r"clinical\s+note|report\s+status"
    )

    def is_label(value: str) -> bool:
        return bool(
            re.fullmatch(
                rf"(?:{label_pattern})\s*:?",
                value.strip(),
                flags=re.IGNORECASE,
            )
        )

    def find_value(pattern: str) -> str:
        # Labels and values on separate lines.
        for index, line in enumerate(lines):
            if re.fullmatch(
                rf"(?:{pattern})\s*:?",
                line,
                flags=re.IGNORECASE,
            ):
                for candidate in lines[index + 1:index + 5]:
                    candidate = candidate.strip()

                    if not candidate:
                        continue

                    if is_label(candidate):
                        break

                    # Ignore obvious headings instead of treating
                    # them as patient values.
                    if re.fullmatch(
                        r"(?:page\s+\d+|laboratory results|"
                        r"sample interpretation note)",
                        candidate,
                        flags=re.IGNORECASE,
                    ):
                        continue

                    return candidate

        # Labels and values on the same line, e.g. "Age: 45".
        match = re.search(
            rf"^\s*(?:{pattern})\s*:\s*(.+?)\s*$",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )

        if match:
            return match.group(1).strip()

        return ""

    # Patient name
    name = find_value(
        r"patient\s+name|name\s+of\s+patient|name"
    )

    if name:
        name = re.sub(
            r"\s*\(fictional\)\s*$",
            "",
            name,
            flags=re.IGNORECASE,
        ).strip()

        if name and not is_label(name):
            fields["patient_name"] = name

    # Patient ID
    patient_id = find_value(
        r"patient\s+id|patient\s+number|id"
    )

    if patient_id and not is_label(patient_id):
        fields["patient_id"] = patient_id

    # Age and sex together, e.g. "45 years / Female".
    age_sex = find_value(r"age\s*/\s*sex")

    if age_sex:
        age_match = re.search(
            r"\b(\d{1,3})\s*(?:years?|yrs?)?\b",
            age_sex,
            flags=re.IGNORECASE,
        )
        sex_match = re.search(
            r"\b(male|female|other)\b",
            age_sex,
            flags=re.IGNORECASE,
        )

        if age_match:
            fields["age"] = age_match.group(1)

        if sex_match:
            fields["gender"] = sex_match.group(1).capitalize()

    # Separate age field.
    if "age" not in fields:
        age_text = find_value(r"(?:patient\s+)?age")
        age_match = re.search(
            r"\b(\d{1,3})\s*(?:years?|yrs?)?\b",
            age_text,
            flags=re.IGNORECASE,
        )

        if age_match:
            fields["age"] = age_match.group(1)

    # Separate gender/sex field.
    if "gender" not in fields:
        gender_text = find_value(r"gender|sex")
        gender_match = re.search(
            r"\b(male|female|other)\b",
            gender_text,
            flags=re.IGNORECASE,
        )

        if gender_match:
            fields["gender"] = gender_match.group(1).capitalize()

    # Report date, including labels on separate lines.
    report_date = find_value(
        r"report\s+date|date\s+of\s+report|"
        r"date\s+of\s+visit|date\s+of\s+collection|"
        r"collection\s+date"
    )

    if not report_date:
        report_date = find_value(r"date")

    if report_date and not is_label(report_date):
        fields["report_date"] = report_date.strip()

    return fields


# ---------------------------------------------------------
# LABORATORY RESULT EXTRACTION
# ---------------------------------------------------------

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

    Supports test name, result and range on the same line.
    Attempts a limited multi-line fallback for isolated labels.
    """
    if not extracted_text or not str(extracted_text).strip():
        return []

    text = _normalize_text(extracted_text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    results = []
    seen = set()

    for index, original_line in enumerate(lines):
        line = original_line
        found = _find_test(line)

        # Limited fallback when the label and result are separated.
        if found and not VALUE_RE.search(line):
            next_line = (
                lines[index + 1]
                if index + 1 < len(lines)
                else ""
            )

            if next_line and len(next_line) < 200:
                combined = f"{line} {next_line}"
                combined_found = _find_test(combined)

                if combined_found:
                    line = combined
                    found = combined_found

        if not found or len(line) > 300:
            continue

        canonical, alias, test_match = found

        reference_range = _extract_range(line, test_match)

        value_text, _ = _extract_value(
            line,
            test_match,
            reference_range,
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
                "Its meaning depends on the laboratory method "
                "and clinical context."
            ),
            "interpretation": (
                "Compared with the reference range detected in "
                "the extracted text. This is not a diagnosis."
                if status in (
                    "Below range",
                    "Above range",
                    "Within range",
                )
                else
                "The result or reference range could not be safely "
                "classified. Check the original report."
            ),
            "source_line": line,
            "needs_review": status in (
                "Needs review",
                "Reference range unavailable",
            ),
        })

    return results
