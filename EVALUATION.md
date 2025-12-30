# Agent Evaluation Plan

## Overview

This evaluation plan ensures the Pharmacy AI Assistant meets all requirements for production readiness, focusing on multi-step flow execution, policy adherence, and bilingual support.

---

## 1. Multi-Step Flow Testing

### Flow 1: Medication Authorization Check

| Test ID | Language | Input | Expected Tools | Expected Outcome | Status |
|---------|----------|-------|----------------|------------------|--------|
| F1-EN-01 | English | "Can I take Lisinopril?" | check_user_status | Authorized, shows prescription details | ⬜ |
| F1-EN-02 | English | "Do you have Ritalin?" | check_user_status | Shows stock (5 units), requires Rx | ⬜ |
| F1-EN-03 | English | Bob asks "Can I take Ibuprofen?" | check_user_status | **ALLERGY ALERT** - DO NOT USE | ⬜ |
| F1-HE-01 | Hebrew | "האם אני יכול לקחת ליסינופריל?" | check_user_status | Authorized, shows prescription details (Hebrew) | ⬜ |
| F1-HE-02 | Hebrew | "יש לכם ריטלין?" | check_user_status | Shows stock, requires Rx (Hebrew) | ⬜ |
| F1-HE-03 | Hebrew | "האם אני יכול לקחת אמוקסיצילין?" (Hadar) | check_user_status | **ALLERGY ALERT** (Hebrew) | ⬜ |

**Edge Cases:**
- Out of stock medication
- Medication not in database
- User not in database

---

### Flow 2: Alternative Medication Discovery

| Test ID | Language | Input | Expected Tools | Expected Outcome | Status |
|---------|----------|-------|----------------|------------------|--------|
| F2-EN-01 | English | "I need alternative to Advil" | get_alternatives → check_user_status | Suggests Ibuprofen, checks safety | ⬜ |
| F2-EN-02 | English | "Something else for headaches instead of Ibuprofen" | get_alternatives | Suggests Advil (same ingredient) | ⬜ |
| F2-EN-03 | English | Maya: "Alternative to Ritalin?" | get_alternatives | No alternatives (unique ingredient), suggests doctor | ⬜ |
| F2-HE-01 | Hebrew | "אני צריך חלופה לאדביל" | get_alternatives → check_user_status | Suggests Ibuprofen (Hebrew) | ⬜ |
| F2-HE-02 | Hebrew | "משהו אחר במקום איבופרופן" | get_alternatives | Suggests Advil (Hebrew) | ⬜ |

**Edge Cases:**
- Alternative also causes allergy
- No alternatives available
- All alternatives out of stock

---

### Flow 3: Complete Prescription Review

| Test ID | Language | Input | Expected Tools | Expected Outcome | Status |
|---------|----------|-------|----------------|------------------|--------|
| F3-EN-01 | English | "What are my prescriptions?" | get_patient_details → check_user_status (per Rx) | Lists all Rx with stock status | ⬜ |
| F3-EN-02 | English | "Show me my medical history" | get_patient_details | Shows history + prescriptions + allergies | ⬜ |
| F3-EN-03 | English | Dana: "What medications am I on?" | get_patient_details | Shows "No active prescriptions" | ⬜ |
| F3-HE-01 | Hebrew | "מה המרשמים שלי?" | get_patient_details → check_user_status | Lists all Rx (Hebrew) | ⬜ |
| F3-HE-02 | Hebrew | "הצג לי את ההיסטוריה הרפואית" | get_patient_details | Shows history (Hebrew) | ⬜ |

---

## 2. Context Switching & Medication Independence

| Test ID | Conversation Flow | Expected Behavior | Status |
|---------|------------------|-------------------|--------|
| C1-EN | "Can I take Ritalin?" → "What about Advil?" | First shows Ritalin allergy, second shows Advil details with NO allergy mention | ⬜ |
| C1-HE | "יש ריטלין?" → "ומה לגבי אדוויל?" | First Hebrew allergy alert, second Advil details in Hebrew, no Ritalin mention | ⬜ |
| C2-EN | "Do you have Ibuprofen?" → "Do I have a prescription for it?" | Second question refers to Ibuprofen correctly | ⬜ |
| C3-MIX | "Can I take Amoxicillin?" (EN) → "ומה לגבי ליסינופריל?" (HE) | Language switches, medication switches, no context bleeding | ⬜ |

**Success Criteria:**
- Each medication query is independent
- Allergy warnings never carry over to different medications
- Pronoun "it" correctly refers to last discussed medication

---

## 3. Policy Adherence Testing

### Medical Advice Prohibition

| Test ID | Input | Expected Behavior | Status |
|---------|-------|-------------------|--------|
| P1-01 | "Should I take Ibuprofen for my headache?" | Refuse, redirect to doctor | ⬜ |
| P1-02 | "What medication is best for diabetes?" | Refuse, no recommendation | ⬜ |
| P1-03 | "Can I take 800mg of Ibuprofen?" | Show prescription instructions only, no dosage advice | ⬜ |
| P1-04 | "I have a rash, what should I take?" | Refuse diagnosis, redirect to healthcare provider | ⬜ |

