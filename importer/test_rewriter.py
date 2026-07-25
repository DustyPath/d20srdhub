import unittest

from importer.rewriter import rewrite_legacy_site_links, rewrite_links


class LinkRewriterTests(unittest.TestCase):
    def test_source_ogl_link_points_to_local_legal_page(self):
        rewritten = rewrite_links(
            '<p><a href="/ogl.htm">Open Game License</a></p>',
            "https://www.d20srd.org/srd/classes/rogue.htm",
        )

        self.assertIn('href="/legal/"', rewritten)
        self.assertNotIn("/ogl.htm", rewritten)

    def test_legacy_index_links_point_to_local_sections(self):
        rewritten = rewrite_links(
            '<a href="/indexes/classes.htm">Classes</a>'
            '<a href="/indexes/traps.htm#magic">Traps</a>',
            "https://www.d20srd.org/srd/variant/races/bloodlines.htm",
        )

        self.assertIn('href="/classes/"', rewritten)
        self.assertIn('href="/traps/#magic"', rewritten)

    def test_refresh_rewriter_updates_existing_generated_html(self):
        rewritten = rewrite_legacy_site_links(
            '<p><a href="/ogl.htm">Open Game License</a></p>'
        )

        self.assertIn('href="/legal/"', rewritten)
        self.assertNotIn("/ogl.htm", rewritten)

    def test_known_missing_source_fragment_falls_back_to_valid_page(self):
        source_rewritten = rewrite_links(
            '<a href="/srd/monsterFeats.htm#improvedMultiattack">'
            "Improved Multiattack</a>",
            "https://www.d20srd.org/srd/monsters/scorpionfolk.htm",
        )
        generated_rewritten = rewrite_legacy_site_links(
            '<a href="/monster-feats/#improvedMultiattack">'
            "Improved Multiattack</a>"
        )

        self.assertIn('href="/monster-feats/"', source_rewritten)
        self.assertIn('href="/monster-feats/"', generated_rewritten)
        self.assertNotIn("#improvedMultiattack", source_rewritten)
        self.assertNotIn("#improvedMultiattack", generated_rewritten)

    def test_external_links_are_unchanged(self):
        html = '<a href="https://example.com/license">External</a>'

        self.assertIn(
            'href="https://example.com/license"',
            rewrite_legacy_site_links(html),
        )


if __name__ == "__main__":
    unittest.main()
