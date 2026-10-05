import streamlit as st
from extractor import extract_text_from_pdf
from analyzer import analyze_report

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺"
)

st.title("🩺 AI Medical Report Explainer")

st.write(
    "Upload a medical report and analyze the test results."
)

st.info(
    "⚠️ Educational purpose only. This application does not "
    "provide diagnosis or treatment."
)

st.subheader("📄 Upload Medical Report")

uploaded_file = st.file_uploader(
    "Choose a PDF medical report",
    type=["pdf"]
)

if uploaded_file is not None:

    st.success(
        f"✅ File uploaded: {uploaded_file.name}"
    )

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(
        uploaded_file
    )

    if extracted_text.strip():

        st.subheader("📋 Extracted Report Text")

        st.text_area(
            "Report content",
            extracted_text,
            height=300
        )

        # Analyze extracted text
        if st.button("🔍 Analyze Report"):

            results = analyze_report(
                extracted_text
            )

            if not results.empty:

                st.subheader("📊 Analysis Results")

                st.dataframe(
                    results,
                    use_container_width=True
                )

                within = len(
                    results[
                        results["Status"] == "Within Range"
                    ]
                )

                below = len(
                    results[
                        results["Status"] == "Below Range"
                    ]
                )

                above = len(
                    results[
                        results["Status"] == "Above Range"
                    ]
                )

                st.subheader("📌 Summary")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "🟢 Within Range",
                    within
                )

                col2.metric(
                    "🟠 Below Range",
                    below
                )

                col3.metric(
                    "🔴 Above Range",
                    above

                )

            else:

                st.warning(
                    "No test results could be detected "
                    "from the extracted text."
                )

    else:

        st.warning(
            "No text could be extracted from this PDF. "
            "This may be a scanned/image-based PDF. "
            "We will add OCR support later."
        )
