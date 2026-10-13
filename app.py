
import io
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from extractor import extract_text_from_pdf
from ocr_service import extract_text_from_image
from analyzer import analyze_report


st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 AI Medical Report Explainer")
st.caption(
    "Upload a medical report to extract text and review recognized "
    "laboratory results."
)

st.warning(
    "Educational use only. This app does not diagnose conditions "
    "or replace advice from a qualified healthcare professional."
)

uploaded_file = st.file_uploader(
    "Upload a medical report",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    file_name = uploaded_file.name.lower()
    extracted_text = ""

    with st.spinner("Reading your report..."):
        try:
            if file_name.endswith(".pdf"):
                extracted_text = extract_text_from_pdf(uploaded_file)
            else:
                extracted_text = extract_text_from_image(uploaded_file)

        except Exception as error:
            st.error(f"Could not extract text: {error}")

    st.subheader("📄 Extracted Report Text")

    if extracted_text and extracted_text.strip():
        st.success(
            f"Text extraction completed: {len(extracted_text)} characters."
        )

        st.text_area(
            "Text detected in your report",
            value=extracted_text,
            height=260
        )

        st.download_button(
            "Download extracted text",
            data=extracted_text,
            file_name="extracted_report.txt",
            mime="text/plain"
        )

        st.subheader("🔬 Laboratory Results Analysis")

        try:
            results = analyze_report(extracted_text)

            if results is None or results.empty:
                st.warning(
                    "No laboratory results were recognized. "
                    "Check the extracted text and analyzer patterns."
                )
                st.info(
                    "If the extracted text is readable, the analyzer "
                    "may need to support your report's layout."
                )

            else:
                st.dataframe(results, use_container_width=True)

                col1, col2 = st.columns(2)
                col1.metric("Recognized tests", len(results))
                col2.metric(
                    "Tests needing review",
                    int(results["Status"].isin(
                        ["Below range", "Above range"]
                    ).sum())
                )

                # Plot results separately by test because their units
                # and scales may be different.
                st.subheader("📊 Results Graph")

                numeric_results = pd.to_numeric(
                    results["Result"], errors="coerce"
                )
                graph_data = results.loc[
                    numeric_results.notna()
                ].copy()
                graph_data["Result"] = numeric_results[
                    numeric_results.notna()
                ]

                if not graph_data.empty:
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.bar(
                        graph_data["Test"],
                        graph_data["Result"]
                    )
                    ax.set_xlabel("Laboratory test")
                    ax.set_ylabel("Reported result")
                    ax.set_title(
                        "Extracted laboratory values "
                        "(different units are not directly comparable)"
                    )
                    ax.tick_params(axis="x", rotation=35)
                    fig.tight_layout()

                    st.pyplot(fig)

                    image_buffer = io.BytesIO()
                    fig.savefig(
                        image_buffer,
                        format="png",
                        dpi=150,
                        bbox_inches="tight"
                    )
                    plt.close(fig)

                    st.download_button(
                        "Download graph (PNG)",
                        data=image_buffer.getvalue(),
                        file_name="laboratory_results.png",
                        mime="image/png"
                    )

                st.download_button(
                    "Download results (CSV)",
                    data=results.to_csv(index=False),
                    file_name="laboratory_results.csv",
                    mime="text/csv"
                )

                # Optional AI explanation
                st.subheader("🤖 AI Explanation")

                if st.button("Explain these results"):
                    try:
                        from ai_explainer import ai_explain_report

                        explanation = ai_explain_report(
                            results.to_string(index=False)
                        )

                        if explanation:
                            st.write(explanation)
                        else:
                            st.info(
                                "No explanation was returned. "
                                "Check your AI configuration."
                            )

                    except Exception as error:
                        st.error(
                            f"AI explanation failed: {error}"
                        )

        except Exception as error:
            st.error(f"Laboratory analysis failed: {error}")

    else:
        st.error(
            "No text was extracted. For an image, check OCR setup "
            "and try a clear, straight, high-resolution image. "
            "For a scanned PDF, OCR may also be required."
        )
        st.info(
            "If this message persists, check the Streamlit app logs "
            "for the exact OCR or PDF extraction error."
        )
