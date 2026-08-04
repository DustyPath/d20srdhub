import tempfile
import unittest
from pathlib import Path

from importer.psionics_directory import build_psionics_article, parse_power_page


class PsionicsDirectoryTests(unittest.TestCase):
    def test_parses_power_discipline_and_levels(self):
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            page = public / "psionic" / "powers" / "test-power" / "index.html"
            page.parent.mkdir(parents=True)
            page.write_text(
                '<main class="article-card"><h1>Test Power</h1>'
                '<h4>Telepathy [Mind-Affecting]</h4><table><tr>'
                '<th>Level:</th><td>Psion/wilder 2, psychic warrior 3</td>'
                '</tr></table></main>',
                encoding="utf-8",
            )
            entry = parse_power_page(page, public)
            self.assertEqual(entry.discipline, "Telepathy")
            self.assertEqual(entry.levels, ("2", "3"))
            self.assertEqual(entry.href, "/psionic/powers/test-power/")

    def test_builds_filterable_power_directory_and_section_links(self):
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            page = public / "psionic" / "powers" / "test-power" / "index.html"
            page.parent.mkdir(parents=True)
            page.write_text(
                '<main class="article-card"><h1>Test Power</h1>'
                '<h4>Psychokinesis</h4><table><tr><th>Level:</th>'
                '<td>Psion/wilder 1</td></tr></table></main>',
                encoding="utf-8",
            )
            article = build_psionics_article([parse_power_page(page, public)])
            self.assertIn("data-power-directory", article)
            self.assertIn("Test Power", article)
            self.assertIn('href="/psionic/classes/"', article)
            self.assertIn('href="/psionic/items/"', article)
            self.assertIn("psionics-directory.js?v=1", article)

    def test_normalizes_psychokinetic_source_label(self):
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            page = public / "psionic" / "powers" / "energy-push" / "index.html"
            page.parent.mkdir(parents=True)
            page.write_text(
                '<main class="article-card"><h1>Energy Push</h1>'
                '<h4>Psychokinetic [see text]</h4><table><tr><th>Level:</th>'
                '<td>Psion/wilder 2</td></tr></table></main>',
                encoding="utf-8",
            )
            entry = parse_power_page(page, public)
            self.assertEqual(entry.discipline, "Psychokinesis")


if __name__ == "__main__":
    unittest.main()
