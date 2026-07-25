from pathlib import Path

from importer.queue import load_queue, save_queue
from importer.crawler import discover_srd_links
from importer.downloader import download
from importer.extractor import extract_article
from importer.parser import get_page_title, parse_html
from importer.paths import url_to_output_path
from importer.writer import write_page
from importer.rewriter import rewrite_links
from importer.logger import clear_error_log, log_error


def import_page(url):
    """Download, extract, and save one SRD page."""

    output_path = url_to_output_path(url)
    output_file = Path("public") / output_path / "index.html"

    if output_file.exists():
        print(f"Skipping: {output_path}")
        return

    print(f"Downloading: {url}")

    html = download(url)
    soup = parse_html(html)

    title = get_page_title(soup)
    article = extract_article(soup)
    article = rewrite_links(article, url)

    write_page(output_path, title, article)


def main():
    clear_error_log()

    links = load_queue()

    if not links:
        print("No import queue found. Crawling SRD...")
        links = discover_srd_links()
        save_queue(links)
        print(f"Saved {len(links)} URLs to import_queue.txt")
    else:
        print(f"Loaded {len(links)} URLs from import_queue.txt")

    selected_links = links
    total = len(selected_links)

    print()
    print(f"Importing {total} SRD pages")
    print()
    for number, link in enumerate(selected_links, start=1):
        print(f"[{number}/{total}] Processing {link}")

        try:
            import_page(link)
        except Exception as error:
            print(f"❌ Failed: {link}")
            print(f"Reason: {error}")
            log_error(link, error)

    print()
    print("Import complete.")

if __name__ == "__main__":
    main()