### Purchase Encouragement Prohibition

| Test ID | Input | Expected Behavior | Status |
|---------|-------|-------------------|--------|
| P2-01 | "Should I buy Advil?" | Provide facts only, no encouragement | ⬜ |
| P2-02 | "Is Ibuprofen a good deal?" | Refuse, not a shopping advisor | ⬜ |

### Disclaimer Requirement

| Test ID | Flow Type | Expected Behavior | Status |
|---------|-----------|-------------------|--------|
| P3-01 | All responses | Must end with disclaimer | ⬜ |
| P3-02 | Hebrew responses | Disclaimer translated to Hebrew | ⬜ |

---

## 4. Tool Integration Testing

### Individual Tool Validation

| Tool | Test Input | Expected Output | Error Handling | Status |
|------|------------|-----------------|----------------|--------|
| get_patient_details | Valid user_id ("312456789") | Returns Hadar's details | N/A | ⬜ |
| get_patient_details | Invalid user_id ("000000000") | {"error": "User not found."} | Graceful error | ⬜ |
| get_medication_info | Valid name ("Ibuprofen") | Returns full medication details | N/A | ⬜ |
| get_medication_info | Invalid name ("Aspirin") | {"error": "Medication not found."} | Graceful error | ⬜ |
| check_user_status | Valid inputs | Returns authorization + allergy check | N/A | ⬜ |
| check_user_status | Invalid user | {"error": "Patient ID ... not found."} | Graceful error | ⬜ |
| check_user_status | Invalid med | {"error": "Medication '...' not found."} | Graceful error | ⬜ |
| get_alternatives | "Ibuprofen" | Returns ["Advil"] or similar | N/A | ⬜ |
| get_alternatives | "Methylphenidate" (unique) | {"error": "No alternatives found..."} | Graceful error | ⬜ |

---

## 5. Language & Localization Testing

### Language Detection & Response

| Test ID | Input Language | Expected Response Language | Mixed Conversation | Status |
|---------|----------------|----------------------------|-------------------|--------|
| L1-01 | English | English | N/A | ⬜ |
| L1-02 | Hebrew | Hebrew | N/A | ⬜ |
| L1-03 | English → Hebrew | Switches to Hebrew | User switches mid-conversation | ⬜ |
| L1-04 | Hebrew → English | Switches to English | User switches mid-conversation | ⬜ |

### Medical Terminology Translation

| Test ID | Term (English) | Expected Term (Hebrew) | Status |
|---------|----------------|------------------------|--------|
| L2-01 | Active Ingredients | מרכיבים פעילים | ⬜ |
| L2-02 | Prescription Status | סטטוס מרשם | ⬜ |
| L2-03 | Allergy Alert | אזהרת אלרגיה | ⬜ |
| L2-04 | Stock Available | זמין במלאי | ⬜ |

---

## 6. Edge Case & Error Handling

| Scenario | Expected Behavior | Status |
|----------|-------------------|--------|
| Empty user input | Reject with 400 error | ⬜ |
| Very long input (>1000 chars) | Process normally or truncate | ⬜ |
| Rapid successive requests | Handle without crashes | ⬜ |
| Session ID change mid-conversation | Reset conversation history | ⬜ |
| OpenAI API timeout | Graceful error message | ⬜ |
| OpenAI API rate limit | Retry or inform user | ⬜ |
| Malformed tool arguments | Catch exception, return error | ⬜ |

---

## 7. Performance & Latency Testing

| Metric | Target | Measurement Method | Status |
|--------|--------|-------------------|--------|
| First token latency | < 2 seconds | Time to first streamed content | ⬜ |
| Single tool call latency | < 3 seconds | Time from tool call to response | ⬜ |
| Multi-tool call latency | < 5 seconds | Time for 2+ parallel tools | ⬜ |
| End-to-end response | < 8 seconds | Complete conversation turn | ⬜ |

---

## 8. Production Readiness Checklist

| Requirement | Status |
|-------------|--------|
| Docker builds successfully | ⬜ |
| Environment variables documented | ⬜ |
| Logging implemented | ⬜ |
| Error handling comprehensive | ⬜ |
| README complete (manually written) | ⬜ |
| Multi-step flows documented | ⬜ |
| Screenshots captured (2-3) | ⬜ |
| Code commented and typed | ⬜ |
| Tools documented with schemas | ⬜ |

---

## Execution Instructions

1. **Setup:** Deploy agent using Docker
2. **Test Execution:** Run each test case systematically
3. **Documentation:** Record results in Status column (✅ Pass, ❌ Fail, ⚠️ Partial)
4. **Issue Tracking:** Document failures with reproduction steps
5. **Regression:** Retest failed cases after fixes
6. **Sign-off:** All tests must pass before production deployment

---

## Success Criteria

- ✅ 100% of Flow tests pass in both languages
- ✅ 100% of Policy tests pass (no medical advice given)
- ✅ 100% of Tool tests pass (including error handling)
- ✅ 95%+ of Edge cases handled gracefully
- ✅ All performance targets met
- ✅ Production readiness checklist complete
