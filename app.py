import streamlit as st

from extractor import extract_text_from_pdf
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from ocr_service import extract_text_from_image
from report_generator import generate_report


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide"
)


# =========================================================
# CUSTOM UI STYLE
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #666666;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 10px;
    }

    .info-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #dddddd;
        margin-bottom: 15px;
    }

    .disclaimer {
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🩺 AI Medical Report Explainer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Upload a medical report and understand laboratory results in simple language.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# INFORMATION
# =========================================================

st.info(
    "ℹ️ This application provides informational explanations "
    "only and does not replace professional medical evaluation."
)


# =========================================================
# UPLOAD SECTION
# =========================================================

st.markdown(
    '<div class="section-title">📄 Upload Medical Report</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "Choose a PDF or image file",
    type=["pdf", "jpg", "jpeg", "png"],
    help="Supported formats: PDF, JPG, JPEG and PNG"
)


# =========================================================
# PROCESS FILE
# =========================================================

if uploaded_file is not None:

    st.success(
        f"✅ Upload successful: {uploaded_file.name}"
    )

    try:

        file_name = uploaded_file.name.lower()

        # =================================================
        # PDF
        # =================================================

        if file_name.endswith(".pdf"):

            with st.spinner(
                "📄 Extracting text from PDF..."
            ):

                extracted_text = extract_text_from_pdf(
                    uploaded_file
                )

        # =================================================
        # IMAGE
        # =================================================

        else:

            with st.spinner(
                "🔎 Reading text from image..."
            ):

                extracted_text = extract_text_from_image(
                    uploaded_file
                )


        # =================================================
        # CHECK TEXT
        # =================================================

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

            # =================================================
            # EXTRACTED TEXT
            # =================================================

            st.markdown(
                '<div class="section-title">📋 Extracted Report Text</div>',
                unsafe_allow_html=True
            )

            st.text_area(
                "Report content",
                extracted_text,
                height=350
            )


            # =================================================
            # ANALYZE BUTTON
            # =================================================

            if st.button(
                "🔍 Analyze Report",
                use_container_width=True
            ):

                # =================================================
                # ANALYZE
                # =================================================

                results = analyze_report(
                    extracted_text
                )


                # =================================================
                # LABORATORY RESULTS
                # =================================================

                st.markdown(
                    '<div class="section-title">'
                    '🧪 Laboratory Results'
                    '</div>',
                    unsafe_allow_html=True
                )


                if not results.empty:

                    # ---------------------------------------------
                    # RESULT TABLE
                    # ---------------------------------------------

                    st.dataframe(
                        results,
                        use_container_width=True,
                        hide_index=True
                    )


                    # =================================================
                    # RESULT COUNTS
                    # =================================================

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


                    st.markdown(
                        '<div class="section-title">'
                        '📊 Result Summary'
                        '</div>',
                        unsafe_allow_html=True
                    )


                    col1, col2, col3 = st.columns(3)


                    with col1:

                        st.metric(
                            "🟢 Within Range",
                            within
                        )


                    with col2:

                        st.metric(
                            "🟠 Below Range",
                            below
                        )


                    with col3:

                        st.metric(
                            "🔴 Above Range",
                            above
                        )


                    # =================================================
                    # SHORT SUMMARY
                    # =================================================

                    st.markdown(
                        '<div class="section-title">'
                        '📌 Short Summary'
                        '</div>',
                        unsafe_allow_html=True
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

                    st.write(
                        summary_text
                    )


                    # =================================================
                    # AI EXPLANATION
                    # =================================================

                    st.markdown(
                        '<div class="section-title">'
                        '🤖 AI Educational Explanation'
                        '</div>',
                        unsafe_allow_html=True
                    )


                    with st.spinner(
                        "AI is analyzing the report..."
                    ):

                        ai_summary = ai_explain_report(
                            extracted_text
                        )


                    st.markdown(
                        ai_summary
                    )


                    # =================================================
                    # DOWNLOAD REPORT
                    # =================================================

                    st.markdown(
                        '<div class="section-title">'
                        '📥 Download Report'
                        '</div>',
                        unsafe_allow_html=True
                    )


                    try:

                        pdf_report = generate_report(
                            results,
                            ai_summary
                        )


                        st.download_button(
                            label="📥 Download Medical Report",
                            data=pdf_report,
                            file_name=(
                                "medical_report_explanation.pdf"
                            ),
                            mime="application/pdf",
                            use_container_width=True
                        )


                    except Exception as e:

                        st.error(
                            f"❌ Could not create the PDF report: {e}"
                        )


                    # =================================================
                    # DISCLAIMER
                    # =================================================

                    st.markdown(
                        '<div class="section-title">'
                        '⚠️ Important Medical Information'
                        '</div>',
                        unsafe_allow_html=True
                    )


                    st.warning(
                        "This explanation is for informational "
                        "and educational purposes only. It does "
                        "not provide a medical diagnosis or "
                        "treatment. Actual medical results should "
                        "be discussed with a qualified healthcare "
                        "professional."
                    )


                else:

                    # =================================================
                    # NO RESULTS
                    # =================================================

                    st.warning(
                        "No laboratory test results were detected."
                    )

                    st.info(
                        "The text was extracted successfully, "
                        "but the laboratory values could not be "
                        "identified. This can happen when the "
                        "report layout or OCR text is different "
                        "from the supported format."
                    )


    except Exception as e:

        st.error(
            f"❌ Could not process the file: {e}"
        )
        
