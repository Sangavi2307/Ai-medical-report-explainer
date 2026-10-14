import re
import pandas as pd


RESULT_COLUMNS = [
    "Test",
    "Result",
    "Unit",
    "Reference Range",
    "Status",
    "Explanation",
]


REPORT_KEYWORDS = {
    "Blood / Laboratory": [
        "cbc", "hemoglobin", "haemoglobin", "wbc", "rbc",
        "platelet", "glucose", "blood sugar", "hba1c",
        "creatinine", "urea", "bilirubin", "sgot", "sgpt",
        "tsh", "t3", "t4", "cholesterol", "triglyceride",
        "vitamin d", "vitamin b12", "albumin",
    ],
    "Urine / Infection": [
        "urinalysis", "urine routine", "urine culture",
        "pus cells", "urine protein", "urine glucose",
        "bacteria", "sensitivity test",
    ],
    "Imaging Report Text": [
        "x-ray", "xray", "radiology", "ct scan", "mri",
        "ultrasound", "sonography", "impression:", "findings:",
    ],
    "Cardiac / ECG Report Text": [
        "ecg", "ekg", "electrocardiogram", "qrs",
        "st segment", "pr interval", "qt interval",
    ],
    "Pathology": [
        "histopathology", "biopsy", "specimen", "microscopy",
    ],
    "Prescription": [
        "prescription", "dosage", "tablet", "capsule",
        "medication", "take once daily",
    ],
    "Discharge Summary": [
        "discharge summary", "discharge diagnosis",
        "hospital course", "discharge medication",
    ],
    "Clinical Report": [
        "clinical history", "symptoms", "examination",
        "diagnosis", "treatment plan", "clinical notes",
    ],
}


def identify_report_type(text):
    lower = text.lower()

    scores = {
        category: sum(keyword in lower for keyword in keywords)
        for category, keywords in REPORT_KEYWORDS.items()
    }

    if not scores or max(scores.values()) == 0:
        return "General Medical Document"

    return max(scores, key=scores.get)


def extract_patient_fields(text):
    patterns = {
        "Patient Name": (
            r"(?im)^\s*(?:patient\s+name|patient|name)\s*[:\-]\s*"
            r"([A-Za-z][A-Za-z .'-]{1,59})\s*$"
        ),
        "Age": r"\bAge\s*[:\-]?\s*(\d{1,3})\s*(?:years?|yrs?)?\b",
        "Gender": r"\b(?:gender|sex)\s*[:\-]?\s*(male|female|other)\b",
        "Report Date": (
            r"\b(?:report date|collection date|date)\s*[:\-]\s*"
            r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})"
        ),
    }

    fields = {}

    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            value = match.group(1).strip()
            fields[field] = value.title() if field == "Gender" else value
        else:
            fields[field] = "Not found"

    return fields


def _explanation(test, status):
    name = test.lower()

    descriptions = [
        (("hemoglobin", "haemoglobin"), "Hemoglobin carries oxygen in red blood cells."),
        (("wbc", "white blood cell"), "White blood cells are part of the immune system."),
        (("rbc", "red blood cell"), "Red blood cells carry oxygen."),
        (("platelet",), "Platelets help blood clot."),
        (("glucose", "blood sugar"), "Glucose is a blood sugar measurement."),
        (("hba1c",), "HbA1c estimates average blood sugar over roughly two to three months."),
        (("creatinine", "urea"), "This measurement may help clinicians assess kidney function."),
        (("tsh", "thyroid", "t3", "t4"), "This test relates to thyroid function."),
        (("cholesterol", "triglyceride", "hdl", "ldl"), "This test measures a type of blood lipid."),
        (("bilirubin", "sgot", "sgpt", "albumin"), "This measurement may be used when assessing liver function."),
        (("vitamin d", "vitamin b12"), "This test measures a vitamin level."),
    ]

    result = (
        "This laboratory measurement needs to be interpreted using its "
        "units, reference range, and clinical context."
    )

    for keywords, description in descriptions:
        if any(keyword in name for keyword in keywords):
            result = description
            break

    if status == "Below range":
        result += " The extracted value is below the printed range."
    elif status == "Above range":
        result += " The extracted value is above the printed range."
    elif status == "Within range":
        result += " The extracted value is within the printed range."
    else:
        result += " No reliable numerical comparison was made."

    return result


def analyze_report(text):
    rows = []
    seen = set()

    # Examples supported:
    # Hemoglobin: 13.5 g/dL (12.0-16.0)
    # TSH: 2.4 (0.4-4.0)
    # Creatinine: 1.1 mg/dL Reference Range: 0.6-1.2
    patterns = [
        re.compile(
            r"^\s*([A-Za-z][A-Za-z0-9 /()._%+-]{1,54}?)\s*[:=]\s*"
            r"([<>]?\s*\d+(?:\.\d+)?)\s*"
            r"([A-Za-zµμ/%][A-Za-z0-9µμ/%^.-]*)?"
            r"\s*\(\s*(\d+(?:\.\d+)?)\s*[-–]\s*"
            r"(\d+(?:\.\d+)?)\s*\)\s*$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\s*([A-Za-z][A-Za-z0-9 /()._%+-]{1,54}?)\s*[:=]\s*"
            r"([<>]?\s*\d+(?:\.\d+)?)\s*"
            r"([A-Za-zµμ/%][A-Za-z0-9µμ/%^.-]*)?"
            r".*?reference\s*range\s*[:=]?\s*"
            r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)",
            re.IGNORECASE,
        ),
    ]

    ignored = {
        "age", "patient age", "height", "weight",
        "phone", "mobile", "date", "report date",
    }

    for line in text.splitlines():
        match = None

        for pattern in patterns:
            match = pattern.match(line.strip())
            if match:
                break

        if not match:
            continue

        test = match.group(1).strip()
        result_text = match.group(2).replace(" ", "")
        unit = match.group(3) or ""
        low = match.group(4)
        high = match.group(5)

        if test.lower() in ignored:
            continue

        try:
            numeric_value = float(result_text.lstrip("<>"))
        except ValueError:
            continue

        identity = (test.lower(), result_text, unit.lower())
        if identity in seen:
            continue
        seen.add(identity)

        if low is None or high is None or result_text.startswith(("<", ">")):
            reference = "Not found" if low is None else f"{low} - {high}"
            status = "Not evaluated"
        else:
            reference = f"{low} - {high}"

            if numeric_value < float(low):
                status = "Below range"
            elif numeric_value > float(high):
                status = "Above range"
            else:
                status = "Within range"

        rows.append({
            "Test": test,
            "Result": result_text,
            "Unit": unit,
            "Reference Range": reference,
            "Status": status,
            "Explanation": _explanation(test, status),
        })

    return pd.DataFrame(rows, columns=RESULT_COLUMNS)


def summarize_document(text, report_type):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    markers = (
        "impression", "findings", "conclusion", "recommendation",
        "interpretation", "diagnosis", "observation", "clinical history",
        "treatment plan", "discharge advice", "positive", "negative",
        "detected", "not detected",
    )

    selected = []

    for line in lines:
        if any(marker in line.lower() for marker in markers):
            if line not in selected:
                selected.append(line[:500])

    if not selected:
        selected = lines[:8]

    return {
        "Report Type": report_type,
        "Extracted Text Lines": len(lines),
        "Key Sections": selected[:12],
    }
