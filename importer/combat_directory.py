"""Generate the complete, filterable combat landing page."""

from dataclasses import dataclass
from html import escape

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.writer import write_page

CATEGORIES = (
    (
        "Combat Fundamentals",
        "fundamentals",
        "Rounds, initiative, attacks, damage, defenses, and the basic combat sequence.",
    ),
    (
        "Actions & Reactions",
        "actions",
        "Standard, move, full-round, free, readied, and opportunity actions.",
    ),
    (
        "Movement & Position",
        "movement",
        "Speed, terrain, cover, concealment, reach, and positioning.",
    ),
    (
        "Special Attacks & Injury",
        "advanced",
        "Combat maneuvers, modifiers, hit-point loss, dying, and recovery.",
    ),
)

PAGES = (
    ("How Combat Works", "how-combat-works", "Combat Fundamentals"),
    ("Initiative", "initiative", "Combat Fundamentals"),
    ("Combat Statistics", "combat-statistics", "Combat Fundamentals"),
    ("Actions in Combat", "actions-in-combat", "Actions & Reactions"),
    ("Attacks of Opportunity", "attacks-of-opportunity", "Actions & Reactions"),
    ("Special Initiative Actions", "special-initiative-actions", "Actions & Reactions"),
    ("Movement, Position, and Distance", "movement-position-and-distance", "Movement & Position"),
    ("Combat Modifiers", "combat-modifiers", "Movement & Position"),
    ("Special Attacks", "special-attacks", "Special Attacks & Injury"),
    ("Injury and Death", "injury-and-death", "Special Attacks & Injury"),
)


@dataclass(frozen=True)
class CombatTopic:
    name: str
    page: str
    category: str
    href: str


def collect_page_topics(page_file, page_title, category):
    """Extract linked rule headings from one generated combat page."""

    soup = BeautifulSoup(
        page_file.read_text(encoding="utf-8", errors="replace"),
        "html.parser",
    )
    article = soup.select_one(".article-card")
    topics = []

    if article is None:
        return topics

    for heading in article.find_all(["h1", "h2", "h3", "h4", "h5"]):
        name = heading.get_text(" ", strip=True)

        if not name:
            continue

        href = f"/combat/{page_file.parent.name}/"

        if heading.get("id"):
            href += f"#{heading['id']}"

        topics.append(CombatTopic(name, page_title, category, href))

    return topics


def collect_combat_topics(public_dir=PUBLIC_DIR):
    """Return the complete list of linked combat topics."""

    topics = []

    for title, slug, category in PAGES:
        page_file = public_dir / "combat" / slug / "index.html"

        if page_file.exists():
            topics.extend(collect_page_topics(page_file, title, category))

    unique = {topic.href: topic for topic in topics}
    return sorted(
        unique.values(),
        key=lambda topic: (
            topic.category.casefold(),
            topic.page.casefold(),
            topic.name.casefold(),
        ),
    )


def build_combat_article(topics):
    """Build the complete combat hub article."""

    category_cards = "\n".join(
        f'<a class="combat-category-card" href="#combat-{escape(slug)}">'
        f'<strong class="combat-category-title">{escape(title)}</strong>'
        f"<p>{escape(description)}</p></a>"
        for title, slug, description in CATEGORIES
    )
    category_options = "\n".join(
        f'<option value="{escape(title, quote=True)}">{escape(title)}</option>'
        for title, _slug, _description in CATEGORIES
    )
    page_cards = "\n".join(
        f'<a class="combat-page-card" href="/combat/{escape(slug)}/">'
        f"<strong>{escape(title)}</strong><span>{escape(category)}</span></a>"
        for title, slug, category in PAGES
    )
    groups = []

    for category, slug, _description in CATEGORIES:
        entries = []

        for topic in topics:
            if topic.category != category:
                continue

            search_text = f"{topic.name} {topic.page}".casefold()
            entries.append(
                '<li data-combat-item '
                f'data-name="{escape(search_text, quote=True)}" '
                f'data-category="{escape(topic.category, quote=True)}">'
                f'<a href="{escape(topic.href, quote=True)}">'
                f"<strong>{escape(topic.name)}</strong>"
                f'<span class="combat-directory-meta">'
                f"{escape(topic.page)}</span></a></li>"
            )

        groups.append(
            '<section class="combat-reference-group" data-combat-group '
            f'id="combat-{escape(slug)}"><h2>{escape(category)}</h2>'
            '<ul class="combat-directory-list">\n'
            + "\n".join(entries)
            + "\n</ul></section>"
        )

    return (
        "<h1>Combat</h1>\n"
        "<p>Find the complete combat rules for initiative, actions, attacks, "
        "movement, positioning, special maneuvers, damage, and recovery.</p>\n"
        '<section class="combat-category-grid" '
        'aria-label="Combat rule categories">\n'
        f"{category_cards}\n</section>\n"
        '<section aria-labelledby="combat-pages-heading">\n'
        '<h2 id="combat-pages-heading">Combat rulebooks</h2>\n'
        f'<div class="combat-page-grid">{page_cards}</div>\n</section>\n'
        '<section class="combat-directory" data-combat-directory '
        'aria-labelledby="combat-reference">\n'
        '<h2 id="combat-reference">Combat quick reference</h2>\n'
        '<div class="combat-filters">\n'
        '<label>Rule or topic<input data-combat-search type="search" '
        'placeholder="Filter combat rules…"></label>\n'
        '<label>Category<select data-combat-category>'
        '<option value="">All categories</option>\n'
        f"{category_options}</select></label>\n"
        '<p class="combat-result-count" data-combat-count '
        'aria-live="polite"></p>\n</div>\n'
        + "\n".join(groups)
        + "\n</section>\n"
        '<script src="/assets/combat-directory.js?v=1" defer></script>'
    )


def generate_combat_directory(public_dir=PUBLIC_DIR):
    """Generate `/combat/` and return the number of indexed topics."""

    topics = collect_combat_topics(public_dir)

    if public_dir == PUBLIC_DIR:
        write_page("combat", "Combat", build_combat_article(topics))

    return len(topics)


def main():
    count = generate_combat_directory()
    print(f"Created combat directory with {count} topics.")


if __name__ == "__main__":
    main()
