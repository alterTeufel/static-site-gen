# src/copystatic.py
import os
import shutil

def _ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def copy_tree_clean(src_dir: str, dst_dir: str):
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"Source directory does not exist: {src_dir}")

    # remove existing destination for clean copy
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    _ensure_dir(dst_dir)

    def _copy_recursive(src, dst):
        for name in os.listdir(src):
            src_path = os.path.join(src, name)
            dst_path = os.path.join(dst, name)
            if os.path.isfile(src_path):
                shutil.copy(src_path, dst_path)
                print(f"Copied: {src_path} -> {dst_path}")
            elif os.path.isdir(src_path):
                _ensure_dir(dst_path)
                _copy_recursive(src_path, dst_path)
            # ignore other file types (symlinks/dev) or handle as needed

    _copy_recursive(src_dir, dst_dir)
