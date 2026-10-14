import re


def ai_explain_report(report_text, results_df=None):
    """
    Generate a simple educational explanation for one uploaded medical report.
    No paid API or API key is required.
    """

    report_text = str(report_text or "").strip()

    if not report_text:
        return (
            "No readable text was found in the uploaded report. "
            "Please upload a clearer image or PDF."
        )

    output = [
        "## Medical Report Explanation",
        "",
        "This explanation uses the text extracted from your uploaded report.",
        "It is for educational purposes only and is not a medical diagnosis.",
        "",
    ]

    # Display the structured results from analyzer.py.
    if results_df is not None and not getattr(results_df, "empty", True):
        output.extend(["### Lab Results", ""])

        for _, row in results_df.iterrows():
            # Convert the row to a dictionary so different column names
            # can be handled safely.
            data = {
                str(key).strip().lower(): value
                for key, value in row.to_dict().items()
            }

            def get_value(*names):
                for name in names:
                    value = data.get(name)
                    if value is not None and str(value).strip().lower() not in {
                        "", "nan", "none"
                    }:
                        return str(value).strip()
                return ""

            test_name = get_value(
                "test", "test_name", "parameter", "name"
            ) or "Lab test"

            result_value = get_value(
                "value", "result", "observed_value"
            ) or "Not available"

            reference_range = get_value(
                "reference range", "reference_range",
                "normal range", "normal_range", "range"
            )

            status = get_value("status", "interpretation")

            output.append(f"**{test_name}:** {result_value}")

            if reference_range:
                output.append(f"- Reference range: {reference_range}")

            if status:
                output.append(f"- Status: {status}")

            output.append("")

    else:
        output.extend([
            "### Lab Results",
            "",
            "No structured lab results were provided by the analyzer.",
            "Please check whether the report was extracted and analyzed correctly.",
            "",
        ])

    # Check for urgent wording in the current uploaded report only.
    if re.search(
        r"\b(critical|panic value|urgent)\b",
        report_text,
        flags=re.IGNORECASE,
    ):
        output.extend([
            "### Important Notice",
            "",
            "The report contains wording that may indicate urgency. "
            "Contact a qualified healthcare professional or the reporting "
            "laboratory promptly.",
            "",
        ])

    output.extend([
        "### Next Steps",
        "",
        "- Compare each result with the reference range printed by the laboratory.",
        "- Discuss abnormal results with a qualified healthcare professional.",
        "- Do not change medication based only on this explanation.",
        "",
        "**Disclaimer:** This tool provides general educational information. "
        "It does not diagnose diseases or replace professional medical advice.",
    ])

    return "\n".join(output)