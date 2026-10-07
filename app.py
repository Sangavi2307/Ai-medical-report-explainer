import streamlit as st
import pandas as pd

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
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ---------- MAIN BACKGROUND ---------- */

    .stApp {
        background-color: #f5f8fc;
    }

    /* ---------- SIDEBAR ---------- */

    [data-testid="stSidebar"] {
        background-color: #0f2747;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    /* ---------- MAIN TITLE ---------- */

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

    /* ---------- SECTION TITLE ---------- */

    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #123b63;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    /* ---------- INFORMATION CARD ---------- */

    .info-card {
        background: white;
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
        margin: 0;
    }

    /* ---------- METRIC CARDS ---------- */

    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #dce6f0;
        box-shadow: 0 3px 12px rgba(20, 55, 90, 0.08);
        text-align: center;
        min-height: 120px;
    }

    .metric-number {
        font-size: 32px;
        font-weight: 700;
        margin-top: 5px;
    }

    .metric-label {
        font-size: 15px;
        color: #60758a;
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

    .blue-number {
        color: #1769aa;
    }

    /* ---------- UPLOAD AREA ---------- */

    [data-testid="stFileUploader"] {
        background-color: white;
        border: 2px dashed #8bb7dd;
        border-radius: 14px;
        padding: 15px;
    }

    /* ---------- BUTTON ---------- */

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: none;
        background-color: #1769aa;
        color: white;
        font-size: 16px;
        font-weight: 600;
        padding: 12px;
    }

    .stButton > button:hover {
        background-color: #0f568e;
        color: white;
    }

    /* ---------- RESULT STATUS ---------- */

    .status-within {
        background-color: #e8f7ee;
        color: #138a42;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    .status-below {
        background-color: #fff2df;
        color: #d47700;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    .status-above {
        background-color: #fde8e8;
        color: #c62828;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
    }

    /* ---------- AI BOX ---------- */

    .ai-box {
        background: white;
        border-left: 5px solid #1769aa;
        padding: 22px;
        border-radius: 12px;
        border-top: 1px solid #dce6f0;
        border-right: 1px solid #dce6f0;
        border-bottom: 1px solid #dce6f0;
        box-shadow: 0 3px 12px rgba(20, 55, 90, 0.08);
    }

    /* ---------- DISCLAIMER ---------- */

    .medical-disclaimer {
        background-color: #fff7e6;
        border-left: 5px solid #f0a500;
        padding: 18px;
        border-radius: 10px;
        color: #684d00;
        margin-top: 20px;
    }

    /* ---------- FOOTER ---------- */

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
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:15px 0;">
            <div style="font-size:55px;">🩺</div>
            <h2>Medical Report</h2>
            <h2>Explainer</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### 📌 About")

    st.write(
        "This application extracts laboratory information "
        "from medical reports and provides educational "
        "explanations."
    )

    st.markdown("---")

    st.markdown("### 📄 Supported Files")

    st.write("✅ PDF")
    st.write("✅ JPG")
    st.write("✅ JPEG")
    st.write("✅ PNG")

    st.markdown("---")

    st.markdown("### 🔐 Privacy")

    st.write(
        "Upload reports only for testing or demonstration. "
        "Avoid uploading sensitive personal medical documents "
        "unless appropriate safeguards are in place."
    )

    st.markdown("---")

    st.markdown("### ⚠️ Important")

    st.write(
        "This application is for educational and informational "
        "purposes only."
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🩺 AI Medical Report Explainer</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Upload a medical report and understand the laboratory
    results in a simple and easy-to-read format.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# INTRO CARD
# =========================================================

st.markdown(
    """
    <div class="info-card">
        <h3>📋 How it works</h3>
        <p>
        Upload your medical report → Extract the report text →
        Identify laboratory results → Get an educational AI explanation.
        </p>
    </div>
    """,
    unsafe_allow_html=True
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
# FILE PROCESSING
# =========================================================

if uploaded_file is not None:

    st.success(
        f"✅ Upload successful: {uploaded_file.name}"
    )

    file_name = uploaded_file.name.lower()

    # -----------------------------------------------------
    # PDF EXTRACTION
    # -----------------------------------------------------

    try:

        if file_name.endswith(".pdf"):

            with st.spinner(
                "📄 Extracting text from PDF..."
            ):

                extracted_text = extract_text_from_pdf(
                    uploaded_file
                )

        # -------------------------------------------------
        # IMAGE OCR
        # -------------------------------------------------

        else:

            with st.spinner(
                "🔎 Reading text from image..."
            ):

                extracted_text = extract_text_from_image(
                    uploaded_file
                )


        # =================================================
        # CHECK EXTRACTED TEXT
        # =================================================

        if not extracted_text or not extracted_text.strip():

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
                    "Try uploading a clearer image with good "
                    "lighting and readable text."
                )


        else:

            # =============================================
            # EXTRACTED TEXT
            # =============================================

            st.markdown(
                '<div class="section-title">📋 Extracted Report Text</div>',
                unsafe_allow_html=True
            )

            with st.expander(
                "View extracted report text",
                expanded=True
            ):

                st.text_area(
                    "Report content",
                    extracted_text,
                    height=300,
                    label_visibility="collapsed"
                )


            # =============================================
            # ANALYZE BUTTON
            # =============================================

            st.markdown("")

            analyze_clicked = st.button(
                "🔍 Analyze Report",
                use_container_width=True
            )


            if analyze_clicked:

                # =========================================
                # ANALYZE REPORT
                # =========================================

                with st.spinner(
                    "🔬 Analyzing laboratory results..."
                ):

                    results = analyze_report(
                        extracted_text
                    )


                # =========================================
                # LABORATORY RESULTS
                # =========================================

                st.markdown(
                    '<div class="section-title">🧪 Laboratory Results</div>',
                    unsafe_allow_html=True
                )


                if not results.empty:

                    # =====================================
                    # RESULT COUNTS
                    # =====================================

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

                    total_tests = len(results)


                    # =====================================
                    # DASHBOARD CARDS
                    # =====================================

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.markdown(
                            f"""
                            <div class="metric-card">
                                <div class="metric-label">
                                    🧪 Total Tests
                                </div>
                                <div class="metric-number blue-number">
                                    {total_tests}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    with col2:

                        st.markdown(
                            f"""
                            <div class="metric-card">
                                <div class="metric-label">
                                    🟢 Within Range
                                </div>
                                <div class="metric-number green-number">
                                    {within}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    with col3:

                        st.markdown(
                            f"""
                            <div class="metric-card">
                                <div class="metric-label">
                                    🟠 Below Range
                                </div>
                                <div class="metric-number orange-number">
                                    {below}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    with col4:

                        st.markdown(
                            f"""
                            <div class="metric-card">
                                <div class="metric-label">
                                    🔴 Above Range
                                </div>
                                <div class="metric-number red-number">
                                    {above}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                    st.markdown("")


                    # =====================================
                    # RESULT TABLE
                    # =====================================

                    display_results = results.copy()

                    def color_status(value):

                        if value == "Within Range":
                            return (
                                "background-color: #e8f7ee; "
                                "color: #138a42; "
                                "font-weight: 600;"
                            )

                        if value == "Below Range":
                            return (
                                "background-color: #fff2df; "
                                "color: #d47700; "
                                "font-weight: 600;"
                            )

                        if value == "Above Range":
                            return (
                                "background-color: #fde8e8; "
                                "color: #c62828; "
                                "font-weight: 600;"
                            )

                        return ""


                    styled_results = (
                        display_results.style
                        .map(
                            color_status,
                            subset=["Status"]
                        )
                    )


                    st.dataframe(
                        styled_results,
                        use_container_width=True,
                        hide_index=True
                    )


                    # =====================================
                    # SHORT SUMMARY
                    # =====================================

                    st.markdown(
                        '<div class="section-title">📌 Result Summary</div>',
                        unsafe_allow_html=True
                    )


                    summary_parts = []

                    summary_parts.append(
                        f"The report contains {total_tests} "
                        f"laboratory test(s)."
                    )

                    if within > 0:

                        summary_parts.append(
                            f"{within} result(s) are within "
                            f"the reference range shown on "
                            f"the report."
                        )

                    if below > 0:

                        summary_parts.append(
                            f"{below} result(s) are below "
                            f"the reference range shown on "
                            f"the report."
                        )

                    if above > 0:

                        summary_parts.append(
                            f"{above} result(s) are above "
                            f"the reference range shown on "
                            f"the report."
                        )


                    summary_text = " ".join(
                        summary_parts
                    )


                    st.markdown(
                        f"""
                        <div class="info-card">
                            <p>{summary_text}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    # =====================================
                    # AI EXPLANATION
                    # =====================================

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
                        f"""
                        <div class="ai-box">
                            {ai_summary.replace(chr(10), "<br>")}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    # =====================================
                    # DOWNLOAD REPORT
                    # =====================================

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


                    except Exception as e:

                        st.error(
                            f"❌ Could not create the PDF report: {e}"
                        )


                    # =====================================
                    # MEDICAL DISCLAIMER
                    # =====================================

                    st.markdown(
                        """
                        <div class="medical-disclaimer">

                        <b>⚠️ Important Medical Disclaimer</b>

                        <br><br>

                        This application provides informational
                        and educational explanations only.

                 
