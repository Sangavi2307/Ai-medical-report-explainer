
import pandas as pd


# This file is independent of analyzer.py.
# It does not require an API key or external AI service.

TEST_ALIASES = {
    "Fasting Blood Sugar": [
        "fasting blood sugar", "fasting glucose", "fbs"
    ],
    "Random Blood Sugar": ["random blood sugar", "rbs"],
    "Hemoglobin": ["hemoglobin", "haemoglobin"],
    "WBC Count": [
        "wbc count", "white blood cell count",
        "white blood cells", "wbc"
    ],
    "Platelets": [
        "platelet count", "platelets", "thrombocyte count"
    ],
    "RBC Count": [
        "rbc count", "red blood cell count", "rbc"
    ],
    "HbA1c": ["hba1c", "glycated hemoglobin"],
    "Creatinine": ["serum creatinine", "creatinine"],
    "Urea": ["blood urea", "serum urea", "urea"],
    "Total Cholesterol": ["total cholesterol", "cholesterol"],
    "LDL Cholesterol": ["ldl cholesterol", "ldl"],
    "HDL Cholesterol": ["hdl cholesterol", "hdl"],
    "Triglycerides": ["triglycerides", "triglyceride"],
    "Sodium": ["serum sodium", "sodium"],
    "Potassium": ["serum potassium", "potassium"],
    "Calcium": ["serum calcium", "calcium"],
    "Bilirubin": ["total bilirubin", "bilirubin"],
    "ALT": ["sgpt", "alanine aminotransferase", "alt"],
    "AST": ["sgot", "aspartate aminotransferase", "ast"],
    "TSH": ["thyroid stimulating hormone", "tsh"],
    "Vitamin D": ["25-oh vitamin d", "vitamin d"],
    "Vitamin B12": ["vitamin b12", "b12"],
    "ESR": ["erythrocyte sedimentation rate", "esr"],
    "CRP": ["c-reactive protein", "crp"],
    "Uric Acid": ["serum uric acid", "uric acid"],
    "Albumin": ["serum albumin", "albumin"],
    "Total Protein": ["total protein"],
    "MCV": ["mean corpuscular volume", "mcv"],
    "MCH": ["mean corpuscular hemoglobin", "mch"],
    "MCHC": ["mean corpuscular hemoglobin concentration", "mchc"],
    "Hematocrit": ["hematocrit", "packed cell volume", "pcv"],
}

