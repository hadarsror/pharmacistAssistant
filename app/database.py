"""
Synthetic Database for Pharmacist Assistant.
10 Users and 5 Medications included.
"""

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
    "204567891": {
        "id": "204567891",
        "name": "Alice Cohen",
        "allergies": [],
        "prescriptions": [{"name": "Metformin", "instructions": "Take 850mg twice daily with meals."}],
        "history": "Type 2 Diabetes."
    },
    "058123456": {
        "id": "058123456",
        "name": "Bob Levy",
        "allergies": ["NSAIDs"],
        "prescriptions": [{"name": "Lisinopril", "instructions": "Take 20mg once daily."}],
        "history": "Hypertension."
    },
    "300987654": {
        "id": "300987654",
        "name": "Dana Silver",
        "allergies": [],
        "prescriptions": [],
        "history": "No known issues."
    },
    "201234567": {
        "id": "201234567",
        "name": "Yossi Mizrahi",
        "allergies": [],
        "prescriptions": [{"name": "Ritalin", "instructions": "Take 10mg twice daily, 30 mins before meals."}],
        "history": "ADHD management."
    },
    "012345678": {
        "id": "012345678",
        "name": "Sarah Goldberg",
        "allergies": [],
        "prescriptions": [{"name": "Amoxicillin", "instructions": "Take 500mg every 12 hours for 7 days."}],
        "history": "Recent dental surgery."
    },
    "111222333": {
        "id": "111222333",
        "name": "Michael Levi",
        "allergies": [],
        "prescriptions": [{"name": "Metformin", "instructions": "Take 500mg once daily."}],
        "history": "Prediabetic."
    },
    "444555666": {
        "id": "444555666",
        "name": "Noa Biton",
        "allergies": [],
        "prescriptions": [{"name": "Ibuprofen", "instructions": "Take 200mg as needed for headaches."}],
        "history": "Seasonal allergies."
    },
    "777888999": {
        "id": "777888999",
        "name": "David Cohen",
        "allergies": ["Penicillin"],
        "prescriptions": [],
        "history": "History of asthma."
    },
    "123123123": {
        "id": "123123123",
        "name": "Maya Avni",
        "allergies": [],
        "prescriptions": [{"name": "Ritalin", "instructions": "Take 20mg once daily in the morning."}],
        "history": "No known allergies."
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