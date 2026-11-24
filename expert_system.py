import json
import re
from pathlib import Path
from collections import defaultdict
from core.inference import InferenceEngine
from nlp.evidence_extractor import extract_evidence


class TomatoExpertSystem:
    """Rule-based expert system for tomato symptoms and disease questions."""

    def __init__(self, knowledge_base_path=None):
        if knowledge_base_path is None:
            knowledge_base_path = Path(__file__).parent / "knowledge_base" / "knowledge_base.json"
        with open(knowledge_base_path, "r", encoding="utf-8") as f:
            self.kb = json.load(f)
        self.rules = self.kb["rules"]
        self.inference_engine = InferenceEngine(self.rules)
        self.assertions = self.kb["assertions"]
        self.profiles = self._build_profiles()
        self.symptom_terms = self._build_symptom_terms()

    def _build_profiles(self):
        profiles = {}
        for fact in self.assertions:
            profiles.setdefault(fact["subject"], {})[fact["predicate"]] = fact["value"]
        return profiles

    def _build_symptom_terms(self):
        terms = {}
        for profile in self.profiles.values():
            for i in range(1, 6):
                symptom = profile[f"symptom_{i}"]
                terms[symptom] = symptom

        aliases = {
            "yellow leaves": "yellowing lower leaves",
            "leaves turning yellow": "yellowing lower leaves",
            "brown rings": "concentric rings",
            "ring spots": "concentric rings",
            "white mold": "white fuzzy growth underside",
            "white fungus": "white powdery leaf coating",
            "powder on leaves": "white powdery leaf coating",
            "wilting": "sudden plant wilting",
            "drooping": "sudden plant wilting",
            "curled leaves": "upward leaf curling",
            "curly leaves": "upward leaf curling",
            "knots on roots": "root galls",
            "swollen roots": "knotted swollen roots",
            "fruit bottom rot": "dark sunken patch at blossom end",
            "black bottom on tomato": "dark sunken patch at blossom end",
            "mosaic pattern": "mosaic light and dark green leaves",
            "green mosaic": "mosaic light and dark green leaves",
            "brown spots": "dark brown spots",
            "spots with rings": "concentric rings",
            "white patches": "white powdery leaf coating",
            "white powdery patches": "white powdery leaf coating",
            "powdery white growth": "white powdery leaf coating",
            "small circular brown spots": "many small circular spots",
            "gray centers": "gray centers in leaf spots",
            "yellow halos": "yellow halos around spots",
            "water soaked spots": "water-soaked lesions",
            "water soaked patches": "water-soaked leaf lesions",
            "sunken spots on fruit": "sunken circular fruit lesions",
            "sunken fruit spots": "sunken circular fruit lesions",
            "white growth at soil line": "white fungal growth at soil line",
            "tiny tan balls": "small tan round fungal bodies",
            "upward curled leaves": "upward leaf curling",
            "leaves curl upward": "upward leaf curling",
            "leaves curl": "leaf curling",
            "roots have galls": "root galls",
            "roots are knotted": "knotted swollen roots",
            "fruit bottom is black": "dark sunken patch at blossom end",
            "black patch on bottom of fruit": "dark sunken patch at blossom end",
            "gray mold": "gray fuzzy mold",
            "grey mold": "gray fuzzy mold",
        }
        terms.update(aliases)
        return terms

    @staticmethod
    def _normalize(text):
        text = text.lower().replace("-", " ")
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def get_disease_information(self, user_text):
        """Answer questions about conditions stored in the knowledge base."""
        text = self._normalize(user_text)
        question_words = (
            "what is", "tell me", "explain", "information", "details",
            "symptoms", "treatment", "treat", "management", "prevent",
            "prevention", "about", "cause", "causes"
        )
        is_question = any(word in text for word in question_words)
        matched_profile = None

        for pid, profile in self.profiles.items():
            common_name = profile.get("has_common_name", "")
            name = self._normalize(common_name)
            profile_id = self._normalize(pid.replace("_", " "))
            if (name and name in text) or (profile_id and profile_id in text):
                matched_profile = (pid, profile)
                break

        # A disease name by itself is also treated as a request for information.
        if matched_profile is None and not is_question:
            return None

        if matched_profile is None:
            names = sorted(
                profile.get("has_common_name", pid.replace("_", " ").title())
                for pid, profile in self.profiles.items()
            )
            return {
                "found": False,
                "requested": user_text,
                "available_diseases": names
            }

        pid, profile = matched_profile
        symptoms = [
            profile[f"symptom_{i}"]
            for i in range(1, 6)
            if profile.get(f"symptom_{i}")
        ]
        return {
            "found": True,
            "id": pid,
            "name": profile.get("has_common_name", pid.replace("_", " ").title()),
            "symptoms": symptoms,
            "management": profile.get(
                "management",
                "No management advice is available in the knowledge base."
            ),
            "prevention": profile.get(
                "prevention",
                "No prevention advice is available in the knowledge base."
            )
        }

    def extract_evidence(self, user_text):
        """Return positive, negative, uncertain, and contradictory symptom mentions."""
        return extract_evidence(user_text, self.symptom_terms)

    def extract_symptoms(self, user_text):
        """Return only confirmed positive symptoms for backward compatibility."""
        return set(self.extract_evidence(user_text)["confirmed_facts"])

    def forward_chain(self, observed):
        """Run the modular inference engine and preserve the legacy return shape."""
        result = self.inference_engine.forward_chain(observed)
        return result["fired_rules"], result["conclusions"]

    def backward_chain(self, goal, observed):
        """Attempt to prove a diagnosis from observed symptoms and show gaps."""
        return self.inference_engine.backward_chain(goal, observed)

    def diagnose(self, user_text):
        observed = self.extract_symptoms(user_text)
        fired, conclusions = self.forward_chain(observed)
        ranked = []
        for pid, matched_rules in conclusions.items():
            profile = self.profiles[pid]
            # This is a heuristic evidence score, not a clinical probability.
            raw = sum(rule["weight"] for rule in matched_rules) / len(matched_rules)
            coverage = min(1.0, len(matched_rules) / 3.0)
            score = round(min(0.99, raw * (0.65 + 0.35 * coverage)) * 100)
            ranked.append({
                "id": pid,
                "name": profile["has_common_name"],
                "score": score,
                "matched_rules": [rule["id"] for rule in matched_rules],
                "explanation": matched_rules[0]["explanation"],
                "management": profile["management"],
                "prevention": profile["prevention"]
            })
        ranked.sort(
            key=lambda item: (item["score"], len(item["matched_rules"])),
            reverse=True
        )
        return {
            "recognized_symptoms": sorted(observed),
            "fired_rule_count": len(fired),
            "diagnoses": ranked
        }

    def validate_knowledge_base(self):
        return {
            "rule_count": len(self.rules),
            "assertion_count": len(self.assertions),
            "unique_rule_ids": len({rule["id"] for rule in self.rules}),
            "unique_assertion_ids": len({fact["id"] for fact in self.assertions}),
            "all_rules_have_antecedents": all(
                rule.get("if_all_symptoms") for rule in self.rules
            ),
            "all_rules_have_conclusions": all(
                rule.get("then_diagnosis") for rule in self.rules
            )
        }
