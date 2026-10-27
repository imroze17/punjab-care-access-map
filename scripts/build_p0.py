#!/usr/bin/env python3
"""Build the Punjab Care Access static runtime from committed canonical records.

The public output is deliberately static and coordinate-free. The build emits a semantic HTML
shell plus same-origin CSS, application JavaScript, and runtime-data JavaScript so it can use a
restrictive GitHub-Pages-compatible CSP without inline executable content.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL = ROOT / "data/canonical/punjab-care-records.v1.json"
DEFAULT_MANIFEST = ROOT / "data/manifests/source-artifact.v1.json"
DEFAULT_TEMPLATE = ROOT / "src/template.html"
DEFAULT_BASE_RUNTIME = ROOT / "src/base-runtime.js"
DEFAULT_P0_HELPERS = ROOT / "src/p0-helpers.js"
DEFAULT_P1_RUNTIME = ROOT / "src/p1-runtime.js"
DEFAULT_TOKENS_STYLE = ROOT / "src/tokens.css"
DEFAULT_BASE_STYLE = ROOT / "src/base-style.css"
DEFAULT_P0_STYLE = ROOT / "src/p0-style.css"
DEFAULT_P1_STYLE = ROOT / "src/p1-style.css"
DEFAULT_ALIASES = ROOT / "data/config/district-aliases.v1.json"
DEFAULT_PUBLIC_CONFIG = ROOT / "data/config/public-site-config.v1.json"
DEFAULT_EN_LOCALE = ROOT / "data/locales/en.v1.json"
DEFAULT_LOCALE_OVERLAYS = ROOT / "data/reviewed/locale-overlays.v1.json"
DEFAULT_ACCESS_EVIDENCE = ROOT / "data/reviewed/access-evidence.v1.json"
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

SHELL_MESSAGE_TOKENS = {
    "__MSG_META_DESCRIPTION__": "metaDescription",
    "__MSG_PAGE_TITLE__": "pageTitle",
    "__MSG_OG_DESCRIPTION__": "ogDescription",
    "__MSG_SITE_NAME__": "siteName",
    "__MSG_SITE_TAGLINE__": "siteTagline",
    "__MSG_HEADER_STAT_AFTER__": "headerStatAfter",
    "__MSG_SKIP_TO_RESULTS__": "skipToResults",
    "__MSG_DIRECTORY_HEADING__": "directoryHeading",
    "__MSG_CHOOSE_VIEW__": "chooseView",
    "__MSG_LIST_VIEW__": "listView",
    "__MSG_MAP_VIEW__": "mapView",
    "__MSG_FIND_LISTING__": "findListing",
    "__MSG_DISTRICT__": "district",
    "__MSG_CHOOSE_DISTRICT__": "chooseDistrict",
    "__MSG_ALL_PUNJAB_DISTRICTS__": "allPunjabDistricts",
    "__MSG_SEARCH_PLACEHOLDER__": "searchPlaceholder",
    "__MSG_SEARCH_DIRECTORY__": "searchDirectory",
    "__MSG_SOURCE_OWNERSHIP_CLAIM__": "sourceOwnershipClaim",
    "__MSG_SOURCE_OWNERSHIP_CLAIM_FILTERS__": "sourceOwnershipClaimFilters",
    "__MSG_SOURCE_RECORD_ROLE__": "sourceRecordRole",
    "__MSG_ALL_SOURCE_RECORD_ROLES__": "allSourceRecordRoles",
    "__MSG_MAP_LAYERS__": "mapLayers",
    "__MSG_TOGGLE_CULTURAL_REGIONS__": "toggleCulturalRegions",
    "__MSG_DISTRICT_BOUNDARIES__": "districtBoundaries",
    "__MSG_DISTRICT_LABELS__": "districtLabels",
    "__MSG_CULTURAL_REGION_WASH__": "culturalRegionWash",
    "__MSG_REGIONAL_LABELS__": "regionalLabels",
    "__MSG_MAJOR_RIVERS__": "majorRivers",
    "__MSG_RIVER_LABELS__": "riverLabels",
    "__MSG_DIRECTORY_ENTRIES__": "directoryEntries",
    "__MSG_CLEAR_FILTERS__": "clearFilters",
    "__MSG_CLEAR_DISTRICT__": "clearDistrict",
    "__MSG_EXPORT_CSV__": "exportCsv",
    "__MSG_PRINT_DIRECTORY__": "printDirectory",
    "__MSG_PRINT_CONTEXT_HEADING__": "printContextHeading",
    "__MSG_MAP_HEADING__": "mapHeading",
    "__MSG_MAP_DESCRIPTION__": "mapDescription",
    "__MSG_VISIBLE_LISTINGS__": "visibleListings",
    "__MSG_DISTRICT_GROUPS__": "districtGroups",
    "__MSG_COVERAGE_RECORDS__": "coverageRecords",
    "__MSG_DOWNLOAD_MAP__": "downloadMap",
    "__MSG_MAP_EXPORT__": "mapExport",
    "__MSG_MAP_ARIA__": "mapAria",
    "__MSG_ZOOM_IN__": "zoomIn",
    "__MSG_ZOOM_OUT__": "zoomOut",
    "__MSG_RESET_MAP__": "resetMap",
    "__MSG_MAP_NOTE__": "mapNote",
    "__MSG_MAP_SYMBOL__": "mapSymbol",
    "__MSG_DISTRICT_GROUP_COUNT__": "districtGroupCount",
    "__MSG_INDIVIDUAL_LOCATIONS_NOT_MAPPED__": "individualLocationsNotMapped",
    "__MSG_LABELLED_RIVERS__": "labelledRivers",
    "__MSG_FOOTER_MAP_NOTES__": "footerMapNotes",
}

RUNTIME_MESSAGE_KEYS = {
    "invalidListing", "selectedNoLongerMatches", "noMatches", "noLocalListings", "viewDetails",
    "closeDetails", "suppliedContact", "contactUnavailable", "notClassified", "noSourceTerms",
    "sourceRemark", "coverage", "suppliedAddress", "unconfirmedStatus", "reportUnavailable",
    "copyLink", "emptyExport", "exportSuccess", "exportFailure", "sourceTerms", "allSourceTerms",
    "sourceRecordRole", "allSourceRecordRoles", "allPunjabDistricts", "mapNotice", "printContext",
    "coverageScopes",
}

REQUIRED_ENGLISH_MESSAGE_KEYS = frozenset(SHELL_MESSAGE_TOKENS.values()) | RUNTIME_MESSAGE_KEYS


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
    display_scope = SCOPE_LABELS[scope] if not area else (
        f"Reported district: {area}" if scope == "not_stated_or_single_site" else f"Reported district: {area} (multiple sites noted)"
    )
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


def assert_runtime(records: list[dict[str, Any]], aliases: dict[str, Any]) -> None:
    if len(records) != 112:
        raise ValueError(f"expected 112 runtime records, found {len(records)}")
    ids = [record["id"] for record in records]
    if len(set(ids)) != len(ids):
        raise ValueError("runtime record IDs are not unique")
    if any("lat" in record or "lon" in record or "latitude" in record or "longitude" in record for record in records):
        raise ValueError("runtime records must not contain coordinates")
    district_records = [record for record in records if record["mapRepresentation"] == "district_group_summary"]
    coverage_records = [record for record in records if record["mapRepresentation"] == "coverage_scope_control"]
    if len(district_records) != 108 or len(coverage_records) != 4:
        raise ValueError(f"expected 108 district-group and 4 coverage records, got {len(district_records)} and {len(coverage_records)}")
    if len({record["mapDistrict"] for record in district_records}) != 22:
        raise ValueError("expected 22 mapped district groups")
    if set(record["coverageScope"] for record in coverage_records) != {"multi_district", "statewide"}:
        raise ValueError("coverage controls must include multi-district and statewide records")
    alias_names = [item["name"] for item in aliases.get("districts", [])]
    if len(alias_names) != 23 or len(set(alias_names)) != 23:
        raise ValueError("district alias configuration must contain 23 unique Punjab districts")
    if not {record["mapDistrict"] for record in district_records}.issubset(alias_names):
        raise ValueError("runtime district groups must be represented in the explicit alias configuration")


def script_json(value: Any) -> str:
    """Safely serialize data for a same-origin JavaScript file, not an HTML script body."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def replace_once(text: str, token: str, value: str, source_name: str) -> str:
    count = text.count(token)
    if count != 1:
        raise ValueError(f"{source_name} expected one {token}, found {count}")
    return text.replace(token, value)


