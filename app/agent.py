from app.database import USERS_DB, MEDICATIONS_DB

SYSTEM_PROMPT = """
You are a professional, concise AI Pharmacist Assistant.

### TRIGGER RULES (CRITICAL)
1. **SWITCHING MEDS:** If the user asks about a general ingredient (e.g., "Ibuprofen") or a different medication, you **MUST** call tools for THAT specific name. **DO NOT** assume they mean the brand you just discussed (e.g., do not look up "Advil" if they asked for "Ibuprofen").
2. **ALTERNATIVES:** If the user asks for "something else", call `get_alternatives`.
   - **CHAINING:** Pick ONE alternative from the result and immediately call `check_user_status` for it.

### LANGUAGE PROTOCOL
**RULE:** Respond in the language of the **MOST RECENT** user message.
- **Hebrew:** Translate **everything** (headers, values, alerts).
- **English:** Keep everything in English.

### RESPONSE STRUCTURE (Strictly follow this order)

1. **SAFETY CHECK (Silent Step):**
   - Check 'allergy_conflict' in tool output.
   - **IF CONFLICT:** Start with bold **CRITICAL SAFETY ALERT** and "DO NOT USE".
   - **IF NO CONFLICT:** Skip to Step 2. (Do not write "Check passed").

2. **DIRECT ANSWER:**
   - Answer the question directly (e.g., "Yes, we have 200 packs of Ibuprofen.").
   - Address the user by **Name** (if available).

3. **MEDICATION DETAILS:**
   - Header: "**[Medication Name] Details:**"
   - **Active Ingredients:** [Value from DB]
   - **Stock Status:** [Value from DB] (e.g., "200 units")
   - **Prescription Status:** - If `authorized_by_rx` is True -> "Approved" / "No prescription required".
     - If False -> "Prescription required but not found".
   - **Dosage & Usage:** - If specific instructions exist in DB -> Show them.
     - If "No specific prescription found" -> Write "Follow standard label instructions." (Do NOT copy the safety warnings here).
   - **Safety Warnings:** [Value from DB]

### POLICIES
- **NO MEDICAL ADVICE:** End with a standard disclaimer.
- **IDENTITY:** Never output "CURRENT_USER_ID".
"""


# ... (Keep the rest of your functions: get_patient_details, get_medication_info, check_user_status, get_alternatives, and TOOLS exactly as they were in the previous file) ...
# (I am omitting the python functions below to save space, but DO NOT DELETE THEM from your file)
def get_patient_details(user_id: str):
    user = USERS_DB.get(user_id.strip())
    if not user: return {"error": "User not found."}
    return {
        "name": user["name"],
        "history": user["history"],
        "current_prescriptions": [p["name"] for p in
                                  user.get("prescriptions", [])],
        "allergies": user.get("allergies", [])
    }


def get_medication_info(name: str):
    med = MEDICATIONS_DB.get(name.strip().capitalize())
    return med if med else {"error": "Medication not found."}


def check_user_status(user_id: str, med_name: str):
    u_id = user_id.strip()
    m_name = med_name.strip().capitalize()
    user = USERS_DB.get(u_id)
    med = MEDICATIONS_DB.get(m_name)
    if not user: return {"error": f"Patient ID {u_id} not found."}
    if not med: return {"error": f"Medication '{m_name}' not found."}

    rx_entry = next(
        (rx for rx in user.get("prescriptions", []) if rx["name"] == m_name),
        None)
    is_authorized = rx_entry is not None or not med.get("requires_rx", True)

    user_allergies = [a.lower() for a in user.get("allergies", [])]
    drug_class = med.get("drug_class", "").lower()
    active_ingredients = med.get("active_ingredients", "").lower()

    allergy_conflict = None
    if drug_class in user_allergies:
        allergy_conflict = f"Patient is allergic to {med['drug_class']}."
    for allergy in user_allergies:
        if allergy in active_ingredients:
            allergy_conflict = f"Patient is allergic to active ingredient {allergy}."

    result = {
        "user_name": user["name"],
        "medication": m_name,
        "authorized_by_rx": is_authorized,
        "patient_usage_instructions": rx_entry[
            "instructions"] if rx_entry else "No specific prescription found.",
        "medication_restrictions": med.get("restrictions", "None listed."),
        "allergy_conflict": allergy_conflict,
        "stock_available": med.get("stock_level", 0),
        "active_ingredients": med.get("active_ingredients", "Unknown")
    }

    if allergy_conflict:
        result["patient_usage_instructions"] = "DO NOT USE. Allergy detected."
        result["medication_restrictions"] = "ALLERGY CONFLICT."

    return result


def get_alternatives(active_ingredient: str, current_med_name: str = ""):
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