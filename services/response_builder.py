"""Plain-language summaries for consultation results."""


def build_consultation_response(turn: dict) -> dict:
    evidence = turn.get("evidence", {})
    diagnoses = turn.get("diagnosis", {}).get("diagnoses", [])
    if evidence.get("contradictions"):
        summary = "Some symptom details conflict. Please check those observations before relying on a result."
    elif not evidence.get("positive"):
        summary = "I do not have enough confirmed symptoms yet. Please provide more details."
    elif diagnoses:
        names = ", ".join(item["name"] for item in diagnoses[:3])
        summary = f"The observed symptoms match these possible conditions: {names}. This is a screening result, not a confirmed diagnosis."
    else:
        summary = "The confirmed symptoms do not yet match a complete diagnosis rule. More observations may help."
    return {
        "summary": summary,
        "positive_evidence": evidence.get("positive", []),
        "negative_evidence": evidence.get("negative", []),
        "uncertain_evidence": evidence.get("uncertain", []),
        "possible_diagnoses": [item["name"] for item in diagnoses],
        "follow_up_question": (turn.get("next_question") or {}).get("text"),
        "disclaimer": "Educational screening only. Consult a local agricultural specialist for serious or spreading symptoms.",
    }
