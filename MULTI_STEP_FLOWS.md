# Multi-Step Flows

## Flow 1: Medication Authorization Check with Alternative Discovery

**User scenario:** Customer wants to take a medication, needs safety verification, and if unsafe, looks for alternatives with the same active ingredient.

**Steps:**
1. User asks: "Can I take [medication]?"
2. Agent calls `check_user_status(user_id, medication_name)` (may optionally call `get_patient_details` first)
3. Tool checks if patient has prescription for this medication
4. Tool checks if patient is allergic to medication's active ingredients or drug class
5. Agent responds:
   - If allergy found → Critical Safety Alert (DO NOT USE)
   - If no allergy → Shows medication details (ingredients, stock, prescription status, dosage, warnings)
6. User asks: "What can I take instead?"
7. Agent calls `get_alternatives(active_ingredient, current_medication)`
8. Agent calls `check_user_status(user_id, alternative_name)` for each suggested alternative
9. Agent responds with safe alternatives (same active ingredient) or advises consulting pharmacist if all alternatives are unsafe

**Tools:** `check_user_status`, `get_alternatives`, `get_medication_info` (optional)

**Example:**
- User: "Can I take Ibuprofen?" (Bob - allergic to Ibuprofen)
- Agent: ⚠️ CRITICAL SAFETY ALERT - You are allergic to Ibuprofen. DO NOT USE.
- User: "What can I take instead?"
- Agent: Calls `get_alternatives`, finds Advil (same active ingredient: Ibuprofen), calls `check_user_status` on Advil
- Agent: "Advil also contains Ibuprofen and would trigger your allergy. Please consult your pharmacist for guidance on alternative medications."

---

## Flow 2: Stock Availability Check with Alternative Options

**User scenario:** Customer needs a specific medication but it's out of stock, requiring alternatives with the same active ingredient.

**Steps:**
1. User asks: "Do you have [medication] in stock?"
2. Agent calls `get_medication_info(medication_name)`
3. Tool returns stock level and medication details
4. Agent responds:
   - If in stock → Confirms availability with details
   - If out of stock → Informs user medication is unavailable
5. User asks: "What alternatives do you have?"
6. Agent calls `get_alternatives(active_ingredient, current_medication)`
7. For each alternative found, agent calls `get_medication_info` to check stock
8. Agent calls `check_user_status(user_id, alternative_name)` to verify safety
9. Agent responds with in-stock, safe alternatives (same active ingredient) or informs if no alternatives available

**Tools:** `get_medication_info`, `get_alternatives`, `check_user_status`

**Example:**
- User: "Do you have Advil in stock?" (Dana - no allergies)
- Agent: Calls `get_medication_info`
- Agent: "Advil is currently out of stock (0 units). It contains Ibuprofen as the active ingredient."
- User: "What alternatives do you have?"
- Agent: Calls `get_alternatives` for Ibuprofen active ingredient
- Agent: Calls `get_medication_info` to check stock of alternatives, calls `check_user_status` for safety
- Agent: "Ibuprofen is an alternative with the same active ingredient and is in stock (200 units). You have no allergies to this medication."

---

## Flow 3: Complete Prescription Review with Medication Information

**User scenario:** Customer wants to review their prescriptions and learn detailed information about their medications.

**Steps:**
1. User asks: "What are my prescriptions?" or "Show me my prescription list"
2. Agent calls `get_patient_details(user_id)`
3. Tool returns patient's prescriptions, medical history, and allergies
4. Agent automatically calls `check_user_status(user_id, medication_name)` for EACH prescription to get stock levels, dosage instructions, and safety verification
5. Agent responds with:
   - List of current prescriptions with dosage instructions and stock availability
   - Medical history
   - Known allergies
   - Warning if prescription-allergy conflict detected
6. User asks: "Tell me more about [specific medication from their list]"
7. Agent calls `check_user_status(user_id, medication_name)` to provide complete details
8. Agent responds with detailed medication information (active ingredients, drug class, restrictions, stock level, prescription status, dosage)
9. If conflict exists, agent emphasizes the safety concern and recommends immediate consultation with doctor

**Tools:** `get_patient_details`, `check_user_status`

**Example:**
- User: "What are my prescriptions?" (Hadar - prescribed Lisinopril, allergic to Penicillin, no conflicts)
- Agent: Calls `get_patient_details`, then automatically calls `check_user_status` for Lisinopril
- Agent: "Your prescriptions: Lisinopril (Take 10mg once daily in the morning, 50 units in stock). Known allergies: Penicillin. Medical history: History of hypertension."
- User: "Tell me more about Lisinopril"
- Agent: Calls `check_user_status` for complete details
- Agent: "Lisinopril Details: Active Ingredients: Lisinopril. Stock: 50 units. Prescription Status: Authorized by prescription. Dosage: Take 10mg once daily in the morning. Safety Warnings: May cause a persistent dry cough. Monitor blood pressure."

---

## Key Characteristics of Multi-Step Flows

Each flow demonstrates:
- **Multiple tool calls** across several user-agent exchanges
- **Sequential decision-making** based on previous tool results
- **Complete customer journey** from initial request to resolution
- **Safety verification** at checkpoints
- **No medical advice** - agent only provides factual medication information and directs to healthcare professionals
- **Alternatives are same active ingredient only** - not therapeutic alternatives
- **Professional escalation** when needed (consult pharmacist/doctor)
- **Bilingual support** (can be conducted in Hebrew or English)
