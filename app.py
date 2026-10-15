
import streamlit as st
import pandas as pd

from extractor import extract_text_from_pdf
from ocr_service import (
    extract_text_from_image,
    extract_text_from_scanned_pdf,
)
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import explain_report


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="MediLens | Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
)


# ---------------- DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07111f, #10243a);
    color: #edf5ff;
}
h1, h2, h3 {
    color: #55d6be !important;
}
p, label, li {
    color: #edf5ff;
}
div[data-testid="stMetric"] {
    background: #132a40;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #24506a;
}
.stButton > button,
.stDownloadButton > button {
    background: #20bfa9;
    color: #07111f;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}
div[data-testid="stExpander"] {
    border: 1px solid #24506a;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.title("🩺 MediLens")
st.subheader("Medical Report Explainer")

st.write(
    "Upload a medical report to extract laboratory results, "
    "understand what tests measure, and review possible explanations."
)

st.warning(
    "Educational use only. MediLens does not diagnose medical "
    "conditions or recommend treatment."
)


# ---------------- FILE UPLOAD ----------------

uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    key="medical_report_upload",
)


# ---------------- INITIALIZE VARIABLES ----------------

report_text = ""
results_df = pd.DataFrame()
patient_fields = {}
explanation = None


if uploaded_file is None:
    st.info("Upload a PDF or image to begin.")
    st.stop()


# ---------------- EXTRACT REPORT TEXT ----------------

file_name = uploaded_file.name.lower()

try:
    with st.spinner("Reading your uploaded report..."):

        if file_name.endswith(".pdf"):
            # Extract selectable text first.
            report_text = extract_text_from_pdf(uploaded_file)

            # Use OCR if the PDF has no selectable text.
            if not report_text or not report_text.strip():
                uploaded_file.seek(0)
                report_text = extract_text_from_scanned_pdf(
                    uploaded_file
                )

        else:
            # Extract text from the uploaded image.
            report_text = extract_text_from_image(uploaded_file)

except Exception as error:
    st.error("Unable to read the uploaded file.")
    st.caption(
        "Check extractor.py, ocr_service.py, and the Streamlit logs."
    )
    st.exception(error)
    st.stop()


# ---------------- CHECK EXTRACTED TEXT ----------------

if not report_text or not report_text.strip():
    st.error(
        "No readable text was found. Try a clearer image "
        "or a text-based PDF."
    )
    st.stop()

st.success("Report text extracted successfully.")

with st.expander("View extracted report text"):
    st.text(report_text)


# ---------------- ANALYZE CURRENT REPORT ----------------

try:
    with st.spinner("Analyzing the uploaded report..."):
        results_df = analyze_report(report_text)
        patient_fields = extract_patient_fields(report_text)

except Exception as error:
    st.error("The report was read, but analysis failed.")
    st.exception(error)
    st.stop()


# Ensure the result is a DataFrame.
if not isinstance(results_df, pd.DataFrame):
    st.error("The analyzer did not return a pandas DataFrame.")
    st.stop()


# ---------------- PATIENT INFORMATION ----------------

st.divider()
st.header("📋 Report Information")

if patient_fields:
    for field, value in patient_fields.items():
        st.write(f"**{field}:** {value}")
else:
    st.info("Patient information was not detected in the report.")


# ---------------- LAB RESULTS ----------------

st.divider()
st.header("🔬 Laboratory Results")

if results_df.empty:
    st.warning(
        "No laboratory results were detected. "
        "Review the extracted report text above."
    )

else:
    st.dataframe(
        results_df,
        use_container_width=True,
        hide_index=True,
    )

    # Safely handle missing columns.
    if "Status" in results_df.columns:
        status = results_df["Status"].astype(str).str.lower()
    else:
        status = pd.Series(
            ["unknown"] * len(results_df),
            index=results_df.index,
        )

    within_range = status.isin(
        ["within range", "normal", "within normal range"]
    ).sum()

    below_range = status.isin(
        ["below range", "low", "below normal"]
    ).sum()

    above_range = status.isin(
        ["above range", "high", "above normal"]
    ).sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Tests found", len(results_df))
    col2.metric("Within range", int(within_range))
    col3.metric("Below range", int(below_range))
    col4.metric("Above range", int(above_range))

    # ---------------- CSV DOWNLOAD ----------------

    csv_data = results_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Results as CSV",
        data=csv_data,
        file_name="medilens_results.csv",
        mime="text/csv",
    )

    # ---------------- RESULTS CHART ----------------

    if "Result" in results_df.columns and "Test" in results_df.columns:
        numeric_results = results_df.copy()

        numeric_results["Result"] = pd.to_numeric(
            numeric_results["Result"]
            .astype(str)
            .str.replace(",", "", regex=False),
            errors="coerce",
        )

        numeric_results = numeric_results.dropna(
            subset=["Result"]
        )

        if not numeric_results.empty:
            st.subheader("📊 Extracted Results Chart")

            chart_data = numeric_results.set_index("Test")[["Result"]]
            st.bar_chart(chart_data)

            st.caption(
                "Only numeric results are plotted. Different tests may use "
                "different units and scales, so bar heights are not directly "
                "comparable across different tests."
            )


