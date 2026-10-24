
import re
import pandas as pd


# ============================================================
# MEDILENS - MEDICAL REPORT EXPLANATION LIBRARY
# Educational explanations only. This is not a diagnostic tool.
# ============================================================

TEST_ALIASES = {
    "Hemoglobin": ["hemoglobin", "haemoglobin", "hb", "hgb"],
    "WBC Count": [
        "wbc", "white blood cell", "white blood cells",
        "total leukocyte count", "total leucocyte count", "tlc",
        "leukocyte count", "leucocyte count"
    ],
    "RBC Count": [
        "rbc", "red blood cell", "red blood cells",
        "erythrocyte count"
    ],
    "Platelets": [
        "platelet", "platelets", "platelet count", "plt",
        "thrombocyte count"
    ],
    "Fasting Blood Sugar": [
        "fasting blood sugar", "fasting glucose",
        "fasting blood glucose", "fbs", "fasting plasma glucose"
    ],
    "Random Blood Sugar": [
        "random blood sugar", "random glucose",
        "random blood glucose", "rbs"
    ],
    "Postprandial Blood Sugar": [
        "postprandial glucose", "post prandial glucose",
        "ppbs", "2 hour glucose", "2-hour glucose"
    ],
    "HbA1c": [
        "hba1c", "glycated hemoglobin",
        "glycosylated hemoglobin", "glycohemoglobin"
    ],
    "Creatinine": ["creatinine", "serum creatinine"],
    "Urea": ["urea", "serum urea", "blood urea"],
    "BUN": ["bun", "blood urea nitrogen"],
    "eGFR": [
        "egfr", "estimated glomerular filtration rate",
        "glomerular filtration rate"
    ],
    "Total Cholesterol": ["total cholesterol", "cholesterol total"],
    "LDL Cholesterol": [
        "ldl cholesterol", "ldl-c", "low density lipoprotein", "ldl"
    ],
    "HDL Cholesterol": [
        "hdl cholesterol", "hdl-c", "high density lipoprotein", "hdl"
    ],
    "Triglycerides": ["triglyceride", "triglycerides", "tg"],
    "TSH": ["tsh", "thyroid stimulating hormone", "thyrotropin"],
    "T3": ["total t3", "free t3", "triiodothyronine"],
    "T4": ["total t4", "free t4", "thyroxine"],
    "Vitamin D": [
        "25-oh vitamin d", "25 oh vitamin d",
        "25-hydroxy vitamin d", "25 hydroxy vitamin d", "vitamin d"
    ],
    "Vitamin B12": ["vitamin b12", "vit b12", "cobalamin", "b12"],
    "Calcium": ["calcium", "serum calcium"],
    "Sodium": ["sodium", "serum sodium", "na"],
    "Potassium": ["potassium", "serum potassium", "k"],
    "Chloride": ["chloride", "serum chloride"],
    "Bilirubin": [
        "total bilirubin", "bilirubin total", "serum bilirubin", "bilirubin"
    ],
    "ALT": ["alanine aminotransferase", "alt", "sgpt"],
    "AST": ["aspartate aminotransferase", "ast", "sgot"],
    "ALP": ["alkaline phosphatase", "alp"],
    "Albumin": ["albumin", "serum albumin"],
    "Total Protein": ["total protein", "serum total protein"],
    "CRP": ["c-reactive protein", "c reactive protein", "crp"],
    "ESR": ["erythrocyte sedimentation rate", "esr"],
    "Uric Acid": ["uric acid", "serum uric acid"],
    "Urine Protein": ["urine protein", "urine albumin", "protein urine"],
    "Urine Glucose": ["urine glucose", "glucose urine"],
    "Urine Ketones": ["urine ketones", "ketone bodies urine"],
    "Urine Blood": ["urine blood", "blood in urine", "urine occult blood"],
    "MCV": ["mcv", "mean corpuscular volume"],
    "MCH": ["mch", "mean corpuscular hemoglobin", "mean corpuscular haemoglobin"],
    "MCHC": [
        "mchc", "mean corpuscular hemoglobin concentration",
        "mean corpuscular haemoglobin concentration"
    ],
    "Hematocrit": [
        "hematocrit", "haematocrit", "packed cell volume", "pcv"
    ],
}


