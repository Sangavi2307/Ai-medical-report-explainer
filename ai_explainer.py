
def create_report_summary(report_text, results_df, patient_fields):
    parts = []

    name = patient_fields.get("Patient Name", "")
    if name:
        parts.append(f"The extracted report lists the patient as {name}.")

    date = patient_fields.get("Report Date", "")
    if date:
        parts.append(f"The extracted report date is {date}.")

    if results_df is not None and not results_df.empty:
        count = len(results_df)
        parts.append(
            f"The application recognized {count} laboratory result line(s)."
        )
        parts.append(
            "Recognized values are displayed as extracted. This prototype "
            "does not verify whether results are normal, abnormal, or "
            "clinically significant."
        )
    else:
        parts.append(
            "No laboratory result lines matched the application's supported "
            "text patterns. This does not mean the report contains no results."
        )

    parts.append(
        "This summary is generated from text extraction rules, not a "
        "medical diagnosis. Ask a qualified healthcare professional to "
        "interpret your results."
    )

    return "\n\n".join(parts)
