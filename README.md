
# MediLens — Medical Report Explainer

MediLens is a Streamlit educational application that accepts PDF laboratory reports, extracts selectable text, detects supported laboratory results, displays a dashboard, and provides downloadable outputs.

## Features

- PDF-only upload
- Text extraction from selectable-text PDFs
- Laboratory result table
- Result-status dashboard graph
- CSV, TXT, PNG, and PDF downloads
- Educational-use medical disclaimer

## Run locally

Install dependencies:

    pip install -r requirements.txt

Start the application:

    streamlit run app.py

## Limitations

- Scanned PDFs need OCR support.
- The analyzer supports a limited set of laboratory test names and layouts.
- Reference ranges must be present on the same line to be assessed.
- Extracted values must be checked against the original report.

## Safety

This application does not diagnose medical conditions or recommend treatment. It does not replace professional medical advice.
