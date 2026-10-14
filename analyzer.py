
import os


def ai_explain_report(report_text, results_df=None):
    api_key = os.getenv("OPENAI_API_KEY", "")

    if not report_text or not report_text.strip():
        return (
            "No readable text was extracted from this report. "
            "Please upload a clearer image or a text-based PDF."
        )

    if not api_key:
        return (
            "AI explanation is unavailable because the API key is not configured. "
            "The extracted report text is available for review, but an AI "
            "explanation cannot be generated until a working model is configured."
        )

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        result_context = ""
        if results_df is not None and not results_df.empty:
            result_context = results_df.to_string(index=False)

        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions="""
You are an educational medical report explainer.

Analyze the COMPLETE supplied medical report, not only laboratory results.

Identify and explain the sections that are actually present:
1. Patient details and report date.
2. Reason for visit and symptoms.
3. Medical history, previous surgeries, and allergies.
4. Vital signs, including blood pressure, pulse, temperature,
   respiratory rate, and oxygen saturation when present.
5. Laboratory tests, measured values, units, and reference ranges.
6. Imaging, radiology, scans, and other diagnostic findings.
7. Doctor's observations, clinical notes, and assessment.
8. Medicines and instructions already written in the report.
9. Follow-up instructions and recommendations.
10. A simple-language summary of the report.

For each section:
- Explain medical terms in simple English.
- Use only information supported by the supplied report.
- Clearly state when information is missing or unreadable.
- Never invent patient details, test results, units, or reference ranges.
- Do not assume that an omitted result is normal.
- Explain abnormal flags only when supported by the report and its
  reference ranges.
- Do not diagnose a disease or prescribe, stop, or change medication.
- Do not treat OCR mistakes as confirmed medical facts.
- If information is unclear or contradictory, point it out.
- Recommend discussing important concerns with a qualified clinician.

Use clear headings and bullet points.
Finish with a brief summary and a reminder that the explanation is
educational and does not replace professional medical advice.
""",
            input=(
                "Analyze this complete medical report.\n\n"
                "EXTRACTED REPORT TEXT:\n"
                f"{report_text[:18000]}\n\n"
                "LABORATORY RESULTS RECOGNIZED BY THE APPLICATION:\n"
                f"{result_context[:6000] if result_context else 'No structured laboratory results were recognized. Analyze the original extracted text as well.'}"
            ),
        )

        explanation = response.output_text

        if not explanation or not explanation.strip():
            return (
                "The AI returned an empty explanation. "
                "Please try again with a clearer report."
            )

        return explanation

    except Exception as error:
        return (
            "The report text was extracted, but the AI explanation failed. "
            "Check your API key, available API credits, model access, and "
            "Streamlit deployment logs. "
            f"Technical detail: {error}"
        )
