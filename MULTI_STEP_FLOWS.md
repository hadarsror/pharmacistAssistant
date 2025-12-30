# Multi-Step Flows

## Flow 1: Medication Authorization Check

**User asks:** "Can I take [medication]?"

**Steps:**
1. Agent calls `check_user_status(user_id, medication_name)`
2. Tool checks if patient has prescription for this medication
3. Tool checks if patient is allergic to medication's active ingredients or drug class
4. Agent responds:
   - If allergy found → Critical Safety Alert (DO NOT USE)
   - If no allergy → Shows medication details (ingredients, stock, prescription status, dosage, warnings)

**Tools:** `check_user_status`, `get_medication_info` (optional)

---

## Flow 2: Alternative Medication Discovery

**User asks:** "I need an alternative to [medication]"

**Steps:**
1. Agent calls `get_alternatives(active_ingredient, current_medication)`
2. Tool finds medications with same active ingredient
3. Agent calls `check_user_status(user_id, alternative_name)` for suggested alternative
4. Agent responds:
   - If alternative is safe → Shows alternative details
   - If alternative also causes allergy → Warns user
   - If no alternatives exist → Informs user to consult doctor

**Tools:** `get_alternatives`, `check_user_status`, `get_medication_info` (optional)

---

## Flow 3: Complete Prescription Review

**User asks:** "What are my prescriptions?"

**Steps:**
1. Agent calls `get_patient_details(user_id)`
2. Tool returns patient's prescriptions, medical history, and allergies
3. Agent responds with:
   - List of current prescriptions with dosage instructions
   - Medical history
   - Known allergies
   - Warning if prescription-allergy conflict detected

**Tools:** `get_patient_details`

---

## Examples

**Flow 1 Example:**
User: "Can I take Ibuprofen?" (Bob - allergic to Ibuprofen)
Agent: ⚠️ CRITICAL SAFETY ALERT - You are allergic to Ibuprofen. DO NOT USE.



**Flow 2 Example:**
User: "Alternative to Ibuprofen?" (Dana - no allergies)
Agent: "An alternative is Advil (same active ingredient). Stock: 50 units."



**Flow 3 Example:**
User: "What are my prescriptions?" (Hadar)
Agent: "Your prescriptions: Lisinopril (Take 10mg once daily). Known allergies: Penicillin."


undefined