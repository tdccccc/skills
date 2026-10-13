import re


def slugify(text):
    """Lowercase text and join its alphanumeric words with hyphens."""
    return "-".join(re.findall(r"[a-z0-9]+", text.lower()))
