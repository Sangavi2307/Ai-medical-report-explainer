
import os
import pandas as pd
from openai import OpenAI


def ai_explain_report(
    results,
    patient_fields=None,
    report_text="",
):
    """
    Generate a plain-English explanation using an AI model.
    Requires OPENAI_API_KEY in the environment.
    """

    patient_fields = patient_fields or {}

    # Prepare laboratory results for the model.
    if isinstance(results, pd.DataFrame) and not results.empty:
        lab_data = results.to_dict(orient="records")
    else:
        lab_data = []

    if not report_text or not report_text.strip():
        return (
            "## Explanation unavailable\n\n"
            "No readable text was extracted from the report. "
            "Try a clearer image or PDF."
        )

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return (
            "## AI explanation is not configured\n\n"
            "The report text was extracted, but a real AI explanation "
            "requires an OpenAI API key.\n\n"
            "Add OPENAI_API_KEY to your Streamlit Cloud app secrets, "
            "then redeploy the application.\n\n"
            "The extracted report text is not itself an AI explanation."
        )

    # Do not send unlimited document text to the model.
    safe_report_text = report_text[:18000]

    prompt = f"""
You explain medical laboratory reports in simple English for educational
purposes. You are not a doctor and must not diagnose or prescribe treatment.

Patient details extracted from the document:
{patient_fields}

Laboratory results extracted by the application:
{lab_data}

Extracted report text:
{safe_report_text}

Instructions:
1. Explain the identified tests in understandable language.
2. Use the supplied result and reference range exactly as provided.
3. Never invent a missing value, unit, range, patient detail, or diagnosis.
4. Explain whether a value is below, within, or above its stated range
   only when the provided data supports that comparison.
5. If OCR or the table parsing may be incorrect, explicitly say to verify
   the value against the original report.
6. Mention important findings in a neutral way without claiming that a
   single result proves a disease.
7. Summarize the report, explain identified tests, list uncertainties,
   and give general guidance to discuss results with a qualified
   healthcare professional.
8. If no laboratory results were identified, say so clearly.
9. Do not provide medication doses or treatment instructions.
10. Use clear headings and simple English.
"""

    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        explanation = response.output_text.strip()

        if not explanation:
            return (
                "## AI explanation unavailable\n\n"
                "The AI model returned an empty response. "
                "Please try again."
            )

        return explanation

    except Exception as error:
        # Keep the error useful for troubleshooting without exposing
        # credentials or the full report.
        return (
            "## AI explanation failed\n\n"
            "The report was extracted, but the AI service could not "
            "generate an explanation.\n\n"
            f"Error type: {type(error).__name__}\n\n"
            "Check your API key, API billing or available credits, "
            "model access, and Streamlit Cloud logs."
        )
