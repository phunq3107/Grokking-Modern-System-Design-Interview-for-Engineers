
from pathlib import Path
from html import escape
from urllib.parse import quote
import re

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "index.html"

EXCLUDED_DIRS = {
    ".git",
    ".github",
    "scripts",
}


def natural_sort_key(name):
    """
    Sort names by numeric prefix.

    Examples:
        1. Introduction
        2. Database
        10. Distributed Systems
    """
    match = re.match(r"^(\d+)\.\s*(.*)$", name)

    if match:
        return (0, int(match.group(1)), match.group(2).casefold())

    return (1, 0, name.casefold())


def create_tree(files):
    """
    Build a nested directory tree from HTML file paths.
    """
    tree = {
        "dirs": {},
        "files": []
    }

    for file in files:
        relative_path = file.relative_to(ROOT)
        parts = relative_path.parts

        current = tree

        # Traverse directory components
        for directory in parts[:-1]:
            current = current["dirs"].setdefault(
                directory,
                {"dirs": {}, "files": []}
            )

        # Add file to its parent directory
        current["files"].append((parts[-1], relative_path))

    return tree


def render_tree(tree):
    """
    Recursively render directory and file entries as HTML.
    """
    items = []

    # Add directories
    for name, subtree in tree["dirs"].items():
        items.append((
            natural_sort_key(name),
            0,
            name,
            subtree
        ))

    # Add files
    for name, path in tree["files"]:
        items.append((
            natural_sort_key(name),
            1,
            name,
            path
        ))

    # Sort folders and files naturally
    items.sort(key=lambda item: (item[0], item[1]))

    html = ["<ul>"]

    for _, item_type, name, value in items:
        if item_type == 0:
            # Directory
            html.append(
                f"<li><strong>{escape(name)}</strong>"
                f"{render_tree(value)}</li>"
            )
        else:
            # HTML file
            relative_path = value.as_posix()
            href = quote(relative_path, safe="/")

            html.append(
                f'<li><a href="{href}">{escape(name)}</a></li>'
            )

    html.append("</ul>")

    return "\n".join(html)


# Discover all HTML files recursively
html_files = [
    file
    for file in ROOT.rglob("*")
    if file.is_file()
    and file.suffix.lower() == ".html"
    and file != OUTPUT
    and not any(
        part in EXCLUDED_DIRS
        for part in file.relative_to(ROOT).parts
    )
]

# Build directory tree
tree = create_tree(html_files)

# Generate HTML index
index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>My HTML Pages</title>
</head>
<body>
    <h1>My HTML Pages</h1>
    {render_tree(tree)}
</body>
</html>
"""

OUTPUT.write_text(index_content, encoding="utf-8")

print(f"Generated {OUTPUT} with {len(html_files)} pages.")