# ---------------- DETAILED EXPLANATIONS ----------------

st.divider()
st.header("💡 Detailed Report Explanations")

try:
    with st.spinner("Preparing detailed explanations..."):
        explanation = explain_report(
            report_text=report_text,
            results_df=results_df,
            patient_fields=patient_fields,
        )

    st.info(explanation.get("summary", "Explanation summary unavailable."))

    detailed_results = explanation.get("results", [])

    if detailed_results:

        for item in detailed_results:
            test_name = item.get("Test", "Unknown test")
            test_status = item.get("Status", "Needs review")

            with st.expander(
                f"🔎 {test_name} — {test_status}",
                expanded=False,
            ):
                st.markdown("#### Result details")

                st.write(
                    "**Reported result:**",
                    item.get("Result", "Not provided"),
                )

                st.write(
                    "**Reference range:**",
                    item.get("Reference Range", "Not provided"),
                )

                st.write(
                    "**Status:**",
                    test_status,
                )

                st.markdown("#### What this test measures")
                st.write(
                    item.get(
                        "Meaning",
                        "Detailed information is not available for this test.",
                    )
                )

                st.markdown("#### Why this test matters")
                st.write(
                    item.get(
                        "Importance",
                        "Interpret the result using the reference range "
                        "and clinical context.",
                    )
                )

                st.markdown("#### Understanding the result")
                st.write(
                    item.get(
                        "Interpretation",
                        item.get(
                            "Explanation",
                            "Compare the result with the original report "
                            "and its reference range.",
                        ),
                    )
                )

                possible_causes = item.get("Possible Causes", [])

                if possible_causes:
                    st.markdown(
                        "#### Possible reasons to discuss with a clinician"
                    )

                    for cause in possible_causes:
                        st.markdown(f"- {cause}")

                    st.caption(
                        "These are possible explanations, not a diagnosis "
                        "or confirmation of the cause."
                    )

                st.markdown("#### Possible follow-up")
                st.write(
                    item.get(
                        "Follow-up",
                        "Discuss unexpected results with a qualified "
                        "healthcare professional.",
                    )
                )

    else:
        st.warning(
            "There are no extracted laboratory results to explain."
        )

    # ---------------- GENERAL NOTES ----------------

    st.divider()
    st.subheader("📌 Important Notes")

    general_notes = explanation.get("general_notes", [])

    if general_notes:
        for note in general_notes:
            st.markdown(f"- {note}")
    else:
        st.write(
            "Verify the extracted values and reference ranges against "
            "the original report."
        )

except Exception as error:
    st.error("The report was analyzed, but the explanations could not be displayed.")
    st.caption(
        "Check that app.py and ai_explainer.py use matching field names."
    )
    st.exception(error)


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "MediLens | Educational project | Explanations are informational, "
    "not a diagnosis or substitute for professional medical advice."
)
