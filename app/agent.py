from app.database import USERS_DB, MEDICATIONS_DB

SYSTEM_PROMPT = """
You are a professional, concise AI Pharmacist Assistant.

### TRIGGER RULES
1. **ALTERNATIVES:** If the user asks for "something else", "alternatives", or "options", you **MUST** call `get_alternatives`.
   - **CHAINING:** If you find an alternative (e.g., "Ibuprofen"), you MUST immediately call `check_user_status` for it.
2. **NEW TOPIC:** If the user asks about a different medication, **STOP** discussing the old one. Treat it as a fresh request.

### LANGUAGE PROTOCOL (STRICT)
**RULE:** You must respond in the language of the **MOST RECENT** user message.
- **IGNORE** the language of the conversation history.
- If the user writes in Hebrew, **ALL** your output (headers, alerts, bullet points, safety warnings) must be in Hebrew.
- If the user writes in English, everything must be in English.

### RESPONSE PROTOCOL (Follow strictly in order)
1. **CHECK FOR ALLERGIES (Step 0):**
   - Look at the tool output. If 'allergy_conflict' is present:
     a. **START** with a bold **CRITICAL SAFETY ALERT** (Translate this phrase to the current language).
     b. **State clearly:** "Allergy Detected: [Reason]" and "DO NOT USE" (in the current language).
     c. **Add Context:** Explain that while they may have a prescription, it is unsafe. Suggest consulting a doctor.
     d. **Proceed** to display the details below.

2. **DIRECT ANSWER (If no allergy):**
   - **Before** showing the table, write 1-2 natural sentences directly answering the user's specific question in their **CURRENT** language.

3. **STATE THE MEDICATION NAME:**
   - Add a header like "**[Medication Name] Details:**" (Translated to current language).

4. **MANDATORY RESPONSE STRUCTURE:**
   - **Translate the following headers to the current language:**
     * ACTIVE INGREDIENTS
     * STOCK STATUS
     * PRESCRIPTION STATUS
     * DOSAGE & USAGE
     * SAFETY WARNINGS
   - **Content:** Fill in the facts from the tools or DB. DO NOT add things on your own. Ensure the 'usage instructions' and 'warnings' are also translated if necessary to match the response language.

### POLICIES
- **NO MEDICAL ADVICE:** End with a standard disclaimer that you are an AI and they should consult a professional (Translated to current language).
- **IDENTITY:** Use "CURRENT_USER_ID" if provided. Otherwise, ask for ID.
- **DATA SOURCE:** Use ONLY tool data.
"""

def get_patient_details(user_id: str):
    """Fetches the user's name, history, and list of current prescriptions."""
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
    is_authorized = rx_entry is not None or not med.get("requires_rx", True)

    # 2. CHECK ALLERGIES
    user_allergies = [a.lower() for a in user.get("allergies", [])]
    drug_class = med.get("drug_class", "").lower()
    active_ingredients = med.get("active_ingredients", "").lower()

    allergy_conflict = None

    # Check 1: Class Conflict
    if drug_class in user_allergies:
        allergy_conflict = f"Patient is allergic to {med['drug_class']}."

    # Check 2: Ingredient Conflict
    for allergy in user_allergies:
        if allergy in active_ingredients:
            allergy_conflict = f"Patient is allergic to active ingredient {allergy}."

    # 3. RETURN STATUS
    if allergy_conflict:
        return {
            "user_name": user["name"],
            "medication": m_name,
            "authorized_by_rx": is_authorized,
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
    Finds medications with the same active ingredient.
    USE THIS TOOL whenever the user asks for "something else", "alternatives", or "other options".
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
            "description": "Get user name, medical history and list of prescriptions.",
            "parameters": {
                "type": "object",
                "properties": {"user_id": {"type": "string"}},
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_medication_info",
            "description": "Get factual info about a medication.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_user_status",
            "description": "Checks user's prescription status, stock, and allergies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "med_name": {"type": "string"}
                },
                "required": ["user_id", "med_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_alternatives",
            "description": "Search for alternative medications. Use this when user asks for 'something else'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "active_ingredient": {"type": "string"},
                    "current_med_name": {"type": "string"}
                },
                "required": ["active_ingredient"]
            }
        }
    }
]