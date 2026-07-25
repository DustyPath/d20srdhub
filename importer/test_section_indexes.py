import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from importer.section_indexes import (
    build_section_article,
    generate_section_indexes,
    linked_section_paths,
    section_label,
)


class SectionIndexTests(unittest.TestCase):
    def test_special_section_labels_are_readable(self):
        self.assertEqual(section_label("psionic"), "Psionics")
        self.assertEqual(section_label("variant"), "Variant Rules")
        self.assertEqual(section_label("magic-items"), "Magic Items")

    def test_finds_linked_directory_without_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)
            page = public_dir / "source" / "index.html"
            child = public_dir / "variant" / "adventuring" / "index.html"
            page.parent.mkdir(parents=True)
            child.parent.mkdir(parents=True)
            page.write_text('<a href="/variant/">Variant</a>', encoding="utf-8")
            child.write_text("<h1>Adventuring</h1>", encoding="utf-8")

            self.assertEqual(
                linked_section_paths(public_dir),
                ["variant"],
            )

    def test_article_lists_immediate_children(self):
        title, article = build_section_article(
            "psionic",
            [("classes", "Classes"), ("powers", "Powers")],
        )

        self.assertEqual(title, "Psionics")
        self.assertIn('href="/psionic/classes/"', article)
        self.assertIn('href="/psionic/powers/"', article)

    def test_generates_missing_index_with_shared_template(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            public_dir = project_root / "public"
            templates_dir = project_root / "templates"
            source = public_dir / "source" / "index.html"
            child = public_dir / "variant" / "adventuring" / "index.html"

            source.parent.mkdir(parents=True)
            child.parent.mkdir(parents=True)
            templates_dir.mkdir()
            source.write_text('<a href="/variant/">Variant</a>', encoding="utf-8")
            child.write_text("<h1>Adventuring</h1>", encoding="utf-8")
            (templates_dir / "page.html").write_text(
                "<title>{{TITLE}}</title>"
                "<nav>{{BREADCRUMBS}}</nav>"
                "<main>{{ARTICLE}}</main>"
                "<nav>{{PAGE_NAVIGATION}}</nav>",
                encoding="utf-8",
            )

            with (
                patch("importer.writer.PROJECT_ROOT", project_root),
                patch("importer.writer.PUBLIC_DIR", public_dir),
            ):
                created = generate_section_indexes(public_dir)

            generated = public_dir / "variant" / "index.html"

            self.assertEqual(created, ["variant"])
            self.assertTrue(generated.exists())
            self.assertIn("Variant Rules", generated.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
