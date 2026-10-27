#!/usr/bin/env python3
"""Import the legacy Punjab Care Access source into the P0 record-and-observation model.

The source is CSV-like: names and remarks can contain unquoted commas while the current
source quotes its address field. This importer validates that known contract and fails
rather than silently moving values between columns.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "pca-record/v1"
PARSER_VERSION = "pca-legacy-import/v2"
EXPECTED_HEADER = ["Name", "District", "Address / Location", "Type", "Contact (if available)", "Remarks"]
CURRENT_ARTIFACT_ID = "source:deepseek_csv_20261027_e08391"
CURRENT_DATASET_VERSION = "pca-2026-10-27-v1"

DISTRICT_NORMALIZATION = {
    "Ropar": "Rupnagar",
    "Shaheed Bhagat Singh Nagar (Nawanshahr)": "Shaheed Bhagat Singh Nagar",
    "Nawanshahr": "Shaheed Bhagat Singh Nagar",
    "Mohali": "Sahibzada Ajit Singh Nagar",
    "Derabassi (Mohali)": "Sahibzada Ajit Singh Nagar",
    "Khanpur (Patiala)": "Patiala",
    "Ropar/Ludhiana": "Ludhiana",
    "Punjab (multiple)": "Punjab-wide",
    "Statewide": "Statewide",
}

REGION_MAP = {
    "Pathankot": "Majha", "Gurdaspur": "Majha", "Amritsar": "Majha", "Tarn Taran": "Majha",
    "Hoshiarpur": "Doaba", "Jalandhar": "Doaba", "Kapurthala": "Doaba", "Shaheed Bhagat Singh Nagar": "Doaba",
    "Ferozepur": "Malwa", "Fazilka": "Malwa", "Sri Muktsar Sahib": "Malwa", "Faridkot": "Malwa",
    "Moga": "Malwa", "Ludhiana": "Malwa", "Malerkotla": "Malwa", "Barnala": "Malwa",
    "Sangrur": "Malwa", "Bathinda": "Malwa", "Mansa": "Malwa",
    "Patiala": "Puadh", "Fatehgarh Sahib": "Puadh", "Sahibzada Ajit Singh Nagar": "Puadh", "Rupnagar": "Puadh",
}


@dataclass(frozen=True)
class ParsedRow:
    row_number: int
    raw_line: str
    name: str
    district: str
    address: str
    record_type: str
    contact: str
    remarks: str
    parse_warnings: tuple[str, ...] = ()

    def as_source_fields(self) -> dict[str, str]:
        return {
            "name": self.name,
            "district": self.district,
            "address": self.address,
            "type": self.record_type,
            "contact": self.contact,
            "remarks": self.remarks,
        }


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def legacy_reconciliation_value(value: str) -> str:
    """Normalize only serializer-introduced whitespace around commas for baseline matching."""
    return re.sub(r"\s*,\s*", ",", value.strip())


def legacy_reconciliation_hash(fields: dict[str, str]) -> str:
    return sha256_text(canonical_json({key: legacy_reconciliation_value(value) for key, value in fields.items()}))


def parse_csv_like_line(line: str, row_number: int) -> list[tuple[str, bool]]:
    """Return values plus whether each token was quoted; reject malformed quoting."""
    fields: list[tuple[str, bool]] = []
    buffer: list[str] = []
    quoted = False
    token_quoted = False
    at_start = True
    index = 0
    while index < len(line):
        char = line[index]
        if char == '"':
            if quoted and index + 1 < len(line) and line[index + 1] == '"':
                buffer.append('"')
                index += 2
                at_start = False
                continue
            if not quoted and not at_start:
                raise ValueError(f"row {row_number}: quote begins inside an unquoted token")
            quoted = not quoted
            token_quoted = True
            index += 1
            continue
        if char == "," and not quoted:
            fields.append(("".join(buffer).strip(), token_quoted))
            buffer = []
            token_quoted = False
            at_start = True
            index += 1
            continue
        buffer.append(char)
        if not char.isspace() or buffer:
            at_start = False
        index += 1
    if quoted:
        raise ValueError(f"row {row_number}: unbalanced quote")
    fields.append(("".join(buffer).strip(), token_quoted))
    return fields


def parse_source(source_path: Path) -> tuple[str, list[ParsedRow]]:
    raw_bytes = source_path.read_bytes()
    text = raw_bytes.decode("utf-8-sig")
    lines = text.splitlines()
    if not lines:
        raise ValueError("source is empty")
    header = [part.strip() for part in lines[0].split(",")]
    if header != EXPECTED_HEADER:
        raise ValueError(f"unexpected source header {header!r}; expected {EXPECTED_HEADER!r}")

    rows: list[ParsedRow] = []
    for row_number, line in enumerate(lines[1:], start=2):
        if not line.strip():
            raise ValueError(f"row {row_number}: blank rows are not accepted")

        # The approved legacy source has unquoted commas in names/remarks but starts its
        # address field with the first quote. Split the two stable fields after that address,
        # and preserve the remaining text as remarks. This avoids treating an unmatched quote
        # in a free-text remark as a field shift.
        quote_start = line.find('"')
        if quote_start < 0:
            raise ValueError(f"row {row_number}: expected quoted address anchor")
        quote_end = quote_start + 1
        while quote_end < len(line):
            if line[quote_end] == '"':
                if quote_end + 1 < len(line) and line[quote_end + 1] == '"':
                    quote_end += 2
                    continue
                break
            quote_end += 1
        if quote_end >= len(line):
            raise ValueError(f"row {row_number}: address quote does not close")
        prefix = line[:quote_start]
        if not prefix.endswith(','):
            raise ValueError(f"row {row_number}: quoted address does not follow a district delimiter")
        try:
            name, district = prefix[:-1].rsplit(',', 1)
        except ValueError as error:
            raise ValueError(f"row {row_number}: cannot split name from district before address") from error
        address = line[quote_start + 1 : quote_end].replace('""', '"').strip()
        suffix = line[quote_end + 1 :]
        if not suffix.startswith(','):
            raise ValueError(f"row {row_number}: address is not followed by type/contact fields")
        trailing = suffix[1:].split(',', 2)
        if len(trailing) != 3:
            raise ValueError(f"row {row_number}: expected type, contact, and remarks after address")
        record_type, contact, remarks = (value.strip() for value in trailing)
        warnings: list[str] = []
        if remarks.startswith('"') and remarks.endswith('"') and len(remarks) >= 2:
            remarks = remarks[1:-1].replace('""', '"')
        elif remarks.startswith('"'):
            remarks = remarks[1:]
            warnings.append("recovered_unbalanced_leading_quote_in_remarks")
        elif remarks.endswith('"'):
            remarks = remarks[:-1]
            warnings.append("recovered_unbalanced_trailing_quote_in_remarks")
        name, district = name.strip(), district.strip()
        if not all([name, district, address, record_type]):
            raise ValueError(f"row {row_number}: required logical field is blank")
        rows.append(ParsedRow(row_number, line, name, district, address, record_type, contact, remarks, tuple(warnings)))
    return hashlib.sha256(raw_bytes).hexdigest(), rows


def normalize_district(value: str) -> str:
    return DISTRICT_NORMALIZATION.get(value, value)


def source_tokens(row: ParsedRow) -> list[str]:
    return sorted(set(re.findall(r"\[reference:([^\]]+)\]", row.remarks, flags=re.I)))


def derive_record_kind(row: ParsedRow) -> dict[str, Any]:
    haystack = f"{row.name} {row.record_type}".lower()
    if "helpline" in haystack or "district office" in haystack:
        value = "helpline_or_information_record"
    elif row.record_type.strip().lower() == "government society":
        value = "administrative_or_coordination_record"
    elif row.district in {"Statewide", "Punjab (multiple)"} or "various blocks" in row.address.lower():
        value = "coverage_or_multi_site_record"
    else:
        value = "site_or_provider_record"
    return {"value": value, "derivation": "source_text_rule", "ruleId": "record-kind/v1", "evidence": [{"field": "type_or_name", "text": f"{row.record_type} | {row.name}"}]}


def derive_ownership(row: ParsedRow) -> dict[str, Any]:
    source_type = row.record_type.strip()
    lower = source_type.lower()
    if lower.startswith("government"):
        value = "government_claim"
    elif "ngo" in lower and "private" in lower:
        value = "mixed_or_ambiguous_claim"
    elif lower.startswith("private"):
        value = "private_claim"
    elif lower.startswith("ngo"):
        value = "ngo_or_trust_claim"
    else:
        value = "not_stated"
    return {"value": value, "derivation": "source_text_rule", "ruleId": "ownership-claim/v1", "evidence": [{"field": "type", "text": source_type}]}


def derive_service_mentions(row: ParsedRow) -> list[dict[str, str]]:
    rules = [
        ("ooat_mentioned", r"\bOOAT\b"),
        ("mmt_or_methadone_mentioned", r"\bMMT\b|methadone"),
        ("ddtc_mentioned", r"\bDDTC\b"),
        ("ost_mentioned", r"\bOST\b"),
        ("model_centre_mentioned", r"\bmodel\b"),
        ("rehabilitation_mentioned", r"rehabilitation"),
        ("helpline_mentioned", r"helpline"),
    ]
    values: list[dict[str, str]] = []
    for code, pattern in rules:
        for field, text in (("type", row.record_type), ("name", row.name), ("remarks", row.remarks)):
            if re.search(pattern, text, flags=re.I):
                values.append({"code": code, "sourceField": field, "sourceText": text, "verificationStatus": "source_mentioned_not_independently_verified"})
                break
    return values


def derive_coverage(row: ParsedRow) -> dict[str, Any]:
    if row.district == "Statewide":
        scope = "statewide"
    elif row.district == "Punjab (multiple)":
        scope = "multi_district"
    elif "various blocks" in row.address.lower():
        scope = "multiple_sites_within_district"
    else:
        scope = "not_stated_or_single_site"
    return {"scope": scope, "sourceAreaText": [row.district], "derivation": "source_text_rule", "ruleId": "coverage/v1"}


def derive_granularity(row: ParsedRow, coverage_scope: str) -> str:
    address = row.address.strip().lower()
    if coverage_scope in {"statewide", "multi_district"}:
        return "coverage_scope_no_single_place"
    if "various blocks" in address:
        return "multiple_sites_no_single_place"
    if address == row.district.strip().lower():
        return "district_or_city_text"
    if any(term in address for term in ["civil hospital", "medical college", "community health centre", "chc", "sdh", "hospital"]):
        return "named_institution_text_unverified"
    if re.search(r"\d|road|street|sector|village|near|ward|post", address):
        return "detailed_address_text_unverified"
    return "locality_text_unverified"


def legacy_category(legacy: dict[str, Any] | None) -> str | None:
    return legacy.get("category") if legacy else None


def make_record(row: ParsedRow, legacy: dict[str, Any] | None, source_sha: str, artifact_id: str, record_id: str) -> dict[str, Any]:
    fields = row.as_source_fields()
    tuple_hash = sha256_text(canonical_json(fields))
    map_area = normalize_district(row.district)
    coverage = derive_coverage(row)
    representation = "coverage_scope_control" if coverage["scope"] in {"statewide", "multi_district"} else "district_group_summary"
    source_observation = {
        "observationId": f"pca:observation:{artifact_id}:r{row.row_number:06d}",
        "sourceArtifactId": artifact_id,
        "sourceArtifactSha256": source_sha,
        "sourceRowNumber": row.row_number,
        "sourceLineSha256": sha256_text(row.raw_line),
        "parsedTupleSha256": tuple_hash,
        "parserVersion": PARSER_VERSION,
        "parsedFields": fields,
        "sourceReferenceTokens": source_tokens(row),
        "parseWarnings": list(row.parse_warnings),
    }
    return {
        "recordId": record_id,
        "legacyIds": [legacy["id"]] if legacy else [],
        "recordStatus": "unreviewed_source_record",
        "sourceObservations": [source_observation],
        "recordKind": derive_record_kind(row),
        "ownershipClaim": derive_ownership(row),
        "serviceMentions": derive_service_mentions(row),
        "coverage": coverage,
        "location": {
            "sourceAddress": row.address,
            "sourceDistrict": row.district,
            "sourceAddressGranularity": derive_granularity(row, coverage["scope"]),
            "verifiedCoordinates": None,
        },
        "mapPresentation": {
            "displayAnchorArea": map_area if representation == "district_group_summary" else None,
            "editorialRegion": REGION_MAP.get(map_area, "Punjab-wide"),
            "representation": representation,
            "isVerifiedGeocode": False,
            "coordinatePrecision": "not_geocoded",
        },
        "legacyClassification": {
            "category": legacy_category(legacy),
            "serviceGroup": legacy.get("serviceGroup") if legacy else None,
        },
        "review": {"duplicateReviewStatus": "not_reviewed", "classificationReviewStatus": "not_reviewed"},
    }


def normalise_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def token_overlap(a: str, b: str) -> float:
    left, right = set(normalise_text(a).split()), set(normalise_text(b).split())
    if not left or not right:
        return 0.0
    return len(left & right) / min(len(left), len(right))


def duplicate_candidates(records: list[dict[str, Any]], source_sha: str, artifact_id: str) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    same_location_different_labels: list[dict[str, Any]] = []
    for left, right in itertools.combinations(records, 2):
        a, b = left["sourceObservations"][0], right["sourceObservations"][0]
        af, bf = a["parsedFields"], b["parsedFields"]
        same_name = normalise_text(af["name"]) == normalise_text(bf["name"])
        same_type = normalise_text(af["type"]) == normalise_text(bf["type"])
        same_district = normalise_text(af["district"]) == normalise_text(bf["district"])
        same_address = normalise_text(af["address"]) == normalise_text(bf["address"])
        overlap = token_overlap(af["address"], bf["address"])
        same_display_area = left["mapPresentation"]["displayAnchorArea"] == right["mapPresentation"]["displayAnchorArea"]
        if same_name and same_type and same_district and same_address:
            candidate_type, confidence, reason = "possible_duplicate", "high", "same normalized name, district, address, and type"
        elif same_name and same_type and same_display_area and overlap >= 0.8:
            candidate_type, confidence, reason = "needs_manual_review", "medium", "same normalized name and type with overlapping address/locality text"
        elif same_display_area and same_address and not same_type:
            same_location_different_labels.append({
                "left": {"recordId": left["recordId"], "legacyIds": left["legacyIds"], "sourceRowNumber": a["sourceRowNumber"], "name": af["name"], "type": af["type"]},
                "right": {"recordId": right["recordId"], "legacyIds": right["legacyIds"], "sourceRowNumber": b["sourceRowNumber"], "name": bf["name"], "type": bf["type"]},
                "displayAnchorArea": left["mapPresentation"]["displayAnchorArea"],
                "sourceAddress": af["address"],
                "notice": "Shared source address or display area does not establish a duplicate; source labels differ.",
            })
            continue
        else:
            continue
        candidate_id = sha256_text("|".join(sorted([left["recordId"], right["recordId"]])))[:16]
        candidates.append({
            "candidateId": f"pca:duplicate:{candidate_id}",
            "candidateType": candidate_type,
            "confidenceBand": confidence,
            "reason": reason,
            "left": {"recordId": left["recordId"], "legacyIds": left["legacyIds"], "observationId": a["observationId"], "sourceRowNumber": a["sourceRowNumber"]},
            "right": {"recordId": right["recordId"], "legacyIds": right["legacyIds"], "observationId": b["observationId"], "sourceRowNumber": b["sourceRowNumber"]},
            "comparison": {
                "name": {"left": af["name"], "right": bf["name"], "sameNormalized": same_name},
                "district": {"left": af["district"], "right": bf["district"], "sameNormalized": same_district},
                "address": {"left": af["address"], "right": bf["address"], "sameNormalized": same_address, "tokenOverlap": round(overlap, 3)},
                "type": {"left": af["type"], "right": bf["type"], "sameNormalized": same_type},
            },
            "review": {"status": "unreviewed", "reviewer": None, "reviewDate": None, "rationale": None},
        })
    candidates.sort(key=lambda x: ({"high": 0, "medium": 1, "low": 2}[x["confidenceBand"]], x["candidateId"]))
    return {
        "reportVersion": "duplicate-candidates/v1",
        "sourceArtifactId": artifact_id,
        "sourceArtifactSha256": source_sha,
        "normalizationRuleVersion": "duplicate-normalization/v1",
        "candidates": candidates,
        "sameLocationDifferentSourceLabels": same_location_different_labels,
        "notice": "Candidates are review prompts only. No source observations were merged, deleted, or hidden.",
    }


def load_legacy(path: Path) -> dict[str, list[dict[str, Any]]]:
    values = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, list[dict[str, Any]]] = {}
    for value in values:
        source_fields = {
            "name": value["Name"], "district": value["District"], "address": value["Address"],
            "type": value["Type"], "contact": value["Contact"], "remarks": value["Remarks"],
        }
        result.setdefault(legacy_reconciliation_hash(source_fields), []).append(value)
    return result


def load_crosswalk(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    mappings = payload.get("mappings", [])
    registry: dict[str, str] = {}
    for mapping in mappings:
        fingerprint, record_id = mapping["parsedTupleSha256"], mapping["recordId"]
        if fingerprint in registry and registry[fingerprint] != record_id:
            raise ValueError(f"crosswalk contains conflicting IDs for source fingerprint {fingerprint}")
        registry[fingerprint] = record_id
    return registry


def compare_legacy(row: ParsedRow, legacy: dict[str, Any]) -> None:
    expected = {"Name": row.name, "District": row.district, "Address": row.address, "Type": row.record_type, "Contact": row.contact, "Remarks": row.remarks}
    differing = [key for key, value in expected.items() if legacy_reconciliation_value(legacy.get(key, "")) != legacy_reconciliation_value(value)]
    if differing:
        raise ValueError(f"row {row.row_number}: legacy generated data differs in {', '.join(differing)}")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="approved source CSV-like file")
    parser.add_argument("--legacy", required=True, type=Path, help="current legacy generated JSON used only to preserve F IDs and editorial map groups")
    parser.add_argument("--crosswalk", type=Path, help="optional prior legacy-ID crosswalk; unchanged parsed records reuse its immutable record IDs")
    parser.add_argument("--artifact-id", default=CURRENT_ARTIFACT_ID, help="controlled source-artifact identity; set a new value for a new source artifact")
    parser.add_argument("--dataset-version", default=CURRENT_DATASET_VERSION, help="controlled output dataset version; set a new value for a new source artifact")
    parser.add_argument("--data-root", default=Path("data"), type=Path, help="repository data root")
    args = parser.parse_args()

    source_sha, rows = parse_source(args.input)
    legacy_by_tuple = load_legacy(args.legacy)
    prior_ids = load_crosswalk(args.crosswalk)
    records = []
    for row in rows:
        tuple_hash = legacy_reconciliation_hash(row.as_source_fields())
        legacy_matches = legacy_by_tuple.get(tuple_hash, [])
        if not legacy_matches:
            raise ValueError(f"row {row.row_number}: no matching legacy observation for parsed source content")
        legacy = legacy_matches.pop(0)
        compare_legacy(row, legacy)
        parsed_tuple_hash = sha256_text(canonical_json(row.as_source_fields()))
        record_id = prior_ids.get(parsed_tuple_hash, f"pca:record:{uuid.uuid5(uuid.NAMESPACE_URL, f'{args.artifact_id}:{parsed_tuple_hash}')}")
        records.append(make_record(row, legacy, source_sha, args.artifact_id, record_id))
    unmatched = [legacy for matches in legacy_by_tuple.values() for legacy in matches]
    if unmatched:
        raise ValueError(f"{len(unmatched)} legacy records did not reconcile to parsed source content")
    if len({record["recordId"] for record in records}) != len(records):
        raise ValueError("generated record IDs are not unique")

    root = args.data_root
    manifest = {
        "schemaVersion": "pca-source-artifact/v1",
        "datasetVersion": args.dataset_version,
        "sourceArtifact": {
            "sourceArtifactId": args.artifact_id,
            "fileName": args.input.name,
            "sha256": source_sha,
            "expectedHeader": EXPECTED_HEADER,
            "parserVersion": PARSER_VERSION,
            "sourceRecordCount": len(records),
            "rawContentCommitted": False,
            "notice": "The controlled raw upload is intentionally not committed. This manifest retains hash-based provenance for the approved import.",
        },
    }
    canonical = {
        "schemaVersion": SCHEMA_VERSION,
        "datasetVersion": args.dataset_version,
        "sourceArtifactId": args.artifact_id,
        "sourceRecordCount": len(records),
        "records": records,
    }
    crosswalk = {
        "schemaVersion": "pca-legacy-id-crosswalk/v1",
        "datasetVersion": args.dataset_version,
        "notice": "Legacy F identifiers remain aliases only. They are not canonical durable identifiers.",
        "mappings": [
            {
                "legacyId": record["legacyIds"][0],
                "recordId": record["recordId"],
                "sourceRowNumber": record["sourceObservations"][0]["sourceRowNumber"],
                "parsedTupleSha256": record["sourceObservations"][0]["parsedTupleSha256"],
            }
            for record in records
        ],
    }
    write_json(root / "manifests/source-artifact.v1.json", manifest)
    write_json(root / "canonical/punjab-care-records.v1.json", canonical)
    write_json(root / "migrations/legacy-id-crosswalk.v1.json", crosswalk)
    write_json(root / "reviews/duplicate-candidates.v1.json", duplicate_candidates(records, source_sha, args.artifact_id))
    print(f"Imported {len(records)} source observations into canonical P0 data under {root}")


if __name__ == "__main__":
    main()
