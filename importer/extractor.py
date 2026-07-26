from bs4 import Tag


def find_main_heading(soup):
    """
    Return the main H1 heading for the page.
    """

    return soup.find("h1")


def extract_article(soup):
    """
    Extract the main article from the page.
    """

    heading = find_main_heading(soup)

    # Some SRD pages (such as Rogue) don't have an H1.
    # In that case, begin at the first H2.
    if heading is None:
        heading = soup.find("h2")

    if heading is None:
        raise ValueError("No H1 or H2 heading found.")

    article = []

    current = heading

    while current:

        if getattr(current, "name", None) == "hr":
            break

        if (
            isinstance(current, Tag)
            and "footer" in current.get("class", [])
        ):
            break

        if isinstance(current, Tag):
            article.append(str(current))

        current = current.find_next_sibling()

    return "\n".join(article)
