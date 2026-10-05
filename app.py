import streamlit as st
from analyzer import analyze_report

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺"
)

st.title("🩺 AI Medical Report Explainer")

st.write(
    "Analyze medical report values and compare them "
    "with the reference ranges provided in the report."
)

st.info(
    "⚠️ Educational purpose only. This application does not "
    "provide diagnosis or treatment."
)

st.subheader("🧪 Test Report Analysis")

sample_report = """
Hemoglobin 12.8 g/dL 12.0 - 15.5
Glucose 108 mg/dL 70 - 99
Vitamin D 18 ng/mL 30 - 100
WBC 7200 /uL 4000 - 11000
"""

if st.button("🔍 Analyze Report"):

    results = analyze_report(sample_report)

    if not results.empty:

        st.subheader("📊 Analysis Results")

        st.dataframe(
            results,
            use_container_width=True
        )

        st.subheader("📌 Summary")

        within = len(
            results[results["Status"] == "Within Range"]
        )

        below = len(
            results[results["Status"] == "Below Range"]
        )

        above = len(
            results[results["Status"] == "Above Range"]
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("🟢 Within Range", within)
        col2.metric("🟠 Below Range", below)
        col3.metric("🔴 Above Range", above)

    else:

        st.warning(
            "No test results could be detected."
        )