TEST_INFO = {
    "Hemoglobin": (
        "Measures the oxygen-carrying protein in red blood cells.",
        "A low result can be associated with anemia or other conditions.",
        "A high result can occur with dehydration or other conditions.",
    ),
    "WBC Count": (
        "Measures white blood cells, which help the body fight infections.",
        "A low result can have several causes and may need review.",
        "A high result can occur with infection, inflammation, or other conditions.",
    ),
    "Platelets": (
        "Measures blood cells that help blood clot.",
        "A low result may increase bleeding risk, depending on the level and cause.",
        "A high result can have several causes and may need review.",
    ),
    "Fasting Blood Sugar": (
        "Measures blood glucose after fasting.",
        "A low result may indicate low blood glucose and needs context.",
        "A high result may need follow-up testing and professional interpretation.",
    ),
    "Random Blood Sugar": (
        "Measures blood glucose without requiring fasting.",
        "A low result needs interpretation in clinical context.",
        "A high result may need follow-up testing and professional interpretation.",
    ),
    "HbA1c": (
        "Estimates average blood glucose over roughly the previous two to three months.",
        "A low result should be interpreted in clinical context.",
        "A high result may indicate elevated average blood glucose.",
    ),
    "Creatinine": (
        "A blood measurement commonly used when assessing kidney function.",
        "A low result can be associated with muscle mass and other factors.",
        "A high result may require assessment of kidney function and other factors.",
    ),
    "Urea": (
        "A waste product used alongside other measurements to assess health.",
        "A low result has several possible causes.",
        "A high result can occur with dehydration or kidney-related issues.",
    ),
    "Total Cholesterol": (
        "Measures the total amount of cholesterol in the blood.",
        "Interpret alongside the full lipid profile and clinical context.",
        "A high result may contribute to cardiovascular risk.",
    ),
    "LDL Cholesterol": (
        "LDL is often called bad cholesterol because it can contribute to plaque buildup.",
        "Interpret alongside the complete lipid profile.",
        "A high result may increase cardiovascular risk.",
    ),
    "HDL Cholesterol": (
        "HDL helps transport cholesterol away from tissues.",
        "A low result can be one factor in cardiovascular risk assessment.",
        "Interpret the result alongside the complete lipid profile.",
    ),
    "Triglycerides": (
        "Measures a type of fat found in the blood.",
        "Interpret a low result in clinical context.",
        "A high result may need follow-up and review of fasting status.",
    ),
    "Sodium": (
        "An electrolyte involved in fluid balance and nerve function.",
        "A low result can have multiple causes and may need medical review.",
        "A high result can be associated with fluid balance problems.",
    ),
    "Potassium": (
        "An electrolyte important for muscles, nerves, and heart function.",
        "A low result may affect muscle or heart function.",
        "A high result may affect heart rhythm and needs prompt professional assessment.",
    ),
    "Calcium": (
        "Supports bones, muscles, nerves, and other body functions.",
        "A low result can have several causes.",
        "A high result can have several causes.",
    ),
    "Bilirubin": (
        "A substance produced when red blood cells break down.",
        "Interpret a low result in clinical context.",
        "A high result may require assessment of liver function and other causes.",
    ),
    "ALT": (
        "An enzyme commonly measured when assessing liver health.",
        "Interpret a low result in clinical context.",
        "A high result may indicate liver cell irritation or injury, among other causes.",
    ),
    "AST": (
        "An enzyme found in the liver and other tissues.",
        "Interpret a low result in clinical context.",
        "A high result can have liver-related or other causes.",
    ),
    "TSH": (
        "A hormone test used to help assess thyroid function.",
        "A low result can have several possible explanations.",
        "A high result can be associated with reduced thyroid function.",
    ),
    "Vitamin D": (
        "Helps the body absorb calcium and supports bone health.",
        "A low result may indicate insufficiency or deficiency, depending on lab criteria.",
        "A high result should be reviewed with supplement use and clinical history.",
    ),
    "Vitamin B12": (
        "Supports nerve function and red blood cell production.",
        "A low result may need evaluation for deficiency.",
        "A high result may be related to supplements or other factors.",
    ),
    "ESR": (
        "A nonspecific measurement that can indicate inflammation.",
        "Interpret with the rest of the report.",
        "A high result can occur with inflammation and many other conditions.",
    ),
    "CRP": (
        "A protein that can rise when inflammation is present.",
        "Interpret with the laboratory range and clinical context.",
        "A high result can occur with infections and other inflammatory conditions.",
    ),
    "Uric Acid": (
        "A substance produced when the body breaks down purines.",
        "Interpret a low result in context.",
        "A high result may be associated with gout but does not diagnose it by itself.",
    ),
    "Albumin": (
        "A protein made by the liver that helps maintain fluid balance.",
        "A low result can have liver, kidney, nutritional, or other causes.",
        "A high result can be associated with dehydration.",
    ),
    "Total Protein": (
        "Measures albumin and globulins in the blood.",
        "A low result can have several causes.",
        "A high result can have several causes.",
    ),
    "MCV": (
        "Measures the average size of red blood cells.",
        "A low result can occur with iron deficiency and some other conditions.",
        "A high result can occur with vitamin deficiencies and other conditions.",
    ),
    "MCH": (
        "Measures the average amount of hemoglobin in a red blood cell.",
        "A low result can occur with some types of anemia.",
        "Interpret a high result alongside other blood count results.",
    ),
    "MCHC": (
        "Measures the concentration of hemoglobin inside red blood cells.",
        "A low result can occur with some types of anemia.",
        "Interpret a high result alongside other blood count results.",
    ),
    "Hematocrit": (
        "Measures the proportion of blood volume made up of red blood cells.",
        "A low result can occur with anemia or other conditions.",
        "A high result can occur with dehydration or other conditions.",
    ),
}


