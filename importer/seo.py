"""Add crawl metadata and generate search-engine discovery files."""

from html import escape
from pathlib import Path
import re
from urllib.parse import quote

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR, SITE_URL
from importer.writer import MAX_DESCRIPTION_LENGTH

DESCRIPTION_META = re.compile(
    r'<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*>',
    re.IGNORECASE | re.DOTALL,
)
CANONICAL_LINK = re.compile(
    r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*>',
    re.IGNORECASE | re.DOTALL,
)


def page_route(page_file, public_dir=PUBLIC_DIR):
    """Return the public route for an index page."""

    relative = page_file.relative_to(public_dir)

    if relative == Path("index.html"):
        return "/"

    return f"/{relative.parent.as_posix()}/"


def page_description(soup):
    """Return a concise description from a rendered page."""

    main = soup.find("main")
    source = main or soup.body or soup
    paragraphs = source.find_all("p")
    text_source = next(
        (
            paragraph
            for paragraph in paragraphs
            if len(paragraph.get_text(" ", strip=True)) >= 50
        ),
        paragraphs[0] if paragraphs else source,
    )
    text = " ".join(text_source.get_text(" ", strip=True).split())

    if len(text) <= MAX_DESCRIPTION_LENGTH:
        return text

    shortened = text[: MAX_DESCRIPTION_LENGTH - 1].rsplit(" ", 1)[0]
    return f"{shortened}…"


def set_meta(soup, route):
    """Add or update description and canonical metadata."""

    if soup.head is None:
        raise ValueError("Page has no head element.")

    description = page_description(soup)
    canonical_url = f"{SITE_URL}{route}"

    description_meta = soup.head.find("meta", attrs={"name": "description"})

    if description_meta is None:
        description_meta = soup.new_tag("meta")
        description_meta["name"] = "description"
        soup.head.append(description_meta)

    description_meta["content"] = description

    canonical = soup.head.find("link", attrs={"rel": "canonical"})

    if canonical is None:
        canonical = soup.new_tag("link")
        canonical["rel"] = "canonical"
        soup.head.append(canonical)

    canonical["href"] = canonical_url

    return description, canonical_url


def update_page_file(page_file, public_dir=PUBLIC_DIR):
    """Update one page's metadata without reformatting its HTML."""

    html = page_file.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    route = page_route(page_file, public_dir)
    description = page_description(soup)
    canonical_url = f"{SITE_URL}{route}"
    description_tag = (
        f'<meta name="description" content="{escape(description, quote=True)}">'
    )
    canonical_tag = (
        f'<link rel="canonical" href="{escape(canonical_url, quote=True)}">'
    )

    if DESCRIPTION_META.search(html):
        html = DESCRIPTION_META.sub(description_tag, html, count=1)
    else:
        html = html.replace(
            "</title>",
            f"</title>\n    {description_tag}",
            1,
        )

    if CANONICAL_LINK.search(html):
        html = CANONICAL_LINK.sub(canonical_tag, html, count=1)
    else:
        html = html.replace(
            description_tag,
            f"{description_tag}\n    {canonical_tag}",
            1,
        )

    page_file.write_text(html, encoding="utf-8")


def update_existing_pages(public_dir=PUBLIC_DIR):
    """Add SEO metadata to all public index pages."""

    updated = 0

    for page_file in sorted(public_dir.rglob("index.html")):
        update_page_file(page_file, public_dir)
        updated += 1

    return updated


def sitemap_routes(public_dir=PUBLIC_DIR):
    """Return every canonical, indexable page route."""

    routes = []

    for page_file in public_dir.rglob("index.html"):
        soup = BeautifulSoup(
            page_file.read_text(encoding="utf-8", errors="replace"),
            "html.parser",
        )

        robots = soup.head.find("meta", attrs={"name": "robots"}) if soup.head else None

        if robots and "noindex" in robots.get("content", "").lower():
            continue

        routes.append(page_route(page_file, public_dir))

    return sorted(set(routes))


def write_sitemap(public_dir=PUBLIC_DIR):
    """Write sitemap.xml and return the number of URLs."""

    routes = sitemap_routes(public_dir)
    entries = "\n".join(
        f"  <url><loc>{escape(SITE_URL + quote(route, safe='/'))}</loc></url>"
        for route in routes
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )
    (public_dir / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    return len(routes)


def write_robots(public_dir=PUBLIC_DIR):
    """Write a permissive robots.txt with the sitemap location."""

    (public_dir / "robots.txt").write_text(
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )


def main():
    updated = update_existing_pages()
    url_count = write_sitemap()
    write_robots()
    print(f"Updated metadata on {updated} pages.")
    print(f"Created sitemap.xml with {url_count} URLs.")
    print("Created robots.txt.")


if __name__ == "__main__":
    main()
