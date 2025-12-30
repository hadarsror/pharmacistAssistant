"""
OpenAI tool schemas for function calling.
Defines the JSON schemas that OpenAI uses to understand available tools.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_patient_details",
            "description": "Retrieve patient name, medical history, current prescriptions, and known allergies. Use this when you need to understand a patient's medical background.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "9-digit patient identifier"
                    }
                },
                "required": ["user_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_medication_info",
            "description": "Get factual information about a medication including active ingredients, drug class, stock level, and general restrictions. Does NOT include patient-specific authorization.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Medication name (e.g., 'Ibuprofen', 'Advil')"
                    }
                },
                "required": ["name"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_user_status",
            "description": "Check if a specific patient is authorized to take a medication. Verifies prescription status, checks for allergy conflicts, and provides patient-specific usage instructions. This is the PRIMARY safety check tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "9-digit patient identifier"
                    },
                    "med_name": {
                        "type": "string",
                        "description": "Medication name to check"
                    }
                },
                "required": ["user_id", "med_name"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_alternatives",
            "description": "Find alternative medications with the same active ingredient. Use when patient cannot take current medication due to allergies, stock issues, or preference. After getting alternatives, you should call check_user_status on the suggested alternative.",
            "parameters": {
                "type": "object",
                "properties": {
                    "active_ingredient": {
                        "type": "string",
                        "description": "Active ingredient to search for (e.g., 'Ibuprofen', 'Methylphenidate')"
                    },
                    "current_med_name": {
                        "type": "string",
                        "description": "Current medication name to exclude from results"
                    },
                    "exclude_drug_classes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of drug classes to filter out (e.g., ['Penicillin', 'NSAIDs'])"
                    }
                },
                "required": ["active_ingredient"],
                "additionalProperties": False
            }
        }
    }
]
