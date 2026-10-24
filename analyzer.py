
import re
import pandas as pd


TEST_ALIASES = {
    "Hemoglobin": ["hemoglobin", "haemoglobin", "hb"],
    "WBC Count": [
        "white blood cell count", "white blood cells",
        "wbc count", "total leukocyte count",
        "total leucocyte count", "tlc", "wbc"
    ],
    "Platelets": [
        "platelet count", "platelets", "thrombocyte count"
    ],
    "Fasting Blood Sugar": [
        "fasting blood sugar", "fasting blood glucose",
        "fasting glucose", "fbs"
    ],
    "Random Blood Sugar": [
        "random blood sugar", "random blood glucose",
        "random glucose", "rbs"
    ],
    "RBC Count": [
        "red blood cell count", "rbc count", "rbc"
    ],
    "HbA1c": [
        "hba1c", "hb a1c", "glycated hemoglobin",
        "glycosylated hemoglobin"
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
    "ALT": ["alanine aminotransferase", "sgpt", "alt"],
    "AST": ["aspartate aminotransferase", "sgot", "ast"],
    "TSH": ["thyroid stimulating hormone", "tsh"],
    "Vitamin D": ["25-oh vitamin d", "vitamin d"],
    "Vitamin B12": ["vitamin b12", "b12"],
    "ESR": ["erythrocyte sedimentation rate", "esr"],
    "CRP": ["c-reactive protein", "c reactive protein", "crp"],
    "Uric Acid": ["serum uric acid", "uric acid"],
    "Albumin": ["serum albumin", "albumin"],
    "Total Protein": ["total protein"],
    "MCV": ["mean corpuscular volume", "mcv"],
    "MCH": ["mean corpuscular hemoglobin", "mch"],
    "MCHC": [
        "mean corpuscular hemoglobin concentration", "mchc"
    ],
    "Hematocrit": ["hematocrit", "packed cell volume", "pcv"],
}

COLUMNS = [
    "Test", "Result", "Unit", "Reference Range", "Status"
]

NUMBER = r"[-+]?\d[\d,]*(?:\.\d+)?"

RANGE_PATTERN = re.compile(
    rf"(?<![\w.])({NUMBER})\s*(?:-|–|—|to)\s*({NUMBER})(?![\d.])",
    re.IGNORECASE,
)

UNIT_PATTERN = re.compile(
    r"(?:"
    r"g\s*/\s*d[l1]|g\s*/\s*l|"
    r"mg\s*/\s*d[l1]|mg\s*/\s*l|"
    r"mmol\s*/\s*l|µmol\s*/\s*l|umol\s*/\s*l|"
    r"ng\s*/\s*ml|pg\s*/\s*ml|"
    r"u\s*/\s*l|iu\s*/\s*l|miu\s*/\s*l|"
    r"cells?\s*/\s*(?:cumm|mm3|mm\^?3|µl|ul)|"
    r"lakh\s*/\s*(?:cumm|mm3|µl|ul)|"
    r"fl|pg|bpm|mm\s*/\s*hr?|%"
    r")",
    re.IGNORECASE,
)


def clean_line(value):
    value = str(value).replace("\u00a0", " ")
    value = value.replace("−", "-").replace("：", ":")
    return re.sub(r"\s+", " ", value).strip()


def number_value(value):
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def normalize_text(value):
    return re.sub(
        r"[^a-z0-9]+", " ", clean_line(value).lower()
    ).strip()


def find_test(line):
    normalized = normalize_text(line)
    matches = []

    for test_name, aliases in TEST_ALIASES.items():
        for alias in aliases:
            alias_normalized = normalize_text(alias)

            if re.search(
                r"(?<!\w)" + re.escape(alias_normalized) + r"(?!\w)",
                normalized,
            ):
                matches.append((test_name, len(alias_normalized)))

    if not matches:
        return None

    longest = max(length for _, length in matches)
    best = {
        name for name, length in matches if length == longest
    }

    return next(iter(best)) if len(best) == 1 else None


def find_test_match(line, test_name):
    matches = []

    for alias in TEST_ALIASES.get(test_name, []):
        pattern = re.compile(
            r"(?<![A-Za-z0-9])"
            + re.escape(alias)
            + r"(?![A-Za-z0-9])",
            re.IGNORECASE,
        )
        match = pattern.search(line)

        if match:
            matches.append(match)

    return max(matches, key=lambda m: len(m.group(0))) if matches else None


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
    return clean_line(line).lower().strip(":") in {
        "test", "test name", "result", "results",
        "reference range", "normal range", "units", "unit",
        "laboratory results", "laboratory result",
        "patient information", "clinical details"
    }


def parse_candidate(text):
    text = clean_line(text)

    if not text or is_header(text):
        return None

    range_match = RANGE_PATTERN.search(text)
    reference_range = None
    range_text = ""
    result_text = text

    if range_match:
        low = number_value(range_match.group(1))
        high = number_value(range_match.group(2))

        if low is not None and high is not None and low <= high:
            reference_range = (low, high)
            range_text = range_match.group(0)

        result_text = (
            text[:range_match.start()]
            + " "
            + text[range_match.end():]
        )

    unit = extract_unit(text)
    result_text = UNIT_PATTERN.sub(" ", result_text)

    result_text = re.sub(
        r"\b(?:result|value|observed value)\b\s*[:=]?",
        " ",
        result_text,
        flags=re.IGNORECASE,
    )

    numbers = re.findall(NUMBER, result_text)
    result = number_value(numbers[0]) if len(numbers) == 1 else None

    return {
        "result": result,
        "unit": unit,
        "reference_range": reference_range,
        "range_text": range_text,
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

        match = find_test_match(line, test_name)

        if match:
            own_line = (
                line[:match.start()] + " " + line[match.end():]
            ).strip(" :-|")
        else:
            own_line = line

        parsed = parse_candidate(own_line)

        if parsed is None:
            continue

        # Only consider a continuation when the test's own line
        # does not contain an unambiguous result.
        if parsed["result"] is None:
            continuations = []

            for j in range(index + 1, min(index + 3, len(lines))):
                next_line = lines[j]

                # Never take data from the next test.
                if find_test(next_line):
                    break

                if is_header(next_line):
                    continue

                item = parse_candidate(next_line)

                if item and item["result"] is not None:
                    continuations.append(item)

            if len(continuations) == 1:
                item = continuations[0]
                parsed["result"] = item["result"]

                if not parsed["unit"]:
                    parsed["unit"] = item["unit"]

                if parsed["reference_range"] is None:
                    parsed["reference_range"] = item["reference_range"]
                    parsed["range_text"] = item["range_text"]

        result = parsed["result"]
        unit = parsed["unit"]
        reference_range = parsed["reference_range"]

        results.append({
            "Test": test_name,
            "Result": result if result is not None else "Needs review",
            "Unit": unit,
            "Reference Range": parsed["range_text"],
            "Status": classify_result(
                test_name, result, reference_range, unit
            ),
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
                pattern, text, re.IGNORECASE | re.MULTILINE
            )

            if match:
                fields[field_name] = match.group(1).strip()[:100]
                break

    return fields
