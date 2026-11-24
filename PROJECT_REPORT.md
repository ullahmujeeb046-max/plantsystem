# Project Report: Tomato Plant Disease Diagnosis Expert System

## 1. Introduction
The Tomato Plant Disease Diagnosis Expert System is a small rule-based artificial intelligence prototype. It accepts a user's description of visible tomato-plant symptoms, identifies symptom facts, applies IF-THEN rules using forward chaining, and presents possible diagnoses with general management and prevention suggestions.

## 2. Problem statement
Tomato growers may notice leaf spots, yellowing, wilting, mold, root abnormalities, or fruit lesions without knowing what may be causing them. The prototype demonstrates how expert knowledge can be represented as facts and rules to support an initial screening decision.

## 3. Scope
The knowledge base covers 18 tomato diseases and two physiological disorders. It is an educational demonstration and does not provide a laboratory-confirmed diagnosis.

## 4. Knowledge representation
- **Assertions:** 300 structured facts stored in `knowledge_base/knowledge_base.json`. Each assertion has an ID, subject, predicate, and value. For each of the 20 diagnosis profiles, 15 assertions describe the crop, common name, five symptoms, management, prevention, and other domain metadata.
- **Rules:** 100 IF-THEN rules. Each rule contains required symptom observations and a diagnosis conclusion. Five symptom-pattern rules are defined for each diagnosis profile.
- **Working memory:** Symptoms extracted from the user's description form the facts used during a consultation.

## 5. Inference engine
The prototype uses **forward chaining**:
1. Read the user's symptom description.
2. Normalize the text and map recognized phrases to canonical symptom facts.
3. Compare the observed facts with the antecedents of every rule.
4. Fire a rule when all its required symptoms are present.
5. Group fired rules by their diagnosis conclusion.
6. Rank the possible diagnoses and show the evidence and matched rule IDs.

The displayed evidence score is a heuristic rule-match score, not a medically or scientifically calibrated probability.

## 6. Natural-language interface
The interface accepts free-text English descriptions instead of requiring the user to select every symptom from a fixed form. It recognizes symptom phrases and a collection of common alternatives, such as "drooping" for wilting and "white powdery patches" for powdery mildew-like symptoms. Explicitly negated observations such as "no yellowing" are ignored when detected.

## 7. Example consultation
**User input:** `The lower leaves have dark brown spots with concentric rings and yellowing.`

**Expected reasoning:** The interface recognizes dark brown spots, concentric rings, and yellowing lower leaves. The early-blight pattern rules whose required symptom combinations are present fire. Early blight is therefore included among the possible diagnoses.

## 8. Limitations
- Symptoms of different tomato diseases can overlap.
- Phrase matching is a lightweight local NLP approach, not a full language model.
- The rule set and assertions are a curated teaching dataset, not an independently validated agricultural database.
- Treatment depends on local conditions, crop variety, and regulations. The system intentionally avoids pesticide dosage instructions.
- A local agricultural extension specialist or laboratory test should confirm serious or spreading cases.

## 9. Conclusion
The prototype demonstrates all main parts of a traditional expert system: a knowledge base, assertions, production rules, a forward-chaining inference engine, and a natural-language user interface. The project can be extended with a graphical interface, more crop profiles, and expert-validated rules.
