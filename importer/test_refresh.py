import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from importer.refresh import clean_title, extract_page_data, refresh_page


class RefreshTests(unittest.TestCase):
    def test_clean_title_removes_generated_and_source_suffixes(self):
        self.assertEqual(
            clean_title("Ranger :: d20srd.org | d20 SRD Hub"),
            "Ranger",
        )

    def test_extracts_article_from_legacy_generated_page(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            page_file = Path(temp_dir) / "index.html"
            page_file.write_text(
                "<html><head><title>Ranger :: d20srd.org</title></head>"
                "<body><main><h1>Ranger</h1><p>Article text.</p></main></body>"
                "</html>",
                encoding="utf-8",
            )

            title, article = extract_page_data(page_file)

            self.assertEqual(title, "Ranger")
            self.assertIn("<h1>Ranger</h1>", article)
            self.assertIn("<p>Article text.</p>", article)

    def test_refresh_page_uses_current_template(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            public_dir = project_root / "public"
            page_directory = public_dir / "classes" / "rogue"
            templates_dir = project_root / "templates"
            page_directory.mkdir(parents=True)
            templates_dir.mkdir()

            (page_directory / "index.html").write_text(
                "<title>Rogue :: d20srd.org</title>"
                "<main><h1>Rogue</h1><p>Article text.</p></main>",
                encoding="utf-8",
            )
            (templates_dir / "page.html").write_text(
                "<title>{{TITLE}}</title>"
                "<nav>{{BREADCRUMBS}}</nav>"
                "<main>{{ARTICLE}}</main>"
                "<nav>{{PAGE_NAVIGATION}}</nav>",
                encoding="utf-8",
            )

            with (
                patch("importer.refresh.PUBLIC_DIR", public_dir),
                patch("importer.writer.PUBLIC_DIR", public_dir),
                patch("importer.writer.PROJECT_ROOT", project_root),
            ):
                refreshed = refresh_page("classes/rogue")

            generated = (page_directory / "index.html").read_text(
                encoding="utf-8"
            )

            self.assertTrue(refreshed)
            self.assertIn('<a href="/classes/">Classes</a>', generated)
            self.assertIn("<h1>Rogue</h1>", generated)
            self.assertNotIn("{{", generated)


if __name__ == "__main__":
    unittest.main()
