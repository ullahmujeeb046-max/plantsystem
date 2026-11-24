"""Explainable forward- and backward-chaining for the tomato knowledge base."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


class InferenceEngine:
    """Evaluate IF-THEN rules against explicit, confirmed symptom facts."""

    def __init__(self, rules: list[dict[str, Any]]) -> None:
        self.rules = list(rules)
        self._rules_by_conclusion: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for rule in self.rules:
            conclusion = rule.get("then_diagnosis")
            if isinstance(conclusion, str) and conclusion:
                self._rules_by_conclusion[conclusion].append(rule)

    @staticmethod
    def _priority(rule: dict[str, Any]) -> float:
        """Use explicit priority; legacy weight remains a compatible fallback."""
        value = rule.get("priority", rule.get("weight", 0))
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _normalize_facts(facts: Iterable[str]) -> set[str]:
        if isinstance(facts, (str, bytes)):
            raise TypeError("Facts must be an iterable of fact strings, not one text value.")
        try:
            values = set(facts)
        except TypeError as exc:
            raise TypeError("Facts must be an iterable of strings.") from exc
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError("Every observed fact must be a non-empty string.")
        return {value.strip() for value in values}

    def forward_chain(self, facts: Iterable[str]) -> dict[str, Any]:
        """Fire every rule whose complete antecedent is present and trace evaluation."""
        known = self._normalize_facts(facts)
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
                "category": rule.get("category", "uncategorized"),
                "priority": self._priority(rule),
                "explanation": rule.get("explanation", ""),
                "matched": matched,
                "matched_conditions": sorted(conditions & known),
                "missing_conditions": missing,
            })
            if matched:
                fired.append(rule)
                conclusions[rule["then_diagnosis"]].append(rule)

        selected = {
            conclusion: max(
                matched_rules,
                key=lambda rule: (self._priority(rule), rule.get("id", "")),
            )
            for conclusion, matched_rules in conclusions.items()
        }
        return {
            "facts": sorted(known),
            "fired_rules": fired,
            "conclusions": dict(conclusions),
            "selected_rules": selected,
            "trace": evaluated,
            "evaluated_rule_count": len(evaluated),
        }

    def backward_chain(self, goal: str, facts: Iterable[str]) -> dict[str, Any]:
        """Try to prove a requested diagnosis without assuming missing evidence."""
        known = self._normalize_facts(facts)
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("The backward-chaining goal must be a non-empty string.")
        goal = goal.strip()
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
                "category": rule.get("category", "uncategorized"),
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
            "evaluated_rule_count": len(proofs),
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
