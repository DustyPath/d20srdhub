import unittest
from pathlib import Path

from importer.config import PUBLIC_DIR
from importer.theme_migration import extract_article, page_title


class ThemeMigrationTests(unittest.TestCase):
    def test_extract_article_keeps_main_content_only(self):
        article = extract_article(
            "<html><head><style>old</style></head><body>"
            "<header>Old header</header>"
            "<main><h1>Combat</h1><p>Rules text.</p></main>"
            "<footer>Old footer</footer></body></html>"
        )

        self.assertIn("<h1>Combat</h1>", article)
        self.assertIn("<p>Rules text.</p>", article)
        self.assertNotIn("Old header", article)
        self.assertNotIn("<style>", article)

    def test_first_heading_is_promoted_when_h1_is_missing(self):
        article = extract_article("<main><h2>Legal</h2><p>Terms.</p></main>")

        self.assertIn("<h1>Legal</h1>", article)
        self.assertEqual(page_title(article, "Fallback"), "Legal")

    def test_every_public_html_page_uses_shared_stylesheet(self):
        missing = [
            page.relative_to(PUBLIC_DIR).as_posix()
            for page in PUBLIC_DIR.rglob("*.html")
            if "/assets/site.css" not in page.read_text(
                encoding="utf-8",
                errors="replace",
            )
        ]

        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
