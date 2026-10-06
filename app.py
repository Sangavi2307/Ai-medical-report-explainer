import streamlit as st
from extractor import extract_text_from_pdf
from analyzer import analyze_report


st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺"
)

st.title("🩺 AI Medical Report Explainer")

st.write(
    "Upload a medical report and extract and analyze laboratory results."
)

st.info(
    "This application provides informational explanations "
    "and does not replace professional medical evaluation."
)

st.subheader("📄 Upload Medical Report")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"]
)

if uploaded_file is not None:

    st.success(
        f"✅ Upload successful: {uploaded_file.name}"
    )

    try:

        extracted_text = extract_text_from_pdf(
            uploaded_file
        )

        if extracted_text.strip():

            st.subheader("📋 Extracted Report Text")

            st.text_area(
                "Report content",
                extracted_text,
                height=400
            )

            st.subheader("📊 Medical Test Analysis")

            if st.button("🔍 Analyze Report"):

                results = analyze_report(
                    extracted_text
                )

                if not results.empty:

                    st.dataframe(
                        results,
                        use_container_width=True
                    )

                    st.subheader("📌 Summary")

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
                        "No laboratory test results were detected."
                    )

        else:

            st.warning(
                "The PDF was uploaded successfully, "
                "but no text was found."
            )

            st.info(
                "This may be a scanned or image-based PDF. "
                "OCR support will be added later."
            )

    except Exception as e:

        st.error(
            f"Could not process the PDF: {e}"
        )
