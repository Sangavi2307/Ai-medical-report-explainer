
import re
import pandas as pd


TEST_ALIASES = {
    "Hemoglobin": ["hemoglobin", "haemoglobin", "hb"],
    "WBC Count": ["wbc count", "white blood cell count", "white blood cells", "wbc"],
    "Platelets": ["platelet count", "platelets", "thrombocyte count"],
    "Fasting Blood Sugar": ["fasting blood sugar", "fasting glucose", "fbs"],
    "Random Blood Sugar": ["random blood sugar", "random glucose", "rbs"],
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


COLUMNS = [
    "Test",
    "Result",
    "Unit",
    "Reference Range",
    "Status",
]


NUMBER = r"[-+]?\d[\d,]*(?:\.\d+)?"

RANGE_PATTERN = re.compile(
    rf"(?<![\w.])({NUMBER})\s*(?:-|–|—|to)\s*({NUMBER})(?![\d.])",
    re.IGNORECASE,
)

UNIT_PATTERN = re.compile(
    r"\b(?:g\s*/\s*d[l1]|g\s*/\s*l|mg\s*/\s*d[l1]|mg\s*/\s*l|"
    r"mmol\s*/\s*l|umol\s*/\s*l|µmol\s*/\s*l|"
    r"ng\s*/\s*ml|pg\s*/\s*ml|u\s*/\s*l|iu\s*/\s*l|"
    r"miu\s*/\s*l|fl|pg|bpm|mm\s*/\s*hr?|"
    r"lakh\s*/\s*[µu]l|/\s*[µu]l|%)\b?",
    re.IGNORECASE,
)


def clean_line(value):
    value = str(value).replace("\u00a0", " ")
    value = value.replace("−", "-")
    return re.sub(r"\s+", " ", value).strip()


def number_value(value):
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def find_test(line):
    normalized = re.sub(
        r"[^a-z0-9]+", " ", clean_line(line).lower()
    ).strip()

    aliases = []

    for canonical, names in TEST_ALIASES.items():
        for alias in names:
            alias_clean = re.sub(
                r"[^a-z0-9]+", " ", alias.lower()
            ).strip()
            aliases.append((canonical, alias_clean))

    aliases.sort(key=lambda item: len(item[1]), reverse=True)

    for canonical, alias in aliases:
        if re.search(
            r"(?<!\w)" + re.escape(alias) + r"(?!\w)",
            normalized,
        ):
            return canonical

    return None


def parse_range(text):
    match = RANGE_PATTERN.search(clean_line(text))

    if not match:
        return None

    low = number_value(match.group(1))
    high = number_value(match.group(2))

    if low is None or high is None or low > high:
        return None

    return low, high, match.group(0)


def extract_unit(text):
    match = UNIT_PATTERN.search(clean_line(text))
    return clean_line(match.group(0)) if match else ""


def classify_result(test_name, result, reference_range, unit=""):
    value = number_value(result)

    if value is None or reference_range is None:
        return "Needs review"

    low, high = reference_range

    if low is None or high is None or low > high:
        return "Needs review"

    if value < low:
        return "Below range"

    if value > high:
        return "Above range"

    return "Within range"


def is_header(line):
    normalized = clean_line(line).lower().strip(":")
    return normalized in {
        "test", "test name", "result", "results",
        "reference range", "normal range", "units", "unit",
        "laboratory results", "laboratory result",
        "patient information", "clinical details",
    }


def analyze_report(report_text):
    if not report_text or not str(report_text).strip():
        return pd.DataFrame(columns=COLUMNS)

    lines = [
        clean_line(line)
        for line in str(report_text).splitlines()
        if clean_line(line)
    ]

    results = []
    seen = set()

    for index, line in enumerate(lines):
        test_name = find_test(line)

        if not test_name or test_name in seen:
            continue

        # First look at the same line after the test name.
        alias_match = None
        normalized_line = clean_line(line)

        for alias in sorted(
            TEST_ALIASES[test_name],
            key=len,
            reverse=True,
        ):
            alias_match = re.search(
                re.escape(alias),
                normalized_line,
                re.IGNORECASE,
            )
            if alias_match:
                break

        same_line_remainder = (
            normalized_line[alias_match.end():]
            if alias_match else ""
        )

        # Look at the test line and the next few lines.
        # Stop before crossing into the next identified test.
        candidates = [same_line_remainder]

        for j in range(index + 1, min(index + 5, len(lines))):
            if find_test(lines[j]):
                break
            candidates.append(lines[j])

        result = None
        unit = ""
        reference_range = None
        range_text = ""

        for candidate in candidates:
            if not candidate or is_header(candidate):
                continue

            # Remove the reference range before looking for the result.
            parsed = parse_range(candidate)
            candidate_without_range = candidate

            if parsed:
                low, high, range_text = parsed
                reference_range = (low, high)
                candidate_without_range = (
                    candidate[:RANGE_PATTERN.search(candidate).start()]
                    + candidate[RANGE_PATTERN.search(candidate).end():]
                )

            found_unit = extract_unit(candidate)
            if found_unit and not unit:
                unit = found_unit

            numbers = re.findall(NUMBER, candidate_without_range)

            # Do not treat a range-only line as a result.
            if len(numbers) == 1 and result is None:
                result = number_value(numbers[0])

            # A line may contain result and range together.
            # If the range was found, the remaining single number is the result.
            if parsed and result is None:
                remaining = re.findall(NUMBER, candidate_without_range)
                if len(remaining) == 1:
                    result = number_value(remaining[0])

        # Some reports print result, unit and range on one line.
        status = classify_result(
            test_name,
            result,
            reference_range,
            unit,
        )

        if result is not None:
            results.append({
                "Test": test_name,
                "Result": result,
                "Unit": unit,
                "Reference Range": range_text,
                "Status": status,
            })
            seen.add(test_name)

    return pd.DataFrame(results, columns=COLUMNS)


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
            r"\b(?:gender|sex)\s*[:/\-]?\s*(male|female|other)\b",
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
