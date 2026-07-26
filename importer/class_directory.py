"""Generate the complete, filterable classes landing page."""

from dataclasses import dataclass
from html import escape

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.writer import write_page

CATEGORIES = (
    (
        "Core Classes",
        "core",
        "The standard adventuring classes, their progression, and class features.",
    ),
    (
        "Character Advancement",
        "advancement",
        "Multiclass characters, favored classes, experience, and advancement.",
    ),
    (
        "NPC Classes",
        "npc",
        "Adept, aristocrat, commoner, expert, and warrior class rules.",
    ),
    (
        "Prestige Classes",
        "prestige",
        "Specialized classes with prerequisites and advanced class features.",
    ),
)

CORE_PAGES = (
    ("Barbarian", "classes/barbarian"),
    ("Bard", "classes/bard"),
    ("Cleric", "classes/cleric"),
    ("Druid", "classes/druid"),
    ("Fighter", "classes/fighter"),
    ("Monk", "classes/monk"),
    ("Paladin", "classes/paladin"),
    ("Ranger", "classes/ranger"),
    ("Rogue", "classes/rogue"),
    ("Sorcerer & Wizard", "classes/sorcerer-wizard"),
)
ADVANCEMENT_PAGES = (("Multiclass Characters", "classes/multiclass"),)
NPC_PAGES = (
    ("Adept", "npc-classes/adept"),
    ("Aristocrat", "npc-classes/aristocrat"),
    ("Commoner", "npc-classes/commoner"),
    ("Expert", "npc-classes/expert"),
    ("Warrior", "npc-classes/warrior"),
)
PRESTIGE_PAGES = (
    ("Arcane Archer", "prestige-classes/arcane-archer"),
    ("Arcane Trickster", "prestige-classes/arcane-trickster"),
    ("Archmage", "prestige-classes/archmage"),
    ("Assassin", "prestige-classes/assassin"),
    ("Blackguard", "prestige-classes/blackguard"),
    ("Dragon Disciple", "prestige-classes/dragon-disciple"),
    ("Duelist", "prestige-classes/duelist"),
    ("Dwarven Defender", "prestige-classes/dwarven-defender"),
    ("Eldritch Knight", "prestige-classes/eldritch-knight"),
    ("Hierophant", "prestige-classes/hierophant"),
    ("Horizon Walker", "prestige-classes/horizon-walker"),
    ("Loremaster", "prestige-classes/loremaster"),
    ("Mystic Theurge", "prestige-classes/mystic-theurge"),
    ("Shadowdancer", "prestige-classes/shadowdancer"),
    ("Thaumaturgist", "prestige-classes/thaumaturgist"),
)
PAGE_GROUPS = (
    ("Core Classes", CORE_PAGES),
    ("Character Advancement", ADVANCEMENT_PAGES),
    ("NPC Classes", NPC_PAGES),
    ("Prestige Classes", PRESTIGE_PAGES),
)


@dataclass(frozen=True)
class ClassTopic:
    name: str
    page: str
    category: str
    href: str


def collect_page_topics(page_file, page_title, category, output_path):
    """Extract linked class features from one generated page."""

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

        href = f"/{output_path}/"

        if heading.get("id"):
            href += f"#{heading['id']}"

        topics.append(ClassTopic(name, page_title, category, href))

    return topics


def collect_class_topics(public_dir=PUBLIC_DIR):
    """Return linked class features across every class family."""

    topics = []

    for category, pages in PAGE_GROUPS:
        for title, output_path in pages:
            page_file = public_dir / output_path / "index.html"

            if page_file.exists():
                topics.extend(
                    collect_page_topics(
                        page_file,
                        title,
                        category,
                        output_path,
                    )
                )

    unique = {topic.href: topic for topic in topics}
    return sorted(
        unique.values(),
        key=lambda topic: (
            topic.category.casefold(),
            topic.page.casefold(),
            topic.name.casefold(),
        ),
    )


def build_class_article(topics):
    """Build the complete class hub article."""

    category_cards = "\n".join(
        f'<a class="class-category-card" href="#class-{escape(slug)}">'
        f'<strong class="class-category-title">{escape(title)}</strong>'
        f"<p>{escape(description)}</p></a>"
        for title, slug, description in CATEGORIES
    )
    category_options = "\n".join(
        f'<option value="{escape(title, quote=True)}">{escape(title)}</option>'
        for title, _slug, _description in CATEGORIES
    )
    page_sections = []
    topic_sections = []

    for category, pages in PAGE_GROUPS:
        slug = next(
            slug for title, slug, _description in CATEGORIES
            if title == category
        )
        page_cards = "\n".join(
            f'<a class="class-page-card" href="/{escape(output_path)}/">'
            f"<strong>{escape(title)}</strong>"
            f"<span>{escape(category)}</span></a>"
            for title, output_path in pages
        )
        page_sections.append(
            f'<section class="class-page-group" id="class-{escape(slug)}">'
            f"<h2>{escape(category)}</h2>"
            f'<div class="class-page-grid">{page_cards}</div></section>'
        )
        entries = []

        for topic in topics:
            if topic.category != category:
                continue

            search_text = f"{topic.name} {topic.page}".casefold()
            entries.append(
                '<li data-class-item '
                f'data-name="{escape(search_text, quote=True)}" '
                f'data-category="{escape(topic.category, quote=True)}">'
                f'<a href="{escape(topic.href, quote=True)}">'
                f"<strong>{escape(topic.name)}</strong>"
                f'<span class="class-directory-meta">'
                f"{escape(topic.page)}</span></a></li>"
            )

        topic_sections.append(
            '<section class="class-reference-group" data-class-group>'
            f'<strong class="class-reference-title">{escape(category)}</strong>'
            '<ul class="class-directory-list">\n'
            + "\n".join(entries)
            + "\n</ul></section>"
        )

    return (
        "<h1>Classes</h1>\n"
        "<p>Browse core classes, multiclass rules, NPC classes, prestige "
        "classes, progression tables, and individual class features.</p>\n"
        '<section class="class-category-grid" '
        'aria-label="Class categories">\n'
        f"{category_cards}\n</section>\n"
        + "\n".join(page_sections)
        + "\n"
        '<section class="class-directory" data-class-directory '
        'aria-labelledby="class-reference">\n'
        '<h2 id="class-reference">Class feature quick reference</h2>\n'
        '<div class="class-filters">\n'
        '<label>Class or feature<input data-class-search type="search" '
        'placeholder="Filter classes and features…"></label>\n'
        '<label>Category<select data-class-category>'
        '<option value="">All categories</option>\n'
        f"{category_options}</select></label>\n"
        '<p class="class-result-count" data-class-count '
        'aria-live="polite"></p>\n</div>\n'
        + "\n".join(topic_sections)
        + "\n</section>\n"
        '<script src="/assets/class-directory.js?v=1" defer></script>'
    )


def generate_class_directory(public_dir=PUBLIC_DIR):
    """Generate `/classes/` and return the number of indexed features."""

    topics = collect_class_topics(public_dir)

    if public_dir == PUBLIC_DIR:
        write_page("classes", "Classes", build_class_article(topics))

    return len(topics)


def main():
    count = generate_class_directory()
    print(f"Created class directory with {count} features.")


if __name__ == "__main__":
    main()
