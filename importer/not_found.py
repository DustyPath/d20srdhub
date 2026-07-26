"""Generate the branded, searchable 404 page."""

from importer.config import PUBLIC_DIR


def render_not_found():
    """Return the complete 404 page HTML."""

    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script data-theme-init>(function(){try{var t=localStorage.getItem("d20srdhub-theme");if(!t){t=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"}document.documentElement.dataset.theme=t}catch(e){}}())</script>
    <meta name="robots" content="noindex">
    <title>Page Not Found | d20 SRD Hub</title>
    <meta name="description" content="Find the d20 System rule you were looking for.">
    <link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<header class="site-header">
    <h1 class="site-title"><a href="/">d20 SRD Hub</a></h1>

    <form class="site-search" data-search-form role="search">
        <div class="site-search-row">
            <label class="visually-hidden" for="header-search">
                Search the rules
            </label>
            <input
                id="header-search"
                data-search-input
                type="search"
                autocomplete="off"
                placeholder="Search rules…"
            >
            <button type="submit">Search</button>
        </div>
        <div
            class="search-results"
            data-search-results
            aria-live="polite"
            hidden
        ></div>
    </form>

    <nav class="header-links" aria-label="Primary navigation">
        <a href="/">Home</a>
        <a href="/classes/">Classes</a>
        <a href="/combat/">Combat</a>
        <a href="/spells/">Spells</a>
        <a href="/monsters/">Monsters</a>
    </nav>
    <button class="theme-toggle" data-theme-toggle type="button">
        ☾ Dark
    </button>
</header>

<div class="content-column">
    <main class="article-card">
        <p><strong>404</strong></p>
        <h1>That rule slipped away.</h1>
        <p>
            The page may have moved, or the address may be incomplete.
            Search above or continue with one of these popular sections.
        </p>
        <nav class="page-navigation" aria-label="Helpful destinations">
            <a class="page-navigation-link" href="/classes/">
                <span class="page-navigation-label">Browse</span>
                <strong>Classes</strong>
            </a>
            <a class="page-navigation-link" href="/spells/">
                <span class="page-navigation-label">Browse</span>
                <strong>Spells</strong>
            </a>
            <a class="page-navigation-link" href="/monsters/">
                <span class="page-navigation-label">Browse</span>
                <strong>Monsters</strong>
            </a>
        </nav>
    </main>
</div>

<script src="/assets/search.js?v=2" defer></script>
<script src="/assets/theme.js?v=1" defer></script>
</body>
</html>
"""


def write_not_found(public_dir=PUBLIC_DIR):
    """Write the generated 404 page."""

    destination = public_dir / "404.html"
    destination.write_text(render_not_found(), encoding="utf-8")
    return destination


def main():
    destination = write_not_found()
    print(f"Created: {destination}")


if __name__ == "__main__":
    main()
