from app.database import USERS_DB, MEDICATIONS_DB

SYSTEM_PROMPT = """
You are an AI Pharmacist Assistant for a retail pharmacy chain.
Your goal is to assist customers with medication facts, stock checks, and prescription status.

CRITICAL POLICIES:
1. NO MEDICAL ADVICE: Never diagnose or recommend a treatment. If asked "what should I take for X?", respond: "I cannot provide medical advice or diagnoses. Please consult a healthcare professional."
2. FACTUAL ONLY: Use the provided tools for every data point. If a medication is not in the database, say you don't have information on it.
3. ALLERGY SAFETY: Before confirming interest in a medication, check the user's 'history' for allergies. If a conflict exists (e.g., Penicillin allergy and Amoxicillin), warn the user immediately.
4. PRESCRIPTION CHECK: If a medication 'requires_rx' is True, you must verify the user has it in their 'prescriptions' list before confirming availability for them.
5. TONE: Professional, efficient, and helpful.
6. LANGUAGE: Respond in the language used by the user (Hebrew or English).

MULTI-STEP FLOW LOGIC:
- If a user wants to buy/refill: Check User -> Check Med Info -> Check Stock -> Check Allergy Conflict -> Final Answer.
"""

SYSTEM_PROMPT = """
You are an AI Pharmacist Assistant for a retail pharmacy chain.
Your goal is to assist customers with medication facts, stock checks, and prescription status.

IDENTITY VERIFICATION POLICY:
- Every conversation MUST start by identifying the patient.
- If the user asks for medication info, stock, or refills but has NOT provided their 9-digit Patient ID, you MUST politely ask for it first.
- Example: "I'd be happy to help. May I please have your 9-digit Patient ID to access your records?"
- Do NOT call 'check_user_status' until you have the ID.

CRITICAL POLICIES:
1. NO MEDICAL ADVICE: Never diagnose or recommend a treatment. 
2. FACTUAL ONLY: Use the provided tools for every data point.
3. ALLERGY SAFETY: Before confirming interest in a medication, use the tool to check 'history'.
4. PRESCRIPTION CHECK: Verify 'requires_rx' status before confirming availability.
5. TONE: Professional, efficient, and helpful.
6. LANGUAGE: Respond in the language used by the user (Hebrew or English).

MULTI-STEP FLOW LOGIC:
1. Greet User -> 2. Request/Verify Patient ID -> 3. Call check_user_status -> 4. Check Allergy/Stock/RX -> 5. Final Answer.
"""

def get_medication_info(name: str):
    """Fetches factual data about a medication (ingredients, usage)."""
    med = MEDICATIONS_DB.get(name.strip().capitalize())
    return med if med else {"error": "Medication not found."}

def check_user_status(user_id: str, med_name: str):
    """
    Executes a multi-step verification flow.
    Requires a valid 9-digit user_id.
    """
    u_id = user_id.strip()
    m_name = med_name.strip().capitalize()

    user = USERS_DB.get(u_id)
    med = MEDICATIONS_DB.get(m_name)

    if not user:
        return {"error": f"Patient ID {u_id} not found in our records. Please verify the ID."}
    if not med:
        return {"error": f"Medication '{m_name}' not found."}

    # Allergy Check
    allergy_warning = None
    if "Penicillin" in user["history"] and "Amoxicillin" in med["active_ingredients"]:
        allergy_warning = f"SAFETY ALERT: Patient history shows {user['history']}. Amoxicillin is a Penicillin-class drug."

    return {
        "user_name": user["name"],
        "medication": m_name,
        "authorized_by_rx": not med["requires_rx"] or m_name in user["prescriptions"],
        "allergy_conflict": allergy_warning,
        "stock_available": med["stock_level"],
        "usage_instructions": med["usage"]
    }

# Update TOOLS schema to reflect the new check_user_status function
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_medication_info",
            "description": "Get factual info, ingredients, and usage for a medication.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string",
                             "description": "The name of the medication, e.g., 'Ibuprofen'"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_user_status",
            "description": "Checks if the user has a prescription, enough stock, and no allergy conflicts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string",
                                "description": "The ID of the user, e.g., 'U1'"},
                    "med_name": {"type": "string",
                                 "description": "The medication they are asking about."}
                },
                "required": ["user_id", "med_name"]
            }
        }
    }
]