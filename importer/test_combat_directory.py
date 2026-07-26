import tempfile
import unittest
from pathlib import Path

from importer.combat_directory import build_combat_article, collect_page_topics


class CombatDirectoryTests(unittest.TestCase):
    def test_extracts_heading_topics_and_anchor_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            page = Path(temp_dir) / "initiative" / "index.html"
            page.parent.mkdir()
            page.write_text(
                '<main class="article-card"><h1>Initiative</h1>'
                '<h2 id="initiativeChecks">Initiative Checks</h2>'
                "<p>Rules text.</p></main>",
                encoding="utf-8",
            )

            topics = collect_page_topics(
                page,
                "Initiative",
                "Combat Fundamentals",
            )

            self.assertEqual(len(topics), 2)
            self.assertEqual(
                topics[1].href,
                "/combat/initiative/#initiativeChecks",
            )

    def test_builds_filterable_combat_hub(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            page = Path(temp_dir) / "special-attacks" / "index.html"
            page.parent.mkdir()
            page.write_text(
                '<main class="article-card"><h1>Special Attacks</h1>'
                '<h2 id="bullRush">Bull Rush</h2></main>',
                encoding="utf-8",
            )
            topics = collect_page_topics(
                page,
                "Special Attacks",
                "Special Attacks & Injury",
            )
            article = build_combat_article(topics)

            self.assertIn("data-combat-directory", article)
            self.assertIn("Bull Rush", article)
            self.assertIn("/combat/actions-in-combat/", article)
            self.assertIn("Combat rulebooks", article)


if __name__ == "__main__":
    unittest.main()
