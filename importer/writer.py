from importer.config import PROJECT_ROOT, PUBLIC_DIR

def write_page(output_path, title, article_html):

    template_path = PROJECT_ROOT / "templates" / "page.html"

    template = template_path.read_text(encoding="utf-8")

    page = (
        template
        .replace("{{TITLE}}", title)
        .replace("{{ARTICLE}}", article_html)
    )

    destination = PUBLIC_DIR / output_path / "index.html"

    destination.parent.mkdir(parents=True, exist_ok=True)

    destination.write_text(page, encoding="utf-8")

    print("Created:", destination)