import tempfile
import unittest
from pathlib import Path

from importer.psionics_sections import (
    build_feats_article,
    collect_feats,
    collect_pages,
    content_tabs,
)


class PsionicsSectionTests(unittest.TestCase):
    def test_collects_class_pages_without_generic_index(self):
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            for slug, title in (("index", "Psionic Classes"), ("psion", "Psion")):
                page = public / "psionic" / "classes" / slug / "index.html"
                page.parent.mkdir(parents=True)
                page.write_text(
                    f'<main class="article-card"><h1>{title}</h1>'
                    '<p>Complete class rules and features.</p></main>',
                    encoding="utf-8",
                )
            entries = collect_pages("classes", public)
            self.assertEqual([entry.name for entry in entries], ["Psion"])
            self.assertEqual(entries[0].href, "/psionic/classes/psion/")

    def test_collects_and_filters_feat_headings(self):
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            page = public / "psionic" / "psionic-feats" / "index.html"
            page.parent.mkdir(parents=True)
            page.write_text(
                '<main class="article-card"><h1>Psionic Feats</h1>'
                '<h3 id="rules">Rules</h3><h2 id="featDescriptions">Feat Descriptions</h2>'
                '<h3 id="testFeat">Test Feat [Psionic]</h3></main>',
                encoding="utf-8",
            )
            entries = collect_feats(public)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].feat_type, "Psionic")
            article = build_feats_article(entries)
            self.assertIn("data-psionic-feat-directory", article)
            self.assertIn("/psionic/psionic-feats/#testFeat", article)

    def test_marks_active_content_tab(self):
        tabs = content_tabs("Powers")
        self.assertIn('href="/psionics/powers/" aria-current="page"', tabs)
        self.assertIn('href="/psionics/character-classes/"', tabs)


if __name__ == "__main__":
    unittest.main()
