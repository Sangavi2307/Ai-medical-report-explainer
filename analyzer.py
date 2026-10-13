
import re
import pandas as pd


TESTS = {
    "Hemoglobin": [
        r"\bhemoglobin\b", r"\bhaemoglobin\b", r"\bhb\b"
    ],
    "WBC Count": [
        r"\bwbc(?:\s+count)?\b",
        r"\bwhite blood cell count\b",
        r"\bwhite blood cells?\b",
        r"\btotal leukocyte count\b",
        r"\btlc\b",
    ],
    "Platelets": [
        r"\bplatelet count\b", r"\bplatelets?\b", r"\bplt\b"
    ],
    "Fasting Blood Sugar": [
        r"\bfasting blood sugar\b",
        r"\bfasting glucose\b",
        r"\bfbs\b",
    ],
    "Random Blood Sugar": [
        r"\brandom blood sugar\b", r"\brandom glucose\b", r"\brbs\b"
    ],
    "HbA1c": [
        r"\bhba1c\b", r"\bglycated hemoglobin\b"
    ],
    "RBC Count": [
        r"\brbc(?:\s+count)?\b", r"\bred blood cell count\b"
    ],
    "Creatinine": [
        r"\bserum creatinine\b", r"\bcreatinine\b"
    ],
    "Total Cholesterol": [
        r"\btotal cholesterol\b", r"\bcholesterol\b"
    ],
    "Urea": [
        r"\bblood urea\b", r"\bserum urea\b", r"\burea\b"
    ],
    "TSH": [
        r"\bthyroid stimulating hormone\b", r"\btsh\b"
    ],
    "Vitamin D": [
        r"\b25[- ]?oh vitamin d\b", r"\bvitamin d\b"
    ],
    "Vitamin B12": [
        r"\bvitamin b12\b", r"\bcobalamin\b"
    ],
}

NUMBER = r"[-+]?\d[\d,]*(?:\.\d+)?"

RANGE_PATTERN = re.compile(
    rf"({NUMBER})\s*(?:-|–|—|\bto\b)\s*({NUMBER})",
    re.IGNORECASE,
)

UNIT_PATTERN = re.compile(
    r"(?:g/dL|g/L|mg/dL|mmol/L|mIU/L|IU/L|U/L|"
    r"cells?/µL|cells?/uL|/µL|/uL|lakh/µL|lakh/uL|"
    r"million/µL|ng/mL|pg/mL|%)",
    re.IGNORECASE,
)


def number_value(value):
    try:
        return float(value.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def normalize_lines(text):
    text = text.replace("\u00a0", " ")
    text = text.replace("−", "-")
    return [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]


def analyze_report(report_text):
    columns = [
        "Test", "Result", "Unit", "Reference Range", "Status"
    ]

    if not isinstance(report_text, str) or not report_text.strip():
        return pd.DataFrame(columns=columns)

    lines = normalize_lines(report_text)
    results = []
    seen = set()

    for i, line in enumerate(lines):
        matched_test = None

        for test_name, patterns in TESTS.items():
            if any(
                re.search(pattern, line, re.IGNORECASE)
                for pattern in patterns
            ):
                matched_test = test_name
                break

        if not matched_test:
            continue

        # Collect this line and the next few lines.
        # Stop if another recognized test name begins.
        block = [line]
        for next_line in lines[i + 1:i + 4]:
            is_next_test = any(
                re.search(pattern, next_line, re.IGNORECASE)
                for patterns in TESTS.values()
                for pattern in patterns
            )
            if is_next_test:
                break
            block.append(next_line)

        block_text = " ".join(block)

        # Find the reference range before extracting the result.
        range_match = RANGE_PATTERN.search(block_text)
        low = high = None
        reference = "Not provided"

        if range_match:
            low = number_value(range_match.group(1))
            high = number_value(range_match.group(2))

            if low is not None and high is not None and low <= high:
                reference = f"{low:g} - {high:g}"

        # Prefer a number on the test-name line.
        test_line = line
        test_match = None

        for pattern in TESTS[matched_test]:
            test_match = re.search(pattern, test_line, re.IGNORECASE)
            if test_match:
                break

        value = None
        unit = ""

        # Check the text after the test name first.
        if test_match:
            remainder = test_line[test_match.end():]
            remainder = re.sub(r"^\s*[:=|]\s*", " ", remainder)
            candidate = re.search(NUMBER, remainder)

            if candidate:
                value = number_value(candidate.group())

                unit_match = UNIT_PATTERN.search(remainder)
                if unit_match:
                    unit = unit_match.group()

        # Otherwise search the following lines for the result.
        # Do not accidentally use a reference-range endpoint.
        if value is None:
            for candidate_line in block[1:]:
                if RANGE_PATTERN.search(candidate_line):
                    continue

                candidate = re.search(NUMBER, candidate_line)
                if candidate:
                    value = number_value(candidate.group())

                    unit_match = UNIT_PATTERN.search(candidate_line)
                    if unit_match:
                        unit = unit_match.group()

                    break

        if value is None:
            continue

        if low is not None and high is not None:
            if value < low:
                status = "Below range"
            elif value > high:
                status = "Above range"
            else:
                status = "Within range"
        else:
            status = "Needs reference range"

        key = (matched_test, value)
        if key in seen:
            continue
        seen.add(key)

        results.append({
            "Test": matched_test,
            "Result": value,
            "Unit": unit,
            "Reference Range": reference,
            "Status": status,
        })

    return pd.DataFrame(results, columns=columns)
