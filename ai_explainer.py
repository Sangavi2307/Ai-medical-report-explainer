
import re
import pandas as pd


# ============================================================
# MEDILENS - MEDICAL REPORT EXPLANATION LIBRARY
# Suitable for common numerical laboratory test reports.
# This is an educational, rule-based system, not a diagnosis.
# ============================================================


TEST_ALIASES = {
    "Hemoglobin": [
        "hemoglobin", "haemoglobin", "hb", "hgb"
    ],
    "WBC Count": [
        "wbc", "white blood cell", "white blood cells",
        "total leukocyte count", "tlc", "leukocyte count",
        "leucocyte count"
    ],
    "RBC Count": [
        "rbc", "red blood cell", "red blood cells",
        "erythrocyte count"
    ],
    "Platelets": [
        "platelet", "platelets", "platelet count",
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
        "hba1c", "glycated hemoglobin", "glycosylated hemoglobin",
        "glycohemoglobin"
    ],
    "Creatinine": [
        "creatinine", "serum creatinine"
    ],
    "Urea": [
        "urea", "serum urea"
    ],
    "BUN": [
        "bun", "blood urea nitrogen"
    ],
    "eGFR": [
        "egfr", "estimated glomerular filtration rate",
        "glomerular filtration rate"
    ],
    "Total Cholesterol": [
        "total cholesterol", "cholesterol total"
    ],
    "LDL Cholesterol": [
        "ldl", "ldl cholesterol", "low density lipoprotein"
    ],
    "HDL Cholesterol": [
        "hdl", "hdl cholesterol", "high density lipoprotein"
    ],
    "Triglycerides": [
        "triglyceride", "triglycerides", "tg"
    ],
    "TSH": [
        "tsh", "thyroid stimulating hormone",
        "thyrotropin"
    ],
    "T3": [
        "total t3", "free t3", "triiodothyronine"
    ],
    "T4": [
        "total t4", "free t4", "thyroxine"
    ],
    "Vitamin D": [
        "vitamin d", "25 oh vitamin d", "25-oh vitamin d",
        "25 hydroxy vitamin d", "25-hydroxy vitamin d",
        "25 oh d"
    ],
    "Vitamin B12": [
        "vitamin b12", "b12", "cobalamin"
    ],
    "Calcium": [
        "calcium", "serum calcium"
    ],
    "Sodium": [
        "sodium", "serum sodium", "na"
    ],
    "Potassium": [
        "potassium", "serum potassium", "k"
    ],
    "Chloride": [
        "chloride", "serum chloride"
    ],
    "Bilirubin": [
        "total bilirubin", "bilirubin total",
        "serum bilirubin"
    ],
    "ALT": [
        "alt", "sgpt", "alanine aminotransferase"
    ],
    "AST": [
        "ast", "sgot", "aspartate aminotransferase"
    ],
    "ALP": [
        "alp", "alkaline phosphatase"
    ],
    "Albumin": [
        "albumin", "serum albumin"
    ],
    "Total Protein": [
        "total protein", "serum total protein"
    ],
    "CRP": [
        "crp", "c reactive protein", "c-reactive protein"
    ],
    "ESR": [
        "esr", "erythrocyte sedimentation rate"
    ],
    "Uric Acid": [
        "uric acid", "serum uric acid"
    ],
    "Urine Protein": [
        "urine protein", "urine albumin", "protein urine"
    ],
    "Urine Glucose": [
        "urine glucose", "glucose urine"
    ],
    "Urine Ketones": [
        "urine ketones", "ketone bodies urine"
    ],
    "Urine Blood": [
        "urine blood", "blood in urine", "urine occult blood"
    ],
    "MCV": [
        "mcv", "mean corpuscular volume"
    ],
    "MCH": [
        "mch", "mean corpuscular hemoglobin"
    ],
    "MCHC": [
        "mchc", "mean corpuscular hemoglobin concentration"
    ],
    "Hematocrit": [
        "hematocrit", "haematocrit", "packed cell volume", "pcv"
    ],
}


# Possible causes are educational examples, not a complete disease list.
# Actual interpretation depends on age, sex, symptoms, units, medications,
# pregnancy status, laboratory range, and other test results.

