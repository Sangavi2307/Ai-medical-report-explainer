
import re
import pandas as pd


# --------------------------------------------------
# COMMON LAB TEST INFORMATION
# --------------------------------------------------

TEST_INFO = {
    "hemoglobin": {
        "name": "Hemoglobin (Hb)",
        "purpose": "Measures the oxygen-carrying protein in red blood cells.",
        "high": "A high value may occur with dehydration or other conditions.",
        "low": "A low value may be associated with anemia, blood loss, or nutritional deficiencies."
    },
    "wbc": {
        "name": "White Blood Cell Count (WBC)",
        "purpose": "Measures white blood cells, which help the body fight infections.",
        "high": "A high value can occur with infection, inflammation, stress, or certain medicines.",
        "low": "A low value can occur with some infections, medicines, or bone marrow conditions."
    },
    "rbc": {
        "name": "Red Blood Cell Count (RBC)",
        "purpose": "Measures the number of red blood cells that carry oxygen.",
        "high": "A high value can occur with dehydration or other medical conditions.",
        "low": "A low value may be associated with anemia or blood loss."
    },
    "platelet": {
        "name": "Platelet Count",
        "purpose": "Measures platelets, which help blood clot.",
        "high": "A high value can occur with inflammation, iron deficiency, or other conditions.",
        "low": "A low value may increase bleeding risk, depending on how low it is."
    },
    "glucose": {
        "name": "Blood Glucose",
        "purpose": "Measures the amount of glucose in the blood. Interpretation depends on whether the sample was fasting, random, or taken after a meal.",
        "high": "A high value may indicate elevated blood sugar and may need follow-up testing.",
        "low": "A low value may indicate low blood sugar; symptoms and circumstances matter."
    },
    "hba1c": {
        "name": "HbA1c",
        "purpose": "Estimates average blood glucose over approximately the previous two to three months.",
        "high": "A high value can indicate that average blood glucose has been elevated.",
        "low": "A low value should be interpreted with the clinical context; some blood conditions can affect accuracy."
    },
    "creatinine": {
        "name": "Creatinine",
        "purpose": "A waste product used, alongside other information, to assess kidney function.",
        "high": "A high value may occur with reduced kidney function, dehydration, or other causes.",
        "low": "A low value can be associated with lower muscle mass and is not usually interpreted alone."
    },
    "urea": {
        "name": "Blood Urea",
        "purpose": "Measures a waste product processed by the kidneys.",
        "high": "A high value can occur with dehydration, kidney problems, high protein breakdown, or other causes.",
        "low": "A low value may occur with low protein intake, certain liver conditions, or overhydration."
    },
    "cholesterol": {
        "name": "Total Cholesterol",
        "purpose": "Measures total cholesterol in the blood and contributes to cardiovascular risk assessment.",
        "high": "A high value may increase cardiovascular risk depending on the full lipid profile and other risk factors.",
        "low": "A low value is generally interpreted alongside the full clinical picture."
    },
    "ldl": {
        "name": "LDL Cholesterol",
        "purpose": "Often called 'bad' cholesterol because higher levels can contribute to plaque in arteries.",
        "high": "A high value may increase cardiovascular risk. The appropriate target depends on individual risk.",
        "low": "A low value is often desirable, but interpretation depends on the clinical context."
    },
    "hdl": {
        "name": "HDL Cholesterol",
        "purpose": "Often called 'good' cholesterol; it is one part of cardiovascular risk assessment.",
        "high": "Higher HDL is often associated with lower risk, but very high values are not always protective.",
        "low": "A low value can be associated with increased cardiovascular risk."
    },
    "triglyceride": {
        "name": "Triglycerides",
        "purpose": "Measures a type of fat in the blood.",
        "high": "A high value may be associated with metabolic factors, diet, medicines, or other conditions.",
        "low": "A low value is often not concerning by itself but should be interpreted in context."
    },
    "sodium": {
        "name": "Sodium",
        "purpose": "An electrolyte important for fluid balance and nerve and muscle function.",
        "high": "A high value may be related to water balance or other medical conditions.",
        "low": "A low value can have several causes and may be important if substantially reduced."
    },
    "potassium": {
        "name": "Potassium",
        "purpose": "An electrolyte essential for muscle function and the heart's electrical activity.",
        "high": "A high value can affect heart rhythm. A falsely high result can also occur if the sample is damaged.",
        "low": "A low value can affect muscles and heart rhythm."
    },
    "calcium": {
        "name": "Calcium",
        "purpose": "Supports bones, muscles, nerves, and other body functions.",
        "high": "A high value can have several causes and may require further assessment.",
        "low": "A low value may be associated with vitamin D, parathyroid, kidney, or other problems."
    },
    "bilirubin": {
        "name": "Bilirubin",
        "purpose": "A substance produced when red blood cells break down; it is assessed in liver and blood-related investigations.",
        "high": "A high value may occur with liver or bile duct problems or increased red blood cell breakdown.",
        "low": "A low value is usually not significant on its own."
    },
    "alt": {
        "name": "ALT",
        "purpose": "An enzyme commonly measured to assess liver cell irritation or injury.",
        "high": "A high value can have multiple causes, including liver inflammation, medicines, or fatty liver.",
        "low": "A low value is generally not a concern by itself."
    },
    "ast": {
        "name": "AST",
        "purpose": "An enzyme found in the liver and other tissues, including muscles.",
        "high": "A high value can be associated with liver or muscle injury and must be interpreted with other results.",
        "low": "A low value is generally not a concern by itself."
    },
    "tsh": {
        "name": "TSH",
        "purpose": "A hormone test used with thyroid hormone measurements to assess thyroid function.",
        "high": "A high value can be associated with an underactive thyroid, but other results and context are needed.",
        "low": "A low value can be associated with an overactive thyroid or thyroid medication effects."
    },
    "vitamin d": {
        "name": "Vitamin D",
        "purpose": "Assesses vitamin D status, which is important for bone and muscle health.",
        "high": "A high value may indicate excessive supplementation and should be reviewed.",
        "low": "A low value may indicate vitamin D deficiency."
    },
    "vitamin b12": {
        "name": "Vitamin B12",
        "purpose": "A vitamin important for red blood cell production and nerve function.",
        "high": "A high value may reflect supplementation or other factors; interpretation depends on context.",
        "low": "A low value may be associated with anemia or nerve symptoms."
    },
    "esr": {
        "name": "ESR",
        "purpose": "A nonspecific measure that may rise with inflammation.",
        "high": "A high value can occur with inflammation, infection, and many other conditions; it does not identify a specific cause.",
        "low": "A low value is generally less concerning and must be interpreted in context."
    },
    "crp": {
        "name": "CRP",
        "purpose": "A marker of inflammation in the body.",
        "high": "A high value suggests inflammation but does not identify its cause.",
        "low": "A low value generally indicates little measurable CRP-related inflammation at the time of testing."
    },
    "uric acid": {
        "name": "Uric Acid",
        "purpose": "Measures uric acid in the blood; it may be used when evaluating gout and other conditions.",
        "high": "A high value may increase the chance of gout in some people, but does not diagnose gout by itself.",
        "low": "A low value is usually interpreted alongside symptoms and other results."
    },
    "albumin": {
        "name": "Albumin",
        "purpose": "A major blood protein that can provide information about liver function, nutrition, and protein loss.",
        "high": "A high value often occurs with dehydration.",
        "low": "A low value can have several causes, including liver disease, kidney protein loss, inflammation, or poor nutrition."
    },
    "protein": {
        "name": "Total Protein",
        "purpose": "Measures the combined amount of several proteins in the blood.",
        "high": "A high value may occur with dehydration or certain inflammatory conditions.",
        "low": "A low value can have several causes, including liver or kidney conditions and nutritional issues."
    },
    "hemoglobin": {
        "name": "Hemoglobin (Hb)",
        "purpose": "Measures the oxygen-carrying protein in red blood cells.",
        "high": "A high value may occur with dehydration or other conditions.",
        "low": "A low value may be associated with anemia, blood loss, or nutritional deficiencies."
    }
}


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def find_test_info(test_name):
    """Match common test names and abbreviations."""
    name = clean_text(test_name).lower()

    aliases = {
        "hb": "hemoglobin",
        "haemoglobin": "hemoglobin",
        "white blood cells": "wbc",
        "white blood cell count": "wbc",
        "total leukocyte count": "wbc",
        "tlc": "wbc",
        "total leucocyte count": "wbc",
        "red blood cells": "rbc",
        "red blood cell count": "rbc",
        "thrombocyte count": "platelet",
        "platelets": "platelet",
        "fbs": "glucose",
        "fasting blood sugar": "glucose",
        "rbs": "glucose",
        "random blood sugar": "glucose",
        "blood sugar": "glucose",
        "glycated hemoglobin": "hba1c",
        "glycosylated hemoglobin": "hba1c",
        "serum creatinine": "creatinine",
        "blood urea nitrogen": "urea",
        "bun": "urea",
        "total cholesterol": "cholesterol",
        "ldl cholesterol": "ldl",
        "hdl cholesterol": "hdl",
        "sgpt": "alt",
        "sgot": "ast",
        "25-oh vitamin d": "vitamin d",
        "c-reactive protein": "crp",
        "serum uric acid": "uric acid",
        "total protein": "protein"
    }

    for alias, key in aliases.items():
        if alias in name:
            name = key
            break

    for key, info in TEST_INFO.items():
        if key in name:
            return info

    return None


