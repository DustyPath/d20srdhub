from config import BASE_URL
from downloader import download

html = download(BASE_URL + "/index.htm")

print()
print("Downloaded", len(html), "characters")
print()
print(html[:500])