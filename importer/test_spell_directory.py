import tempfile
import unittest
from pathlib import Path

from importer.spell_directory import (
    build_spell_article,
    collect_spells,
    parse_spell,
)


def sample_page(title, school, levels):
    return (
        '<html><body><main class="article-card">'
        f"<h1>{title}</h1><h4>{school}</h4>"
        f'<table class="statBlock"><tr><td>Level: {levels}</td>'
        "<td>Components: V, S</td></tr></table>"
        "</main></body></html>"
    )


class SpellDirectoryTests(unittest.TestCase):
    def test_parses_spell_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            page = Path(temp_dir) / "fireball" / "index.html"
            page.parent.mkdir()
            page.write_text(
                sample_page("Fireball", "Evocation [Fire]", "Sor/Wiz 3"),
                encoding="utf-8",
            )

            spell = parse_spell(page)

            self.assertEqual(spell.title, "Fireball")
            self.assertEqual(spell.school, "Evocation")
            self.assertEqual(spell.levels, ("3",))

    def test_collects_and_builds_filterable_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            spells_dir = Path(temp_dir) / "spells"

            for slug, title, school, levels in (
                ("fireball", "Fireball", "Evocation [Fire]", "Sor/Wiz 3"),
                ("detect-magic", "Detect Magic", "Divination", "Brd 0, Clr 0"),
            ):
                page = spells_dir / slug / "index.html"
                page.parent.mkdir(parents=True)
                page.write_text(
                    sample_page(title, school, levels),
                    encoding="utf-8",
                )

            spells = collect_spells(Path(temp_dir))
            article = build_spell_article(spells)

            self.assertEqual([spell.title for spell in spells],
                             ["Detect Magic", "Fireball"])
            self.assertIn("data-spell-directory", article)
            self.assertIn('data-levels="0"', article)
            self.assertIn("/spell-lists/sorcerer-wizard-spells/", article)
            self.assertIn("https://library.d20srdhub.com/", article)


if __name__ == "__main__":
    unittest.main()
