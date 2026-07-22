from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

SOURCE_FILE = Path("downloaded_homepage.html")
BASE_URL = "https://www.d20srd.org/index.htm"


def main() -> None:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            "downloaded_homepage.html was not found. "
            "Run download_page.py first."
        )

    html = SOURCE_FILE.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    internal_links: set[str] = set()

    for link in soup.find_all("a", href=True):
        absolute_url = urljoin(BASE_URL, link["href"])
        parsed = urlparse(absolute_url)

        if parsed.netloc in {"www.d20srd.org", "d20srd.org"}:
            clean_url = absolute_url.split("#", 1)[0]
            internal_links.add(clean_url)

    sorted_links = sorted(internal_links)

    print(f"Found {len(sorted_links)} internal links:\n")

    for url in sorted_links:
        print(url)


if __name__ == "__main__":
    main()