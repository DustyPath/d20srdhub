import tempfile
import unittest
from pathlib import Path

from importer.equipment_directory import (
    build_equipment_article,
    collect_page_items,
)


class EquipmentDirectoryTests(unittest.TestCase):
    def test_extracts_table_rows_and_anchor_links(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            page = Path(temp_dir) / "weapons" / "index.html"
            page.parent.mkdir()
            page.write_text(
                '<html><main class="article-card"><table>'
                '<caption>Table: Weapons</caption>'
                '<tr><th>Weapon</th><th>Cost</th><th>Damage</th></tr>'
                '<tr><td><a href="#dagger">Dagger</a></td>'
                "<td>2 gp</td><td>1d4</td></tr>"
                "</table></main></html>",
                encoding="utf-8",
            )

            items = collect_page_items(page, "Weapons")

            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].name, "Dagger")
            self.assertEqual(items[0].href, "/equipment/weapons/#dagger")

    def test_builds_filterable_category_hub(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            page = Path(temp_dir) / "armor" / "index.html"
            page.parent.mkdir()
            page.write_text(
                '<html><main class="article-card"><table>'
                '<caption>Table: Armor and Shields</caption>'
                "<tr><td>Padded</td><td>5 gp</td><td>+1</td></tr>"
                "</table></main></html>",
                encoding="utf-8",
            )
            items = collect_page_items(page, "Armor & Shields")
            article = build_equipment_article(items)

            self.assertIn("data-equipment-directory", article)
            self.assertIn("Padded", article)
            self.assertIn("/equipment/goods-and-services/", article)


if __name__ == "__main__":
    unittest.main()
