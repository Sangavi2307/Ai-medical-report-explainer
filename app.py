import streamlit as st
from extractor import extract_text_from_pdf
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from ocr_service import extract_text_from_image


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
    "Choose a PDF or image file",
    type=["pdf", "jpg", "jpeg", "png"]
)

if uploaded_file is not None:

    st.success(
        f"✅ Upload successful: {uploaded_file.name}"
    )

    try:

        file_type = uploaded_file.name.lower()

        # PDF extraction
        if file_type.endswith(".pdf"):

            extracted_text = extract_text_from_pdf(
                uploaded_file
            )

        # Image OCR extraction
        else:

            with st.spinner("🔎 Reading text from the image..."):

                extracted_text = extract_text_from_image(
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

                    st.subheader(
                        "🤖 AI Educational Explanation"
                    )

                    with st.spinner(
                        "AI is analyzing the report..."
                    ):

                        ai_summary = ai_explain_report(
                            extracted_text
                        )

                    st.markdown(ai_summary)

                else:

                    st.warning(
                        "No laboratory test results were detected."
                    )

        else:

            st.warning(
                "The file was uploaded successfully, "
                "but no text was found."
            )

            if not file_type.endswith(".pdf"):

                st.info(
                    "OCR could not detect readable text in this image. "
                    "Try uploading a clearer image."
                )

            else:

                st.info(
                    "This PDF may be scanned or image-based. "
                    "Try uploading the report as a JPG or PNG image."
                )

    except Exception as e:

        st.error(
            f"Could not process the file: {e}"
        )
