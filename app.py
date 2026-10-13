
import re
from io import BytesIO

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

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
    initial_sidebar_state="expanded",
)


# =====================================================
# DESIGN
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
    padding: 14px;
    border-radius: 12px;
}
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def find_column(df, names):
    for col in df.columns:
        if str(col).strip().lower() in names:
            return col
    return None


def to_dataframe(data):
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


def to_number(series):
    cleaned = (
        series.fillna("")
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"([-+]?\d*\.?\d+)")[0]
    )
    return pd.to_numeric(cleaned, errors="coerce")


def get_status_counts(df, status_col):
    statuses = (
        df[status_col]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.strip()
    )

    normal = statuses.isin([
        "within range",
        "within the stated range",
        "normal",
    ]).sum()

    high = statuses.isin([
        "above range",
        "above",
        "high",
        "above normal",
    ]).sum()

    low = statuses.isin([
        "below range",
        "below",
        "low",
        "below normal",
    ]).sum()

    unknown = len(df) - normal - high - low

    return int(normal), int(high), int(low), int(unknown)


def make_summary(df, test_col, result_col, unit_col,
                 reference_col, status_col):
    lines = [
        "AI MEDICAL REPORT EXPLAINER",
        "Laboratory Results Summary",
        "=" * 35,
        "",
        "This is an educational summary, not a diagnosis.",
        "",
    ]

    for _, row in df.iterrows():
        test = row.get(test_col, "Unknown") if test_col else "Unknown"
        result = row.get(result_col, "Not available") if result_col else "Not available"
        unit = row.get(unit_col, "") if unit_col else ""
        reference = row.get(reference_col, "") if reference_col else ""
        status = row.get(status_col, "Not assessed") if status_col else "Not assessed"

        lines.append(f"Test: {test}")
        lines.append(f"Result: {result} {unit}".strip())
        lines.append(f"Reference range: {reference or 'Not provided'}")
        lines.append(f"Status: {status}")
        lines.append("")

    return "\n".join(lines)


# =====================================================
# HEADER
# =====================================================

st.title("🩺 AI Medical Report Explainer")

st.write(
    "Upload a medical report in PDF or image format. "
    "View the extracted text, laboratory analysis, summary, graph, "
    "and downloadable results."
)

st.info(
    "Educational use only. This app cannot diagnose disease. "
    "Verify extracted values and interpretations with a qualified clinician."
)


# =====================================================
# UPLOAD PDF OR IMAGE
# =====================================================

uploaded_file = st.file_uploader(
    "📄 Upload a medical report",
    type=["pdf", "png", "jpg", "jpeg"],
)

