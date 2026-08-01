import tempfile
import unittest
from pathlib import Path

from importer.basics_directory import build_basics_article, collect_basics_topics
from importer.rules_directories import RuleTopic


class BasicsDirectoryTests(unittest.TestCase):
    def test_assigns_ability_and_mechanics_categories(self):
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            basics = public / "the-basics"
            basics.mkdir()
            basics.joinpath("index.html").write_text(
                '<main class="article-card"><h1>The Basics</h1>'
                '<h2 id="theCoreMechanic">The Core Mechanic</h2>'
                '<h2 id="abilityScores">Ability Scores</h2>'
                '<h3 id="strengthStr">Strength (Str)</h3></main>',
                encoding="utf-8",
            )
            topics = collect_basics_topics(public)
            categories = {topic.name: topic.category for topic in topics}
            self.assertEqual(categories["The Core Mechanic"], "Core Mechanics")
            self.assertEqual(categories["Ability Scores"], "Ability Scores")
            self.assertEqual(categories["Strength (Str)"], "Ability Scores")

    def test_hub_contains_search_and_character_links(self):
        article = build_basics_article(
            [RuleTopic("Dice", "The Basics", "Core Mechanics", "/the-basics/#dice")]
        )
        self.assertIn("data-rule-directory", article)
        self.assertIn("Filter the basics", article)
        self.assertIn("/races/", article)
        self.assertIn("/classes/", article)
        self.assertIn("Dice", article)


if __name__ == "__main__":
    unittest.main()
