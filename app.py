
import streamlit as st
import pandas as pd

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image, extract_text_from_scanned_pdf
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
p, label {
    color: #edf5ff;
}
div[data-testid="stMetric"] {
    background: #132a40;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #24506a;
}
.stButton > button {
    background: #20bfa9;
    color: #07111f;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.title("🩺 MediLens")
st.subheader("AI Medical Report Explainer")
st.write(
    "Upload a medical report to extract laboratory results "
    "and view simple explanations."
)

st.warning(
    "Educational use only. This application does not diagnose "
    "medical conditions or recommend treatment."
)


# ---------------- FILE UPLOAD ----------------

uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    key="medical_report_upload",
)

# Initialize report_text before using it.
report_text = ""
results_df = pd.DataFrame()
patient_fields = {}
explanation = None


# ---------------- EXTRACT REPORT TEXT ----------------

if uploaded_file is None:
    st.info("Upload a PDF or image to begin.")
    st.stop()

file_name = uploaded_file.name.lower()

try:
    with st.spinner("Reading your uploaded report..."):

        if file_name.endswith(".pdf"):
            # First try extracting selectable PDF text.
            report_text = extract_text_from_pdf(uploaded_file)

            # If the PDF is scanned, try OCR.
            if not report_text or not report_text.strip():
                uploaded_file.seek(0)
                report_text = extract_text_from_scanned_pdf(
                    uploaded_file
                )

        else:
            # Read the uploaded image using OCR.
            report_text = extract_text_from_image(uploaded_file)

except Exception as error:
    st.error("Unable to read this file.")
    st.caption(
        "Check extractor.py, ocr_service.py and the app logs."
    )
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


# ---------------- ANALYZE THIS REPORT ONLY ----------------

try:
    results_df = analyze_report(report_text)
    patient_fields = extract_patient_fields(report_text)

except Exception:
    st.error("The report was read, but analysis failed.")
    st.exception(Exception("Check analyzer.py for the analysis error."))
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
        "Open the extracted report text above to check what was read."
    )
else:
    st.dataframe(
        results_df,
        use_container_width=True,
        hide_index=True,
    )

    total_tests = len(results_df)
    within_range = (
        results_df["Status"].astype(str).str.lower()
        .isin(["within range", "normal", "within normal range"])
        .sum()
    )
    below_range = (
        results_df["Status"].astype(str).str.lower()
        .isin(["below range", "low", "below normal"])
        .sum()
    )
    above_range = (
        results_df["Status"].astype(str).str.lower()
        .isin(["above range", "high", "above normal"])
        .sum()
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Tests found", total_tests)
    col2.metric("Within range", int(within_range))
    col3.metric("Below range", int(below_range))
    col4.metric("Above range", int(above_range))

    # Download extracted results.
    csv_data = results_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Results as CSV",
        data=csv_data,
        file_name="medilens_results.csv",
        mime="text/csv",
    )

    # ---------------- CHART ----------------

    numeric_results = results_df.copy()
    numeric_results["Result"] = pd.to_numeric(
        numeric_results["Result"],
        errors="coerce",
    )
    numeric_results = numeric_results.dropna(subset=["Result"])

    if not numeric_results.empty:
        st.subheader("📊 Extracted Results Chart")

        chart_data = numeric_results.set_index("Test")[["Result"]]
        st.bar_chart(chart_data)


# ---------------- EXPLANATIONS ----------------

st.divider()
st.header("💡 Report Explanations")

try:
    explanation = explain_report(
        report_text=report_text,
        results_df=results_df,
        patient_fields=patient_fields,
    )

    st.info(explanation["summary"])

    if explanation["results"]:
        for item in explanation["results"]:
            with st.expander(str(item["Test"])):
                st.write("**Result:**", item["Result"])
                st.write(
                    "**Reference range:**",
                    item["Reference Range"],
                )
                st.write("**Status:**", item["Status"])
                st.write("**Meaning:**", item["Meaning"])
                st.write(
                    "**Explanation:**",
                    item["Explanation"],
                )
    else:
        st.warning(
            "There are no extracted results to explain yet."
        )

    st.subheader("Important Notes")

    for note in explanation["general_notes"]:
        st.write(f"- {note}")

except Exception:
    st.error("The report was analyzed, but explanations failed.")
    st.caption(
        "Check ai_explainer.py and the full error in Streamlit Cloud logs."
    )


# ---------------- FOOTER ----------------

st.divider()
st.caption(
    "MediLens | Educational project | Not a substitute "
    "for professional medical advice."
)
