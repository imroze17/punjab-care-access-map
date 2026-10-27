#!/usr/bin/env python3
"""Synchronize the generated static site into the GitHub Pages docs/ folder."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=Path("public"), type=Path)
    parser.add_argument("--target", default=Path("docs"), type=Path)
    args = parser.parse_args()
    if not (args.source / "index.html").is_file():
        raise FileNotFoundError(f"source static output missing {args.source / 'index.html'}")
    if args.target.exists():
        shutil.rmtree(args.target)
    shutil.copytree(args.source, args.target)
    index = args.target / "index.html"
    text = index.read_text(encoding="utf-8")
    if 'href="/logo.svg"' not in text:
        raise RuntimeError("expected root-relative logo reference in public output")
    index.write_text(text.replace('href="/logo.svg"', 'href="logo.svg"', 1), encoding="utf-8")
    (args.target / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Synced {args.source} to {args.target} with a GitHub Pages-relative favicon")


if __name__ == "__main__":
    main()