TEST_INFO = {
    "Hemoglobin": {
        "meaning": "Measures the oxygen-carrying protein in red blood cells.",
        "importance": "Helps assess anemia and other blood-related conditions.",
        "low_causes": [
            "Anemia",
            "Iron deficiency",
            "Vitamin B12 or folate deficiency",
            "Blood loss",
            "Some chronic medical conditions"
        ],
        "high_causes": [
            "Dehydration",
            "Living at high altitude",
            "Smoking-related effects",
            "Some conditions that increase red blood cell production"
        ],
        "follow_up": "Review with a healthcare professional; a complete blood count and iron studies may be appropriate."
    },

    "WBC Count": {
        "meaning": "Measures white blood cells, which help the body fight infections.",
        "importance": "Can provide information about infection, inflammation, and blood or immune conditions.",
        "low_causes": [
            "Some viral infections",
            "Medication effects",
            "Autoimmune conditions",
            "Bone marrow disorders"
        ],
        "high_causes": [
            "Infection",
            "Inflammation",
            "Physical stress",
            "Medication effects",
            "Some blood disorders"
        ],
        "follow_up": "Review the white blood cell differential, symptoms, medicines, and the full blood count with a clinician."
    },

    "RBC Count": {
        "meaning": "Measures the number of red blood cells.",
        "importance": "Helps assess oxygen transport and certain blood-related conditions.",
        "low_causes": [
            "Anemia",
            "Blood loss",
            "Nutritional deficiencies",
            "Some chronic illnesses"
        ],
        "high_causes": [
            "Dehydration",
            "High-altitude exposure",
            "Smoking-related effects",
            "Some conditions that increase red blood cell production"
        ],
        "follow_up": "Interpret together with hemoglobin, hematocrit, MCV, and other blood count results."
    },

    "Platelets": {
        "meaning": "Measures blood components that help form clots and stop bleeding.",
        "importance": "Helps assess bleeding and clotting-related concerns.",
        "low_causes": [
            "Some viral infections",
            "Medication effects",
            "Immune-related platelet destruction",
            "Liver or spleen conditions",
            "Some bone marrow disorders"
        ],
        "high_causes": [
            "Recent infection",
            "Inflammation",
            "Iron deficiency",
            "Some bone marrow disorders"
        ],
        "follow_up": "Review the full blood count and any unusual bruising, bleeding, or clotting symptoms with a clinician."
    },

    "Fasting Blood Sugar": {
        "meaning": "Measures blood glucose after fasting for the period specified by the laboratory.",
        "importance": "Used to screen for and monitor blood glucose disorders.",
        "low_causes": [
            "Medication-related low blood sugar",
            "Prolonged fasting",
            "Some hormonal or liver conditions"
        ],
        "high_causes": [
            "Prediabetes",
            "Diabetes mellitus",
            "Acute illness or physical stress",
            "Some medication effects"
        ],
        "follow_up": "Confirm fasting conditions and discuss repeat testing or HbA1c with a healthcare professional. One result alone may not establish diabetes."
    },

    "Random Blood Sugar": {
        "meaning": "Measures blood glucose at the time the sample is collected, regardless of meal timing.",
        "importance": "Helps assess blood glucose, especially when symptoms are present.",
        "low_causes": [
            "Glucose-lowering medication",
            "Prolonged fasting",
            "Some hormonal or liver conditions"
        ],
        "high_causes": [
            "A recent meal",
            "Acute illness or stress",
            "Prediabetes or diabetes",
            "Some medication effects"
        ],
        "follow_up": "Interpret with meal timing, symptoms, and any recommended fasting glucose or HbA1c testing."
    },

    "Postprandial Blood Sugar": {
        "meaning": "Measures blood glucose after a meal or glucose load, depending on the test protocol.",
        "importance": "Helps assess how the body handles glucose after eating.",
        "low_causes": [
            "Glucose-lowering medication",
            "Some hormonal conditions",
            "Prolonged gaps between meals"
        ],
        "high_causes": [
            "Impaired glucose tolerance",
            "Diabetes mellitus",
            "Meal timing or test-protocol differences"
        ],
        "follow_up": "Check the exact time after eating and discuss the result with a healthcare professional."
    },

    "HbA1c": {
        "meaning": "Estimates average blood glucose over approximately the previous two to three months.",
        "importance": "Used in screening for and monitoring diabetes.",
        "low_causes": [
            "Some conditions that shorten red blood cell lifespan",
            "Recent blood loss",
            "Some forms of anemia or hemoglobin disorders"
        ],
        "high_causes": [
            "Prediabetes",
            "Diabetes mellitus",
            "Some conditions that affect glucose regulation"
        ],
        "follow_up": "Discuss the result with a clinician; anemia and some blood conditions can affect HbA1c accuracy."
    },

    "Creatinine": {
        "meaning": "Measures a waste product filtered from the blood by the kidneys.",
        "importance": "Helps assess kidney function when interpreted with eGFR and clinical context.",
        "low_causes": [
            "Low muscle mass",
            "Some nutritional or medical conditions"
        ],
        "high_causes": [
            "Reduced kidney function",
            "Dehydration",
            "Some medications",
            "Recent intense exercise or muscle injury"
        ],
        "follow_up": "Review eGFR, previous results, hydration, medications, and urine tests with a healthcare professional."
    },

    "Urea": {
        "meaning": "Measures a waste product formed when the body processes protein.",
        "importance": "Can help assess kidney function and hydration along with other tests.",
        "low_causes": [
            "Low protein intake",
            "Some liver conditions",
            "Overhydration"
        ],
        "high_causes": [
            "Dehydration",
            "Reduced kidney function",
            "Increased protein breakdown",
            "Some gastrointestinal bleeding"
        ],
        "follow_up": "Interpret with creatinine, eGFR, hydration, diet, and medical history."
    },

    "BUN": {
        "meaning": "Measures blood urea nitrogen, a waste product related to protein metabolism.",
        "importance": "Helps assess kidney function when considered with other findings.",
        "low_causes": [
            "Low protein intake",
            "Some liver conditions",
            "Overhydration"
        ],
        "high_causes": [
            "Dehydration",
            "Reduced kidney function",
            "Increased protein breakdown",
            "Some gastrointestinal bleeding"
        ],
        "follow_up": "Review alongside creatinine, eGFR, hydration, and clinical history."
    },

    "eGFR": {
        "meaning": "Estimates how well the kidneys filter waste from the blood.",
        "importance": "Helps assess kidney function; interpretation depends on age and other clinical information.",
        "low_causes": [
            "Reduced kidney function",
            "Dehydration or acute illness in some circumstances"
        ],
        "high_causes": [],
        "follow_up": "Discuss with a healthcare professional. Chronic kidney disease generally requires persistence or other evidence, not one result alone."
    },

    "Total Cholesterol": {
        "meaning": "Measures the total amount of cholesterol in the blood.",
        "importance": "Helps assess cardiovascular risk along with LDL, HDL, triglycerides, and other risk factors.",
        "low_causes": [
            "Some nutritional conditions",
            "Some thyroid, liver, or chronic medical conditions"
        ],
        "high_causes": [
            "Inherited cholesterol conditions",
            "Dietary and lifestyle factors",
            "Some thyroid or metabolic conditions"
        ],
        "follow_up": "Review the complete lipid profile and personal cardiovascular risk with a healthcare professional."
    },

    "LDL Cholesterol": {
        "meaning": "Measures low-density lipoprotein cholesterol, often called 'bad cholesterol'.",
        "importance": "Higher LDL can increase the risk of cardiovascular disease.",
        "low_causes": [],
        "high_causes": [
            "Inherited cholesterol conditions",
            "Dietary and lifestyle factors",
            "Some thyroid or metabolic conditions"
        ],
        "follow_up": "Discuss the result in the context of overall cardiovascular risk and any existing treatment."
    },

    "HDL Cholesterol": {
        "meaning": "Measures high-density lipoprotein cholesterol, often called 'good cholesterol'.",
        "importance": "HDL is one component of cardiovascular risk assessment.",
        "low_causes": [
            "Insulin resistance",
            "Smoking",
            "Some lifestyle or metabolic factors"
        ],
        "high_causes": [],
        "follow_up": "Interpret with LDL, triglycerides, and overall cardiovascular risk."
    },

    "Triglycerides": {
        "meaning": "Measures a type of fat circulating in the blood.",
        "importance": "High levels can be associated with metabolic and cardiovascular risk.",
        "low_causes": [],
        "high_causes": [
            "A recent meal if the sample was not fasting",
            "Insulin resistance or diabetes",
            "Alcohol use",
            "Some medication effects",
            "Inherited lipid conditions"
        ],
        "follow_up": "Check whether the test was fasting and discuss the full lipid profile with a clinician."
    },

    "TSH": {
        "meaning": "Measures thyroid-stimulating hormone, which helps regulate thyroid activity.",
        "importance": "Helps assess thyroid function when interpreted with free T4 and sometimes T3.",
        "low_causes": [
            "An overactive thyroid",
            "Excess thyroid hormone medication",
            "Some pituitary conditions"
        ],
        "high_causes": [
            "An underactive thyroid",
            "Some medication effects",
            "Temporary changes during illness or recovery"
        ],
        "follow_up": "Discuss with a healthcare professional; free T4 and sometimes thyroid antibodies may be considered."
    },

    "T3": {
        "meaning": "Measures triiodothyronine, a thyroid hormone.",
        "importance": "Helps evaluate thyroid function alongside TSH and T4.",
        "low_causes": [
            "Some non-thyroid illnesses",
            "An underactive thyroid in some cases"
        ],
        "high_causes": [
            "An overactive thyroid",
            "Some thyroid medication effects"
        ],
        "follow_up": "Interpret with TSH, T4, symptoms, and medications."
    },

    "T4": {
        "meaning": "Measures thyroxine, a thyroid hormone.",
        "importance": "Helps evaluate thyroid function alongside TSH and sometimes T3.",
        "low_causes": [
            "An underactive thyroid",
            "Some pituitary conditions",
            "Some medication effects"
        ],
        "high_causes": [
            "An overactive thyroid",
            "Thyroid hormone medication effects",
            "Some temporary thyroid conditions"
        ],
        "follow_up": "Review with TSH and the type of T4 test performed."
    },

    "Vitamin D": {
        "meaning": "Measures vitamin D status, which contributes to bone and muscle health.",
        "importance": "Helps assess whether vitamin D levels may be inadequate or excessive.",
        "low_causes": [
            "Vitamin D deficiency",
            "Limited sunlight exposure",
            "Low dietary vitamin D intake",
            "Problems absorbing nutrients",
            "Some liver or kidney conditions"
        ],
        "high_causes": [
            "Excessive vitamin D supplementation",
            "Vitamin D toxicity"
        ],
        "follow_up": "Discuss supplementation and follow-up testing with a healthcare professional. Do not start high-dose supplements without advice."
    },

    "Vitamin B12": {
        "meaning": "Measures vitamin B12, which supports nerve function and red blood cell production.",
        "importance": "Helps investigate certain types of anemia and neurological symptoms.",
        "low_causes": [
            "Vitamin B12 deficiency",
            "Low dietary intake",
            "Problems absorbing vitamin B12",
            "Some medication effects"
        ],
        "high_causes": [
            "Recent vitamin B12 supplementation",
            "Some liver or other medical conditions"
        ],
        "follow_up": "Discuss symptoms, diet, medications, and whether additional tests are needed."
    },

    "Calcium": {
        "meaning": "Measures calcium in the blood, which is important for bones, nerves, and muscles.",
        "importance": "Abnormal calcium can be associated with several medical conditions.",
        "low_causes": [
            "Vitamin D deficiency",
            "Low parathyroid hormone",
            "Kidney conditions",
            "Low magnesium in some cases"
        ],
        "high_causes": [
            "Overactive parathyroid glands",
            "Some cancers",
            "Certain medications",
            "Dehydration in some circumstances"
        ],
        "follow_up": "Interpret with albumin, kidney function, symptoms, and any recommended repeat or ionized calcium test."
    },

    "Sodium": {
        "meaning": "Measures sodium, an electrolyte that helps regulate fluid balance and nerve function.",
        "importance": "Marked abnormalities can affect brain and muscle function.",
        "low_causes": [
            "Some medications",
            "Fluid-balance disorders",
            "Heart, kidney, or liver conditions",
            "Some hormonal conditions"
        ],
        "high_causes": [
            "Water loss or dehydration",
            "Some hormonal conditions",
            "Problems with access to or intake of water"
        ],
        "follow_up": "Discuss promptly with a healthcare professional, especially if the abnormality is substantial or symptoms are present."
    },

    "Potassium": {
        "meaning": "Measures potassium, an electrolyte needed for muscle and heart function.",
        "importance": "Significant abnormalities can affect heart rhythm.",
        "low_causes": [
            "Vomiting or diarrhea",
            "Some diuretic medications",
            "Low potassium intake",
            "Some hormonal conditions"
        ],
        "high_causes": [
            "Reduced kidney function",
            "Some medications",
            "Cell breakdown",
            "A falsely high result from sample collection problems"
        ],
        "follow_up": "Promptly review abnormal results with a clinician; a repeat sample may be needed if the result could be affected by collection."
    },

    "Chloride": {
        "meaning": "Measures an electrolyte involved in fluid and acid-base balance.",
        "importance": "Helps interpret fluid balance and certain metabolic conditions.",
        "low_causes": [
            "Vomiting",
            "Some medications",
            "Certain fluid or hormonal conditions"
        ],
        "high_causes": [
            "Dehydration",
            "Some kidney or acid-base conditions",
            "Certain fluid-related conditions"
        ],
        "follow_up": "Interpret alongside sodium, bicarbonate, kidney function, and clinical history."
    },

    "Bilirubin": {
        "meaning": "Measures a pigment produced when red blood cells are broken down.",
        "importance": "Can help assess liver function, bile flow, and red blood cell breakdown.",
        "low_causes": [],
        "high_causes": [
            "Some liver conditions",
            "Bile duct obstruction",
            "Increased red blood cell breakdown",
            "Some inherited conditions"
        ],
        "follow_up": "Review total and direct bilirubin, liver enzymes, symptoms, and medical history."
    },

    "ALT": {
        "meaning": "Measures an enzyme found mainly in liver cells.",
        "importance": "An elevation can indicate liver-cell irritation or injury but does not identify the cause.",
        "low_causes": [],
        "high_causes": [
            "Fatty liver disease",
            "Viral hepatitis",
            "Medication or supplement effects",
            "Alcohol-related liver injury",
            "Other liver conditions"
        ],
        "follow_up": "Review with AST, ALP, bilirubin, medications, and symptoms."
    },

    "AST": {
        "meaning": "Measures an enzyme found in the liver and several other tissues, including muscle.",
        "importance": "An elevation can occur with liver or muscle injury.",
        "low_causes": [],
        "high_causes": [
            "Some liver conditions",
            "Muscle injury or strenuous exercise",
            "Alcohol-related liver injury",
            "Medication effects"
        ],
        "follow_up": "Interpret with ALT, other liver tests, recent exercise, and clinical history."
    },

    "ALP": {
        "meaning": "Measures an enzyme associated mainly with the liver, bile ducts, and bones.",
        "importance": "Can help investigate liver, bile duct, or bone-related conditions.",
        "low_causes": [
            "Some nutritional deficiencies",
            "Some uncommon metabolic conditions"
        ],
        "high_causes": [
            "Bile duct conditions",
            "Some liver conditions",
            "Increased bone activity",
            "Normal growth during childhood or adolescence"
        ],
        "follow_up": "Interpret with age, GGT, bilirubin, other liver tests, and clinical history."
    },

    "Albumin": {
        "meaning": "Measures a major protein in the blood, made by the liver.",
        "importance": "Helps assess nutritional, liver, kidney, and fluid-related conditions.",
        "low_causes": [
            "Liver disease",
            "Protein loss through the kidneys",
            "Inflammation or chronic illness",
            "Poor nutritional intake or absorption"
        ],
        "high_causes": [
            "Dehydration"
        ],
        "follow_up": "Interpret with liver and kidney tests, urine protein, nutrition, and fluid status."
    },

    "Total Protein": {
        "meaning": "Measures the combined amount of several proteins in the blood.",
        "importance": "Can provide information about nutrition, inflammation, liver function, and some immune conditions.",
        "low_causes": [
            "Poor nutritional intake or absorption",
            "Liver disease",
            "Protein loss through kidneys or intestines"
        ],
        "high_causes": [
            "Dehydration",
            "Some chronic inflammatory conditions",
            "Some abnormal antibody-producing conditions"
        ],
        "follow_up": "Review albumin, globulin, liver and kidney tests, and any recommended further investigations."
    },

    "CRP": {
        "meaning": "Measures C-reactive protein, a marker of inflammation.",
        "importance": "Can indicate inflammation but does not identify its source by itself.",
        "low_causes": [],
        "high_causes": [
            "Infection",
            "Inflammatory conditions",
            "Tissue injury",
            "Some chronic diseases"
        ],
        "follow_up": "Interpret with symptoms, examination, and other tests; CRP alone cannot identify a specific disease."
    },

    "ESR": {
        "meaning": "Measures how quickly red blood cells settle in a tube over a specified period.",
        "importance": "Can support assessment of inflammation but is nonspecific.",
        "low_causes": [],
        "high_causes": [
            "Infection",
            "Inflammatory or autoimmune conditions",
            "Anemia",
            "Some chronic diseases"
        ],
        "follow_up": "Interpret with symptoms, blood count, CRP, and other clinical findings."
    },

    "Uric Acid": {
        "meaning": "Measures uric acid, a substance formed when the body breaks down purines.",
        "importance": "Can help assess gout risk and some kidney stone concerns.",
        "low_causes": [
            "Some medications",
            "Some uncommon metabolic or kidney conditions"
        ],
        "high_causes": [
            "Gout risk",
            "Reduced kidney excretion",
            "Some medications",
            "Dietary or metabolic factors"
        ],
        "follow_up": "High uric acid alone does not confirm gout; discuss symptoms and kidney history with a clinician."
    },

    "Urine Protein": {
        "meaning": "Checks whether protein is present in urine.",
        "importance": "Persistent protein in urine can be a sign of kidney damage.",
        "low_causes": [],
        "high_causes": [
            "Kidney disease",
            "Temporary changes after strenuous exercise",
            "Fever or acute illness",
            "Some other medical conditions"
        ],
        "follow_up": "Confirm the type of urine test and discuss repeat testing or a urine albumin-to-creatinine ratio."
    },

    "Urine Glucose": {
        "meaning": "Checks whether glucose is present in urine.",
        "importance": "Can provide information about glucose levels or kidney handling of glucose.",
        "low_causes": [],
        "high_causes": [
            "High blood glucose",
            "Some medications, including SGLT2 inhibitors",
            "Some kidney tubular conditions"
        ],
        "follow_up": "Review blood glucose, HbA1c, medications, and the urine test method with a clinician."
    },

    "Urine Ketones": {
        "meaning": "Checks for ketones, which can appear when the body uses fat for energy.",
        "importance": "May be relevant in diabetes, fasting, or certain illnesses.",
        "low_causes": [],
        "high_causes": [
            "Prolonged fasting or low carbohydrate intake",
            "Vomiting or dehydration",
            "Uncontrolled diabetes",
            "Diabetic ketoacidosis in the appropriate clinical context"
        ],
        "follow_up": "If diabetes is present and ketones are elevated with vomiting, abdominal pain, rapid breathing, or confusion, seek urgent medical care."
    },

    "Urine Blood": {
        "meaning": "Checks for blood or blood-related signals in urine.",
        "importance": "May need investigation even when visible blood is absent.",
        "low_causes": [],
        "high_causes": [
            "Urinary tract infection",
            "Kidney stones",
            "Urinary tract or kidney conditions",
            "Menstrual contamination",
            "Recent strenuous exercise"
        ],
        "follow_up": "Discuss confirmation with microscopy and follow-up testing with a healthcare professional."
    },

    "MCV": {
        "meaning": "Measures the average size of red blood cells.",
        "importance": "Helps classify anemia and guide further testing.",
        "low_causes": [
            "Iron deficiency",
            "Some inherited hemoglobin conditions"
        ],
        "high_causes": [
            "Vitamin B12 deficiency",
            "Folate deficiency",
            "Some liver conditions",
            "Some medication effects"
        ],
        "follow_up": "Interpret with hemoglobin, MCH, RDW, iron studies, and vitamin levels as appropriate."
    },

    "MCH": {
        "meaning": "Measures the average amount of hemoglobin in each red blood cell.",
        "importance": "Helps characterize different patterns of anemia.",
        "low_causes": [
            "Iron deficiency",
            "Some inherited hemoglobin conditions"
        ],
        "high_causes": [
            "Some forms of macrocytic anemia",
            "Certain changes in red blood cell size"
        ],
        "follow_up": "Interpret with MCV, MCHC, hemoglobin, and other blood count results."
    },

    "MCHC": {
        "meaning": "Measures the average concentration of hemoglobin inside red blood cells.",
        "importance": "Helps assess red blood cell characteristics.",
        "low_causes": [
            "Iron deficiency",
            "Some inherited hemoglobin conditions"
        ],
        "high_causes": [
            "Some red blood cell disorders",
            "Certain sample or measurement effects"
        ],
        "follow_up": "Interpret with the complete blood count and, if needed, a blood film."
    },

    "Hematocrit": {
        "meaning": "Measures the proportion of blood volume made up by red blood cells.",
        "importance": "Helps assess anemia, red blood cell concentration, and fluid status.",
        "low_causes": [
            "Anemia",
            "Blood loss",
            "Overhydration"
        ],
        "high_causes": [
            "Dehydration",
            "High-altitude exposure",
            "Some conditions that increase red blood cell production"
        ],
        "follow_up": "Review with hemoglobin, RBC count, hydration, and clinical history."
    },
}


