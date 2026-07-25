import re
from urllib.parse import urlparse


def camel_to_kebab(text):
    """Convert camelCase or PascalCase text into kebab-case."""

    # Handle source names such as injuryandDeath.
    text = re.sub(r"(?<=[a-z0-9])and(?=[A-Z])", "-and-", text)

    # Insert a hyphen between lowercase/digit and uppercase characters.
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)

    # Replace other separators with one hyphen.
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text)

    return text.strip("-").lower()

def url_to_output_path(url):
    """
    Convert an SRD URL into a local website folder path.

    Example:
    /srd/combat/actionsInCombat.htm
    becomes:
    combat/actions-in-combat
    """

    parsed = urlparse(url)
    path = parsed.path

    if not path.startswith("/srd/"):
        raise ValueError(f"Not an SRD URL: {url}")

    path = path[len("/srd/"):]

    if path.endswith(".htm"):
        path = path[:-4]

    parts = path.split("/")
    clean_parts = [camel_to_kebab(part) for part in parts if part]

    return "/".join(clean_parts)