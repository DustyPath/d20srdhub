from config import BASE_URL
from downloader import download
from extractor import extract_article
from parser import get_page_title, parse_html
from writer import write_page


url = BASE_URL + "/srd/combat/actionsInCombat.htm"

html = download(url)
soup = parse_html(html)

title = get_page_title(soup)
article = extract_article(soup)

write_page(
    "combat/actions-in-combat",
    title,
    article
)