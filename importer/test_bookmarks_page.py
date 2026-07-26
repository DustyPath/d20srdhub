import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from importer.bookmarks_page import render_bookmarks_page, write_bookmarks_page


class BookmarksPageTests(unittest.TestCase):
    def test_page_is_private_and_loads_bookmark_support(self):
        soup = BeautifulSoup(render_bookmarks_page(), "html.parser")
        scripts = [script["src"] for script in soup.find_all("script", src=True)]

        self.assertEqual(
            soup.find("meta", attrs={"name": "robots"})["content"],
            "noindex",
        )
        self.assertIn("/assets/bookmarks.js?v=1", scripts)
        self.assertIsNotNone(soup.find(attrs={"data-bookmarks-list": True}))

    def test_writer_creates_bookmarks_page(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = write_bookmarks_page(Path(temp_dir))

            self.assertEqual(destination.relative_to(temp_dir).as_posix(),
                             "bookmarks/index.html")
            self.assertIn(
                "Your bookmarks",
                destination.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
