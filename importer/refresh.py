"""Refresh generated SRD pages with the current shared template."""

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.paths import url_to_output_path
from importer.queue import load_queue
from importer.writer import write_page

TITLE_SUFFIXES = (" | d20 SRD Hub", " :: d20srd.org")


def clean_title(title):
    """Remove site-name suffixes from a generated page title."""

    cleaned = title.strip()

    for suffix in TITLE_SUFFIXES:
        cleaned = cleaned.removesuffix(suffix).strip()

    return cleaned


def extract_page_data(page_file):
    """Return the title and article HTML from a generated page."""

    soup = BeautifulSoup(page_file.read_text(encoding="utf-8"), "html.parser")
    article = soup.find("main")

    if article is None:
        raise ValueError("No main article element found.")

    heading = article.find("h1")

    if heading is not None:
        title = heading.get_text(" ", strip=True)
    elif soup.title is not None:
        title = clean_title(soup.title.get_text(" ", strip=True))
    else:
        raise ValueError("No page title found.")

    return title, article.decode_contents().strip()


def refresh_page(output_path):
    """Rewrite one existing page using the current shared template."""

    page_file = PUBLIC_DIR / output_path / "index.html"

    if not page_file.exists():
        return False

    title, article_html = extract_page_data(page_file)
    write_page(output_path, title, article_html)
    return True


def main():
    """Refresh every imported page listed in the local import queue."""

    output_paths = sorted(
        {url_to_output_path(url) for url in load_queue()}
    )
    refreshed = 0
    missing = 0
    failed = []
    total = len(output_paths)

    for number, output_path in enumerate(output_paths, start=1):
        try:
            if refresh_page(output_path):
                refreshed += 1
            else:
                missing += 1
        except Exception as error:
            failed.append((output_path, str(error)))

        if number % 100 == 0 or number == total:
            print(f"[{number}/{total}] Refreshed {refreshed} pages")

    print()
    print(f"Refresh complete: {refreshed} updated, {missing} missing")

    if failed:
        print(f"{len(failed)} pages failed:")

        for output_path, error in failed:
            print(f"- {output_path}: {error}")

        raise SystemExit(1)


if __name__ == "__main__":
    main()