def identify_test(test_name):
    """Return a canonical test name without importing analyzer.py."""
    text = str(test_name or "").strip().lower()

    # Exact canonical-name match first.
    for canonical in TEST_ALIASES:
        if text == canonical.lower():
            return canonical

    # Prefer longer aliases to avoid matching a shorter name first.
    aliases = sorted(
        [
            (alias, canonical)
            for canonical, names in TEST_ALIASES.items()
            for alias in names
        ],
        key=lambda item: len(item[0]),
        reverse=True,
    )

    import re

    for alias, canonical in aliases:
        pattern = r"(?<![a-z])" + re.escape(alias) + r"(?![a-z])"
        if re.search(pattern, text):
            return canonical

    return str(test_name or "Unknown test").strip()


def normalize_status(status):
    status = str(status or "").strip().lower()

    if status in {"within range", "normal", "within normal range"}:
        return "normal"
    if status in {"below range", "low", "below normal"}:
        return "low"
    if status in {"above range", "high", "above normal"}:
        return "high"

    return "unknown"


def explain_test(test_name, result, unit="", reference_range="", status=""):
    canonical = identify_test(test_name)
    info = TEST_INFO.get(canonical)

    if info:
        meaning, low_explanation, high_explanation = info
    else:
        meaning = (
            "This laboratory test does not yet have a detailed explanation "
            "in the application's built-in library."
        )
        low_explanation = (
            "Compare the result with the laboratory's reference range."
        )
        high_explanation = (
            "Compare the result with the laboratory's reference range."
        )

    normalized = normalize_status(status)

    if normalized == "normal":
        explanation = (
            "The result is marked within the reference range supplied by "
            "the report. This does not rule out every medical condition."
        )
    elif normalized == "low":
        explanation = low_explanation
    elif normalized == "high":
        explanation = high_explanation
    else:
        explanation = (
            "The result could not be classified reliably. Check the original "
            "report and consult a qualified healthcare professional."
        )

    result_text = str(result if result is not None else "")
    if unit and str(unit).strip():
        result_text += " " + str(unit).strip()

    return {
        "Test": canonical,
        "Result": result_text,
        "Reference Range": str(reference_range or "Not provided"),
        "Status": str(status or "Needs review"),
        "Meaning": meaning,
        "Explanation": explanation,
    }


def explain_report(report_text="", results_df=None, patient_fields=None):
    """
    Explain results extracted from the uploaded report.
    No API key or external AI service is required.
    """

    patient_fields = patient_fields or {}

    if not isinstance(results_df, pd.DataFrame):
        results_df = pd.DataFrame()

    if results_df.empty:
        summary = (
            "No laboratory results were extracted. Check the uploaded file "
            "and the analyzer output."
        )
        explained_results = []
    else:
        explained_results = []

        for _, row in results_df.iterrows():
            test_name = row.get("Test", "")
            if not str(test_name).strip():
                continue

            explained_results.append(
                explain_test(
                    test_name=test_name,
                    result=row.get("Result", ""),
                    unit=row.get("Unit", ""),
                    reference_range=row.get("Reference Range", ""),
                    status=row.get("Status", ""),
                )
            )

        counts = {"normal": 0, "low": 0, "high": 0, "unknown": 0}

        for item in explained_results:
            category = normalize_status(item["Status"])
            counts[category] += 1

        summary = (
            f"Analyzed {len(explained_results)} extracted result(s): "
            f"{counts['normal']} within range, "
            f"{counts['low']} below range, "
            f"{counts['high']} above range, and "
            f"{counts['unknown']} needing review."
        )

    return {
        "patient": patient_fields,
        "summary": summary,
        "results": explained_results,
        "general_notes": [
            "These explanations use a built-in information library, not a generative AI model.",
            "Reference ranges can vary between laboratories and patient groups.",
            "Results must be interpreted with symptoms, history, and other findings.",
            "This application is for educational purposes only; it does not diagnose conditions or recommend treatment.",
            "Consult a qualified healthcare professional about actual medical results.",
        ],
    }
