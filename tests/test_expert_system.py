import unittest
from expert_system import TomatoExpertSystem


class ExpertSystemTests(unittest.TestCase):
    def setUp(self):
        self.system = TomatoExpertSystem()

    def test_required_counts(self):
        counts = self.system.validate_knowledge_base()
        self.assertEqual(counts["rule_count"], 100)
        self.assertEqual(counts["assertion_count"], 300)
        self.assertEqual(counts["unique_rule_ids"], 100)
        self.assertEqual(counts["unique_assertion_ids"], 300)

    def test_early_blight_pattern(self):
        result = self.system.diagnose(
            "dark brown spots with concentric rings and yellowing lower leaves"
        )
        names = [d["name"] for d in result["diagnoses"]]
        self.assertIn("Early blight", names)

    def test_powdery_mildew_pattern(self):
        result = self.system.diagnose(
            "white powdery leaf coating and leaf yellowing with leaf curling"
        )
        names = [d["name"] for d in result["diagnoses"]]
        self.assertIn("Powdery mildew", names)

    def test_disease_information_by_name(self):
        result = self.system.get_disease_information("What is Early blight?")
        self.assertTrue(result["found"])
        self.assertEqual(result["name"], "Early blight")
        self.assertTrue(result["symptoms"])
        self.assertTrue(result["management"])
        self.assertTrue(result["prevention"])

    def test_disease_information_by_prevention_question(self):
        result = self.system.get_disease_information(
            "How can I prevent Powdery mildew?"
        )
        self.assertTrue(result["found"])
        self.assertEqual(result["name"], "Powdery mildew")
        self.assertTrue(result["prevention"])

    def test_unknown_disease_question(self):
        result = self.system.get_disease_information("What is potato blight?")
        self.assertFalse(result["found"])
        self.assertTrue(result["available_diseases"])


if __name__ == "__main__":
    unittest.main()
