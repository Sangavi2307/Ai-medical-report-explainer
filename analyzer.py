
import re
import pandas as pd

COLUMNS = ["Test", "Result", "Unit", "Reference Range", "Status"]

TEST_NAMES = [
    ("Fasting Blood Sugar", [
        "fasting blood sugar", "fasting glucose", "fbs"
    ]),
    ("Random Blood Sugar", ["random blood sugar", "random glucose", "rbs"]),
    ("Hemoglobin", ["hemoglobin", "haemoglobin", "hb"]),
    ("WBC Count", [
        "white blood cell count", "white blood cells", "wbc count", "wbc"
    ]),
    ("Platelets", ["platelet count", "platelets", "thrombocyte count"]),
    ("RBC Count", ["red blood cell count", "rbc count", "rbc"]),
    ("HbA1c", ["glycated hemoglobin", "hba1c"]),
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
    ("ALT", ["alanine aminotransferase", "sgpt", "alt"]),
    ("AST", ["aspartate aminotransferase", "sgot", "ast"]),
    ("TSH", ["thyroid stimulating hormone", "tsh"]),
    ("Vitamin D", ["25-oh vitamin d", "vitamin d"]),
    ("Vitamin B12", ["vitamin b12", "b12"]),
    ("ESR", ["erythrocyte sedimentation rate", "esr"]),
    ("CRP", ["c-reactive protein", "crp"]),
    ("Uric Acid", ["serum uric acid", "uric acid"]),
    ("Albumin", ["serum albumin", "albumin"]),
    ("Total Protein", ["total protein"]),
    ("MCV", ["mean corpuscular volume", "mcv"]),
    ("MCHC", ["mean corpuscular hemoglobin concentration", "mchc"]),
    ("MCH", ["mean corpuscular hemoglobin", "mch"]),
    ("Hematocrit", ["hematocrit", "packed cell volume", "pcv"]),
]

ALIASES = sorted(
    [
        (alias, name)
        for name, aliases in TEST_NAMES
        for alias in aliases
    ],
    key=lambda item: len(item[0]),
    reverse=True,
)


def normalize_text(text):
    text = str(text or "")
    text = text.replace("\u00a0", " ")
    text = text.replace("–", "-").replace("—", "-")
    text = text.replace("−", "-")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def find_test_name(text):
    for alias, name in ALIASES:
        pattern = (
            r"(?<![a-z])"
            + re.escape(alias)
            + r"(?![a-z])"
        )
        if re.search(pattern, text, re.IGNORECASE):
            return name
    return None


def parse_range(text):
    """
    Extract a numeric reference range.
    The caller must verify that the extracted range belongs
    to the identified test.
    """
    pattern = (
        r"(?<![\w.])"
        r"(\d[\d,]*(?:\.\d+)?)"
        r"\s*-\s*"
        r"(\d[\d,]*(?:\.\d+)?)"
        r"(?![\d.])"
    )

    match = re.search(pattern, text)

    if not match:
        return None

    low = float(match.group(1).replace(",", ""))
    high = float(match.group(2).replace(",", ""))

    if low > high:
        return None

    return low, high, match.group(0)


def extract_numbers(text):
    """
    Return numeric values with their positions.
    Values are not automatically assumed to be results.
    """
    pattern = r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)(?![\w.])"

    return [
        (
            float(match.group(1).replace(",", "")),
            match.start(),
            match.end(),
        )
        for match in re.finditer(pattern, text)
    ]


