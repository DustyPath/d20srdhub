"""Remove source-site interface and advertising artifacts."""

import re

SOURCE_FOOTER = re.compile(
    r'\s*<div\s+class=["\']footer["\'][^>]*>.*?(?=</main>|$)',
    re.IGNORECASE | re.DOTALL,
)
DICE_ROLLER_LINK = re.compile(
    r'<a\b(?=[^>]*\bclass=["\'][^"\']*\bdiceRoller\b[^"\']*["\'])'
    r"[^>]*>(.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)


def strip_source_artifacts(html):
    """Remove ads, analytics, source footer, and inactive dice controls."""

    cleaned = SOURCE_FOOTER.sub("", html, count=1)
    return DICE_ROLLER_LINK.sub(r"\1", cleaned)
