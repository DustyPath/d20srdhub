"""Move repeated page CSS into one shared, cacheable asset."""

import re

from importer.cleaner import strip_source_artifacts
from importer.config import PROJECT_ROOT, PUBLIC_DIR

STYLE_BLOCK = re.compile(r"\n?\s*<style>(.*?)</style>", re.DOTALL)
CANONICAL_LINK = re.compile(
    r'(<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*>)',
    re.IGNORECASE | re.DOTALL,
)
ARTICLE_CARD_OPEN = re.compile(
    r'(?P<indent>^[ \t]*)<main class="article-card">',
    re.MULTILINE,
)
SHARED_STYLESHEET = '<link rel="stylesheet" href="/assets/site.css">'
LEGACY_SEARCH_SCRIPT = '<script src="/assets/search.js" defer></script>'
SEARCH_SCRIPT = '<script src="/assets/search.js?v=2" defer></script>'
TOC_SCRIPT = '<script src="/assets/toc.js?v=1" defer></script>'
THEME_SCRIPT = '<script src="/assets/theme.js?v=1" defer></script>'
NAVIGATION_SCRIPT = '<script src="/assets/navigation.js?v=1" defer></script>'
PRINT_SCRIPT = '<script src="/assets/print.js?v=1" defer></script>'
BOOKMARKS_SCRIPT = '<script src="/assets/bookmarks.js?v=1" defer></script>'
THEME_INIT = (
    '<script data-theme-init>(function(){try{var t=localStorage.getItem'
    '("d20srdhub-theme");if(!t){t=matchMedia("(prefers-color-scheme: dark)")'
    '.matches?"dark":"light"}document.documentElement.dataset.theme=t}'
    'catch(e){}}())</script>'
)
THEME_BUTTON = (
    '<button class="theme-toggle" data-theme-toggle type="button">\n'
    "        ☾ Dark\n"
    "    </button>"
)
SIDEBAR_TITLE = '<p class="sidebar-title">SRD Sections</p>'
SIDEBAR_TOGGLE = (
    '<button class="sidebar-toggle" data-sidebar-toggle type="button" '
    'aria-controls="sidebar-navigation" aria-expanded="false">\n'
    "            Browse sections\n"
    "        </button>"
)
SIDEBAR_NAV = '<nav class="sidebar-nav" aria-label="SRD sections">'
SIDEBAR_NAV_WITH_ID = (
    '<nav id="sidebar-navigation" class="sidebar-nav" '
    'aria-label="SRD sections">'
)
PRINT_TOOLS = (
    '<div class="article-tools" aria-label="Page tools">\n'
    '            <button class="print-button" data-print-page type="button">\n'
    "                Print / Save PDF\n"
    "            </button>\n"
    "        </div>"
)
ARTICLE_TOOLS = (
    '<div class="article-tools" aria-label="Page tools">\n'
    '            <button class="bookmark-button" data-bookmark-page '
    'type="button">\n'
    "                ☆ Save rule\n"
    "            </button>\n"
    '            <button class="print-button" data-print-page type="button">\n'
    "                Print / Save PDF\n"
    "            </button>\n"
    "        </div>"
)
LEGAL_LINK = '<a href="/legal/">Legal</a>'
BOOKMARKS_LINK = '<a href="/bookmarks/">Bookmarks</a>'


