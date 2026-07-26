"""Move repeated page CSS into one shared, cacheable asset."""

import re

from importer.cleaner import strip_source_artifacts
from importer.config import PROJECT_ROOT, PUBLIC_DIR

STYLE_BLOCK = re.compile(r"\n?\s*<style>(.*?)</style>", re.DOTALL)
CANONICAL_LINK = re.compile(
    r'(<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*>)',
    re.IGNORECASE | re.DOTALL,
)
SHARED_STYLESHEET = '<link rel="stylesheet" href="/assets/site.css">'
LEGACY_SEARCH_SCRIPT = '<script src="/assets/search.js" defer></script>'
SEARCH_SCRIPT = '<script src="/assets/search.js?v=2" defer></script>'


def migrate_html(html):
    """Replace shared-template inline CSS with the shared stylesheet link."""

    migrated = strip_source_artifacts(html)
    migrated = migrated.replace(LEGACY_SEARCH_SCRIPT, SEARCH_SCRIPT)

    if SEARCH_SCRIPT not in migrated or not STYLE_BLOCK.search(migrated):
        return migrated

    migrated = STYLE_BLOCK.sub("", migrated, count=1)

    if SHARED_STYLESHEET in migrated:
        return migrated

    canonical = CANONICAL_LINK.search(migrated)

    if canonical is not None:
        return (
            migrated[: canonical.end()]
            + f"\n    {SHARED_STYLESHEET}"
            + migrated[canonical.end() :]
        )

    return migrated.replace(
        "</title>",
        f"</title>\n    {SHARED_STYLESHEET}",
        1,
    )


def extract_template_css(
    template_path=None,
    stylesheet_path=None,
):
    """Extract the template's inline CSS and update the template."""

    template_path = template_path or PROJECT_ROOT / "templates" / "page.html"
    stylesheet_path = (
        stylesheet_path or PUBLIC_DIR / "assets" / "site.css"
    )
    template = template_path.read_text(encoding="utf-8")
    match = STYLE_BLOCK.search(template)

    if match is None:
        if not stylesheet_path.exists():
            raise ValueError("Template has no inline CSS to extract.")

        return stylesheet_path.stat().st_size

    css = match.group(1).strip() + "\n"
    stylesheet_path.parent.mkdir(parents=True, exist_ok=True)
    stylesheet_path.write_text(css, encoding="utf-8")
    template_path.write_text(migrate_html(template), encoding="utf-8")
    return len(css.encode("utf-8"))


def migrate_generated_pages(public_dir=PUBLIC_DIR):
    """Migrate every page produced from the shared template."""

    updated = 0

    for page_file in public_dir.rglob("index.html"):
        html = page_file.read_text(encoding="utf-8")
        migrated = migrate_html(html)

        if migrated == html:
            continue

        page_file.write_text(migrated, encoding="utf-8")
        updated += 1

    return updated


def audit_shared_styles(public_dir=PUBLIC_DIR):
    """Return shared-template pages that still have a CSS problem."""

    problems = []

    for page_file in public_dir.rglob("index.html"):
        html = page_file.read_text(encoding="utf-8", errors="replace")

        if SEARCH_SCRIPT not in html:
            continue

        if STYLE_BLOCK.search(html):
            problems.append((page_file, "inline style remains"))

        if SHARED_STYLESHEET not in html:
            problems.append((page_file, "shared stylesheet is missing"))

        other_scripts = re.findall(
            r"<script\b(?![^>]*\bsrc=[\"']/assets/search\.js(?:\?v=\d+)?[\"'])",
            html,
            re.IGNORECASE,
        )

        if other_scripts:
            problems.append((page_file, "unexpected imported script remains"))

        if "diceRoller" in html or "javascript:void(0)" in html:
            problems.append((page_file, "inactive source control remains"))

    return problems


def main():
    css_size = extract_template_css()
    updated = migrate_generated_pages()
    problems = audit_shared_styles()

    print(f"Created shared stylesheet ({css_size:,} bytes).")
    print(f"Migrated {updated:,} generated pages.")

    if problems:
        for page_file, problem in problems:
            print(f"- {page_file}: {problem}")

        raise SystemExit(1)

    print("Shared-style audit passed.")


if __name__ == "__main__":
    main()
