import requests

from importer.config import USER_AGENT


def download(url):
    """Download a web page and return its HTML."""

    headers = {
        "User-Agent": USER_AGENT
    }

    print(f"Downloading: {url}")

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    response.encoding = "utf-8"

    return response.text