def migrate_html(html):
    """Replace shared-template inline CSS with the shared stylesheet link."""

    migrated = strip_source_artifacts(html)
    migrated = migrated.replace(LEGACY_SEARCH_SCRIPT, SEARCH_SCRIPT)
    has_sidebar_navigation = (
        SIDEBAR_NAV in migrated or SIDEBAR_NAV_WITH_ID in migrated
    )
    has_article = 'class="article-card"' in migrated

    if SEARCH_SCRIPT in migrated and TOC_SCRIPT not in migrated:
        migrated = migrated.replace(
            SEARCH_SCRIPT,
            f"{SEARCH_SCRIPT}\n{TOC_SCRIPT}",
            1,
        )

    if SEARCH_SCRIPT in migrated and THEME_SCRIPT not in migrated:
        migrated = migrated.replace(
            TOC_SCRIPT,
            f"{TOC_SCRIPT}\n{THEME_SCRIPT}",
            1,
        )

    if (
        SEARCH_SCRIPT in migrated
        and has_sidebar_navigation
        and NAVIGATION_SCRIPT not in migrated
    ):
        migrated = migrated.replace(
            THEME_SCRIPT,
            f"{THEME_SCRIPT}\n{NAVIGATION_SCRIPT}",
            1,
        )

    if SEARCH_SCRIPT in migrated and has_article and PRINT_SCRIPT not in migrated:
        script_anchor = (
            NAVIGATION_SCRIPT
            if NAVIGATION_SCRIPT in migrated
            else THEME_SCRIPT
        )
        migrated = migrated.replace(
            script_anchor,
            f"{script_anchor}\n{PRINT_SCRIPT}",
            1,
        )

    if SEARCH_SCRIPT in migrated and has_article and BOOKMARKS_SCRIPT not in migrated:
        migrated = migrated.replace(
            PRINT_SCRIPT,
            f"{PRINT_SCRIPT}\n{BOOKMARKS_SCRIPT}",
            1,
        )

    if not has_sidebar_navigation and NAVIGATION_SCRIPT in migrated:
        migrated = migrated.replace(f"\n{NAVIGATION_SCRIPT}", "", 1)

    if SEARCH_SCRIPT in migrated and THEME_INIT not in migrated:
        if SHARED_STYLESHEET in migrated:
            migrated = migrated.replace(
                SHARED_STYLESHEET,
                f"{THEME_INIT}\n    {SHARED_STYLESHEET}",
                1,
            )
        else:
            migrated = migrated.replace(
                "</head>",
                f"    {THEME_INIT}\n</head>",
                1,
            )

    if SEARCH_SCRIPT in migrated and "data-theme-toggle" not in migrated:
        if "</header>" in migrated:
            migrated = migrated.replace(
                "</header>",
                f"    {THEME_BUTTON}\n</header>",
                1,
            )
        else:
            migrated = migrated.replace(
                "<body>",
                f"<body>\n    {THEME_BUTTON}",
                1,
            )

    if SEARCH_SCRIPT in migrated and "data-sidebar-toggle" not in migrated:
        migrated = migrated.replace(
            SIDEBAR_TITLE,
            f"{SIDEBAR_TITLE}\n\n        {SIDEBAR_TOGGLE}",
            1,
        )

    if SEARCH_SCRIPT in migrated and 'id="sidebar-navigation"' not in migrated:
        migrated = migrated.replace(
            SIDEBAR_NAV,
            SIDEBAR_NAV_WITH_ID,
            1,
        )

    if (
        SEARCH_SCRIPT in migrated
        and has_article
        and "data-print-page" not in migrated
    ):
        migrated = ARTICLE_CARD_OPEN.sub(
            lambda match: (
                f"{match.group('indent')}{PRINT_TOOLS}\n\n"
                f'{match.group("indent")}<main class="article-card">'
            ),
            migrated,
            count=1,
        )

    if has_article and "data-bookmark-page" not in migrated:
        migrated = migrated.replace(PRINT_TOOLS, ARTICLE_TOOLS, 1)

    if LEGAL_LINK in migrated and BOOKMARKS_LINK not in migrated:
        migrated = migrated.replace(
            LEGAL_LINK,
            f"{BOOKMARKS_LINK}\n        {LEGAL_LINK}",
            1,
        )

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

        if TOC_SCRIPT not in html:
            problems.append((page_file, "table-of-contents script is missing"))

        if THEME_SCRIPT not in html or THEME_INIT not in html:
            problems.append((page_file, "theme support is missing"))

        if "data-theme-toggle" not in html:
            problems.append((page_file, "theme toggle is missing"))

        if 'class="sidebar-nav"' in html:
            if NAVIGATION_SCRIPT not in html or "data-sidebar-toggle" not in html:
                problems.append((page_file, "mobile navigation is missing"))

            if 'id="sidebar-navigation"' not in html:
                problems.append((page_file, "sidebar navigation id is missing"))

        if 'class="article-card"' in html:
            if PRINT_SCRIPT not in html or "data-print-page" not in html:
                problems.append((page_file, "print support is missing"))
            if BOOKMARKS_SCRIPT not in html or "data-bookmark-page" not in html:
                problems.append((page_file, "bookmark support is missing"))

        script_audit_html = html.replace(THEME_INIT, "")
        other_scripts = re.findall(
            r"<script\b(?![^>]*\bsrc=[\"']/assets/"
            r"(?:search|toc|theme|navigation|print|bookmarks)"
            r"\.js(?:\?v=\d+)?[\"'])",
            script_audit_html,
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
