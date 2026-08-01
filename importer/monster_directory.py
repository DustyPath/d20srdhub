"""Generate the complete, filterable monster landing page."""

from dataclasses import dataclass
from fractions import Fraction
from html import escape
import re

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.writer import write_page


CREATURE_TYPES = (
    "Monstrous Humanoid",
    "Magical Beast",
    "Aberration",
    "Animal",
    "Construct",
    "Dragon",
    "Elemental",
    "Fey",
    "Giant",
    "Humanoid",
    "Ooze",
    "Outsider",
    "Plant",
    "Undead",
    "Vermin",
)

FEATURED_TYPES = (
    ("Humanoids", "Humanoid", "People-like creatures, cultures, and adversaries."),
    ("Dragons", "Dragon", "True dragons, dragonkind, and draconic creatures."),
    ("Magical Beasts", "Magical Beast", "Fantastic animals with supernatural traits."),
    ("Outsiders", "Outsider", "Celestials, fiends, and planar beings."),
    ("Undead", "Undead", "Unliving creatures powered by negative energy."),
    ("Constructs", "Construct", "Created creatures, guardians, and animated objects."),
)

REFERENCE_PAGES = (
    ("Creature Types & Subtypes", "/types-subtypes/", "Traits shared by creature types and subtypes."),
    ("Special Abilities", "/special-abilities/", "Extraordinary, supernatural, and spell-like abilities."),
    ("Monster Feats", "/monster-feats/", "Feats commonly used by monsters and creatures."),
    ("Monsters as Races", "/monsters-as-races/", "Rules for monster characters and level adjustment."),
)


@dataclass(frozen=True)
class MonsterEntry:
    name: str
    href: str
    creature_type: str
    challenge_rating: str
    cr_band: str
    letter: str


def parse_challenge_rating(value):
    """Return a display CR and a useful filtering band."""

    tokens = re.findall(r"(?<![A-Za-z])(?:\d+/\d+|\d+(?:\.\d+)?)(?![A-Za-z])", value)
    ratings = []
    for token in tokens:
        try:
            ratings.append(float(Fraction(token)))
        except (ValueError, ZeroDivisionError):
            continue

    if not ratings:
        return "Reference", "reference"

    highest = max(ratings)
    display = value.strip(" ,;-")
    if highest <= 1:
        band = "0-1"
    elif highest <= 5:
        band = "2-5"
    elif highest <= 10:
        band = "6-10"
    elif highest <= 15:
        band = "11-15"
    else:
        band = "16+"
    return display, band


def detect_creature_type(size_type_text):
    """Detect the primary SRD creature type from a stat block."""

    for creature_type in CREATURE_TYPES:
        if re.search(rf"\b{re.escape(creature_type)}\b", size_type_text, re.IGNORECASE):
            return creature_type
    return "Creature Family / Rules"


def parse_monster_page(page_file, public_dir=PUBLIC_DIR):
    """Extract directory metadata from one generated monster page."""

    soup = BeautifulSoup(page_file.read_text(encoding="utf-8", errors="replace"), "html.parser")
    article = soup.select_one(".article-card")
    if article is None:
        return None

    heading = article.find("h1")
    if heading is None:
        return None
    name = heading.get_text(" ", strip=True)
    text = article.get_text(" ", strip=True)

    size_type = re.search(r"Size/Type\s*:\s*(.*?)\s+Hit Dice\s*:", text, re.IGNORECASE)
    creature_type = detect_creature_type(size_type.group(1) if size_type else "")

    cr_match = re.search(
        r"Challenge Rating\s*:\s*(.*?)(?=\s+(?:Treasure|Alignment|Advancement|Level Adjustment)\s*:)",
        text,
        re.IGNORECASE,
    )
    challenge_rating, cr_band = parse_challenge_rating(cr_match.group(1) if cr_match else "")
    href = "/" + page_file.parent.relative_to(public_dir).as_posix() + "/"
    letter = name[0].upper() if name and name[0].isalpha() else "#"
    return MonsterEntry(name, href, creature_type, challenge_rating, cr_band, letter)


