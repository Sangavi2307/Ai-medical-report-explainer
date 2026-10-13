
import os


def ai_explain_report(report_text, results_df=None):
    api_key = os.getenv("OPENAI_API_KEY", "")

    if not api_key:
        return (
            "AI explanation is not configured. Add OPENAI_API_KEY to "
            "your Streamlit app Secrets to enable this feature. "
            "The extracted report and recognized results can still be reviewed."
        )

    if not report_text or not report_text.strip():
        return "No report text is available to explain."

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        result_context = ""
        if results_df is not None and not results_df.empty:
            result_context = results_df.to_string(index=False)

        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=(
                "Explain medical laboratory report text in plain, calm English. "
                "Do not diagnose, prescribe treatment, or invent missing values, "
                "units, or reference ranges. Explain that reference ranges vary "
                "by laboratory and patient factors. If a value's range is absent, "
                "say it cannot be classified from the supplied information. "
                "Encourage the user to discuss results with a qualified clinician. "
                "This is educational information, not medical advice."
            ),
            input=(
                "Explain the following extracted report and recognized results.\n\n"
                f"EXTRACTED REPORT:\n{report_text[:12000]}\n\n"
                f"RECOGNIZED RESULTS:\n{result_context[:6000]}"
            ),
        )

        return response.output_text

    except Exception as error:
        return (
            "The AI explanation could not be generated. Check your API key, "
            f"model access, and deployment logs. Technical detail: {error}"
        )
        