# ------------------------------------------------------------
# GENERAL HELPERS
# ------------------------------------------------------------

def clean_text(value):
    """Convert values safely to readable strings."""
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    if isinstance(value, (list, tuple, set)):
        return "; ".join(str(item) for item in value if item is not None)

    return str(value).strip()


def normalize_name(name):
    """Normalize test names for matching."""
    text = clean_text(name).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def identify_test(test_name):
    """Return the canonical name of a supported test, or None."""
    name = normalize_name(test_name)

    if not name:
        return None

    # Prefer exact alias matches before partial matches.
    for canonical, aliases in TEST_ALIASES.items():
        if name == normalize_name(canonical):
            return canonical

        for alias in aliases:
            if name == normalize_name(alias):
                return canonical

    # Allow a longer report label, e.g. 'Serum Creatinine'.
    for canonical, aliases in TEST_ALIASES.items():
        candidates = [canonical] + aliases

        for alias in candidates:
            alias_normalized = normalize_name(alias)

            if len(alias_normalized) >= 4 and alias_normalized in name:
                return canonical

    return None


def normalize_status(status):
    """Normalize common status labels from the analyzer."""
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

    return "Needs review"


def readable_causes(test_info, status):
    """Always return a readable string, never an empty Python list."""
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
            "No specific disease is indicated by this result alone. "
            "A result within range does not rule out every condition."
        )

    if status == "Needs urgent review":
        return (
            "The result may require urgent professional assessment. "
            "Possible causes cannot be determined safely from this value alone."
        )

    return (
        "Possible causes cannot be determined reliably because the result "
        "status is uncertain or this test has no suitable cause rules. "
        "Verify the value, unit, and laboratory reference range."
    )


