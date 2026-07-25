"""Generate landing pages for linked SRD section directories."""

from html import escape
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.writer import write_page

SPECIAL_LABELS = {
    "epic": "Epic Rules",
    "magic-items": "Magic Items",
    "magic-overview": "Magic Overview",
    "npc-classes": "NPC Classes",
    "prestige-classes": "Prestige Classes",
    "psionic": "Psionics",
    "spell-lists": "Spell Lists",
    "variant": "Variant Rules",
}


def section_label(slug):
    """Return a readable label for a section slug."""

    return SPECIAL_LABELS.get(slug, slug.replace("-", " ").title())


def linked_section_paths(public_dir=PUBLIC_DIR):
    """Return linked local directories that need an index page."""

    sections = set()

    for page_file in public_dir.rglob("*.html"):
        soup = BeautifulSoup(
            page_file.read_text(encoding="utf-8", errors="replace"),
            "html.parser",
        )

        for anchor in soup.find_all("a", href=True):
            path = urlsplit(anchor["href"]).path

            if not path.startswith("/") or not path.endswith("/"):
                continue

            output_path = path.strip("/")

            if not output_path:
                continue

            directory = public_dir / output_path

            if directory.is_dir() and not (directory / "index.html").exists():
                sections.add(output_path)

    return sorted(sections, key=lambda path: (path.count("/"), path))


def child_pages(output_path, public_dir=PUBLIC_DIR):
    """Return immediate child pages for a section."""

    section_dir = public_dir / output_path
    children = []

    for child in sorted(section_dir.iterdir()):
        index_file = child / "index.html"

        if child.is_dir() and (
            index_file.exists() or any(child.rglob("index.html"))
        ):
            children.append((child.name, section_label(child.name)))

    return children


def build_section_article(output_path, children):
    """Build the article HTML for one section landing page."""

    title = section_label(Path(output_path).name)
    items = "\n".join(
        f'  <li><a href="/{escape(output_path)}/{escape(slug)}/">'
        f"{escape(label)}</a></li>"
        for slug, label in children
    )

    return title, (
        f"<h1>{escape(title)}</h1>\n"
        "<p>Browse the rules pages in this section.</p>\n"
        f'<ul class="section-index">\n{items}\n</ul>'
    )


def generate_section_indexes(public_dir=PUBLIC_DIR):
    """Create every linked section index that is currently missing."""

    created = []

    for output_path in linked_section_paths(public_dir):
        children = child_pages(output_path, public_dir)

        if not children:
            continue

        title, article = build_section_article(output_path, children)
        write_page(output_path, title, article)
        created.append(output_path)

    return created


def main():
    created = generate_section_indexes()

    print(f"Created {len(created)} section indexes.")

    for output_path in created:
        print(f"- /{output_path}/")


if __name__ == "__main__":
    main()
