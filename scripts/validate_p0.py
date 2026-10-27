#!/usr/bin/env python3
"""Deterministic validation for the Punjab Care Access P0 static build."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def extract_runtime(html: str):
    match = re.search(r"const facilities = (.*?);\nconst datasetManifest =", html, flags=re.S)
    if not match:
        raise AssertionError("could not locate embedded runtime records")
    return json.loads(match.group(1))


def main() -> None:
    canonical = read_json(ROOT / "data/canonical/punjab-care-records.v1.json")
    crosswalk = read_json(ROOT / "data/migrations/legacy-id-crosswalk.v1.json")
    report = read_json(ROOT / "data/reviews/duplicate-candidates.v1.json")
    runtime_payload = read_json(ROOT / "data/generated/runtime-records.v1.json")
    build_manifest = read_json(ROOT / "data/generated/build-manifest.v1.json")
    public_html = (ROOT / "public/index.html").read_text(encoding="utf-8")
    docs_html = (ROOT / "docs/index.html").read_text(encoding="utf-8")

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

    runtime = runtime_payload["records"]
    assert len(runtime) == 112
    assert all("lat" not in record and "lon" not in record for record in runtime)
    assert sum(record["mapRepresentation"] == "district_group_summary" for record in runtime) == 108
    assert sum(record["mapRepresentation"] == "coverage_scope_control" for record in runtime) == 4
    assert len({record["mapDistrict"] for record in runtime if record["mapRepresentation"] == "district_group_summary"}) == 22
    assert build_manifest["coordinatesPublished"] is False

    embedded = extract_runtime(public_html)
    assert embedded == runtime
    assert "project(f.lat" not in public_html
    assert "district-summary-marker" in public_html
    assert "grouped by reported district or coverage scope—not facility locations" in public_html
    assert "select a marker for the supplied listing" not in public_html
    assert "Marks are display anchors, not rooftop geocodes" not in public_html
    assert "Source ownership claim" in public_html
    assert "__P0_" not in public_html and "__RUNTIME_" not in public_html
    assert docs_html == public_html.replace('href="/logo.svg"', 'href="logo.svg"', 1)
    assert (ROOT / "docs/.nojekyll").is_file()
    assert (ROOT / "public/logo.svg").read_bytes() == (ROOT / "docs/logo.svg").read_bytes()
    assert read_json(ROOT / "public/manus-routes.json") == {"routes": [{"path": "/", "title": "Punjab Care Access Map"}]}

    script_blocks = re.findall(r"<script>(.*?)</script>", public_html, flags=re.S)
    assert len(script_blocks) == 1
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is required for static JavaScript syntax validation")
    result = subprocess.run([node, "-e", "const vm=require('vm');new vm.Script(require('fs').readFileSync(0,'utf8'));"], input=script_blocks[0], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"inline JavaScript syntax check failed:\n{result.stderr}")
    print("P0 validation passed: canonical lineage, coordinate-free runtime, generated site, Pages copy, and inline JavaScript are coherent.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ValueError, RuntimeError) as error:
        print(f"P0 validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
