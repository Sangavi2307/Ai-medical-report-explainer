
import re
import pandas as pd


TEST_ALIASES = {
    "Hemoglobin": ["hemoglobin", "haemoglobin", "hb"],
    "WBC Count": [
        "wbc count",
        "white blood cell count",
        "white blood cells",
        "wbc",
    ],
    "Platelets": ["platelet count", "platelets", "thrombocyte count"],
    "Fasting Blood Sugar": [
        "fasting blood sugar",
        "fasting glucose",
        "fbs",
    ],
    "Random Blood Sugar": ["random blood sugar", "random glucose", "rbs"],
    "RBC Count": ["rbc count", "red blood cell count", "rbc"],
    "HbA1c": [
        "hba1c",
        "hb a1c",
        "glycated hemoglobin",
        "glycosylated hemoglobin",
    ],
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
    r"(?:g\s*/\s*d[l1]|g\s*/\s*l|mg\s*/\s*d[l1]|mg\s*/\s*l|"
    r"mmol\s*/\s*l|µmol\s*/\s*l|umol\s*/\s*l|"
    r"ng\s*/\s*ml|pg\s*/\s*ml|u\s*/\s*l|iu\s*/\s*l|"
    r"miu\s*/\s*l|fl|pg|ml|bpm|mm\s*/\s*h[r]?|"
    r"/\s*µl|/\s*ul|%|lakh\s*/\s*µl|lakh\s*/\s*ul)",
    re.IGNORECASE,
)


def to_number(value):
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def extract_numbers(text):
    values = []

    for match in NUMBER_PATTERN.finditer(str(text)):
        number = to_number(match.group())

        if number is not None:
            values.append((number, match.start(), match.end()))

    return values


def parse_range(text):
    match = RANGE_PATTERN.search(str(text))

    if not match:
        return None

    low = to_number(match.group(1))
    high = to_number(match.group(2))

    if low is None or high is None or low > high:
        return None

    return low, high, match.group(0)


def normalize_line(line):
    line = str(line).replace("\u00a0", " ")
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def find_test(line):
    normalized = normalize_line(line).lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized).strip()

    aliases = []

    for canonical, names in TEST_ALIASES.items():
        for alias in names:
            aliases.append((canonical, alias))

    # Match longer test names before short names such as "hb" or "ldl".
    aliases.sort(key=lambda item: len(item[1]), reverse=True)

    for canonical, alias in aliases:
        alias_normalized = re.sub(
            r"[^a-z0-9]+", " ", alias.lower()
        ).strip()

        if re.search(
            r"(?<!\w)" + re.escape(alias_normalized) + r"(?!\w)",
            normalized,
        ):
            return canonical, alias

    return None, None


def extract_unit(text):
    match = UNIT_PATTERN.search(str(text))
    return normalize_line(match.group(0)) if match else ""


def classify_result(test_name, result, reference_range, unit=""):
    if result is None or reference_range is None:
        return "Needs review"

    value = to_number(result)

    if value is None:
        return "Needs review"

    try:
        low = to_number(reference_range[0])
        high = to_number(reference_range[1])
    except (TypeError, IndexError):
        return "Needs review"

    if low is None or high is None or low > high:
        return "Needs review"

    if value < low:
        return "Below range"

    if value > high:
        return "Above range"

    return "Within range"


def is_header_or_metadata(line):
    text = normalize_line(line).lower().rstrip(":")
    ignored = {
        "test",
        "result",
        "reference range",
        "normal range",
        "laboratory results",
        "laboratory result",
        "patient information",
        "clinical details",
        "assessment",
        "advice",
        "units",
        "unit",
    }
    return text in ignored


def looks_like_result_line(line):
    text = normalize_line(line)

    if not text or is_header_or_metadata(text):
        return False

    # A range-only line must not be mistaken for the result.
    if parse_range(text):
        return False

    numbers = extract_numbers(text)
    return len(numbers) == 1


def analyze_report(report_text):
    columns = [
        "Test",
        "Result",
        "Unit",
        "Reference Range",
        "Status",
    ]

    if not report_text or not str(report_text).strip():
        return pd.DataFrame(columns=columns)

    lines = [
        normalize_line(line)
        for line in str(report_text).splitlines()
        if normalize_line(line)
    ]

    results = []
    seen_tests = set()

    for index, line in enumerate(lines):
        test_name, _ = find_test(line)

        if not test_name or test_name in seen_tests:
            continue

        # This sample format places the result and reference range
        # on separate lines after the test name.
        result_index = None
        result_value = None
        result_line = ""

        for j in range(index + 1, min(index + 5, len(lines))):
            candidate = lines[j]

            # Stop if the next test starts before we find this result.
            next_test, _ = find_test(candidate)
            if next_test:
                break

            if is_header_or_metadata(candidate):
                continue

            if looks_like_result_line(candidate):
                nums = extract_numbers(candidate)
                result_value = nums[0][0]
                result_index = j
                result_line = candidate
                break

        if result_index is None:
            continue

        # Search after the result for its range, stopping at another test.
        range_text = ""
        reference_range = None

        for j in range(result_index + 1, min(result_index + 4, len(lines))):
            candidate = lines[j]

            next_test, _ = find_test(candidate)
            if next_test:
                break

            parsed_range = parse_range(candidate)

            if parsed_range:
                low, high, range_text = parsed_range
                reference_range = (low, high)
                break

        combined_text = result_line
        if range_text:
            combined_text += " " + range_text

        unit = extract_unit(combined_text)

        status = classify_result(
            test_name,
            result_value,
            reference_range,
            unit,
        )

        results.append({
            "Test": test_name,
            "Result": result_value,
            "Unit": unit,
            "Reference Range": range_text,
            "Status": status,
        })

        seen_tests.add(test_name)

    return pd.DataFrame(results, columns=columns)


def extract_patient_fields(report_text):
    fields = {}

    if not report_text:
        return fields

    text = str(report_text)

    patterns = {
        "patient_name": [
            r"Patient\s*Name\s*[:\-]?\s*\n?\s*([^\n\r]+)",
            r"\bName\s*[:\-]\s*([^\n\r]+)",
        ],
        "age": [
            r"\bAge\s*[/:\-]?\s*(\d{1,3})\s*(?:years?|yrs?)?\b",
        ],
        "gender": [
            r"\b(?:gender|sex)\s*[:/\-]?\s*(?:\d{1,3}\s*years?\s*/\s*)?"
            r"(male|female|other)\b",
        ],
        "report_date": [
            r"(?:report\s*date|collection\s*date|date\s*of\s*visit|date)"
            r"\s*[:\-]?\s*\n?\s*"
            r"(\d{1,2}\s+[A-Za-z]+\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        ],
        "patient_id": [
            r"(?:patient\s*id|patient\s*no|mrn|registration\s*no)"
            r"\s*[:\-]?\s*\n?\s*([A-Za-z0-9\-\/]+)",
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
