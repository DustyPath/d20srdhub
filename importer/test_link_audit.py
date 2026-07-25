import tempfile
import unittest
from pathlib import Path

from importer.link_audit import audit_internal_links


class LinkAuditTests(unittest.TestCase):
    def test_valid_page_and_fragment_links_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)
            source = public_dir / "classes" / "index.html"
            target = public_dir / "classes" / "rogue" / "index.html"
            source.parent.mkdir(parents=True)
            target.parent.mkdir(parents=True)
            source.write_text(
                '<a href="/classes/rogue/#skills">Rogue</a>',
                encoding="utf-8",
            )
            target.write_text('<h2 id="skills">Skills</h2>', encoding="utf-8")

            self.assertEqual(audit_internal_links(public_dir), [])

    def test_missing_page_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)
            source = public_dir / "index.html"
            source.write_text(
                '<a href="/classes/rogue/">Rogue</a>',
                encoding="utf-8",
            )

            broken = audit_internal_links(public_dir)

            self.assertEqual(len(broken), 1)
            self.assertEqual(broken[0][1:], ("/classes/rogue/", "missing page"))

    def test_missing_fragment_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)
            source = public_dir / "index.html"
            target = public_dir / "rules" / "index.html"
            target.parent.mkdir()
            source.write_text(
                '<a href="/rules/#missing">Rule</a>',
                encoding="utf-8",
            )
            target.write_text("<h1>Rules</h1>", encoding="utf-8")

            broken = audit_internal_links(public_dir)

            self.assertEqual(len(broken), 1)
            self.assertEqual(broken[0][2], "missing fragment")

    def test_external_links_are_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            public_dir = Path(temp_dir)
            source = public_dir / "index.html"
            source.write_text(
                '<a href="https://example.com/missing">External</a>',
                encoding="utf-8",
            )

            self.assertEqual(audit_internal_links(public_dir), [])


if __name__ == "__main__":
    unittest.main()
