import re
import pandas as pd


# Common laboratory test names and their variations.
TESTS = {
    "Hemoglobin": [r"hemoglobin", r"\bha\b", r"\bhb\b"],
    "WBC": [r"white blood cells?", r"\bwbc\b", r"total leukocyte count"],
    "RBC": [r"red blood cells?", r"\brbc\b", r"erythrocyte count"],
    "Platelets": [r"platelet count", r"\bplatelets?\b"],
    "Hematocrit": [r"hematocrit", r"\bhct\b", r"\bpcv\b"],
    "MCV": [r"\bmcv\b", r"mean corpuscular volume"],
    "MCH": [r"\bmch\b", r"mean corpuscular hemoglobin"],
    "MCHC": [r"\bmchc\b"],
    "Neutrophils": [r"neutrophils?"],
    "Lymphocytes": [r"lymphocytes?"],
    "Eosinophils": [r"eosinophils?"],
    "Monocytes": [r"monocytes?"],
    "Fasting Blood Sugar": [
        r"fasting blood sugar", r"fasting glucose", r"\bfbs\b"
    ],
    "Random Blood Sugar": [
        r"random blood sugar", r"random glucose", r"\brbs\b"
    ],
    "HbA1c": [r"\bhba1c\b", r"glycated hemoglobin"],
    "Creatinine": [r"serum creatinine", r"\bcreatinine\b"],
    "Blood Urea": [r"blood urea", r"\burea\b"],
    "BUN": [r"\bbun\b", r"blood urea nitrogen"],
    "Total Cholesterol": [r"total cholesterol", r"\bcholesterol\b"],
    "HDL Cholesterol": [r"\bhdl\b"],
    "LDL Cholesterol": [r"\bldl\b"],
    "Triglycerides": [r"triglycerides?"],
    "Bilirubin": [r"total bilirubin", r"\bbilirubin\b"],
    "AST/SGOT": [r"\bast\b", r"\bsgot\b"],
    "ALT/SGPT": [r"\balt\b", r"\bsgpt\b"],
    "Alkaline Phosphatase": [r"alkaline phosphatase", r"\balp\b"],
    "TSH": [r"\btsh\b", r"thyroid stimulating hormone"],
    "T3": [r"\bt3\b", r"triiodothyronine"],
    "T4": [r"\bt4\b", r"thyroxine"],
    "Vitamin D": [r"vitamin d", r"25-oh vitamin d"],
    "Vitamin B12": [r"vitamin b12", r"cobalamin"],
    "Calcium": [r"\bcalcium\b"],
    "Sodium": [r"\bsodium\b"],
    "Potassium": [r"\bpotassium\b"],
    "Chloride": [r"\bchloride\b"],
    "Uric Acid": [r"uric acid"],
    "Albumin": [r"\balbumin\b"],
    "Total Protein": [r"total protein"],
    "CRP": [r"\bcrp\b", r"c-reactive protein"],
    "ESR": [r"\besr\b", r"erythrocyte sedimentation rate"],
    "Urine Protein": [r"urine protein"],
}


def _clean_number(value):
    """Convert a recognized numeric string to a number."""
    try:
        return float(value.replace(",", ""))
    except (ValueError, AttributeError):
        return None


def _parse_range(text):
    """
    Recognize reference ranges such as:
    4.0 - 10.0, 4.0–10.0, or 4.0 to 10.0.
    """
    match = re.search(
        r"(\d[\d,]*(?:\.\d+)?)\s*(?:-|–|—|\bto\b)\s*"
        r"(\d[\d,]*(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )

    if not match:
        return None, None

    low = _clean_number(match.group(1))
    high = _clean_number(match.group(2))

    if low is None or high is None or low > high:
        return None, None

    return low, high


def _find_test(line):
    """Return the matching test name without matching inside other words."""
    for test_name, patterns in TESTS.items():
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return test_name
    return None


def _parse_result(line, test_name):
    """
    Extract a result from a line.
    Supports formats such as:
    Hemoglobin: 13.5 g/dL
    WBC 7,500 /uL
    Glucose | 95 | mg/dL | 70-100
    """
    patterns = [
        r"[:=]\s*(-?\d[\d,]*(?:\.\d+)?)",
        r"\s(-?\d[\d,]*(?:\.\d+)?)\s*(?:mg|g|mmol|umol|µmol|"
        r"u/l|iu|%|fl|pg|cells|/|x|10|\bmm|bpm|°|"
        r"million|lakhs?)",
        r"\s(-?\d[\d,]*(?:\.\d+)?)\s*$",
    ]

    for pattern in patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            value = _clean_number(match.group(1))
            if value is not None:
                return value

    return None


def analyze_report(report_text):
    """
    Analyze common laboratory results from extracted report text.

    Status is determined only when an explicit reference range is
    available on the same line. It does not diagnose conditions.
    """
    columns = [
        "Test",
        "Result",
        "Unit",
        "Reference Range",
        "Status",
        "Source Line",
    ]

    if not report_text or not report_text.strip():
        return pd.DataFrame(columns=columns)

    lines = [
        line.strip()
        for line in report_text.splitlines()
        if line.strip()
    ]

    results = []
    seen = set()

    for index, line in enumerate(lines):
        test_name = _find_test(line)

        if not test_name:
            continue

        # Prevent a broad match such as "HDL" inside "HDL Cholesterol"
        # from producing duplicate test rows.
        key = (test_name, index)
        if key in seen:
            continue

        value = _parse_result(line, test_name)

        # If a test name and value are separated by a line break,
        # inspect the next line only when it begins with a number.
        result_line = line
        if value is None and index + 1 < len(lines):
            next_line = lines[index + 1]
            if re.match(r"^\s*-?\d[\d,]*(?:\.\d+)?\b", next_line):
                value = _parse_result(next_line, test_name)
                if value is not None:
                    result_line = line + " " + next_line

        if value is None:
            continue

        low, high = _parse_range(result_line)

        range_text = ""
        status = "Reference range not found"

        if low is not None and high is not None:
            range_text = f"{low:g} - {high:g}"

            if value < low:
                status = "Below supplied range"
            elif value > high:
                status = "Above supplied range"
            else:
                status = "Within supplied range"

        # Extract a likely unit, if available.
        unit_match = re.search(
            r"\b(mg/dL|g/dL|g/L|mmol/L|umol/L|µmol/L|"
            r"mIU/L|uIU/mL|IU/L|U/L|cells/uL|cells/µL|"
            r"10\^?\d*/uL|%|fL|pg/mL|pg|ng/mL|ng/dL|"
            r"mL/min|mmHg|bpm|/min)\b",
            result_line,
            re.IGNORECASE,
        )
        unit = unit_match.group(0) if unit_match else ""

        results.append({
            "Test": test_name,
            "Result": value,
            "Unit": unit,
            "Reference Range": range_text,
            "Status": status,
            "Source Line": result_line,
        })

        seen.add(key)

    # Remove duplicate test/result combinations.
    unique_results = []
    unique_keys = set()

    for row in results:
        key = (row["Test"], row["Result"], row["Source Line"])
        if key not in unique_keys:
            unique_results.append(row)
            unique_keys.add(key)

    return pd.DataFrame(unique_results, columns=columns)
