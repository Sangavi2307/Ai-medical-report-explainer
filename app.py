
import streamlit as st
import pandas as pd

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report, extract_patient_fields
from ai_explainer import create_report_summary
from report_generator import generate_pdf_report


st.set_page_config(
    page_title="MediLens | Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp { background: #f3f7fb; }
.block-container { max-width: 1250px; padding-top: 1.5rem; }
.hero {
    background: linear-gradient(120deg, #103b55, #087e8b);
    padding: 28px;
    border-radius: 18px;
    color: white;
    margin-bottom: 22px;
}
.hero h1 { color: white; font-size: 36px; }
.hero p { color: #e2f6f6; font-size: 16px; }
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e0e8ef;
    padding: 16px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🩺 MediLens</h1>
    <p>Medical Report Explainer · Understand your report more clearly</p>
</div>
""", unsafe_allow_html=True)

st.warning(
    "Educational use only. MediLens does not diagnose conditions, "
    "recommend treatment, or replace professional medical advice."
)

if "report_text" not in st.session_state:
    st.session_state.report_text = ""
if "results_df" not in st.session_state:
    st.session_state.results_df = pd.DataFrame()
if "patient_fields" not in st.session_state:
    st.session_state.patient_fields = {}
if "report_summary" not in st.session_state:
    st.session_state.report_summary = ""
if "report_name" not in st.session_state:
    st.session_state.report_name = ""

with st.sidebar:
    st.title("MediLens")
    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Upload & Analyze",
            "Laboratory Results",
            "Report Summary",
            "Extracted Text",
        ],
    )
    st.divider()
    st.caption("Offline educational prototype")

if page == "Dashboard":
    st.subheader("Your report dashboard")
    st.write(
        "Upload a medical report to extract its text, inspect recognized "
        "laboratory results, and download a report summary."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Report loaded", "Yes" if st.session_state.report_text else "No")
    col2.metric("Recognized results", len(st.session_state.results_df))
    col3.metric(
        "Patient details",
        "Available" if st.session_state.patient_fields else "Not extracted",
    )

    st.markdown("### Workflow")
    st.markdown(
        "1. Upload a PDF or report image.\n"
        "2. Extract the report text.\n"
        "3. Review recognized laboratory results.\n"
        "4. Read the educational summary and download a PDF."
    )

    if st.session_state.report_text:
        st.info(f"Current report: {st.session_state.report_name}")

elif page == "Upload & Analyze":
    st.subheader("Upload a medical report")

    uploaded_file = st.file_uploader(
        "Choose a PDF, PNG, JPG, or JPEG",
        type=["pdf", "png", "jpg", "jpeg"],
    )

    if uploaded_file and st.button("Analyze Report", type="primary"):
        try:
            with st.spinner("Extracting and reviewing this report..."):
                name = uploaded_file.name
                if name.lower().endswith(".pdf"):
                    text = extract_text_from_pdf(uploaded_file)
                else:
                    text = extract_text_from_image(uploaded_file)

                if not text.strip():
                    st.error(
                        "No readable text was found. Try a clearer image "
                        "or a PDF with selectable text."
                    )
                else:
                    # Replace all report-specific state with this upload.
                    st.session_state.report_text = text
                    st.session_state.report_name = name
                    st.session_state.results_df = analyze_report(text)
                    st.session_state.patient_fields = extract_patient_fields(text)
                    st.session_state.report_summary = create_report_summary(
                        text,
                        st.session_state.results_df,
                        st.session_state.patient_fields,
                    )
                    st.success("Report processing completed.")

        except Exception as error:
            st.error("The report could not be processed.")
            st.code(f"{type(error).__name__}: {error}")

    if st.session_state.report_text:
        st.markdown("### Current report")
        st.write(st.session_state.report_name)
        st.metric("Extracted characters", len(st.session_state.report_text))
        st.info("Open Laboratory Results or Report Summary in the sidebar.")

elif page == "Laboratory Results":
    st.subheader("Laboratory Results")

    if not st.session_state.report_text:
        st.info("Upload a report first.")
    else:
        fields = st.session_state.patient_fields
        c1, c2, c3 = st.columns(3)
        c1.metric("Recognized tests", len(st.session_state.results_df))
        c2.metric("Patient", fields.get("Patient Name") or "Not extracted")
        c3.metric("Report date", fields.get("Report Date") or "Not extracted")

        df = st.session_state.results_df

        if df.empty:
            st.info(
                "No supported laboratory result lines were recognized. "
                "Review the Extracted Text page."
            )
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

            numeric = pd.to_numeric(df["Result"], errors="coerce")
            chart_df = pd.DataFrame({
                "Test": df["Test"],
                "Result": numeric,
            }).dropna()

            if not chart_df.empty:
                st.markdown("### Numeric result overview")
                st.caption(
                    "Values are shown as extracted. Different tests and units "
                    "may not be directly comparable."
                )
                st.bar_chart(chart_df.set_index("Test"))

            st.caption(
                "This prototype does not medically validate reference ranges "
                "or classify results as normal or abnormal."
            )

elif page == "Report Summary":
    st.subheader("Report Summary")

    if not st.session_state.report_text:
        st.info("Upload a report first.")
    else:
        fields = st.session_state.patient_fields

        st.markdown("### Extracted patient details")
        for key, value in fields.items():
            st.write(f"**{key}:** {value or 'Not extracted'}")

        st.markdown("### Educational overview")
        st.write(st.session_state.report_summary)

        if st.button("Prepare downloadable PDF"):
            try:
                pdf_bytes = generate_pdf_report(
                    report_name=st.session_state.report_name,
                    patient_fields=fields,
                    results_df=st.session_state.results_df,
                    summary=st.session_state.report_summary,
                )
                st.download_button(
                    "Download report summary (PDF)",
                    data=pdf_bytes,
                    file_name="medilens_report_summary.pdf",
                    mime="application/pdf",
                )
            except Exception as error:
                st.error("Could not generate the PDF.")
                st.code(f"{type(error).__name__}: {error}")

elif page == "Extracted Text":
    st.subheader("Extracted Report Text")

    if not st.session_state.report_text:
        st.info("Upload a report first.")
    else:
        st.text_area(
            "Text from the current report",
            value=st.session_state.report_text,
            height=400,
        )
        st.download_button(
            "Download extracted text",
            data=st.session_state.report_text,
            file_name="extracted_report.txt",
            mime="text/plain",
        )

st.divider()
st.caption(
    "MediLens is an educational prototype. Extraction may be incomplete. "
    "Confirm medical results and their interpretation with a qualified "
    "healthcare professional."
)
