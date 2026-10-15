
import pandas as pd
from analyzer import find_test_name


TEST_INFO = {
    "hemoglobin": (
        "Measures the oxygen-carrying protein in red blood cells.",
        "A high result can have several causes, including dehydration.",
        "A low result can be associated with anemia, blood loss, or nutritional deficiencies."
    ),
    "wbc": (
        "Measures white blood cells, which help the body fight infections.",
        "A high result may occur with infection, inflammation, stress, or some medicines.",
        "A low result may occur with certain infections, medicines, or bone marrow conditions."
    ),
    "rbc": (
        "Measures the number of red blood cells that carry oxygen.",
        "A high result may occur with dehydration or other conditions.",
        "A low result may be associated with anemia or blood loss."
    ),
    "platelets": (
        "Measures platelets, which help blood clot.",
        "A high result can occur with inflammation, iron deficiency, or other causes.",
        "A low result can increase bleeding risk, depending on the level."
    ),
    "glucose": (
        "Measures blood sugar. Interpretation depends on whether the sample was fasting, random, or after a meal.",
        "A high result may indicate elevated blood sugar and could need follow-up testing.",
        "A low result may indicate low blood sugar; symptoms and circumstances matter."
    ),
    "hba1c": (
        "Estimates average blood glucose over approximately two to three months.",
        "A high result can indicate that average blood glucose has been elevated.",
        "A low result should be interpreted in context because some blood conditions can affect accuracy."
    ),
    "creatinine": (
        "A waste product used alongside other information to assess kidney function.",
        "A high result may occur with reduced kidney function, dehydration, or other causes.",
        "A low result may be associated with lower muscle mass and is not usually interpreted alone."
    ),
    "urea": (
        "Measures a waste product processed by the kidneys.",
        "A high result can occur with dehydration, kidney problems, or other causes.",
        "A low result may occur with low protein intake, overhydration, or some liver conditions."
    ),
    "total cholesterol": (
        "Measures total cholesterol in the blood.",
        "A high result may increase cardiovascular risk depending on the full lipid profile and other risk factors.",
        "A low result should be interpreted with the overall clinical picture."
    ),
    "ldl": (
        "LDL is often called 'bad' cholesterol because higher levels can contribute to plaque in arteries.",
        "A high result may increase cardiovascular risk; the target depends on individual risk.",
        "A low result is often desirable, but context still matters."
    ),
    "hdl": (
        "HDL is often called 'good' cholesterol and is part of cardiovascular risk assessment.",
        "Higher HDL is often associated with lower risk, but it is not protective in every circumstance.",
        "A low result can be associated with increased cardiovascular risk."
    ),
    "triglycerides": (
        "Measures a type of fat in the blood.",
        "A high result may be associated with metabolic factors, diet, medicines, or other conditions.",
        "A low result is often not concerning by itself."
    ),
    "sodium": (
        "An electrolyte important for fluid balance and nerve and muscle function.",
        "A high result may be related to water balance or other medical conditions.",
        "A low result has several possible causes and can be important if substantially reduced."
    ),
    "potassium": (
        "An electrolyte essential for muscle function and the heart's electrical activity.",
        "A high result can affect heart rhythm; sample damage can also cause a falsely high result.",
        "A low result can affect muscles and heart rhythm."
    ),
    "calcium": (
        "Supports bones, muscles, nerves, and other body functions.",
        "A high result has several possible causes and may require assessment.",
        "A low result may be associated with vitamin D, parathyroid, kidney, or other problems."
    ),
    "bilirubin": (
        "A substance produced when red blood cells break down.",
        "A high result can occur with liver or bile duct problems or increased red blood cell breakdown.",
        "A low result is usually not significant on its own."
    ),
    "alt": (
        "An enzyme commonly measured to assess liver cell irritation or injury.",
        "A high result has several possible causes, including liver inflammation, medicines, or fatty liver.",
        "A low result is generally not concerning by itself."
    ),
    "ast": (
        "An enzyme found in the liver and other tissues, including muscles.",
        "A high result may be associated with liver or muscle injury.",
        "A low result is generally not concerning by itself."
    ),
    "tsh": (
        "A hormone test used with thyroid hormone measurements to assess thyroid function.",
        "A high result can be associated with an underactive thyroid, but other results are needed.",
        "A low result can be associated with an overactive thyroid or thyroid medicine effects."
    ),
    "vitamin d": (
        "Assesses vitamin D status, which is important for bone and muscle health.",
        "A high result may indicate excessive supplementation and should be reviewed.",
        "A low result may indicate vitamin D deficiency."
    ),
    "vitamin b12": (
        "A vitamin important for red blood cell production and nerve function.",
        "A high result may reflect supplementation or other factors.",
        "A low result may be associated with anemia or nerve symptoms."
    ),
    "esr": (
        "A nonspecific measure that may rise with inflammation.",
        "A high result can occur with inflammation, infection, and many other conditions.",
        "A low result is generally less concerning but must be interpreted in context."
    ),
    "crp": (
        "A marker of inflammation in the body.",
        "A high result suggests inflammation but does not identify its cause.",
        "A low result generally indicates little measurable CRP-related inflammation at the time of testing."
    ),
    "uric acid": (
        "Measures uric acid in the blood and may be used when evaluating gout.",
        "A high result can increase the chance of gout in some people but does not diagnose gout alone.",
        "A low result is usually interpreted alongside symptoms and other results."
    ),
    "albumin": (
        "A major blood protein that can provide information about liver function, nutrition, and protein loss.",
        "A high result often occurs with dehydration.",
        "A low result has several possible causes, including liver disease, kidney protein loss, inflammation, or poor nutrition."
    ),
    "total protein": (
        "Measures the combined amount of several proteins in the blood.",
        "A high result may occur with dehydration or some inflammatory conditions.",
        "A low result can have several causes, including liver or kidney conditions and nutritional issues."
    )
}