# ============================================================
# EDUCATIONAL TEST INFORMATION
# ============================================================

TEST_INFO = {
    "Hemoglobin": {
        "meaning": "Measures the oxygen-carrying protein in red blood cells.",
        "importance": "Helps assess anemia and other blood-related conditions.",
        "low_causes": [
            "Iron deficiency", "Vitamin B12 or folate deficiency",
            "Blood loss", "Some chronic medical conditions"
        ],
        "high_causes": [
            "Dehydration", "High-altitude exposure",
            "Smoking-related effects", "Some conditions increasing red blood cell production"
        ],
        "follow_up": "Discuss the result with a healthcare professional. Other blood count and iron tests may be considered."
    },
    "WBC Count": {
        "meaning": "Measures white blood cells that help the body fight infections.",
        "importance": "Can provide information about infection, inflammation, and immune conditions.",
        "low_causes": [
            "Some viral infections", "Medication effects",
            "Autoimmune conditions", "Some bone marrow disorders"
        ],
        "high_causes": [
            "Infection", "Inflammation", "Physical stress",
            "Medication effects", "Some blood disorders"
        ],
        "follow_up": "Review the differential count, symptoms, medicines, and complete blood count with a clinician."
    },
    "RBC Count": {
        "meaning": "Measures the number of red blood cells.",
        "importance": "Helps assess oxygen transport and blood-related conditions.",
        "low_causes": [
            "Anemia", "Blood loss", "Nutritional deficiencies",
            "Some chronic illnesses"
        ],
        "high_causes": [
            "Dehydration", "High-altitude exposure",
            "Smoking-related effects", "Some blood conditions"
        ],
        "follow_up": "Interpret together with hemoglobin, hematocrit, MCV, and other blood count results."
    },
    "Platelets": {
        "meaning": "Measures blood components that help form clots and stop bleeding.",
        "importance": "Helps assess bleeding and clotting-related concerns.",
        "low_causes": [
            "Some viral infections", "Medication effects",
            "Immune-related platelet destruction", "Some liver or spleen conditions"
        ],
        "high_causes": [
            "Recent infection", "Inflammation", "Iron deficiency",
            "Some bone marrow disorders"
        ],
        "follow_up": "Discuss unusual bruising, bleeding, clotting symptoms, or abnormal results with a clinician."
    },
    "Fasting Blood Sugar": {
        "meaning": "Measures blood glucose after the laboratory-specified fasting period.",
        "importance": "Used to screen for and monitor blood glucose disorders.",
        "low_causes": [
            "Glucose-lowering medicines", "Prolonged fasting",
            "Some hormonal or liver conditions"
        ],
        "high_causes": [
            "Prediabetes or diabetes", "Acute illness or stress",
            "Some medication effects"
        ],
        "follow_up": "Confirm fasting conditions and discuss repeat testing or HbA1c with a healthcare professional. One result alone may not establish diabetes."
    },
    "Random Blood Sugar": {
        "meaning": "Measures blood glucose regardless of meal timing.",
        "importance": "Helps assess blood glucose, particularly when symptoms are present.",
        "low_causes": [
            "Glucose-lowering medicines", "Prolonged fasting",
            "Some hormonal or liver conditions"
        ],
        "high_causes": [
            "A recent meal", "Acute illness or stress",
            "Prediabetes or diabetes", "Some medication effects"
        ],
        "follow_up": "Interpret with meal timing, symptoms, and any recommended fasting glucose or HbA1c testing."
    },
    "Postprandial Blood Sugar": {
        "meaning": "Measures blood glucose after a meal or glucose load.",
        "importance": "Helps assess how the body handles glucose after eating.",
        "low_causes": ["Glucose-lowering medicines", "Some hormonal conditions"],
        "high_causes": [
            "Impaired glucose tolerance", "Diabetes",
            "Meal timing or test-protocol differences"
        ],
        "follow_up": "Check the exact time after eating and discuss the result with a healthcare professional."
    },
    "HbA1c": {
        "meaning": "Estimates average blood glucose over approximately the previous two to three months.",
        "importance": "Used in screening for and monitoring diabetes.",
        "low_causes": [
            "Some conditions shortening red blood cell lifespan",
            "Recent blood loss", "Some forms of anemia"
        ],
        "high_causes": ["Prediabetes", "Diabetes", "Some glucose-regulation conditions"],
        "follow_up": "Discuss the result with a clinician. Anemia and some blood conditions can affect HbA1c accuracy."
    },
    "Creatinine": {
        "meaning": "Measures a waste product filtered from the blood by the kidneys.",
        "importance": "Helps assess kidney function when interpreted with eGFR and clinical context.",
        "low_causes": ["Low muscle mass", "Some nutritional or medical conditions"],
        "high_causes": [
            "Reduced kidney function", "Dehydration",
            "Some medicines", "Recent intense exercise or muscle injury"
        ],
        "follow_up": "Review eGFR, previous results, hydration, medicines, and urine tests with a healthcare professional."
    },
    "Urea": {
        "meaning": "Measures a waste product formed during protein metabolism.",
        "importance": "Can help assess kidney function and hydration alongside other tests.",
        "low_causes": ["Low protein intake", "Some liver conditions", "Overhydration"],
        "high_causes": [
            "Dehydration", "Reduced kidney function",
            "Increased protein breakdown", "Some gastrointestinal bleeding"
        ],
        "follow_up": "Interpret with creatinine, eGFR, hydration, diet, and medical history."
    },
    "BUN": {
        "meaning": "Measures blood urea nitrogen, a waste product related to protein metabolism.",
        "importance": "Helps assess kidney function alongside other findings.",
        "low_causes": ["Low protein intake", "Some liver conditions", "Overhydration"],
        "high_causes": [
            "Dehydration", "Reduced kidney function",
            "Increased protein breakdown", "Some gastrointestinal bleeding"
        ],
        "follow_up": "Review alongside creatinine, eGFR, hydration, and clinical history."
    },
    "eGFR": {
        "meaning": "Estimates how well the kidneys filter waste from the blood.",
        "importance": "Helps assess kidney function; interpretation depends on clinical information.",
        "low_causes": ["Reduced kidney function", "Some acute illnesses or fluid changes"],
        "high_causes": [],
        "follow_up": "Discuss with a healthcare professional. One result alone does not establish chronic kidney disease."
    },
    "Total Cholesterol": {
        "meaning": "Measures the total amount of cholesterol in the blood.",
        "importance": "Helps assess cardiovascular risk with LDL, HDL, triglycerides, and other risk factors.",
        "low_causes": ["Some nutritional, thyroid, liver, or chronic medical conditions"],
        "high_causes": [
            "Inherited cholesterol conditions", "Dietary or lifestyle factors",
            "Some thyroid or metabolic conditions"
        ],
        "follow_up": "Review the complete lipid profile and personal cardiovascular risk with a healthcare professional."
    },
    "LDL Cholesterol": {
        "meaning": "Measures low-density lipoprotein cholesterol, often called bad cholesterol.",
        "importance": "Higher LDL can increase cardiovascular risk.",
        "low_causes": [],
        "high_causes": [
            "Inherited cholesterol conditions", "Dietary or lifestyle factors",
            "Some thyroid or metabolic conditions"
        ],
        "follow_up": "Discuss the result in the context of overall cardiovascular risk and any current treatment."
    },
    "HDL Cholesterol": {
        "meaning": "Measures high-density lipoprotein cholesterol, often called good cholesterol.",
        "importance": "HDL is one component of cardiovascular risk assessment.",
        "low_causes": ["Insulin resistance", "Smoking", "Some lifestyle or metabolic factors"],
        "high_causes": [],
        "follow_up": "Interpret with LDL, triglycerides, and overall cardiovascular risk."
    },
    "Triglycerides": {
        "meaning": "Measures a type of fat circulating in the blood.",
        "importance": "High levels can be associated with metabolic and cardiovascular risk.",
        "low_causes": [],
        "high_causes": [
            "A recent meal if the sample was not fasting",
            "Insulin resistance or diabetes", "Alcohol use",
            "Some medication effects", "Inherited lipid conditions"
        ],
        "follow_up": "Check whether the test was fasting and discuss the complete lipid profile with a clinician."
    },
    "TSH": {
        "meaning": "Measures thyroid-stimulating hormone, which helps regulate thyroid activity.",
        "importance": "Helps assess thyroid function with free T4 and sometimes T3.",
        "low_causes": [
            "An overactive thyroid", "Excess thyroid hormone medication",
            "Some pituitary conditions"
        ],
        "high_causes": [
            "An underactive thyroid", "Some medication effects",
            "Temporary changes during illness or recovery"
        ],
        "follow_up": "Discuss with a healthcare professional; free T4 and sometimes thyroid antibodies may be considered."
    },
    "T3": {
        "meaning": "Measures triiodothyronine, a thyroid hormone.",
        "importance": "Helps evaluate thyroid function alongside TSH and T4.",
        "low_causes": ["Some non-thyroid illnesses", "An underactive thyroid in some cases"],
        "high_causes": ["An overactive thyroid", "Some thyroid medication effects"],
        "follow_up": "Interpret with TSH, T4, symptoms, and medicines."
    },
    "T4": {
        "meaning": "Measures thyroxine, a thyroid hormone.",
        "importance": "Helps evaluate thyroid function with TSH and sometimes T3.",
        "low_causes": ["An underactive thyroid", "Some pituitary conditions", "Some medicines"],
        "high_causes": ["An overactive thyroid", "Thyroid hormone medicine effects"],
        "follow_up": "Review with TSH and the specific type of T4 test performed."
    },
    "Vitamin D": {
        "meaning": "Measures vitamin D status, which contributes to bone and muscle health.",
        "importance": "Helps assess whether vitamin D levels may be inadequate or excessive.",
        "low_causes": [
            "Limited sunlight exposure", "Low dietary intake",
            "Problems absorbing nutrients", "Some liver or kidney conditions"
        ],
        "high_causes": ["Excessive vitamin D supplementation", "Vitamin D toxicity"],
        "follow_up": "Discuss supplementation and follow-up testing with a healthcare professional. Avoid unsupervised high-dose supplements."
    },
    "Vitamin B12": {
        "meaning": "Measures vitamin B12, which supports nerve function and red blood cell production.",
        "importance": "Helps investigate certain types of anemia and neurological symptoms.",
        "low_causes": [
            "Low dietary intake", "Problems absorbing vitamin B12",
            "Some medication effects"
        ],
        "high_causes": [
            "Recent vitamin B12 supplementation",
            "Some liver or other medical conditions"
        ],
        "follow_up": "Discuss symptoms, diet, medicines, and whether additional tests are needed."
    },
    "Calcium": {
        "meaning": "Measures calcium in the blood, important for bones, nerves, and muscles.",
        "importance": "Abnormal calcium can be associated with several medical conditions.",
        "low_causes": ["Vitamin D deficiency", "Kidney conditions", "Some hormonal conditions"],
        "high_causes": [
            "Overactive parathyroid glands", "Some cancers",
            "Certain medicines", "Dehydration in some circumstances"
        ],
        "follow_up": "Interpret with albumin, kidney function, symptoms, and any recommended repeat testing."
    },
    "Sodium": {
        "meaning": "Measures an electrolyte involved in fluid balance and nerve function.",
        "importance": "Marked abnormalities can affect brain and muscle function.",
        "low_causes": ["Some medicines", "Fluid-balance disorders", "Heart, kidney, or liver conditions"],
        "high_causes": ["Water loss or dehydration", "Some hormonal conditions"],
        "follow_up": "Discuss promptly with a healthcare professional, especially if symptoms or substantial abnormalities are present."
    },
    "Potassium": {
        "meaning": "Measures an electrolyte needed for muscle and heart function.",
        "importance": "Significant abnormalities can affect heart rhythm.",
        "low_causes": ["Vomiting or diarrhea", "Some diuretic medicines", "Some hormonal conditions"],
        "high_causes": [
            "Reduced kidney function", "Some medicines",
            "Cell breakdown", "Sample collection effects"
        ],
        "follow_up": "Promptly review abnormal results with a clinician. A repeat sample may be needed if collection affected the result."
    },
    "Chloride": {
        "meaning": "Measures an electrolyte involved in fluid and acid-base balance.",
        "importance": "Helps interpret fluid balance and certain metabolic conditions.",
        "low_causes": ["Vomiting", "Some medicines", "Certain fluid or hormonal conditions"],
        "high_causes": ["Dehydration", "Some kidney or acid-base conditions"],
        "follow_up": "Interpret alongside sodium, bicarbonate, kidney function, and clinical history."
    },
    "Bilirubin": {
        "meaning": "Measures a pigment produced when red blood cells are broken down.",
        "importance": "Can help assess liver function, bile flow, and red blood cell breakdown.",
        "low_causes": [],
        "high_causes": [
            "Some liver conditions", "Bile duct obstruction",
            "Increased red blood cell breakdown", "Some inherited conditions"
        ],
        "follow_up": "Review total and direct bilirubin, liver enzymes, symptoms, and medical history."
    },
    "ALT": {
        "meaning": "Measures an enzyme found mainly in liver cells.",
        "importance": "An elevation can indicate liver-cell irritation or injury but does not identify its cause.",
        "low_causes": [],
        "high_causes": [
            "Fatty liver disease", "Viral hepatitis",
            "Medicine or supplement effects", "Other liver conditions"
        ],
        "follow_up": "Review with AST, ALP, bilirubin, medicines, and symptoms."
    },
    "AST": {
        "meaning": "Measures an enzyme found in liver and several other tissues, including muscle.",
        "importance": "An elevation can occur with liver or muscle injury.",
        "low_causes": [],
        "high_causes": [
            "Some liver conditions", "Muscle injury or strenuous exercise",
            "Medicine effects"
        ],
        "follow_up": "Interpret with ALT, other liver tests, recent exercise, and clinical history."
    },
    "ALP": {
        "meaning": "Measures an enzyme associated mainly with liver, bile ducts, and bones.",
        "importance": "Can help investigate liver, bile duct, or bone-related conditions.",
        "low_causes": ["Some nutritional deficiencies"],
        "high_causes": [
            "Bile duct conditions", "Some liver conditions",
            "Increased bone activity", "Normal growth during childhood or adolescence"
        ],
        "follow_up": "Interpret with age, GGT, bilirubin, other liver tests, and clinical history."
    },
    "Albumin": {
        "meaning": "Measures a major blood protein made by the liver.",
        "importance": "Helps assess nutritional, liver, kidney, and fluid-related conditions.",
        "low_causes": [
            "Liver disease", "Protein loss through kidneys",
            "Inflammation or chronic illness", "Poor nutrition or absorption"
        ],
        "high_causes": ["Dehydration"],
        "follow_up": "Interpret with liver and kidney tests, urine protein, nutrition, and fluid status."
    },
    "Total Protein": {
        "meaning": "Measures the combined amount of several proteins in the blood.",
        "importance": "Can provide information about nutrition, inflammation, liver function, and some immune conditions.",
        "low_causes": [
            "Poor nutrition or absorption", "Liver disease",
            "Protein loss through kidneys or intestines"
        ],
        "high_causes": [
            "Dehydration", "Some chronic inflammatory conditions",
            "Some abnormal antibody-producing conditions"
        ],
        "follow_up": "Review albumin, globulin, liver and kidney tests, and recommended further investigations."
    },
    "CRP": {
        "meaning": "Measures C-reactive protein, a marker of inflammation.",
        "importance": "Can indicate inflammation but does not identify its source by itself.",
        "low_causes": [],
        "high_causes": ["Infection", "Inflammatory conditions", "Tissue injury", "Some chronic diseases"],
        "follow_up": "Interpret with symptoms, examination, and other tests; CRP alone cannot identify a specific disease."
    },
    "ESR": {
        "meaning": "Measures how quickly red blood cells settle in a tube over a specified time.",
        "importance": "Can support assessment of inflammation but is nonspecific.",
        "low_causes": [],
        "high_causes": ["Infection", "Inflammatory conditions", "Anemia", "Some chronic diseases"],
        "follow_up": "Interpret with symptoms, blood count, CRP, and other clinical findings."
    },
    "Uric Acid": {
        "meaning": "Measures uric acid, formed when the body breaks down purines.",
        "importance": "Can help assess gout risk and some kidney stone concerns.",
        "low_causes": ["Some medicines", "Some uncommon metabolic or kidney conditions"],
        "high_causes": ["Gout risk", "Reduced kidney excretion", "Some medicines", "Metabolic factors"],
        "follow_up": "High uric acid alone does not confirm gout. Discuss symptoms and kidney history with a clinician."
    },
    "Urine Protein": {
        "meaning": "Checks whether protein is present in urine.",
        "importance": "Persistent protein in urine can be a sign of kidney damage.",
        "low_causes": [],
        "high_causes": [
            "Kidney disease", "Strenuous exercise",
            "Fever or acute illness", "Some other medical conditions"
        ],
        "follow_up": "Confirm the urine test type and discuss repeat testing or a urine albumin-to-creatinine ratio."
    },
    "Urine Glucose": {
        "meaning": "Checks whether glucose is present in urine.",
        "importance": "Can provide information about blood glucose or kidney handling of glucose.",
        "low_causes": [],
        "high_causes": [
            "High blood glucose", "Some medicines including SGLT2 inhibitors",
            "Some kidney tubular conditions"
        ],
        "follow_up": "Review blood glucose, HbA1c, medicines, and the urine test method with a clinician."
    },
    "Urine Ketones": {
        "meaning": "Checks for ketones, which can appear when the body uses fat for energy.",
        "importance": "May be relevant in diabetes, fasting, or certain illnesses.",
        "low_causes": [],
        "high_causes": [
            "Prolonged fasting or low-carbohydrate intake",
            "Vomiting or dehydration", "Uncontrolled diabetes"
        ],
        "follow_up": "If diabetes is present and ketones are elevated with vomiting, abdominal pain, rapid breathing, or confusion, seek urgent medical care."
    },
    "Urine Blood": {
        "meaning": "Checks for blood or blood-related signals in urine.",
        "importance": "May need investigation even when visible blood is absent.",
        "low_causes": [],
        "high_causes": [
            "Urinary tract infection", "Kidney stones",
            "Urinary tract or kidney conditions",
            "Menstrual contamination", "Recent strenuous exercise"
        ],
        "follow_up": "Discuss confirmation with microscopy and follow-up testing with a healthcare professional."
    },
    "MCV": {
        "meaning": "Measures the average size of red blood cells.",
        "importance": "Helps classify anemia and guide further testing.",
        "low_causes": ["Iron deficiency", "Some inherited hemoglobin conditions"],
        "high_causes": [
            "Vitamin B12 deficiency", "Folate deficiency",
            "Some liver conditions", "Some medicine effects"
        ],
        "follow_up": "Interpret with hemoglobin, MCH, RDW, iron studies, and vitamin levels as appropriate."
    },
    "MCH": {
        "meaning": "Measures the average amount of hemoglobin in each red blood cell.",
        "importance": "Helps characterize different patterns of anemia.",
        "low_causes": ["Iron deficiency", "Some inherited hemoglobin conditions"],
        "high_causes": ["Some forms of macrocytic anemia", "Certain changes in red blood cell size"],
        "follow_up": "Interpret with MCV, MCHC, hemoglobin, and other blood count results."
    },
    "MCHC": {
        "meaning": "Measures the average concentration of hemoglobin inside red blood cells.",
        "importance": "Helps assess red blood cell characteristics.",
        "low_causes": ["Iron deficiency", "Some inherited hemoglobin conditions"],
        "high_causes": ["Some red blood cell disorders", "Certain sample or measurement effects"],
        "follow_up": "Interpret with the complete blood count and, if needed, a blood film."
    },
    "Hematocrit": {
        "meaning": "Measures the proportion of blood volume made up by red blood cells.",
        "importance": "Helps assess anemia, red blood cell concentration, and fluid status.",
        "low_causes": ["Anemia", "Blood loss", "Overhydration"],
        "high_causes": [
            "Dehydration", "High-altitude exposure",
            "Some conditions increasing red blood cell production"
        ],
        "follow_up": "Review with hemoglobin, RBC count, hydration, and clinical history."
    },
}


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean_text(value):
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    if isinstance(value, (list, tuple, set)):
        return "; ".join(
            str(item) for item in value if item is not None
        )

    return str(value).strip()


