
import re


def explain_report(report_text, results_df, patient_fields):
    text = (report_text or "").strip()
    lower = text.lower()
    sections = []

    def add(title, body):
        sections.append(f"## {title}\n\n{body}")

    # 1. Document overview
    if any(word in lower for word in [
        "medical leave", "fitness for work", "fit to work",
        "date of examination", "physician"
    ]):
        document_type = "Medical or examination report"
    elif any(word in lower for word in [
        "laboratory results", "reference range", "hemoglobin",
        "platelets", "glucose"
    ]):
        document_type = "Potential laboratory report"
    else:
        document_type = "General medical document"

    add(
        "1. Document overview",
        f"**Detected document category:** {document_type}\n\n"
        "This category is inferred from words in the extracted text. "
        "It is not a verified classification of the original document."
    )

    # 2. Patient details
    details = []
    for label, value in (patient_fields or {}).items():
        if value and value != "Not found":
            details.append(f"- **{label}:** {value}")

    add(
        "2. Patient information",
        "\n".join(details) if details else
        "No patient details could be confidently extracted."
    )

    # 3. Clinical context
    clinical_labels = [
        ("Chief complaint", r"Chief Complaint\s*:?\s*([^\n]+)"),
        ("Presenting symptoms", r"Presenting Symptoms\s*:?\s*([^\n]+)"),
        ("Duration", r"Duration\s*:?\s*([^\n]+)"),
        ("Temperature", r"Temperature\s*:?\s*([^\n]+)"),
        ("Blood pressure", r"Blood Pressure\s*:?\s*([^\n]+)"),
        ("Pulse rate", r"Pulse Rate\s*:?\s*([^\n]+)"),
        ("Assessment", r"Assessment\s*:?\s*([^\n]+)"),
        ("Advice", r"Advice\s*:?\s*([^\n]+)"),
    ]

    clinical = []
    for label, pattern in clinical_labels:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if value:
                clinical.append(f"- **{label}:** {value}")

    if "pulmonary function" in lower:
        clinical.append(
            "- **Pulmonary function test:** The text mentions a test "
            "used to assess breathing and aspects of lung function. "
            "The actual measurements and interpretation were not "
            "verified by this application."
        )

    if "acute bronchitis" in lower:
        clinical.append(
            "- **Respiratory wording:** The extracted text contains "
            "the phrase 'acute bronchitis'. OCR may have altered the "
            "surrounding sentence, so verify this wording against the "
            "original report."
        )

    add(
        "3. Clinical information found",
        "\n".join(clinical) if clinical else
        "No clearly labelled clinical details were identified. "
        "Review the extracted text for missing or incorrectly read content."
    )

    # 4. Laboratory results
    if results_df is not None and not results_df.empty:
        lab_lines = []

        for _, row in results_df.iterrows():
            test = str(row.get("Test", "Unknown test"))
            result = str(row.get("Result", "Not found"))
            unit = str(row.get("Unit", "") or "")
            reference = str(row.get("Reference Range", "") or "")
            status = str(row.get("Status", "Not assessed"))

            lab_lines.append(
                f"- **{test}:** {result} {unit}. "
                f"Reference range shown in report: "
                f"{reference or 'not identified'}. "
                f"Automated comparison: {status}."
            )

        add(
            "4. Laboratory findings",
            "\n".join(lab_lines) +
            "\n\nThese comparisons depend on correctly extracted values "
            "and ranges. Reference intervals vary by laboratory and "
            "individual circumstances."
        )
    else:
        add(
            "4. Laboratory findings",
            "No supported laboratory measurements were identified. "
            "This does not mean the report is normal or abnormal. "
            "The document may describe symptoms, an examination, "
            "or a diagnostic test without numerical laboratory values."
        )

    # 5. OCR limitations
    words = re.findall(r"\b[\w'-]+\b", text)
    suspicious = []

    # Heuristic warning only; this is not a validated OCR score.
    if len(words) < 25:
        suspicious.append("Only a small amount of text was extracted.")

    if re.search(r"\b(?:nntioorr|nmiodi|incatng|mecical|roared)\b",
                 lower):
        suspicious.append(
            "Some extracted words appear corrupted or incorrectly recognized."
        )

    if re.search(r"\b(?:YYYY|MM/DD/YYYY|Number of Days)\b", text,
                 re.IGNORECASE):
        suspicious.append(
            "The text contains placeholders or incomplete date information."
        )

    add(
        "5. Data quality and limitations",
        "\n".join(f"- {item}" for item in suspicious)
        if suspicious else
        "No specific OCR warning was triggered. This does not guarantee "
        "that all text or numbers were extracted correctly."
    )

    # 6. Practical next steps
    next_steps = [
        "Compare the extracted text with the original image or PDF.",
        "Confirm names, dates, test values, units, and reference ranges.",
        "Ask the treating healthcare professional to clarify unclear findings.",
        "Do not use this automated explanation to make treatment or work-fitness decisions.",
    ]

    add("6. Recommended next steps",
        "\n".join(f"{i}. {step}" for i, step in enumerate(next_steps, 1)))

    # 7. Safety note
    add(
        "Important medical notice",
        "This application provides educational document assistance only. "
        "It does not verify a diagnosis, determine medical fitness for "
        "work, recommend treatment, or replace a qualified healthcare "
        "professional. Incorrect OCR can change the meaning of a report."
    )

    return "\n\n".join(sections)
