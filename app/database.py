USERS_DB = {
    "312456789": {
        "id": "312456789",
        "name": "Hadar",
        "allergies": ["Penicillin"],
        "prescriptions": [
            {"name": "Amoxicillin", "instructions": "Take 1 capsule every 8 hours for 10 days."},
            {"name": "Lisinopril", "instructions": "Take 10mg once daily in the morning."}
        ],
        "history": "History of hypertension."
    },
    "058123456": {
        "id": "058123456",
        "name": "Bob Levy",
        "allergies": ["Ibuprofen"],
        "prescriptions": [{"name": "Ibuprofen", "instructions": "Take 400mg twice daily."}],
        "history": "Chronic headaches."
    },
    "123123123": {
        "id": "123123123",
        "name": "Maya Avni",
        "allergies": ["Methylphenidate"],
        "prescriptions": [{"name": "Ritalin", "instructions": "Take 20mg once daily in the morning."}],
        "history": "ADHD."
    },
    "204567891": {
        "id": "204567891",
        "name": "Alice Cohen",
        "allergies": [],
        "prescriptions": [{"name": "Metformin", "instructions": "Take 850mg twice daily with meals."}],
        "history": "Type 2 Diabetes."
    },
    "300987654": {
        "id": "300987654",
        "name": "Dana Silver",
        "allergies": [],
        "prescriptions": [],
        "history": "No known issues."
    },
    # --- NEW USERS ADDED TO MEET ASSIGNMENT REQUIREMENTS ---
    "111222333": {
        "id": "111222333",
        "name": "Levi Ackermann",
        "allergies": [],
        "prescriptions": [
            {"name": "Amoxicillin", "instructions": "Take 1 capsule twice daily for 7 days."}
        ],
        "history": "Occasional ear infections."
    },
    "444555666": {
        "id": "444555666",
        "name": "Mikasa Arlert",
        "allergies": ["Penicillin"],
        "prescriptions": [
            {"name": "Lisinopril", "instructions": "Take 5mg once daily."}
        ],
        "history": "Mild hypertension."
    },
    "777888999": {
        "id": "777888999",
        "name": "Eren Yeager",
        "allergies": [],
        "prescriptions": [
            {"name": "Metformin", "instructions": "Take 500mg daily."}
        ],
        "history": "Pre-diabetic monitoring."
    },
    "121212121": {
        "id": "121212121",
        "name": "Armin Arlert",
        "allergies": ["Ibuprofen"],
        "prescriptions": [
            {"name": "Ritalin", "instructions": "Take 10mg as needed for focus."}
        ],
        "history": "ADHD; history of stomach ulcers."
    },
    "989898989": {
        "id": "989898989",
        "name": "Jean Kirschtein",
        "allergies": [],
        "prescriptions": [],
        "history": "No significant medical history."
    }
}

MEDICATIONS_DB = {
    "Amoxicillin": {
        "sku": "MED-AMX-500",
        "name": "Amoxicillin",
        "drug_class": "Penicillin",
        "active_ingredients": "Amoxicillin Trihydrate",
        "requires_rx": True,
        "stock_level": 12,
        "restrictions": "Finish the full course. Notify doctor of any rash."
    },
    "Ibuprofen": {
        "sku": "MED-IBU-200",
        "name": "Ibuprofen",
        "drug_class": "NSAIDs",
        "active_ingredients": "Ibuprofen",
        "requires_rx": False,
        "stock_level": 200,
        "restrictions": "Avoid taking on an empty stomach. Do not exceed 1200mg/day."
    },
    "Advil": {
        "sku": "MED-ADV-200",
        "name": "Advil",
        "drug_class": "NSAIDs",
        "active_ingredients": "Ibuprofen",
        "requires_rx": False,
        "stock_level": 50,
        "restrictions": "Avoid taking on an empty stomach. Do not exceed 1200mg/day."
    },
    "Ritalin": {
        "sku": "MED-RIT-10",
        "name": "Ritalin",
        "drug_class": "Stimulants",
        "active_ingredients": "Methylphenidate",
        "requires_rx": True,
        "stock_level": 5,
        "restrictions": "Controlled substance. Potential for abuse. Monitor heart rate."
    },
    "Lisinopril": {
        "sku": "MED-LIS-10",
        "name": "Lisinopril",
        "drug_class": "ACE Inhibitors",
        "active_ingredients": "Lisinopril",
        "requires_rx": True,
        "stock_level": 50,
        "restrictions": "May cause a persistent dry cough. Monitor blood pressure."
    },
    "Metformin": {
        "sku": "MED-MET-850",
        "name": "Metformin",
        "drug_class": "Biguanides",
        "active_ingredients": "Metformin Hydrochloride",
        "requires_rx": True,
        "stock_level": 80,
        "restrictions": "Take with meals. Avoid excessive alcohol consumption."
    }
}