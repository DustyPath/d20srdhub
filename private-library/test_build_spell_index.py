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

    def test_extracts_split_school_and_level_metadata(self):
        pages = [
            {
                "page": 10,
                "text": (
                    "CREAKING\n"
                    "CACOPHONY\n"
                    "Illusion (Figment) [Sonic]\n"
                    "Level: Bard 3, druid 3\n"
                    "Components: V, S\n"
                ),
            }
        ]
        self.assertEqual(
            MODULE.extract_spells(pages, set()),
            [
                {
                    "name": "CREAKING CACOPHONY",
                    "page": 10,
                    "school": "Illusion",
                    "levels": "Bard 3, druid 3",
                }
            ],
        )

    def test_build_index_records_requested_book_name(self):
        original_extract_pages = MODULE.extract_pages
        original_public_spell_slugs = MODULE.public_spell_slugs
        try:
            MODULE.extract_pages = lambda *_: [
                {
                    "page": 5,
                    "text": "Private Spell\nEvocation\nLevel: Wizard 2\nComponents: V",
                }
            ]
            MODULE.public_spell_slugs = lambda *_: set()
            with self.subTest("custom book name"):
                import tempfile

                with tempfile.TemporaryDirectory() as directory:
                    output = Path(directory) / "index.json"
                    payload = MODULE.build_index(
                        Path("book.pdf"),
                        Path("public"),
                        output,
                        book_name="Spell Compendium v2",
                    )
                    self.assertEqual(payload["book"], "Spell Compendium v2")
        finally:
            MODULE.extract_pages = original_extract_pages
            MODULE.public_spell_slugs = original_public_spell_slugs


if __name__ == "__main__":
    unittest.main()
