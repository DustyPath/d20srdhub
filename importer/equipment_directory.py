"""Generate the complete, filterable equipment landing page."""

from dataclasses import dataclass
from html import escape
from pathlib import Path

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.writer import write_page

CATEGORIES = (
    (
        "Weapons",
        "weapons",
        "Weapon categories, costs, damage, critical hits, range, weight, and descriptions.",
    ),
    (
        "Armor & Shields",
        "armor",
        "Armor bonuses, Dexterity limits, check penalties, spell failure, speed, and weight.",
    ),
    (
        "Goods & Services",
        "goods-and-services",
        "Adventuring gear, tools, clothing, lodging, mounts, transport, and spellcasting services.",
    ),
    (
        "Wealth & Money",
        "wealth-and-money",
        "Coins, exchange values, trade goods, starting wealth, and selling loot.",
    ),
)
AUXILIARY_TABLES = {
    "Donning Armor",
    "Larger and Smaller Weapon Damage",
}


@dataclass(frozen=True)
class EquipmentItem:
    name: str
    category: str
    subcategory: str
    details: str
    href: str


def table_label(table):
    """Return a readable table label."""

    caption = table.find("caption")

    if caption:
        return caption.get_text(" ", strip=True).removeprefix("Table: ").strip()

    return "Other Equipment"


def collect_page_items(page_file, category):
    """Extract useful quick-reference rows from one equipment page."""

    soup = BeautifulSoup(
        page_file.read_text(encoding="utf-8", errors="replace"),
        "html.parser",
    )
    article = soup.select_one(".article-card")
    items = []

    if article is None:
        return items

    for table in article.find_all("table"):
        subcategory = table_label(table)

        if subcategory in AUXILIARY_TABLES:
            continue

        for row in table.find_all("tr"):
            cells = row.find_all("td", recursive=False)

            if len(cells) < 2:
                continue

            values = [cell.get_text(" ", strip=True) for cell in cells]

            if subcategory == "Trade Goods":
                name = values[1]
                details = values[0]
                name_cell = cells[1]
            else:
                name = values[0]
                details = " · ".join(value for value in values[1:4] if value)
                name_cell = cells[0]

            if not name or len(name) > 100 or len(details) > 180:
                continue

            anchor = name_cell.find("a", href=True)
            href = f"/equipment/{page_file.parent.name}/"

            if anchor and anchor["href"].startswith("#"):
                href += anchor["href"]

            items.append(
                EquipmentItem(
                    name=name,
                    category=category,
                    subcategory=subcategory,
                    details=details,
                    href=href,
                )
            )

    return items


def collect_equipment(public_dir=PUBLIC_DIR):
    """Return unique equipment entries grouped from all four source pages."""

    items = []

    for title, slug, _description in CATEGORIES:
        page_file = public_dir / "equipment" / slug / "index.html"

        if page_file.exists():
            items.extend(collect_page_items(page_file, title))

    unique = {}

    for item in items:
        unique[(item.category, item.subcategory, item.name)] = item

    return sorted(
        unique.values(),
        key=lambda item: (
            item.category.casefold(),
            item.subcategory.casefold(),
            item.name.casefold(),
        ),
    )


def build_equipment_article(items):
    """Build the complete equipment hub article."""

    cards = "\n".join(
        f'        <a class="equipment-category-card" '
        f'href="/equipment/{escape(slug)}/">'
        f"<h2>{escape(title)}</h2><p>{escape(description)}</p></a>"
        for title, slug, description in CATEGORIES
    )
    category_options = "\n".join(
        f'                <option value="{escape(title, quote=True)}">'
        f"{escape(title)}</option>"
        for title, _slug, _description in CATEGORIES
    )
    groups = []

    for subcategory in sorted({item.subcategory for item in items}):
        entries = []

        for item in items:
            if item.subcategory != subcategory:
                continue

            entries.append(
                '                <li data-equipment-item '
                f'data-name="{escape(item.name.casefold(), quote=True)}" '
                f'data-category="{escape(item.category, quote=True)}">'
                f'<a href="{escape(item.href, quote=True)}">'
                f"<strong>{escape(item.name)}</strong>"
                f'<span class="equipment-directory-meta">'
                f"{escape(item.category)} · {escape(item.details)}</span>"
                "</a></li>"
            )

        groups.append(
            '<section class="equipment-reference-group" data-equipment-group>'
            f"<h2>{escape(subcategory)}</h2>"
            '<ul class="equipment-directory-list">\n'
            + "\n".join(entries)
            + "\n            </ul></section>"
        )

    return (
        "<h1>Equipment</h1>\n"
        "<p>Browse weapons, armor, adventuring gear, services, transport, "
        "currency, and trade goods from the d20 System Reference Document.</p>\n"
        f'<section class="equipment-category-grid" '
        f'aria-label="Equipment categories">\n{cards}\n</section>\n'
        '<section class="equipment-directory" data-equipment-directory '
        'aria-labelledby="equipment-reference">\n'
        '<h2 id="equipment-reference">Equipment quick reference</h2>\n'
        '<div class="equipment-filters">\n'
        '<label>Item or service<input data-equipment-search type="search" '
        'placeholder="Filter equipment…"></label>\n'
        '<label>Category<select data-equipment-category>'
        '<option value="">All categories</option>\n'
        f"{category_options}</select></label>\n"
        '<p class="equipment-result-count" data-equipment-count '
        'aria-live="polite"></p>\n'
        "</div>\n"
        + "\n".join(groups)
        + "\n</section>\n"
        '<script src="/assets/equipment-directory.js?v=1" defer></script>'
    )


def generate_equipment_directory(public_dir=PUBLIC_DIR):
    """Generate `/equipment/` and return the number of indexed entries."""

    items = collect_equipment(public_dir)

    if public_dir == PUBLIC_DIR:
        write_page("equipment", "Equipment", build_equipment_article(items))

    return len(items)


def main():
    count = generate_equipment_directory()
    print(f"Created equipment directory with {count} entries.")


if __name__ == "__main__":
    main()