# ------------------------------------------------------------
# EXPLAIN ONE TEST
# ------------------------------------------------------------

def explain_test(test_name, result, reference_range="", status=""):
    """
    Create an educational explanation for one test.

    Parameters:
        test_name: test label
        result: measured value
        reference_range: laboratory-provided reference range
        status: analyzer status

    Returns:
        A dictionary of readable strings.
    """
    canonical = identify_test(test_name)
    display_name = canonical or clean_text(test_name) or "Unknown test"
    result_text = clean_text(result) or "Not available"
    range_text = clean_text(reference_range) or "Not provided"
    normalized = normalize_status(status)

    info = TEST_INFO.get(canonical, {})

    if info:
        meaning = info.get(
            "meaning",
            "This test measures a component of health."
        )
        importance = info.get(
            "importance",
            "Interpret alongside other test results and clinical history."
        )
        follow_up = info.get(
            "follow_up",
            "Discuss abnormal results with a qualified healthcare professional."
        )
    else:
        meaning = (
            "This test measures a laboratory parameter. Its exact meaning "
            "depends on the test method and clinical context."
        )
        importance = (
            "Use the laboratory's reference range and interpret this result "
            "with the patient's symptoms and other findings."
        )
        follow_up = (
            "Verify the result and reference range on the original report. "
            "Ask a qualified healthcare professional for interpretation."
        )

    if normalized == "Within range":
        interpretation = (
            "The supplied analyzer marks this result within the provided "
            "reference range. This alone does not rule out disease."
        )
    elif normalized == "Below range":
        interpretation = (
            "The supplied analyzer marks this result below the provided "
            "reference range. The significance depends on how low it is "
            "and on the patient's clinical context."
        )
    elif normalized == "Above range":
        interpretation = (
            "The supplied analyzer marks this result above the provided "
            "reference range. The significance depends on how high it is "
            "and on the patient's clinical context."
        )
    elif normalized == "Needs urgent review":
        interpretation = (
            "The analyzer has marked this result for urgent review. "
            "Confirm the value and contact an appropriate healthcare "
            "professional promptly."
        )
    else:
        interpretation = (
            "The result status could not be reliably classified. Check "
            "the extracted value, units, and reference range against "
            "the original laboratory report."
        )

    possible_causes = readable_causes(info, normalized)

    return {
        "Test": display_name,
        "Result": result_text,
        "Reference Range": range_text,
        "Status": normalized,
        "Meaning": meaning,
        "Importance": importance,
        "Interpretation": interpretation,
        "Possible Causes": possible_causes,
        "Follow-up": follow_up,
    }


