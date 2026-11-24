"""Explainable forward- and backward-chaining for the tomato knowledge base.

The engine is domain-agnostic: it consumes rules with if_all_symptoms and
then_diagnosis fields and never invents facts or conclusions.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


class InferenceEngine:
    """Evaluate the project's IF-THEN rules against explicit evidence."""

    def __init__(self, rules: list[dict[str, Any]]) -> None:
        self.rules = list(rules)
        self._rules_by_conclusion: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for rule in self.rules:
            conclusion = rule.get("then_diagnosis")
            if isinstance(conclusion, str) and conclusion:
                self._rules_by_conclusion[conclusion].append(rule)

    @staticmethod
    def _priority(rule: dict[str, Any]) -> float:
        """Use explicit priority when introduced; retain legacy weight otherwise."""
        value = rule.get("priority", rule.get("weight", 0))
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def forward_chain(self, facts: Iterable[str]) -> dict[str, Any]:
        """Fire every rule whose complete antecedent is present.

        If several rules support the same conclusion, the highest-priority
        matched rule is selected as the primary explanation; all matched rules
        remain visible in the trace.
        """
        known = set(facts)
        fired: list[dict[str, Any]] = []
        conclusions: dict[str, list[dict[str, Any]]] = defaultdict(list)
        evaluated: list[dict[str, Any]] = []

        for rule in self.rules:
            conditions = set(rule.get("if_all_symptoms", []))
            missing = sorted(conditions - known)
            matched = not missing and bool(conditions)
            evaluated.append({
                "rule_id": rule.get("id", "UNKNOWN"),
                "conclusion": rule.get("then_diagnosis"),
                "matched": matched,
                "matched_conditions": sorted(conditions & known),
                "missing_conditions": missing,
            })
            if matched:
                fired.append(rule)
                conclusions[rule["then_diagnosis"]].append(rule)

        selected = {}
        for conclusion, matched_rules in conclusions.items():
            selected[conclusion] = max(
                matched_rules,
                key=lambda rule: (self._priority(rule), rule.get("id", "")),
            )

        return {
            "facts": sorted(known),
            "fired_rules": fired,
            "conclusions": dict(conclusions),
            "selected_rules": selected,
            "trace": evaluated,
        }

    def backward_chain(self, goal: str, facts: Iterable[str]) -> dict[str, Any]:
        """Try to prove a requested diagnosis from observed symptom facts.

        This is goal-directed: only rules that conclude the requested goal
        are examined. Unobserved antecedents are returned as missing evidence,
        not assumed to be true.
        """
        known = set(facts)
        candidate_rules = self._rules_by_conclusion.get(goal, [])
        proofs = []
        all_missing: set[str] = set()

        for rule in candidate_rules:
            required = set(rule.get("if_all_symptoms", []))
            matched = sorted(required & known)
            missing = sorted(required - known)
            all_missing.update(missing)
            proofs.append({
                "rule_id": rule.get("id", "UNKNOWN"),
                "explanation": rule.get("explanation", ""),
                "required_conditions": sorted(required),
                "matched_conditions": matched,
                "missing_conditions": missing,
                "proven": bool(required) and not missing,
                "priority": self._priority(rule),
            })

        proven = [item for item in proofs if item["proven"]]
        proven.sort(key=lambda item: (item["priority"], item["rule_id"]), reverse=True)
        return {
            "goal": goal,
            "proved": bool(proven),
            "known_facts": sorted(known),
            "candidate_rule_count": len(candidate_rules),
            "proofs": proofs,
            "supporting_rule_ids": [item["rule_id"] for item in proven],
            "missing_evidence": sorted(all_missing) if not proven else [],
            "message": (
                "The goal is supported by the observed facts."
                if proven else
                "The available facts do not prove this goal. Missing evidence is listed."
                if candidate_rules else
                "No rule in the knowledge base concludes this goal."
            ),
        }
