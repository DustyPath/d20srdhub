import tempfile
import unittest
from pathlib import Path

from importer.skill_directory import (
    SkillPage,
    add_heading_ids,
    build_skill_article,
    collect_page_topics,
    skill_category,
)


class SkillDirectoryTests(unittest.TestCase):
    def test_classifies_standard_skills_by_ability(self):
        self.assertEqual(
            skill_category(
                "Balance (Dex; Armor Check Penalty)",
                "skills/balance",
            ),
            "Dexterity Skills",
        )
        self.assertEqual(
            skill_category("Using Skills", "skills/using-skills"),
            "Skill Rules",
        )

    def test_extracts_skill_uses_and_anchor_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            page_file = Path(temp_dir) / "heal" / "index.html"
            page_file.parent.mkdir()
            page_file.write_text(
                '<main class="article-card"><h1>Heal (Wis)</h1>'
                '<h2 id="firstAid">First Aid</h2></main>',
                encoding="utf-8",
            )
            page = SkillPage("Heal (Wis)", "skills/heal", "Wisdom Skills")
            topics = collect_page_topics(page_file, page)

            self.assertEqual(len(topics), 2)
            self.assertEqual(topics[1].href, "/skills/heal/#firstAid")

    def test_adds_stable_ids_to_legacy_subheadings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            page_file = Path(temp_dir) / "balance" / "index.html"
            page_file.parent.mkdir()
            page_file.write_text(
                '<main class="article-card"><h1>Balance</h1>'
                "<h5>Check</h5><h5>Action</h5></main>",
                encoding="utf-8",
            )

            changed = add_heading_ids(page_file)
            updated = page_file.read_text(encoding="utf-8")

            self.assertTrue(changed)
            self.assertIn('<h5 id="check">Check</h5>', updated)
            self.assertIn('<h5 id="action">Action</h5>', updated)

    def test_builds_skill_families_and_filter_controls(self):
        page = SkillPage("Heal (Wis)", "skills/heal", "Wisdom Skills")
        article = build_skill_article(
            [page],
            [],
        )

        self.assertIn("data-skill-directory", article)
        self.assertIn("Epic &amp; Psionic Skills", article)
        self.assertIn("/skills/heal/", article)
        self.assertIn("Skill-use quick reference", article)


if __name__ == "__main__":
    unittest.main()
