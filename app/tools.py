"""
Tool implementations for the pharmacy assistant agent.
Each tool provides specific functionality for medication and patient management.
"""

from typing import Dict, List, Optional, Any
import logging
from app.database import USERS_DB, MEDICATIONS_DB

logger = logging.getLogger(__name__)


def get_patient_details(user_id: str) -> Dict[str, Any]:
    """
    Retrieve patient demographic and medical information.

    Args:
        user_id: Patient identifier (9-digit string)

    Returns:
        Dictionary containing patient name, medical history, prescriptions, and allergies.
        Returns error dictionary if user not found.

    Error Handling:
        - Invalid user_id: Returns {"error": "User not found."}

    Fallback Behavior:
        - Missing fields default to empty lists/strings
    """
    user_id = user_id.strip()
    logger.info(f"Fetching patient details for user_id: {user_id}")

    user = USERS_DB.get(user_id)
    if not user:
        logger.warning(f"User not found: {user_id}")
        return {"error": "User not found."}

    return {
        "name": user.get("name", "Unknown"),
        "history": user.get("history", "No medical history available."),
        "current_prescriptions": [p["name"] for p in
                                  user.get("prescriptions", [])],
        "allergies": user.get("allergies", [])
    }


def get_medication_info(name: str) -> Dict[str, Any]:
    """
    Retrieve factual information about a specific medication.


    Args:
        name: Medication name (English or Hebrew, case-insensitive for English)


    Returns:
        Dictionary containing medication details: sku, name, name_hebrew, drug_class,
        active_ingredients, requires_rx, stock_level, restrictions.
        Returns error dictionary if medication not found.


    Error Handling:
        - Medication not found: Returns {"error": "Medication not found."}


    Fallback Behavior:
        - Case-insensitive matching via capitalization for English names
        - Exact match for Hebrew names
    """
    name = name.strip()
    logger.info(f"Fetching medication info for: {name}")

    # Try English name (case-insensitive via capitalization)
    name_capitalized = name.capitalize()
    med = MEDICATIONS_DB.get(name_capitalized)
    
    if med:
        return med
    
    # Try Hebrew name (exact match with normalization)
    for med_key, med_data in MEDICATIONS_DB.items():
        if med_data.get("name_hebrew", "").strip() == name:
            logger.info(f"Found medication by Hebrew name: {name} -> {med_key}")
            return med_data
    
    # Not found
    logger.warning(f"Medication not found: {name}")
    return {"error": "Medication not found."}