# ------------------------------------------------------------
# OVERALL REPORT SUMMARY
# ------------------------------------------------------------

def build_report_summary(results_df):
    """Create an overall summary without making a diagnosis."""
    if results_df is None or not isinstance(results_df, pd.DataFrame):
        return (
            "No structured test results were available for summarization. "
            "Check that the report was extracted correctly."
        )

    if results_df.empty:
        return (
            "No laboratory results were recognized. This may happen if "
            "the report is scanned, has an unusual layout, or contains "
            "tests not supported by the current analyzer."
        )

    if "Status" not in results_df.columns:
        return (
            "Test results were extracted, but their statuses are unavailable. "
            "Verify the values and reference ranges before interpretation."
        )

    statuses = results_df["Status"].apply(normalize_status)

    low_count = int((statuses == "Below range").sum())
    high_count = int((statuses == "Above range").sum())
    normal_count = int((statuses == "Within range").sum())
    review_count = int(
        statuses.isin(["Needs review", "Needs urgent review"]).sum()
    )

    parts = [
        f"{len(results_df)} test result(s) were recognized.",
        f"{normal_count} marked within range.",
        f"{low_count} marked below range.",
        f"{high_count} marked above range.",
    ]

    if review_count:
        parts.append(
            f"{review_count} result(s) need verification or professional review."
        )

    parts.append(
        "These counts depend on the extracted values and reference ranges. "
        "They do not establish or exclude a diagnosis."
    )

    return " ".join(parts)


