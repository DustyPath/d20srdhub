import re
from html import escape, unescape

from bs4 import BeautifulSoup

from importer.config import PROJECT_ROOT, PUBLIC_DIR

TITLE_PATTERN = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
MAX_DESCRIPTION_LENGTH = 155


def build_description(article_html, title):
    """Build a concise plain-text description from an article."""

    soup = BeautifulSoup(article_html, "html.parser")
    paragraphs = soup.find_all("p")
    source = next(
        (
            paragraph
            for paragraph in paragraphs
            if len(paragraph.get_text(" ", strip=True)) >= 50
        ),
        paragraphs[0] if paragraphs else soup,
    )
    text = " ".join(source.get_text(" ", strip=True).split())

    if not text:
        text = f"Rules reference for {title}."

    if len(text) <= MAX_DESCRIPTION_LENGTH:
        return text

    shortened = text[: MAX_DESCRIPTION_LENGTH - 1].rsplit(" ", 1)[0]
    return f"{shortened}…"


def build_breadcrumbs(output_path, title):
    """Create breadcrumb HTML from the generated output path."""

    parts = output_path.strip("/").split("/")
    breadcrumbs = ['<a href="/">Home</a>']

    for index, part in enumerate(parts[:-1]):
        link_path = "/" + "/".join(parts[: index + 1]) + "/"
        label = escape(part.replace("-", " ").title())

        breadcrumbs.append(
            f'<a href="{link_path}">{label}</a>'
        )

    breadcrumbs.append(f"<span>{escape(title)}</span>")

    separator = ' <span aria-hidden="true">›</span> '
    return separator.join(breadcrumbs)


def get_page_label(page_directory):
    """Return a readable label for a generated page directory."""

    page_file = page_directory / "index.html"

    if page_file.exists():
        match = TITLE_PATTERN.search(page_file.read_text(encoding="utf-8"))

        if match:
            title = unescape(match.group(1)).strip()
            title = title.removesuffix(" | d20 SRD Hub").strip()
            return title.removesuffix(" :: d20srd.org").strip()

    return page_directory.name.replace("-", " ").title()


def build_page_navigation(output_path):
    """Create previous and next links for pages in the same section."""

    relative_path = output_path.strip("/")
    current_directory = PUBLIC_DIR / relative_path
    section_directory = current_directory.parent

    if not section_directory.exists():
        return ""

    existing_siblings = {
        directory
        for directory in section_directory.iterdir()
        if directory.is_dir() and (directory / "index.html").exists()
    }
    siblings = sorted(existing_siblings | {current_directory})

    try:
        current_index = siblings.index(current_directory)
    except ValueError:
        return ""

    links = []

    if current_index > 0:
        previous = siblings[current_index - 1]
        previous_path = "/" + previous.relative_to(PUBLIC_DIR).as_posix() + "/"
        links.append(
            '<a class="page-navigation-link previous" '
            f'href="{previous_path}">'
            '<span class="page-navigation-direction">← Previous</span>'
            f'<span>{escape(get_page_label(previous))}</span>'
            "</a>"
        )
    else:
        links.append('<span class="page-navigation-spacer"></span>')

    if current_index < len(siblings) - 1:
        next_page = siblings[current_index + 1]
        next_path = "/" + next_page.relative_to(PUBLIC_DIR).as_posix() + "/"
        links.append(
            '<a class="page-navigation-link next" '
            f'href="{next_path}">'
            '<span class="page-navigation-direction">Next →</span>'
            f'<span>{escape(get_page_label(next_page))}</span>'
            "</a>"
        )
    else:
        links.append('<span class="page-navigation-spacer"></span>')

    if all("page-navigation-spacer" in link for link in links):
        return ""

    return "\n".join(links)


def write_page(output_path, title, article_html):
    template_path = PROJECT_ROOT / "templates" / "page.html"

    template = template_path.read_text(encoding="utf-8")

    breadcrumbs = build_breadcrumbs(output_path, title)
    page_navigation = build_page_navigation(output_path)
    description = build_description(article_html, title)
    canonical_url = f"https://d20srdhub.com/{output_path.strip('/')}/"

    page = (
        template
        .replace("{{TITLE}}", escape(title))
        .replace("{{DESCRIPTION}}", escape(description, quote=True))
        .replace("{{CANONICAL_URL}}", escape(canonical_url, quote=True))
        .replace("{{BREADCRUMBS}}", breadcrumbs)
        .replace("{{ARTICLE}}", article_html)
        .replace("{{PAGE_NAVIGATION}}", page_navigation)
    )
    page = "\n".join(line.rstrip() for line in page.splitlines()) + "\n"

    destination = PUBLIC_DIR / output_path / "index.html"

    destination.parent.mkdir(parents=True, exist_ok=True)

    destination.write_text(page, encoding="utf-8")

    print("Created:", destination)
