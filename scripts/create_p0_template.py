#!/usr/bin/env python3
"""One-time migration: turn the approved current static runtime into a committed P0 template."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def replace_between(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[:start] + replacement + text[end:]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=Path("public/index.html"), type=Path)
    parser.add_argument("--output", default=Path("src/template.html"), type=Path)
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8")
    text, substitutions = re.subn(
        r"const facilities = .*?;\nconst districtGeo =",
        "const facilities = __RUNTIME_RECORDS_JSON__;\nconst datasetManifest = __DATASET_MANIFEST_JSON__;\nconst districtGeo =",
        text,
        flags=re.S,
    )
    if substitutions != 1:
        raise RuntimeError(f"expected one embedded facilities block, found {substitutions}")
    text = replace_between(text, "function createMap()", "function downloadBlob", "__P0_RUNTIME_JS__\n\n")
    text = replace_between(text, "function makeExportSvg()", "async function exportMapCanvas", "")
    text = replace_between(text, "function setupControls()", "function svgPoint", "")
    text = replace_between(text, "function exportVisible()", "createMap();", "")
    text, substitutions = re.subn(
        r"createMap\(\);\nconst totals=.*?setupControls\(\);render\(\);",
        "createMap();\np0UpdateOwnershipCounts();\nsetupControls();\nrender();",
        text,
        flags=re.S,
    )
    if substitutions != 1:
        raise RuntimeError(f"expected one old runtime footer, found {substitutions}")
    if "__P0_STYLE__" not in text:
        text = text.replace("</style>", "\n__P0_STYLE__\n</style>", 1)
    for token in ("__RUNTIME_RECORDS_JSON__", "__DATASET_MANIFEST_JSON__", "__P0_RUNTIME_JS__", "__P0_STYLE__"):
        if text.count(token) != 1:
            raise RuntimeError(f"template token {token} appears {text.count(token)} times")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(f"Wrote P0 template to {args.output}")


if __name__ == "__main__":
    main()
