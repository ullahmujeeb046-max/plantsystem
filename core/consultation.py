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

    @staticmethod
    def _question_for_fact(fact: str) -> str:
        """Turn a knowledge-base symptom fact into a clear, natural question."""
        questions = {
            "concentric rings": "Do the spots have circular rings, like a target?",
            "yellowing lower leaves": "Are the older, lower leaves turning yellow?",
            "leaf drop": "Are leaves falling off the plant?",
            "stem lesions": "Do you see damaged or discolored patches on the stems?",
            "water-soaked leaf lesions": "Do the leaves have wet-looking, water-soaked patches?",
            "rapidly spreading brown patches": "Are the brown patches spreading quickly?",
            "white fuzzy growth underside": "Is there white fuzzy growth on the underside of the leaves?",
            "brown stem lesions": "Do you see brown lesions on the stems?",
            "firm brown fruit lesions": "Are there firm brown spots or lesions on the tomatoes?",
            "many small circular spots": "Do the leaves have many small, round spots?",
            "gray centers in leaf spots": "Do the spots have gray centers?",
            "dark borders around spots": "Do the leaf spots have dark-colored edges?",
            "small dark leaf spots": "Are there small, dark spots on the leaves?",
            "yellow halos around spots": "Is there a yellow ring around the leaf spots?",
            "raised scabby fruit spots": "Do the tomatoes have raised, rough or scabby spots?",
            "water-soaked lesions": "Do you see wet-looking patches on the plant?",
            "leaf yellowing": "Are the leaves turning yellow?",
            "sudden plant wilting": "Did the plant start wilting suddenly?",
            "leaves remain green while wilting": "Do the leaves stay green even while the plant is wilting?",
            "vascular tissue brown": "When you look inside a cut stem, is the inner tissue brown?",
            "one-sided wilting": "Is only one side of the plant wilting?",
            "one-sided leaf wilting": "Are leaves wilting mainly on one side of the plant?",
            "plant does not recover overnight": "Does the plant remain wilted the next morning?",
            "yellowing starts on lower leaves": "Does yellowing begin with the lower leaves?",
            "one-sided yellowing": "Is the yellowing mainly on one side of the plant?",
            "wilting during warm hours": "Does the plant wilt during the warmest part of the day?",
            "brown vascular tissue": "Does the inner tissue of a cut stem look brown?",
            "progressive plant decline": "Is the plant gradually becoming weaker or less healthy?",
            "V-shaped yellow lesions": "Do the leaves have yellow, V-shaped patches?",
            "lower leaf yellowing": "Are the lower leaves turning yellow?",
            "wilting in warm weather": "Does the plant wilt when the weather is warm?",
            "slow stunted growth": "Is the plant growing unusually slowly or remaining small?",
            "white powdery leaf coating": "Do the leaves have a white, powder-like coating?",
            "white patches on upper leaf surface": "Are there white patches on the upper surface of the leaves?",
            "leaf curling": "Are the leaves curling or bending?",
            "premature leaf drop": "Are leaves falling before they normally would?",
            "gray fuzzy mold": "Do you see gray, fuzzy mold on the plant?",
            "soft water-soaked lesions": "Are there soft, wet-looking lesions on the plant?",
            "brown stem cankers": "Do the stems have brown, sunken or damaged areas?",
            "flowers turn brown": "Are the flowers turning brown?",
            "fruit rot near stem": "Is the fruit rotting near the stem?",
            "root galls": "Can you see lumps or swellings on the roots?",
            "knotted swollen roots": "Do the roots look knotted or swollen?",
            "wilting despite moist soil": "Does the plant wilt even when the soil is moist?",
            "poor nutrient uptake": "Does the plant show signs of poor growth despite receiving nutrients?",
            "dark sunken patch at blossom end": "Is there a dark, sunken patch on the bottom of the tomato, opposite the stem?",
            "leathery fruit bottom": "Does the bottom of the tomato feel tough or leathery?",
            "fruit rot opposite stem": "Is the tomato rotting at the end opposite the stem?",
            "irregular soil moisture": "Does the soil alternate between very dry and very wet?",
            "rapid fruit growth": "Have the tomatoes been growing very rapidly?",
            "pale white patch on exposed fruit": "Do exposed tomatoes have pale or whitish patches?",
            "papery fruit skin": "Does the affected fruit skin look dry and papery?",
            "sunken dry fruit lesion": "Is there a dry, sunken area on the fruit?",
            "sudden fruit exposure to sun": "Was the fruit recently exposed to direct sunlight after being shaded?",
            "leaf loss exposing fruit": "Have leaves fallen off and left the fruit exposed to sunlight?",
            "mosaic light and dark green leaves": "Do the leaves show a light-and-dark green mosaic pattern?",
            "small leaves": "Are the new leaves unusually small?",
            "stunted plant growth": "Is the plant's growth stunted or much slower than usual?",
            "poor fruit set": "Is the plant producing very few fruits?",
            "bronze young leaves": "Are the youngest leaves turning bronze or brownish?",
            "dark rings on fruit": "Do the tomatoes have dark rings on their surface?",
            "necrotic leaf spots": "Do the leaves have dead, dark or dried-out spots?",
            "wilting shoot tips": "Are the growing tips or new shoots wilting?",
            "small gray leaf lesions": "Do you see small gray spots or lesions on the leaves?",
            "rectangular spots between veins": "Are there rectangular spots between the leaf veins?",
            "yellowing leaves": "Are the leaves turning yellow?",
            "leaf blight": "Are parts of the leaves drying out or dying?",
            "lower canopy leaf drop": "Are leaves falling from the lower part of the plant?",
            "white fungal growth at soil line": "Is there white fungal growth around the stem where it meets the soil?",
            "small tan round fungal bodies": "Can you see small, round, tan-colored fungal bodies near the stem?",
            "stem rot near soil": "Is the stem rotting near the soil surface?",
            "lower stem girdling": "Does the lower stem have a damaged or rotting band around it?",
            "brown leaf margins": "Are the edges of the leaves turning brown?",
            "stem cankers": "Do you see canker-like damaged areas on the stems?",
            "vascular discoloration": "Does the inside of the stem show unusual brown discoloration?",
            "bird's-eye fruit spots": "Do the tomatoes have small spots with a pale center and dark edge?",
        }
        if fact in questions:
            return questions[fact]
        readable = fact.rstrip(".")
        return f"Have you noticed {readable} on your tomato plant?"

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
                {"fact": question_fact, "text": self._question_for_fact(question_fact)}
                if question_fact else None
            ),
            "complete": question_fact is None,
        }
