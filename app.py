import pandas as pd
import plotly.express as px
import streamlit as st

from analyzer import (
    identify_report_type,
    extract_patient_fields,
    analyze_report,
    summarize_document,
)
from extractor import extract_text_from_pdf
from ocr_service import (
    extract_text_from_image,
    extract_text_from_scanned_pdf,
)
from report_generator import generate_pdf_report


# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="MediLens | Medical Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------- DESIGN ----------------

st.markdown("""
<style>
:root {
    --navy: #16324f;
    --teal: #147d92;
    --muted: #60748a;
}

.stApp {
    background: #f4f7fb;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
}

.hero {
    padding: 28px 30px;
    border-radius: 18px;
    background: linear-gradient(120deg, #16324f, #147d92);
    color: white;
    margin-bottom: 20px;
}

.hero h1 {
    color: white;
    margin: 0;
    font-size: 2.2rem;
}

.hero p {
    color: #e6f4f7;
    margin: 8px 0 0 0;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e0e8f0;
    border-radius: 14px;
    padding: 15px;
}

div[data-testid="stMetricLabel"] {
    color: #60748a;
}

div.stButton > button[kind="primary"] {
    background: #147d92;
    color: white;
    border: 0;
    border-radius: 9px;
    font-weight: 600;
}

div[data-testid="stFileUploader"] {
    background: white;
    border-radius: 12px;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ---------------- STATE ----------------

if "report_data" not in st.session_state:
    st.session_state.report_data = None


# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>🩺 MediLens</h1>
    <p>Medical Report Explainer · Structured extraction · Clear summaries</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "Educational prototype only. This application does not diagnose diseases "
    "or recommend treatment. Always verify extracted information against the "
    "original report and consult a qualified healthcare professional."
)


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("## MediLens")
    st.caption("Medical report workspace")

    page = st.radio(
        "Workspace",
        [
            "Overview",
            "Upload Report",
            "Laboratory Results",
            "Report Explanation",
            "Extracted Text",
        ],
    )

    st.divider()

    st.caption("Supported formats")
    st.write("PDF · PNG · JPG · JPEG")

    if st.button("Clear Loaded Report", use_container_width=True):
        st.session_state.report_data = None
        st.rerun()


# ---------------- UPLOAD ----------------

if page == "Upload Report":
    st.title("Upload a medical report")
    st.write(
        "Process one report at a time. The application extracts text and "
        "identifies information it can recognize."
    )

    uploaded_file = st.file_uploader(
        "Select a report",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Clear, readable documents provide better extraction results.",
    )

    if uploaded_file:
        st.success(f"Selected: {uploaded_file.name}")

        if st.button("Process Report", type="primary"):
            try:
                with st.spinner("Extracting text from your report..."):
                    if uploaded_file.name.lower().endswith(".pdf"):
                        # First attempt ordinary PDF text extraction.
                        text = extract_text_from_pdf(uploaded_file)

                        # If the PDF is scanned, use OCR on its pages.
                        if len(text.strip()) < 20:
                            text = extract_text_from_scanned_pdf(uploaded_file)
                    else:
                        text = extract_text_from_image(uploaded_file)

                if not text.strip():
                    st.error(
                        "No readable text was detected. Try a clearer image "
                        "or a different PDF."
                    )
                else:
                    with st.spinner("Organizing recognized information..."):
                        report_type = identify_report_type(text)
                        patient = extract_patient_fields(text)
                        results = analyze_report(text)
                        document_summary = summarize_document(
                            text,
                            report_type,
                        )

                        if results.empty:
                            summary = [
                                f"Detected category: {report_type}.",
                                "No structured laboratory values were recognized.",
                                "Review the extracted sections and original document.",
                                "No diagnosis has been generated.",
                            ]
                        else:
                            status_counts = results["Status"].value_counts()

                            summary = [
                                f"Detected category: {report_type}.",
                                f"Recognized laboratory values: {len(results)}.",
                                "Extracted status counts: "
                                + ", ".join(
                                    f"{status}: {count}"
                                    for status, count in status_counts.items()
                                ),
                                "Comparisons are made only against ranges "
                                "recognized in the extracted text.",
                                "Verify values, units, and ranges against "
                                "the original report.",
                            ]

                        st.session_state.report_data = {
                            "name": uploaded_file.name,
                            "text": text,
                            "type": report_type,
                            "patient": patient,
                            "results": results,
                            "summary": summary,
                            "document_summary": document_summary,
                        }

                    st.success("Report processing completed.")
                    st.info(
                        "Open Overview to review the results, or Report "
                        "Explanation to see extracted key sections."
                    )

            except Exception as error:
                st.error("The report could not be processed.")
                st.code(f"{type(error).__name__}: {error}")


# ---------------- REPORT PAGES ----------------

data = st.session_state.report_data


if page != "Upload Report":
    if data is None:
        st.title("Welcome to MediLens")
        st.write(
            "Upload a medical report to start extracting and reviewing "
            "its contents."
        )

        st.markdown("""
        ### Workspace features

        - PDF and image text extraction
        - Basic medical report categorization
        - Recognized laboratory values and reference-range comparisons
        - Dashboard charts and result tables
        - PDF summary and CSV export
        """)

        st.warning(
            "The application has no report loaded yet. Select **Upload Report** "
            "from the sidebar to begin."
        )

    else:
        results = data["results"]

        if page == "Overview":
            st.title("Report Overview")
            st.caption(f"File: {data['name']}")

            first, second, third = st.columns(3)

            first.metric("Detected Category", data["type"])
            second.metric("Lab Values Recognized", len(results))

            outside = 0
            if not results.empty:
                outside = int(
                    results["Status"].isin(
                        ["Below range", "Above range"]
                    ).sum()
                )

            third.metric("Outside Extracted Range", outside)

            st.subheader("Patient Information")

            patient_df = pd.DataFrame(
                [
                    {"Field": field, "Value": value}
                    for field, value in data["patient"].items()
                ]
            )

            st.dataframe(
                patient_df,
                use_container_width=True,
                hide_index=True,
            )

            st.subheader("Processing Summary")

            for item in data["summary"]:
                st.write("•", item)

            if not results.empty:
                st.subheader("Laboratory Status Distribution")

                counts = (
                    results["Status"]
                    .value_counts()
                    .rename_axis("Status")
                    .reset_index(name="Count")
                )

                fig = px.bar(
                    counts,
                    x="Status",
                    y="Count",
                    title="Recognized status counts",
                    color="Status",
                    color_discrete_sequence=[
                        "#147d92",
                        "#e5a443",
                        "#d96c6c",
                        "#7d8ca3",
                    ],
                )

                fig.update_layout(
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    font_color="#16324f",
                    showlegend=False,
                )

                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Recognized Results")

                st.dataframe(
                    results,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info(
                    "No structured laboratory results were recognized. "
                    "Imaging, ECG, prescription, and discharge documents "
                    "may contain useful text without laboratory tables."
                )

        elif page == "Laboratory Results":
            st.title("Laboratory Results")

            if results.empty:
                st.info(
                    "No structured laboratory values were recognized. "
                    "Check the extracted text and compare it with the original."
                )
            else:
                st.dataframe(
                    results,
                    use_container_width=True,
                    hide_index=True,
                )

                st.download_button(
                    "Download laboratory results (CSV)",
                    data=results.to_csv(index=False).encode("utf-8"),
                    file_name="medilens_laboratory_results.csv",
                    mime="text/csv",
                    type="primary",
                )

        elif page == "Report Explanation":
            st.title("Report Explanation")

            st.subheader("Detected report category")
            st.write(data["type"])

            st.subheader("Key extracted sections")

            sections = data["document_summary"]["Key Sections"]

            if sections:
                for section in sections:
                    st.markdown(f"- {section}")
            else:
                st.info(
                    "No key sections were recognized. Review the extracted text."
                )

            if not results.empty:
                st.subheader("Laboratory explanations")

                for _, row in results.iterrows():
                    with st.expander(str(row["Test"])):
                        st.write(
                            f"**Extracted result:** {row['Result']} {row['Unit']}"
                        )
                        st.write(
                            f"**Extracted reference range:** "
                            f"{row['Reference Range']}"
                        )
                        st.write(f"**Rule-based status:** {row['Status']}")
                        st.write(row["Explanation"])

            st.caption(
                "These descriptions explain common test purposes. They are "
                "not patient-specific medical advice."
            )

        elif page == "Extracted Text":
            st.title("Extracted Report Text")

            st.write(
                "Check the extracted content carefully. OCR can misread "
                "numbers, decimal points, units, names, and medical terms."
            )

            st.text_area(
                "Extracted content",
                value=data["text"],
                height=420,
            )

            st.download_button(
                "Download extracted text (TXT)",
                data=data["text"].encode("utf-8"),
                file_name="medilens_extracted_text.txt",
                mime="text/plain",
            )

        # ---------------- EXPORTS ----------------

        st.divider()
        st.subheader("Export")

        export_col1, export_col2 = st.columns(2)

        with export_col1:
            if not results.empty:
                st.download_button(
                    "Download CSV",
                    data=results.to_csv(index=False).encode("utf-8"),
                    file_name="medilens_results.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            else:
                st.caption("CSV export is available when lab values are recognized.")

        with export_col2:
            try:
                pdf_bytes = generate_pdf_report(
                    report_name=data["name"],
                    report_type=data["type"],
                    patient_fields=data["patient"],
                    results_df=results,
                    summary=data["summary"],
                )

                st.download_button(
                    "Download PDF Summary",
                    data=pdf_bytes,
                    file_name="medilens_report_summary.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            except Exception as error:
                st.error("PDF generation failed.")
                st.code(f"{type(error).__name__}: {error}")


# ---------------- FOOTER ----------------

st.divider()
st.caption(
    "MediLens · Educational prototype · Not a medical device or a substitute "
    "for professional clinical interpretation."
)