def extract_unit(text):
    patterns = [
        r"lakh\s*/?\s*[µuμ]l",
        r"million\s*/?\s*[µuμ]l",
        r"10\s*\^?\s*\d+\s*/?\s*[µuμ]l",
        r"mg\s*/\s*dl",
        r"g\s*/\s*dl",
        r"mmol\s*/\s*l",
        r"µmol\s*/\s*l",
        r"umol\s*/\s*l",
        r"ng\s*/\s*ml",
        r"pg\s*/\s*ml",
        r"miu\s*/\s*l",
        r"uiu\s*/\s*ml",
        r"iu\s*/\s*l",
        r"u\s*/\s*l",
        r"mm\s*/\s*hr",
        r"mm/hr",
        r"fl",
        r"pg",
        r"%",
        r"g/l",
        r"mg/l",
        r"meq/l",
        r"cells\s*/?\s*[µuμ]l",
        r"/\s*[µuμ]l",
        r"lakh",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return re.sub(r"\s+", "", match.group(0))

    return ""


def classify_status(result, reference_range, test_name):
    """
    Do not classify a result when its reference range is
    absent or implausible for the test.
    """
    if reference_range is None:
        return "Needs review"

    low, high, _ = reference_range

    # Broad sanity checks. These are not clinical reference ranges.
    # They only catch obvious parsing errors.
    sanity_limits = {
        "Hemoglobin": (1, 30),
        "Platelets": (1, 2000),
        "WBC Count": (0.1, 1000),
        "RBC Count": (0.1, 20),
        "Fasting Blood Sugar": (1, 2000),
        "Random Blood Sugar": (1, 2000),
        "HbA1c": (1, 30),
        "Creatinine": (0.01, 100),
        "Sodium": (50, 250),
        "Potassium": (1, 15),
    }

    limits = sanity_limits.get(test_name)

    if limits and not (
        limits[0] <= low <= high <= limits[1]
    ):
        return "Needs review"

    if result < low:
        return "Below range"

    if result > high:
        return "Above range"

    return "Within range"


def analyze_report(report_text):
    if not report_text or not str(report_text).strip():
        return pd.DataFrame(columns=COLUMNS)

    lines = [
        normalize_text(line)
        for line in str(report_text).splitlines()
        if normalize_text(line)
    ]

    results = []
    seen = set()

    # Each recognized test is processed independently.
    for index, line in enumerate(lines):
        test_name = find_test_name(line)

        if not test_name:
            continue

        # Prefer a result and reference range on the same line.
        # Allow the next line only when it does not start another test.
        block_lines = [line]

        if index + 1 < len(lines):
            next_line = lines[index + 1]
            next_test = find_test_name(next_line)

            if not next_test:
                block_lines.append(next_line)

        block = " ".join(block_lines)

        # Remove the test name from the beginning so numbers
        # in names or nearby headings are less likely to be selected.
        alias_used = None

        for alias, canonical in ALIASES:
            if canonical != test_name:
                continue

            match = re.search(
                r"(?<![a-z])" + re.escape(alias) + r"(?![a-z])",
                line,
                re.IGNORECASE,
            )

            if match:
                alias_used = match
                break

        remainder = (
            line[alias_used.end():]
            if alias_used
            else line
        )

        # Use the same-line remainder first.
        # If no result is found, try the additional line.
        number_matches = extract_numbers(remainder)

        if not number_matches and len(block_lines) > 1:
            remainder = " ".join(block_lines)
            number_matches = extract_numbers(remainder)

        if not number_matches:
            continue

        range_info = parse_range(remainder)

        # A numeric range normally contains two numbers.
        # If a range is found, do not assume its first number
        # is the measured result.
        if range_info:
            range_low, range_high, range_text = range_info

            range_match = re.search(
                r"(?<![\w.])"
                + re.escape(str(range_low))
                + r"\s*-\s*"
                + re.escape(str(range_high))
                + r"(?![\d.])",
                remainder,
            )

            # Locate the first numeric value before the range.
            before_range = (
                remainder[:range_match.start()]
                if range_match
                else remainder
            )

            before_numbers = extract_numbers(before_range)

            if not before_numbers:
                # Some reports put the result after the range.
                after_range = (
                    remainder[range_match.end():]
                    if range_match
                    else ""
                )
                after_numbers = extract_numbers(after_range)

                if not after_numbers:
                    result_value = None
                else:
                    result_value = after_numbers[0][0]
            else:
                result_value = before_numbers[0][0]

            reference_range = range_info
        else:
            result_value = number_matches[0][0]
            range_text = ""
            reference_range = None

        if result_value is None:
            continue

        # If the range was not found, the result cannot be
        # confidently classified.
        unit = extract_unit(remainder)

        status = classify_status(
            result_value,
            reference_range,
            test_name,
        )

        # Do not silently discard duplicate values from different
        # sections, but avoid exact repeated OCR rows.
        key = (test_name, result_value, unit, range_text)

        if key in seen:
            continue

        seen.add(key)

        results.append({
            "Test": test_name,
            "Result": result_value,
            "Unit": unit,
            "Reference Range": range_text,
            "Status": status,
        })

    return pd.DataFrame(results, columns=COLUMNS)


def extract_patient_fields(report_text):
    text = normalize_text(report_text)
    fields = {}

    patterns = {
        "Patient Name": (
            r"Patient Name\s*[:\n]+\s*([^\n]+)"
        ),
        "Age / Gender": (
            r"Age\s*/\s*Gender\s*[:\n]+\s*([^\n]+)"
        ),
        "Patient ID": (
            r"Patient ID\s*[:\n]+\s*([^\n]+)"
        ),
        "Date of Visit": (
            r"Date of Visit\s*[:\n]+\s*([^\n]+)"
        ),
        "Consulting Doctor": (
            r"Consulting Doctor\s*[:\n]+\s*([^\n]+)"
        ),
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            continue

        value = match.group(1).strip()

        if value and value.lower() not in {
            "laboratory results",
            "clinical details",
        }:
            fields[key] = value

    return fields
