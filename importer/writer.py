from html import escape

from importer.config import PROJECT_ROOT, PUBLIC_DIR


def build_breadcrumbs(output_path, title):
    """Create breadcrumb HTML from the generated output path."""

    parts = output_path.strip("/").split("/")
    breadcrumbs = ['<a href="/">Home</a>']

    for index, part in enumerate(parts[:-1]):
        link_path = "/" + "/".join(parts[: index + 1]) + "/"
        label = escape(part.replace("-", " ").title())

        breadcrumbs.append(
            f'<a href="{link_path}">{label}</a>'
        )

    breadcrumbs.append(f"<span>{escape(title)}</span>")

    separator = ' <span aria-hidden="true">›</span> '
    return separator.join(breadcrumbs)


def write_page(output_path, title, article_html):
    template_path = PROJECT_ROOT / "templates" / "page.html"

    template = template_path.read_text(encoding="utf-8")

    breadcrumbs = build_breadcrumbs(output_path, title)

    page = (
        template
        .replace("{{TITLE}}", title)
        .replace("{{BREADCRUMBS}}", breadcrumbs)
        .replace("{{ARTICLE}}", article_html)
    )

    destination = PUBLIC_DIR / output_path / "index.html"

    destination.parent.mkdir(parents=True, exist_ok=True)

    destination.write_text(page, encoding="utf-8")

    print("Created:", destination)
