import importlib.util
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location(
    "build_spell_index",
    Path(__file__).with_name("build_spell_index.py"),
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SpellIndexTests(unittest.TestCase):
    def test_slugify_normalizes_spell_titles(self):
        self.assertEqual(
            MODULE.slugify("Mordenkainen’s Sword"),
            "mordenkainens-sword",
        )

    def test_rejects_table_rows_that_look_like_titles(self):
        self.assertFalse(MODULE.looks_like_title("Web 10th 1,000 XP"))

    def test_comparison_key_matches_reordered_qualifier(self):
        self.assertEqual(
            MODULE.comparison_key("Mass Haste"),
            MODULE.comparison_key("Haste, Mass"),
        )

    def test_extracts_spell_and_excludes_public_duplicate(self):
        pages = [
            {
                "page": 42,
                "text": (
                    "Fireball\n"
                    "Evocation [Fire] Level: Sor/Wiz 3 Components: V, S, M\n"
                    "A burst of fire.\n"
                    "Private Shadow\n"
                    "Illusion (Shadow) Level: Clr 3, Sor/Wiz 4 Components: V, S\n"
                    "A private effect."
                ),
            }
        ]
        spells = MODULE.extract_spells(pages, {"fireball"})
        self.assertEqual(
            spells,
            [
                {
                    "name": "Private Shadow",
                    "page": 42,
                    "school": "Illusion",
                    "levels": "Clr 3, Sor/Wiz 4",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
