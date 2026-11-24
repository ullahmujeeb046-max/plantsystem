"""Tests for interactive consultation and response building."""
import unittest

from expert_system import TomatoExpertSystem
from core.consultation import ConsultationEngine
from services.response_builder import build_consultation_response


class ConsultationTests(unittest.TestCase):
    def setUp(self):
        self.consultation = ConsultationEngine(TomatoExpertSystem())

    def test_start_extracts_evidence_and_selects_follow_up(self):
        turn = self.consultation.start("My tomato has dark brown spots.")
        self.assertIn("dark brown spots", turn["evidence"]["positive"])
        self.assertIsNotNone(turn["next_question"])
        self.assertFalse(turn["complete"])

    def test_yes_answer_adds_confirmed_fact(self):
        turn = self.consultation.start("My tomato has dark brown spots.")
        fact = turn["next_question"]["fact"]
        updated = self.consultation.answer(turn["session"], fact, "yes")
        self.assertIn(fact, updated["evidence"]["positive"])

    def test_no_answer_is_not_added_as_positive(self):
        turn = self.consultation.start("My tomato has dark brown spots.")
        fact = turn["next_question"]["fact"]
        updated = self.consultation.answer(turn["session"], fact, "no")
        self.assertIn(fact, updated["evidence"]["negative"])
        self.assertNotIn(fact, updated["evidence"]["positive"])

    def test_unsure_answer_remains_uncertain(self):
        turn = self.consultation.start("My tomato has dark brown spots.")
        fact = turn["next_question"]["fact"]
        updated = self.consultation.answer(turn["session"], fact, "unsure")
        self.assertIn(fact, updated["evidence"]["uncertain"])

    def test_invalid_answer_is_rejected(self):
        turn = self.consultation.start("My tomato has dark brown spots.")
        fact = turn["next_question"]["fact"]
        with self.assertRaises(ValueError):
            self.consultation.answer(turn["session"], fact, "sometimes")

    def test_empty_description_is_rejected(self):
        with self.assertRaises(ValueError):
            self.consultation.start("  ")

    def test_response_builder_returns_plain_language_summary(self):
        turn = self.consultation.start("My tomato has dark brown spots.")
        response = build_consultation_response(turn)
        self.assertTrue(response["summary"])
        self.assertTrue(response["disclaimer"])
        self.assertIsNotNone(response["follow_up_question"])


if __name__ == "__main__":
    unittest.main()
