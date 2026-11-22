
from pathlib import Path
from html import escape
from urllib.parse import quote
import shutil

ROOT = Path(".")
DIST = Path("dist")

EXCLUDED_DIRS = {
    ".git",
    ".github",
    "scripts",
    "dist",
}

# Remove previous build
if DIST.exists():
    shutil.rmtree(DIST)

DIST.mkdir(parents=True)

# Find all HTML files recursively
html_files = sorted(
    file
    for file in ROOT.rglob("*")
    if file.is_file()
    and file.suffix.lower() == ".html"
    and not any(part in EXCLUDED_DIRS for part in file.parts)
)

# Copy HTML files to dist, preserving directory structure
for file in html_files:
    relative_path = file.relative_to(ROOT)
    destination = DIST / relative_path

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file, destination)

# Generate homepage links
links = []

for file in html_files:
    relative_path = file.relative_to(ROOT).as_posix()

    # Encode URL while preserving directory separators
    href = quote(relative_path, safe="/")

    # Escape HTML text to prevent malformed markup
    title = escape(relative_path)

    links.append(
        f'<li><a href="{href}">{title}</a></li>'
    )

index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>My HTML Pages</title>
</head>
<body>
    <h1>My HTML Pages</h1>
    <ul>
        {"".join(links)}
    </ul>
</body>
</html>
"""

(DIST / "index.html").write_text(
    index_content,
    encoding="utf-8"
)

print(f"Successfully generated index.html with {len(html_files)} pages.")
