from bs4 import BeautifulSoup


def parse_html(html):
    """Convert HTML text into a BeautifulSoup document."""

    return BeautifulSoup(html, "lxml")


def get_page_title(soup):
    """Return the page title text."""

    if soup.title is None:
        return "Untitled Page"

    return soup.title.get_text(" ", strip=True)


def get_headings(soup):
    """Return all h1, h2, and h3 heading text."""

    headings = []

    for heading in soup.find_all(["h1", "h2", "h3"]):
        text = heading.get_text(" ", strip=True)

        if text:
            headings.append(text)

    return headings