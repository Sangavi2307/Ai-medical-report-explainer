
import re
import pandas as pd

COLUMNS = [
    "Test", "Result", "Unit", "Reference Range", "Status"
]

# Common laboratory tests and their aliases.
TESTS = [
    ("Hemoglobin", [r"hemoglobin", r"haemoglobin", r"\bhb\b"]),
    ("WBC Count", [r"\bwbc\b", r"white blood cell"]),
    ("RBC Count", [r"\brbc\b", r"red blood cell"]),
    ("Platelets", [r"platelet"]),
    ("Hematocrit", [r"hematocrit", r"haematocrit", r"\bpcv\b"]),
    ("MCV", [r"\bmcv\b", r"mean corpuscular volume"]),
    ("MCH", [r"\bmch\b", r"mean corpuscular hemoglobin"]),
    ("MCHC", [r"\bmchc\b"]),
    ("Neutrophils", [r"neutrophil"]),
    ("Lymphocytes", [r"lymphocyte"]),
    ("Eosinophils", [r"eosinophil"]),
    ("Monocytes", [r"monocyte"]),
    ("Basophils", [r"basophil"]),
    ("Fasting Blood Sugar", [r"fasting blood sugar", r"fasting glucose", r"\bfbs\b"]),
    ("Random Blood Sugar", [r"random blood sugar", r"random glucose", r"\brbs\b"]),
    ("HbA1c", [r"\bhba1c\b", r"glycated hemoglobin"]),
    ("Total Cholesterol", [r"total cholesterol"]),
    ("HDL Cholesterol", [r"\bhdl\b"]),
    ("LDL Cholesterol", [r"\bldl\b"]),
    ("Triglycerides", [r"triglyceride"]),
    ("Creatinine", [r"creatinine"]),
    ("Blood Urea", [r"\burea\b", r"\bbun\b", r"blood urea nitrogen"]),
    ("Uric Acid", [r"uric acid"]),
    ("Sodium", [r"\bsodium\b", r"\bna\+\b"]),
    ("Potassium", [r"\bpotassium\b", r"\bk\+\b"]),
    ("Chloride", [r"\bchloride\b"]),
    ("Calcium", [r"\bcalcium\b"]),
    ("Magnesium", [r"\bmagnesium\b"]),
    ("Phosphorus", [r"\bphosphorus\b"]),
    ("Total Bilirubin", [r"total bilirubin"]),
    ("Direct Bilirubin", [r"direct bilirubin"]),
    ("ALT / SGPT", [r"\balt\b", r"\bsgpt\b"]),
    ("AST / SGOT", [r"\bast\b", r"\bsgot\b"]),
    ("Alkaline Phosphatase", [r"alkaline phosphatase", r"\balp\b"]),
    ("Albumin", [r"\balbumin\b"]),
    ("Total Protein", [r"total protein"]),
    ("TSH", [r"\btsh\b", r"thyroid stimulating hormone"]),
    ("T3", [r"\bt3\b", r"triiodothyronine"]),
    ("T4", [r"\bt4\b", r"thyroxine"]),
    ("Vitamin D", [r"vitamin d", r"25-oh vitamin d"]),
    ("Vitamin B12", [r"vitamin b12", r"cobalamin"]),
    ("CRP", [r"\bcrp\b", r"c-reactive protein"]),
    ("ESR", [r"\besr\b", r"erythrocyte sedimentation"]),
    ("Amylase", [r"\bamylase\b"]),
    ("Lipase", [r"\blipase\b"]),
    ("PSA", [r"\bpsa\b", r"prostate specific antigen"]),
    ("Ferritin", [r"\bferritin\b"]),
    ("Iron", [r"\biron\b"]),
    ("Urine pH", [r"urine ph"]),
    ("Specific Gravity", [r"specific gravity"]),
]

NUMBER = r"[-+]?\d[\d,]*(?:\.\d+)?"

RANGE = re.compile(
    rf"({NUMBER})\s*(?:-|to)\s*({NUMBER})",
    re.I
)

VALUE = re.compile(NUMBER)

UNIT = re.compile(
    r"\b(?:mg/dL|mg/L|g/dL|g/L|mmol/L|"
    r"umol/L|µmol/L|ng/mL|pg/mL|"
    r"mIU/L|uIU/mL|IU/L|U/L|"
    r"cells/uL|cells/µL|"
    r"mm/hr|mm/h|fL|pg|%|"
    r"million/uL|lakh/uL)\b|"
    r"/\s*[uµμ]?L",
    re.I
)


def normalize(text):
    text = (text or "").replace("\u00a0", " ")
    text = text.replace("–", "-").replace("—", "-").replace("−", "-")
    return re.sub(r"[ \t]+", " ", text)


def match_test(line):
    low = line.lower()

    for name, aliases in TESTS:
        for alias in aliases:
            match = re.search(alias, low, re.I)
            if match:
                return name, match.start(), match.end()

    return None


def number_value(text):
    try:
        return float(text.replace(",", ""))
    except (ValueError, AttributeError):
        return None


def parse_line_block(name, block):
    """
    Parse a test and its nearby text.
    Results are kept uncertain if the value or range is ambiguous.
    """
    block = normalize(block)

    found = match_test(block)
    if not found:
        return None

    _, start, end = found
    remainder = block[:start] + " " + block[end:]

    range_match = RANGE.search(remainder)
    reference = ""
    low = high = None

    if range_match:
        low = number_value(range_match.group(1))
        high = number_value(range_match.group(2))
        reference = range_match.group(0)

        remainder = (
            remainder[:range_match.start()]
            + " "
            + remainder[range_match.end():]
        )

    # Remove dates and common ID-like values from consideration.
    remainder = re.sub(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        " ",
        remainder
    )

    numbers = [
        number_value(m.group())
        for m in VALUE.finditer(remainder)
    ]

    numbers = [n for n in numbers if n is not None]

    # If no value remains after removing the reference range,
    # the result cannot be safely identified.
    if not numbers:
        return None

    result = numbers[0]

    # Avoid treating a range endpoint as the measured result.
    if low is not None and result in (low, high):
        return None

    unit_match = UNIT.search(block)
    unit = unit_match.group(0) if unit_match else ""

    if low is None or high is None:
        status = "Range not identified"
    elif low <= result <= high:
        status = "Within stated range"
    elif result < low:
        status = "Below stated range"
    else:
        status = "Above stated range"

    return {
        "Test": name,
        "Result": result,
        "Unit": unit,
        "Reference Range": reference,
        "Status": status,
    }


def analyze_report(report_text):
    if not report_text or not report_text.strip():
        return pd.DataFrame(columns=COLUMNS)

    lines = [
        line.strip()
        for line in normalize(report_text).splitlines()
        if line.strip()
    ]

    results = []
    seen = set()

    # First pass: test names and their nearby lines.
    for i, line in enumerate(lines):
        found = match_test(line)
        if not found:
            continue

        name, _, _ = found

        if name in seen:
            continue

        # Keep the block short to reduce accidental cross-matching.
        block = " ".join(lines[i:min(i + 4, len(lines))])
        parsed = parse_line_block(name, block)

        if parsed:
            results.append(parsed)
            seen.add(name)

    # Second pass: same-line entries such as "Glucose 92 mg/dL 70-100".
    for line in lines:
        found = match_test(line)
        if not found:
            continue

        name, _, _ = found

        if name in seen:
            continue

        parsed = parse_line_block(name, line)

        if parsed:
            results.append(parsed)
            seen.add(name)

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
            if value:
                fields[field] = value

    return fields