def render_message(value: str, context: dict[str, str]) -> str:
    for key, replacement in context.items():
        value = value.replace("{" + key + "}", replacement)
    return value


def render_shell(template: str, messages: dict[str, Any], context: dict[str, str]) -> str:
    for token, key in SHELL_MESSAGE_TOKENS.items():
        if token not in template:
            raise ValueError(f"template expected locale token {token}")
        value = messages[key]
        template = template.replace(token, html.escape(render_message(value, context), quote=True))
    for token, value in {"__RUNTIME_RECORD_COUNT__": context["recordCount"]}.items():
        if token not in template:
            raise ValueError(f"template expected runtime token {token}")
        template = template.replace(token, value)
    if "__MSG_" in template or "__RUNTIME_" in template:
        raise ValueError("unreplaced locale or runtime token remains in template")
    return template


def validate_public_content(public_config: dict[str, Any], english: dict[str, Any], overlays: dict[str, Any], evidence: dict[str, Any]) -> None:
    if public_config.get("schemaVersion") != "pca-public-site-config/v1":
        raise ValueError("unexpected public site configuration schema")
    if public_config.get("publishedLocales") != ["en"]:
        raise ValueError("only the reviewed English locale may be published until a complete reviewed locale is implemented")
    if public_config.get("canonicalPublicUrl") is not None or public_config.get("correctionRoute") is not None:
        raise ValueError("canonical URL and correction route require a dedicated reviewed implementation before publication")
    if english.get("schemaVersion") != "pca-locale/v1" or english.get("locale") != "en" or english.get("status") != "approved_source_interface":
        raise ValueError("approved English locale metadata is required")
    messages = english.get("messages")
    if not isinstance(messages, dict):
        raise ValueError("English locale messages are required")
    missing = REQUIRED_ENGLISH_MESSAGE_KEYS - set(messages)
    invalid = [key for key in REQUIRED_ENGLISH_MESSAGE_KEYS if not isinstance(messages.get(key), str) or not messages[key].strip()]
    if missing or invalid:
        raise ValueError(f"English locale is incomplete: missing={sorted(missing)} invalid={sorted(invalid)}")
    if overlays.get("schemaVersion") != "pca-reviewed-locales/v1" or overlays.get("overlays") != []:
        raise ValueError("non-English overlays cannot be published before the reviewed locale pipeline is approved")
    if evidence.get("schemaVersion") != "pca-access-evidence/v1" or evidence.get("entries") != []:
        raise ValueError("access enrichment cannot be published without field-specific evidence pipeline approval")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", default=DEFAULT_CANONICAL, type=Path)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, type=Path)
    parser.add_argument("--template", default=DEFAULT_TEMPLATE, type=Path)
    parser.add_argument("--base-runtime", default=DEFAULT_BASE_RUNTIME, type=Path)
    parser.add_argument("--p0-helpers", default=DEFAULT_P0_HELPERS, type=Path)
    parser.add_argument("--p1-runtime", default=DEFAULT_P1_RUNTIME, type=Path)
    parser.add_argument("--tokens-style", default=DEFAULT_TOKENS_STYLE, type=Path)
    parser.add_argument("--base-style", default=DEFAULT_BASE_STYLE, type=Path)
    parser.add_argument("--p0-style", default=DEFAULT_P0_STYLE, type=Path)
    parser.add_argument("--p1-style", default=DEFAULT_P1_STYLE, type=Path)
    parser.add_argument("--aliases", default=DEFAULT_ALIASES, type=Path)
    parser.add_argument("--public-config", default=DEFAULT_PUBLIC_CONFIG, type=Path)
    parser.add_argument("--english-locale", default=DEFAULT_EN_LOCALE, type=Path)
    parser.add_argument("--locale-overlays", default=DEFAULT_LOCALE_OVERLAYS, type=Path)
    parser.add_argument("--access-evidence", default=DEFAULT_ACCESS_EVIDENCE, type=Path)
    parser.add_argument("--logo", default=DEFAULT_LOGO, type=Path)
    parser.add_argument("--out-dir", default=DEFAULT_OUTPUT, type=Path)
    args = parser.parse_args()

    canonical = read_json(args.canonical)
    manifest = read_json(args.manifest)
    aliases = read_json(args.aliases)
    public_config = read_json(args.public_config)
    english = read_json(args.english_locale)
    overlays = read_json(args.locale_overlays)
    evidence = read_json(args.access_evidence)
    if canonical["schemaVersion"] != "pca-record/v1":
        raise ValueError("unexpected canonical schema version")
    if canonical["sourceRecordCount"] != len(canonical["records"]):
        raise ValueError("canonical sourceRecordCount does not match records")
    validate_public_content(public_config, english, overlays, evidence)

    dataset_version = canonical["datasetVersion"]
    runtime = [runtime_record(record, dataset_version) for record in canonical["records"]]
    assert_runtime(runtime, aliases)
    runtime_payload = {"schemaVersion": "pca-runtime/v1", "datasetVersion": dataset_version, "records": runtime}
    build_manifest = {
        "schemaVersion": "pca-build-manifest/v2",
        "datasetVersion": dataset_version,
        "sourceArtifactId": canonical["sourceArtifactId"],
        "sourceArtifactSha256": manifest["sourceArtifact"]["sha256"],
        "sourceRecordCount": len(runtime),
        "districtGroupRecordCount": sum(record["mapRepresentation"] == "district_group_summary" for record in runtime),
        "coverageScopeRecordCount": sum(record["mapRepresentation"] == "coverage_scope_control" for record in runtime),
        "runtimeRecordsSha256": sha256_text(json.dumps(runtime_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))),
        "coordinatesPublished": False,
        "publishedLocales": public_config["publishedLocales"],
        "assetModel": "same-origin external static assets; no inline executable script or stylesheet in generated HTML",
        "notice": "Runtime records are source-derived directory records grouped by reported district or coverage scope, not verified facility locations.",
    }
    write_json(ROOT / "data/generated/runtime-records.v1.json", runtime_payload)
    write_json(ROOT / "data/generated/build-manifest.v1.json", build_manifest)

    template = args.template.read_text(encoding="utf-8")
    if "<style" in template or "<script>" in template:
        raise ValueError("public template must not contain inline style or executable script blocks")
    if 'src="runtime-data.js"' not in template or 'src="app.js"' not in template or 'href="app.css"' not in template:
        raise ValueError("public template must reference same-origin app.css, runtime-data.js, and app.js")
    if "Content-Security-Policy" not in template:
        raise ValueError("public template must declare its compatible restrictive CSP")
    template = render_shell(template, english["messages"], {
        "recordCount": str(len(runtime)),
        "districtCount": str(len(aliases.get("districts", []))),
    })

    css = "\n\n".join(path.read_text(encoding="utf-8").strip() for path in (args.tokens_style, args.base_style, args.p0_style, args.p1_style)) + "\n"
    application_runtime = "\n\n".join(path.read_text(encoding="utf-8").strip() for path in (args.p0_helpers, args.p1_runtime)) + "\n"
    app_js = args.base_runtime.read_text(encoding="utf-8")
    app_js = replace_once(app_js, "__P1_RUNTIME_JS__", application_runtime, "base runtime")
    app_js = replace_once(app_js, "__PCA_EXPORT_CSS__", script_json(css), "base runtime")
    if "__P1_" in app_js or "__PCA_" in app_js:
        raise ValueError("unreplaced application JavaScript build token remains")
    runtime_js = "window.PCA_RUNTIME = " + script_json({
        "records": runtime,
        "buildManifest": build_manifest,
        "districtAliases": aliases,
        "publicConfig": public_config,
        "localeMessages": english["messages"],
    }) + ";\n"

    if args.out_dir.exists():
        shutil.rmtree(args.out_dir)
    args.out_dir.mkdir(parents=True)
    (args.out_dir / "index.html").write_text(template, encoding="utf-8")
    (args.out_dir / "app.css").write_text(css, encoding="utf-8")
    (args.out_dir / "app.js").write_text(app_js, encoding="utf-8")
    (args.out_dir / "runtime-data.js").write_text(runtime_js, encoding="utf-8")
    shutil.copyfile(args.logo, args.out_dir / "logo.svg")
    (args.out_dir / "manus-routes.json").write_text(json.dumps({"routes": [{"path": "/", "title": "Punjab Care Access Map"}]}) + "\n", encoding="utf-8")
    print(f"Built {args.out_dir / 'index.html'} with {len(runtime)} coordinate-free runtime records and same-origin static assets")


if __name__ == "__main__":
    main()
