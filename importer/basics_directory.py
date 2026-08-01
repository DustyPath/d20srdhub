"""Generate the searchable Basics landing page."""

from html import escape

from importer.config import PUBLIC_DIR
from importer.rules_directories import build_directory_article, collect_page_set
from importer.writer import write_page


BASICS_GROUPS = (
    ("Core Mechanics", "mechanics", "Checks, dice, modifiers, rounding, and multiplication."),
    ("Ability Scores", "abilities", "Ability scores, modifiers, spellcasting, and the six abilities."),
    ("Character Details", "characters", "Alignment, age, height, weight, and other descriptive details."),
    ("Movement & Encumbrance", "movement", "Movement scales, pursuit, carrying capacity, and load limits."),
)

BASICS_PAGES = (
    ("The Basics", "the-basics", "Core Mechanics"),
    ("The Basics", "the-basics", "Ability Scores"),
    ("Character Description", "description", "Character Details"),
    ("Movement", "movement", "Movement & Encumbrance"),
    ("Carrying Capacity", "carrying-capacity", "Movement & Encumbrance"),
)

CHARACTER_LINKS = (
    ("Races", "/races/", "Traits, languages, favored classes, and playable ancestries."),
    ("Classes", "/classes/", "Core classes, advancement, class features, and prestige classes."),
    ("Skills", "/skills/", "Skill checks, modifiers, difficulty classes, and individual skills."),
    ("Feats", "/feats/", "Feat prerequisites, types, and complete descriptions."),
    ("Equipment", "/equipment/", "Weapons, armor, adventuring gear, services, and wealth."),
    ("Combat", "/combat/", "Initiative, actions, attacks, movement, injury, and recovery."),
)


def collect_basics_topics(public_dir=PUBLIC_DIR):
    """Collect the relevant headings and assign each to one Basics category."""

    mechanics = collect_page_set((BASICS_PAGES[0],), public_dir)
    ability_names = {
        "Ability Scores",
        "Ability Modifiers",
        "Abilities And Spellcasters",
        "The Abilities",
        "Strength (Str)",
        "Dexterity (Dex)",
        "Constitution (Con)",
        "Intelligence (Int)",
        "Wisdom (Wis)",
        "Charisma (Cha)",
    }

    topics = []
    for topic in mechanics:
        category = "Ability Scores" if topic.name in ability_names else "Core Mechanics"
        topics.append(type(topic)(topic.name, topic.page, category, topic.href))

    topics.extend(collect_page_set(BASICS_PAGES[2:], public_dir))
    unique = {topic.href: topic for topic in topics}
    return sorted(unique.values(), key=lambda item: (item.category, item.name.casefold()))


def build_basics_article(topics):
    """Build the complete Basics landing-page article."""

    character_cards = "".join(
        '<a class="rule-page-card" href="{}"><strong>{}</strong><span>{}</span></a>'.format(
            escape(href, quote=True), escape(name), escape(description)
        )
        for name, href, description in CHARACTER_LINKS
    )
    extras = (
        '<section aria-labelledby="character-building-heading">'
        '<h2 id="character-building-heading">Build a character</h2>'
        '<p>Continue from the core rules to the main character-building references.</p>'
        f'<div class="rule-page-grid">{character_cards}</div></section>'
    )

    page_links = (
        ("Core Mechanics & Abilities", "the-basics", "The foundational d20 rules"),
        ("Character Description", "description", "Alignment and vital statistics"),
        ("Movement", "movement", "Tactical, local, and overland movement"),
        ("Carrying Capacity", "carrying-capacity", "Loads, lifting, and encumbrance"),
    )
    return build_directory_article(
        "The Basics",
        "Start with the core d20 mechanic, dice and modifiers, ability scores, character details, movement, and carrying capacity.",
        BASICS_GROUPS,
        page_links,
        topics,
        "basics",
        extras,
    )


def generate_basics_directory(public_dir=PUBLIC_DIR):
    """Generate the Basics hub and return its searchable topic count."""

    topics = collect_basics_topics(public_dir)
    if public_dir == PUBLIC_DIR:
        write_page("basics", "The Basics", build_basics_article(topics))
    return len(topics)


def main():
    count = generate_basics_directory()
    print(f"Created the Basics directory with {count} searchable topics.")


if __name__ == "__main__":
    main()
