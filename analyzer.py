
import re
import pandas as pd

COLUMNS = [
    "Test",
    "Result",
    "Unit",
    "Reference Range",
    "Status",
]

TEST_PATTERNS = [
    ("HbA1c", r"\bhba1c\b"),
    ("Hemoglobin", r"\b(?:hemoglobin|haemoglobin|hb)\b"),
    ("WBC Count", r"\b(?:wbc(?:\s+count)?|white blood cells?(?:\s+count)?)\b"),
    ("Platelets", r"\b(?:platelets?|platelet count)\b"),
    ("Fasting Blood Sugar", r"\b(?:fasting blood sugar|fasting glucose|fbs)\b"),
    ("Random Blood Sugar", r"\b(?:random blood sugar|random glucose|rbs)\b"),
    ("RBC Count", r"\b(?:rbc(?:\s+count)?|red blood cells?(?:\s+count)?)\b"),
    ("Total Cholesterol", r"\btotal cholesterol\b"),
    ("Creatinine", r"\bcreatinine\b"),
    ("Urea", r"\burea\b"),
    ("Sodium", r"\bsodium\b"),
    ("Potassium", r"\bpotassium\b"),
    ("TSH", r"\btsh\b"),
    ("Hematocrit", r"\b(?:hematocrit|haematocrit|pcv)\b"),
]

NUMBER = r"\d[\d,]*(?:\.\d+)?"

RANGE_RE = re.compile(
    rf"(?<![\d.])({NUMBER})\s*(?:-|to)\s*({NUMBER})(?![\d.])",
    re.I,
)

UNIT_RE = re.compile(
    r"(?:"
    r"lakh\s*/\s*[µμu]?l|"
    r"million\s*/\s*[µμu]?l|"
    r"cells?\s*/\s*[µμu]?l|"
    r"/\s*[µμu]?l|"
    r"mg\s*/\s*dl|g\s*/\s*dl|"
    r"mmol\s*/\s*l|"
    r"m[iu]u\s*/\s*l|"
    r"ng\s*/\s*ml|pg\s*/\s*ml|"
    r"µ?mol\s*/\s*l|"
    r"fl|%"
    r")",
    re.I,
)


def clean_lines(text):
    text = (text or "").replace("\r", "\n")
    text = text.replace("\u00a0", " ")
    text = text.replace("–", "-").replace("—", "-").replace("−", "-")

    return [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]


def find_test(line):
    for name, pattern in TEST_PATTERNS:
        match = re.search(pattern, line, re.I)
        if match:
            return name, pattern, match
    return None


def to_number(value):
    try:
        return float(value.replace(",", ""))
    except (ValueError, AttributeError):
        return None


def parse_block(test_name, lines):
    block = " ".join(lines)

    pattern = dict(TEST_PATTERNS)[test_name]
    block = re.sub(pattern, " ", block, count=1, flags=re.I)

    range_match = RANGE_RE.search(block)
    low = high = None
    reference_range = ""

    if range_match:
        low = to_number(range_match.group(1))
        high = to_number(range_match.group(2))
        reference_range = range_match.group(0).strip()

        # Remove the range before looking for the measured result.
        block_for_value = (
            block[:range_match.start()]
            + " "
            + block[range_match.end():]
        )
    else:
        block_for_value = block

    values = re.findall(
        r"(?<![\w.])(" + NUMBER + r")(?![\w.])",
        block_for_value,
    )

    if not values:
        return None

    result = to_number(values[0])

    if result is None:
        return None

    unit_match = UNIT_RE.search(block)
    unit = unit_match.group(0) if unit_match else ""

    if low is None or high is None:
        status = "Range not recognized"
    elif low <= result <= high:
        status = "Within Range"
    elif result < low:
        status = "Below Range"
    else:
        status = "Above Range"

    return {
        "Test": test_name,
        "Result": result,
        "Unit": unit,
        "Reference Range": reference_range,
        "Status": status,
    }


def analyze_report(report_text):
    if not report_text or not report_text.strip():
        return pd.DataFrame(columns=COLUMNS)

    lines = clean_lines(report_text)
    starts = []

    for index, line in enumerate(lines):
        found = find_test(line)

        if found:
            name, _, _ = found
            starts.append((index, name))

    results = []
    seen = set()

    for position, (start, test_name) in enumerate(starts):
        if test_name in seen:
            continue

        if position + 1 < len(starts):
            end = starts[position + 1][0]
        else:
            end = min(start + 7, len(lines))

        block_lines = lines[start:end][:7]
        parsed = parse_block(test_name, block_lines)

        if parsed is not None:
            results.append(parsed)
            seen.add(test_name)

    # If test labels and results are separated into table columns,
    # try matching each test with nearby numbers and ranges.
    if not results:
        flat_text = " ".join(lines)
        for test_name, pattern in TEST_PATTERNS:
            match = re.search(pattern, flat_text, re.I)
            if not match:
                continue

            parsed = parse_block(
                test_name,
                [flat_text[match.start():match.start() + 180]],
            )

            if parsed is not None:
                results.append(parsed)

    return pd.DataFrame(results, columns=COLUMNS)


def extract_patient_fields(report_text):
    text = report_text or ""

    fields = {
        "Patient Name": "Not found",
        "Age / Gender": "Not found",
        "Patient ID": "Not found",
        "Date of Visit": "Not found",
        "Physician": "Not found",
    }

    patterns = {
        "Patient Name": r"Patient Name\s*:?\s*([^\n]+)",
        "Age / Gender": r"Age\s*/\s*Gender\s*:?\s*([^\n]+)",
        "Patient ID": r"Patient ID\s*:?\s*([^\n]+)",
        "Date of Visit": r"(?:Date of Visit|Date of Examination)\s*:?\s*([^\n]+)",
        "Physician": r"(?:Physician|Consulting Doctor)\s*:?\s*([^\n]+)",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.I)

        if match:
            value = match.group(1).strip()

            if value and value.lower() not in {
                "not found", "name", "age", "gender"
            }:
                fields[field] = value

    return fields
