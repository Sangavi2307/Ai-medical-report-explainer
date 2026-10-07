import streamlit as st

from extractor import extract_text_from_pdf
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from ocr_service import extract_text_from_image
from report_generator import generate_report


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide"
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f5f8fc;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .main-title {
        font-size: 38px;
        font-weight: 700;
        color: #123b63;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #60758a;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #123b63;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .info-card {
        background-color: white;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #dce6f0;
        box-shadow: 0 3px 12px rgba(20, 55, 90, 0.08);
        margin-bottom: 18px;
    }

    .info-card h3 {
        color: #123b63;
        margin-bottom: 8px;
    }

    .info-card p {
        color: #60758a;
        line-height: 1.6;
    }

    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #dce6f0;
        box-shadow: 0 3px 12px rgba(20, 55, 90, 0.08);
        text-align: center;
        min-height: 120px;
    }

    .metric-label {
        color: #60758a;
        font-size: 15px;
    }

    .metric-number {
        font-size: 32px;
        font-weight: 700;
        margin-top: 8px;
    }

    .blue-number {
        color: #1769aa;
    }

    .green-number {
        color: #159447;
    }

    .orange-number {
        color: #e38b18;
    }

    .red-number {
        color: #d63b3b;
    }

    [data-testid="stFileUploader"] {
        background-color: white;
        border: 2px dashed #8bb7dd;
        border-radius: 14px;
        padding: 15px;
    }

    .ai-box {
        background-color: white;
        border-left: 5px solid #1769aa;
        padding: 22px;
        border-radius: 12px;
        border-top: 1px solid #dce6f0;
        border-right: 1px solid #dce6f0;
        border-bottom: 1px solid #dce6f0;
        box-shadow: 0 3px 12px rgba(20, 55, 90, 0.08);
        line-height: 1.7;
        color: #34495e;
    }

    .medical-disclaimer {
        background-color: #fff7e6;
        border-left: 5px solid #f0a500;
        padding: 18px;
        border-radius: 10px;
        color: #684d00;
        margin-top: 20px;
        line-height: 1.6;
    }

    .footer {
        text-align: center;
        color: #718096;
        font-size: 13px;
        padding: 30px 0 10px 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <style>

    /* your existing CSS */

    .main-title {
        ...
    }

    .subtitle {
        ...
    }


    /* ADD THE NEW HERO CSS HERE */

    .hero-section {
        background: linear-gradient(
            135deg,
            #123b63,
            #1769aa
        );
        padding: 35px;
        border-radius: 22px;
        display: flex;
        align-items: center;
        gap: 25px;
        margin-bottom: 28px;
        box-shadow: 0 8px 25px rgba(20, 55, 90, 0.18);
    }

    .hero-icon {
        background: rgba(255, 255, 255, 0.15);
        width: 85px;
        height: 85px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 45px;
    }

    .hero-title {
        color: white;
        font-size: 36px;
        font-weight: 700;
    }

    .hero-subtitle {
        color: #e5f1fb;
        font-size: 17px;
        margin-top: 8px;
    }

    .hero-badges {
        display: flex;
        gap: 10px;
        margin-top: 18px;
        flex-wrap: wrap;
    }

    .hero-badges span {
        background: rgba(255, 255, 255, 0.14);
        color: white;
        padding: 7px 12px;
        border-radius: 20px;
        font-size: 13px;
    }


    /* your other existing CSS */


    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HOW IT WORKS
# =========================================================

st.markdown(
    '<div class="info-card">'
    '<h3>📋 How it works</h3>'
    '<p>Upload your medical report → Extract the report text → '
    'Identify laboratory results → Get an educational AI explanation.</p>'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# UPLOAD
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
# FILE PROCESSING
# =========================================================

if uploaded_file is not None:

    st.success(
        "✅ Upload successful: " + uploaded_file.name
    )

    file_name = uploaded_file.name.lower()

    try:

        # -------------------------------------------------
        # PDF
        # -------------------------------------------------

        if file_name.endswith(".pdf"):

            with st.spinner("📄 Extracting text from PDF..."):

                extracted_text = extract_text_from_pdf(
                    uploaded_file
                )

        # -------------------------------------------------
        # IMAGE
        # -------------------------------------------------

        else:

            with st.spinner("🔎 Reading text from image..."):

                extracted_text = extract_text_from_image(
                    uploaded_file
                )


        # -------------------------------------------------
        # NO TEXT
        # -------------------------------------------------

        if not extracted_text or not extracted_text.strip():

            st.error(
                "❌ No readable text was found in the uploaded file."
            )

            if file_name.endswith(".pdf"):

                st.info(
                    "This PDF may be scanned or image-based. "
                    "Try uploading the report as JPG or PNG."
                )

            else:

                st.info(
                    "Try uploading a clearer image with good lighting "
                    "and readable text."
                )


        else:

            # -------------------------------------------------
            # EXTRACTED TEXT
            # -------------------------------------------------

            st.markdown(
                '<div class="section-title">📋 Extracted Report Text</div>',
                unsafe_allow_html=True
            )

            with st.expander(
                "View extracted report text",
                expanded=True
            ):

                st.text_area(
                    "Report text",
                    extracted_text,
                    height=300,
                    label_visibility="collapsed"
                )


            # -------------------------------------------------
            # ANALYZE BUTTON
            # -------------------------------------------------

            analyze_clicked = st.button(
                "🔍 Analyze Report",
                use_container_width=True
            )


            if analyze_clicked:

                with st.spinner(
                    "🔬 Analyzing laboratory results..."
                ):

                    results = analyze_report(
                        extracted_text
                    )


                # -------------------------------------------------
                # RESULTS
                # -------------------------------------------------

                st.markdown(
                    '<div class="section-title">🧪 Laboratory Results</div>',
                    unsafe_allow_html=True
                )


                if not results.empty:

                    total_tests = len(results)

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


                    # -------------------------------------------------
                    # DASHBOARD CARDS
                    # -------------------------------------------------

                    col1, col2, col3, col4 = st.columns(4)


                    with col1:

                        st.markdown(
                            '<div class="metric-card">'
                            '<div class="metric-label">🧪 Total Tests</div>'
                            '<div class="metric-number blue-number">'
                            + str(total_tests) +
                            '</div>'
                            '</div>',
                            unsafe_allow_html=True
                        )


                    with col2:

                        st.markdown(
                            '<div class="metric-card">'
                            '<div class="metric-label">🟢 Within Range</div>'
                            '<div class="metric-number green-number">'
                            + str(within) +
                            '</div>'
                            '</div>',
                            unsafe_allow_html=True
                        )


                    with col3:

                        st.markdown(
                            '<div class="metric-card">'
                            '<div class="metric-label">🟠 Below Range</div>'
                            '<div class="metric-number orange-number">'
                            + str(below) +
                            '</div>'
                            '</div>',
                            unsafe_allow_html=True
                        )


                    with col4:

                        st.markdown(
                            '<div class="metric-card">'
                            '<div class="metric-label">🔴 Above Range</div>'
                            '<div class="metric-number red-number">'
                            + str(above) +
                            '</div>'
                            '</div>',
                            unsafe_allow_html=True
                        )


                    # -------------------------------------------------
                    # RESULT TABLE
                    # -------------------------------------------------

                    st.markdown(
                        '<div class="section-title">📊 Detailed Results</div>',
                        unsafe_allow_html=True
                    )


                    def highlight_status(value):

                        if value == "Within Range":

                            return (
                                "background-color: #e8f7ee;"
                                "color: #138a42;"
                                "font-weight: 600;"
                            )

                        if value == "Below Range":

                            return (
                                "background-color: #fff2df;"
                                "color: #d47700;"
                                "font-weight: 600;"
                            )

                        if value == "Above Range":

                            return (
                                "background-color: #fde8e8;"
                                "color: #c62828;"
                                "font-weight: 600;"
                            )

                        return ""


                    styled_results = results.style.map(
                        highlight_status,
                        subset=["Status"]
                    )


                    st.dataframe(
                        styled_results,
                        use_container_width=True,
                        hide_index=True
                    )


                    # -------------------------------------------------
                    # SUMMARY
                    # -------------------------------------------------

                    st.markdown(
                        '<div class="section-title">📌 Result Summary</div>',
                        unsafe_allow_html=True
                    )


                    summary_text = (
                        "The report contains "
                        + str(total_tests)
                        + " laboratory test(s). "
                    )


                    if within > 0:

                        summary_text += (
                            str(within)
                            + " result(s) are within the reference "
                            "range shown on the report. "
                        )


                    if below > 0:

                        summary_text += (
                            str(below)
                            + " result(s) are below the reference "
                            "range shown on the report. "
                        )


                    if above > 0:

                        summary_text += (
                            str(above)
                            + " result(s) are above the reference "
                            "range shown on the report."
                        )


                    st.markdown(
                        '<div class="info-card">'
                        '<p>'
                        + summary_text +
                        '</p>'
                        '</div>',
                        unsafe_allow_html=True
                    )


                    # -------------------------------------------------
                    # AI EXPLANATION
                    # -------------------------------------------------

                    st.markdown(
                        '<div class="section-title">🤖 AI Educational Explanation</div>',
                        unsafe_allow_html=True
                    )


                    with st.spinner(
                        "🤖 AI is preparing the explanation..."
                    ):

                        ai_summary = ai_explain_report(
                            extracted_text
                        )


                    st.markdown(
                        '<div class="ai-box">'
                        + ai_summary.replace("\n", "<br>")
                        + '</div>',
                        unsafe_allow_html=True
                    )


                    # -------------------------------------------------
                    # DOWNLOAD
                    # -------------------------------------------------

                    st.markdown(
                        '<div class="section-title">📥 Download Report</div>',
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
                            file_name="medical_report_explanation.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )


                    except Exception as error:

                        st.error(
                            "❌ Could not create the PDF report: "
                            + str(error)
                        )


                    # -------------------------------------------------
                    # DISCLAIMER
                    # -------------------------------------------------

                    st.markdown(
                        '<div class="medical-disclaimer">'
                        '<b>⚠️ Important Medical Disclaimer</b>'
                        '<br><br>'
                        'This application provides informational and '
                        'educational explanations only.'
                        '<br><br>'
                        'It does not provide a medical diagnosis or treatment.'
                        '<br><br>'
                        'Laboratory results should be interpreted by a '
                        'qualified healthcare professional together with '
                        'symptoms, medical history, medications and other '
                        'clinical information.'
                        '</div>',
                        unsafe_allow_html=True
                    )


                else:

                    st.warning(
                        "⚠️ No laboratory test results were detected."
                    )

                    st.info(
                        "The report text was extracted successfully, "
                        "but laboratory values could not be identified. "
                        "This may happen when the report layout or OCR "
                        "text is different from the supported format."
                    )


    except Exception as error:

        st.error(
            "❌ Could not process the file: "
            + str(error)
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="footer">'
    '🩺 AI Medical Report Explainer | '
    'Educational Use Only | '
    'Not a Substitute for Professional Medical Evaluation'
    '</div>',
    unsafe_allow_html=True
            )
