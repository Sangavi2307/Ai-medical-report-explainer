
import os
import pandas as pd
from openai import OpenAI, RateLimitError, APIConnectionError, APIStatusError


def _fallback_explanation(results, patient_fields=None):
    """Provide a cautious explanation without calling the AI API."""
    if results is None or results.empty:
        return (
            "### Basic report summary\n\n"
            "No supported laboratory results were confidently "
            "identified. Please check the extracted text against "
            "your original report."
        )

    messages = [
        "### Basic report summary",
        "",
        "The AI service is currently unavailable. The following "
        "summary is generated using detected reference-range flags "
        "only; it is not an AI interpretation or a diagnosis.",
        ""
    ]

    for _, row in results.iterrows():
        test = str(row.get("Test", "Unknown test"))
        result = str(row.get("Result", "Not detected"))
        unit = str(row.get("Unit", "") or "")
        reference = str(row.get("Reference Range", "") or "")
        status = str(row.get("Status", "Range not detected"))

        measurement = f"{result} {unit}".strip()

        messages.append(f"- **{test}:** {measurement}")

        if reference:
            messages.append(f"  - Detected reference range: {reference}")

        if status == "Below detected range":
            messages.append(
                "  - The detected value is below the range printed "
                "or extracted from this report."
            )
        elif status == "Above detected range":
            messages.append(
                "  - The detected value is above the range printed "
                "or extracted from this report."
            )
        elif status == "Within detected range":
            messages.append(
                "  - The detected value falls within the detected "
                "range for this report."
            )
        else:
            messages.append(
                "  - A reference range was not reliably detected; "
                "no range-based conclusion is provided."
            )

    messages.extend([
        "",
        "**Important:** OCR or text extraction can misread values, "
        "decimal points, units, and reference ranges. Verify each "
        "result against the original report. A value within a "
        "reference range does not guarantee that a person is healthy, "
        "and a flagged value does not by itself establish a disease.",
        "",
        "For personal interpretation, consult a qualified healthcare "
        "professional."
    ])

    return "\n".join(messages)


def ai_explain_report(results, patient_fields=None, report_text=""):
    """
    Generate an educational report explanation.

    If the OpenAI API is unavailable or rate-limited, return a
    cautious rule-based summary instead.
    """
    patient_fields = patient_fields or {}

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return (
            "### AI explanation unavailable\n\n"
            "The `OPENAI_API_KEY` secret is not configured. "
            "A basic report summary is shown below instead.\n\n"
            + _fallback_explanation(results, patient_fields)
        )

    if results is None or results.empty:
        return _fallback_explanation(results, patient_fields)

    # Only send extracted results and limited report context.
    # Avoid sending unnecessary patient identifiers.
    safe_fields = {
        key: value
        for key, value in patient_fields.items()
        if key != "Patient Name" and value
    }

    results_text = results.to_string(index=False)

    # Limit the prompt size when the uploaded report is very long.
    safe_report_text = (report_text or "")[:8000]

    prompt = f"""
You are an educational medical-report explainer, not a doctor.

Explain the supplied laboratory results in simple English.
Do not diagnose diseases, prescribe medication, recommend treatment,
or claim that a result proves a condition.

Instructions:
1. Explain what each test generally measures.
2. Use only values, units, and reference ranges supplied below.
3. Explain detected flags cautiously.
4. If a reference range is missing or uncertain, say so.
5. Mention that ranges may vary by laboratory, age, sex, pregnancy,
   medical history, and other factors.
6. Do not invent test results or reference ranges.
7. Tell the reader to verify extracted data against the original report.
8. Recommend discussing personal concerns with a qualified clinician.
9. Keep the explanation clear, organized, and beginner-friendly.

Patient fields detected (may be incomplete):
{safe_fields}

Parsed laboratory results:
{results_text}

Extracted report text for context:
{safe_report_text}
"""

    try:
        client = OpenAI(api_key=api_key, timeout=30.0, max_retries=0)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        explanation = (response.output_text or "").strip()

        if explanation:
            return explanation

        return (
            "### AI response was empty\n\n"
            + _fallback_explanation(results, patient_fields)
        )

    except RateLimitError:
        return (
            "### AI explanation temporarily unavailable\n\n"
            "The OpenAI API rejected the request because of a rate "
            "limit or usage/billing limit. Check your API usage and "
            "billing, or wait and retry if it is a temporary request "
            "rate limit.\n\n"
            + _fallback_explanation(results, patient_fields)
        )

    except APIConnectionError:
        return (
            "### AI service connection failed\n\n"
            "The app could not connect to the AI service. Check the "
            "connection and try again.\n\n"
            + _fallback_explanation(results, patient_fields)
        )

    except APIStatusError as exc:
        return (
            "### AI service request failed\n\n"
            f"The API returned HTTP status `{exc.status_code}`. "
            "Check your API key, model access, project limits, and "
            "API service status.\n\n"
            + _fallback_explanation(results, patient_fields)
        )

    except Exception as exc:
        return (
            "### AI explanation unavailable\n\n"
            f"Error type: `{type(exc).__name__}`.\n\n"
            + _fallback_explanation(results, patient_fields)
        )
