
import re
import pandas as pd


TEST_NAMES = {
    "Hemoglobin": [r"\bhemoglobin\b", r"\bhaemoglobin\b", r"\bhb\b"],
    "WBC": [r"\bwbc\b", r"\bwhite blood cells?\b", r"\btotal leukocyte count\b"],
    "RBC": [r"\brbc\b", r"\bred blood cells?\b"],
    "Platelets": [r"\bplatelets?\b", r"\bplatelet count\b"],
    "Glucose": [r"\bglucose\b", r"\bblood sugar\b", r"\bfbs\b", r"\brbs\b"],
    "Creatinine": [r"\bcreatinine\b"],
    "Urea": [r"\burea\b", r"\bblood urea\b"],
    "Cholesterol": [r"\btotal cholesterol\b", r"\bcholesterol\b"],
    "Vitamin D": [r"\bvitamin\s*d\b"],
    "Vitamin B12": [r"\bvitamin\s*b12\b"],
    "TSH": [r"\btsh\b", r"\bthyroid stimulating hormone\b"],
    "ALT": [r"\balt\b", r"\bsgpt\b", r"\balanine aminotransferase\b"],
    "AST": [r"\bast\b", r"\bsgot\b", r"\baspartate aminotransferase\b"],
}


def analyze_report(text):
    columns = [
        "Test", "Result", "Unit", "Reference Range", "Status"
    ]

    if not isinstance(text, str) or not text.strip():
        return pd.DataFrame(columns=columns)

    rows = []
    seen = set()

    for line in text.splitlines():
        clean_line = re.sub(r"\s+", " ", line).strip()

        if not clean_line:
            continue

        # Find the test name
        matched_test = None

        for test_name, patterns in TEST_NAMES.items():
            if any(re.search(pattern, clean_line, re.IGNORECASE)
                   for pattern in patterns):
                matched_test = test_name
                break

        if not matched_test:
            continue

        # Extract numeric values, including decimals and commas
        numbers = re.findall(
            r"(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?",
            clean_line
        )

        if not numbers:
            continue

        # Use the first number after the test name as the result
        match = None
        for pattern in TEST_NAMES[matched_test]:
            match = re.search(pattern, clean_line, re.IGNORECASE)
            if match:
                break

        remainder = clean_line[match.end():] if match else clean_line
        result_match = re.search(
            r"[-+]?\d[\d,]*(?:\.\d+)?",
            remainder
        )

        if not result_match:
            continue

        result_text = result_match.group().replace(",", "")

        try:
            result_value = float(result_text)
        except ValueError:
            continue

        # Find a possible reference range on this same line
        range_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)",
            clean_line,
            re.IGNORECASE
        )

        reference_range = ""
        status = "Not assessed"

        if range_match:
            low = float(range_match.group(1))
            high = float(range_match.group(2))
            reference_range = f"{low:g} - {high:g}"

            if result_value < low:
                status = "Below range"
            elif result_value > high:
                status = "Above range"
            else:
                status = "Within range"

        # Capture possible unit text after the result
        unit_match = re.match(
            r"\s*([a-zA-Zµμ/%]+(?:/[a-zA-Zµμ]+)?)",
            remainder[result_match.end():]
        )
        unit = unit_match.group(1) if unit_match else ""

        key = (matched_test, result_text)
        if key in seen:
            continue
        seen.add(key)

        rows.append({
            "Test": matched_test,
            "Result": result_value,
            "Unit": unit,
            "Reference Range": reference_range,
            "Status": status
        })

    return pd.DataFrame(rows, columns=columns)
