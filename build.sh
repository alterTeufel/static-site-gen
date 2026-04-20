#!/usr/bin/env bash
set -euo pipefail

# Build for production with repository basepath
python3 src/main.py "/static-site-gen/"
