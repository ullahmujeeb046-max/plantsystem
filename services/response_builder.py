"""Plain-language summaries for consultation results."""


def build_consultation_response(turn: dict) -> dict:
    evidence = turn.get("evidence", {})
    diagnoses = turn.get("diagnosis", {}).get("diagnoses", [])
    if evidence.get("contradictions"):
        summary = (
            "Some symptom details conflict. Please check those observations "
            "before relying on a result."
        )
    elif evidence.get("unknown_input") or not (
        evidence.get("positive") or evidence.get("negative")
        or evidence.get("uncertain")
    ):
        summary = (
            "I could not recognize a tomato symptom in your description. "
            "This detail is not currently covered by my symptom knowledge base. "
            "Please try a known symptom, such as 'dark brown spots on leaves' "
            "or 'yellowing lower leaves'."
        )
    elif diagnoses:
        names = ", ".join(item["name"] for item in diagnoses[:3])
        summary = (
            f"The observed symptoms match these possible conditions: {names}. "
            "This is a screening result, not a confirmed diagnosis."
        )
    else:
        summary = (
            "I recognized your symptom(s), but no complete diagnosis rule in "
            "my current knowledge base matches this combination. I cannot "
            "identify a disease from the available rules yet."
        )
    return {
        "summary": summary,
        "positive_evidence": evidence.get("positive", []),
        "negative_evidence": evidence.get("negative", []),
        "uncertain_evidence": evidence.get("uncertain", []),
        "possible_diagnoses": [item["name"] for item in diagnoses],
        "follow_up_question": (turn.get("next_question") or {}).get("text"),
        "disclaimer": (
            "Educational screening only. Consult a local agricultural "
            "specialist for serious or spreading symptoms."
        ),
    }
