from app.database import USERS_DB, MEDICATIONS_DB

SYSTEM_PROMPT = """
You are a professional, concise AI Pharmacist Assistant. Your responses must be structured and factual.

LANGUAGE POLICY:
- Always respond in the same language the user uses (Hebrew or English).
- Keep Hebrew responses as concise as English ones.
- Answer the user's specific question first (e.g., the dose) before listing ingredients or stock.

MANDATORY RESPONSE STRUCTURE:
When a user asks about a medication, your response MUST include:
1. ACTIVE INGREDIENTS: List the active ingredients.
2. STOCK STATUS: State if it is currently in stock.
3. PRESCRIPTION STATUS: State if the user has a valid prescription on file.
4. DOSAGE & USAGE: Provide the patient-specific usage instructions from the user's prescription record.
5. SAFETY WARNINGS: Report any allergy conflicts based on drug class and mention medication-specific restrictions (e.g., "Take with food").

POLICIES:
- NO MEDICAL ADVICE: Never suggest a treatment, diagnose, or say "it is safe for you." If asked for advice or safety confirmation, you MUST respond: "I am an AI assistant and cannot provide medical advice. Please consult with our pharmacist or your healthcare professional."
- IDENTITY: CHECK CONTEXT. If "CURRENT_USER_ID" is provided in the system message, you know the user—use that ID for tools and do NOT ask for it. If it is NOT provided, you MUST politely ask for their 9-digit Patient ID before providing any personalized data.
- DATA SOURCE: Use ONLY information provided by tools. If a medication is missing, state that you don't have information on it.
- ALTERNATIVES: If a medication is out of stock, use the 'get_alternatives' tool to find options with the same active ingredient, but remind the user they need a new prescription for any alternative.
- SAFETY FIRST: If an allergy conflict is detected, you MUST start your response with "⚠️ CRITICAL SAFETY ALERT: ALLERGY DETECTED" in bold. 
- NO USAGE FOR ALLERGIES: If a patient is allergic, do NOT provide dosage instructions. Instead, explain the conflict and suggest consulting a doctor for an alternative.
- DIRECT ANSWERS: Always answer the user's specific question in the first sentence before providing the structured bullet points.
"""

def get_patient_details(user_id: str):
    """Fetches the user's name, history, and list of current prescriptions."""
    # This tool is CRITICAL for "Who am I" questions
    user = USERS_DB.get(user_id.strip())
    if not user:
        return {"error": "User not found."}
    return {
        "name": user["name"],
        "history": user["history"],
        "current_prescriptions": [p["name"] for p in user.get("prescriptions", [])],
        "allergies": user.get("allergies", [])
    }

def get_medication_info(name: str):
    """Fetches factual data about a medication (ingredients, restrictions)."""
    med = MEDICATIONS_DB.get(name.strip().capitalize())
    return med if med else {"error": "Medication not found."}


def check_user_status(user_id: str, med_name: str):
    """
    Robustly checks for prescriptions, stock, and allergy conflicts.
    """
    u_id = user_id.strip()
    m_name = med_name.strip().capitalize()

    user = USERS_DB.get(u_id)
    med = MEDICATIONS_DB.get(m_name)

    if not user:
        return {"error": f"Patient ID {u_id} not found."}
    if not med:
        return {"error": f"Medication '{m_name}' not found."}

    # 1. CHECK PRESCRIPTION FIRST (Regardless of allergy)
    rx_entry = next(
        (rx for rx in user.get("prescriptions", []) if rx["name"] == m_name),
        None)
    # It is authorized if they have an Rx OR if the med doesn't require one
    is_authorized = rx_entry is not None or not med.get("requires_rx", True)

    # 2. CHECK ALLERGIES
    user_allergies = [a.lower() for a in user.get("allergies", [])]
    drug_class = med.get("drug_class", "").lower()
    active_ingredients = med.get("active_ingredients", "").lower()

    allergy_conflict = None

    # Check 1: Class Conflict
    if drug_class in user_allergies:
        allergy_conflict = f"CRITICAL SAFETY ALERT: Patient is allergic to {med['drug_class']}."

    # Check 2: Ingredient Conflict
    for allergy in user_allergies:
        if allergy in active_ingredients:
            allergy_conflict = f"CRITICAL SAFETY ALERT: Patient is allergic to active ingredient {allergy}."

    # 3. RETURN STATUS
    if allergy_conflict:
        return {
            "user_name": user["name"],
            "medication": m_name,
            "authorized_by_rx": is_authorized,
            # <--- FIXED: Returns actual DB status (True)
            "patient_usage_instructions": "DO NOT USE. Allergy detected.",
            "medication_restrictions": "ALLERGY CONFLICT.",
            "allergy_conflict": allergy_conflict,
            "stock_available": med.get("stock_level", 0),
            "active_ingredients": med.get("active_ingredients", "Unknown")
        }

    return {
        "user_name": user["name"],
        "medication": m_name,
        "authorized_by_rx": is_authorized,
        "patient_usage_instructions": rx_entry[
            "instructions"] if rx_entry else "No specific prescription found in your records.",
        "medication_restrictions": med.get("restrictions", "None listed."),
        "allergy_conflict": allergy_conflict,
        "stock_available": med.get("stock_level", 0),
        "active_ingredients": med.get("active_ingredients", "Unknown")
    }


def get_alternatives(active_ingredient: str, current_med_name: str = ""):
    """
    Finds medications with the same active ingredient, excluding the current one.
    """
    ingredient_lower = active_ingredient.lower()
    alternatives = [
        m["name"] for m in MEDICATIONS_DB.values()
        if ingredient_lower in m["active_ingredients"].lower()
           and m["name"].lower() != current_med_name.lower()
    ]

    if alternatives:
        return {"alternatives": alternatives}
    return {
        "error": f"No alternatives found with active ingredient: {active_ingredient}"}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_patient_details",
            "description": "Get user name, medical history and list of prescriptions. Use this if the user asks 'Who am I' or 'What do I take'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The 9-digit patient ID."}
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_medication_info",
            "description": "Get factual info, ingredients, and general restrictions for a medication.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The medication name, e.g., 'Amoxicillin'"}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_user_status",
            "description": "Checks user's prescription status, stock, and robustly verifies allergy conflicts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The 9-digit patient ID."},
                    "med_name": {"type": "string", "description": "The name of the medication."}
                },
                "required": ["user_id", "med_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_alternatives",
            "description": "Search for medications containing the same active ingredient.",
            "parameters": {
                "type": "object",
                "properties": {
                    "active_ingredient": {"type": "string",
                                          "description": "The chemical ingredient to search for."},
                    "current_med_name": {"type": "string",
                                         "description": "The med name to exclude from results."}
                },
                "required": ["active_ingredient"]
            }
        }
    }
]