"""Tests for lightweight NLP normalization and evidence extraction."""
import unittest

from nlp.normalizer import normalize_text, tokenize
from nlp.evidence_extractor import extract_evidence
from expert_system import TomatoExpertSystem
from services.response_builder import build_consultation_response


class NLPTests(unittest.TestCase):
    def setUp(self):
        self.phrases = {
            "yellow leaves": "yellowing lower leaves",
            "yellowing lower leaves": "yellowing lower leaves",
            "dark brown spots": "dark brown spots",
            "concentric rings": "concentric rings",
            "white powdery leaf coating": "white powdery leaf coating",
        }

    def test_normalization_and_tokenization(self):
        self.assertEqual(normalize_text("  DARK-brown spots! "), "dark brown spots")
        self.assertEqual(tokenize("Yellow leaves"), ["yellow", "leaves"])

    def test_positive_symptoms_are_extracted(self):
        result = extract_evidence("The plant has dark brown spots and concentric rings.", self.phrases)
        self.assertEqual(set(result["confirmed_facts"]), {"dark brown spots", "concentric rings"})

    def test_negated_symptom_is_not_confirmed(self):
        result = extract_evidence("There are no yellow leaves.", self.phrases)
        self.assertEqual(result["negative_facts"], ["yellowing lower leaves"])
        self.assertEqual(result["confirmed_facts"], [])

    def test_uncertain_symptom_is_not_confirmed(self):
        result = extract_evidence("Maybe the plant has dark brown spots.", self.phrases)
        self.assertEqual(result["uncertain_facts"], ["dark brown spots"])
        self.assertEqual(result["confirmed_facts"], [])

    def test_positive_and_negative_mentions_are_flagged_as_contradiction(self):
        result = extract_evidence("Yellow leaves are present, but no yellow leaves.", self.phrases)
        self.assertEqual(result["contradictions"], ["yellowing lower leaves"])
        self.assertEqual(result["confirmed_facts"], [])

    def test_unknown_text_does_not_create_facts(self):
        result = extract_evidence("My tomato plant looks strange.", self.phrases)
        self.assertTrue(result["unknown_input"])
        self.assertEqual(result["confirmed_facts"], [])

    def test_expert_system_uses_only_confirmed_positive_evidence(self):
        system = TomatoExpertSystem()
        evidence = system.extract_evidence("No dark brown spots, but concentric rings.")
        self.assertIn("dark brown spots", evidence["negative_facts"])
        self.assertNotIn("dark brown spots", system.extract_symptoms("No dark brown spots, but concentric rings."))

    def test_natural_sentence_variants_are_recognized(self):
        system = TomatoExpertSystem()
        evidence = system.extract_evidence(
            "My tomato plant has black spots on its leaves, yellow circles around the spots, and the bottom leaves are falling off."
        )
        self.assertIn("dark brown spots", evidence["confirmed_facts"])
        self.assertIn("yellow halos around spots", evidence["confirmed_facts"])
        self.assertIn("leaf drop", evidence["confirmed_facts"])

    def test_plural_symptom_phrase_is_recognized(self):
        result = extract_evidence("The leaves have concentric rings.", self.phrases)
        self.assertIn("concentric rings", result["confirmed_facts"])

    def test_unknown_question_returns_human_friendly_message(self):
        system = TomatoExpertSystem()
        result = system.get_disease_information("How can I fix a tomato plant with an unknown problem?")
        self.assertIsNotNone(result)
        self.assertFalse(result["found"])
        self.assertIn("not available", result["message"])

    def test_unknown_short_query_also_returns_knowledge_base_message(self):
        system = TomatoExpertSystem()
        result = system.get_disease_information("brown edges")
        self.assertIsNotNone(result)
        self.assertFalse(result["found"])
        self.assertIn("not available", result["message"])

    def test_unrecognized_consultation_explains_what_is_missing(self):
        turn = {
            "evidence": {
                "positive": [], "negative": [], "uncertain": [],
                "contradictions": [], "unknown_input": True
            },
            "diagnosis": {"diagnoses": []},
            "next_question": None
        }
        result = build_consultation_response(turn)
        self.assertIn("could not recognize", result["summary"])
        self.assertIn("knowledge base", result["summary"])


if __name__ == "__main__":
    unittest.main()
