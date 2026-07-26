"""Generate the complete, filterable spells landing page."""

from dataclasses import dataclass
from html import escape
from pathlib import Path
import re

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.writer import write_page

LEVEL_PATTERN = re.compile(
    r"\bLevel\s*:\s*(.*?)(?=\bComponents\s*:|$)",
    re.IGNORECASE,
)

SPELL_LISTS = (
    ("Bard", "/spell-lists/bard-spells/"),
    ("Cleric", "/spell-lists/cleric-spells/"),
    ("Cleric Domains", "/spell-lists/cleric-domains/"),
    ("Druid", "/spell-lists/druid-spells/"),
    ("Paladin", "/spell-lists/paladin-spells/"),
    ("Ranger", "/spell-lists/ranger-spells/"),
    ("Sorcerer / Wizard", "/spell-lists/sorcerer-wizard-spells/"),
)


@dataclass(frozen=True)
class Spell:
    title: str
    slug: str
    school: str
    levels: tuple[str, ...]
    level_text: str


def parse_spell(page_file):
    """Extract directory metadata from one generated spell page."""

    soup = BeautifulSoup(
        page_file.read_text(encoding="utf-8", errors="replace"),
        "html.parser",
    )
    article = soup.select_one(".article-card")

    if article is None:
        return None

    heading = article.find(["h1", "h2"])

    if heading is None:
        return None

    school_heading = heading.find_next("h4")
    school_text = school_heading.get_text(" ", strip=True) if school_heading else ""
    school = re.split(r"\s*[\[(]", school_text, maxsplit=1)[0].strip()
    stat_block = article.select_one("table.statBlock")
    stat_text = stat_block.get_text(" ", strip=True) if stat_block else ""
    level_match = LEVEL_PATTERN.search(stat_text)
    level_text = level_match.group(1).strip() if level_match else ""
    levels = tuple(sorted(set(re.findall(r"\b[0-9]\b", level_text))))

    return Spell(
        title=heading.get_text(" ", strip=True),
        slug=page_file.parent.name,
        school=school or "Other",
        levels=levels,
        level_text=level_text,
    )


def collect_spells(public_dir=PUBLIC_DIR):
    """Return every individual spell sorted by title."""

    spells_dir = public_dir / "spells"
    spells = []

    for page_file in spells_dir.glob("*/index.html"):
        spell = parse_spell(page_file)

        if spell is not None:
            spells.append(spell)

    return sorted(spells, key=lambda spell: spell.title.casefold())


def build_spell_article(spells):
    """Build the filterable spell-directory article."""

    schools = sorted({spell.school for spell in spells})
    school_options = "\n".join(
        f'                    <option value="{escape(name, quote=True)}">'
        f"{escape(name)}</option>"
        for name in schools
    )
    class_links = "\n".join(
        f'            <a href="{href}">{escape(label)}</a>'
        for label, href in SPELL_LISTS
    )
    groups = []

    for letter in sorted({spell.title[0].upper() for spell in spells}):
        entries = []

        for spell in spells:
            if spell.title[0].upper() != letter:
                continue

            levels = ",".join(spell.levels)
            meta = " · ".join(
                part for part in (spell.school, spell.level_text) if part
            )
            entries.append(
                '                <li data-spell-item '
                f'data-name="{escape(spell.title.casefold(), quote=True)}" '
                f'data-school="{escape(spell.school, quote=True)}" '
                f'data-levels="{escape(levels, quote=True)}">'
                f'<a href="/spells/{escape(spell.slug)}/">'
                f"<strong>{escape(spell.title)}</strong>"
                f'<span class="spell-directory-meta">{escape(meta)}</span>'
                "</a></li>"
            )

        groups.append(
            f'        <section class="spell-letter-group" data-spell-group>'
            f'<h2>{escape(letter)}</h2>'
            f'<ul class="spell-directory-list">\n'
            + "\n".join(entries)
            + "\n            </ul></section>"
        )

    return (
        "<h1>Spells</h1>\n"
        f"<p>Browse {len(spells)} spells from the d20 System Reference "
        "Document by class, name, school, or spell level.</p>\n"
        '<section class="spell-list-shortcuts" aria-labelledby="class-lists">\n'
        '    <h2 id="class-lists">Spell lists by class</h2>\n'
        f'    <div class="spell-list-links">\n{class_links}\n    </div>\n'
        "</section>\n"
        '<section class="spell-directory" data-spell-directory '
        'aria-labelledby="all-spells">\n'
        '    <h2 id="all-spells">All spells</h2>\n'
        '    <div class="spell-filters">\n'
        '        <label>Spell name<input data-spell-search type="search" '
        'placeholder="Filter by name…"></label>\n'
        '        <label>School<select data-spell-school>'
        '<option value="">All schools</option>\n'
        f"{school_options}</select></label>\n"
        '        <label>Level<select data-spell-level>'
        '<option value="">All levels</option>'
        + "".join(f'<option value="{level}">{level}</option>' for level in range(10))
        + "</select></label>\n"
        '        <p class="spell-result-count" data-spell-count '
        'aria-live="polite"></p>\n'
        "    </div>\n"
        + "\n".join(groups)
        + "\n</section>\n"
        '<script src="/assets/spell-directory.js?v=1" defer></script>'
    )


def generate_spell_directory(public_dir=PUBLIC_DIR):
    """Generate `/spells/` and return the number of indexed spells."""

    spells = collect_spells(public_dir)

    if public_dir == PUBLIC_DIR:
        write_page("spells", "Spells", build_spell_article(spells))
    else:
        destination = public_dir / "spells" / "article.html"
        destination.write_text(build_spell_article(spells), encoding="utf-8")

    return len(spells)


def main():
    count = generate_spell_directory()
    print(f"Created spell directory with {count} spells.")


if __name__ == "__main__":
    main()
