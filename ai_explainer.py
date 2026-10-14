
def ai_explain_report(report_text, results_df=None):
    report_text = str(report_text or "").strip()

    if not report_text:
        return "No readable text was found in the uploaded report."

    lines = [
        "## Medical Report Explanation",
        "",
        "This is an educational summary, not a medical diagnosis.",
        "",
        "### Extracted Lab Results",
        ""
    ]

    if results_df is not None and not results_df.empty:
        for _, row in results_df.iterrows():
            details = " | ".join(
                f"{key}: {value}" for key, value in row.items()
            )
            lines.append("- " + details)
    else:
        lines.append("No structured lab results were detected.")

    lines.extend([
        "",
        "Please discuss your results with a qualified healthcare professional."
    ])

    return "\n".join(lines)
