from importer.config import BASE_URL
from importer.downloader import download
from importer.parser import get_headings, get_page_title, parse_html


url = BASE_URL + "/srd/combat/actionsInCombat.htm"

html = download(url)
soup = parse_html(html)

print()
print("Page title:")
print(get_page_title(soup))

print()
print("Headings:")

for heading in get_headings(soup):
    print("-", heading)
