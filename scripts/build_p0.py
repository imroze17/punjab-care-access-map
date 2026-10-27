#!/usr/bin/env python3
"""Build the Punjab Care Access P0 static runtime from committed canonical records."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL = ROOT / "data/canonical/punjab-care-records.v1.json"
DEFAULT_MANIFEST = ROOT / "data/manifests/source-artifact.v1.json"
DEFAULT_TEMPLATE = ROOT / "src/template.html"
DEFAULT_RUNTIME_JS = ROOT / "src/p0-runtime.js"
DEFAULT_STYLE = ROOT / "src/p0-style.css"
DEFAULT_LOGO = ROOT / "src/logo.svg"
DEFAULT_OUTPUT = ROOT / "public"

OWNERSHIP_LABELS = {
    "government_claim": "Government claim",
    "ngo_or_trust_claim": "NGO / trust claim",
    "private_claim": "Private claim",
    "mixed_or_ambiguous_claim": "Mixed / not stated",
    "not_stated": "Mixed / not stated",
}
RECORD_KIND_LABELS = {
    "site_or_provider_record": "Source site / provider record",
    "administrative_or_coordination_record": "Coordination / administrative record",
    "helpline_or_information_record": "Helpline / information record",
    "coverage_or_multi_site_record": "Multi-site / coverage record",
}
SCOPE_LABELS = {
    "statewide": "Statewide coverage",
    "multi_district": "Punjab-wide / multi-district coverage",
    "multiple_sites_within_district": "Multiple sites within reported district",
    "not_stated_or_single_site": "Reported district",
}
MENTION_LABELS = {
    "ooat_mentioned": "OOAT (source term)",
    "mmt_or_methadone_mentioned": "MMT / methadone (source term)",
    "ddtc_mentioned": "DDTC (source term)",
    "ost_mentioned": "OST (source term)",
    "model_centre_mentioned": "Model centre (source term)",
    "rehabilitation_mentioned": "Rehabilitation (source term)",
    "helpline_mentioned": "Helpline (source term)",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def public_remarks(value: str) -> str:
    import re
    return re.sub(r"\[reference:[^\]]+\]", "", value, flags=re.I).strip()


def runtime_record(record: dict[str, Any], dataset_version: str) -> dict[str, Any]:
    observation = record["sourceObservations"][0]
    fields = observation["parsedFields"]
    presentation = record["mapPresentation"]
    coverage = record["coverage"]
    scope = coverage["scope"]
    area = presentation["displayAnchorArea"]
    display_scope = SCOPE_LABELS[scope] if not area else (f"Reported district: {area}" if scope == "not_stated_or_single_site" else f"Reported district: {area} (multiple sites noted)")
    return {
        "id": record["recordId"],
        "legacyId": ", ".join(record["legacyIds"]),
        "Name": fields["name"],
        "District": fields["district"],
        "Address": fields["address"],
        "Type": fields["type"],
        "Contact": fields["contact"],
        "Remarks": public_remarks(fields["remarks"]),
        "sourceRow": observation["sourceRowNumber"],
        "recordKind": record["recordKind"]["value"],
        "recordKindLabel": RECORD_KIND_LABELS[record["recordKind"]["value"]],
        "ownershipClaim": record["ownershipClaim"]["value"],
        "ownershipLabel": OWNERSHIP_LABELS[record["ownershipClaim"]["value"]],
        "serviceMentionLabels": [MENTION_LABELS[item["code"]] for item in record["serviceMentions"] if item["code"] in MENTION_LABELS],
        "coverageScope": scope,
        "displayScope": display_scope,
        "locationPrecision": record["location"]["sourceAddressGranularity"],
        "mapRepresentation": presentation["representation"],
        "mapDistrict": area or "",
        "region": presentation["editorialRegion"],
        "datasetVersion": dataset_version,
    }


def assert_runtime(records: list[dict[str, Any]]) -> None:
    if len(records) != 112:
        raise ValueError(f"expected 112 runtime records, found {len(records)}")
    ids = [record["id"] for record in records]
    if len(set(ids)) != len(ids):
        raise ValueError("runtime record IDs are not unique")
    if any("lat" in record or "lon" in record for record in records):
        raise ValueError("runtime records must not contain coordinates")
    district_records = [record for record in records if record["mapRepresentation"] == "district_group_summary"]
    coverage_records = [record for record in records if record["mapRepresentation"] == "coverage_scope_control"]
    if len(district_records) != 108 or len(coverage_records) != 4:
        raise ValueError(f"expected 108 district-group and 4 coverage records, got {len(district_records)} and {len(coverage_records)}")
    if len({record["mapDistrict"] for record in district_records}) != 22:
        raise ValueError("expected 22 mapped district groups")
    if set(record["coverageScope"] for record in coverage_records) != {"multi_district", "statewide"}:
        raise ValueError("coverage controls must include multi-district and statewide records")


def escape_script_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", default=DEFAULT_CANONICAL, type=Path)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, type=Path)
    parser.add_argument("--template", default=DEFAULT_TEMPLATE, type=Path)
    parser.add_argument("--runtime-js", default=DEFAULT_RUNTIME_JS, type=Path)
    parser.add_argument("--style", default=DEFAULT_STYLE, type=Path)
    parser.add_argument("--logo", default=DEFAULT_LOGO, type=Path)
    parser.add_argument("--out-dir", default=DEFAULT_OUTPUT, type=Path)
    args = parser.parse_args()

    canonical = read_json(args.canonical)
    manifest = read_json(args.manifest)
    if canonical["schemaVersion"] != "pca-record/v1":
        raise ValueError("unexpected canonical schema version")
    if canonical["sourceRecordCount"] != len(canonical["records"]):
        raise ValueError("canonical sourceRecordCount does not match records")
    dataset_version = canonical["datasetVersion"]
    runtime = [runtime_record(record, dataset_version) for record in canonical["records"]]
    assert_runtime(runtime)
    runtime_payload = {"schemaVersion": "pca-runtime/v1", "datasetVersion": dataset_version, "records": runtime}
    build_manifest = {
        "schemaVersion": "pca-build-manifest/v1",
        "datasetVersion": dataset_version,
        "sourceArtifactId": canonical["sourceArtifactId"],
        "sourceArtifactSha256": manifest["sourceArtifact"]["sha256"],
        "sourceRecordCount": len(runtime),
        "districtGroupRecordCount": sum(record["mapRepresentation"] == "district_group_summary" for record in runtime),
        "coverageScopeRecordCount": sum(record["mapRepresentation"] == "coverage_scope_control" for record in runtime),
        "runtimeRecordsSha256": sha256_text(json.dumps(runtime_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))),
        "coordinatesPublished": False,
        "notice": "Runtime records are source-derived directory records grouped by reported district or coverage scope, not verified facility locations.",
    }
    write_json(ROOT / "data/generated/runtime-records.v1.json", runtime_payload)
    write_json(ROOT / "data/generated/build-manifest.v1.json", build_manifest)

    template = args.template.read_text(encoding="utf-8")
    replacements = {
        "__RUNTIME_RECORDS_JSON__": escape_script_json(runtime),
        "__DATASET_MANIFEST_JSON__": escape_script_json(build_manifest),
        "__P0_RUNTIME_JS__": args.runtime_js.read_text(encoding="utf-8"),
        "__P0_STYLE__": args.style.read_text(encoding="utf-8"),
    }
    for token, value in replacements.items():
        if template.count(token) != 1:
            raise ValueError(f"template expected one {token}, found {template.count(token)}")
        template = template.replace(token, value)
    if "__" in template and any(token in template for token in replacements):
        raise ValueError("unreplaced build token remains in template")
    if "project(f.lat" in template or "project(f.lon" in template:
        raise ValueError("legacy coordinate marker code remains in public output")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "index.html").write_text(template, encoding="utf-8")
    shutil.copyfile(args.logo, args.out_dir / "logo.svg")
    (args.out_dir / "manus-routes.json").write_text(json.dumps({"routes": [{"path": "/", "title": "Punjab Care Access Map"}]}) + "\n", encoding="utf-8")
    print(f"Built {args.out_dir / 'index.html'} with {len(runtime)} coordinate-free runtime records")


if __name__ == "__main__":
    main()
