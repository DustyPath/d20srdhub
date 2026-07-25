import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from importer.seo import (
    page_route,
    set_meta,
    sitemap_routes,
    update_page_file,
    write_robots,
    write_sitemap,
)


class SeoTests(unittest.TestCase):
    def test_page_route_handles_home_and_nested_pages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)

            self.assertEqual(
                page_route(public_dir / "index.html", public_dir),
                "/",
            )
            self.assertEqual(
                page_route(
                    public_dir / "spells" / "fireball" / "index.html",
                    public_dir,
                ),
                "/spells/fireball/",
            )

    def test_metadata_is_added_and_updated_idempotently(self):
        soup = BeautifulSoup(
            "<html><head><title>Fireball</title></head>"
            "<body><main><p>A fiery spell.</p></main></body></html>",
            "html.parser",
        )

        set_meta(soup, "/spells/fireball/")
        set_meta(soup, "/spells/fireball/")

        self.assertEqual(
            len(soup.head.find_all("meta", attrs={"name": "description"})),
            1,
        )
        self.assertEqual(
            soup.head.find("link", attrs={"rel": "canonical"})["href"],
            "https://d20srdhub.com/spells/fireball/",
        )

    def test_description_skips_unhelpfully_short_paragraphs(self):
        soup = BeautifulSoup(
            "<html><head></head><body><main><p>Any.</p><p>"
            "Rogues rely on skill, stealth, and precise attacks to overcome "
            "obstacles and opponents during an adventure."
            "</p></main></body></html>",
            "html.parser",
        )

        description, _ = set_meta(soup, "/classes/rogue/")

        self.assertTrue(description.startswith("Rogues rely on skill"))

    def test_file_update_preserves_existing_html_formatting(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)
            page_file = public_dir / "spells" / "fireball" / "index.html"
            page_file.parent.mkdir(parents=True)
            page_file.write_text(
                "<!DOCTYPE html>\n"
                "<html><head><title>Fireball</title></head>\n"
                "<body>\n  <main><p>A fiery spell.</p></main>\n</body></html>",
                encoding="utf-8",
            )

            update_page_file(page_file, public_dir)
            first_update = page_file.read_text(encoding="utf-8")
            update_page_file(page_file, public_dir)
            second_update = page_file.read_text(encoding="utf-8")

            self.assertIn("\n  <main>", first_update)
            self.assertIn('name="description"', first_update)
            self.assertIn('rel="canonical"', first_update)
            self.assertEqual(first_update, second_update)

    def test_sitemap_excludes_noindex_pages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)
            included = public_dir / "rules" / "index.html"
            excluded = public_dir / "private" / "index.html"
            included.parent.mkdir(parents=True)
            excluded.parent.mkdir(parents=True)
            included.write_text("<html><head></head></html>", encoding="utf-8")
            excluded.write_text(
                '<html><head><meta name="robots" content="noindex"></head></html>',
                encoding="utf-8",
            )

            self.assertEqual(sitemap_routes(public_dir), ["/rules/"])

    def test_writes_valid_discovery_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)
            home = public_dir / "index.html"
            home.write_text("<html><head></head></html>", encoding="utf-8")

            count = write_sitemap(public_dir)
            write_robots(public_dir)

            self.assertEqual(count, 1)
            self.assertIn(
                "https://d20srdhub.com/",
                (public_dir / "sitemap.xml").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "Sitemap: https://d20srdhub.com/sitemap.xml",
                (public_dir / "robots.txt").read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
