"""Streamlit application startup smoke test."""
from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


class StreamlitAppSmokeTests(unittest.TestCase):
    def test_app_starts_without_streamlit_exception(self):
        app_path = Path(__file__).parents[1] / "app.py"
        app = AppTest.from_file(str(app_path), default_timeout=30).run()
        self.assertEqual(len(app.exception), 0, [str(item) for item in app.exception])
        self.assertTrue(any("Tomato Plant Disease Expert System" in item.value for item in app.title))


if __name__ == "__main__":
    unittest.main()
