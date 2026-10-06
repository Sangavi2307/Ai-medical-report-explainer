import os
from openai import OpenAI


def ai_explain_report(report_text):

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "AI explanation is unavailable because the API key is not configured."

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are an educational medical-report explanation assistant.

Analyze ONLY the information contained in the report below.

Your response should:

1. Give a short summary of the report.
2. Explain the laboratory results in simple language.
3. Use the reference ranges printed in the report.
4. Clearly identify results as within, below, or above the stated range.
5. Explain what each test generally measures.
6. Do not diagnose diseases.
7. Do not prescribe medicines or treatment.
8. Do not recommend stopping or changing medicines.
9. Do not invent missing patient information or test results.
10. Mention that abnormal results can have many possible causes.
11. Clearly state that the explanation is informational only.
12. Recommend discussing actual medical results with a qualified healthcare professional.

REPORT:
{report_text}
"""

    response = client.responses.create(
        model="gpt-6-luna",
        input=prompt
    )

    return response.output_text
