
import re
import pandas as pd

COLUMNS = ["Test", "Result", "Unit", "Reference Range", "Status"]

TEST_NAMES = [
    ("Fasting Blood Sugar", ["fasting blood sugar", "fasting glucose", "fbs"]),
    ("Hemoglobin", ["hemoglobin", "haemoglobin", "hb"]),
    ("WBC Count", ["wbc count", "white blood cell count", "white blood cells", "wbc"]),
    ("Platelets", ["platelet count", "platelets", "thrombocyte count"]),
    ("RBC Count", ["rbc count", "red blood cell count", "rbc"]),
    ("Random Blood Sugar", ["random blood sugar", "rbs"]),
    ("HbA1c", ["hba1c", "glycated hemoglobin"]),
    ("Creatinine", ["serum creatinine", "creatinine"]),
    ("Urea", ["blood urea", "serum urea", "urea"]),
    ("Total Cholesterol", ["total cholesterol", "cholesterol"]),
    ("LDL Cholesterol", ["ldl cholesterol", "ldl"]),
    ("HDL Cholesterol", ["hdl cholesterol", "hdl"]),
    ("Triglycerides", ["triglycerides", "triglyceride"]),
    ("Sodium", ["serum sodium", "sodium"]),
    ("Potassium", ["serum potassium", "potassium"]),
    ("Calcium", ["serum calcium", "calcium"]),
    ("Bilirubin", ["total bilirubin", "bilirubin"]),
    ("ALT", ["sgpt", "alanine aminotransferase", "alt"]),
    ("AST", ["sgot", "aspartate aminotransferase", "ast"]),
    ("TSH", ["thyroid stimulating hormone", "tsh"]),
    ("Vitamin D", ["25-oh vitamin d", "vitamin d"]),
    ("Vitamin B12", ["vitamin b12", "b12"]),
    ("ESR", ["erythrocyte sedimentation rate", "esr"]),
    ("CRP", ["c-reactive protein", "crp"]),
    ("Uric Acid", ["serum uric acid", "uric acid"]),
    ("Albumin", ["serum albumin", "albumin"]),
    ("Total Protein", ["total protein"]),
    ("MCV", ["mean corpuscular volume", "mcv"]),
    ("MCH", ["mean corpuscular hemoglobin", "mch"]),
    ("MCHC", ["mean corpuscular hemoglobin concentration", "mchc"]),
    ("Hematocrit", ["hematocrit", "packed cell volume", "pcv"]),
]

# Longest aliases first to avoid matching "cholesterol" inside "LDL cholesterol".
ALIASES = sorted(
    [(alias, name) for name, aliases in TEST_NAMES for alias in aliases],
    key=lambda item: len(item[0]),
    reverse=True
)


def find_test_name(text):
    text_lower = text.lower()

    for alias, canonical_name in ALIASES:
        pattern = r"(?<![a-z])" + re.escape(alias) + r"(?![a-z])"
        if re.search(pattern, text_lower):
            return canonical_name

    return None


def normalize_text(text):
    text = text.replace("\u00a0", " ")
    text = text.replace("–", "-").replace("—", "-")
    return re.sub(r"[ \t]+", " ", text).strip()


def parse_range(text):
    """
    Recognizes examples:
    12-16 g/dL
    4,000-11,000 /uL
    70-100 mg/dL
    1.5-4.5 lakh/uL
    """
    match = re.search(
        r"(-?\d[\d,]*(?:\.\d+)?)\s*-\s*"
        r"(-?\d[\d,]*(?:\.\d+)?)\s*"
        r"(lakh\s*/?\s*[µuμ]l|"
        r"10\^?\d+\s*/?\s*[µuμ]l|"
        r"/?\s*[µuμ]l|"
        r"mg\s*/\s*dl|"
        r"g\s*/\s*dl|"
        r"mmol\s*/\s*l|"
        r"iu\s*/\s*l|"
        r"u\s*/\s*l|"
        r"%)?",
        text,
        flags=re.IGNORECASE
    )

    if not match:
        return None

    low = float(match.group(1).replace(",", ""))
    high = float(match.group(2).replace(",", ""))
    full_range = match.group(0).strip()

    return low, high, full_range