def normalize_name(name):
    text = clean_text(name).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def identify_test(test_name):
    """Identify supported tests without unsafe short partial matches."""
    name = normalize_name(test_name)

    if not name:
        return None

    # Exact matches first.
    for canonical, aliases in TEST_ALIASES.items():
        if name == normalize_name(canonical):
            return canonical

        for alias in aliases:
            if name == normalize_name(alias):
                return canonical

    # Longer labels may contain a known test name.
    # Require token boundaries to prevent accidental matches.
    candidates = []

    for canonical, aliases in TEST_ALIASES.items():
        for alias in [canonical] + aliases:
            alias_name = normalize_name(alias)

            if len(alias_name) < 4:
                continue

            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(alias_name)
                + r"(?![a-z0-9])"
            )

            if re.search(pattern, name):
                candidates.append((len(alias_name), canonical))

    if candidates:
        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]

    return None


def normalize_status(status):
    value = normalize_name(status)

    if value in {
        "low", "below", "below range", "below normal",
        "decreased", "abnormal low"
    }:
        return "Below range"

    if value in {
        "high", "above", "above range", "above normal",
        "increased", "abnormal high"
    }:
        return "Above range"

    if value in {
        "normal", "within range", "within normal range",
        "normal range", "in range"
    }:
        return "Within range"

    if value in {
        "critical", "critical high", "critical low",
        "dangerously high", "dangerously low"
    }:
        return "Needs urgent review"

    if value in {
        "reference range unavailable",
        "range unavailable",
        "no reference range"
    }:
        return "Reference range unavailable"

    return "Needs review"


