
import re
import pandas as pd


# --------------------------------------------------
# TEST ALIASES
# --------------------------------------------------

TEST_ALIASES = {
    "Fasting Blood Sugar": ["fasting blood sugar", "fasting glucose", "fbs"],
    "Random Blood Sugar": ["random blood sugar", "random glucose", "rbs"],
    "Hemoglobin": ["hemoglobin", "haemoglobin", "hb"],
    "WBC Count": ["wbc count", "white blood cell count", "white blood cells", "wbc"],
    "Platelets": ["platelet count", "platelets", "thrombocyte count"],
    "RBC Count": ["rbc count", "red blood cell count", "rbc"],
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


# --------------------------------------------------
# DETAILED TEST INFORMATION
# --------------------------------------------------

TEST_INFO = {
    "Hemoglobin": {
        "meaning": "Measures the oxygen-carrying protein in red blood cells.",
        "importance": (
            "Hemoglobin carries oxygen from the lungs to body tissues. "
            "It supports normal energy production and organ function."
        ),
        "low": [
            "Iron deficiency",
            "Vitamin B12 or folate deficiency",
            "Blood loss",
            "Some chronic illnesses"
        ],
        "high": [
            "Dehydration",
            "Living at high altitude",
            "Some lung or blood conditions"
        ],
        "follow_up": (
            "A clinician may review RBC count, hematocrit, MCV, iron studies, "
            "symptoms, and medical history."
        ),
    },

    "WBC Count": {
        "meaning": "Measures white blood cells that help defend the body.",
        "importance": (
            "White blood cells are part of the immune system. They help "
            "the body respond to infections and other immune challenges."
        ),
        "low": [
            "Some viral infections",
            "Certain medicines",
            "Some nutritional or bone marrow conditions"
        ],
        "high": [
            "Infections",
            "Inflammation",
            "Physical stress or certain medicines"
        ],
        "follow_up": (
            "The WBC differential, symptoms, medicines, and previous blood "
            "results may help explain an abnormal result."
        ),
    },

    "Platelets": {
        "meaning": "Measures the blood cells that help blood clot.",
        "importance": (
            "Platelets help form clots that reduce bleeding when a blood "
            "vessel is injured."
        ),
        "low": [
            "Some infections",
            "Certain medicines",
            "Immune-related conditions",
            "Reduced platelet production"
        ],
        "high": [
            "Recent infection or inflammation",
            "Iron deficiency",
            "Other reactive or blood-related conditions"
        ],
        "follow_up": (
            "Review the platelet count, previous results, bleeding or bruising "
            "symptoms, and other blood count findings with a clinician."
        ),
    },

    "Fasting Blood Sugar": {
        "meaning": "Measures blood glucose after fasting.",
        "importance": (
            "Glucose is an important energy source. This test helps assess "
            "blood sugar regulation when the fasting conditions are correct."
        ),
        "low": [
            "Some diabetes medicines",
            "Prolonged fasting",
            "Some hormonal or other medical conditions"
        ],
        "high": [
            "Diabetes or prediabetes",
            "Recent illness or stress",
            "Some medicines"
        ],
        "follow_up": (
            "Confirm fasting duration. A clinician may recommend repeat testing "
            "or HbA1c where appropriate."
        ),
    },

    "Random Blood Sugar": {
        "meaning": "Measures blood glucose at the time the sample is taken.",
        "importance": (
            "This test does not require fasting. Results can be affected by "
            "meals, timing, illness, and medicines."
        ),
        "low": [
            "Some glucose-lowering medicines",
            "Long periods without food",
            "Other medical conditions"
        ],
        "high": [
            "A recent meal",
            "Illness or physical stress",
            "Diabetes or other causes of elevated glucose"
        ],
        "follow_up": (
            "Consider meal timing, symptoms, and whether confirmatory glucose "
            "or HbA1c testing is appropriate."
        ),
    },

    "HbA1c": {
        "meaning": "Estimates average blood glucose over roughly two to three months.",
        "importance": (
            "HbA1c measures glucose attached to hemoglobin and is used to "
            "assess longer-term blood sugar levels."
        ),
        "low": [
            "Some conditions that shorten red blood cell lifespan",
            "Certain types of anemia or recent blood loss",
            "Low average glucose in some circumstances"
        ],
        "high": [
            "Persistently elevated blood glucose",
            "Diabetes or inadequate glucose control"
        ],
        "follow_up": (
            "Discuss diagnostic criteria with a clinician. Anemia and some "
            "other conditions can affect HbA1c accuracy."
        ),
    },

    "Creatinine": {
        "meaning": "Measures a waste product commonly used to assess kidney function.",
        "importance": (
            "Creatinine is produced by muscles and removed mainly by the kidneys. "
            "It is often considered together with estimated GFR (eGFR)."
        ),
        "low": [
            "Lower muscle mass",
            "Pregnancy or other physiological factors"
        ],
        "high": [
            "Reduced kidney filtration",
            "Dehydration",
            "Some medicines or recent intense exercise"
        ],
        "follow_up": (
            "Review eGFR, urine tests, hydration, medicines, previous results, "
            "and clinical history with a healthcare professional."
        ),
    },

    "TSH": {
        "meaning": "Measures thyroid-stimulating hormone.",
        "importance": (
            "TSH helps regulate thyroid hormone production. It is often "
            "interpreted with symptoms and sometimes free T4."
        ),
        "low": [
            "An overactive thyroid",
            "Some thyroid medicines",
            "Other medical conditions"
        ],
        "high": [
            "An underactive thyroid",
            "Some medicines or temporary thyroid changes"
        ],
        "follow_up": (
            "Review free T4, symptoms, medicines, relevant pregnancy status, "
            "and the laboratory reference range."
        ),
    },

    "Vitamin D": {
        "meaning": "Usually measures 25-hydroxyvitamin D to assess vitamin D status.",
        "importance": (
            "Vitamin D supports calcium absorption and bone and muscle health."
        ),
        "low": [
            "Limited sun exposure",
            "Low dietary intake",
            "Reduced absorption or some medical conditions"
        ],
        "high": [
            "Excessive vitamin D supplementation",
            "Some less common medical conditions"
        ],
        "follow_up": (
            "Review the exact value, unit, calcium result, supplement use, "
            "and medical history before changing supplements."
        ),
    },

    "Total Cholesterol": {
        "meaning": "Measures the total cholesterol in the blood.",
        "importance": (
            "Cholesterol is needed by the body, but lipid levels help assess "
            "cardiovascular risk when considered together."
        ),
        "low": [
            "Some nutritional or medical conditions",
            "Certain medicines"
        ],
        "high": [
            "Dietary and genetic factors",
            "Some medical conditions",
            "Other cardiovascular risk factors"
        ],
        "follow_up": (
            "Review LDL, HDL, triglycerides, blood pressure, diabetes status, "
            "and family history with a healthcare professional."
        ),
    },

    "Vitamin B12": {
        "meaning": "Measures vitamin B12, which supports nerves and red blood cells.",
        "importance": (
            "Vitamin B12 is needed for normal nerve function and blood cell "
            "production."
        ),
        "low": [
            "Low dietary intake",
            "Reduced absorption",
            "Some medicines or digestive conditions"
        ],
        "high": [
            "Vitamin B12 supplements",
            "Some liver or other medical conditions"
        ],
        "follow_up": (
            "A clinician may consider symptoms, blood counts, diet, supplements, "
            "and additional testing where appropriate."
        ),
    },
}


# --------------------------------------------------
# TEST IDENTIFICATION
# --------------------------------------------------

def identify_test(test_name):
    text = str(test_name or "").strip().lower()

    for canonical in TEST_ALIASES:
        if text == canonical.lower():
            return canonical

    aliases = sorted(
        [
            (alias, canonical)
            for canonical, names in TEST_ALIASES.items()
            for alias in names
        ],
        key=lambda item: len(item[0]),
        reverse=True,
    )

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


# --------------------------------------------------
# DETAILED EXPLANATION FOR ONE TEST
# --------------------------------------------------

def explain_test(
    test_name,
    result,
    unit="",
    reference_range="",
    status=""
):
    canonical = identify_test(test_name)
    info = TEST_INFO.get(canonical, {})

    meaning = info.get(
        "meaning",
        "This test does not yet have a detailed entry in the built-in library."
    )

    importance = info.get(
        "importance",
        "Interpret this test using its laboratory reference range and clinical context."
    )

    normalized = normalize_status(status)

    if normalized == "normal":
        interpretation = (
            "The report marks this result within its reference range. "
            "This does not rule out every medical condition."
        )
        causes = []

    elif normalized == "low":
        interpretation = (
            "The report marks this result below its reference range. "
            "The significance depends on the actual value and clinical context."
        )
        causes = info.get("low", [])

    elif normalized == "high":
        interpretation = (
            "The report marks this result above its reference range. "
            "The significance depends on the actual value and clinical context."
        )
        causes = info.get("high", [])

    else:
        interpretation = (
            "The result could not be classified reliably. Check the original "
            "report and reference range."
        )
        causes = []

    result_text = str(result if result is not None else "")
    if unit and str(unit).strip():
        result_text += " " + str(unit).strip()

    return {
        "Test": canonical,
        "Result": result_text,
        "Reference Range": str(reference_range or "Not provided"),
        "Status": str(status or "Needs review"),
        "Meaning": meaning,
        "Importance": importance,
        "Interpretation": interpretation,
        "Possible Causes": causes,
        "Follow-up": info.get(
            "follow_up",
            "Discuss unexpected results with a qualified healthcare professional."
        ),
    }


# --------------------------------------------------
# DETAILED EXPLANATION FOR THE WHOLE REPORT
# --------------------------------------------------

def explain_report(report_text="", results_df=None, patient_fields=None):
    patient_fields = patient_fields or {}

    if not isinstance(results_df, pd.DataFrame):
        results_df = pd.DataFrame()

    detailed_results = []

    for _, row in results_df.iterrows():
        test_name = row.get("Test", "")

        if not str(test_name).strip():
            continue

        detailed_results.append(
            explain_test(
                test_name=test_name,
                result=row.get("Result", ""),
                unit=row.get("Unit", ""),
                reference_range=row.get("Reference Range", ""),
                status=row.get("Status", ""),
            )
        )

    counts = {"normal": 0, "low": 0, "high": 0, "unknown": 0}

    for item in detailed_results:
        counts[normalize_status(item["Status"])] += 1

    summary = (
        f"Reviewed {len(detailed_results)} extracted result(s): "
        f"{counts['normal']} within range, "
        f"{counts['low']} below range, "
        f"{counts['high']} above range, and "
        f"{counts['unknown']} needing review."
    )

    if not detailed_results:
        summary = (
            "No laboratory results were extracted. Check the uploaded report "
            "and the analyzer output."
        )

    return {
        "patient": patient_fields,
        "summary": summary,
        "results": detailed_results,
        "general_notes": [
            "These explanations use a built-in information library, not a generative AI model.",
            "Possible causes are not a diagnosis.",
            "Reference ranges can vary between laboratories and patient groups.",
            "Verify extracted values against the original report.",
            "Consult a qualified healthcare professional about medical results.",
        ],
    }