def extract_result_and_unit(text):
    """
    Recognizes a numeric result and optional unit.
    Examples: 13.2 g/dL, 7,800 /uL, 2.45 lakh/uL, 92 mg/dL.
    """
    match = re.search(
        r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)\s*"
        r"(lakh\s*/?\s*[µuμ]l|"
        r"mg\s*/\s*dl|"
        r"g\s*/\s*dl|"
        r"mmol\s*/\s*l|"
        r"10\^?\d+\s*/?\s*[µuμ]l|"
        r"/\s*[µuμ]l|"
        r"[µuμ]l|"
        r"iu\s*/\s*l|"
        r"u\s*/\s*l|"
        r"%)?",
        text,
        flags=re.IGNORECASE
    )

    if not match:
        return None

    number = float(match.group(1).replace(",", ""))
    unit = (match.group(2) or "").strip()

    return number, unit, match.start(), match.end()


def classify_status(result, reference_range, test_name):
    if not reference_range:
        return "Needs review"

    low, high, _ = reference_range

    # The supplied example reports platelets in lakh/uL.
    # Convert the reference values only if result and range use the same scale.
    if result < low:
        return "Below range"
    if result > high:
        return "Above range"
    return "Within range"


def analyze_report(report_text):
    if not report_text or not report_text.strip():
        return pd.DataFrame(columns=COLUMNS)

    lines = [
        normalize_text(line)
        for line in report_text.splitlines()
        if normalize_text(line)
    ]

    results = []
    i = 0

    while i < len(lines):
        line = lines[i]
        test_name = find_test_name(line)

        if not test_name:
            i += 1
            continue

        # Collect this line and the next few lines because reports may
        # place test, result, and reference range on separate lines.
        collected = [line]
        j = i + 1

        while j < len(lines) and j <= i + 4:
            if find_test_name(lines[j]):
                break

            # Stop at common report section headings.
            if re.match(
                r"^(assessment|advice|clinical details|patient information|"
                r"patient name|age / gender|laboratory results)\b",
                lines[j],
                re.IGNORECASE
            ):
                break

            collected.append(lines[j])
            j += 1

        block = " ".join(collected)

        # Search only the text after the recognized test name.
        alias_match = None
        for alias, canonical_name in ALIASES:
            if canonical_name == test_name:
                pattern = r"(?<![a-z])" + re.escape(alias) + r"(?![a-z])"
                alias_match = re.search(pattern, block, re.IGNORECASE)
                if alias_match:
                    break

        remainder = block[alias_match.end():] if alias_match else block

        result_match = extract_result_and_unit(remainder)
        range_info = parse_range(remainder)

        if result_match:
            result, unit, _, result_end = result_match

            # Find the reference range after the result where possible.
            after_result = remainder[result_end:]
            range_info = parse_range(after_result) or range_info

            if range_info:
                reference_text = range_info[2]
                status = classify_status(result, range_info, test_name)
            else:
                reference_text = ""
                status = "Needs review"

            results.append({
                "Test": test_name,
                "Result": result,
                "Unit": unit,
                "Reference Range": reference_text,
                "Status": status
            })

        i += 1

    # Avoid duplicate rows caused by repeated OCR lines.
    unique = []
    seen = set()

    for row in results:
        key = (row["Test"], row["Result"], row["Unit"])
        if key not in seen:
            unique.append(row)
            seen.add(key)

    return pd.DataFrame(unique, columns=COLUMNS)


def extract_patient_fields(report_text):
    text = report_text or ""
    fields = {}

    patterns = {
        "Patient Name": r"Patient Name\s*[:\n]+\s*([^\n]+)",
        "Age / Gender": r"Age\s*/\s*Gender\s*[:\n]+\s*([^\n]+)",
        "Patient ID": r"Patient ID\s*[:\n]+\s*([^\n]+)",
        "Date of Visit": r"Date of Visit\s*[:\n]+\s*([^\n]+)",
        "Consulting Doctor": r"Consulting Doctor\s*[:\n]+\s*([^\n]+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if value and value.lower() not in {"laboratory results", "clinical details"}:
                fields[key] = value

    return fields
