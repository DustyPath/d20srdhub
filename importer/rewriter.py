from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup

from importer.config import BASE_URL
from importer.paths import url_to_output_path


def rewrite_links(article_html, source_url):
    """Convert SRD article links into local d20 SRD Hub links."""

    soup = BeautifulSoup(article_html, "lxml")

    for anchor in soup.find_all("a", href=True):
        original_href = anchor["href"]

        # Leave links that only jump to a heading on the same page unchanged.
        if original_href.startswith("#"):
            continue

        absolute_url = urljoin(source_url, original_href)
        clean_url, fragment = urldefrag(absolute_url)
        parsed = urlparse(clean_url)

        # Only rewrite d20srd.org SRD pages.
        if parsed.netloc not in {"d20srd.org", "www.d20srd.org"}:
            continue

        if not parsed.path.startswith("/srd/"):
            continue

        if not parsed.path.endswith(".htm"):
            continue

        try:
            local_path = url_to_output_path(clean_url)
        except ValueError:
            continue

        local_href = f"/{local_path}/"

        if fragment:
            local_href += f"#{fragment}"

        anchor["href"] = local_href

    # Return only the article contents, without added html/body tags.
    body = soup.body

    if body is not None:
        return "".join(str(item) for item in body.contents)

    return str(soup)