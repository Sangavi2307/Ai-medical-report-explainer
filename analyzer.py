
import re
import pandas as pd


# Common laboratory test names and their usual units.
# These are matching hints, not universal reference ranges.
TESTS = {
    "Hemoglobin": {
        "names": [r"hemoglobin", r"\bhgb\b", r"\bhb\b"],
        "unit": r"(?:g\s*/\s*d[lL]|g\s*/\s*[lL])"
    },
    "WBC": {
        "names": [
            r"white blood cell(?: count)?",
            r"\bwbc\b",
            r"total leukocyte count",
            r"\bt lc\b"
        ],
        "unit": r"(?:cells?\s*/\s*(?:cu\.?\s*mm|mm3|µ[lL]|u[lL])|10\^?3\s*/\s*µ[lL])"
    },
    "Platelets": {
        "names": [r"platelet(?: count)?", r"\bplt\b"],
        "unit": r"(?:lakhs?\s*/\s*µ[lL]|10\^?3\s*/\s*µ[lL]|cells?\s*/\s*µ[lL])"
    },
    "Fasting Glucose": {
        "names": [
            r"fasting blood sugar",
            r"fasting glucose",
            r"\bfbs\b"
        ],
        "unit": r"(?:mg\s*/\s*d[lL]|mmol\s*/\s*[lL])"
    },
    "Random Glucose": {
        "names": [
            r"random blood sugar",
            r"random glucose",
            r"\brbs\b"
        ],
        "unit": r"(?:mg\s*/\s*d[lL]|mmol\s*/\s*[lL])"
    },
    "Creatinine": {
        "names": [r"\bcreatinine\b"],
        "unit": r"(?:mg\s*/\s*d[lL]|µmol\s*/\s*[lL]|umol\s*/\s*[lL])"
    },
    "Total Cholesterol": {
        "names": [r"total cholesterol", r"\bcholesterol\b"],
        "unit": r"(?:mg\s*/\s*d[lL]|mmol\s*/\s*[lL])"
    },
    "Triglycerides": {
        "names": [r"\btriglycerides?\b", r"\btg\b"],
        "unit": r"(?:mg\s*/\s*d[lL]|mmol\s*/\s*[lL])"
    },
    "TSH": {
        "names": [
            r"thyroid stimulating hormone",
            r"\btsh\b"
        ],
        "unit": r"(?:µ[iuIU]?\s*/\s*[lL]|miu\s*/\s*[lL])"
    },
    "HbA1c": {
        "names": [
            r"\bhba1c\b",
            r"glycated hemoglobin"
        ],
        "unit": r"(?:%|mmol\s*/\s*mol)"
    }
}


def extract_patient_fields(report_text):
    """Extract basic patient fields when explicitly present in the text."""
    fields = {
        "Patient Name": None,
        "Age": None,
        "Gender": None,
        "Report Date": None
    }

    if not report_text:
        return fields

    patterns = {
        "Patient Name": [
            r"(?im)^\s*(?:patient\s*name|name)\s*[:\-]\s*([^\n\r]+)"
        ],
        "Age": [
            r"(?im)^\s*age\s*[:\-]\s*(\d{1,3}\s*(?:years?|yrs?)?)"
        ],
        "Gender": [
            r"(?im)^\s*(?:gender|sex)\s*[:\-]\s*(male|female|other)"
        ],
        "Report Date": [
            r"(?im)^\s*(?:report\s*date|collection\s*date|date)\s*[:\-]\s*([^\n\r]+)"
        ]
    }

    for field, regexes in patterns.items():
        for pattern in regexes:
            match = re.search(pattern, report_text)
            if match:
                fields[field] = match.group(1).strip()
                break

    return fields


def _parse_number(value):
    """Convert a numeric string into a float."""
    try:
        return float(value.replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


def analyze_report(report_text):
    """
    Extract test values with nearby units and reference ranges.

    A result is flagged only when a reference range is explicitly
    detected near that test. It does not diagnose medical conditions.
    """
    rows = []

    if not report_text or not report_text.strip():
        return pd.DataFrame(
            columns=[
                "Test", "Result", "Unit",
                "Reference Range", "Status"
            ]
        )

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in report_text.splitlines()
        if line.strip()
    ]

    for test_name, config in TESTS.items():
        matched = False

        for index, line in enumerate(lines):
            if not any(
                re.search(name, line, re.IGNORECASE)
                for name in config["names"]
            ):
                continue

            # Look at this line and the next two lines only.
            # This reduces accidental matches from unrelated sections.
            context = " | ".join(lines[index:index + 3])

            # Find a numeric result near the test name.
            result_match = re.search(
                r"(?:"
                + "|".join(config["names"])
                + r")\s*[:=\-]?\s*"
                r"([<>≤≥]?\s*-?\d[\d,]*(?:\.\d+)?)",
                context,
                re.IGNORECASE
            )

            if not result_match:
                # Some reports put the result before the test name.
                result_match = re.search(
                    r"([<>≤≥]?\s*-?\d[\d,]*(?:\.\d+)?)"
                    r"\s*(?:"
                    + "|".join(config["names"])
                    + r")",
                    context,
                    re.IGNORECASE
                )

            if not result_match:
                continue

            raw_result = result_match.group(1).strip()
            numeric_result = _parse_number(
                re.sub(r"^[<>≤≥]\s*", "", raw_result)
            )

            # Extract a nearby unit when present.
            unit_match = re.search(
                config["unit"],
                context,
                re.IGNORECASE
            )
            unit = unit_match.group(0) if unit_match else ""

            # Extract an explicit range such as 12.0 - 16.0.
            range_match = re.search(
                r"(?:reference(?:\s*range)?|normal\s*range|range)"
                r"\s*[:\-]?\s*"
                r"(\d[\d,]*(?:\.\d+)?\s*[-–to]+\s*"
                r"\d[\d,]*(?:\.\d+)?)",
                context,
                re.IGNORECASE
            )

            if not range_match:
                range_match = re.search(
                    r"\b(\d[\d,]*(?:\.\d+)?\s*[-–]\s*"
                    r"\d[\d,]*(?:\.\d+)?)\b",
                    context
                )

            reference_range = (
                range_match.group(1).strip()
                if range_match else ""
            )

            status = "Range not detected"

            if reference_range and numeric_result is not None:
                range_numbers = re.findall(
                    r"\d[\d,]*(?:\.\d+)?",
                    reference_range
                )

                if len(range_numbers) >= 2:
                    low = _parse_number(range_numbers[0])
                    high = _parse_number(range_numbers[1])

                    if low is not None and high is not None:
                        if numeric_result < low:
                            status = "Below detected range"
                        elif numeric_result > high:
                            status = "Above detected range"
                        else:
                            status = "Within detected range"

            rows.append({
                "Test": test_name,
                "Result": raw_result,
                "Unit": unit,
                "Reference Range": reference_range,
                "Status": status
            })

            matched = True
            break

        # Do not add fake or assumed results when a test is missing.
        if not matched:
            continue

    return pd.DataFrame(
        rows,
        columns=[
            "Test", "Result", "Unit",
            "Reference Range", "Status"
        ]
    )
