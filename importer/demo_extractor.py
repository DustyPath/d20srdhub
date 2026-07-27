from importer.config import BASE_URL
from importer.downloader import download
from importer.extractor import extract_article
from importer.parser import parse_html

url = BASE_URL + "/srd/combat/actionsInCombat.htm"

html = download(url)
soup = parse_html(html)

article = extract_article(soup)

print(article[:3000])
