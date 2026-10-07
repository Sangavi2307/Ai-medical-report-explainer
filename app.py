import streamlit as st
from extractor import extract_text_from_pdf
from analyzer import analyze_report
from ai_explainer import ai_explain_report
from ocr_service import extract_text_from_image
from report_generator import generate_report


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# PROFESSIONAL UI
# =========================================================

st.markdown("""
<style>

.stApp {
    background: #f4f8fc;
}

.block-container {
    max-width: 1150px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none;
}


/* HERO */

.hero {
    background: linear-gradient(
        135deg,
        #0b3d66,
        #1478b8
    );

    border-radius: 24px;
    padding: 30px;
    margin-bottom: 28px;

    box-shadow:
        0 10px 28px rgba(11,61,102,.18);
}

.hero-icon {
    font-size: 40px;
}

.hero-title {
    color: #ffffff !important;
    font-size: 36px;
    font-weight: 800;
    line-height: 1.2;
}

.hero-subtitle {
    color: #eaf6ff !important;
    font-size: 16px;
    line-height: 1.6;
    max-width: 760px;
    margin-top: 9px;
}

.badge {
    display: inline-block;
    color: #ffffff !important;
    background: rgba(255,255,255,.15);
    border: 1px solid rgba(255,255,255,.22);
    border-radius: 30px;
    padding: 7px 12px;
    margin: 16px 7px 0 0;
    font-size: 12px;
}


/* SECTIONS */

.section-title {
    color: #123b63;
    font-size: 24px;
    font-weight: 800;
    margin: 28px 0 8px;
}

.section-text {
    color: #687b8d;
    font-size: 14px;
    margin-bottom: 16px;
}


/* HOW IT WORKS */

.step-card {
    background: #ffffff;
    border: 1px solid #e0e9f1;
    border-radius: 18px;
    padding: 18px 14px;
    min-height: 165px;
    text-align: center;

    box-shadow:
        0 5px 18px rgba(24,63,95,.07);
}

.step-number {
    width: 40px;
    height: 40px;

    margin: 0 auto 8px;

    border-radius: 50%;

    background: #e8f3fb;
    color: #1261a0;

    font-weight: 800;

    display: flex;
    align-items: center;
    justify-content: center;
}

.step-icon {
    font-size: 25px;
}

.step-title {
    color: #123b63;
    font-weight: 750;
    margin-top: 6px;
}

.step-text {
    color: #718294;
    font-size: 12px;
    line-height: 1.5;
    margin-top: 5px;
}


/* UPLOAD */

.upload-info {
    background: #ffffff;
    border: 1px solid #dce7f0;
    border-radius: 18px;
    padding: 20px;

    box-shadow:
        0 5px 18px rgba(24,63,95,.06);

    margin-bottom: 12px;
}

.upload-title {
    color: #123b63;
    font-size: 19px;
    font-weight: 750;
}

.upload-text {
    color: #718294;
    font-size: 13px;
    margin-top: 4px;
}

[data-testid="stFileUploader"] {
    background: #f9fcff !important;
    border: 2px dashed #8dbbd8 !important;
    border-radius: 16px !important;
}


/* BUTTON */

.stButton > button {
    width: 100%;
    min-height: 48px;

    border: 0;
    border-radius: 12px;

    background: linear-gradient(
        135deg,
        #1261a0,
        #1683c4
    );

    color: #ffffff !important;

    font-weight: 750;
    font-size: 15px;

    box-shadow:
        0 5px 15px rgba(18,97,160,.18);
}


/* METRICS */

.metric-card {
    background: #ffffff;
    border: 1px solid #e0e8f0;
    border-radius: 16px;

    padding: 17px 8px;

    text-align: center;
    min-height: 118px;

    box-shadow:
        0 5px 18px rgba(24,63,95,.06);
}

.metric-icon {
    font-size: 22px;
}

.metric-label {
    color: #718294;
    font-size: 12px;
    margin-top: 5px;
}

.metric-value {
    font-size: 29px;
    font-weight: 800;
    margin-top: 3px;
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


/* CARDS */

.card {
    background: #ffffff;
    border: 1px solid #dce7f0;
    border-radius: 16px;

    padding: 20px;

    box-shadow:
        0 5px 18px rgba(24,63,95,.06);
}

.summary-card {
    border-left: 5px solid #1683c4;
}

.ai-card {
    border-left: 5px solid #1261a0;
    color: #3e5366;
    line-height: 1.75;
}

.download-card {
    background: #edf7ff;
    border: 1px solid #cce7f8;
}

.card-title {
    color: #123b63;
    font-size: 18px;
    font-weight: 750;
    margin-bottom: 7px;
}

.card-text {
    color: #627588;
    line-height: 1.7;
}


/* DISCLAIMER */

.disclaimer {
    background: #fff8e8;
    border-left: 5px solid #e6a21a;

    border-radius: 14px;

    padding: 19px;
    margin-top: 25px;

    color: #69531e;
    line-height: 1.7;
}

.disclaimer-title {
    font-weight: 800;
    font-size: 17px;
}


/* FOOTER */

.footer {
    text-align: center;
    color: #7a8b9b;

    font-size: 12px;

    margin-top: 32px;
    padding: 20px 0;
}


/* MOBILE */

@media (max-width: 700px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        padding: 24px 20px;
    }

    .hero-title {
        font-size: 27px;
    }

    .hero-subtitle {
        font-size: 14px;
    }

    .section-title {
        font-size: 21px;
    }

    .step-card {
        min-height: auto;
        margin-bottom: 10px;
    }

    .metric-card {
        margin-bottom: 10px;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HERO HEADER
# =========================================================

st.markdown("""
<div class="hero">

    <div class="hero-icon">
        🩺
    </div>

    <div class="hero-title">
        AI Medical Report Explainer
    </div>

    <div class="hero-subtitle">
        Understand laboratory reports with clear,
        simple and educational AI explanations.
        Upload a PDF or image and review the
        extracted results.
    </div>

    <span class="badge">
        🔒 Privacy Focused
    </span>

    <span class="badge">
        🤖 AI Assisted
    </span>

    <span class="badge">
        📊 Easy to Understand
    </span>

</div>
""", unsafe_allow_html=True)


# =========================================================
# HOW IT WORKS
# =========================================================

st.markdown(
    '<div class="section-title">📋 How It Works</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-text">'
    'Four simple steps from report upload to educational explanation.'
    '</div>',
    unsafe_allow_html=True
)


steps = [
    (
        "1",
        "📄",
        "Upload Report",
        "Upload a PDF, JPG, JPEG or PNG medical report."
    ),
    (
        "2",
        "🔎",
        "Extract Text",
        "Read text from the PDF or use OCR for images."
    ),
    (
        "3",
        "🧪",
        "Analyze Results",
        "Identify laboratory values and report ranges."
    ),
    (
        "4",
        "🤖",
        "AI Explanation",
        "Get a simple educational explanation."
    )
]


columns = st.columns(4)


for column, step in zip(columns, steps):

    number, icon, title, description = step

    with column:

        st.markdown(
            f"""
            <div class="step-card">

                <div class="step-number">
                    {number}
                </div>

                <div class="step-icon">
                    {icon}
                </div>

                <div class="step-title">
                    {title}
                </div>

                <div class="step-text">
                    {description}
                </div>

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

st.markdown(
    """
    <div class="upload-info">

        <div class="upload-title">
            Choose your report
        </div>

        <div class="upload-text">
            Supported formats: PDF, JPG, JPEG and PNG.
            For best OCR results, use a clear,
            well-lit image.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


uploaded_file = st.file_uploader(
    "Choose a PDF or image file",
    type=[
        "pdf",
        "jpg",
        "jpeg",
        "png"
    ],
    label_visibility="collapsed"
)


# =========================================================
# FILE PROCESSING
# =========================================================

if uploaded_file is not None:

    st.success(
        f"✅ File uploaded successfully: "
        f"{uploaded_file.name}"
    )

    file_name = uploaded_file.name.lower()

    try:

        # PDF
        if file_name.endswith(".pdf"):

            with st.spinner(
                "📄 Reading your PDF report..."
            ):

                extracted_text = extract_text_from_pdf(
                    uploaded_file
                )

        # IMAGE
        else:

            with st.spinner(
                "🔎 Reading text from your image..."
            ):

                extracted_text = extract_text_from_image(
                    uploaded_file
                )


        # =================================================
        # NO TEXT
        # =================================================

        if not extracted_text or not extracted_text.strip():

            st.error(
                "❌ No readable text was found in this file."
            )

            if file_name.endswith(".pdf"):

                st.info(
                    "This PDF may be scanned or image-based. "
                    "Try uploading the report as JPG or PNG."
                )

            else:

                st.info(
                    "Try a clearer image with readable text."
                )


        # =================================================
        # TEXT FOUND
        # =================================================

        else:

            st.markdown(
                '<div class="section-title">'
                '📋 Extracted Report'
                '</div>',
                unsafe_allow_html=True
            )


            with st.expander(
                "View extracted report text"
            ):

                st.text_area(
                    "Extracted text",
                    extracted_text,
                    height=300,
                    label_visibility="collapsed"
                )


            st.markdown("")


            analyze_clicked = st.button(
                "🔍 Analyze Medical Report",
                use_container_width=True
            )


            # =================================================
            # ANALYZE
            # =================================================

            if analyze_clicked:

                with st.spinner(
                    "🔬 Analyzing laboratory results..."
                ):

                    results = analyze_report(
                        extracted_text
                    )


                # =================================================
                # NO RESULTS
                # =================================================

                if results.empty:

                    st.warning(
                        "⚠️ No laboratory test results were detected."
                    )

                    st.info(
                        "The report text was extracted, but "
                        "laboratory values could not be identified. "
                        "Check the extracted text or try a clearer report."
                    )


                # =================================================
                # RESULTS FOUND
                # =================================================

                else:

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
                    # DASHBOARD
                    # =================================================

                    st.markdown(
                        '<div class="section-title">'
                        '📊 Laboratory Results Dashboard'
                        '</div>',
                        unsafe_allow_html=True
                    )


                    metric_data = [
                        (
                            "🧪",
                            "Total Tests",
                            total_tests,
                            "blue"
                        ),
                        (
                            "🟢",
                            "Within Range",
                            within,
                            "green"
                        ),
                        (
                            "🟠",
                            "Below Range",
                            below,
                            "orange"
                        ),
                        (
                            "🔴",
                            "Above Range",
                            above,
                            "red"
                        )
                    ]


                    metric_columns = st.columns(4)


                    for column, data in zip(
                        metric_columns,
                        metric_data
                    ):

                        icon, label, value, color = data

                        with column:

                            st.markdown(
                                f"""
                                <div class="metric-card">

                                    <div class="metric-icon">
                                        {icon}
                                    </div>

                                    <div class="metric-label">
                                        {label}
                                    </div>

                                    <div class="metric-value {color}">
                                        {value}
                                    </div>

                                </div>
                                """,
                                unsafe_allow_html=True
                            )


                    # =================================================
                    # TABLE
                    # =================================================

                    st.markdown(
                        '<div class="section-title">'
                        '🧪 Detailed Laboratory Results'
                        '</div>',
                        unsafe_allow_html=True
                    )


                    st.dataframe(
                        results,
                        use_container_width=True,
                        hide_index=True
                    )


                    # =================================================
                    # SUMMARY
                    # =================================================

                    summary = (
                        f"The report contains "
                        f"{total_tests} laboratory test(s). "
                    )


                    if within:

                        summary += (
                            f"{within} result(s) are within "
                            f"the reference range shown "
                            f"on the report. "
                        )


                    if below:

                        summary += (
                            f"{below} result(s) are below "
                            f"the reference range shown "
                            f"on the report. "
                        )


                    if above:

                        summary += (
                            f"{above} result(s) are above "
                            f"the reference range shown "
                            f"on the report."
                        )


                    st.markdown(
                        '<div class="section-title">'
                        '📌 Result Summary'
                        '</div>',
                        unsafe_allow_html=True
                    )


                    st.markdown(
                        f"""
                        <div class="card summary-card">

                            <div class="card-title">
                                Analysis Overview
                            </div>

                            <div class="card-text">
                                {summary}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
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
                        "🤖 Preparing educational explanation..."
                    ):

                        ai_summary = ai_explain_report(
                            extracted_text
                        )


                    safe_ai_summary = (
                        ai_summary
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace("\n", "<br>")
                    )


                    st.markdown(
                        f"""
                        <div class="card ai-card">
                            {safe_ai_summary}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    # =================================================
                    # DOWNLOAD
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


                        st.markdown(
                            """
                            <div class="card download-card">

                                <div class="card-title">
                                    📄 Your report is ready
                                </div>

                                <div class="card-text">
                                    Download the laboratory results
                                    and educational explanation
                                    as a PDF.
                                </div>

                            </div>
                            """,
           
