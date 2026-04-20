# src/main.py
import os
import sys
from copystatic import copy_tree_clean
from sitegen import generate_pages_recursive

def main():
    src_static = "./static"
    dst_dir = "./docs"        # changed from "./public"
    ##content_md = "./content/index.md"
    content_dir = "./content"
    template_html = "./template.html"
    ##dest_html = os.path.join(dst_public, "index.html")

    # CLI: optional first argument is basepath (default "/")
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"

    try:
        copy_tree_clean(src_static, dst_dir)
        # generate_page(content_md, template_html, dest_html)
        generate_pages_recursive(content_dir, template_html, dst_dir, basepath)
        print("Build complete.")
    except Exception as e:
        print("Build failed:", e)
        raise

if __name__ == "__main__":
    main()
