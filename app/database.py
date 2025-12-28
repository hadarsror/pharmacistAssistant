"""
Synthetic Database for Pharmacist Assistant.
Using realistic ID formats and professional data structures.
"""

USERS_DB = {
    "312456789": {
        "id": "312456789",
        "name": "Hadar",
        "age": 28,
        "prescriptions": ["Amoxicillin", "Lisinopril"],
        "history": "Allergic to Penicillin."
    },
    "204567891": {
        "id": "204567891",
        "name": "Alice Cohen",
        "age": 45,
        "prescriptions": ["Metformin"],
        "history": "Type 2 Diabetes."
    },
    "058123456": {
        "id": "058123456",
        "name": "Bob Levy",
        "age": 62,
        "prescriptions": ["Atorvastatin", "Lisinopril"],
        "history": "Hypertension and high cholesterol."
    },
    "300987654": {
        "id": "300987654",
        "name": "Dana Silver",
        "age": 31,
        "prescriptions": [],
        "history": "No known allergies."
    },
    "201234567": {
        "id": "201234567",
        "name": "Yossi Mizrahi",
        "age": 19,
        "prescriptions": ["Ritalin"],
        "history": "ADHD management."
    },
    "012345678": {
        "id": "012345678",
        "name": "Sarah Goldberg",
        "age": 74,
        "prescriptions": ["Amoxicillin"],
        "history": "Recent dental surgery."
    }
}

MEDICATIONS_DB = {
    "Amoxicillin": {
        "sku": "MED-AMX-500",
        "name": "Amoxicillin",
        "active_ingredients": "Amoxicillin Trihydrate",
        "requires_rx": True,
        "stock_level": 12,
        "usage": "Take 500mg every 8 hours for 7-10 days.",
        "warnings": "Do not take if allergic to penicillin."
    },
    "Ibuprofen": {
        "sku": "MED-IBU-200",
        "name": "Ibuprofen",
        "active_ingredients": "Ibuprofen",
        "requires_rx": False,
        "stock_level": 200,
        "usage": "200-400mg every 4-6 hours as needed.",
        "warnings": "Avoid taking on an empty stomach."
    },
    "Ritalin": {
        "sku": "MED-RIT-10",
        "name": "Ritalin",
        "active_ingredients": "Methylphenidate",
        "requires_rx": True,
        "stock_level": 5,
        "usage": "Follow physician's precise timing.",
        "warnings": "Controlled substance. Potential for abuse."
    }
}