
import re
import pandas as pd


def extract_report_details(report_text):
    """Extract general information from a medical report."""

    text = report_text or ""

    sections = {
        "Patient Details": [],
        "Medical History": [],
        "Vital Signs": [],
        "Doctor's Observations": [],
        "Medications and Advice": [],
        "Other Information": [],
    }

    section_patterns = {
        "Patient Details": [
            "patient details", "patient information",
            "personal details"
        ],
        "Medical History": [
            "medical history", "past medical history",
            "allergies", "surgeries"
        ],
        "Vital Signs": [
            "vitals", "vital signs"
        ],
        "Doctor's Observations": [
            "doctor's observations", "clinical findings",
            "examination", "assessment"
        ],
        "Medications and Advice": [
            "medications", "medicines", "treatment",
            "advice", "recommendations", "next steps",
            "plan"
        ],
    }

    current_section = "Other Information"

    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()

        if not line:
            continue

        normalized = line.lower().strip(" :.-")

        matched_section = None

        for section, headings in section_patterns.items():
            if normalized in headings:
                matched_section = section
                break

        if matched_section:
            current_section = matched_section
            continue

        sections[current_section].append(line)

    details = {}

    for section, lines in sections.items():
        details[section] = "\n".join(lines).strip()

    return details


def analyze_report(report_text):
    """Extract laboratory results when recognizable test names exist."""

    columns = [
        "Test", "Result", "Unit", "Reference Range", "Status"
    ]

    if not isinstance(report_text, str) or not report_text.strip():
        return pd.DataFrame(columns=columns)

    tests = {
        "Hemoglobin": r"\b(?:hemoglobin|haemoglobin|hb)\b",
        "WBC Count": r"\b(?:wbc(?:\s+count)?|white blood cell count|total leukocyte count|tlc)\b",
        "Platelets": r"\b(?:platelets?|platelet count|plt)\b",
        "Fasting Blood Sugar": r"\b(?:fasting blood sugar|fasting glucose|fbs)\b",
        "Random Blood Sugar": r"\b(?:random blood sugar|random glucose|rbs)\b",
        "HbA1c": r"\b(?:hba1c|glycated hemoglobin)\b",
        "RBC Count": r"\b(?:rbc(?:\s+count)?|red blood cell count)\b",
        "Creatinine": r"\b(?:serum creatinine|creatinine)\b",
        "Total Cholesterol": r"\b(?:total cholesterol|cholesterol)\b",
        "Urea": r"\b(?:blood urea|serum urea|urea)\b",
        "TSH": r"\b(?:thyroid stimulating hormone|tsh)\b",
        "Vitamin D": r"\b(?:25[- ]?oh vitamin d|vitamin d)\b",
        "Vitamin B12": r"\b(?:vitamin b12|cobalamin)\b",
    }

    number = r"[-+]?\d[\d,]*(?:\.\d+)?"
    range_pattern = re.compile(
        rf"({number})\s*(?:-|–|—|\bto\b)\s*({number})",
        re.IGNORECASE,
    )

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in report_text.replace("\u00a0", " ").splitlines()
        if line.strip()
    ]

    results = []
    seen = set()

    for i, line in enumerate(lines):
        for test_name, pattern in tests.items():
            match = re.search(pattern, line, re.IGNORECASE)

            if not match:
                continue

            # Look at nearby lines for the result and reference range.
            block = [line] + lines[i + 1:i + 4]
            block_text = " ".join(block)

            range_match = range_pattern.search(block_text)
            low = high = None
            reference = "Not provided"

            if range_match:
                try:
                    low = float(range_match.group(1).replace(",", ""))
                    high = float(range_match.group(2).replace(",", ""))
                    if low <= high:
                        reference = f"{low:g} - {high:g}"
                    else:
                        low = high = None
                except ValueError:
                    low = high = None

            value = None
            unit = ""

            # Search after the test name first.
            remainder = line[match.end():]
            value_match = re.search(number, remainder)

            if value_match:
                value = float(value_match.group().replace(",", ""))
                unit = remainder[value_match.end():].strip()

            # Otherwise look on the following lines.
            if value is None:
                for candidate_line in block[1:]:
                    if range_pattern.search(candidate_line):
                        continue

                    candidate = re.search(number, candidate_line)

                    if candidate:
                        value = float(candidate.group().replace(",", ""))
                        unit = candidate_line[candidate.end():].strip()
                        break

            if value is None:
                continue

            if low is None or high is None:
                status = "Needs review"
            elif value < low:
                status = "Below range"
            elif value > high:
                status = "Above range"
            else:
                status = "Within range"

            key = (test_name, value)

            if key not in seen:
                seen.add(key)
                results.append({
                    "Test": test_name,
                    "Result": value,
                    "Unit": unit,
                    "Reference Range": reference,
                    "Status": status,
                })

            break

    return pd.DataFrame(results, columns=columns)
