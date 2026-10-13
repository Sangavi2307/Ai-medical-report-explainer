
import re
import pandas as pd


TEST_PATTERNS = [
    ("Hemoglobin", r"\b(?:haemoglobin|hemoglobin|hb)\b"),
    ("WBC", r"\b(?:wbc|total\s+leucocyte\s+count|white\s+blood\s+cells?)\b"),
    ("RBC", r"\b(?:rbc|red\s+blood\s+cells?)\b"),
    ("Platelets", r"\b(?:platelet\s+count|platelets?)\b"),
    ("Fasting glucose", r"\b(?:fasting\s+blood\s+sugar|fasting\s+glucose|fbs)\b"),
    ("Random glucose", r"\b(?:random\s+blood\s+sugar|random\s+glucose|rbs)\b"),
    ("HbA1c", r"\bhba1c\b"),
    ("Creatinine", r"\bcreatinine\b"),
    ("Urea", r"\burea\b"),
    ("Total cholesterol", r"\btotal\s+cholesterol\b"),
    ("Vitamin D", r"\b(?:25[- ]?oh\s+)?vitamin\s*d\b"),
    ("Vitamin B12", r"\bvitamin\s*b12\b"),
    ("TSH", r"\btsh\b"),
    ("ALT", r"\b(?:alt|sgpt)\b"),
    ("AST", r"\b(?:ast|sgot)\b"),
]

NUMBER = r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?"


def parse_range(line):
    match = re.search(
        rf"({NUMBER})\s*(?:-|–|to)\s*({NUMBER})",
        line,
        re.IGNORECASE
    )

    if not match:
        return None

    try:
        low = float(match.group(1).replace(",", ""))
        high = float(match.group(2).replace(",", ""))

        if low > high:
            return None

        return low, high

    except ValueError:
        return None


def parse_value(line, pattern):
    label_match = re.search(pattern, line, re.IGNORECASE)

    if not label_match:
        return None

    tail = line[label_match.end():]

    match = re.search(
        rf"^\s*[:=]?\s*({NUMBER})",
        tail
    )

    if not match:
        return None

    try:
        return float(match.group(1).replace(",", ""))

    except ValueError:
        return None


def display_number(value):
    if float(value).is_integer():
        return str(int(value))

    return f"{value:g}"


def analyze_report(text):
    rows = []
    seen = set()

    for line in text.splitlines():
        clean = re.sub(r"\s+", " ", line).strip()

        if not clean:
            continue

        for name, pattern in TEST_PATTERNS:
            if not re.search(pattern, clean, re.IGNORECASE):
                continue

            value = parse_value(clean, pattern)

            if value is None:
                continue

            key = (name, value, clean.lower())

            if key in seen:
                continue

            seen.add(key)
            reference_range = parse_range(clean)

            if reference_range:
                low, high = reference_range

                if value < low:
                    result_status = "Below range"
                elif value > high:
                    result_status = "Above range"
                else:
                    result_status = "Within range"

                reference_text = (
                    f"{display_number(low)} - {display_number(high)}"
                )

            else:
                result_status = "Not assessed"
                reference_text = "Not found on result line"

            rows.append({
                "Test": name,
                "Value": display_number(value),
                "Reference range": reference_text,
                "Status": result_status,
                "Source line": clean
            })

            break

    return pd.DataFrame(
        rows,
        columns=[
            "Test",
            "Value",
            "Reference range",
            "Status",
            "Source line"
        ]
    )
