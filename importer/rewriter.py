from urllib.parse import urldefrag, urljoin, urlparse

from bs4 import BeautifulSoup

from importer.config import BASE_URL
from importer.paths import url_to_output_path


LEGACY_SITE_LINKS = {
    "/ogl.htm": "/legal/",
    "/indexes/classes.htm": "/classes/",
    "/indexes/traps.htm": "/traps/",
}

LEGACY_FRAGMENT_LINKS = {
    ("/srd/monsterFeats.htm", "improvedMultiattack"): (
        "/monster-feats/",
        "",
    ),
    ("/monster-feats/", "improvedMultiattack"): (
        "/monster-feats/",
        "",
    ),
}


def rewrite_legacy_site_links(article_html):
    """Rewrite legacy site-level links that are outside the SRD URL tree."""

    soup = BeautifulSoup(article_html, "lxml")

    for anchor in soup.find_all("a", href=True):
        parsed = urlparse(anchor["href"])
        fragment_replacement = LEGACY_FRAGMENT_LINKS.get(
            (parsed.path, parsed.fragment)
        )

        if fragment_replacement is not None:
            path, fragment = fragment_replacement
            anchor["href"] = path + (f"#{fragment}" if fragment else "")
            continue

        replacement = LEGACY_SITE_LINKS.get(parsed.path)

        if replacement is None:
            continue

        anchor["href"] = replacement

        if parsed.fragment:
            anchor["href"] += f"#{parsed.fragment}"

    body = soup.body

    if body is not None:
        return "".join(str(item) for item in body.contents)

    return str(soup)


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

        fragment_replacement = LEGACY_FRAGMENT_LINKS.get(
            (parsed.path, fragment)
        )

        if fragment_replacement is not None:
            path, replacement_fragment = fragment_replacement
            anchor["href"] = path

            if replacement_fragment:
                anchor["href"] += f"#{replacement_fragment}"

            continue

        replacement = LEGACY_SITE_LINKS.get(parsed.path)

        if replacement is not None:
            anchor["href"] = replacement

            if fragment:
                anchor["href"] += f"#{fragment}"

            continue

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
