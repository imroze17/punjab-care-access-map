#!/usr/bin/env python3
"""One-time migration from the P0 inline document to a P1 modular static shell.

It extracts the committed base CSS and map/runtime JavaScript into source files, then rewrites
`src/template.html` as a semantic shell that loads only same-origin assets. This command is
intentionally guarded: run it once against the P0 source, then maintain the extracted sources.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "src/template.html"
BASE_STYLE = ROOT / "src/base-style.css"
BASE_RUNTIME = ROOT / "src/base-runtime.js"


def replace_once(value: str, old: str, new: str, label: str) -> str:
    count = value.count(old)
    if count != 1:
        raise ValueError(f"expected one {label} replacement, found {count}")
    return value.replace(old, new)


def main() -> None:
    source = TEMPLATE.read_text(encoding="utf-8")
    if 'src="runtime-data.js"' in source:
        raise SystemExit("P1 shell already exists; this one-time migration must not be rerun")

    style_match = re.search(r"<style>(.*?)</style>", source, flags=re.S)
    script_match = re.search(r"<script>(.*?)</script>", source, flags=re.S)
    if not style_match or not script_match:
        raise ValueError("could not locate exactly one inline style and script block")

    base_style = style_match.group(1).replace("__P0_STYLE__", "").strip() + "\n"
    base_runtime = script_match.group(1)
    base_runtime = replace_once(
        base_runtime,
        "const facilities = __RUNTIME_RECORDS_JSON__;\nconst datasetManifest = __DATASET_MANIFEST_JSON__;",
        "const { records: facilities, buildManifest: datasetManifest, districtAliases, publicConfig, localeMessages } = window.PCA_RUNTIME;",
        "runtime-data bootstrap",
    )
    base_runtime = replace_once(base_runtime, "__P0_RUNTIME_JS__", "__P1_RUNTIME_JS__", "P1 runtime placeholder")
    old_export_style = "function exportStyleText() { return Array.from(document.querySelectorAll('style')).map(style=>style.textContent).join('\\n'); }"
    base_runtime = replace_once(base_runtime, old_export_style, "function exportStyleText() { return __PCA_EXPORT_CSS__; }", "export CSS bridge")

    shell = source[:style_match.start()] + '<link rel="stylesheet" href="app.css">' + source[style_match.end():script_match.start()] + '<script src="runtime-data.js" defer></script>\n<script src="app.js" defer></script>' + source[script_match.end():]
    shell = replace_once(
        shell,
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; script-src \'self\'; style-src \'self\'; img-src \'self\' data: blob:; connect-src \'self\'; object-src \'none\'; base-uri \'self\'; form-action \'none\'">',
        "CSP meta",
    )
    shell = replace_once(shell, '<body>\n', '<body>\n<a class="skip-link" href="#directory-results">Skip to directory results</a>\n', "skip link")
    shell = replace_once(shell, '<div class="workspace">', '<main id="main-content"><div class="workspace">', "main wrapper")
    shell = replace_once(shell, '    <aside aria-label="Map filters and facility list">', '    <aside aria-labelledby="directoryHeading">\n      <h2 id="directoryHeading" class="visually-hidden">Directory controls and results</h2>', "directory landmark")
    shell = replace_once(shell, '<div class="section-label">Find a listing</div>', '<div class="view-controls" role="group" aria-label="Choose directory or map view"><button type="button" data-view="list" aria-pressed="true">List</button><button type="button" data-view="map" aria-pressed="false">Map</button></div>\n      <div class="section-label">Find a listing</div>', "view controls")
    shell = replace_once(shell, '<div class="search-wrap"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></svg><input id="search" type="search" placeholder="Search name, district, address…" aria-label="Search listed facilities"></div>', '<div class="section-label">District</div><select id="districtSelect" class="type-select" aria-label="Choose a Punjab district"><option value="">All Punjab districts</option></select>\n      <div class="search-wrap"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></svg><input id="search" type="search" placeholder="Search name, district, address…" aria-label="Search listed directory records"></div>', "district select")
    shell = replace_once(shell, '<div class="section-label">Service type</div>', '<div class="section-label">Source record role</div>', "role label")
    shell = replace_once(shell, '<div class="section-label">Map layers</div>\n      <div class="control-card">', '<details class="map-layer-details"><summary>Explore map layers</summary><div class="control-card">', "layer details open")
    shell = replace_once(shell, '      <div id="selection" class="selection" aria-live="polite"></div>', '      </div></details>\n      <section id="directory-results" tabindex="-1" aria-labelledby="resultsHeading"><div id="selection" class="selection"></div>', "results section open")
    shell = replace_once(shell, '<div class="result-head"><div class="section-label">Index entries <span id="resultCount"></span></div><button id="download" class="small-action" title="Download the currently visible rows as CSV">Export CSV</button></div>\n      <div id="activeContext" class="active-context"><span id="contextText"></span><button id="clearDistrict">Clear</button></div>\n      <div id="facilityList" class="facility-list"></div>\n    </aside>', '<div class="result-head"><h2 id="resultsHeading" class="section-label">Directory entries <span id="resultCount"></span></h2><div class="result-actions"><button id="clearFilters" class="small-action" type="button">Clear filters</button><button id="download" class="small-action" type="button">Export CSV</button><button id="printDirectory" class="small-action" type="button">Print directory</button></div></div>\n      <div id="activeFilterChips" class="filter-chips" aria-label="Active directory filters"></div>\n      <div id="activeContext" class="active-context"><span id="contextText"></span><button id="clearDistrict" type="button">Clear district</button></div>\n      <div id="facilityList" class="facility-list"></div></section>\n    </aside>', "results section and actions")
    shell = replace_once(shell, '    <main>\n      <div class="map-topline"><div class="map-title"><h2>Explore the service landscape</h2>', '    <section id="mapPanel" class="map-panel" aria-labelledby="mapHeading">\n      <div class="map-topline"><div class="map-title"><h2 id="mapHeading">Explore the service landscape</h2>', "map section")
    shell = replace_once(shell, '    </main>\n  </div>\n</div>', '    </section>\n  </div></main>\n</div>', "main close")
    shell = shell.replace(' id="regionLayer" type="checkbox" checked', ' id="regionLayer" type="checkbox"')
    shell = shell.replace(' data-region="Majha" checked', ' data-region="Majha"')
    shell = shell.replace(' data-region="Doaba" checked', ' data-region="Doaba"')
    shell = shell.replace(' data-region="Malwa" checked', ' data-region="Malwa"')
    shell = shell.replace(' data-region="Puadh" checked', ' data-region="Puadh"')
    shell = shell.replace(' id="regionLabels" type="checkbox" checked', ' id="regionLabels" type="checkbox"')
    shell = shell.replace(' id="riverLayer" type="checkbox" checked', ' id="riverLayer" type="checkbox"')
    shell = shell.replace(' id="riverLabels" type="checkbox" checked', ' id="riverLabels" type="checkbox"')
    shell = shell.replace('target="_blank" rel="noopener"', 'target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer"')
    shell = replace_once(shell, '  </header>\n  <main id="main-content">', '  </header>\n  <p id="appStatus" class="app-status" role="status" aria-live="polite" aria-atomic="true"></p>\n  <main id="main-content">', "status region")

    BASE_STYLE.write_text(base_style, encoding="utf-8")
    BASE_RUNTIME.write_text(base_runtime.strip() + "\n", encoding="utf-8")
    TEMPLATE.write_text(shell, encoding="utf-8")
    print(f"Created {BASE_STYLE.name}, {BASE_RUNTIME.name}, and modular {TEMPLATE.name}")


if __name__ == "__main__":
    main()
