import tempfile
import unittest
from pathlib import Path

from importer.rules_directories import (
    RuleTopic,
    build_conditions_article,
    build_magic_article,
    collect_topics,
)


class RulesDirectoryTests(unittest.TestCase):
    def test_collects_linked_heading_topics(self):
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text(
                '<main class="article-card"><h1>Casting Spells</h1>'
                '<h2 id="counterspells">Counterspells</h2></main>',
                encoding="utf-8",
            )
            topics = collect_topics(page, "Casting Spells", "Casting Spells", "magic-overview/casting-spells")
            self.assertEqual(topics[1].href, "/magic-overview/casting-spells/#counterspells")

    def test_magic_hub_links_spell_directory(self):
        article = build_magic_article([
            RuleTopic("Counterspells", "Casting Spells", "Casting Spells", "/counterspells/")
        ])
        self.assertIn("data-rule-directory", article)
        self.assertIn('/spells/', article)
        self.assertIn("Counterspells", article)

    def test_conditions_hub_is_searchable(self):
        article = build_conditions_article([
            RuleTopic("Blinded", "Condition Summary", "Awareness & Senses", "/condition-summary/#blinded")
        ])
        self.assertIn("Filter conditions", article)
        self.assertIn("Blinded", article)
        self.assertIn("Awareness &amp; Senses", article)


if __name__ == "__main__":
    unittest.main()