# ------------------------------------------------------------
# EXPLAIN THE COMPLETE REPORT
# ------------------------------------------------------------

def explain_report(report_text, results_df, patient_fields=None):
    """
    Explain a complete report.

    This function is compatible with the app call:
        explain_report(report_text, results, patient)

    Returns a dictionary containing:
        patient, summary, results, general_notes
    """
    patient_fields = patient_fields or {}

    if not isinstance(patient_fields, dict):
        patient_fields = {}

    detailed_results = []

    if isinstance(results_df, pd.DataFrame) and not results_df.empty:
        for _, row in results_df.iterrows():
            row_data = row.to_dict()

            test_name = (
                row_data.get("Test")
                or row_data.get("Test Name")
                or row_data.get("Parameter")
                or row_data.get("Investigation")
                or ""
            )

            result_value = (
                row_data.get("Result")
                if row_data.get("Result") is not None
                else row_data.get("Value", "")
            )

            reference_range = (
                row_data.get("Reference Range")
                or row_data.get("Reference Range / Normal Range")
                or row_data.get("Normal Range")
                or ""
            )

            status = row_data.get("Status", "Needs review")

            explanation = explain_test(
                test_name=test_name,
                result=result_value,
                reference_range=reference_range,
                status=status,
            )

            # Keep the actual unit visible when the analyzer provides it.
            unit = clean_text(row_data.get("Unit", ""))
            if unit:
                explanation["Result"] = (
                    f"{explanation['Result']} {unit}"
                ).strip()

            detailed_results.append(explanation)

    report_summary = build_report_summary(results_df)

    general_notes = [
        "This tool provides educational information and does not diagnose disease.",
        "Possible causes are not confirmed diagnoses and may not include every cause.",
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
            "The report may contain unsupported tests or require OCR/parser improvements."
        )

    return {
        "patient": patient_fields,
        "summary": report_summary,
        "results": detailed_results,
        "general_notes": general_notes,
    }
