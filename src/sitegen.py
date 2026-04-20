import os
from markdown_utils import markdown_to_html_node, extract_title
from pathlib import Path

def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def generate_page(from_path: str, template_path: str, dest_path: str):
    """
    Generate a full HTML page.

    - Prints a status message.
    - Reads markdown from from_path and template from template_path.
    - Converts markdown to HTML via markdown_to_html_node(...).to_html().
    - Extracts H1 title via extract_title(...).
    - Replaces {{ Title }} and {{ Content }} in the template.
    - Writes output to dest_path, creating parent dirs as needed.
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    # Read markdown
    with open(from_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Read template
    with open(template_path, "r", encoding="utf-8") as f:
        tpl_text = f.read()

    # Convert markdown to HTML string
    node = markdown_to_html_node(md_text)
    content_html = node.to_html()

    # Extract title (will raise if no H1)
    title = extract_title(md_text)

    # Replace placeholders
    page_html = tpl_text.replace("{{ Title }}", title).replace("{{ Content }}", content_html)

    # Ensure destination directory exists
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    # Write output
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(page_html)

def generate_pages_recursive(dir_path_content: str, template_path: str, dest_dir_path: str):
    """
    Walk dir_path_content recursively. For each *.md file:
      - generate HTML using template_path
      - write to dest_dir_path preserving relative paths, replacing .md with .html
    """
    content_root = Path(dir_path_content)
    dest_root = Path(dest_dir_path)
    if not content_root.exists():
        raise FileNotFoundError(f"Content dir not found: {content_root}")

    for p in content_root.rglob("*.md"):
        rel = p.relative_to(content_root)               # e.g., "blog/post.md" or "index.md"
        dest_rel = rel.with_suffix(".html")             # "blog/post.html"
        src_path = str(p)
        dest_path = str(dest_root.joinpath(dest_rel))
        # ensure parent exists and generate
        _ensure_dir(os.path.dirname(dest_path))
        generate_page(src_path, template_path, dest_path)