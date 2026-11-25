"""Interactive evidence-gathering workflow for symptom consultations."""
from __future__ import annotations


class ConsultationEngine:
    """Collect symptom evidence, ask focused questions, and run diagnosis."""

    def __init__(self, expert_system):
        self.system = expert_system

    def start(self, description: str) -> dict:
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Please describe at least one plant symptom.")
        evidence = self.system.extract_evidence(description)
        session = {
            "positive_facts": set(evidence["confirmed_facts"]),
            "negative_facts": set(evidence["negative_facts"]),
            "uncertain_facts": set(evidence["uncertain_facts"]),
            "contradictions": set(evidence["contradictions"]),
            "asked_facts": set(),
            "original_description": description,
        }
        return self._build_turn(session)

    def answer(self, session: dict, fact: str, answer: str) -> dict:
        if not isinstance(session, dict) or not isinstance(fact, str):
            raise ValueError("A valid consultation session and symptom are required.")
        answer = str(answer).strip().lower()
        if answer not in {"yes", "no", "unsure"}:
            raise ValueError("Answer must be yes, no, or unsure.")
        session["asked_facts"].add(fact)
        session["positive_facts"].discard(fact)
        session["negative_facts"].discard(fact)
        session["uncertain_facts"].discard(fact)
        session["contradictions"].discard(fact)
        if answer == "yes":
            session["positive_facts"].add(fact)
        elif answer == "no":
            session["negative_facts"].add(fact)
        else:
            session["uncertain_facts"].add(fact)
        return self._build_turn(session)

    def _next_question(self, session: dict):
        known = set(session["positive_facts"]) | set(session["negative_facts"]) | set(session["uncertain_facts"])
        candidates = []
        for rule in self.system.rules:
            required = set(rule.get("if_all_symptoms", []))
            matched = required & session["positive_facts"]
            missing = required - known
            if matched and missing:
                candidates.append((len(matched), float(rule.get("priority", rule.get("weight", 0))), rule, missing))
        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        counts = {}
        priorities = {}
        for matched_count, priority, rule, missing in candidates:
            for fact in missing:
                if fact not in session["asked_facts"]:
                    counts[fact] = counts.get(fact, 0) + matched_count
                    priorities[fact] = max(priorities.get(fact, 0), priority)
        if not counts:
            return None
        selected = max(counts, key=lambda fact: (counts[fact], priorities[fact], fact))
        return selected

    def _build_turn(self, session: dict) -> dict:
        facts = sorted(session["positive_facts"])
        diagnosis = self.system.diagnose_from_facts(facts) if hasattr(self.system, "diagnose_from_facts") else None
        if diagnosis is None:
            # Reuse the public diagnosis method without changing its text parser.
            fired, conclusions = self.system.forward_chain(facts)
            diagnoses = []
            for pid, rules in conclusions.items():
                profile = self.system.profiles[pid]
                diagnoses.append({
                    "id": pid,
                    "name": profile["has_common_name"],
                    "matched_rules": [rule["id"] for rule in rules],
                    "explanation": rules[0].get("explanation", ""),
                    "management": profile.get("management", ""),
                    "prevention": profile.get("prevention", ""),
                })
            diagnosis = {"recognized_symptoms": facts, "fired_rule_count": len(fired), "diagnoses": diagnoses}
        question_fact = self._next_question(session)
        return {
            "session": session,
            "evidence": {
                "positive": sorted(session["positive_facts"]),
                "negative": sorted(session["negative_facts"]),
                "uncertain": sorted(session["uncertain_facts"]),
                "contradictions": sorted(session["contradictions"]),
                "unknown_input": not bool(
                    session["positive_facts"] or session["negative_facts"]
                    or session["uncertain_facts"] or session["contradictions"]
                ),
            },
            "diagnosis": diagnosis,
            "next_question": (
                {"fact": question_fact, "text": f"Have you noticed {question_fact} on the tomato plant?"}
                if question_fact else None
            ),
            "complete": question_fact is None,
        }
