from config import BASE_URL
from downloader import download
from parser import parse_html
from extractor import extract_article

url = BASE_URL + "/srd/combat/actionsInCombat.htm"

html = download(url)
soup = parse_html(html)

article = extract_article(soup)

print(article[:3000])