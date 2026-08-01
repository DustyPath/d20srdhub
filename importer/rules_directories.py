"""Generate the Magic, Magic Items, and Conditions landing pages."""

from dataclasses import dataclass
from html import escape

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.writer import write_page


MAGIC_GROUPS = (
    ("Foundations", "foundations", "Core concepts, spell schools, and how magic works."),
    ("Casting Spells", "casting", "Choosing, casting, countering, and resolving spells."),
    ("Magical Traditions", "traditions", "Preparing and learning arcane and divine magic."),
    ("Spell Reference", "reference", "Spell anatomy, lists, and individual descriptions."),
)

MAGIC_PAGES = (
    ("Magic Overview", "magic-overview/magic-overview", "Foundations"),
    ("Casting Spells", "magic-overview/casting-spells", "Casting Spells"),
    ("Arcane Spells", "magic-overview/arcane-spells", "Magical Traditions"),
    ("Divine Spells", "magic-overview/divine-spells", "Magical Traditions"),
    ("Spell Descriptions", "magic-overview/spell-descriptions", "Spell Reference"),
)

ITEM_GROUPS = (
    ("Using Magic Items", "basics", "Activation, body slots, saving throws, damage, and charges."),
    ("Weapons & Armor", "arms", "Magic weapons, armor, shields, and special abilities."),
    ("Charged & Consumable Items", "consumables", "Potions, scrolls, wands, and staffs."),
    ("Permanent Items", "permanent", "Rings, rods, and wondrous items."),
    ("Special Items", "special", "Intelligent, cursed, and artifact-level items."),
    ("Item Creation", "creation", "Creation prerequisites, costs, values, and procedures."),
)

ITEM_PAGES = (
    ("Magic Item Basics", "magic-item-basics", "Using Magic Items"),
    ("Magic Armor", "magic-armor", "Weapons & Armor"),
    ("Magic Weapons", "magic-weapons", "Weapons & Armor"),
    ("Potions and Oils", "potions-and-oils", "Charged & Consumable Items"),
    ("Scrolls", "scrolls", "Charged & Consumable Items"),
    ("Wands", "wands", "Charged & Consumable Items"),
    ("Staffs", "staffs", "Charged & Consumable Items"),
    ("Rings", "rings", "Permanent Items"),
    ("Rods", "rods", "Permanent Items"),
    ("Wondrous Items", "wondrous-items", "Permanent Items"),
    ("Intelligent Items", "intelligent-items", "Special Items"),
    ("Cursed Items", "cursed-items", "Special Items"),
    ("Artifacts", "artifacts", "Special Items"),
    ("Creating Magic Items", "creating-magic-items", "Item Creation"),
)

CONDITION_GROUPS = (
    ("Ability & Energy", "ability", "Ability damage, drain, and negative levels."),
    ("Awareness & Senses", "senses", "Sight, hearing, visibility, and awareness."),
    ("Actions & Movement", "actions", "Conditions that restrict actions, speed, or positioning."),
    ("Fear & Mental States", "mental", "Fear, confusion, fascination, and related effects."),
    ("Health & Survival", "health", "Injury, fatigue, dying, and death."),
    ("Restraint & Vulnerability", "restraint", "Conditions that bind, immobilize, or expose a creature."),
)

CONDITION_CATEGORIES = {
    "Ability Damaged": "Ability & Energy",
    "Ability Drained": "Ability & Energy",
    "Energy Drained": "Ability & Energy",
    "Blinded": "Awareness & Senses",
    "Dazzled": "Awareness & Senses",
    "Deafened": "Awareness & Senses",
    "Invisible": "Awareness & Senses",
    "Blown Away": "Actions & Movement",
    "Checked": "Actions & Movement",
    "Dazed": "Actions & Movement",
    "Knocked Down": "Actions & Movement",
    "Staggered": "Actions & Movement",
    "Confused": "Fear & Mental States",
    "Cowering": "Fear & Mental States",
    "Fascinated": "Fear & Mental States",
    "Frightened": "Fear & Mental States",
    "Panicked": "Fear & Mental States",
    "Shaken": "Fear & Mental States",
    "Dead": "Health & Survival",
    "Disabled": "Health & Survival",
    "Dying": "Health & Survival",
    "Exhausted": "Health & Survival",
    "Fatigued": "Health & Survival",
    "Nauseated": "Health & Survival",
    "Sickened": "Health & Survival",
    "Stable": "Health & Survival",
    "Entangled": "Restraint & Vulnerability",
    "Flat-Footed": "Restraint & Vulnerability",
    "Grappling": "Restraint & Vulnerability",
    "Helpless": "Restraint & Vulnerability",
    "Incorporeal": "Restraint & Vulnerability",
    "Paralyzed": "Restraint & Vulnerability",
    "Petrified": "Restraint & Vulnerability",
    "Pinned": "Restraint & Vulnerability",
    "Prone": "Restraint & Vulnerability",
    "Squeezing": "Restraint & Vulnerability",
    "Stunned": "Restraint & Vulnerability",
    "Turned": "Actions & Movement",
    "Unconscious": "Restraint & Vulnerability",
}


@dataclass(frozen=True)
class RuleTopic:
    name: str
    page: str
    category: str
    href: str


def collect_topics(page_file, page_title, category, public_path):
    """Extract linked headings from an existing generated rules page."""

    soup = BeautifulSoup(page_file.read_text(encoding="utf-8", errors="replace"), "html.parser")
    article = soup.select_one(".article-card")
    topics = []

    if article is None:
        return topics

    for heading in article.find_all(["h1", "h2", "h3", "h4"]):
        name = heading.get_text(" ", strip=True)
        if not name:
            continue
        href = f"/{public_path}/"
        if heading.get("id"):
            href += f"#{heading['id']}"
        topics.append(RuleTopic(name, page_title, category, href))

    return topics


