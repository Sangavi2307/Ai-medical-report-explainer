
import streamlit as st
import pandas as pd
import re

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# CUSTOM DESIGN
# =====================================================

st.markdown("""
<style>
.stApp {
    background-color: #10141e;
    color: #f4f6fa;
}

h1, h2, h3 {
    color: #69b9ff;
}

div[data-testid="stMetric"] {
    background-color: #202a39;
    border: 1px solid #43536a;
    padding: 15px;
    border-radius: 12px;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
}

div[data-testid="stAlert"] {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def find_column(dataframe, possible_names):
    """Find a column using case-insensitive names."""

    for column in dataframe.columns:
        cleaned = str(column).strip().lower()

        if cleaned in possible_names:
            return column

    return None


def convert_to_dataframe(data):
    """Convert analyzer output into a DataFrame."""

    if isinstance(data, pd.DataFrame):
        return data.copy()

    if isinstance(data, list):
        return pd.DataFrame(data)

    if isinstance(data, dict):
        for key in ("results", "data", "analysis"):
            if isinstance(data.get(key), list):
                return pd.DataFrame(data[key])

        return pd.DataFrame([data])

    return pd.DataFrame()


def convert_numeric(series):
    """Convert values such as 7,800 and 13.2 into numbers."""

    cleaned = (
        series.fillna("")
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"([-+]?\d*\.?\d+)")[0]
    )

    return pd.to_numeric(cleaned, errors="coerce")


def count_statuses(dataframe, status_column):
    """Count recognized status labels."""

    statuses = (
        dataframe[status_column]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    normal = statuses.isin({
        "within range",
        "within the stated range",
        "normal"
    }).sum()

    high = statuses.isin({
        "above range",
        "above",
        "high",
        "above normal"
    }).sum()

    low = statuses.isin({
        "below range",
        "below",
        "low",
        "below normal"
    }).sum()

    return int(normal), int(high), int(low)


# =====================================================
# HEADER
# =====================================================

st.title("🩺 AI Medical Report Explainer")

st.write(
    "Upload a medical report to extract its text, "
    "review detected laboratory results, and view a graph."
)

st.info(
    "Educational use only. This application does not provide "
    "a medical diagnosis or replace advice from a qualified doctor."
)


# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "📄 Upload your medical report",
    type=["pdf", "png", "jpg", "jpeg"]
)


# =====================================================
# MAIN PROCESSING
# =====================================================

if uploaded_file is not None:

    st.markdown("---")
    st.subheader("📁 Uploaded Report")

    st.write("**File name:**", uploaded_file.name)

    # -------------------------------------------------
    # TEXT EXTRACTION
    # -------------------------------------------------

    try:
        with st.spinner("Extracting report text..."):

            if uploaded_file.name.lower().endswith(".pdf"):
                extracted_text = extract_text_from_pdf(
                    uploaded_file
                )
            else:
                extracted_text = extract_text_from_image(
                    uploaded_file
                )

        if extracted_text is None:
            extracted_text = ""

        extracted_text = str(extracted_text).strip()

    except Exception as error:
        st.error("Unable to extract text from the report.")
        st.code(str(error))
        st.stop()

    st.subheader("📝 Extracted Report Text")

    if not extracted_text:
        st.warning(
            "No text was detected. Try a clearer image or another PDF."
        )
        st.stop()

    st.text_area(
        "Text detected in the report",
        value=extracted_text,
        height=220
    )

    # -------------------------------------------------
    # LABORATORY ANALYSIS
    # -------------------------------------------------

    st.markdown("---")
    st.subheader("🔬 Laboratory Results Analysis")

    try:
        with st.spinner("Analyzing laboratory results..."):
            analysis_output = analyze_report(extracted_text)

        results_df = convert_to_dataframe(analysis_output)

    except Exception as error:
        st.error("Laboratory analysis failed.")
        st.code(str(error))
        st.stop()

    if results_df.empty:
        st.warning(
            "No laboratory results were recognized. "
            "Check the extracted text and the test names supported "
            "by analyzer.py."
        )

    else:

        # Identify columns returned by analyzer.py.
        test_col = find_column(
            results_df,
            {
                "test",
                "test name",
                "parameter",
                "lab test",
                "name"
            }
        )

        result_col = find_column(
            results_df,
            {
                "result",
                "value",
                "test result",
                "measured value"
            }
        )

        status_col = find_column(
            results_df,
            {
                "status",
                "interpretation",
                "flag"
            }
        )

        # ---------------------------------------------
        # RESULTS TABLE
        # ---------------------------------------------

        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True
        )

        # ---------------------------------------------
        # RESULTS SUMMARY
        # ---------------------------------------------

        st.markdown("---")
        st.subheader("📌 Results Summary")

        if status_col is not None:

            normal_count, high_count, low_count = (
                count_statuses(results_df, status_col)
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Within Range",
                normal_count
            )

            col2.metric(
                "Above Range",
                high_count
            )

            col3.metric(
                "Below Range",
                low_count
            )

            st.caption(
                "Counts are based on the status labels returned "
                "by the analyzer. They do not establish a diagnosis."
            )

        else:
            st.warning(
                "The analyzer did not return a recognized Status column. "
                "Check the column names in analyzer.py."
            )

        # ---------------------------------------------
        # LABORATORY RESULTS GRAPH
        # ---------------------------------------------

        st.markdown("---")
        st.subheader("📊 Laboratory Results Graph")

        if test_col is None or result_col is None:

            st.warning(
                "The graph needs Test and Result columns. "
                "Check the column names returned by analyzer.py."
            )

        else:

            chart_df = results_df[
                [test_col, result_col]
            ].copy()

            chart_df.columns = [
                "Test",
                "Original Result"
            ]

            chart_df["Test"] = (
                chart_df["Test"]
                .fillna("")
                .astype(str)
                .str.strip()
            )

            chart_df["Numeric Result"] = convert_numeric(
                chart_df["Original Result"]
            )

            chart_df = chart_df[
                chart_df["Test"] != ""
            ].dropna(subset=["Numeric Result"])

            if not chart_df.empty:

                # Use the first occurrence of each test name.
                chart_df = chart_df.drop_duplicates(
                    subset=["Test"],
                    keep="first"
                )

                chart_data = chart_df[
                    ["Test", "Numeric Result"]
                ].set_index("Test")

                st.bar_chart(
                    chart_data,
                    use_container_width=True,
                    y_label="Reported numeric value"
                )

                with st.expander("View graph data"):
                    st.dataframe(
                        chart_df[
                            ["Test", "Original Result", "Numeric Result"]
                        ],
                        use_container_width=True,
                        hide_index=True
                    )

                st.caption(
                    "Different laboratory tests can use different units "
                    "and scales. The bars show reported numbers only and "
                    "should not be compared as measures of medical severity."
                )

            else:
                st.warning(
                    "No numeric results were available for the graph. "
                    "Check the Result column returned by analyzer.py."
                )


    # =================================================
    # AI EXPLANATION
    # =================================================

    st.markdown("---")
    st.subheader("🤖 AI Explanation")

    st.write(
        "Generate a plain-language explanation of the extracted report."
    )

    st.caption(
        "AI explanations can be inaccurate. Verify actual medical results "
        "with a qualified healthcare professional."
    )

    if st.button(
        "✨ Explain My Report",
        use_container_width=True
    ):

        try:
            from ai_explainer import ai_explain_report

            with st.spinner("Generating explanation..."):
                explanation = ai_explain_report(extracted_text)

            if explanation:
                st.markdown("### Explanation")
                st.write(explanation)
            else:
                st.warning("The AI returned an empty explanation.")

        except Exception as error:
            st.error(
                "Could not generate the AI explanation. "
                "Check ai_explainer.py and your API-key configuration."
            )
            st.code(str(error))


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "AI Medical Report Explainer | Educational project | "
    "Not a substitute for professional medical advice."
            )
