
import pandas as pd

from analyzer import find_test_name


# --------------------------------------------------
# TEST INFORMATION
# --------------------------------------------------

TEST_INFO = {
    "Hemoglobin": {
        "meaning": "Hemoglobin is a protein in red blood cells that carries oxygen.",
        "low": "A low value can be associated with anemia or other conditions.",
        "high": "A high value can be associated with dehydration or other conditions.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "WBC Count": {
        "meaning": "White blood cells help the body fight infections.",
        "low": "A low value can have several causes and may need medical review.",
        "high": "A high value can occur with infections, inflammation, or other conditions.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Platelets": {
        "meaning": "Platelets help blood clot.",
        "low": "A low value may increase bleeding risk, depending on the level and cause.",
        "high": "A high value can have several causes and may need medical review.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Fasting Blood Sugar": {
        "meaning": "Fasting blood sugar measures glucose in the blood after fasting.",
        "low": "A low result may indicate low blood glucose and needs context.",
        "high": "A high result may need follow-up testing and professional interpretation.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Random Blood Sugar": {
        "meaning": "Random blood sugar measures glucose without requiring fasting.",
        "low": "A low result may indicate low blood glucose and needs context.",
        "high": "A high result may need follow-up testing and professional interpretation.",
        "normal": "Interpret the result using the report's reference range and clinical context.",
    },
    "HbA1c": {
        "meaning": "HbA1c estimates average blood glucose over roughly the previous 2–3 months.",
        "low": "A low value should be interpreted in clinical context.",
        "high": "A high value can indicate elevated average blood glucose and may need follow-up.",
        "normal": "Compare the value with the laboratory's reference or decision limits.",
    },
    "Creatinine": {
        "meaning": "Creatinine is a waste product used to help assess kidney function.",
        "low": "A low value can be associated with muscle mass and other factors.",
        "high": "A high value may need assessment of kidney function and other factors.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Urea": {
        "meaning": "Urea is a waste product that can help assess kidney function and hydration.",
        "low": "A low value can have several causes and needs context.",
        "high": "A high value can be associated with dehydration or kidney-related issues.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Total Cholesterol": {
        "meaning": "Total cholesterol measures several types of cholesterol in the blood.",
        "low": "Interpret the result alongside other lipid measurements and clinical context.",
        "high": "A high value may contribute to cardiovascular risk, depending on the full lipid profile.",
        "normal": "Compare the result with the laboratory's range and individual risk factors.",
    },
    "LDL Cholesterol": {
        "meaning": "LDL cholesterol is often called bad cholesterol because higher levels can contribute to plaque buildup.",
        "low": "Interpret the value with the full lipid profile and clinical context.",
        "high": "A high value may increase cardiovascular risk.",
        "normal": "The result should be interpreted against the person's risk-based target.",
    },
    "HDL Cholesterol": {
        "meaning": "HDL cholesterol helps transport cholesterol away from tissues.",
        "low": "A low value can be one factor in cardiovascular risk assessment.",
        "high": "Interpret the value in the context of the complete lipid profile.",
        "normal": "Interpret the result alongside other cholesterol measurements.",
    },
    "Triglycerides": {
        "meaning": "Triglycerides are a type of fat found in the blood.",
        "low": "A low result is often interpreted in context.",
        "high": "A high value may need follow-up and review of fasting status.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Sodium": {
        "meaning": "Sodium is an electrolyte that helps regulate fluid balance and nerve function.",
        "low": "A low value can have multiple causes and may need medical review.",
        "high": "A high value can be associated with fluid balance problems.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Potassium": {
        "meaning": "Potassium is an electrolyte important for muscles, nerves, and heart function.",
        "low": "A low value may affect muscle or heart function and needs context.",
        "high": "A high value may affect heart rhythm and needs prompt professional assessment.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Calcium": {
        "meaning": "Calcium supports bones, muscles, nerves, and other body functions.",
        "low": "A low value can have several causes and may need review.",
        "high": "A high value can have several causes and may need review.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Bilirubin": {
        "meaning": "Bilirubin is a substance produced when red blood cells break down.",
        "low": "A low value is often not significant by itself.",
        "high": "A high value may need assessment of liver function and other causes.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "ALT": {
        "meaning": "ALT is an enzyme commonly measured when assessing liver health.",
        "low": "A low value is often not concerning by itself.",
        "high": "A high value may indicate liver cell irritation or injury, among other causes.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "AST": {
        "meaning": "AST is an enzyme found in the liver and other tissues.",
        "low": "A low value is often not concerning by itself.",
        "high": "A high value can have liver-related or other causes.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "TSH": {
        "meaning": "TSH is a hormone used to help assess thyroid function.",
        "low": "A low value may be associated with several thyroid or other conditions.",
        "high": "A high value may be associated with reduced thyroid function.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Vitamin D": {
        "meaning": "Vitamin D helps the body absorb calcium and supports bone health.",
        "low": "A low value may indicate vitamin D insufficiency or deficiency, depending on the lab criteria.",
        "high": "A high value should be reviewed in the context of supplements and clinical history.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Vitamin B12": {
        "meaning": "Vitamin B12 supports nerve function and red blood cell production.",
        "low": "A low value may need evaluation for deficiency and its cause.",
        "high": "A high value may be related to supplements or other factors.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "ESR": {
        "meaning": "ESR is a nonspecific measure that can indicate inflammation.",
        "low": "A low value is usually interpreted with the rest of the report.",
        "high": "A high value can occur with inflammation and many other conditions.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "CRP": {
        "meaning": "CRP is a protein that can rise with inflammation.",
        "low": "A low value may indicate little measurable inflammation at the time of testing.",
        "high": "A high value can occur with infections and other inflammatory conditions.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Uric Acid": {
        "meaning": "Uric acid is produced when the body breaks down purines.",
        "low": "A low value is interpreted in context.",
        "high": "A high value may be associated with gout or kidney-related factors, but does not diagnose gout by itself.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Albumin": {
        "meaning": "Albumin is a protein made by the liver that helps maintain fluid balance.",
        "low": "A low value can have several causes, including liver, kidney, or nutritional issues.",
        "high": "A high value can be associated with dehydration.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Total Protein": {
        "meaning": "Total protein measures albumin and globulins in the blood.",
        "low": "A low value can have several causes and may need review.",
        "high": "A high value can have several causes and may need review.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "MCV": {
        "meaning": "MCV measures the average size of red blood cells.",
        "low": "A low value can occur with iron deficiency and some other conditions.",
        "high": "A high value can occur with vitamin deficiencies and other conditions.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "MCH": {
        "meaning": "MCH measures the average amount of hemoglobin in a red blood cell.",
        "low": "A low value can occur with some types of anemia.",
        "high": "A high value should be interpreted with other blood count results.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "MCHC": {
        "meaning": "MCHC measures the concentration of hemoglobin inside red blood cells.",
        "low": "A low value can occur with some types of anemia.",
        "high": "A high value may need review alongside other blood count results.",
        "normal": "The result is within the reference range provided in the report.",
    },
    "Hematocrit": {
        "meaning": "Hematocrit is the proportion of blood volume made up of red blood cells.",
        "low": "A low value can occur with anemia or other conditions.",
        "high": "A high value can occur with dehydration or other conditions.",
        "normal": "The result is within the reference range provided in the report.",
    },
}


# --------------------------------------------------
# STATUS NORMALIZATION
# --------------------------------------------------

def normalize_status(status):
    status = str(status or "").strip().lower()

    if status in {"within range", "normal", "within normal range"}:
        return "normal"

    if status in {"below range", "low", "below normal"}:
        return "low"

    if status in {"above range", "high", "above normal"}:
        return "high"

    return "unknown"


# --------------------------------------------------
# EXPLAIN ONE TEST
# --------------------------------------------------

def explain_test(test_name, result, unit="", reference_range="", status=""):
    # Use the same canonical test names as analyzer.py.
    canonical_name = find_test_name(str(test_name))

    if not canonical_name:
        canonical_name = str(test_name).strip()

    info = TEST_INFO.get(canonical_name)

    if not info:
        return {
            "Test": canonical_name,
            "Result": result,
            "Reference Range": reference_range or "Not provided",
            "Status": status or "Needs review",
            "Meaning": "This test is not yet included in the application's explanation library.",
            "Explanation": (
                "Compare this result with the reference range printed by the laboratory. "
                "A healthcare professional should interpret it with the patient's history."
            ),
        }

    normalized = normalize_status(status)

    if normalized == "normal":
        explanation = info["normal"]
    elif normalized == "low":
        explanation = info["low"]
    elif normalized == "high":
        explanation = info["high"]
    else:
        explanation = (
            "The result could not be classified reliably from the available reference range. "
            "Please check the original report."
        )

    result_text = str(result)
    if unit:
        result_text += f" {unit}"

    return {
        "Test": canonical_name,
        "Result": result_text,
        "Reference Range": reference_range or "Not provided",
        "Status": status or "Needs review",
        "Meaning": info["meaning"],
        "Explanation": explanation,
    }


# --------------------------------------------------
# EXPLAIN THE UPLOADED REPORT
# --------------------------------------------------

def explain_report(report_text="", results_df=None, patient_fields=None):
    """
    Creates explanations only from the supplied report and extracted results.
    This function does not call an external AI service or require an API key.
    """

    patient_fields = patient_fields or {}

    if results_df is None or not isinstance(results_df, pd.DataFrame):
        results_df = pd.DataFrame()

    report_text = report_text or ""

    report_is_empty = not report_text.strip() and results_df.empty

    if report_is_empty:
        return {
            "patient": patient_fields,
            "summary": "No report text or laboratory results were provided.",
            "results": [],
            "general_notes": [
                "Upload a readable medical report to begin.",
                "Check that the report text was extracted successfully.",
            ],
        }

    explained_results = []

    if not results_df.empty:
        for _, row in results_df.iterrows():
            test_name = str(row.get("Test", "")).strip()

            if not test_name:
                continue

            explanation = explain_test(
                test_name=test_name,
                result=row.get("Result", ""),
                unit=row.get("Unit", ""),
                reference_range=row.get("Reference Range", ""),
                status=row.get("Status", ""),
            )

            explained_results.append(explanation)

    if explained_results:
        normal_count = sum(
            1 for item in explained_results
            if normalize_status(item["Status"]) == "normal"
        )

        low_count = sum(
            1 for item in explained_results
            if normalize_status(item["Status"]) == "low"
        )

        high_count = sum(
            1 for item in explained_results
            if normalize_status(item["Status"]) == "high"
        )

        unknown_count = len(explained_results) - (
            normal_count + low_count + high_count
        )

        summary = (
            f"Extracted {len(explained_results)} laboratory result(s): "
            f"{normal_count} within range, {low_count} below range, "
            f"{high_count} above range, and {unknown_count} needing review."
        )
    else:
        summary = (
            "No laboratory results could be extracted from this report. "
            "Check whether the uploaded file is readable and contains test results."
        )

    general_notes = [
        "Explanations are generated from the application's built-in information library, not an external AI model.",
        "Reference ranges can differ between laboratories, age groups, and other patient factors.",
        "A result within range does not rule out every medical condition.",
        "This application is educational only and does not provide a diagnosis or treatment recommendation.",
        "Consult a qualified healthcare professional for interpretation of actual medical results.",
    ]

    return {
        "patient": patient_fields,
        "summary": summary,
        "results": explained_results,
        "general_notes": general_notes,
    }
