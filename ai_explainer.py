import os
from openai import OpenAI


def ai_explain_report(report_text):

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return (
            "AI explanation is unavailable because "
            "the API key is not configured."
        )

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are an educational medical laboratory report explanation assistant.

Analyze ONLY the information present in the report.

Create a clear, beginner-friendly explanation.

For EACH laboratory test found in the report, use this format:

### Test Name
- Result:
- Reference Range:
- Status:
- What this test measures:
- Simple explanation:

Then provide:

### Overall Summary
Give a short summary of the laboratory results.

### Important Note
Explain that:
- Reference ranges can vary between laboratories.
- An abnormal result does not automatically mean a disease.
- Results should be interpreted together with symptoms, history,
  medications, and other clinical information.
- OCR or extracted text can sometimes contain errors.

STRICT SAFETY RULES:

1. Do not diagnose any disease.
2. Do not prescribe medicines.
3. Do not recommend changing or stopping medicines.
4. Do not invent test results.
5. Use ONLY the reference ranges shown in the report.
6. Do not assume a missing reference range.
7. Clearly distinguish the reported result from general education.
8. Keep the explanation simple and understandable.
9. Recommend discussing actual medical results with a qualified
   healthcare professional.
10. This is an educational explanation only.

REPORT:
{report_text}
"""

    try:

        response = client.responses.create(
            model="gpt-6-luna",
            input=prompt
        )

        return response.output_text

    except Exception as e:

        return (
            "Unable to generate the AI explanation at this time.\n\n"
            f"Error: {e}"
        )
