from bs4 import Tag


def find_main_heading(soup):
    """
    Return the main H1 heading for the page.
    """

    return soup.find("h1")


def extract_article(soup):
    """
    Extract everything from the H1 until the next horizontal rule.
    """

    heading = find_main_heading(soup)

    if heading is None:
        raise ValueError("No H1 heading found.")

    article = []

    current = heading

    while current:

        if getattr(current, "name", None) == "hr":
            break

        if isinstance(current, Tag):
            article.append(str(current))

        current = current.find_next_sibling()

    return "\n".join(article)