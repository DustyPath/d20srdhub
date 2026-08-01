from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]


class TorchThemeTests(unittest.TestCase):
    def test_desktop_layout_leaves_room_for_torches(self):
        css = (ROOT / "public" / "assets" / "site.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("@media (min-width: 1321px)", css)
        self.assertIn("width: min(1180px, calc(100% - 220px));", css)
        self.assertIn("background-size: max(100vw, 1717px) auto;", css)

    def test_flame_animation_respects_reduced_motion(self):
        css = (ROOT / "public" / "assets" / "site.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("@keyframes torch-flicker", css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)
        self.assertIn("animation: none;", css)

    def test_stylesheet_cache_version_is_updated(self):
        homepage = (ROOT / "public" / "index.html").read_text(encoding="utf-8")
        template = (ROOT / "templates" / "page.html").read_text(encoding="utf-8")
        self.assertIn("/assets/site.css?v=5", homepage)
        self.assertIn("/assets/site.css?v=5", template)


if __name__ == "__main__":
    unittest.main()
