
import streamlit as st
import pandas as pd

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import explain_report
from report_generator import generate_pdf_report

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
)

st.markdown("""
<style>
.stApp { background: #0d111b; color: #f4f6fa; }
.block-container { max-width: 1200px; padding-top: 1.5rem; }
h1, h2, h3 { color: #f4f6fa; }
.hero {
    background: linear-gradient(120deg,#14283d,#075d68);
    padding: 24px;
    border-radius: 15px;
    margin-bottom: 22px;
}
.hero h1 { color: white; margin: 0; }
.hero p { color: #d8edf0; margin-bottom: 0; }
.panel {
    background: #191f2c;
    border: 1px solid #303849;
    border-radius: 12px;
    padding: 16px;
}
div[data-testid="stMetric"] {
    background: #191f2c;
    border: 1px solid #303849;
    padding: 14px;
    border-radius: 12px;
}
.stButton > button, .stDownloadButton > button {
    border-radius: 9px;
    min-height: 42px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🩺 AI Medical Report Explainer</h1>
  <p>Upload your report, review extracted results, and understand the information.</p>
</div>
""", unsafe_allow_html=True)

st.warning(
    "Educational use only. This application does not diagnose conditions "
    "or recommend treatment. Consult a qualified healthcare professional."
)

if "report_text" not in st.session_state:
    st.session_state.report_text = ""
if "report_name" not in st.session_state:
    st.session_state.report_name = ""
if "results_df" not in st.session_state:
    st.session_state.results_df = pd.DataFrame()
if "patient_fields" not in st.session_state:
    st.session_state.patient_fields = {}
if "explanation" not in st.session_state:
    st.session_state.explanation = ""

with st.sidebar:
    st.title("🩺 MediLens")
    page = st.radio(
        "Navigation",
        [
            "Report Dashboard",
            "Upload Report",
            "Laboratory Results",
            "AI Explanation",
            "Extracted Text",
        ],
    )
    st.divider()
    st.caption("Private report session · Educational prototype")

if page == "Upload Report":
    st.subheader("📄 Upload your medical report")

    uploaded = st.file_uploader(
        "Choose a PDF or image",
        type=["pdf", "png", "jpg", "jpeg"],
    )

    if uploaded:
        st.caption(f"Selected file: {uploaded.name}")

        if st.button("🔎 Analyze My Report", type="primary"):
            try:
                with st.spinner("Extracting report text..."):
                    if uploaded.name.lower().endswith(".pdf"):
                        text = extract_text_from_pdf(uploaded)
                    else:
                        text = extract_text_from_image(uploaded)

                if not text.strip():
                    st.error(
                        "No readable text was detected. Try a clearer image "
                        "or a text-based PDF."
                    )
                else:
                    # Reset and replace all report-specific data.
                    st.session_state.report_text = text
                    st.session_state.report_name = uploaded.name
                    st.session_state.results_df = analyze_report(text)
                    st.session_state.patient_fields = extract_patient_fields(text)
                    st.session_state.explanation = explain_report(
                        text,
                        st.session_state.results_df,
                        st.session_state.patient_fields,
                    )
                    st.success("Report analysis completed.")

            except Exception as error:
                st.error("Unable to process this report.")
                st.code(f"{type(error).__name__}: {error}")

elif page == "Report Dashboard":
    st.subheader("📋 Uploaded Report")

    if not st.session_state.report_text:
        st.info("Open Upload Report in the sidebar to get started.")
    else:
        st.write(f"**File name:** {st.session_state.report_name}")
        st.subheader("📝 Extracted Report Text")
        st.text_area(
            "Text detected in the report",
            st.session_state.report_text,
            height=160,
        )

        df = st.session_state.results_df
        fields = st.session_state.patient_fields

        st.divider()
        st.subheader("🔬 Laboratory Results Analysis")

        if df.empty:
            st.info("No supported laboratory result lines were recognized.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("📌 Results Summary")
        a, b, c = st.columns(3)
        a.metric("Tests recognized", len(df))
        b.metric("Patient details", sum(bool(v) for v in fields.values()))
        c.metric("Report text", f"{len(st.session_state.report_text)} chars")

        st.divider()
        st.subheader("📊 Laboratory Results Graph")

        if not df.empty:
            chart_data = df[["Test", "Result"]].copy()
            chart_data["Result"] = pd.to_numeric(
                chart_data["Result"].astype(str).str.replace(",", ""),
                errors="coerce",
            )
            chart_data = chart_data.dropna()

            if not chart_data.empty:
                st.bar_chart(chart_data.set_index("Test"))
                st.caption(
                    "Values are plotted as extracted. Different tests and units "
                    "are not directly comparable; this graph is not a health rating."
                )
            else:
                st.info("No numeric values were available to plot.")

        st.divider()
        st.subheader("✨ AI Explanation")
        st.write(st.session_state.explanation)

        try:
            pdf = generate_pdf_report(
                st.session_state.report_name,
                fields,
                df,
                st.session_state.explanation,
            )
            st.download_button(
                "📥 Download PDF Summary",
                data=pdf,
                file_name="medilens_report_summary.pdf",
                mime="application/pdf",
            )
        except Exception as error:
            st.error(f"PDF generation failed: {error}")

elif page == "Laboratory Results":
    st.subheader("🔬 Laboratory Results Analysis")
    if st.session_state.report_text:
        fields = st.session_state.patient_fields
        for label, value in fields.items():
            if value:
                st.write(f"**{label}:** {value}")

        df = st.session_state.results_df
        if df.empty:
            st.info("No supported results were recognized.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Upload a report first.")

elif page == "AI Explanation":
    st.subheader("✨ AI Explanation")
    if st.session_state.explanation:
        st.markdown(st.session_state.explanation)
    else:
        st.info("Upload a report first to generate its educational explanation.")

elif page == "Extracted Text":
    st.subheader("📝 Extracted Report Text")
    if st.session_state.report_text:
        st.text_area(
            "Text detected in the current report",
            st.session_state.report_text,
            height=400,
        )
        st.download_button(
            "Download text",
            st.session_state.report_text,
            file_name="extracted_report.txt",
            mime="text/plain",
        )
    else:
        st.info("Upload a report first.")

st.divider()
st.caption(
    "AI Medical Report Explainer | Educational project | "
    "Not a substitute for professional medical advice."
)
