
from ai_explainer import explain_report

explanation = explain_report(
    report_text=report_text,
    results_df=results_df,
    patient_fields=patient_fields,
)

st.subheader("Report Summary")
st.write(explanation["summary"])

st.subheader("Test Explanations")

if explanation["results"]:
    for item in explanation["results"]:
        with st.expander(item["Test"]):
            st.write("**Result:**", item["Result"])
            st.write("**Reference range:**", item["Reference Range"])
            st.write("**Status:**", item["Status"])
            st.write("**What this test measures:**", item["Meaning"])
            st.write("**Explanation:**", item["Explanation"])
else:
    st.info(
        "No test results were extracted. Please check the uploaded report "
        "and the analyzer output."
    )

st.subheader("Important Notes")
for note in explanation["general_notes"]:
    st.write(f"- {note}")
