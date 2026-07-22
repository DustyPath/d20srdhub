from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.d20srd.org/srd/combat/actionsInCombat.htm"
OUTPUT_FILE = Path("public/combat/actions-in-combat/index.html")


def download_source() -> str:
    print(f"Downloading: {SOURCE_URL}")

    response = requests.get(
        SOURCE_URL,
        timeout=30,
        headers={
            "User-Agent": "d20SRDHub development importer/0.1"
        },
    )

    response.raise_for_status()
    response.encoding = "utf-8"

    return response.text


def extract_article(source_html: str) -> BeautifulSoup:
    soup = BeautifulSoup(source_html, "html.parser")

    heading = soup.find(
        lambda tag: (
            tag.name in {"h1", "h2"}
            and "Actions In Combat" in tag.get_text(" ", strip=True)
        )
    )

    if heading is None:
        raise RuntimeError(
            "Could not locate the Actions In Combat heading."
        )

    article_html_parts = [str(heading)]

    allowed_elements = {
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "p",
        "table",
        "ul",
        "ol",
        "blockquote",
    }

    for element in heading.find_all_next():
        if element.name in allowed_elements:
            article_html_parts.append(str(element))

    article = BeautifulSoup(
        "\n".join(article_html_parts),
        "html.parser",
    )

    for link in article.find_all("a", href=True):
        link["href"] = urljoin(SOURCE_URL, link["href"])

    return article


def build_page(article: BeautifulSoup) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <title>Actions in Combat | d20 SRD Hub</title>

  <style>
    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      background: #eee8da;
      color: #26211d;
      font-family: Georgia, "Times New Roman", serif;
      line-height: 1.65;
    }}

    header {{
      padding: 30px 20px;
      background: #542020;
      color: white;
      text-align: center;
      border-bottom: 5px solid #341313;
    }}

    header h1 {{
      margin: 0;
      font-size: clamp(2.2rem, 6vw, 4rem);
    }}

    header p {{
      margin: 10px 0 0;
    }}

    nav {{
      padding: 12px 20px;
      background: #341313;
      text-align: center;
    }}

    nav a {{
      display: inline-block;
      margin: 6px 12px;
      color: white;
      font-family: Arial, Helvetica, sans-serif;
      font-weight: bold;
      text-decoration: none;
    }}

    main {{
      max-width: 1000px;
      margin: 36px auto;
      padding: 40px;
      background: #fffdf8;
      border: 1px solid #c9bda9;
      box-shadow: 0 8px 24px rgb(49 34 23 / 12%);
    }}

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {{
      color: #542020;
      line-height: 1.25;
    }}

    a {{
      color: #7a2e2e;
    }}

    table {{
      width: 100%;
      margin: 24px 0;
      border-collapse: collapse;
    }}

    th,
    td {{
      padding: 9px;
      border: 1px solid #b9ad99;
      text-align: left;
      vertical-align: top;
    }}

    tr:nth-child(even) {{
      background: #f5efe4;
    }}

    .source-notice {{
      margin-bottom: 28px;
      padding: 16px 20px;
      background: #f5efe4;
      border-left: 5px solid #7a2e2e;
    }}

    footer {{
      padding: 25px;
      background: #341313;
      color: white;
      text-align: center;
    }}

    @media (max-width: 700px) {{
      main {{
        margin: 18px;
        padding: 24px;
        overflow-x: auto;
      }}
    }}
  </style>
</head>

<body>
  <header>
    <h1>d20 SRD Hub</h1>
    <p>An independent tabletop roleplaying rules reference</p>
  </header>

  <nav aria-label="Primary navigation">
    <a href="/">Home</a>
    <a href="/combat/">Combat</a>
    <a href="/classes/">Classes</a>
    <a href="/skills/">Skills</a>
    <a href="/feats/">Feats</a>
    <a href="/spells/">Spells</a>
  </nav>

  <main>
    <div class="source-notice">
      <strong>Source:</strong>
      Open rules content reproduced from the d20 System Reference Document.
      <a href="{SOURCE_URL}">View the source reference page.</a>
    </div>

    {article}
  </main>

  <footer>
    d20 SRD Hub
  </footer>
</body>
</html>
"""


def main() -> None:
    source_html = download_source()
    article = extract_article(source_html)
    finished_page = build_page(article)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        finished_page,
        encoding="utf-8",
    )

    print(f"Created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()