def readable_causes(test_info, status):
    if status == "Below range":
        causes = test_info.get("low_causes", [])
    elif status == "Above range":
        causes = test_info.get("high_causes", [])
    else:
        causes = []

    if isinstance(causes, str):
        causes = [causes] if causes.strip() else []

    causes = [
        str(cause).strip()
        for cause in causes
        if cause is not None and str(cause).strip()
    ]

    if causes:
        return (
            "Possible conditions or causes: "
            + "; ".join(causes)
            + ". These are possibilities, not a diagnosis."
        )

    if status == "Within range":
        return (
            "This result alone does not establish or exclude a medical condition."
        )

    if status == "Needs urgent review":
        return (
            "Prompt professional assessment may be needed. "
            "Possible causes cannot be determined safely from this value alone."
        )

    return (
        "Possible causes cannot be determined reliably. "
        "Verify the result, unit, and laboratory reference range."
    )


# ============================================================
# EXPLAIN ONE TEST
# ============================================================

def explain_test(test_name, result, reference_range="", status=""):
    canonical = identify_test(test_name)
    display_name = canonical or clean_text(test_name) or "Unknown test"

    result_text = clean_text(result) or "Not available"
    range_text = clean_text(reference_range) or "Not provided"
    normalized = normalize_status(status)

    info = TEST_INFO.get(canonical, {})

    meaning = info.get(
        "meaning",
        "This test measures a laboratory parameter. Its meaning depends on the test method and clinical context."
    )
    importance = info.get(
        "importance",
        "Use the laboratory reference range and interpret this result with symptoms and other findings."
    )
    follow_up = info.get(
        "follow_up",
        "Verify the result and reference range on the original report. Ask a qualified healthcare professional for interpretation."
    )

    if normalized == "Within range":
        interpretation = (
            "The analyzer marks this result within the supplied reference range. "
            "This alone does not rule out disease."
        )
    elif normalized == "Below range":
        interpretation = (
            "The analyzer marks this result below the supplied reference range. "
            "Its significance depends on the degree of difference and clinical context."
        )
    elif normalized == "Above range":
        interpretation = (
            "The analyzer marks this result above the supplied reference range. "
            "Its significance depends on the degree of difference and clinical context."
        )
    elif normalized == "Needs urgent review":
        interpretation = (
            "The result has been marked for urgent review. Confirm the value "
            "and contact an appropriate healthcare professional promptly."
        )
    elif normalized == "Reference range unavailable":
        interpretation = (
            "A reference range was not available. The result cannot be safely "
            "classified as low, normal, or high."
        )
    else:
        interpretation = (
            "The result status could not be reliably classified. Check the "
            "value, unit, and reference range against the original report."
        )

    return {
        "Test": display_name,
        "Result": result_text,
        "Reference Range": range_text,
        "Status": normalized,
        "Meaning": meaning,
        "Importance": importance,
        "Interpretation": interpretation,
        "Possible Causes": readable_causes(info, normalized),
        "Follow-up": follow_up,
    }


