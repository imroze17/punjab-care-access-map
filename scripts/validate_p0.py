#!/usr/bin/env python3
"""Deterministic P0/P1/P2 scaffold validation for the Punjab Care Access static build."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROHIBITED_TERM = "wave" + "front"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def extract_runtime_data(script: str):
    match = re.fullmatch(r"window\.PCA_RUNTIME = (.*);\n?", script, flags=re.S)
    if not match:
        raise AssertionError("could not locate the runtime-data assignment")
    return json.loads(match.group(1))


def check_javascript(node: str, path: Path) -> None:
    result = subprocess.run([node, "--check", str(path)], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"JavaScript syntax check failed for {path.name}:\n{result.stderr}")


# Smallest interface text the redesign permits, in rem at a 16px root (handoff §8.3).
MIN_UI_TEXT_REM = 0.875

# Tokens whose values were contrast-checked in design/CONTRAST_TABLE.md. Changing a
# value here without re-measuring re-opens the UX-07 defect, so the validator pins them.
PINNED_TOKENS = {
    "--color-text": "#202522",
    "--color-text-secondary": "#59645f",
    "--color-primary": "#246b52",
    "--color-page": "#f3f4f8",
    "--color-surface": "#ffffff",
    "--color-control-border": "#738078",
    "--color-focus": "#073b9b",
    "--text-xs": "0.875rem",
    "--text-sm": "0.9375rem",
    "--text-base": "1rem",
    "--text-card": "1.125rem",
}


def check_phase1_visual_tokens(app_css: str) -> None:
    """Phase 1 redesign guards: token layer present, no sub-14px interface text.

    The pre-redesign build rendered 17 of 17 probed interface text styles below
    14px and failed WCAG AA on five muted-grey pairs. These assertions stop both
    from silently returning.
    """
    # 1. The token layer must be concatenated first so later rules can consume it.
    if ":root {" not in app_css:
        raise AssertionError("design token :root block missing from generated app.css")
    token_block_end = app_css.index("}", app_css.index(":root {"))
    if token_block_end > app_css.index("html, body"):
        raise AssertionError("src/tokens.css must be concatenated ahead of base-style.css")

    # 2. Contrast-checked token values must not drift.
    for token, expected in PINNED_TOKENS.items():
        match = re.search(rf"{re.escape(token)}:\s*([^;]+);", app_css)
        if not match:
            raise AssertionError(f"required design token {token} missing from app.css")
        actual = match.group(1).strip().lower()
        if actual != expected:
            raise AssertionError(
                f"token {token} is {actual!r}, expected {expected!r}. "
                "Re-measure contrast and update design/CONTRAST_TABLE.md before changing this."
            )

    # 3. No interface text below 14px. rem-based sizes are interface text; the few
    #    remaining px sizes are SVG map glyphs (district labels/counts), which are
    #    graphical encodings sized in user units, not document text.
    offenders = sorted(
        {
            value
            for value in re.findall(r"font-size:\s*([0-9.]+)rem", app_css)
            if float(value) < MIN_UI_TEXT_REM
        },
        key=float,
    )
    if offenders:
        raise AssertionError(
            "interface text below the "
            f"{MIN_UI_TEXT_REM}rem ({MIN_UI_TEXT_REM * 16:.0f}px) floor: "
            + ", ".join(f"{value}rem" for value in offenders)
        )

    # 4. Translucent legend/map-note panels made the measured ratio depend on map
    #    content (handoff §9.5); both must now sit on an opaque surface.
    for selector in (".map-note {", ".legend {"):
        block = app_css[app_css.index(selector) : app_css.index("}", app_css.index(selector))]
        if "rgba(255,255,255" in block.replace(" ", "") or "0.92" in block:
            raise AssertionError(f"{selector.strip(' {')} must use an opaque background surface")


def main() -> None:
    canonical = read_json(ROOT / "data/canonical/punjab-care-records.v1.json")
    crosswalk = read_json(ROOT / "data/migrations/legacy-id-crosswalk.v1.json")
    report = read_json(ROOT / "data/reviews/duplicate-candidates.v1.json")
    aliases = read_json(ROOT / "data/config/district-aliases.v1.json")
    public_config = read_json(ROOT / "data/config/public-site-config.v1.json")
    english = read_json(ROOT / "data/locales/en.v1.json")
    overlays = read_json(ROOT / "data/reviewed/locale-overlays.v1.json")
    evidence = read_json(ROOT / "data/reviewed/access-evidence.v1.json")
    runtime_payload = read_json(ROOT / "data/generated/runtime-records.v1.json")
    build_manifest = read_json(ROOT / "data/generated/build-manifest.v1.json")
    public_dir = ROOT / "public"
    docs_dir = ROOT / "docs"
    public_html = (public_dir / "index.html").read_text(encoding="utf-8")
    docs_html = (docs_dir / "index.html").read_text(encoding="utf-8")
    app_js = (public_dir / "app.js").read_text(encoding="utf-8")
    app_css = (public_dir / "app.css").read_text(encoding="utf-8")
    runtime_js = (public_dir / "runtime-data.js").read_text(encoding="utf-8")

    records = canonical["records"]
    assert canonical["schemaVersion"] == "pca-record/v1"
    assert len(records) == 112 == canonical["sourceRecordCount"]
    assert len({record["recordId"] for record in records}) == 112
    assert len({record["legacyIds"][0] for record in records}) == 112
    assert len({record["sourceObservations"][0]["sourceRowNumber"] for record in records}) == 112
    assert all(record["sourceObservations"][0]["sourceRowNumber"] >= 2 for record in records)
    assert all(record["location"]["verifiedCoordinates"] is None for record in records)
    assert all(record["mapPresentation"]["isVerifiedGeocode"] is False for record in records)
    assert all(record["mapPresentation"]["coordinatePrecision"] == "not_geocoded" for record in records)
    assert all(record["recordKind"]["derivation"] == "source_text_rule" for record in records)
    assert all(record["ownershipClaim"]["derivation"] == "source_text_rule" for record in records)

    mappings = crosswalk["mappings"]
    assert len(mappings) == 112
    assert {mapping["recordId"] for mapping in mappings} == {record["recordId"] for record in records}
    assert {mapping["legacyId"] for mapping in mappings} == {record["legacyIds"][0] for record in records}
    assert all(candidate["review"]["status"] == "unreviewed" for candidate in report["candidates"])
    assert all("legacyIds" in candidate["left"] and "legacyIds" in candidate["right"] for candidate in report["candidates"])
    assert report["notice"].startswith("Candidates are review prompts")

    assert aliases["schemaVersion"] == "pca-district-aliases/v1"
    alias_names = [item["name"] for item in aliases["districts"]]
    assert len(alias_names) == 23 == len(set(alias_names))
    assert public_config["schemaVersion"] == "pca-public-site-config/v1"
    assert public_config["publishedLocales"] == ["en"]
    assert public_config["canonicalPublicUrl"] is None and public_config["correctionRoute"] is None
    assert english["schemaVersion"] == "pca-locale/v1" and english["locale"] == "en"
    assert english["status"] == "approved_source_interface" and bool(english["messages"])
    assert overlays == {"schemaVersion": "pca-reviewed-locales/v1", "overlays": [], "notice": overlays["notice"]}
    assert evidence == {"schemaVersion": "pca-access-evidence/v1", "entries": [], "notice": evidence["notice"]}
    assert (ROOT / "data/schemas/pca-localized-content-v1.schema.json").is_file()
    assert (ROOT / "data/schemas/pca-access-evidence-v1.schema.json").is_file()

    runtime = runtime_payload["records"]
    assert len(runtime) == 112
    assert all(not {"lat", "lon", "latitude", "longitude"} & set(record) for record in runtime)
    assert sum(record["mapRepresentation"] == "district_group_summary" for record in runtime) == 108
    assert sum(record["mapRepresentation"] == "coverage_scope_control" for record in runtime) == 4
    assert len({record["mapDistrict"] for record in runtime if record["mapRepresentation"] == "district_group_summary"}) == 22
    assert build_manifest["schemaVersion"] == "pca-build-manifest/v2"
    assert build_manifest["coordinatesPublished"] is False
    assert build_manifest["publishedLocales"] == ["en"]

    embedded = extract_runtime_data(runtime_js)
    assert embedded["records"] == runtime
    assert embedded["buildManifest"] == build_manifest
    assert embedded["districtAliases"] == aliases
    assert embedded["publicConfig"] == public_config
    assert embedded["localeMessages"] == english["messages"]

    assert "<style" not in public_html and "style=" not in public_html
    assert "<script>" not in public_html
    assert '<link rel="stylesheet" href="app.css">' in public_html
    assert '<script src="runtime-data.js" defer></script>' in public_html
    assert '<script src="app.js" defer></script>' in public_html
    assert "Content-Security-Policy" in public_html and "unsafe-inline" not in public_html
    assert "default-src 'self'" in public_html and "script-src 'self'" in public_html and "style-src 'self'" in public_html
    assert 'id="main-content"' in public_html and 'id="directory-results"' in public_html and 'id="appStatus"' in public_html
    assert 'id="districtSelect"' in public_html and 'data-view="list"' in public_html and 'data-view="map"' in public_html
    assert 'id="regionLayer" type="checkbox" checked' not in public_html and 'id="riverLayer" type="checkbox" checked' not in public_html
    assert "project(f.lat" not in app_js and "project(f.lon" not in app_js
    assert "district-summary-marker" in app_js
    assert "grouped by reported district or coverage scope—not facility locations" in app_js
    assert "Source ownership claim" in app_js
    assert "tel:" not in app_js and "innerHTML" not in app_js and "alert(" not in app_js
    assert "localStorage" not in app_js and "sessionStorage" not in app_js and "navigator.geolocation" not in app_js
    assert "__P0_" not in public_html and "__P1_" not in app_js and "__PCA_" not in app_js and "__MSG_" not in public_html and "__RUNTIME_" not in public_html
    assert 'id="printContext"' in public_html and "p1RenderPrintContext" in app_js and "printContext" in app_js
    assert "selectionNoLongerMatches" in app_js and "p1CurrentSelectionIsVisible(p1ActiveFacilities())" in app_js
    assert "@media print" in app_css and "prefers-reduced-motion" in app_css and ".skip-link" in app_css and ".print-context" in app_css

    check_phase1_visual_tokens(app_css)

    assert docs_html == public_html.replace('href="/logo.svg"', 'href="logo.svg"', 1)
    for name in ("app.css", "app.js", "runtime-data.js", "logo.svg", "manus-routes.json"):
        assert (public_dir / name).read_bytes() == (docs_dir / name).read_bytes(), f"Pages asset drift: {name}"
    assert (docs_dir / ".nojekyll").is_file()
    assert read_json(public_dir / "manus-routes.json") == {"routes": [{"path": "/", "title": "Punjab Care Access Map"}]}

    workflow = (ROOT / ".github/workflows/site.yml").read_text(encoding="utf-8")
    required_action_pins = {
        "actions/checkout": "d23441a48e516b6c34aea4fa41551a30e30af803",
        "actions/setup-python": "a26af69be951a213d495a4c3e4e4022e16d87065",
        "actions/setup-node": "49933ea5288caeca8642d1e84afbd3f7d6820020",
        "actions/configure-pages": "983d7736d9b0ae728b81ab479565c72886d7745b",
        "actions/upload-pages-artifact": "7b1f4a764d45c48632c6b24a0339c27f5614fb0b",
        "actions/deploy-pages": "d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e",
    }
    assert "run: make check" in workflow and "path: docs" in workflow
    assert "pages: write" in workflow and "id-token: write" in workflow and "name: github-pages" in workflow
    assert all(f"{action}@{commit}" in workflow for action, commit in required_action_pins.items())
    for filename in (
        "RELEASE_RUNBOOK.md", "PRIVACY_AND_SECURITY.md", "ACCESSIBILITY_NOTES.md",
        "MAINTAINER_CHECKLIST.md", "TEST_REPORT.md", "QUALITY_REPORT.md", "LOCALE_AND_EVIDENCE_GOVERNANCE.md",
    ):
        assert (ROOT / filename).is_file(), f"required P1/P2 document missing: {filename}"

    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is required for static JavaScript syntax validation")
    check_javascript(node, public_dir / "app.js")
    check_javascript(node, public_dir / "runtime-data.js")

    project_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts and path.suffix in {".md", ".py", ".js", ".css", ".html", ".json", ".yml", ".yaml", ".txt"})
    assert PROHIBITED_TERM not in project_text.lower()
    active_sources = [
        ROOT / "Makefile", ROOT / "src/template.html", ROOT / "src/base-runtime.js", ROOT / "src/base-style.css",
        ROOT / "src/tokens.css",
        ROOT / "src/p0-helpers.js", ROOT / "src/p1-runtime.js", ROOT / "src/p1-style.css",
        ROOT / "scripts/build_p0.py", ROOT / "scripts/sync_github_pages.py", ROOT / "scripts/import_legacy_source.py", ROOT / "scripts/validate_p0.py",
    ]
    active_text = "\n".join(path.read_text(encoding="utf-8") for path in active_sources)
    assert "/home/ubuntu/" + "upload" not in active_text

    print("P1/P2 validation passed: lineage, coordinate-free records, modular CSP output, Pages synchronization, English-only gating, and public-safe static assets are coherent.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ValueError, RuntimeError) as error:
        print(f"P1/P2 validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
