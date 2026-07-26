"""Move legacy standalone pages onto the shared site template."""

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.writer import write_page

LEGACY_PATHS = (
    "adventuring",
    "basics",
    "classes",
    "combat",
    "combat/injuryand-death",
    "conditions",
    "epic",
    "legal",
    "magic",
    "magic-items",
    "monsters",
    "psionics",
    "skills",
)


def extract_article(page_html):
    """Return the meaningful main content from a standalone legacy page."""

    soup = BeautifulSoup(page_html, "html.parser")
    main = soup.find("main")

    if main is None:
        raise ValueError("Legacy page does not contain a <main> element")

    if main.find("h1") is None:
        first_heading = main.find(["h2", "h3"])

        if first_heading is not None:
            first_heading.name = "h1"

    return main.decode_contents().strip()


def page_title(article_html, fallback):
    """Read a migrated article title from its first heading."""

    soup = BeautifulSoup(article_html, "html.parser")
    heading = soup.find(["h1", "h2", "h3"])
    return heading.get_text(" ", strip=True) if heading else fallback


def migrate_pages(public_dir=PUBLIC_DIR, paths=LEGACY_PATHS):
    """Rewrite selected legacy pages with the shared template."""

    migrated = []

    for output_path in paths:
        page_file = public_dir / output_path / "index.html"

        if not page_file.exists():
            continue

        article = extract_article(page_file.read_text(encoding="utf-8"))
        fallback = output_path.rsplit("/", 1)[-1].replace("-", " ").title()
        write_page(output_path, page_title(article, fallback), article)
        migrated.append(output_path)

    return migrated


def main():
    migrated = migrate_pages()
    print(f"Migrated {len(migrated)} legacy pages to the shared theme.")

    for output_path in migrated:
        print(f"- /{output_path}/")


if __name__ == "__main__":
    main()
