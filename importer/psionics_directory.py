"""Generate the complete, filterable Psionics landing page."""

from dataclasses import dataclass
from html import escape
import re

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.writer import write_page


DISCIPLINES = (
    "Clairsentience",
    "Metacreativity",
    "Psychokinesis",
    "Psychometabolism",
    "Psychoportation",
    "Telepathy",
)

REFERENCE_CARDS = (
    ("Psionic Rules", "/psionic/psionic-powers-overview/", "Manifesting powers, displays, power resistance, and psionic disciplines."),
    ("Power Lists", "/psionic/power-list/", "Powers by manifester class, discipline, and level."),
    ("Psionic Feats", "/psionic/psionic-feats/", "General, metapsionic, and psionic feat descriptions."),
    ("Psionic Races", "/psionic/psionic-races/", "Racial traits and psionic character options."),
)

LIBRARY_CARDS = (
    ("Psionic Classes", "/psionic/classes/", "Psion, psychic warrior, soulknife, and wilder."),
    ("Prestige Classes", "/psionic/prestige-classes/", "Advanced psionic paths and their class features."),
    ("Psionic Skills", "/psionic/skills/", "Autohypnosis, Psicraft, and other psionic skill rules."),
    ("Psionic Items", "/psionic/items/", "Dorjes, power stones, psicrowns, weapons, armor, and artifacts."),
    ("Psionic Monsters", "/psionic/monsters/", "Psionic creatures and complete statistics."),
)


@dataclass(frozen=True)
class PowerEntry:
    name: str
    href: str
    discipline: str
    levels: tuple[str, ...]
    level_text: str
    letter: str


def _power_levels(level_text):
    """Return every power level found in a power's level entry."""

    levels = sorted({match for match in re.findall(r"\b[0-9]\b", level_text)})
    return tuple(levels)


def parse_power_page(page_file, public_dir=PUBLIC_DIR):
    """Extract directory metadata from one generated psionic power page."""

    soup = BeautifulSoup(
        page_file.read_text(encoding="utf-8", errors="replace"),
        "html.parser",
    )
    article = soup.select_one(".article-card")
    if article is None:
        return None

    heading = article.find("h1")
    if heading is None:
        return None

    name = heading.get_text(" ", strip=True)
    discipline_heading = article.find("h4")
    discipline_text = discipline_heading.get_text(" ", strip=True) if discipline_heading else ""
    discipline = next(
        (item for item in DISCIPLINES if item.casefold() in discipline_text.casefold()),
        "Other",
    )
    if discipline == "Other" and "psychokinetic" in discipline_text.casefold():
        discipline = "Psychokinesis"

    level_text = ""
    for row in article.select("table tr"):
        header = row.find("th")
        value = row.find("td")
        header_text = header.get_text(" ", strip=True).rstrip(":").strip() if header else ""
        if value and header_text.casefold() == "level":
            level_text = value.get_text(" ", strip=True)
            break

    href = "/" + page_file.parent.relative_to(public_dir).as_posix() + "/"
    letter = name[0].upper() if name and name[0].isalpha() else "#"
    return PowerEntry(name, href, discipline, _power_levels(level_text), level_text, letter)


def collect_powers(public_dir=PUBLIC_DIR):
    """Return every imported psionic power with filter metadata."""

    entries = []
    for page_file in (public_dir / "psionic" / "powers").glob("*/index.html"):
        entry = parse_power_page(page_file, public_dir)
        if entry is not None:
            entries.append(entry)
    return sorted(entries, key=lambda item: item.name.casefold())


def _cards(cards, class_name):
    return "".join(
        f'<a class="{class_name}" href="{escape(href, quote=True)}">'
        f"<strong>{escape(title)}</strong><span>{escape(description)}</span></a>"
        for title, href, description in cards
    )


def build_psionics_article(entries):
    """Build the Psionics hub and filterable power directory."""

    disciplines = sorted({entry.discipline for entry in entries})
    discipline_options = "".join(
        f'<option value="{escape(value, quote=True)}">{escape(value)}</option>'
        for value in disciplines
    )
    groups = []
    for letter in sorted({entry.letter for entry in entries}):
        items = []
        for entry in entries:
            if entry.letter != letter:
                continue
            levels = " ".join(entry.levels)
            metadata = entry.discipline
            if entry.level_text:
                metadata += f" · {entry.level_text}"
            search_text = f"{entry.name} {entry.discipline} {entry.level_text}".casefold()
            items.append(
                '<li data-power-item '
                f'data-name="{escape(search_text, quote=True)}" '
                f'data-discipline="{escape(entry.discipline, quote=True)}" '
                f'data-levels="{escape(levels, quote=True)}">'
                f'<a href="{escape(entry.href, quote=True)}"><strong>{escape(entry.name)}</strong>'
                f"<span>{escape(metadata)}</span></a></li>"
            )
        groups.append(
            f'<section class="power-letter-group" data-power-group id="powers-{escape(letter.lower())}">'
            f'<h2>{escape(letter)}</h2><ul class="power-directory-list">'
            + "\n".join(items)
            + "</ul></section>"
        )

    return (
        "<h1>Psionics</h1>\n"
        "<p>Explore the complete SRD psionics system: manifesters, powers, disciplines, feats, skills, items, races, and creatures.</p>"
        '<section aria-labelledby="psionic-rules-heading"><h2 id="psionic-rules-heading">Start with the rules</h2>'
        '<div class="psionic-reference-grid">'
        + _cards(REFERENCE_CARDS, "psionic-reference-card")
        + "</div></section>"
        '<section aria-labelledby="psionic-library-heading"><h2 id="psionic-library-heading">Characters and equipment</h2>'
        '<div class="psionic-library-grid">'
        + _cards(LIBRARY_CARDS, "psionic-library-card")
        + "</div></section>"
        '<section class="power-directory" id="power-directory" data-power-directory>'
        '<h2>Power directory</h2><p>Search all imported psionic powers and narrow the results by discipline or power level.</p>'
        '<div class="power-filters"><label>Power name or keyword'
        '<input data-power-search type="search" placeholder="Try: energy, teleport, mind…"></label>'
        '<label>Discipline<select data-power-discipline><option value="">All disciplines</option>'
        + discipline_options
        + '</select></label><label>Level<select data-power-level><option value="">All levels</option>'
        + "".join(f'<option value="{level}">Level {level}</option>' for level in map(str, range(1, 10)))
        + '</select></label><p data-power-count aria-live="polite"></p></div>'
        + "".join(groups)
        + '</section><script src="/assets/psionics-directory.js?v=1" defer></script>'
    )


def generate_psionics_directory(public_dir=PUBLIC_DIR):
    """Generate `/psionics/` and return its indexed power count."""

    entries = collect_powers(public_dir)
    if public_dir == PUBLIC_DIR:
        write_page("psionics", "Psionics", build_psionics_article(entries))
    return len(entries)


def main():
    count = generate_psionics_directory()
    print(f"Created the Psionics directory with {count} searchable powers.")


if __name__ == "__main__":
    main()
