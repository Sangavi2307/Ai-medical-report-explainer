```python
import pandas as pd
import streamlit as st

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from report_generator import generate_pdf_report


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
)

st.title("🩺 AI Medical Report Explainer")

st.caption(
    "Upload a medical report to review patient details, medical history, "
    "vital signs, laboratory results, doctor's observations, medications, "
    "and follow-up advice."
)

st.warning(
    "Educational use only. This application does not diagnose diseases "
    "or recommend treatment. Consult a qualified healthcare professional."
)


# ---------------- FILE UPLOAD ----------------

uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg"],
)

pasted_text = st.text_area(
    "Or paste your report text here",
    height=180,
    placeholder="Paste the complete text of your medical report...",
)


# ---------------- SESSION STATE ----------------

if "report_text" not in st.session_state:
    st.session_state.report_text = ""

if "results_df" not in st.session_state:
    st.session_state.results_df = pd.DataFrame()

if "ai_explanation" not in st.session_state:
    st.session_state.ai_explanation = ""


# ---------------- EXTRACT REPORT ----------------

if st.button("Extract and analyze report", type="primary"):

    report_text = ""

    try:
        with st.spinner("Reading your medical report..."):

            if pasted_text.strip():
                report_text = pasted_text.strip()

            elif uploaded_file is not None:
                file_name = uploaded_file.name.lower()

                if file_name.endswith(".pdf"):
                    report_text = extract_text_from_pdf(uploaded_file)
                else:
                    report_text = extract_text_from_image(uploaded_file)

            else:
                st.error("Please upload a report or paste report text.")
                st.stop()

        if not report_text or not report_text.strip():
            st.error(
                "No readable text was extracted. Try a clearer image "
                "or paste the report text manually."
            )
            st.stop()

        if report_text.startswith("No selectable text was found"):
            st.warning(
                "This PDF may be scanned. Try uploading it as an image "
                "or paste its text manually."
            )
            st.stop()

        # Save the extracted report.
        st.session_state.report_text = report_text

        # Analyze laboratory results separately.
        # An empty table does not prevent the full report explanation.
        try:
            results = analyze_report(report_text)

            if isinstance(results, pd.DataFrame):
                st.session_state.results_df = results
            else:
                st.session_state.results_df = pd.DataFrame()

        except Exception:
            st.session_state.results_df = pd.DataFrame()

        # Clear the previous explanation for the new report.
        st.session_state.ai_explanation = ""

        st.success("Report text extracted successfully.")

    except Exception as error:
        st.error(f"Could not process this report: {error}")


# ---------------- DISPLAY REPORT ----------------

report_text = st.session_state.report_text
results_df = st.session_state.results_df

if report_text:

    st.divider()
    st.subheader("1. Extracted Medical Report")

    st.text_area(
        "Extracted text — check that it matches your report",
        value=report_text,
        height=250,
        disabled=True,
        key="extracted_text_display",
    )

    st.download_button(
        "Download extracted text",
        data=report_text,
        file_name="extracted_report.txt",
        mime="text/plain",
    )

    # ---------------- LABORATORY ANALYSIS ----------------

    st.divider()
    st.subheader("2. Laboratory Results")

    if not results_df.empty:

        st.success(
            f"Recognized {len(results_df)} laboratory result(s)."
        )

        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = results_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download laboratory results as CSV",
            data=csv_data,
            file_name="laboratory_results.csv",
            mime="text/csv",
        )

    else:
        st.info(
            "No laboratory values were recognized. You can still generate "
            "an explanation of the complete report, including patient "
            "details, history, vital signs, observations, medications, "
            "and follow-up advice."
        )

    # ---------------- FULL REPORT EXPLANATION ----------------

    st.divider()
    st.subheader("3. Complete Medical Report Explanation")

    st.write(
        "Generate a plain-English explanation of the extracted report. "
        "The explanation depends on the readability of the extracted text "
        "and availability of the configured AI service."
    )

    if st.button("Generate full report explanation", type="primary"):

        with st.spinner("Analyzing the complete report..."):

            try:
                explanation = ai_explain_report(
                    report_text,
                    results_df,
                )

                st.session_state.ai_explanation = (
                    str(explanation)
                    if explanation
                    else "The AI service returned no explanation."
                )

            except Exception as error:
                st.session_state.ai_explanation = (
                    f"Could not generate the explanation: {error}"
                )

    if st.session_state.ai_explanation:

        st.markdown("### Explanation")

        st.markdown(st.session_state.ai_explanation)

        st.caption(
            "This explanation is informational only. Verify medical "
            "interpretations with a qualified healthcare professional."
        )

    # ---------------- DOWNLOAD SUMMARY ----------------

    st.divider()
    st.subheader("4. Download Report Summary")

    try:
        pdf_bytes = generate_pdf_report(
            report_text=report_text,
            results_df=results_df,
            ai_explanation=st.session_state.ai_explanation,
        )

        st.download_button(
            "Download summary as PDF",
            data=pdf_bytes,
            file_name="medical_report_summary.pdf",
            mime="application/pdf",
        )

    except Exception as error:
        st.error(f"Could not create PDF report: {error}")
```
