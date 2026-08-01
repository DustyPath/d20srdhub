import tempfile
import unittest
from pathlib import Path

from importer.monster_directory import (
    build_monster_article,
    parse_challenge_rating,
    parse_monster_page,
)


class MonsterDirectoryTests(unittest.TestCase):
    def test_parses_monster_type_and_challenge_rating(self):
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            page = public / "monsters" / "test-beast" / "index.html"
            page.parent.mkdir(parents=True)
            page.write_text(
                '<main class="article-card"><h1>Test Beast</h1><p>'
                'Size/Type: Large Magical Beast Hit Dice: 8d10 '
                'Challenge Rating: 6 Treasure: Standard</p></main>',
                encoding="utf-8",
            )
            entry = parse_monster_page(page, public)
            self.assertEqual(entry.creature_type, "Magical Beast")
            self.assertEqual(entry.challenge_rating, "6")
            self.assertEqual(entry.cr_band, "6-10")

    def test_handles_fractional_and_multiple_challenge_ratings(self):
        self.assertEqual(parse_challenge_rating("1/3"), ("1/3", "0-1"))
        self.assertEqual(parse_challenge_rating("1 2 2"), ("1 2 2", "2-5"))

    def test_builds_filterable_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            page = public / "monsters" / "goblin" / "index.html"
            page.parent.mkdir(parents=True)
            page.write_text(
                '<main class="article-card"><h1>Goblin</h1><p>'
                'Size/Type: Small Humanoid Hit Dice: 1d8 '
                'Challenge Rating: 1/3 Treasure: Standard</p></main>',
                encoding="utf-8",
            )
            entry = parse_monster_page(page, public)
            article = build_monster_article([entry])
            self.assertIn("data-monster-directory", article)
            self.assertIn("Goblin", article)
            self.assertIn("Creature Types &amp; Subtypes", article)


if __name__ == "__main__":
    unittest.main()
