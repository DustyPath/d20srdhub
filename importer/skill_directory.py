"""Generate the complete, filterable skills landing page."""

import re
import unicodedata
from dataclasses import dataclass
from html import escape

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.writer import write_page

CATEGORIES = (
    ("Skill Rules", "rules", "Checks, ranks, modifiers, synergy, taking 10 or 20, and skill descriptions."),
    ("Strength Skills", "strength", "Physical power, climbing, jumping, and swimming."),
    ("Dexterity Skills", "dexterity", "Agility, balance, stealth, movement, riding, and manual precision."),
    ("Constitution Skills", "constitution", "Maintaining focus through injury, motion, weather, and distraction."),
    ("Intelligence Skills", "intelligence", "Appraisal, crafting, knowledge, searching, spellcraft, and technical tasks."),
    ("Wisdom Skills", "wisdom", "Awareness, intuition, healing, professions, perception, and survival."),
    ("Charisma Skills", "charisma", "Influence, deception, performance, intimidation, and social interaction."),
    ("Epic & Psionic Skills", "specialized", "Epic skill uses and the additional psionic skill system."),
)
GENERAL_SLUGS = {"using-skills", "skills-summary", "skill-descriptions"}
ABILITY_CATEGORIES = {
    "Str": "Strength Skills",
    "Dex": "Dexterity Skills",
    "Con": "Constitution Skills",
    "Int": "Intelligence Skills",
    "Wis": "Wisdom Skills",
    "Cha": "Charisma Skills",
}
SUPPLEMENTAL_PATHS = (
    "epic/skills",
    "psionic/skills/overview",
    "psionic/skills/autohypnosis",
    "psionic/skills/concentration",
    "psionic/skills/knowledge-psionics",
    "psionic/skills/psicraft",
    "psionic/skills/use-psionic-device",
)
HEADING_PATTERN = re.compile(
    r"<h(?P<level>[2-5])"
    r"(?P<attributes>(?![^>]*\bid=)[^>]*)>"
    r"(?P<contents>.*?)</h(?P=level)>",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class SkillPage:
    title: str
    output_path: str
    category: str


@dataclass(frozen=True)
class SkillTopic:
    name: str
    page: str
    category: str
    href: str


def heading_slug(value):
    """Return a stable URL-fragment slug."""

    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-") or "rule"


def add_heading_ids(page_file):
    """Add stable IDs to legacy skill subheadings that do not have them."""

    html = page_file.read_text(encoding="utf-8", errors="replace")
    used = set(re.findall(r'\bid=["\']([^"\']+)', html, re.IGNORECASE))

    def replace(match):
        text = BeautifulSoup(
            match.group("contents"),
            "html.parser",
        ).get_text(" ", strip=True)
        base = heading_slug(text)
        candidate = base
        suffix = 2

        while candidate in used:
            candidate = f"{base}-{suffix}"
            suffix += 1

        used.add(candidate)
        return (
            f'<h{match.group("level")} id="{candidate}"'
            f'{match.group("attributes")}>'
            f'{match.group("contents")}</h{match.group("level")}>'
        )

    updated = HEADING_PATTERN.sub(replace, html)

    if updated != html:
        page_file.write_text(updated, encoding="utf-8")

    return updated != html


def article_heading(page_file):
    """Return the first article heading from a generated page."""

    soup = BeautifulSoup(
        page_file.read_text(encoding="utf-8", errors="replace"),
        "html.parser",
    )
    article = soup.select_one(".article-card")
    heading = article.find(["h1", "h2"]) if article else None
    return heading.get_text(" ", strip=True) if heading else ""


def skill_category(title, output_path):
    """Classify a skill page by governing ability or rules family."""

    if not output_path.startswith("skills/"):
        return "Epic & Psionic Skills"

    if output_path.rsplit("/", 1)[-1] in GENERAL_SLUGS:
        return "Skill Rules"

    match = re.search(r"\((Str|Dex|Con|Int|Wis|Cha)\b", title)
    return ABILITY_CATEGORIES.get(
        match.group(1) if match else "",
        "Skill Rules",
    )


def collect_skill_pages(public_dir=PUBLIC_DIR):
    """Return every standard and specialized skill page."""

    pages = []
    skills_dir = public_dir / "skills"

    for page_file in sorted(skills_dir.glob("*/index.html")):
        output_path = page_file.parent.relative_to(public_dir).as_posix()
        title = article_heading(page_file)

        if title:
            pages.append(
                SkillPage(
                    title,
                    output_path,
                    skill_category(title, output_path),
                )
            )

    for output_path in SUPPLEMENTAL_PATHS:
        page_file = public_dir / output_path / "index.html"

        if page_file.exists():
            title = article_heading(page_file)
            pages.append(
                SkillPage(
                    title or output_path.rsplit("/", 1)[-1].title(),
                    output_path,
                    "Epic & Psionic Skills",
                )
            )

    return pages


def collect_page_topics(page_file, page):
    """Extract linked skill uses from one generated skill page."""

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

        href = f"/{page.output_path}/"

        if heading.get("id"):
            href += f"#{heading['id']}"

        topics.append(SkillTopic(name, page.title, page.category, href))

    return topics


def collect_skill_topics(public_dir=PUBLIC_DIR):
    """Return every linked heading in the skill rules."""

    topics = []

    for page in collect_skill_pages(public_dir):
        page_file = public_dir / page.output_path / "index.html"
        topics.extend(collect_page_topics(page_file, page))

    unique = {topic.href: topic for topic in topics}
    return sorted(
        unique.values(),
        key=lambda topic: (
            topic.category.casefold(),
            topic.page.casefold(),
            topic.name.casefold(),
        ),
    )


def build_skill_article(pages, topics):
    """Build the complete skill hub article."""

    category_cards = "\n".join(
        f'<a class="skill-category-card" href="#skill-{escape(slug)}">'
        f'<strong class="skill-category-title">{escape(title)}</strong>'
        f"<p>{escape(description)}</p></a>"
        for title, slug, description in CATEGORIES
    )
    category_options = "\n".join(
        f'<option value="{escape(title, quote=True)}">{escape(title)}</option>'
        for title, _slug, _description in CATEGORIES
    )
    page_sections = []
    topic_sections = []

    for category, slug, _description in CATEGORIES:
        category_pages = [page for page in pages if page.category == category]
        page_cards = "\n".join(
            f'<a class="skill-page-card" href="/{escape(page.output_path)}/">'
            f"<strong>{escape(page.title)}</strong>"
            f"<span>{escape(category)}</span></a>"
            for page in category_pages
        )
        page_sections.append(
            f'<section class="skill-page-group" id="skill-{escape(slug)}">'
            f"<h2>{escape(category)}</h2>"
            f'<div class="skill-page-grid">{page_cards}</div></section>'
        )
        entries = []

        for topic in topics:
            if topic.category != category:
                continue

            search_text = f"{topic.name} {topic.page}".casefold()
            entries.append(
                '<li data-skill-item '
                f'data-name="{escape(search_text, quote=True)}" '
                f'data-category="{escape(topic.category, quote=True)}">'
                f'<a href="{escape(topic.href, quote=True)}">'
                f"<strong>{escape(topic.name)}</strong>"
                f'<span class="skill-directory-meta">'
                f"{escape(topic.page)}</span></a></li>"
            )

        topic_sections.append(
            '<section class="skill-reference-group" data-skill-group>'
            f'<strong class="skill-reference-title">{escape(category)}</strong>'
            '<ul class="skill-directory-list">\n'
            + "\n".join(entries)
            + "\n</ul></section>"
        )

    return (
        "<h1>Skills</h1>\n"
        "<p>Browse every standard skill, general skill rules, individual "
        "skill uses, and specialized epic and psionic skill systems.</p>\n"
        '<section class="skill-category-grid" '
        'aria-label="Skill categories">\n'
        f"{category_cards}\n</section>\n"
        + "\n".join(page_sections)
        + "\n"
        '<section class="skill-directory" data-skill-directory '
        'aria-labelledby="skill-reference">\n'
        '<h2 id="skill-reference">Skill-use quick reference</h2>\n'
        '<div class="skill-filters">\n'
        '<label>Skill or use<input data-skill-search type="search" '
        'placeholder="Filter skills and uses…"></label>\n'
        '<label>Category<select data-skill-category>'
        '<option value="">All categories</option>\n'
        f"{category_options}</select></label>\n"
        '<p class="skill-result-count" data-skill-count '
        'aria-live="polite"></p>\n</div>\n'
        + "\n".join(topic_sections)
        + "\n</section>\n"
        '<script src="/assets/skill-directory.js?v=1" defer></script>'
    )


def generate_skill_directory(public_dir=PUBLIC_DIR):
    """Generate `/skills/` and return the indexed topic count."""

    pages = collect_skill_pages(public_dir)

    if public_dir == PUBLIC_DIR:
        for page in pages:
            add_heading_ids(public_dir / page.output_path / "index.html")

    topics = collect_skill_topics(public_dir)

    if public_dir == PUBLIC_DIR:
        write_page("skills", "Skills", build_skill_article(pages, topics))

    return len(pages), len(topics)


def main():
    page_count, topic_count = generate_skill_directory()
    print(
        f"Created skill directory with {page_count} rulebooks "
        f"and {topic_count} topics."
    )


if __name__ == "__main__":
    main()
