
# MediLens — Medical Report Explainer

MediLens is an educational Streamlit application for extracting text
from medical report PDFs and images and displaying supported laboratory
result lines.

## Features

- PDF text extraction using PyMuPDF
- Image OCR using Tesseract
- Basic laboratory result extraction
- Patient details when supported labels are present
- Interactive dashboard and results graph
- Offline educational summary
- Extracted text download
- PDF report summary download

## Setup

Install Python dependencies:

    pip install -r requirements.txt

Install the Tesseract OCR system application separately.

Run:

    streamlit run app.py

## Limitations

The result parser supports only certain text formats. It may miss results,
patient details, units, or reference ranges. It does not validate medical
ranges or provide diagnosis or treatment advice.

Consult a qualified healthcare professional for medical interpretation.
