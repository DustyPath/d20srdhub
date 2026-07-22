import requests

url = "https://www.d20srd.org/index.htm"

print("Downloading:", url)

response = requests.get(url)

print("Status Code:", response.status_code)

with open("downloaded_homepage.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Done! The page was saved as downloaded_homepage.html")