# ============================================================
# DATAFRAME COLUMN COMPATIBILITY
# ============================================================

def get_value(row_data, *names, default=""):
    """Find a column regardless of capitalization or underscores."""
    normalized_row = {
        normalize_name(key): value
        for key, value in row_data.items()
    }

    for name in names:
        key = normalize_name(name)

        if key in normalized_row:
            value = normalized_row[key]

            if value is not None and clean_text(value):
                return value

    return default


# ============================================================
# OVERALL REPORT SUMMARY
# ============================================================

def build_report_summary(results_df):
    if not isinstance(results_df, pd.DataFrame) or results_df.empty:
        return (
            "No structured laboratory results were recognized. "
            "Check the extracted text and compare it with the original report."
        )

    status_col = next(
        (
            col for col in results_df.columns
            if normalize_name(col) == "status"
        ),
        None,
    )

    if status_col is None:
        return (
            "Test results were extracted, but statuses are unavailable. "
            "Verify values and reference ranges before interpretation."
        )

    statuses = results_df[status_col].apply(normalize_status)

    low_count = int((statuses == "Below range").sum())
    high_count = int((statuses == "Above range").sum())
    normal_count = int((statuses == "Within range").sum())
    review_count = int(
        statuses.isin([
            "Needs review",
            "Needs urgent review",
            "Reference range unavailable",
        ]).sum()
    )

    summary = (
        f"{len(results_df)} test result(s) were recognized. "
        f"{normal_count} marked within range, "
        f"{low_count} marked below range, and "
        f"{high_count} marked above range."
    )

    if review_count:
        summary += f" {review_count} result(s) need verification or review."

    summary += (
        " These classifications depend on the extracted values and laboratory "
        "ranges. They do not establish or exclude a diagnosis."
    )

    return summary