def collect_monsters(public_dir=PUBLIC_DIR):
    """Return all monster pages with extracted type and CR metadata."""

    entries = []
    for page_file in (public_dir / "monsters").glob("*/index.html"):
        entry = parse_monster_page(page_file, public_dir)
        if entry is not None:
            entries.append(entry)
    return sorted(entries, key=lambda item: item.name.casefold())


def build_monster_article(entries):
    """Build the complete monster directory article."""

    featured = "\n".join(
        '<a class="monster-type-card" href="#monster-directory" '
        f'data-monster-type-card="{escape(creature_type, quote=True)}">'
        f"<strong>{escape(title)}</strong><p>{escape(description)}</p></a>"
        for title, creature_type, description in FEATURED_TYPES
    )
    references = "\n".join(
        f'<a class="monster-reference-card" href="{href}"><strong>{escape(title)}</strong>'
        f"<span>{escape(description)}</span></a>"
        for title, href, description in REFERENCE_PAGES
    )
    available_types = sorted({entry.creature_type for entry in entries})
    type_options = "\n".join(
        f'<option value="{escape(value, quote=True)}">{escape(value)}</option>'
        for value in available_types
    )
    groups = []
    for letter in sorted({entry.letter for entry in entries}):
        items = []
        for entry in entries:
            if entry.letter != letter:
                continue
            search_text = f"{entry.name} {entry.creature_type} {entry.challenge_rating}".casefold()
            items.append(
                '<li data-monster-item '
                f'data-name="{escape(search_text, quote=True)}" '
                f'data-type="{escape(entry.creature_type, quote=True)}" '
                f'data-cr="{escape(entry.cr_band, quote=True)}">'
                f'<a href="{escape(entry.href, quote=True)}"><strong>{escape(entry.name)}</strong>'
                f'<span>{escape(entry.creature_type)} · '
                f'{"CR " + escape(entry.challenge_rating) if entry.cr_band != "reference" else "Reference page"}'
                "</span></a></li>"
            )
        groups.append(
            f'<section class="monster-letter-group" data-monster-group id="monsters-{escape(letter.lower())}">'
            f'<h2>{escape(letter)}</h2><ul class="monster-directory-list">'
            + "\n".join(items)
            + "</ul></section>"
        )

    return (
        "<h1>Monsters</h1>\n"
        "<p>Search the complete SRD creature collection by name, creature type, or challenge rating, and open any result for its full statistics and abilities.</p>\n"
        '<section class="monster-type-grid" aria-label="Featured creature types">'
        f"{featured}</section>"
        '<section><h2>Monster rules</h2><div class="monster-reference-grid">'
        f"{references}</div></section>"
        '<section class="monster-directory" id="monster-directory" data-monster-directory>'
        '<h2>Monster directory</h2><div class="monster-filters">'
        '<label>Monster name or keyword<input data-monster-search type="search" '
        'placeholder="Try: dragon, goblin, fire…"></label>'
        '<label>Creature type<select data-monster-type><option value="">All creature types</option>'
        f"{type_options}</select></label>"
        '<label>Challenge rating<select data-monster-cr><option value="">All challenge ratings</option>'
        '<option value="0-1">CR 1 or lower</option><option value="2-5">CR 2–5</option>'
        '<option value="6-10">CR 6–10</option><option value="11-15">CR 11–15</option>'
        '<option value="16+">CR 16+</option><option value="reference">Reference pages</option>'
        '</select></label><p data-monster-count aria-live="polite"></p></div>'
        + "".join(groups)
        + '</section><script src="/assets/monster-directory.js?v=1" defer></script>'
    )


def generate_monster_directory(public_dir=PUBLIC_DIR):
    """Generate `/monsters/` and return its indexed entry count."""

    entries = collect_monsters(public_dir)
    if public_dir == PUBLIC_DIR:
        write_page("monsters", "Monsters", build_monster_article(entries))
    return len(entries)


def main():
    count = generate_monster_directory()
    print(f"Created monster directory with {count} entries.")


if __name__ == "__main__":
    main()
