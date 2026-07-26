"""Generate the private browser-bookmarks page."""

from importer.config import PUBLIC_DIR


def render_bookmarks_page():
    """Return the complete bookmarks page HTML."""

    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script data-theme-init>(function(){try{var t=localStorage.getItem("d20srdhub-theme");if(!t){t=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"}document.documentElement.dataset.theme=t}catch(e){}}())</script>
    <meta name="robots" content="noindex">
    <title>Bookmarks | d20 SRD Hub</title>
    <meta name="description" content="Rules you saved privately in this browser.">
    <link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<header class="site-header">
    <h1 class="site-title"><a href="/">d20 SRD Hub</a></h1>
    <nav class="header-links" aria-label="Primary navigation">
        <a href="/">Home</a>
        <a href="/classes/">Classes</a>
        <a href="/spells/">Spells</a>
        <a href="/monsters/">Monsters</a>
        <a href="/bookmarks/" aria-current="page">Bookmarks</a>
    </nav>
    <button class="theme-toggle" data-theme-toggle type="button">☾ Dark</button>
</header>

<div class="content-column">
    <main class="article-card">
        <h1>Your bookmarks</h1>
        <p>
            Saved rules stay private in this browser. No account is required.
        </p>
        <div data-bookmarks-list aria-live="polite"></div>
    </main>
</div>

<script src="/assets/theme.js?v=1" defer></script>
<script src="/assets/bookmarks.js?v=1" defer></script>
</body>
</html>
"""


def write_bookmarks_page(public_dir=PUBLIC_DIR):
    """Write the generated bookmarks page."""

    destination = public_dir / "bookmarks" / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_bookmarks_page(), encoding="utf-8")
    return destination


def main():
    destination = write_bookmarks_page()
    print(f"Created: {destination}")


if __name__ == "__main__":
    main()
