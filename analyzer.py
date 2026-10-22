
import re
import pandas as pd


TEST_ALIASES = {
    "Fasting Blood Sugar": ["fasting blood sugar", "fasting glucose", "fbs"],
    "Random Blood Sugar": ["random blood sugar", "random glucose", "rbs"],
    "Hemoglobin": ["hemoglobin", "haemoglobin", "hb"],
    "WBC Count": ["wbc count", "white blood cell count", "white blood cells", "wbc"],
    "Platelets": ["platelet count", "platelets", "thrombocyte count"],
    "RBC Count": ["rbc count", "red blood cell count", "rbc"],
    "HbA1c": ["hba1c", "hb a1c", "glycated hemoglobin", "glycosylated hemoglobin"],
    "Creatinine": ["serum creatinine", "creatinine"],
    "Urea": ["blood urea", "serum urea", "urea"],
    "Total Cholesterol": ["total cholesterol", "cholesterol"],
    "LDL Cholesterol": ["ldl cholesterol", "ldl"],
    "HDL Cholesterol": ["hdl cholesterol", "hdl"],
    "Triglycerides": ["triglycerides", "triglyceride"],
    "Sodium": ["serum sodium", "sodium"],
    "Potassium": ["serum potassium", "potassium"],
    "Calcium": ["serum calcium", "calcium"],
    "Bilirubin": ["total bilirubin", "bilirubin"],
    "ALT": ["sgpt", "alanine aminotransferase", "alt"],
    "AST": ["sgot", "aspartate aminotransferase", "ast"],
    "TSH": ["thyroid stimulating hormone", "tsh"],
    "Vitamin D": ["25-oh vitamin d", "vitamin d"],
    "Vitamin B12": ["vitamin b12", "b12"],
    "ESR": ["erythrocyte sedimentation rate", "esr"],
    "CRP": ["c-reactive protein", "crp"],
    "Uric Acid": ["serum uric acid", "uric acid"],
    "Albumin": ["serum albumin", "albumin"],
    "Total Protein": ["total protein"],
    "MCV": ["mean corpuscular volume", "mcv"],
    "MCH": ["mean corpuscular hemoglobin", "mch"],
    "MCHC": ["mean corpuscular hemoglobin concentration", "mchc"],
    "Hematocrit": ["hematocrit", "packed cell volume", "pcv"],
}

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
    r"(%|g/dl|g/l|mg/dl|mg/l|mmol/l|µmol/l|umol/l|"
    r"ng/ml|pg/ml|u/l|iu/l|miu/l|fl|pg|ml|bpm|mm/hr|mm/h)",
    re.IGNORECASE,
)


def to_number(value):
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def extract_numbers(text):
    numbers = []

    for match in NUMBER_PATTERN.finditer(str(text)):
        value = to_number(match.group())

        if value is not None:
            numbers.append((value, match.start(), match.end()))

    return numbers


def parse_range(text):
    match = RANGE_PATTERN.search(str(text))

    if not match:
        return None

    low = to_number(match.group(1))
    high = to_number(match.group(2))

    if low is None or high is None or low > high:
        return None

    return low, high, match.group(0)


def find_test(line):
    aliases = []

    for canonical, names in TEST_ALIASES.items():
        for alias in names:
            aliases.append((canonical, alias))

    aliases.sort(key=lambda item: len(item[1]), reverse=True)

    for canonical, alias in aliases:
        pattern = r"(?<![a-z])" + re.escape(alias) + r"(?![a-z])"

        if re.search(pattern, line, re.IGNORECASE):
            return canonical, alias

    return None, None


def extract_unit(text):
    match = UNIT_PATTERN.search(str(text))
    return match.group(0) if match else ""


def classify_result(test_name, result, reference_range, unit=""):
    if result is None:
        return "Needs review"

    value = to_number(result)

    if value is None:
        return "Needs review"

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

    if str(test_name).strip().lower() == "hba1c" and "%" in str(unit):
        if value < 5.7:
            return "Below diabetes screening threshold"
        elif value < 6.5:
            return "Prediabetes screening range"
        else:
            return "Above diabetes screening threshold"

    return "Needs review"


def parse_test_line(line, extra_line=""):
    canonical, alias = find_test(line)

    if not canonical:
        return None

    alias_match = re.search(
        r"(?<![a-z])" + re.escape(alias) + r"(?![a-z])",
        line,
        re.IGNORECASE,
    )

    remainder = line[alias_match.end():] if alias_match else line
    combined = remainder + (" " + extra_line if extra_line else "")

    range_info = parse_range(combined)

    if range_info:
        low, high, range_text = range_info
        range_match = RANGE_PATTERN.search(combined)

        before_range = combined[:range_match.start()]
        numbers_before = extract_numbers(before_range)

        if numbers_before:
            result_value = numbers_before[0][0]
        else:
            after_range = combined[range_match.end():]
            numbers_after = extract_numbers(after_range)
            result_value = numbers_after[0][0] if numbers_after else None

        reference_range = (low, high, range_text)
    else:
        range_text = ""
        reference_range = None
        numbers = extract_numbers(remainder)

        if not numbers and extra_line:
            numbers = extract_numbers(extra_line)

        result_value = numbers[0][0] if numbers else None

    if result_value is None:
        return None

    unit = extract_unit(combined)

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


def analyze_report(report_text):
    columns = ["Test", "Result", "Unit", "Reference Range", "Status"]

    if not report_text or not str(report_text).strip():
        return pd.DataFrame(columns=columns)

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in str(report_text).splitlines()
        if line.strip()
    ]

    results = []
    seen_tests = set()

    for index, line in enumerate(lines):
        next_line = lines[index + 1] if index + 1 < len(lines) else ""

        parsed = parse_test_line(line, next_line)

        if not parsed:
            continue

        if parsed["Test"] in seen_tests:
            continue

        seen_tests.add(parsed["Test"])
        results.append(parsed)

    return pd.DataFrame(results, columns=columns)


def extract_patient_fields(report_text):
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
                fields[field_name] = match.group(1).strip()[:100]
                break

    return fields