# ============================================================
# EXPLAIN THE COMPLETE REPORT
# ============================================================

def explain_report(report_text, results_df, patient_fields=None):
    """
    Compatible with app.py:
        explain_report(
            report_text=report_text,
            results_df=results,
            patient_fields=patient
        )

    Returns a dictionary with patient, summary, results, and general_notes.
    """
    patient_fields = patient_fields if isinstance(patient_fields, dict) else {}
    detailed_results = []

    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        for _, row in results_df.iterrows():
            row_data = row.to_dict()

            # Supports both analyzer.py's lowercase keys and display-style keys.
            test_name = get_value(
                row_data,
                "Test", "test", "Test Name", "test_name",
                "Parameter", "parameter", "Investigation", "investigation",
                "Name", "name",
            )

            result_value = get_value(
                row_data,
                "Result", "result", "Value", "value",
                "Test Result", "test_result", "Numeric Value",
                "numeric_value", "Observed Value", "observed_value",
                default="",
            )

            reference_range = get_value(
                row_data,
                "Reference Range", "reference_range",
                "Reference Range / Normal Range",
                "Normal Range", "normal_range",
                default="",
            )

            status = get_value(
                row_data,
                "Status", "status",
                default="Needs review",
            )

            explanation = explain_test(
                test_name=test_name,
                result=result_value,
                reference_range=reference_range,
                status=status,
            )

            unit = clean_text(
                get_value(row_data, "Unit", "unit", default="")
            )

            # Do not add a unit twice if the result already includes it.
            if (
                unit
                and explanation["Result"] != "Not available"
                and unit.lower() not in explanation["Result"].lower()
            ):
                explanation["Result"] = (
                    f"{explanation['Result']} {unit}"
                ).strip()

            detailed_results.append(explanation)

    summary = build_report_summary(results_df)

    general_notes = [
        "This tool provides educational information and does not diagnose disease.",
        "Possible causes are examples, not confirmed diagnoses.",
        "Reference ranges can vary by laboratory, age, sex, pregnancy status, and test method.",
        "Verify every extracted value, unit, and reference range against the original report.",
        "Scanned images and unusual report layouts can cause extraction errors.",
        "A result within range does not rule out every medical condition.",
        "Discuss abnormal results and symptoms with a qualified healthcare professional.",
    ]

    if not detailed_results:
        general_notes.insert(
            0,
            "No structured test explanations could be generated. "
            "Check the extracted report text and analyzer output."
        )

    return {
        "patient": patient_fields,
        "summary": summary,
        "results": detailed_results,
        "general_notes": general_notes,
    }
