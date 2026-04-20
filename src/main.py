# src/main.py
import os
from copystatic import copy_tree_clean
from sitegen import generate_pages_recursive

def main():
    src_static = "./static"
    dst_public = "./public"
    # content_md = "./content/index.md"
    content_dir = "./content"
    template_html = "./template.html"
    # dest_html = os.path.join(dst_public, "index.html")

    try:
        copy_tree_clean(src_static, dst_public)
        # generate_page(content_md, template_html, dest_html)
        generate_pages_recursive(content_dir, template_html, dst_public)
        print("Build complete.")
    except Exception as e:
        print("Build failed:", e)
        raise

if __name__ == "__main__":
    main()
