import tempfile
import unittest
from pathlib import Path

from importer.performance import (
    SEARCH_SCRIPT,
    SHARED_STYLESHEET,
    audit_shared_styles,
    extract_template_css,
    migrate_generated_pages,
    migrate_html,
)


class PerformanceTests(unittest.TestCase):
    def test_migrate_html_extracts_only_shared_template_style(self):
        html = (
            "<html><head><title>Rogue</title>"
            '<link rel="canonical" href="https://d20srdhub.com/classes/rogue/">'
            "<style>body { color: black; }</style></head>"
            f"<body>{SEARCH_SCRIPT}</body></html>"
        )

        migrated = migrate_html(html)

        self.assertNotIn("<style>", migrated)
        self.assertIn(SHARED_STYLESHEET, migrated)
        self.assertIn('rel="canonical"', migrated)

    def test_custom_page_without_search_script_is_unchanged(self):
        html = "<html><head><style>body { color: red; }</style></head></html>"

        self.assertEqual(migrate_html(html), html)

    def test_source_ads_and_inactive_dice_controls_are_removed(self):
        html = (
            "<html><head><title>Spell</title>"
            "<style>body { color: black; }</style></head><body>"
            '<main><p><a class="diceRoller" href="javascript:void(0);" '
            'onclick="rollValue()">1d6</a> damage.</p>'
            '<div class="footer"><script>googletag.cmd.push(x);</script></div>'
            "<script>analytics()</script></main>"
            f"{SEARCH_SCRIPT}</body></html>"
        )

        migrated = migrate_html(html)

        self.assertIn("<p>1d6 damage.</p>", migrated)
        self.assertNotIn("diceRoller", migrated)
        self.assertNotIn("googletag", migrated)
        self.assertNotIn("analytics()", migrated)

    def test_extracts_css_and_updates_template(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            template = root / "page.html"
            stylesheet = root / "assets" / "site.css"
            template.write_text(
                "<html><head><title>Page</title>"
                "<style>body { color: black; }</style></head>"
                f"<body>{SEARCH_SCRIPT}</body></html>",
                encoding="utf-8",
            )

            extract_template_css(template, stylesheet)

            self.assertEqual(
                stylesheet.read_text(encoding="utf-8"),
                "body { color: black; }\n",
            )
            self.assertIn(
                SHARED_STYLESHEET,
                template.read_text(encoding="utf-8"),
            )

    def test_migrates_and_audits_generated_pages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)
            page = public_dir / "classes" / "rogue" / "index.html"
            page.parent.mkdir(parents=True)
            page.write_text(
                "<html><head><title>Rogue</title>"
                "<style>body { color: black; }</style></head>"
                f"<body>{SEARCH_SCRIPT}</body></html>",
                encoding="utf-8",
            )

            self.assertEqual(migrate_generated_pages(public_dir), 1)
            self.assertEqual(audit_shared_styles(public_dir), [])


if __name__ == "__main__":
    unittest.main()
