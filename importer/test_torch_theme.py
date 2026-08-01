from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]


class TorchThemeTests(unittest.TestCase):
    def test_desktop_layout_leaves_room_for_torches(self):
        css = (ROOT / "public" / "assets" / "site.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("@media (min-width: 1000px)", css)
        self.assertIn("width: min(1180px, calc(100% - 180px));", css)

    def test_wall_uses_a_stable_fixed_layer_without_animation(self):
        css = (ROOT / "public" / "assets" / "site.css").read_text(
            encoding="utf-8"
        )
        self.assertIn('url("/assets/medieval-hall-background.jpg")', css)
        self.assertIn("transform: translateZ(0);", css)
        self.assertIn("will-change: transform;", css)
        self.assertNotIn("background-attachment: fixed", css)
        self.assertNotIn("body::after {", css)
        self.assertNotIn("torch-flicker", css)

    def test_stylesheet_cache_version_is_updated(self):
        homepage = (ROOT / "public" / "index.html").read_text(encoding="utf-8")
        template = (ROOT / "templates" / "page.html").read_text(encoding="utf-8")
        self.assertIn("/assets/site.css?v=6", homepage)
        self.assertIn("/assets/site.css?v=6", template)

        unversioned_pages = []
        for page_path in (ROOT / "public").rglob("*.html"):
            page = page_path.read_text(encoding="utf-8")
            if 'href="/assets/site.css"' in page:
                unversioned_pages.append(str(page_path.relative_to(ROOT)))

        self.assertEqual([], unversioned_pages)


if __name__ == "__main__":
    unittest.main()
