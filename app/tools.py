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
        name: Medication name (case-insensitive, will be capitalized)

    Returns:
        Dictionary containing medication details: sku, name, drug_class,
        active_ingredients, requires_rx, stock_level, restrictions.
        Returns error dictionary if medication not found.

    Error Handling:
        - Medication not found: Returns {"error": "Medication not found."}

    Fallback Behavior:
        - Case-insensitive matching via capitalization
    """
    name = name.strip().capitalize()
    logger.info(f"Fetching medication info for: {name}")

    med = MEDICATIONS_DB.get(name)
    if not med:
        logger.warning(f"Medication not found: {name}")
        return {"error": "Medication not found."}

    return med


def check_user_status(user_id: str, med_name: str) -> Dict[str, Any]:
    """
    Check if a user is authorized to take a medication and verify allergies.

    This is the core safety tool that combines prescription verification,
    allergy checking, and stock availability.

    Args:
        user_id: Patient identifier (9-digit string)
        med_name: Medication name (case-insensitive)

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
    """
    user_id = user_id.strip()
    med_name = med_name.strip().capitalize()
    logger.info(
        f"Checking user status: user_id={user_id}, med_name={med_name}")

    user = USERS_DB.get(user_id)
    med = MEDICATIONS_DB.get(med_name)

    if not user:
        logger.error(f"Patient not found: {user_id}")
        return {"error": f"Patient ID {user_id} not found."}

    if not med:
        logger.error(f"Medication not found: {med_name}")
        return {"error": f"Medication '{med_name}' not found."}

    # Check prescription authorization
    rx_entry = next(
        (rx for rx in user.get("prescriptions", []) if rx["name"] == med_name),
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
                logger.warning(
                    f"Allergy conflict detected: {allergy_conflict}")
                break

    result = {
        "user_name": user["name"],
        "medication": med_name,
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
