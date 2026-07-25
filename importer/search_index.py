"""Build the static client-side search index."""

import json
import re
from html import unescape

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR
from importer.paths import url_to_output_path
from importer.queue import load_queue

MAX_SEARCH_TEXT = 3500
SITE_TITLE_SUFFIXES = (" | d20 SRD Hub", " :: d20srd.org")
WHITESPACE = re.compile(r"\s+")


def clean_text(value):
    """Collapse whitespace and decode HTML entities."""

    return WHITESPACE.sub(" ", unescape(value)).strip()


def clean_title(value):
    """Remove known site-name suffixes from a document title."""

    title = clean_text(value)

    for suffix in SITE_TITLE_SUFFIXES:
        title = title.removesuffix(suffix).strip()

    return title


def build_search_document(page_file, output_path):
    """Create one compact searchable document from a generated page."""

    soup = BeautifulSoup(page_file.read_text(encoding="utf-8"), "html.parser")
    article = soup.find("main")

    if article is None:
        raise ValueError(f"No main article found in {page_file}")

    heading = article.find("h1")

    if heading is not None:
        title = clean_text(heading.get_text(" ", strip=True))
    elif soup.title is not None:
        title = clean_title(soup.title.get_text(" ", strip=True))
    else:
        title = output_path.rsplit("/", 1)[-1].replace("-", " ").title()

    headings = clean_text(
        " ".join(
            item.get_text(" ", strip=True)
            for item in article.find_all(["h2", "h3", "h4", "h5"])
        )
    )
    text = clean_text(article.get_text(" ", strip=True))
    section = output_path.split("/", 1)[0].replace("-", " ").title()

    return {
        "title": title,
        "url": f"/{output_path}/",
        "section": section,
        "headings": headings[:1200],
        "text": text[:MAX_SEARCH_TEXT],
    }


def build_search_index():
    """Build documents for every imported page in the queue."""

    documents = []
    output_paths = sorted(
        {url_to_output_path(url) for url in load_queue()}
    )

    for output_path in output_paths:
        page_file = PUBLIC_DIR / output_path / "index.html"

        if page_file.exists():
            documents.append(build_search_document(page_file, output_path))

    return documents


def main():
    """Write the static JSON search index."""

    documents = build_search_index()
    output_file = PUBLIC_DIR / "assets" / "search-index.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(documents, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    size_mb = output_file.stat().st_size / 1_000_000
    print(f"Created {output_file}")
    print(f"Indexed {len(documents)} pages ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