# --------------------------------------------------
# STATUS INTERPRETATION
# --------------------------------------------------

def explain_status(status):
    value = clean_text(status).lower()

    if any(word in value for word in ["high", "above", "elevated", "abnormal high"]):
        return (
            "The report marks this result as higher than its stated reference range. "
            "The meaning depends on the test, the amount of elevation, symptoms, "
            "medicines, and medical history."
        )

    if any(word in value for word in ["low", "below", "decreased", "abnormal low"]):
        return (
            "The report marks this result as lower than its stated reference range. "
            "The meaning depends on the test, how far below range it is, symptoms, "
            "and the person's medical context."
        )

    if any(word in value for word in ["normal", "within range", "within reference"]):
        return (
            "The report marks this result as within its stated reference range. "
            "A result within range does not rule out every health condition."
        )

    return (
        "The status could not be interpreted confidently from the extracted text. "
        "Please compare the value with the original report's reference range."
    )


# --------------------------------------------------
# MAIN EXPLANATION FUNCTION
# --------------------------------------------------

def explain_report(report_text, results_df=None, patient_fields=None):
    """
    Creates a detailed educational explanation from extracted report text
    and the structured results DataFrame.

    This function does not diagnose disease.
    """

    report_text = clean_text(report_text)
    patient_fields = patient_fields or {}

    sections = []

    sections.append("MEDICAL REPORT EXPLANATION")
    sections.append(
        "This explanation describes the information extracted from the uploaded report. "
        "It is for education only and is not a diagnosis or treatment recommendation."
    )

    # Patient/report information
    if patient_fields:
        patient_lines = []
        for key, value in patient_fields.items():
            value = clean_text(value)
            if value:
                patient_lines.append(f"- {key.replace('_', ' ').title()}: {value}")

        if patient_lines:
            sections.append("1. PATIENT AND REPORT DETAILS\n" + "\n".join(patient_lines))

    # Test-by-test interpretation
    test_sections = []
    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        for _, row in results_df.iterrows():
            test = clean_text(row.get("Test", row.get("Test Name", "")))
            result = clean_text(row.get("Result", row.get("Value", "")))
            unit = clean_text(row.get("Unit", ""))
            reference = clean_text(
                row.get("Reference Range", row.get("Reference", row.get("Normal Range", "")))
            )
            status = clean_text(row.get("Status", ""))

            if not test:
                continue

            info = find_test_info(test)
            display_result = f"{result} {unit}".strip() or "Not clearly extracted"
            explanation = [
                f"Test: {test}",
                f"Reported result: {display_result}",
                f"Reference range: {reference or 'Not provided or not extracted'}",
                f"Reported status: {status or 'Not identified'}"
            ]

            if info:
                explanation.append(f"What it measures: {info['purpose']}")

                if any(word in status.lower() for word in ["high", "above", "elevated"]):
                    explanation.append(f"Possible meaning: {info['high']}")
                elif any(word in status.lower() for word in ["low", "below", "decreased"]):
                    explanation.append(f"Possible meaning: {info['low']}")
                else:
                    explanation.append(
                        "Interpretation: " + explain_status(status)
                    )
            else:
                explanation.append(
                    "What it means: This test name is not in the built-in explanation "
                    "dictionary. The result and range are shown as extracted, but a "
                    "reliable test-specific interpretation is not available here."
                )
                explanation.append(explain_status(status))

            test_sections.append("\n".join(explanation))

    if test_sections:
        sections.append(
            "2. TEST-BY-TEST EXPLANATION\n\n" + "\n\n".join(test_sections)
        )
    else:
        sections.append(
            "2. TEST-BY-TEST EXPLANATION\n"
            "No structured laboratory results were available to explain. "
            "Check whether the report text was extracted correctly and whether "
            "analyzer.py created rows in the results table."
        )

    # Full report text overview, so non-lab data is not silently ignored
    if report_text:
        lines = [
            re.sub(r"\s+", " ", line).strip()
            for line in report_text.splitlines()
            if line.strip()
        ]

        sections.append(
            "3. OTHER INFORMATION FOUND IN THE REPORT\n"
            "The original extracted text may include symptoms, clinical notes, "
            "specimen details, recommendations, and other information not represented "
            "in the laboratory results table."
        )

        if lines:
            # Show all extracted lines in chunks rather than silently dropping them.
            sections.append("EXTRACTED REPORT TEXT:\n" + "\n".join(lines))

    sections.append(
        "4. IMPORTANT LIMITATIONS\n"
        "- A reference range can vary by laboratory, age, sex, pregnancy status, and method.\n"
        "- The program may misread scanned text, decimal points, units, or reference ranges.\n"
        "- A high or low result does not by itself confirm a disease.\n"
        "- Unknown tests are displayed but are not given a guessed medical interpretation.\n"
        "- Ask a qualified healthcare professional to interpret the original report in context."
    )

    return "\n\n".join(sections)
