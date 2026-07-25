import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from importer.writer import (
    build_breadcrumbs,
    build_description,
    build_page_navigation,
    write_page,
)


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
    def test_description_uses_first_paragraph_and_is_limited(self):
        description = build_description(
            "<h1>Fireball</h1><p>"
            + ("A burst of magical flame deals damage. " * 10)
            + "</p>",
            "Fireball",
        )

        self.assertLessEqual(len(description), 155)
        self.assertTrue(description.endswith("…"))

    def test_write_page_replaces_all_template_placeholders(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            public_dir = project_root / "public"
            templates_dir = project_root / "templates"
            templates_dir.mkdir()
            (templates_dir / "page.html").write_text(
                "<title>{{TITLE}}</title>"
                '<meta name="description" content="{{DESCRIPTION}}">'
                '<link rel="canonical" href="{{CANONICAL_URL}}">'
                "<nav>{{BREADCRUMBS}}</nav>"
                "<main>{{ARTICLE}}</main>"
                "<nav>{{PAGE_NAVIGATION}}</nav>",
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
            self.assertIn(
                'href="https://d20srdhub.com/classes/rogue/"',
                generated,
            )
            self.assertNotIn("{{", generated)


class PageNavigationTests(unittest.TestCase):
    def test_navigation_is_built_before_current_page_is_written(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)

            for slug in ["ranger", "sorcerer-wizard"]:
                page_directory = public_dir / "classes" / slug
                page_directory.mkdir(parents=True)
                (page_directory / "index.html").write_text(
                    f"<title>{slug.title()} | d20 SRD Hub</title>",
                    encoding="utf-8",
                )

            with patch("importer.writer.PUBLIC_DIR", public_dir):
                navigation = build_page_navigation("classes/rogue")

            self.assertIn('href="/classes/ranger/"', navigation)
            self.assertIn('href="/classes/sorcerer-wizard/"', navigation)

    def test_middle_page_links_to_previous_and_next_siblings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)

            for slug, title in [
                ("ranger", "Ranger"),
                ("rogue", "Rogue"),
                ("sorcerer-wizard", "Sorcerer/Wizard"),
            ]:
                page_directory = public_dir / "classes" / slug
                page_directory.mkdir(parents=True)
                (page_directory / "index.html").write_text(
                    f"<title>{title} | d20 SRD Hub</title>",
                    encoding="utf-8",
                )

            with patch("importer.writer.PUBLIC_DIR", public_dir):
                navigation = build_page_navigation("classes/rogue")

            self.assertIn('href="/classes/ranger/"', navigation)
            self.assertIn(">Ranger</span>", navigation)
            self.assertIn('href="/classes/sorcerer-wizard/"', navigation)
            self.assertIn(">Sorcerer/Wizard</span>", navigation)

    def test_first_page_only_has_next_link(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)

            for slug in ["barbarian", "bard"]:
                page_directory = public_dir / "classes" / slug
                page_directory.mkdir(parents=True)
                (page_directory / "index.html").write_text(
                    f"<title>{slug.title()} | d20 SRD Hub</title>",
                    encoding="utf-8",
                )

            with patch("importer.writer.PUBLIC_DIR", public_dir):
                navigation = build_page_navigation("classes/barbarian")

            self.assertNotIn("← Previous", navigation)
            self.assertIn("Next →", navigation)
            self.assertIn('href="/classes/bard/"', navigation)

    def test_only_page_has_no_navigation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)
            page_directory = public_dir / "classes" / "rogue"
            page_directory.mkdir(parents=True)
            (page_directory / "index.html").write_text(
                "<title>Rogue | d20 SRD Hub</title>",
                encoding="utf-8",
            )

            with patch("importer.writer.PUBLIC_DIR", public_dir):
                navigation = build_page_navigation("classes/rogue")

            self.assertEqual(navigation, "")


if __name__ == "__main__":
    unittest.main()
