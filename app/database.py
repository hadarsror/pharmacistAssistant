"""
Database module containing user and medication data.
"""


USERS_DB = {
    "312456789": {
        "id": "312456789",
        "name": "Hadar",
        "name_hebrew": "הדר",
        "allergies": ["Penicillin"],
        "prescriptions": [
            {"name": "Lisinopril", "instructions": "Take 10mg once daily in the morning."}
        ],
        "history": "History of hypertension."
    },
    "058123456": {
        "id": "058123456",
        "name": "Bob Levy",
        "name_hebrew": "בוב לוי",
        "allergies": ["Ibuprofen"],
        "prescriptions": [
            {"name": "Ibuprofen", "instructions": "Take 200mg as needed for pain."}
        ],  # CONFLICT: Has both allergy AND prescription
        "history": "Chronic headaches."
    },
    "123123123": {
        "id": "123123123",
        "name": "Maya Avni",
        "name_hebrew": "מאיה אבני",
        "allergies": ["Methylphenidate"],
        "prescriptions": [
            {"name": "Ritalin", "instructions": "Take 10mg twice daily for ADHD."}
        ],  # CONFLICT: Has both allergy AND prescription
        "history": "ADHD."
    },
    "204567891": {
        "id": "204567891",
        "name": "Alice Cohen",
        "name_hebrew": "אליס כהן",
        "allergies": [],
        "prescriptions": [
            {"name": "Metformin", "instructions": "Take 850mg twice daily with meals."}
        ],
        "history": "Type 2 Diabetes."
    },
    "300987654": {
        "id": "300987654",
        "name": "Dana Silver",
        "name_hebrew": "דנה סילבר",
        "allergies": [],
        "prescriptions": [],
        "history": "No known issues."
    },
    "111222333": {
        "id": "111222333",
        "name": "Levi Ackermann",
        "name_hebrew": "לוי אקרמן",
        "allergies": [],
        "prescriptions": [
            {"name": "Amoxicillin", "instructions": "Take 1 capsule twice daily for 7 days."}
        ],
        "history": "Occasional ear infections."
    },
    "444555666": {
        "id": "444555666",
        "name": "Mikasa Arlert",
        "name_hebrew": "מיקאסה ארלרט",
        "allergies": ["Penicillin"],
        "prescriptions": [
            {"name": "Lisinopril", "instructions": "Take 5mg once daily."}
        ],
        "history": "Mild hypertension."
    },
    "777888999": {
        "id": "777888999",
        "name": "Eren Yeager",
        "name_hebrew": "ארן ייגר",
        "allergies": [],
        "prescriptions": [
            {"name": "Metformin", "instructions": "Take 500mg daily."}
        ],
        "history": "Pre-diabetic monitoring."
    },
    "121212121": {
        "id": "121212121",
        "name": "Armin Arlert",
        "name_hebrew": "ארמין ארלרט",
        "allergies": ["Ibuprofen"],
        "prescriptions": [],
        "history": "ADHD; history of stomach ulcers."
    },
    "989898989": {
        "id": "989898989",
        "name": "Jean Kirschtein",
        "name_hebrew": "ז'אן קירשטיין",
        "allergies": [],
        "prescriptions": [],
        "history": "No significant medical history."
    }
}


MEDICATIONS_DB = {
    "Amoxicillin": {
        "sku": "MED-AMX-500",
        "name": "Amoxicillin",
        "name_hebrew": "אמוקסיצילין",
        "drug_class": "Penicillin",
        "active_ingredients": "Amoxicillin Trihydrate",
        "requires_rx": True,
        "stock_level": 12,
        "restrictions": "Finish the full course. Notify doctor of any rash."
    },
    "Ibuprofen": {
        "sku": "MED-IBU-200",
        "name": "Ibuprofen",
        "name_hebrew": "איבופרופן",
        "drug_class": "NSAIDs",
        "active_ingredients": "Ibuprofen",
        "requires_rx": False,
        "stock_level": 200,
        "restrictions": "Avoid taking on an empty stomach. Do not exceed 1200mg/day."
    },
    "Advil": {
        "sku": "MED-ADV-200",
        "name": "Advil",
        "name_hebrew": "אדוויל",
        "drug_class": "NSAIDs",
        "active_ingredients": "Ibuprofen",
        "requires_rx": False,
        "stock_level": 50,
        "restrictions": "Avoid taking on an empty stomach. Do not exceed 1200mg/day."
    },
    "Ritalin": {
        "sku": "MED-RIT-10",
        "name": "Ritalin",
        "name_hebrew": "ריטלין",
        "drug_class": "Stimulants",
        "active_ingredients": "Methylphenidate",
        "requires_rx": True,
        "stock_level": 5,
        "restrictions": "Controlled substance. Potential for abuse. Monitor heart rate."
    },
    "Lisinopril": {
        "sku": "MED-LIS-10",
        "name": "Lisinopril",
        "name_hebrew": "ליסינופריל",
        "drug_class": "ACE Inhibitors",
        "active_ingredients": "Lisinopril",
        "requires_rx": True,
        "stock_level": 50,
        "restrictions": "May cause a persistent dry cough. Monitor blood pressure."
    },
    "Metformin": {
        "sku": "MED-MET-850",
        "name": "Metformin",
        "name_hebrew": "מטפורמין",
        "drug_class": "Biguanides",
        "active_ingredients": "Metformin Hydrochloride",
        "requires_rx": True,
        "stock_level": 80,
        "restrictions": "Take with meals. Avoid excessive alcohol consumption."
    }
}
