
def explain_report(report_text, results_df, patient_fields):
    text = (report_text or "").lower()
    sections = []

    sections.append("### General explanation")
    sections.append(
        "This explanation is generated from the text extracted from "
        "your uploaded document. OCR can make mistakes, so compare "
        "the extracted text with the original report."
    )

    name = patient_fields.get("Patient Name", "Not found")

    if name != "Not found":
        sections.append(f"**Patient name detected:** {name}")

    if not results_df.empty:
        sections.append("### Laboratory results")

        for _, row in results_df.iterrows():
            sections.append(
                f"- **{row['Test']}**: {row['Result']} "
                f"{row['Unit']}. Reference range: "
                f"{row['Reference Range'] or 'not detected'}. "
                f"Parser status: {row['Status']}."
            )
    else:
        sections.append("### Document type")
        sections.append(
            "No supported laboratory results were identified. "
            "This may be a medical note, medical-leave report, "
            "examination report, or a laboratory report whose layout "
            "could not be parsed."
        )

    if "pulmonary function" in text:
        sections.append(
            "The document mentions a pulmonary function test. "
            "This type of test evaluates aspects of breathing and lung "
            "function. The extracted text alone is not enough to verify "
            "the findings or determine a diagnosis."
        )

    if "fever" in text:
        sections.append(
            "The document mentions fever. The cause cannot be "
            "determined from that word alone."
        )

    if "symptom" in text or "presenting" in text:
        sections.append(
            "The document includes symptom-related information. "
            "Review the original wording because OCR may have changed it."
        )

    sections.append("### Important notice")
    sections.append(
        "For educational use only. This tool does not diagnose, "
        "recommend treatment, or determine fitness for work. A qualified "
        "healthcare professional should interpret the original document."
    )

    return "\n\n".join(sections)