def normalize_status(status):
    status = str(status or "").lower()

    if "above" in status or "high" in status or "elevated" in status:
        return "high"

    if "below" in status or "low" in status or "decreased" in status:
        return "low"

    if "within" in status or "normal" in status:
        return "normal"

    return "unknown"


def explain_report(report_text, results_df=None, patient_fields=None):
    report_text = report_text or ""
    patient_fields = patient_fields or {}

    sections = [
        "# MediLens — Medical Report Explanation",
        (
            "This is an educational explanation of the extracted report. "
            "It is not a diagnosis, and it should not be used to start, stop, "
            "or change treatment."
        )
    ]

    if patient_fields:
        details = []
        for key, value in patient_fields.items():
            if value is not None and str(value).strip():
                details.append(f"- **{key}:** {value}")

        if details:
            sections.append("## 1. Patient and Report Details\n" + "\n".join(details))

    explanations = []

    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        for _, row in results_df.iterrows():
            test = str(row.get("Test", "Unknown test"))
            result = str(row.get("Result", "Not extracted"))
            unit = str(row.get("Unit", "") or "").strip()
            reference = str(row.get("Reference Range", "") or "").strip()
            status = str(row.get("Status", "Needs review") or "Needs review")

            canonical, _, _ = find_test_name(test)
            info = TEST_INFO.get(canonical)

            parts = [
                f"### {test}",
                f"- **Result:** {result} {unit}".strip(),
                f"- **Reference range:** {reference or 'Not extracted'}",
                f"- **Status:** {status}"
            ]

            if info:
                purpose, high_text, low_text = info
                parts.append(f"- **What it measures:** {purpose}")

                status_type = normalize_status(status)

                if status_type == "high":
                    parts.append(f"- **Possible meaning:** {high_text}")
                elif status_type == "low":
                    parts.append(f"- **Possible meaning:** {low_text}")
                elif status_type == "normal":
                    parts.append(
                        "- **Interpretation:** The report marks this result as within "
                        "its reference range. This alone does not rule out all health conditions."
                    )
                else:
                    parts.append(
                        "- **Interpretation:** The status could not be confidently determined. "
                        "Check the value and reference range on the original report."
                    )
            else:
                parts.append(
                    "- **Explanation:** This test is not in the built-in test dictionary. "
                    "Its name and extracted values are displayed without guessing a medical meaning."
                )

            explanations.append("\n".join(parts))

    if explanations:
        sections.append(
            "## 2. Test-by-Test Explanation\n\n" + "\n\n".join(explanations)
        )
    else:
        sections.append(
            "## 2. Test-by-Test Explanation\n"
            "No laboratory rows were extracted. Check the extracted text and the analyzer parser."
        )

    if report_text.strip():
        sections.append(
            "## 3. Original Extracted Report Text\n"
            "Review this text against the uploaded report to check for OCR errors.\n\n"
            + report_text.strip()
        )

    sections.append(
        "## 4. Limitations and Next Steps\n"
        "- OCR may misread decimal points, test names, units, or reference ranges.\n"
        "- Reference intervals differ between laboratories and patient groups.\n"
        "- A high or low result does not confirm a disease by itself.\n"
        "- Review unexpected or concerning results with a qualified healthcare professional.\n"
        "- If you have severe or rapidly worsening symptoms, seek urgent medical care."
    )

    return "\n\n".join(sections)
