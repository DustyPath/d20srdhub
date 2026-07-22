from importer.config import BASE_URL
from importer.downloader import download
from importer.extractor import extract_article
from importer.parser import get_page_title, parse_html
from importer.writer import write_page


def import_page(url, output_path):
    """Download, extract, and save one SRD page."""

    html = download(url)
    soup = parse_html(html)

    title = get_page_title(soup)
    article = extract_article(soup)

    write_page(output_path, title, article)


def main():
    import_page(
        BASE_URL + "/srd/combat/actionsInCombat.htm",
        "combat/actions-in-combat",
    )


if __name__ == "__main__":
    main()