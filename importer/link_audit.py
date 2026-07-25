"""Audit generated pages for broken internal links."""

from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup

from importer.config import PUBLIC_DIR


def resolve_internal_target(public_dir, source_file, href):
    """Resolve one local href to a public file and optional fragment."""

    parsed = urlsplit(href)

    if parsed.scheme or parsed.netloc:
        return None

    if parsed.path.startswith("/"):
        path = unquote(parsed.path).lstrip("/")
    elif parsed.path:
        path = str((source_file.parent / unquote(parsed.path)).relative_to(public_dir))
    else:
        path = str(source_file.relative_to(public_dir))

    target = public_dir / path

    if parsed.path.endswith((".htm", ".html")):
        target_file = target
    elif parsed.path.endswith("/") or not target.suffix:
        target_file = target / "index.html"
    else:
        target_file = target

    return target_file, parsed.fragment


def audit_internal_links(public_dir=PUBLIC_DIR):
    """Return broken-link records from all generated HTML pages."""

    broken = []
    id_cache = {}

    for source_file in public_dir.rglob("*.htm*"):
        soup = BeautifulSoup(
            source_file.read_text(encoding="utf-8", errors="replace"),
            "html.parser",
        )

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            resolved = resolve_internal_target(public_dir, source_file, href)

            if resolved is None:
                continue

            target_file, fragment = resolved

            if not target_file.exists():
                broken.append((source_file, href, "missing page"))
                continue

            if not fragment:
                continue

            if target_file not in id_cache:
                target_soup = BeautifulSoup(
                    target_file.read_text(encoding="utf-8", errors="replace"),
                    "html.parser",
                )
                id_cache[target_file] = {
                    tag.get("id")
                    for tag in target_soup.find_all(id=True)
                } | {
                    tag.get("name")
                    for tag in target_soup.find_all(attrs={"name": True})
                }

            if fragment not in id_cache[target_file]:
                broken.append((source_file, href, "missing fragment"))

    return broken


def main():
    broken = audit_internal_links()

    if not broken:
        print("Internal link audit passed: 0 broken links.")
        return

    print(f"Internal link audit failed: {len(broken)} broken links.")

    for source_file, href, reason in broken:
        source = source_file.relative_to(PUBLIC_DIR)
        print(f"- {source}: {href} ({reason})")

    raise SystemExit(1)


if __name__ == "__main__":
    main()