def collect_page_set(pages, public_dir=PUBLIC_DIR, root=""):
    """Collect topics for a configured set of section pages."""

    topics = []
    for title, path, category in pages:
        public_path = f"{root}/{path}".strip("/")
        page_file = public_dir / public_path / "index.html"
        if page_file.exists():
            topics.extend(collect_topics(page_file, title, category, public_path))
    unique = {topic.href: topic for topic in topics}
    return sorted(unique.values(), key=lambda item: (item.category, item.page, item.name))


def collect_conditions(public_dir=PUBLIC_DIR):
    """Collect every condition heading from the SRD condition summary."""

    page_file = public_dir / "condition-summary" / "index.html"
    topics = collect_topics(page_file, "Condition Summary", "", "condition-summary")
    results = []
    for topic in topics:
        if topic.name == "Condition Summary":
            continue
        category = CONDITION_CATEGORIES.get(topic.name, "Actions & Movement")
        results.append(RuleTopic(topic.name, topic.page, category, topic.href))
    return sorted(results, key=lambda item: item.name.casefold())


def build_directory_article(title, introduction, groups, page_links, topics, prefix, extras=""):
    """Build a shared filterable rules-directory article."""

    cards = "\n".join(
        f'<a class="rule-category-card" href="#{escape(prefix)}-{escape(slug)}">'
        f"<strong>{escape(name)}</strong><p>{escape(description)}</p></a>"
        for name, slug, description in groups
    )
    pages = "\n".join(
        f'<a class="rule-page-card" href="/{escape(path)}/">'
        f"<strong>{escape(name)}</strong><span>{escape(category)}</span></a>"
        for name, path, category in page_links
    )
    options = "\n".join(
        f'<option value="{escape(name, quote=True)}">{escape(name)}</option>'
        for name, _slug, _description in groups
    )
    sections = []
    for category, slug, _description in groups:
        entries = []
        for topic in topics:
            if topic.category != category:
                continue
            search_text = f"{topic.name} {topic.page} {topic.category}".casefold()
            entries.append(
                '<li data-rule-item '
                f'data-name="{escape(search_text, quote=True)}" '
                f'data-category="{escape(category, quote=True)}">'
                f'<a href="{escape(topic.href, quote=True)}"><strong>{escape(topic.name)}</strong>'
                f'<span>{escape(topic.page)}</span></a></li>'
            )
        sections.append(
            f'<section class="rule-reference-group" data-rule-group id="{escape(prefix)}-{escape(slug)}">'
            f'<h2>{escape(category)}</h2><ul class="rule-directory-list">'
            + "\n".join(entries)
            + "</ul></section>"
        )

    return (
        f"<h1>{escape(title)}</h1>\n<p>{escape(introduction)}</p>\n"
        f'<section class="rule-category-grid" aria-label="{escape(title)} categories">{cards}</section>'
        + (f'<section><h2>Rulebooks</h2><div class="rule-page-grid">{pages}</div></section>' if pages else "")
        + extras
        + '<section class="rule-directory" data-rule-directory><h2>Quick reference</h2>'
        '<div class="rule-filters"><label>Rule or topic<input data-rule-search type="search" '
        f'placeholder="Filter {escape(title.lower())}…"></label>'
        '<label>Category<select data-rule-category><option value="">All categories</option>'
        f'{options}</select></label><p data-rule-count aria-live="polite"></p></div>'
        + "".join(sections)
        + '</section><script src="/assets/rule-directory.js?v=1" defer></script>'
    )


def build_magic_article(topics):
    extras = (
        '<aside class="rule-callout"><strong>Looking for a spell?</strong>'
        '<p>Browse individual spells or filter them by class, school, and level.</p>'
        '<a href="/spells/">Open the spell directory →</a></aside>'
    )
    return build_directory_article(
        "Magic",
        "Learn how spells are prepared, cast, resisted, countered, and described, then continue to the complete spell directory.",
        MAGIC_GROUPS,
        MAGIC_PAGES,
        topics,
        "magic",
        extras,
    )


def build_magic_items_article(topics):
    pages = tuple((title, f"magic-items/{slug}", category) for title, slug, category in ITEM_PAGES)
    return build_directory_article(
        "Magic Items",
        "Browse rules for using, identifying, creating, and selecting magic armor, weapons, consumables, permanent items, intelligent items, cursed items, and artifacts.",
        ITEM_GROUPS,
        pages,
        topics,
        "items",
    )


def build_conditions_article(topics):
    return build_directory_article(
        "Conditions",
        "Quickly find the mechanical effects of common character and creature conditions.",
        CONDITION_GROUPS,
        (),
        topics,
        "conditions",
        '<p class="rule-source-link"><a href="/condition-summary/">Read the complete condition summary →</a></p>',
    )


def generate_rules_directories(public_dir=PUBLIC_DIR):
    """Generate all three completed rules hubs."""

    magic_topics = collect_page_set(MAGIC_PAGES, public_dir)
    item_topics = collect_page_set(ITEM_PAGES, public_dir, "magic-items")
    condition_topics = collect_conditions(public_dir)

    if public_dir == PUBLIC_DIR:
        write_page("magic", "Magic", build_magic_article(magic_topics))
        write_page("magic-items", "Magic Items", build_magic_items_article(item_topics))
        write_page("conditions", "Conditions", build_conditions_article(condition_topics))

    return len(magic_topics), len(item_topics), len(condition_topics)


def main():
    magic, items, conditions = generate_rules_directories()
    print(f"Created Magic ({magic}), Magic Items ({items}), and Conditions ({conditions}) directories.")


if __name__ == "__main__":
    main()
