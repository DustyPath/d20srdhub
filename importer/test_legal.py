import unittest
from pathlib import Path

from importer.config import PUBLIC_DIR


class LegalPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.legal_html = (PUBLIC_DIR / "legal" / "index.html").read_text(
            encoding="utf-8"
        )

    def test_complete_ogl_is_present(self):
        self.assertNotIn(
            "A complete copy of the Open Game License Version 1.0a will be inserted",
            self.legal_html,
        )

        for section in range(1, 16):
            self.assertIn(f"<p>{section}.", self.legal_html)

    def test_required_section_15_notices_are_present(self):
        self.assertIn(
            "Open Game License v 1.0a Copyright 2000, Wizards of the Coast, Inc.",
            self.legal_html,
        )
        self.assertIn(
            "System Reference Document Copyright 2000-2003, "
            "Wizards of the Coast, Inc.",
            self.legal_html,
        )
        self.assertIn(
            "d20 SRD Hub Copyright 2026, Thomas Padden.",
            self.legal_html,
        )

    def test_independence_notice_is_present(self):
        self.assertIn("is not affiliated", self.legal_html)
        self.assertIn("Wizards of the Coast", self.legal_html)
        self.assertIn("BoLS Interactive", self.legal_html)


if __name__ == "__main__":
    unittest.main()
