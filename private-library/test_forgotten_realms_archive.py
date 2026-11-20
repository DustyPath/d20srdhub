import json
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("build_forgotten_realms_archive.py")
SPEC = importlib.util.spec_from_file_location("build_forgotten_realms_archive", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)
build, markdown_to_html, slug = MODULE.build, MODULE.markdown_to_html, MODULE.slug


class ForgottenRealmsArchiveTests(unittest.TestCase):
    def test_local_links_and_markup(self):
        rendered = markdown_to_html("## Lore\n\nSee [[Waterdeep|the City of Splendors]].")
        self.assertIn(f'/gm-secrets/forgotten-realms/wiki/{slug("Waterdeep")}/', rendered)
        self.assertIn("the City of Splendors", rendered)
        self.assertNotIn("forgottenrealms.fandom.com/wiki/Waterdeep", rendered)

    def test_builds_attributed_image_free_records(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            vault = root / "vault"; vault.mkdir()
            (vault / "Waterdeep.md").write_text(
                '---\ntitle: "Waterdeep"\ncategory: Settlements\n'
                'source_url: "https://forgottenrealms.fandom.com/wiki/Waterdeep"\n---\n'
                "# Waterdeep\n\nA city linked to [[Sword Coast]].\n",
                encoding="utf-8",
            )
            manifest = build(vault, root / "archive")
            article = json.loads((root / "archive/articles" / f"{slug('Waterdeep')}.json").read_text())
            self.assertEqual(1, manifest["articles"])
            self.assertEqual("CC BY-SA 3.0", article["license"])
            self.assertFalse(manifest["images_included"])
            self.assertNotIn("<img", article["html"])


if __name__ == "__main__":
    unittest.main()
