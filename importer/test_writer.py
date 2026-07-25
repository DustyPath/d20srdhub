import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from importer.writer import build_breadcrumbs, write_page


class BreadcrumbTests(unittest.TestCase):
    def test_nested_page_includes_section_and_title(self):
        breadcrumbs = build_breadcrumbs("classes/rogue", "Rogue")

        self.assertEqual(
            breadcrumbs,
            '<a href="/">Home</a> '
            '<span aria-hidden="true">›</span> '
            '<a href="/classes/">Classes</a> '
            '<span aria-hidden="true">›</span> '
            "<span>Rogue</span>",
        )

    def test_deep_page_includes_each_parent(self):
        breadcrumbs = build_breadcrumbs(
            "variant/building-characters/character-flaws",
            "Character Flaws",
        )

        self.assertIn('<a href="/variant/">Variant</a>', breadcrumbs)
        self.assertIn(
            '<a href="/variant/building-characters/">Building Characters</a>',
            breadcrumbs,
        )
        self.assertTrue(breadcrumbs.endswith("<span>Character Flaws</span>"))

    def test_labels_and_title_are_html_escaped(self):
        breadcrumbs = build_breadcrumbs("classes-and-roles/a", "A & B")

        self.assertIn("Classes And Roles", breadcrumbs)
        self.assertIn("<span>A &amp; B</span>", breadcrumbs)


class WriterTests(unittest.TestCase):
    def test_write_page_replaces_all_template_placeholders(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            public_dir = project_root / "public"
            templates_dir = project_root / "templates"
            templates_dir.mkdir()
            (templates_dir / "page.html").write_text(
                "<title>{{TITLE}}</title>"
                "<nav>{{BREADCRUMBS}}</nav>"
                "<main>{{ARTICLE}}</main>",
                encoding="utf-8",
            )

            with (
                patch("importer.writer.PROJECT_ROOT", project_root),
                patch("importer.writer.PUBLIC_DIR", public_dir),
            ):
                write_page("classes/rogue", "Rogue", "<h1>Rogue</h1>")

            generated = (
                public_dir / "classes" / "rogue" / "index.html"
            ).read_text(encoding="utf-8")

            self.assertIn('<a href="/classes/">Classes</a>', generated)
            self.assertIn("<span>Rogue</span>", generated)
            self.assertIn("<main><h1>Rogue</h1></main>", generated)
            self.assertNotIn("{{", generated)


if __name__ == "__main__":
    unittest.main()