if uploaded_file is not None:

    st.markdown("---")
    st.subheader("📁 Uploaded Report")
    st.write("File:", uploaded_file.name)

    # -------------------------------------------------
    # TEXT EXTRACTION
    # -------------------------------------------------

    try:
        with st.spinner("Extracting text..."):

            if uploaded_file.name.lower().endswith(".pdf"):
                extracted_text = extract_text_from_pdf(uploaded_file)
            else:
                extracted_text = extract_text_from_image(uploaded_file)

        extracted_text = str(extracted_text or "").strip()

    except Exception as error:
        st.error("Could not extract text from the file.")
        st.code(str(error))
        st.stop()

    st.subheader("📝 Extracted Report Text")

    if not extracted_text:
        st.error(
            "No text was extracted. For images, check OCR settings. "
            "For PDFs, try a clearer or text-based PDF."
        )
        st.stop()

    st.text_area(
        "Review the extracted text",
        value=extracted_text,
        height=220,
    )

    # -------------------------------------------------
    # ANALYSIS
    # -------------------------------------------------

    st.markdown("---")
    st.subheader("🔬 Laboratory Results Analysis")

    try:
        with st.spinner("Analyzing laboratory results..."):
            raw_results = analyze_report(extracted_text)

        results_df = to_dataframe(raw_results)

    except Exception as error:
        st.error("Laboratory analysis failed.")
        st.code(str(error))
        st.stop()

    if results_df.empty:
        st.warning(
            "No laboratory results were recognized. "
            "Check the extracted text and the test-name patterns in analyzer.py."
        )
        st.stop()

    # Find the columns produced by analyzer.py.
    test_col = find_column(
        results_df,
        {"test", "test name", "parameter", "lab test", "name"},
    )
    result_col = find_column(
        results_df,
        {"result", "value", "test result", "measured value"},
    )
    unit_col = find_column(
        results_df,
        {"unit", "units"},
    )
    reference_col = find_column(
        results_df,
        {"reference range", "reference", "normal range", "range"},
    )
    status_col = find_column(
        results_df,
        {"status", "interpretation", "flag"},
    )

    # -------------------------------------------------
    # TABLE
    # -------------------------------------------------

    st.dataframe(
        results_df,
        use_container_width=True,
        hide_index=True,
    )

    # -------------------------------------------------
    # SUMMARY CARDS
    # -------------------------------------------------

    st.markdown("---")
    st.subheader("📌 Summary Analysis")

    if status_col is not None:
        normal, high, low, unknown = get_status_counts(
            results_df, status_col
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Within Range", normal)
        c2.metric("Above Range", high)
        c3.metric("Below Range", low)
        c4.metric("Unclassified", unknown)

    else:
        normal = high = low = 0
        unknown = len(results_df)

        st.warning(
            "The analyzer did not return a Status column. "
            "Status summary counts cannot be calculated."
        )

    st.write(f"**Laboratory tests detected:** {len(results_df)}")

    if status_col is not None:
        st.write(
            f"**Summary:** {normal} within-range, {high} above-range, "
            f"{low} below-range, and {unknown} unclassified result(s)."
        )

    st.caption(
        "These counts reflect analyzer labels, not a medical diagnosis. "
        "Incorrect OCR, units, or reference ranges can produce incorrect labels."
    )

    # -------------------------------------------------
    # DOWNLOAD SUMMARY
    # -------------------------------------------------

    summary_text = make_summary(
        results_df,
        test_col,
        result_col,
        unit_col,
        reference_col,
        status_col,
    )

    st.download_button(
        label="⬇️ Download Summary (TXT)",
        data=summary_text,
        file_name="medical_report_summary.txt",
        mime="text/plain",
        use_container_width=True,
    )

    # -------------------------------------------------
    # DOWNLOAD RESULTS CSV
    # -------------------------------------------------

    csv_bytes = results_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="⬇️ Download Laboratory Results (CSV)",
        data=csv_bytes,
        file_name="laboratory_results.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # -------------------------------------------------
    # GRAPH AND PNG DOWNLOAD
    # -------------------------------------------------

    st.markdown("---")
    st.subheader("📊 Laboratory Results Graph")

    if test_col is None or result_col is None:
        st.warning(
            "Graph needs columns named Test and Result. "
            "Check the output column names in analyzer.py."
        )

    else:
        chart_df = results_df[[test_col, result_col]].copy()
        chart_df.columns = ["Test", "Original Result"]

        chart_df["Test"] = (
            chart_df["Test"].fillna("").astype(str).str.strip()
        )
        chart_df["Numeric Result"] = to_number(
            chart_df["Original Result"]
        )

        chart_df = chart_df[
            (chart_df["Test"] != "")
        ].dropna(subset=["Numeric Result"])

        chart_df = chart_df.drop_duplicates(
            subset=["Test"], keep="first"
        )

        if chart_df.empty:
            st.warning(
                "No numeric results could be plotted. "
                "Check the Result column returned by analyzer.py."
            )

        else:
            fig, ax = plt.subplots(figsize=(10, 5))

            ax.bar(
                chart_df["Test"],
                chart_df["Numeric Result"],
            )

            ax.set_title("Reported Laboratory Values")
            ax.set_xlabel("Laboratory Test")
            ax.set_ylabel("Reported Numeric Value")
            ax.tick_params(axis="x", labelrotation=30)
            ax.grid(axis="y", linestyle="--", alpha=0.3)

            fig.tight_layout()

            st.pyplot(fig, use_container_width=True)

            # Convert graph to PNG in memory.
            image_buffer = BytesIO()
            fig.savefig(
                image_buffer,
                format="png",
                dpi=200,
                bbox_inches="tight",
            )
            image_buffer.seek(0)

            st.download_button(
                label="⬇️ Download Graph (PNG)",
                data=image_buffer.getvalue(),
                file_name="laboratory_results_graph.png",
                mime="image/png",
                use_container_width=True,
            )

            plt.close(fig)

            st.caption(
                "Tests may use different units and scales. "
                "The graph displays reported numbers only and does not "
                "compare medical severity."
            )

    # -------------------------------------------------
    # AI EXPLANATION
    # -------------------------------------------------

    st.markdown("---")
    st.subheader("🤖 AI Explanation")

    if st.button("✨ Explain My Report", use_container_width=True):

        try:
            from ai_explainer import ai_explain_report

            with st.spinner("Generating an explanation..."):
                explanation = ai_explain_report(extracted_text)

            if explanation:
                st.markdown("### Explanation")
                st.write(explanation)
            else:
                st.warning("The AI explanation was empty.")

        except Exception as error:
            st.error(
                "AI explanation failed. Check ai_explainer.py "
                "and the API-key configuration."
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
