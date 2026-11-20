#!/usr/bin/env python3
"""Build R2-ready Forgotten Realms article objects from a converted wiki vault.

The input is the Markdown vault produced from Fandom's current-pages XML dump.
The output deliberately contains no images. Each article retains its source URL
and CC BY-SA 3.0 attribution, while wiki links are rewritten to local routes.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import quote

BASE_PATH = "/gm-secrets/forgotten-realms"
LICENSE_NAME = "CC BY-SA 3.0"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/3.0/"
SOURCE_NAME = "Forgotten Realms Wiki"
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")


def slug(title: str) -> str:
    # The hash prevents case-folding and punctuation collisions on macOS and in R2.
    digest = hashlib.sha1(title.encode("utf-8")).hexdigest()[:10]
    return f"{quote(title, safe='-._~')}--{digest}"


def shard_key(title: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "", title.casefold())
    return (normalized[:2] or "__").ljust(2, "_")


def parse_note(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    if text.startswith("---\n"):
        _, frontmatter, text = text.split("---\n", 2)
        for line in frontmatter.splitlines():
            if ":" not in line or line.startswith((" ", "-")):
                continue
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')
    return metadata, text.strip()


def inline_markup(value: str) -> str:
    escaped = html.escape(value, quote=False)

    def wiki_link(match: re.Match[str]) -> str:
        target = html.unescape(match.group(1)).strip()
        label = html.unescape(match.group(2) or target).strip()
        return f'<a href="{BASE_PATH}/wiki/{slug(target)}/">{html.escape(label)}</a>'

    escaped = WIKILINK_RE.sub(wiki_link, escaped)
    escaped = MARKDOWN_LINK_RE.sub(
        lambda match: f'<a href="{html.escape(match.group(2), quote=True)}" rel="nofollow">{html.escape(match.group(1))}</a>',
        escaped,
    )
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*", r"<em>\1</em>", escaped)
    return escaped


def markdown_to_html(markdown: str) -> str:
    output: list[str] = []
    paragraph: list[str] = []
    list_tag: str | None = None

    def flush_paragraph() -> None:
        if paragraph:
            output.append(f"<p>{inline_markup(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_tag
        if list_tag:
            output.append(f"</{list_tag}>")
            list_tag = None

    lines = markdown.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        if not line:
            flush_paragraph(); close_list(); index += 1; continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph(); close_list()
            level = min(len(heading.group(1)) + 1, 6)
            output.append(f"<h{level}>{inline_markup(heading.group(2))}</h{level}>")
            index += 1; continue
        item = re.match(r"^\s*([-*]|\d+\.)\s+(.+)$", line)
        if item:
            flush_paragraph()
            wanted = "ol" if item.group(1)[0].isdigit() else "ul"
            if list_tag != wanted:
                close_list(); output.append(f"<{wanted}>"); list_tag = wanted
            output.append(f"<li>{inline_markup(item.group(2))}</li>")
            index += 1; continue
        if line.startswith(">"):
            flush_paragraph(); close_list()
            output.append(f"<blockquote>{inline_markup(line.lstrip('> '))}</blockquote>")
            index += 1; continue
        paragraph.append(line)
        index += 1
    flush_paragraph(); close_list()
    return "\n".join(output)


def build(vault: Path, output: Path) -> dict[str, object]:
    article_dir = output / "article-shards"
    search_dir = output / "search"
    article_dir.mkdir(parents=True, exist_ok=True)
    search_dir.mkdir(parents=True, exist_ok=True)
    search: dict[str, list[dict[str, str]]] = defaultdict(list)
    article_shards: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    categories: Counter[str] = Counter()
    count = 0
    for note in sorted(vault.rglob("*.md")):
        metadata, markdown = parse_note(note)
        title = metadata.get("title") or note.stem.replace("-", " ")
        source_url = metadata.get("source_url", "")
        category = metadata.get("category") or note.parent.name
        article_slug = slug(title)
        record = {
            "title": title,
            "category": category,
            "source_url": source_url,
            "license": LICENSE_NAME,
            "license_url": LICENSE_URL,
            "html": markdown_to_html(markdown),
        }
        article_shards[hashlib.sha1(title.encode("utf-8")).hexdigest()[:2]][article_slug] = record
        plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", record["html"]))
        search[shard_key(title)].append({
            "title": title,
            "category": category,
            "url": f"{BASE_PATH}/wiki/{article_slug}/",
            "excerpt": html.unescape(plain[:240]),
        })
        categories[category] += 1
        count += 1
    for key, records in article_shards.items():
        (article_dir / f"{key}.json").write_text(
            json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
    for key, records in search.items():
        records.sort(key=lambda item: item["title"].casefold())
        (search_dir / f"{key}.json").write_text(
            json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
    manifest = {
        "articles": count,
        "categories": dict(categories.most_common()),
        "source": SOURCE_NAME,
        "source_dump": "Fandom current-pages XML dump",
        "license": LICENSE_NAME,
        "license_url": LICENSE_URL,
        "images_included": False,
        "article_shards": len(article_shards),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    digest = hashlib.sha256((output / "manifest.json").read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text(f"{digest}  manifest.json\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("vault", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.vault, args.output), indent=2))


if __name__ == "__main__":
    main()
