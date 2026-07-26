from html import escape

from importer.writer import write_page

CATEGORIES = {
    "classes": (
        "Classes",
        "Core classes, class features, advancement, and related rules.",
    ),
    "races": (
        "Races",
        "Racial traits, movement, size, languages, and favored classes.",
    ),
    "skills": (
        "Skills",
        "Skill descriptions, checks, modifiers, and common uses.",
    ),
    "feats": (
        "Feats",
        "General, item creation, metamagic, and special feats.",
    ),
    "spells": (
        "Spells",
        "Spell lists, schools, components, durations, and descriptions.",
    ),
    "monsters": (
        "Monsters",
        "Creature statistics, types, abilities, and encounter information.",
    ),
    "equipment": (
        "Equipment",
        "Weapons, armor, adventuring gear, services, and vehicles.",
    ),
    "magic-items": (
        "Magic Items",
        "Magic-item categories, creation rules, properties, and descriptions.",
    ),
    "combat": (
        "Combat",
        "Initiative, actions, attacks, movement, damage, and conditions.",
    ),
    "basics": (
        "The Basics",
        "Core rules for characters, checks, modifiers, and gameplay.",
    ),
    "adventuring": (
        "Adventuring",
        "Movement, exploration, environments, hazards, and travel.",
    ),
    "magic": (
        "Magic",
        "General spellcasting rules, schools, components, and effects.",
    ),
    "special-abilities": (
        "Special Abilities",
        "Extraordinary, supernatural, spell-like, and related abilities.",
    ),
    "conditions": (
        "Conditions",
        "Descriptions and effects of common character conditions.",
    ),
    "epic": (
        "Epic Rules",
        "Rules and options for characters beyond standard levels.",
    ),
    "psionics": (
        "Psionics",
        "Psionic characters, powers, combat, and related systems.",
    ),
}


def create_category_page(slug: str, title: str, description: str) -> None:
    article = (
        f"<h1>{escape(title)}</h1>\n"
        f"<p>{escape(description)}</p>\n"
        '<div class="notice">\n'
        "  <strong>Section status:</strong> "
        "Browse this section using the navigation and linked rules pages.\n"
        "</div>"
    )
    write_page(slug, title, article)


def main() -> None:
    for slug, (title, description) in CATEGORIES.items():
        create_category_page(slug, title, description)

    print("\nAll category pages were created successfully.")


if __name__ == "__main__":
    main()
