from pathlib import Path

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.d20srd.org/srd/combat/actionsInCombat.htm"
OUTPUT_FILE = Path("test_actions_in_combat.html")


def main() -> None:
    print(f"Downloading: {SOURCE_URL}")

    response = requests.get(
        SOURCE_URL,
        timeout=30,
        headers={
            "User-Agent": "d20SRDHub development importer/0.1"
        },
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    title = soup.title.get_text(" ", strip=True) if soup.title else "Untitled"
    headings = [
        heading.get_text(" ", strip=True)
        for heading in soup.find_all(["h1", "h2", "h3"])
    ]

    report = [
        f"Page title: {title}",
        "",
        "Headings found:",
        *[f"- {heading}" for heading in headings],
    ]

    OUTPUT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8",
    )

    print(f"Saved inspection report: {OUTPUT_FILE}")
    print(f"Found {len(headings)} headings.")


if __name__ == "__main__":
    main()