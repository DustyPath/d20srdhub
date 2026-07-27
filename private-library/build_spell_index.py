"""Build a private, searchable Spell Compendium index.

The generated JSON contains names and rules metadata only. Full descriptions
remain in the protected PDF and results link to the appropriate PDF page.
"""

from __future__ import annotations

import argparse
from html import unescape
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unicodedata


SCHOOLS = (
    "Abjuration",
    "Conjuration",
    "Divination",
    "Enchantment",
    "Evocation",
    "Illusion",
    "Necromancy",
    "Transmutation",
    "Universal",
)
SCHOOL_PATTERN = re.compile(
    rf"^(?:{'|'.join(SCHOOLS)})(?:\s+\([^)]*\)|\s+\[[^]]*\])?",
    re.IGNORECASE,
)
LEVEL_PATTERN = re.compile(
    r"\bLevel\s*:\s*(.*?)(?=\bComponents\s*:|\bCasting Time\s*:|"
    r"\bRange\s*:|\bTargets?\s*:|\bArea\s*:|\bDuration\s*:|"
    r"\bSaving Throw\s*:|\bSpell Resistance\s*:|$)",
    re.IGNORECASE,
)
TITLE_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9'’., -]{1,78}$")
STAT_LABELS = {
    "area",
    "casting time",
    "components",
    "duration",
    "effect",
    "level",
    "range",
    "saving throw",
    "spell resistance",
    "target",
    "targets",
}


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def comparison_key(value: str) -> str:
    """Treat reordered title qualifiers as the same spell name."""

    return "-".join(sorted(slugify(value).split("-")))


def public_spell_slugs(public_dir: Path) -> set[str]:
    spells_dir = public_dir / "spells"
    if not spells_dir.exists():
        raise FileNotFoundError(f"Public spell directory not found: {spells_dir}")
    slugs = set()
    for page in spells_dir.glob("*/index.html"):
        if page.parent.name:
            slugs.add(page.parent.name)
            slugs.add(comparison_key(page.parent.name))
    for page in spells_dir.glob("*/index.html"):
        html = page.read_text(encoding="utf-8", errors="replace")
        for heading in re.findall(
            r"<h1(?:\s[^>]*)?>(.*?)</h1>",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            text = re.sub(r"<[^>]+>", "", heading)
            title = unescape(text).strip()
            slugs.add(slugify(title))
            slugs.add(comparison_key(title))
    return slugs


def clean_lines(text: str) -> list[str]:
    return [
        re.sub(r"\s+", " ", line).strip()
        for line in text.replace("\u00ad", "").splitlines()
        if line.strip()
    ]


def looks_like_title(line: str) -> bool:
    if not TITLE_PATTERN.fullmatch(line):
        return False
    if line.casefold().rstrip(":") in STAT_LABELS:
        return False
    if any(character.isdigit() for character in line):
        return False
    if line.endswith((".", ":", ";", ",")) or len(line.split()) > 9:
        return False
    return any(character.isalpha() for character in line)


def parse_school_and_levels(metadata: str) -> tuple[str, str]:
    school_match = SCHOOL_PATTERN.search(metadata)
    level_match = LEVEL_PATTERN.search(metadata)
    school = school_match.group(0).split(" ", 1)[0].title()
    levels = level_match.group(1).strip()
    return school, levels


def extract_spells(pages: list[dict], existing_slugs: set[str]) -> list[dict]:
    """Extract description headings and omit public-SRD spell titles."""

    discovered: dict[str, dict] = {}
    for page in pages:
        lines = clean_lines(page.get("text", ""))

        for index, title_line in enumerate(lines):
            if not looks_like_title(title_line):
                continue

            metadata = " ".join(lines[index + 1 : index + 8])
            if not SCHOOL_PATTERN.search(metadata) or not LEVEL_PATTERN.search(metadata):
                continue

            title = title_line
            if (
                index > 0
                and title_line == title_line.upper()
                and lines[index - 1] == lines[index - 1].upper()
                and looks_like_title(lines[index - 1])
            ):
                title = f"{lines[index - 1]} {title_line}"

            slug = slugify(title)
            if (
                not slug
                or slug in existing_slugs
                or comparison_key(title) in existing_slugs
                or slug in discovered
            ):
                continue

            school, levels = parse_school_and_levels(metadata)
            discovered[slug] = {
                "name": title,
                "page": int(page["page"]),
                "school": school,
                "levels": levels,
            }

    return sorted(discovered.values(), key=lambda spell: spell["name"].casefold())


def extract_pages(pdf_path: Path, swift_script: Path) -> list[dict]:
    """Use macOS PDFKit to extract page text without third-party packages."""

    with tempfile.TemporaryDirectory(prefix="d20-spell-index-") as cache_dir:
        environment = os.environ.copy()
        environment["SWIFT_MODULECACHE_PATH"] = f"{cache_dir}/swift"
        environment["CLANG_MODULE_CACHE_PATH"] = f"{cache_dir}/clang"
        result = subprocess.run(
            ["swift", str(swift_script), str(pdf_path)],
            check=True,
            capture_output=True,
            env=environment,
        )
    return json.loads(result.stdout)


def build_index(
    pdf_path: Path,
    public_dir: Path,
    output_path: Path,
    book_name: str = "Spell Compendium",
) -> dict:
    pages = extract_pages(pdf_path, Path(__file__).with_name("extract_pdf.swift"))
    existing = public_spell_slugs(public_dir)
    spells = extract_spells(pages, existing)
    payload = {
        "book": book_name,
        "private": True,
        "public_srd_duplicates_excluded": True,
        "spell_count": len(spells),
        "spells": spells,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument(
        "--public-dir",
        type=Path,
        default=Path(__file__).parents[1] / "public",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / "generated" / "spell-compendium-index.json",
    )
    parser.add_argument("--book-name", default="Spell Compendium")
    args = parser.parse_args()
    payload = build_index(
        args.pdf,
        args.public_dir,
        args.output,
        book_name=args.book_name,
    )
    print(f"Indexed {payload['spell_count']} private, non-SRD spells: {args.output}")


if __name__ == "__main__":
    main()