def check_user_status(user_id: str, med_name: str) -> Dict[str, Any]:
    """
    Check if a user is authorized to take a medication and verify allergies.

    This is the core safety tool that combines prescription verification,
    allergy checking, and stock availability.

    Args:
        user_id: Patient identifier (9-digit string)
        med_name: Medication name (English or Hebrew, case-insensitive for English)

    Returns:
        Dictionary containing:
        - user_name: Patient name
        - medication: Medication name
        - authorized_by_rx: Boolean indicating prescription authorization
        - patient_usage_instructions: Prescription instructions or default message
        - medication_restrictions: Usage restrictions
        - allergy_conflict: String describing allergy issue or None
        - stock_available: Integer stock level
        - active_ingredients: String of active ingredients

    Error Handling:
        - Invalid user_id: Returns {"error": "Patient ID {id} not found."}
        - Invalid med_name: Returns {"error": "Medication '{name}' not found."}

    Fallback Behavior:
        - If no prescription exists but medication doesn't require Rx: authorized=True
        - If allergy detected: Sets usage_instructions to "DO NOT USE"
        - Case-insensitive matching via capitalization for English names
        - Exact match for Hebrew names
    """
    user_id = user_id.strip()
    med_name_original = med_name.strip()
    logger.info(f"Checking user status: user_id={user_id}, med_name={med_name_original}")

    user = USERS_DB.get(user_id)
    
    if not user:
        logger.error(f"Patient not found: {user_id}")
        return {"error": f"Patient ID {user_id} not found."}

    # Try to find medication by English name (case-insensitive)
    med_name_capitalized = med_name_original.capitalize()
    med = MEDICATIONS_DB.get(med_name_capitalized)
    med_key = med_name_capitalized
    
    # If not found, try Hebrew name (with normalization)
    if not med:
        for key, med_data in MEDICATIONS_DB.items():
            if med_data.get("name_hebrew", "").strip() == med_name_original:
                logger.info(f"Found medication by Hebrew name: {med_name_original} -> {key}")
                med = med_data
                med_key = key
                break
    
    if not med:
        logger.error(f"Medication not found: {med_name_original}")
        return {"error": f"Medication '{med_name_original}' not found."}

    # Check prescription authorization (prescriptions use English names)
    rx_entry = next(
        (rx for rx in user.get("prescriptions", []) if rx["name"] == med_key),
        None
    )
    is_authorized = rx_entry is not None or not med.get("requires_rx", True)

    # Check for allergy conflicts
    user_allergies = [a.lower() for a in user.get("allergies", [])]
    drug_class = med.get("drug_class", "").lower()
    active_ingredients = med.get("active_ingredients", "").lower()

    allergy_conflict = None
    if drug_class in user_allergies:
        allergy_conflict = f"Patient is allergic to {med['drug_class']}."
        logger.warning(f"Allergy conflict detected: {allergy_conflict}")
    else:
        for allergy in user_allergies:
            if allergy in active_ingredients:
                allergy_conflict = f"Patient is allergic to active ingredient {allergy}."
                logger.warning(f"Allergy conflict detected: {allergy_conflict}")
                break

    # Determine which name to return based on input language
    med_name_to_return = med_name_original if med_name_original == med.get("name_hebrew") else med_key

    result = {
        "user_name": user["name"],
        "user_name_hebrew": user.get("name_hebrew", user["name"]),
        "medication": med_name_to_return,  # Return name in the language requested
        "authorized_by_rx": is_authorized,
        "has_prescription": rx_entry is not None,  # Whether user has a prescription on file
        "requires_prescription": med.get("requires_rx", True),  # Whether medication needs Rx
        "patient_usage_instructions": rx_entry["instructions"] if rx_entry else "No specific prescription found.",
        "medication_restrictions": med.get("restrictions", "None listed."),
        "allergy_conflict": allergy_conflict,
        "stock_available": med.get("stock_level", 0),
        "active_ingredients": med.get("active_ingredients", "Unknown")
    }

    if allergy_conflict:
        result["patient_usage_instructions"] = "DO NOT USE. Allergy detected."
        result["medication_restrictions"] = "ALLERGY CONFLICT."

    return result



def get_alternatives(
        active_ingredient: str,
        current_med_name: str = "",
        exclude_drug_classes: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Find alternative medications containing the same active ingredient.

    Args:
        active_ingredient: The active ingredient to search for
        current_med_name: Current medication to exclude from results (optional)
        exclude_drug_classes: List of drug classes to filter out (optional)

    Returns:
        Dictionary containing list of alternative medication names.
        Returns error dictionary if no alternatives found.

    Error Handling:
        - No alternatives found: Returns {"error": "No alternatives found..."}

    Fallback Behavior:
        - Case-insensitive matching
        - Excludes current medication from results
        - Filters out specified drug classes
    """
    ingredient_lower = active_ingredient.strip().lower()
    current_med_lower = current_med_name.strip().lower()
    exclude_classes = [c.lower() for c in (exclude_drug_classes or [])]

    logger.info(f"Searching alternatives for ingredient: {active_ingredient}")

    alternatives = [
        m["name"] for m in MEDICATIONS_DB.values()
        if ingredient_lower in m["active_ingredients"].lower()
           and m["name"].lower() != current_med_lower
           and m["drug_class"].lower() not in exclude_classes
    ]

    if alternatives:
        logger.info(f"Found {len(alternatives)} alternatives: {alternatives}")
        return {"alternatives": alternatives}

    logger.warning(
        f"No alternatives found for ingredient: {active_ingredient}")
    return {
        "error": f"No alternatives found with active ingredient: {active_ingredient}"
    }
