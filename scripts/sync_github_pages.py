#!/usr/bin/env python3
"""Prepare a GitHub Pages branch-publishing folder from the public static map."""
from pathlib import Path
import shutil

source = Path("public")
target = Path("docs")
target.mkdir(exist_ok=True)

html = (source / "index.html").read_text(encoding="utf-8")
# GitHub Pages project sites use a repository subpath, so a root-relative favicon path would not resolve.
html = html.replace('href="/logo.svg"', 'href="logo.svg"')
(target / "index.html").write_text(html, encoding="utf-8")
shutil.copy2(source / "logo.svg", target / "logo.svg")
(target / ".nojekyll").write_text("", encoding="utf-8")
print("GitHub Pages source prepared in docs/")
