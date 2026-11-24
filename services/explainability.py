"""Human-readable explanation reports for rule-based diagnosis results."""
from __future__ import annotations


def build_explanation_report(inference_result: dict, diagnosis_ids=None) -> dict:
    """Summarize fired rules, missing evidence, and proof status for conclusions."""
    trace = inference_result.get("trace", [])
    fired = [row for row in trace if row.get("matched")]
    pending = [row for row in trace if not row.get("matched")]
    selected = []
    if diagnosis_ids is None:
        diagnosis_ids = sorted({
            row.get("conclusion") for row in fired if row.get("conclusion")
        })
    for diagnosis_id in diagnosis_ids:
        support = [
            row for row in fired if row.get("conclusion") == diagnosis_id
        ]
        gaps = [
            {
                "rule_id": row.get("rule_id"),
                "missing_conditions": row.get("missing_conditions", [])
            }
            for row in pending if row.get("conclusion") == diagnosis_id
        ]
        selected.append({
            "diagnosis_id": diagnosis_id,
            "supported": bool(support),
            "supporting_rules": [
                {
                    "rule_id": row.get("rule_id"),
                    "matched_conditions": row.get("matched_conditions", []),
                    "explanation": row.get("explanation", ""),
                    "priority": row.get("priority", 0)
                }
                for row in support
            ],
            "missing_evidence": sorted({
                fact for gap in gaps for fact in gap["missing_conditions"]
            }),
            "incomplete_rules": gaps
        })
    return {
        "observed_facts": inference_result.get("facts", []),
        "evaluated_rule_count": inference_result.get("evaluated_rule_count", len(trace)),
        "fired_rule_count": len(fired),
        "unmatched_rule_count": len(pending),
        "diagnoses": selected,
        "trace": trace
    }
