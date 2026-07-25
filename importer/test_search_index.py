import tempfile
import unittest
from pathlib import Path

from importer.search_index import (
    MAX_SEARCH_TEXT,
    build_search_document,
    clean_title,
)


class SearchIndexTests(unittest.TestCase):
    def test_clean_title_removes_both_site_suffixes(self):
        self.assertEqual(
            clean_title("Fireball :: d20srd.org | d20 SRD Hub"),
            "Fireball",
        )

    def test_build_search_document_extracts_compact_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            page_file = Path(temp_dir) / "index.html"
            page_file.write_text(
                "<html><head><title>Fireball | d20 SRD Hub</title></head>"
                "<body><main><h1>Fireball</h1><h2>Evocation</h2>"
                "<p>A burst of flame deals fire damage.</p></main></body>"
                "</html>",
                encoding="utf-8",
            )

            document = build_search_document(page_file, "spells/fireball")

            self.assertEqual(document["title"], "Fireball")
            self.assertEqual(document["url"], "/spells/fireball/")
            self.assertEqual(document["section"], "Spells")
            self.assertEqual(document["headings"], "Evocation")
            self.assertIn("fire damage", document["text"])

    def test_search_text_is_capped(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            page_file = Path(temp_dir) / "index.html"
            page_file.write_text(
                f"<main><h1>Long Page</h1><p>{'word ' * 2000}</p></main>",
                encoding="utf-8",
            )

            document = build_search_document(page_file, "rules/long-page")

            self.assertLessEqual(len(document["text"]), MAX_SEARCH_TEXT)


if __name__ == "__main__":
    unittest.main()
