
import streamlit as st
import pandas as pd

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide"
)

# ---------------- CUSTOM DESIGN ----------------
st.markdown("""
<style>
.main {
    background-color: #f7faff;
}
h1 {
    color: #1261a0;
}
h2, h3 {
    color: #174a70;
}
div[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #dce7f3;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🩺 AI Medical Report Explainer")
st.write(
    "Upload a medical report to extract its text, "
    "review detected laboratory results, and view a graph."
)

st.info(
    "Educational use only. This application does not provide "
    "a medical diagnosis or replace advice from a qualified doctor."
)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg"],
    help="Upload a PDF report or a clear image of a report."
)

# ---------------- HELPER FUNCTIONS ----------------
def normalize_results(data):
    """Convert supported analysis output into a DataFrame."""

    if isinstance(data, pd.DataFrame):
        return data.copy()

    if isinstance(data, list):
        return pd.DataFrame(data)

    if isinstance(data, dict):
        # Support dictionaries containing rows under common keys.
        for key in ("results", "data", "analysis"):
            if isinstance(data.get(key), (list, pd.DataFrame)):
                return pd.DataFrame(data[key])
        return pd.DataFrame([data])

    return pd.DataFrame()


def find_column(df, possible_names):
    """Find a column without depending on capitalization."""

    for column in df.columns:
        if str(column).strip().lower() in possible_names:
            return column
    return None


def numeric_values(series):
    """Extract numeric values from strings such as '12.5' or '1,200'."""

    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"([-+]?\d*\.?\d+)")[0],
        errors="coerce"
    )


# ---------------- PROCESS REPORT ----------------
if uploaded_file is not None:

    st.markdown("---")
    st.subheader("📄 Uploaded Report")
    st.write("**File name:**", uploaded_file.name)

    extracted_text = ""

    try:
        with st.spinner("Extracting text from your report..."):

            if uploaded_file.type == "application/pdf":
                extracted_text = extract_text_from_pdf(uploaded_file)

            else:
                extracted_text = extract_text_from_image(uploaded_file)

        if extracted_text is None:
            extracted_text = ""

        extracted_text = str(extracted_text).strip()

    except Exception as error:
        st.error("Unable to extract text from this file.")
        st.code(str(error))
        st.stop()

    # ---------------- EXTRACTED TEXT ----------------
    st.subheader("📝 Extracted Report Text")

    if extracted_text:
        st.text_area(
            "Text detected in the report",
            value=extracted_text,
            height=220
        )
    else:
        st.warning(
            "No text was detected. Try a clearer image or a text-based PDF."
        )
        st.stop()

    # ---------------- ANALYSIS ----------------
    st.markdown("---")
    st.subheader("🔬 Laboratory Results Analysis")

    try:
        with st.spinner("Analyzing detected results..."):
            analysis_output = analyze_report(extracted_text)

        results_df = normalize_results(analysis_output)

    except Exception as error:
        st.error("Could not analyze the extracted report.")
        st.code(str(error))
        st.stop()

    if results_df.empty:
        st.warning(
            "No laboratory results were recognized. "
            "Check the extracted text or the test names and values "
            "supported by analyzer.py."
        )

    else:
        # Identify common column names.
        test_col = find_column(
            results_df,
            {"test", "test name", "parameter", "lab test", "name"}
        )

        result_col = find_column(
            results_df,
            {"result", "value", "test result", "measured value"}
        )

        status_col = find_column(
            results_df,
            {"status", "interpretation", "flag"}
        )

        # Display results.
        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True
        )

        # ---------------- SUMMARY METRICS ----------------
        st.subheader("📌 Results Summary")

        if status_col is not None:
            statuses = (
                results_df[status_col]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            below_count = statuses.str.contains(
                r"\bbelow\b|\blow\b", regex=True
            ).sum()

            above_count = statuses.str.contains(
                r"\babove\b|\bhigh\b", regex=True
            ).sum()

            normal_count = statuses.str.contains(
                r"\bwithin range\b|\bnormal\b", regex=True
            ).sum()

            col1, col2, col3 = st.columns(3)

            col1.metric("Within range", int(normal_count))
            col2.metric("Above range", int(above_count))
            col3.metric("Below range", int(below_count))

        else:
            st.caption(
                "A status column was not provided by analyzer.py, "
                "so status summary metrics are unavailable."
            )

        # ---------------- GRAPH ----------------
        st.markdown("---")
        st.subheader("📊 Laboratory Results Graph")

        if test_col is not None and result_col is not None:

            chart_df = results_df[[test_col, result_col]].copy()

            chart_df["Numeric Result"] = numeric_values(
                chart_df[result_col]
            )

            chart_df[test_col] = chart_df[test_col].astype(str)

            chart_df = chart_df.dropna(
                subset=["Numeric Result"]
            )

            if not chart_df.empty:
                chart_df = chart_df.drop_duplicates(
                    subset=[test_col],
                    keep="first"
                )

                chart_data = chart_df.set_index(test_col)[
                    "Numeric Result"
                ]

                st.bar_chart(
                    chart_data,
                    x_label="Laboratory Test",
                    y_label="Reported Numeric Value",
                    use_container_width=True
                )

                st.caption(
                    "Values may use different units and reference ranges. "
                    "Bars are not directly comparable across different tests. "
                    "This graph does not determine whether a result is healthy."
                )

            else:
                st.info(
                    "Results were found, but no numeric values were available "
                    "to display in the graph."
                )

        else:
            st.warning(
                "The graph needs columns for the test name and numeric result. "
                "Check the column names returned by analyze_report() in analyzer.py."
            )

    # ---------------- AI EXPLANATION ----------------
    st.markdown("---")
    st.subheader("🤖 AI Explanation")

    st.write(
        "Generate a plain-language explanation of the extracted report. "
        "AI output may be inaccurate and must be reviewed by a qualified clinician."
    )

    if st.button("✨ Explain My Report", use_container_width=True):

        try:
            # Import only when the button is clicked.
            from ai_explainer import ai_explain_report

            with st.spinner("Preparing the explanation..."):
                explanation = ai_explain_report(extracted_text)

            if explanation:
                st.markdown("### Explanation")
                st.write(explanation)
            else:
                st.warning("The AI explanation was empty.")

        except Exception as error:
            st.error(
                "AI explanation could not be generated. "
                "Check ai_explainer.py and its API-key configuration."
            )
            st.code(str(error))

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption(
    "AI Medical Report Explainer | Educational project | "
    "Not a substitute for professional medical advice."
)
