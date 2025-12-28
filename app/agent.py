from app.database import USERS_DB, MEDICATIONS_DB

SYSTEM_PROMPT = """
You are a professional, concise AI Pharmacist Assistant. Your responses must be structured and factual.

MANDATORY RESPONSE STRUCTURE:
When a user asks about a medication, your response MUST include:
1. ACTIVE INGREDIENTS: List the active ingredients.
2. STOCK STATUS: State if it is currently in stock.
3. PRESCRIPTION STATUS: State if the user has a valid prescription on file.
4. DOSAGE & USAGE: Provide the patient-specific usage instructions from the user's prescription record.
5. SAFETY WARNINGS: Report any allergy conflicts based on drug class and mention medication-specific restrictions (e.g., "Take with food").

POLICIES:
- NO MEDICAL ADVICE: Never suggest a treatment or diagnose. If asked for advice, respond: "I cannot provide medical advice. Please consult a healthcare professional."
- IDENTITY: If a CURRENT_USER_ID is provided by the system context, proceed silently without asking for it. If not, you MUST ask for the 9-digit Patient ID before calling tools.
- BREVITY: Use bullet points for the structure above. Do not use conversational filler like "I'd be happy to help."
- DATA SOURCE: Use ONLY information provided by the tools. If a medication is missing from the database, state that you don't have information on it.
"""

def get_medication_info(name: str):
    """Fetches factual data about a medication (ingredients, restrictions)."""
    med = MEDICATIONS_DB.get(name.strip().capitalize())
    return med if med else {"error": "Medication not found."}

def check_user_status(user_id: str, med_name: str):
    """
    Robustly checks for prescriptions, stock, and allergy conflicts.
    Logic is data-driven: compares med['drug_class'] to user['allergies'].
    """
    u_id = user_id.strip()
    m_name = med_name.strip().capitalize()

    user = USERS_DB.get(u_id)
    med = MEDICATIONS_DB.get(m_name)

    if not user:
        return {"error": f"Patient ID {u_id} not found."}
    if not med:
        return {"error": f"Medication '{m_name}' not found."}

    # Data-driven Allergy Check
    allergy_conflict = None
    if med.get("drug_class") in user.get("allergies", []):
        allergy_conflict = f"SAFETY ALERT: Patient history shows an allergy to {med['drug_class']}."

    # Patient-specific usage from the User's prescription record
    rx_entry = next((rx for rx in user.get("prescriptions", []) if rx["name"] == m_name), None)

    return {
        "user_name": user["name"],
        "medication": m_name,
        "authorized_by_rx": not med.get("requires_rx", True) or rx_entry is not None,
        "patient_usage_instructions": rx_entry["instructions"] if rx_entry else "No specific prescription found in your records.",
        "medication_restrictions": med.get("restrictions", "None listed."),
        "allergy_conflict": allergy_conflict,
        "stock_available": med.get("stock_level", 0),
        "active_ingredients": med.get("active_ingredients", "Unknown")
    }

def get_alternatives(active_ingredient: str):
    """
    Finds medications with the same active ingredient.
    Fulfills the 3rd tool requirement for inventory/alternative flows.
    """
    alternatives = [m["name"] for m in MEDICATIONS_DB.values()
                    if active_ingredient.lower() in m["active_ingredients"].lower()]
    return {"alternatives": alternatives} if alternatives else {"error": "No alternatives found with that active ingredient."}

TOOLS = [
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
                    "active_ingredient": {"type": "string", "description": "The chemical ingredient to search for."}
                },
                "required": ["active_ingredient"]
            }
        }
    }
]