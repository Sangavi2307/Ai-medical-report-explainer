import os
import pandas as pd
import streamlit as st


def ai_explain_report(report_text, results_df=None):
    if not report_text or not report_text.strip():
        return "No report text is available to explain."

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        try:
            api_key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            api_key = None

    if not api_key:
        return (
            "OpenAI API key is not configured. Add OPENAI_API_KEY "
            "to Streamlit Community Cloud Secrets."
        )

    result_context = "No laboratory values were recognized."
    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        result_context = results_df.to_string(index=False)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model="gpt-4.1-mini",
            instructions=(
                "Explain the complete medical report in simple English. "
                "Organize the answer into patient details, medical history, "
                "vital signs, laboratory results, imaging findings, doctor's "
                "observations, medications, and follow-up instructions when "
                "those sections are present. Only include relevant sections. "
                "Do not invent missing information, correct uncertain OCR "
                "values by guessing, diagnose diseases, or recommend treatment. "
                "Clearly identify unclear or missing information. Explain that "
                "reference ranges vary and encourage review by a qualified "
                "healthcare professional. This is educational information, "
                "not medical advice."
            ),
            input=(
                "Explain this extracted medical report.\n\n"
                "EXTRACTED REPORT:\n"
                f"{report_text[:15000]}\n\n"
                "RECOGNIZED LABORATORY RESULTS:\n"
                f"{result_context[:4000]}"
            ),
            max_output_tokens=1200,
        )

        return response.output_text or "The AI returned an empty explanation."

    except Exception as error:
        error_text = str(error)

        if "credit_balance_exhausted" in error_text or "insufficient_quota" in error_text:
            return (
                "OpenAI API credits are exhausted. Add credits to the API "
                "account associated with your key, then try again."
            )

        if "401" in error_text or "invalid_api_key" in error_text:
            return (
                "The API key was rejected. Check that OPENAI_API_KEY in "
                "Streamlit Secrets is correct and active."
            )

        return f"AI explanation failed. Technical detail: {error_text}"
