from urllib.parse import urldefrag, urljoin

from importer.config import BASE_URL
from importer.downloader import download
from importer.parser import parse_html


def get_links(url):
    """Download one page and return its absolute links."""

    html = download(url)
    soup = parse_html(html)

    links = set()

    for anchor in soup.find_all("a", href=True):
        absolute_url = urljoin(url, anchor["href"])

        # Remove fragments such as #initiative
        clean_url, _ = urldefrag(absolute_url)

        links.add(clean_url)

    return links


def discover_index_links():
    """Find SRD index pages linked from the homepage."""

    homepage_url = BASE_URL + "/index.htm"
    links = get_links(homepage_url)

    return sorted(
        link
        for link in links
        if "/indexes/" in link and link.endswith(".htm")
    )


def discover_srd_links():
    """Visit every index page and find unique SRD page links."""

    index_links = discover_index_links()
    srd_links = set()

    print()
    print("Found", len(index_links), "index pages")
    print()

    for index_url in index_links:
        print("Scanning:", index_url)

        for link in get_links(index_url):
            if "/srd/" in link and link.endswith(".htm"):
                srd_links.add(link)

    return sorted(srd_links)