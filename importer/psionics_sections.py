"""Build dedicated class, prestige class, feat, and power Psionics tabs."""

from dataclasses import dataclass
from html import escape
import re

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.psionics_directory import build_power_directory, collect_powers
from importer.writer import write_page


@dataclass(frozen=True)
class PageEntry:
    name: str
    href: str
    summary: str


@dataclass(frozen=True)
class FeatEntry:
    name: str
    href: str
    feat_type: str


def content_tabs(active):
    """Return navigation shared by all dedicated Psionics pages."""

    tabs = (
        ("Overview", "/psionics/"),
        ("Character Classes", "/psionics/character-classes/"),
        ("Prestige Classes", "/psionics/prestige-classes/"),
        ("Feats", "/psionics/feats/"),
        ("Powers", "/psionics/powers/"),
    )
    links = []
    for label, href in tabs:
        current = ' aria-current="page"' if label == active else ""
        links.append(f'<a href="{href}"{current}>{label}</a>')
    return (
        '<nav class="psionics-content-tabs" aria-label="Psionics content">'
        + "".join(links)
        + "</nav>"
    )


def _summary(article):
    paragraph = article.find("p")
    if paragraph is None:
        return "Open the complete class description and advancement rules."
    text = " ".join(paragraph.get_text(" ", strip=True).split())
    if len(text) > 180:
        text = text[:177].rsplit(" ", 1)[0] + "..."
    return text


def collect_pages(section, public_dir=PUBLIC_DIR):
    """Collect immediate class pages from an imported Psionics section."""

    entries = []
    section_dir = public_dir / "psionic" / section
    for page_file in section_dir.glob("*/index.html"):
        if page_file.parent.name == "index":
            continue
        soup = BeautifulSoup(page_file.read_text(encoding="utf-8"), "html.parser")
        article = soup.select_one(".article-card")
        heading = article.find("h1") if article else None
        if heading is None:
            continue
        href = "/" + page_file.parent.relative_to(public_dir).as_posix() + "/"
        entries.append(PageEntry(heading.get_text(" ", strip=True), href, _summary(article)))
    return sorted(entries, key=lambda entry: entry.name.casefold())


def collect_feats(public_dir=PUBLIC_DIR):
    """Collect feat headings and anchors from the imported feat chapter."""

    page_file = public_dir / "psionic" / "psionic-feats" / "index.html"
    soup = BeautifulSoup(page_file.read_text(encoding="utf-8"), "html.parser")
    article = soup.select_one(".article-card")
    entries = []
    in_descriptions = False
    for heading in article.find_all(["h2", "h3"]):
        if heading.name == "h2":
            in_descriptions = heading.get("id") == "featDescriptions"
            continue
        if not in_descriptions or not heading.get("id"):
            continue
        name = heading.get_text(" ", strip=True)
        match = re.search(r"\[([^]]+)\]\s*$", name)
        feat_type = match.group(1) if match else "Other"
        entries.append(
            FeatEntry(name, f"/psionic/psionic-feats/#{heading['id']}", feat_type)
        )
    return sorted(entries, key=lambda entry: entry.name.casefold())


def build_page_cards(title, introduction, active, entries):
    """Build a dedicated class-card page."""

    cards = "".join(
        '<a class="psionic-section-card" href="{}"><strong>{}</strong><span>{}</span></a>'.format(
            escape(entry.href, quote=True), escape(entry.name), escape(entry.summary)
        )
        for entry in entries
    )
    return (
        f"<h1>{escape(title)}</h1><p>{escape(introduction)}</p>"
        + content_tabs(active)
        + f'<div class="psionic-section-grid">{cards}</div>'
    )


def build_feats_article(entries):
    """Build the searchable, type-filtered Psionics feat page."""

    types = sorted({entry.feat_type for entry in entries})
    options = "".join(f'<option value="{escape(value)}">{escape(value)}</option>' for value in types)
    items = "".join(
        '<li data-psionic-feat data-name="{}" data-type="{}"><a href="{}">'
        '<strong>{}</strong><span>{}</span></a></li>'.format(
            escape(entry.name.casefold(), quote=True),
            escape(entry.feat_type, quote=True),
            escape(entry.href, quote=True),
            escape(entry.name),
            escape(entry.feat_type),
        )
        for entry in entries
    )
    return (
        "<h1>Psionic Feats</h1><p>Search the complete feat chapter and open any result at its full description.</p>"
        + content_tabs("Feats")
        + '<section data-psionic-feat-directory><div class="psionic-feat-filters">'
        '<label>Feat name<input type="search" data-psionic-feat-search placeholder="Try: power, crystal, mind..."></label>'
        '<label>Feat type<select data-psionic-feat-type><option value="">All feat types</option>'
        + options
        + '</select></label><p data-psionic-feat-count aria-live="polite"></p></div>'
        f'<ul class="psionic-feat-list">{items}</ul></section>'
        '<script src="/assets/psionics-feats.js?v=1" defer></script>'
    )


def generate_psionics_sections(public_dir=PUBLIC_DIR):
    """Generate all four dedicated Psionics content tabs."""

    character_classes = collect_pages("classes", public_dir)
    prestige_classes = collect_pages("prestige-classes", public_dir)
    feats = collect_feats(public_dir)
    powers = collect_powers(public_dir)
    if public_dir == PUBLIC_DIR:
        write_page(
            "psionics/character-classes",
            "Psionic Character Classes",
            build_page_cards(
                "Psionic Character Classes",
                "Choose a core psionic class and open its complete advancement table, class features, and powers.",
                "Character Classes",
                character_classes,
            ),
        )
        write_page(
            "psionics/prestige-classes",
            "Psionic Prestige Classes",
            build_page_cards(
                "Psionic Prestige Classes",
                "Explore advanced psionic paths, requirements, advancement, and class features.",
                "Prestige Classes",
                prestige_classes,
            ),
        )
        write_page("psionics/feats", "Psionic Feats", build_feats_article(feats))
        write_page(
            "psionics/powers",
            "Psionic Powers",
            "<h1>Psionic Powers</h1><p>Search the full power collection by name, discipline, or level.</p>"
            + content_tabs("Powers")
            + build_power_directory(powers),
        )
    return {
        "character_classes": len(character_classes),
        "prestige_classes": len(prestige_classes),
        "feats": len(feats),
        "powers": len(powers),
    }


def main():
    counts = generate_psionics_sections()
    print(
        "Created dedicated Psionics tabs: "
        f"{counts['character_classes']} character classes, "
        f"{counts['prestige_classes']} prestige classes, "
        f"{counts['feats']} feats, and {counts['powers']} powers."
    )


if __name__ == "__main__":
    main()
