import tempfile
import unittest
from pathlib import Path

from importer.class_directory import build_class_article, collect_page_topics


class ClassDirectoryTests(unittest.TestCase):
    def test_extracts_class_features_and_anchor_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            page = Path(temp_dir) / "rogue" / "index.html"
            page.parent.mkdir()
            page.write_text(
                '<main class="article-card"><h1>Rogue</h1>'
                '<h2 id="sneakAttack">Sneak Attack</h2></main>',
                encoding="utf-8",
            )

            topics = collect_page_topics(
                page,
                "Rogue",
                "Core Classes",
                "classes/rogue",
            )

            self.assertEqual(len(topics), 2)
            self.assertEqual(
                topics[1].href,
                "/classes/rogue/#sneakAttack",
            )

    def test_builds_all_class_families_and_filter_controls(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            page = Path(temp_dir) / "rogue" / "index.html"
            page.parent.mkdir()
            page.write_text(
                '<main class="article-card"><h1>Rogue</h1></main>',
                encoding="utf-8",
            )
            topics = collect_page_topics(
                page,
                "Rogue",
                "Core Classes",
                "classes/rogue",
            )
            article = build_class_article(topics)

            self.assertIn("data-class-directory", article)
            self.assertIn("/npc-classes/adept/", article)
            self.assertIn("/prestige-classes/archmage/", article)
            self.assertIn("Class feature quick reference", article)


if __name__ == "__main__":
    unittest.main()
