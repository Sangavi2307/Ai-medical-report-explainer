
import pandas as pd


def ai_explain_report(report_text, results_df=None):
    """
    Create an educational explanation from the current report only.
    This function does not use a paid AI API or diagnose diseases.
    """

    report_text = str(report_text or "").strip()

    if not report_text:
        return "No readable text was found in the uploaded report."

    lines = [
        "## MediLens Medical Report Explanation",
        "",
        "This summary is based only on the report currently provided.",
        "It is for educational purposes and is not a medical diagnosis.",
        "",
        "### 1. Report Overview",
        "",
        f"- Extracted text length: {len(report_text)} characters",
        "",
        "### 2. Laboratory Results",
        "",
    ]

    if (
        isinstance(results_df, pd.DataFrame)
        and not results_df.empty
    ):
        for _, row in results_df.iterrows():
            test = str(row.get("Test", "Test name unavailable"))
            result = str(row.get("Result", "Not available"))
            unit = str(row.get("Unit", "") or "")
            reference = str(
                row.get("Reference Range", "Not provided") or "Not provided"
            )
            status = str(
                row.get("Status", "Not evaluated") or "Not evaluated"
            )

            lines.extend([
                f"#### {test}",
                f"- **Reported result:** {result} {unit}".strip(),
                f"- **Reference range:** {reference}",
                f"- **Reported status:** {status}",
            ])

            normalized_status = status.strip().lower()

            if normalized_status in {
                "normal",
                "within range",
                "within normal range",
            }:
                lines.append(
                    "- **Explanation:** The analyzer marked this result "
                    "as within the supplied range."
                )
            elif normalized_status in {
                "high",
                "above range",
                "abnormal high",
            }:
                lines.append(
                    "- **Explanation:** The analyzer marked this result "
                    "as above the supplied range."
                )
            elif normalized_status in {
                "low",
                "below range",
                "abnormal low",
            }:
                lines.append(
                    "- **Explanation:** The analyzer marked this result "
                    "as below the supplied range."
                )
            else:
                lines.append(
                    "- **Explanation:** This result has not been "
                    "classified. Verify it against the original report "
                    "and its reference range."
                )

            lines.append("")

    else:
        lines.extend([
            "No structured laboratory results were detected.",
            "",
            "This does not mean that the report is normal. "
            "Review the extracted text and original document.",
            "",
        ])

    lines.extend([
        "### 3. Important Notes",
        "",
        "- OCR or text extraction can contain errors.",
        "- Reference ranges may vary by laboratory and patient context.",
        "- This summary does not establish a diagnosis or recommend treatment.",
        "",
        "### 4. Next Step",
        "",
        "Discuss your results with a qualified healthcare professional, "
        "especially if you have symptoms or concerns.",
    ])

    return "\n".join(lines)
