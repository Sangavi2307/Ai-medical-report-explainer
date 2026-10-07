
import streamlit as st
from report_generator import generate_report

from extractor import extract_text_from_pdf
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from ocr_service import extract_text_from_image


st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺"
)


# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.title("🩺 AI Medical Report Explainer")

st.write(
    "Upload a medical report in PDF or image format "
    "to extract and explain laboratory results."
)

st.info(
    "ℹ️ This application provides informational explanations "
    "only and does not replace professional medical evaluation."
)


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

st.subheader("📄 Upload Medical Report")

uploaded_file = st.file_uploader(
    "Choose a PDF or image file",
    type=["pdf", "jpg", "jpeg", "png"]
)


# --------------------------------------------------
# PROCESS FILE
# --------------------------------------------------

if uploaded_file is not None:

    st.success(
        f"✅ Upload successful: {uploaded_file.name}"
    )

    try:

        file_name = uploaded_file.name.lower()


        # ------------------------------------------
        # PDF
        # ------------------------------------------

        if file_name.endswith(".pdf"):

            with st.spinner("📄 Extracting text from PDF..."):

                extracted_text = extract_text_from_pdf(
                    uploaded_file
                )


        # ------------------------------------------
        # IMAGE
        # ------------------------------------------

        else:

            with st.spinner("🔎 Reading text from image..."):

                extracted_text = extract_text_from_image(
                    uploaded_file
                )


        # ------------------------------------------
        # CHECK EXTRACTED TEXT
        # ------------------------------------------

        if not extracted_text.strip():

            st.error(
                "❌ No readable text was found in the uploaded file."
            )

            if file_name.endswith(".pdf"):

                st.info(
                    "The PDF may be scanned or image-based. "
                    "Try uploading the report as JPG or PNG."
                )

            else:

                st.info(
                    "Try uploading a clearer image with "
                    "good lighting and readable text."
                )

        else:

            # --------------------------------------
            # EXTRACTED TEXT
            # --------------------------------------

            st.subheader("📋 Extracted Report Text")

            st.text_area(
                "Report content",
                extracted_text,
                height=350
            )


            # --------------------------------------
            # ANALYZE BUTTON
            # --------------------------------------

            if st.button(
                "🔍 Analyze Report",
                use_container_width=True
            ):

                # ----------------------------------
                # LABORATORY ANALYSIS
                # ----------------------------------

                results = analyze_report(
                    extracted_text
                )


                # ----------------------------------
                # LABORATORY RESULTS
                # ----------------------------------

                st.subheader(
                    "🧪 Laboratory Results"
                )

                if not results.empty:

                    st.dataframe(
                        results,
                        use_container_width=True
                    )


                    # ------------------------------
                    # RESULT COUNTS
                    # ------------------------------

                    within = len(
                        results[
                            results["Status"]
                            == "Within Range"
                        ]
                    )

                    below = len(
                        results[
                            results["Status"]
                            == "Below Range"
                        ]
                    )

                    above = len(
                        results[
                            results["Status"]
                            == "Above Range"
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


                    # ----------------------------------
                    # SHORT SUMMARY
                    # ----------------------------------

                    st.subheader(
                        "📌 Short Summary"
                    )

                    total_tests = len(results)

                    summary_parts = []

                    summary_parts.append(
                        f"The report contains "
                        f"{total_tests} laboratory test(s)."
                    )

                    if within > 0:

                        summary_parts.append(
                            f"{within} result(s) are within "
                            f"the reference range shown "
                            f"on the report."
                        )

                    if below > 0:

                        summary_parts.append(
                            f"{below} result(s) are below "
                            f"the reference range shown "
                            f"on the report."
                        )

                    if above > 0:

                        summary_parts.append(
                            f"{above} result(s) are above "
                            f"the reference range shown "
                            f"on the report."
                        )

                    summary_text = " ".join(
                        summary_parts
                    )

                    st.write(summary_text)


                    # ----------------------------------
                    # AI EXPLANATION
                    # ----------------------------------

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
                 
                     # ----------------------------------
                     # DOWNLOAD REPORT
                    # ------------------------------
pdf_report = generate_report(
    results,
    ai_summary
)

st.download_button(
    label="📥 Download Report",
    data=pdf_report,
    file_name="medical_report_explanation.pdf",
    mime="application/pdf",
    use_container_width=True
)
Then
Save app.py
Commit to main
Wait for Streamlit to redeploy
Upload your PDF/JPG
Click 🔍 Analyze Report
Scroll down

You should see:

📥 Download Report

Clicking it should download a PDF containing the laboratory results, AI explanation, and disclaimer.


                    # ----------------------------------
                    # FINAL DISCLAIMER
                    # ----------------------------------

                    st.warning(
                        "⚠️ This explanation is for "
                        "informational and educational "
                        "purposes only. It does not provide "
                        "a medical diagnosis or treatment. "
                        "Actual medical results should be "
                        "discussed with a qualified "
                        "healthcare professional."
                    )


                else:

                    st.warning(
                        "No laboratory test results "
                        "were detected."
                    )

                    st.info(
                        "The text was extracted successfully, "
                        "but the laboratory values could not "
                        "be identified. This can happen when "
                        "the report layout or OCR text is "
                        "different from the supported format."
                    )


    except Exception as e:

        st.error(
            f"❌ Could not process the file: {e}"
        )
