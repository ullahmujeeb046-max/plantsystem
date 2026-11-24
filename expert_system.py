import json
import re
from pathlib import Path
from collections import defaultdict

class TomatoExpertSystem:
    """Forward-chaining, rule-based expert system for tomato plant symptoms."""

    def __init__(self, knowledge_base_path=None):
        if knowledge_base_path is None:
            knowledge_base_path = Path(__file__).parent / "knowledge_base" / "knowledge_base.json"
        with open(knowledge_base_path, "r", encoding="utf-8") as f:
            self.kb = json.load(f)
        self.rules = self.kb["rules"]
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
        for pid, profile in self.profiles.items():
            for i in range(1, 6):
                symptom = profile[f"symptom_{i}"]
                terms[symptom] = symptom
        # Common language variants and abbreviations
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

    def extract_symptoms(self, user_text):
        text = self._normalize(user_text)
        found = set()
        # Longest terms first avoids short phrases obscuring more specific phrases.
        for phrase, canonical in sorted(self.symptom_terms.items(), key=lambda item: len(item[0]), reverse=True):
            phrase_norm = self._normalize(phrase)
            if phrase_norm and phrase_norm in text:
                # Ignore explicitly negated observations (e.g. "no yellowing").
                start = text.find(phrase_norm)
                prefix = text[max(0, start - 24):start].split()
                if prefix and prefix[-1] in {"no", "not", "without", "never", "isnt", "aren't"}:
                    continue
                if len(prefix) >= 2 and prefix[-2:] in (["does", "not"], ["do", "not"]):
                    continue
                found.add(canonical)
        return found

    def forward_chain(self, observed):
        """Fire every rule whose antecedent symptoms are all present."""
        fired = []
        conclusions = defaultdict(list)
        for rule in self.rules:
            required = set(rule["if_all_symptoms"])
            if required.issubset(observed):
                fired.append(rule)
                conclusions[rule["then_diagnosis"]].append(rule)
        return fired, conclusions

    def diagnose(self, user_text):
        observed = self.extract_symptoms(user_text)
        fired, conclusions = self.forward_chain(observed)
        ranked = []
        for pid, matched_rules in conclusions.items():
            profile = self.profiles[pid]
            # Score reflects matched rule weights, capped at 99; it is not a clinical probability.
            raw = sum(rule["weight"] for rule in matched_rules) / len(matched_rules)
            coverage = min(1.0, len(matched_rules) / 3.0)
            score = round(min(0.99, raw * (0.65 + 0.35 * coverage)) * 100)
            ranked.append({
                "id": pid,
                "name": profile["has_common_name"],
                "score": score,
                "matched_rules": [r["id"] for r in matched_rules],
                "explanation": matched_rules[0]["explanation"],
                "management": profile["management"],
                "prevention": profile["prevention"]
            })
        ranked.sort(key=lambda item: (item["score"], len(item["matched_rules"])), reverse=True)
        return {
            "recognized_symptoms": sorted(observed),
            "fired_rule_count": len(fired),
            "diagnoses": ranked
        }

    def validate_knowledge_base(self):
        return {
            "rule_count": len(self.rules),
            "assertion_count": len(self.assertions),
            "unique_rule_ids": len({r["id"] for r in self.rules}),
            "unique_assertion_ids": len({a["id"] for a in self.assertions}),
            "all_rules_have_antecedents": all(r.get("if_all_symptoms") for r in self.rules),
            "all_rules_have_conclusions": all(r.get("then_diagnosis") for r in self.rules)
        }
