import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from importer.not_found import render_not_found, write_not_found


class NotFoundTests(unittest.TestCase):
    def test_page_is_noindex_and_uses_shared_search_assets(self):
        soup = BeautifulSoup(render_not_found(), "html.parser")

        self.assertEqual(
            soup.find("meta", attrs={"name": "robots"})["content"],
            "noindex",
        )
        self.assertEqual(
            soup.find("link", attrs={"rel": "stylesheet"})["href"],
            "/assets/site.css",
        )
        scripts = [script["src"] for script in soup.find_all("script", src=True)]
        self.assertIn("/assets/search.js?v=2", scripts)
        self.assertIn("/assets/theme.js?v=1", scripts)
        self.assertIsNotNone(soup.find(attrs={"data-search-input": True}))
        self.assertIsNotNone(soup.find(attrs={"data-theme-toggle": True}))

    def test_writer_creates_404_page(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = write_not_found(Path(temp_dir))

            self.assertEqual(destination.name, "404.html")
            self.assertIn(
                "That rule slipped away.",
                destination.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
