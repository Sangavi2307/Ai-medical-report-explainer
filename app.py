import streamlit as st

from extractor import extract_text_from_pdf
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from ocr_service import extract_text_from_image
from report_generator import generate_report


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# PROFESSIONAL UI CSS
# ============================================================

st.markdown(
    """
<style>

/* ---------------------------------------------------------
   GENERAL
--------------------------------------------------------- */

.stApp {
    background: #f4f8fc;
}

.block-container {
    max-width: 1180px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}


/* ---------------------------------------------------------
   HIDE SIDEBAR
--------------------------------------------------------- */

[data-testid="stSidebar"] {
    display: none;
}

[data-testid="collapsedControl"] {
    display: none;
}


/* ---------------------------------------------------------
   HERO HEADER
--------------------------------------------------------- */

.hero {
    background: linear-gradient(
        135deg,
        #0d3b66 0%,
        #1261a0 55%,
        #1683c4 100%
    );

    padding: 34px 36px;
    border-radius: 24px;
    margin-bottom: 26px;

    box-shadow:
        0 12px 30px rgba(13, 59, 102, 0.20);
}

.hero-icon {
    font-size: 42px;
    margin-bottom: 8px;
}

.hero-title {
    color: white;
    font-size: 36px;
    font-weight: 750;
    line-height: 1.2;
    margin-bottom: 10px;
}

.hero-subtitle {
    color: #e9f5ff;
    font-size: 17px;
    line-height: 1.6;
    max-width: 750px;
}

.badges {
    margin-top: 20px;
}

.badge {
    display: inline-block;
    color: white;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 30px;
    padding: 7px 13px;
    margin-right: 7px;
    margin-bottom: 7px;
    font-size: 13px;
}


/* ---------------------------------------------------------
   SECTION HEADINGS
--------------------------------------------------------- */

.section-heading {
    color: #123b63;
    font-size: 25px;
    font-weight: 750;
    margin-top: 30px;
    margin-bottom: 15px;
}

.section-description {
    color: #687b8d;
    font-size: 15px;
    margin-top: -5px;
    margin-bottom: 18px;
}


/* ---------------------------------------------------------
   HOW IT WORKS
--------------------------------------------------------- */

.step-card {
    background: white;
    border: 1px solid #e0e9f1;
    border-radius: 18px;
    padding: 20px 16px;
    min-height: 175px;

    box-shadow:
        0 5px 18px rgba(24, 63, 95, 0.07);

    text-align: center;
}

.step-number {
    width: 44px;
    height: 44px;
    margin: 0 auto 10px auto;

    border-radius: 50%;

    background: #e8f3fb;
    color: #1261a0;

    font-size: 20px;
    font-weight: 700;

    display: flex;
    align-items: center;
    justify-content: center;
}

.step-icon {
    font-size: 27px;
    margin-bottom: 6px;
}

.step-title {
    color: #123b63;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 6px;
}

.step-text {
    color: #718294;
    font-size: 13px;
    line-height: 1.5;
}


/* ---------------------------------------------------------
   UPLOAD CARD
--------------------------------------------------------- */

.upload-card {
    background: white;
    border: 1px solid #dce7f0;
    border-radius: 20px;
    padding: 25px;

    box-shadow:
        0 6px 20px rgba(20, 55, 90, 0.07);
}

.upload-title {
    color: #123b63;
    font-size: 21px;
    font-weight: 700;
}

.upload-description {
    color: #718294;
    font-size: 14px;
    margin-top: 5px;
    margin-bottom: 12px;
}


/* ---------------------------------------------------------
   STREAMLIT FILE UPLOADER
--------------------------------------------------------- */

[data-testid="stFileUploader"] {
    background: #f8fbfe !important;
    border: 2px dashed #8dbbd8 !important;
    border-radius: 16px !important;
    padding: 10px !important;
}

[data-testid="stFileUploader"] section {
    background: transparent !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] {
    color: #526b80 !important;
}


/* ---------------------------------------------------------
   BUTTON
--------------------------------------------------------- */

.stButton > button {
    width: 100%;
    min-height: 48px;

    background: linear-gradient(
        135deg,
        #1261a0,
        #1683c4
    );

    color: white !important;

    border: none;
    border-radius: 12px;

    font-size: 16px;
    font-weight: 700;

    box-shadow:
        0 5px 15px rgba(18, 97, 160, 0.20);
}

.stButton > button:hover {
    background: #0d568f;
    color: white !important;
}


/* ---------------------------------------------------------
   METRIC CARDS
--------------------------------------------------------- */

.metric-card {
    background: white;
    border: 1px solid #e0e8f0;
    border-radius: 17px;

    padding: 20px 10px;

    text-align: center;

    min-height: 125px;

    box-shadow:
        0 5px 18px rgba(24, 63, 95, 0.07);
}

.metric-icon {
    font-size: 22px;
}

.metric-label {
    color: #718294;
    font-size: 13px;
    margin-top: 5px;
}

.metric-value {
    font-size: 30px;
    font-weight: 750;
    margin-top: 4px;
}

.blue {
    color: #1261a0;
}

.green {
    color: #159447;
}

.orange {
    color: #df8700;
}

.red {
    color: #d53d3d;
}


/* ---------------------------------------------------------
   RESULT SUMMARY
--------------------------------------------------------- */

.summary-card {
    background: white;

    border-left: 5px solid #1683c4;

    border-radius: 14px;

    padding: 20px;

    margin-top: 10px;

    box-shadow:
        0 5px 18px rgba(24, 63, 95, 0.06);
}

.summary-title {
    color: #123b63;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 7px;
}

.summary-text {
    color: #627588;
    line-height: 1.7;
}


/* ---------------------------------------------------------
   AI BOX
--------------------------------------------------------- */

.ai-card {
    background: white;

    border: 1px solid #dce7f0;
    border-left: 5px solid #1261a0;

    border-radius: 16px;

    padding: 23px;

    box-shadow:
        0 6px 20px rgba(20, 55, 90, 0.07);

    color: #3e5366;

    line-height: 1.75;
}


/* ---------------------------------------------------------
   DOWNLOAD CARD
--------------------------------------------------------- */

.download-card {
    background: #edf7ff;
    border: 1px solid #cce7f8;

    border-radius: 16px;

    padding: 20px;

    margin-top: 15px;
}

.download-title {
    color: #123b63;
    font-weight: 700;
    font-size: 18px;
}

.download-text {
    color: #657a8c;
    font-size: 14px;
}


/* ---------------------------------------------------------
   DISCLAIMER
--------------------------------------------------------- */

.disclaimer {
    background: #fff8e8;

    border-left: 5px solid #e6a21a;

    border-radius: 14px;

    padding: 20px;

    margin-top: 25px;

    color: #69531e;

    line-height: 1.7;
}

.disclaimer-title {
    font-weight: 750;
    font-size: 17px;
}


/* ---------------------------------------------------------
   FOOTER
--------------------------------------------------------- */

.footer {
    text-align: center;

    color: #7a8b9b;

    font-size: 13px;

    margin-top: 35px;
    padding: 20px 0;
}


/* ---------------------------------------------------------
   MOBILE RESPONSIVE
--------------------------------------------------------- */

@media (max-width: 700px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
    }

    .hero {
        padding: 25px 22px;
        border-radius: 20px;
    }

    .hero-title {
        font-size: 27px;
    }

    .hero-subtitle {
        font-size: 15px;
    }

    .section-heading {
        font-size: 21px;
    }

    .step-card {
        min-height: auto;
        margin-bottom: 10px;
    }

    .upload-card {
        padding: 17px;
    }

    .metric-card {
        margin-bottom: 10px;
    }

}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HERO HEADER
# ============================================================

st.markdown(
    """
<div class="hero">

    <div class="hero-icon">
        🩺
    </div>

    <div class="hero-title">
        AI Medical Report Explainer
    </div>

    <div class="hero-subtitle">
        Understand your laboratory reports with clear,
        simple and educational AI explanations.
    </div>

    <div class="badges">
        <span class="badge">🔒 Privacy Focused</span>
        <span class="badge">🤖 AI Assisted</span>
        <span class="badge">📊 Easy to Understand</span>
    </div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# HOW IT WORKS
# ============================================================

st.markdown(
    '<div class="section-heading">📋 How It Works</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Four simple steps to understand your uploaded report.'
    '</div>',
    unsafe_allow_html=True
)


step1, step2, step3, step4 = st.columns(4)


with step1:

    st.markdown(
        """
        <div class="step-card">

            <div class="step-number">1</div>

            <div class="step-icon">📄</div>

            <div class="step-title">
                Upload Report
            </div>

            <div class="step-text">
                Upload your medical report
                as PDF or image.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with step2:

    st.markdown(
        """
        <div class="step-card">

            <div class="step-number">2</div>

            <div class="step-icon">🔎</div>

            <div class="step-title">
                Extract Text
            </div>

            <div class="step-text">
                The application reads
                information from the report.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with step3:

    st.markdown(
        """
        <div class="step-card">

            <div class="step-number">3</div>

            <div class="step-icon">🧪</div>

            <div class="step-title">
                Analyze Results
            </div>

            <div class="step-text">
                Laboratory values and
                reference ranges are identified.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with step4:

    st.markdown(
        """
        <div class="step-card">

            <div class="step-number">4</div>

            <div class="step-icon">🤖</div>

            <div class="step-title">
                AI Explanation
            </div>

            <div class="step-text">
                Results are explained in
                simple educational language.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    '<div class="section-heading">📄 Upload Medical Report</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="upload-card">'
    '<div class="upload-title">Choose your report</div>'
    '<div class="upload-description">'
    'Supported formats: PDF, JPG, JPEG and PNG'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("")


uploaded_file = st.file_uploader(
    "Upload your medical report",
    type=[
        "pdf",
        "jpg",
        "jpeg",
        "png"
    ],
    help="Maximum file size depends on your Streamlit deployment settings.",
    label_visibility="collapsed"
)


# ============================================================
# FILE UPLOADED
# ============================================================

if uploaded_file is not None:

    st.success(
        "✅ File uploaded successfully: "
        + uploaded_file.name
    )

    file_name = uploaded_file.name.lower()


    # ========================================================
    # EXTRACT TEXT
    # ========================================================

    try:

        if file_name.endswith(".pdf"):

            with st.spinner(
                "📄 Reading your PDF report..."
            ):

                extracted_text = extract_text_from_pdf(
                    uploaded_file
                )

        else:

            with st.spinner(
                "🔎 Reading text from your image..."
            ):

                extracted_text = extract_text_from_image(
                    uploaded_file
                )


        # ====================================================
        # TEXT FOUND
        # ====================================================

        if extracted_text and extracted_text.strip():

            st.markdown(
                '<div class="section-heading">'
                '📋 Extracted Report'
                '</div>',
                unsafe_allow_html=True
            )

            with st.expander(
                "View extracted report text",
                expanded=False
            ):

                st.text_area(
                    "Extracted text",
                    extracted_text,
                    height=300,
                    label_visibility="collapsed"
                )


            # =================================================
            # ANALYZE BUTTON
            # =================================================

            st.markdown("")

            analyze_clicked = st.button(
                "🔍 Analyze Medical Report",
                use_container_width=True
            )


            if analyze_clicked:

                with st.spinner(
                    "🔬 Analyzing laboratory results..."
                ):

                    results = analyze_report(
                        extracted_text
                    )


                # =================================================
                # RESULTS FOUND
                # =================================================

                if not results.empty:

                    st.markdown(
                        '<div class="section-heading">'
                        '📊 Laboratory Results Dashboard'
                        '</div>',
                        unsafe_allow_html=True
                    )


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


                    # =================================================
                    # METRICS
                    # =================================================

                    m1, m2, m3, m4 = st.columns(4)


                    with m1:

                        st.markdown(
                            f"""
                            <div class="metric-card">

                                <div class="metric-icon">
                                    🧪
                                </div>

                                <div class="metric-label">
                                    Total Tests
                                </div>

                                <div class="metric-value blue">
                                    {total_tests}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                    with m2:

                        st.markdown(
                            f"""
                            <div class="metric-card">

                                <div class="metric-icon">
                                    🟢
                                </div>

                                <div class="metric-label">
                                    Within Range
                                </div>

                                <div class="metric-value green">
                                    {within}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                    with m3:

                        st.markdown(
                            f"""
                            <div class="metric-card">

                                <div class="metric-icon">
                                    🟠
                                </div>

                                <div class="metric-label">
                                    Below Range
                                </div>

                                <div class="metric-value orange">
                                    {below}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                    with m4:

                        st.markdown(
                            f"""
                            <div class="metric-card">

                                <div class="metric-icon">
                                    🔴
                                </div>

                                <div class="metric-label">
                                    Above Range
                                </div>

                                <div class="metric-value red">
                                    {above}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                    # =================================================
                    # TABLE
                    # =================================================

                    st.markdown(
                        '<div class="section-heading">'
                        '🧪 Detailed Laboratory Results'
                        '</div>',
                        unsafe_allow_html=True
                    )


                    def status_style(value):

                        if value == "Within Range":

                            return (
                                "background-color:#e8f7ee;"
                                "color:#138a42;"
                                "font-weight:700;"
                            )

                        if value == "Below Range":

                            return (
                                "background-color:#fff2df;"
                                "color:#d47700;"
                                "font-weight:700;"
                            )

                        if value == "Above Range":

                            return (
                                "background-color:#fde8e8;"
                                "color:#c62828;"
                                "font-weight:700;"
)
 
