# Punjab Care Access Map — Project Overview

> **Current release:** P0 foundation
> **Dataset version:** `pca-2026-10-27-v1`
> **Product type:** static, source-derived directory and geographic orientation tool
> **Not a verified provider registry, clinical service finder, or facility locator**

## 1. What the project is

Punjab Care Access Map is a responsive single-page map and directory for **112 owner-supplied records** related to treatment, recovery, de-addiction, rehabilitation, OOAT, OST, MMT/methadone, referral, coordination, and information services in Punjab, India. It runs entirely in the browser: no server, database, account system, analytics, payment flow, geocoder, tile service, or private runtime credential is required.

The visual design preserves the supplied white-and-green reference: dark-green masthead, rounded filter/list panels, a responsive sidebar/map composition, and interactive district, cultural-region, and river overlays. P0 deliberately changed the data model and map semantics while retaining that visual language.

The canonical static output is `public/index.html`. `docs/` is a generated GitHub Pages copy of `public/`; it is never a separately edited source of truth.

## 2. P0 geographic safety rule

### Directory records are not facility coordinates

The supplied source does not provide independently verified latitude/longitude values. P0 therefore does **not** publish facility-like coordinates, synthetic anchor coordinates, or sunflower layout offsets for individual source records.

The map instead presents two evidence-aligned representations:

| Representation | Current accounting | Meaning |
| --- | ---: | --- |
| **District-group count symbols** | 108 records across 22 reported district groups | A count bubble means that source records report that district. It does **not** identify a facility, a precise location, a service capacity, or a travel destination. |
| **Coverage-scope controls** | 4 records: 1 Punjab-wide/multi-district and 3 statewide | These are listed through dedicated controls and never placed at an invented map point. |

The map, record detail, legend, ARIA label, CSV, PNG, and PDF all say that the map groups directory records by **reported district or coverage scope—not facility locations**. A source address is shown as supplied text and is labelled as unverified for map purposes.

### Context layers

Punjab district outlines/labels, the Majha/Doaba/Malwa/Puadh wayfinding overlays, and Ravi/Beas/Sutlej/Ghaggar/Kali Bein river traces remain available as orientation layers. The cultural regions are not official administrative boundaries; river traces are schematic orientation lines, not a hydrological survey. None of these layers verifies a source record.

## 3. Supplied source and provenance

### Source contract

The approved source is a CSV-like six-field file with 112 rows and this exact header:

1. `Name`
2. `District`
3. `Address / Location`
4. `Type`
5. `Contact (if available)`
6. `Remarks`

The raw source is intentionally **not committed**. Its origin and integrity are captured by [`data/manifests/source-artifact.v1.json`](data/manifests/source-artifact.v1.json), which contains the artifact ID, original filename, SHA-256 hash, expected header, parser version, record count, and an explicit notice that raw content is not committed.

### Why the importer is controlled

The current source has unquoted commas in names and remarks while its address field is reliably quoted. A generic comma split can shift values between fields. [`scripts/import_legacy_source.py`](scripts/import_legacy_source.py) validates the known contract and fails rather than guessing when it finds an unexpected header, blank row, missing quoted address anchor, malformed address boundary, required blank field, or mismatch against the legacy baseline.

A known malformed leading/trailing quote in a free-text remark is recoverable only with an explicit `parseWarnings` entry. Each imported observation retains:

- Original source row number;
- SHA-256 of the raw source line;
- SHA-256 of the parsed six-field tuple;
- Parser version (`pca-legacy-import/v2`);
- Extracted `[reference:…]` source tokens;
- Any controlled parse warning.

This preserves auditable source lineage without committing the raw upload.

## 4. Canonical record model and IDs

[`data/canonical/punjab-care-records.v1.json`](data/canonical/punjab-care-records.v1.json) contains 112 `pca-record/v1` **source-derived directory records**, not confirmed facilities. Its public schema is [`data/schemas/pca-record-v1.schema.json`](data/schemas/pca-record-v1.schema.json).

Each record stores:

```json
{
  "recordId": "pca:record:<UUID>",
  "legacyIds": ["F001"],
  "recordStatus": "unreviewed_source_record",
  "sourceObservations": [{
    "sourceArtifactId": "source:deepseek_csv_20261027_e08391",
    "sourceRowNumber": 2,
    "sourceLineSha256": "…",
    "parsedTupleSha256": "…",
    "parserVersion": "pca-legacy-import/v2",
    "parsedFields": {"name":"…","district":"…","address":"…","type":"…","contact":"…","remarks":"…"}
  }],
  "recordKind": {"value":"…","derivation":"source_text_rule","ruleId":"…","evidence":[]},
  "ownershipClaim": {"value":"…","derivation":"source_text_rule","ruleId":"…","evidence":[]},
  "serviceMentions": [],
  "coverage": {"scope":"…"},
  "location": {"verifiedCoordinates": null},
  "mapPresentation": {"representation":"district_group_summary","isVerifiedGeocode":false},
  "review": {"duplicateReviewStatus":"not_reviewed","classificationReviewStatus":"not_reviewed"}
}
```

### Durable IDs and legacy aliases

The former `F001`–`F112` identifiers remain as `legacyIds`; they are aliases, not canonical identity. [`data/migrations/legacy-id-crosswalk.v1.json`](data/migrations/legacy-id-crosswalk.v1.json) maps the legacy alias and parsed-tuple hash to a durable canonical `recordId`.

When a future approved source is imported with `--crosswalk`, any unchanged parsed observation reuses its existing canonical record ID even if rows are reordered. A changed/new tuple fails safe pending a reviewed migration; it is never silently treated as the old record, silently assigned to a legacy alias, or silently substituted into the P0 baseline. The importer regression suite contains a row-reorder test proving durable reuse.

## 5. Derived fields: source text only

P0 keeps concepts separate and labels them as rules derived from supplied text. None is a verification claim.

| Field | Values / basis | It does **not** establish |
| --- | --- | --- |
| `recordKind` | Source site/provider, administrative/coordination, helpline/information, multi-site/coverage; derived from name/type/district/address text | A confirmed facility, operation, programme, or contact route |
| `ownershipClaim` | Government, NGO/trust, private, mixed/ambiguous, or not stated; derived from source `Type` | Legal ownership, funding, accreditation, endorsement, or service provision |
| `serviceMentions` | OOAT, MMT/methadone, DDTC, OST, model centre, rehabilitation, helpline terms found in supplied text | Current availability, clinical suitability, staff, capacity, or eligibility |
| `coverage.scope` | Reported district/single-site, multiple-within-district, multi-district, statewide | Actual catchment, eligibility, distance, or service availability |
| `location.sourceAddressGranularity` | Coverage-only, multiple-sites, district/city, named institution, detailed address, locality | A validated address or verified coordinate |
| `mapPresentation` | District summary or coverage-scope control | A facility point, exact route, nearest-service result, or care-access measure |

The user interface accordingly uses **Source ownership claim**, **Source record role**, and **Coverage scopes** labels. Source terms are shown as source terms, not verified offerings.

## 6. Duplicate-review workflow

[`data/reviews/duplicate-candidates.v1.json`](data/reviews/duplicate-candidates.v1.json) is review material, never an automatic deduplication action. The current report contains:

- **3 duplicate-review candidates:** one high-confidence and two medium-confidence prompts;
- **27 same-location/different-source-label cases:** recorded separately because a shared source address/display area does not prove two labels represent the same programme.

Candidate entries preserve both record IDs, legacy aliases, source observations/rows, normalized comparisons, reason, confidence, and blank reviewer/date/rationale fields. P0 never merges, deletes, hides, or resolves a candidate automatically.

## 7. Browser experience

The browser-safe derived view is [`data/generated/runtime-records.v1.json`](data/generated/runtime-records.v1.json). It contains display fields needed by the page and contains **no `lat` or `lon` fields**.

The generated static page offers:

- Full-text search across source/derived display fields;
- Source-ownership claim filter buttons with current counts;
- Source-record-role selector;
- Punjab-wide/multi-district and statewide coverage-scope controls;
- Clickable district count symbols that filter the directory, not facility points;
- A listing-first route to every record;
- Detail cards with supplied address/contact text, source role, coverage, source terms, location-precision statement, and current-status caveat;
- District boundary/label, cultural-region, regional-label, river, and river-label toggles;
- Map pan, zoom, and reset;
- Filtered CSV export and PNG/PDF map exports.

The empty result message is intentionally non-inferential: no matching directory rows do not establish that services are unavailable.

## 8. Exports

### CSV

The filtered CSV includes durable and legacy IDs, name, record kind, source ownership claim, source terms, coverage, reported district/scope, source district/address, location precision, map representation, source type, contact display, source remarks, source row, and dataset version. Formula-like prefixes (`=`, `+`, `-`, `@`) are neutralized before download.

### PNG and PDF

PNG and one-page PDF exports are generated in browser JavaScript from the current SVG state. They include an interpretation key, the dataset version, and a caveat that the map groups records by reported district/coverage scope rather than facility location. No export generates or embeds new coordinates.

Manual P0 validation exercised a filtered coverage-scope export: the CSV contained one `coverage_scope_control` record with no map point; PNG had a valid PNG signature; PDF had a valid `%PDF-1.4` header and one page.

## 9. Source tree and generated artifacts

```text
README.md                         # quick start and non-claims
DEVELOPER_HANDOFF.md              # owner-supplied P0–P2 specification
PROJECT_OVERVIEW.md               # this document
plan.md                           # approved P0 plan
TODO.md                           # delivery status
Makefile                          # normal workflow

data/
  canonical/punjab-care-records.v1.json
  generated/runtime-records.v1.json
  generated/build-manifest.v1.json
  manifests/source-artifact.v1.json
  migrations/legacy-id-crosswalk.v1.json
  reviews/duplicate-candidates.v1.json
  schemas/pca-record-v1.schema.json
  facilities.updated.json         # historical importer reconciliation baseline

src/
  template.html                   # committed static template with placeholders
  p0-runtime.js                   # district-summary renderer, filters, exports
  p0-style.css                    # P0 notice, controls, summary marker styles
  logo.svg

scripts/
  import_legacy_source.py         # controlled provenance-safe importer
  build_p0.py                     # canonical -> runtime/public build
  sync_github_pages.py            # public -> docs full sync
  validate_p0.py                  # deterministic build/data checks
  create_p0_template.py           # retained one-time template migration utility
  prepare_updated_facilities.R    # retired historical intermediate generator
  restore_reference_design.py     # retired historical design helper

tests/test_import_legacy_source.py # import and durable-ID regression tests
public/                            # generated static deployment output
docs/                              # generated GitHub Pages output
```

`public/` and `docs/` are generated. Do not edit them directly or independently.

## 10. Reproducible workflow

A normal checkout build does not need `/home/ubuntu/upload` or another raw source file:

```bash
make build       # canonical data -> public/ -> docs/
make test        # importer contract and durable-ID regression tests
make validate    # canonical/runtime/Pages/static-JS checks
make check       # build + test + validate
make serve       # serves public/ on port 3000
```

To import an approved replacement source that is available outside the repository:

```bash
make refresh-data \
  SOURCE=/absolute/path/to/approved-source.txt \
  ARTIFACT_ID=source:approved-artifact \
  DATASET_VERSION=pca-YYYY-MM-vN
```

The refresh path validates the six-field contract, uses the committed legacy reconciliation baseline and ID crosswalk, regenerates output, and runs the complete checks. A new or changed source observation fails safe rather than being silently assigned to a legacy record or silently replacing one; complete a reviewed migration before introducing it into the P0 baseline.

## 11. Deterministic validation

`make check` verifies:

1. Missing quoted-address anchors are rejected;
2. Durable IDs survive a source-row reorder when the crosswalk is supplied;
3. Script/test Python syntax;
4. 112 canonical records with unique record IDs, legacy aliases, and source rows;
5. Manifest/canonical agreement, lineage fields, explicit null coordinates, and source-text derivations;
6. Complete crosswalk and review-report shape;
7. No coordinate-bearing runtime record; 108 district-summary records, four coverage controls, 22 district groups, and two coverage scopes;
8. Equality between generated runtime JSON and records embedded in `public/index.html`;
9. Absence of the legacy coordinate renderer and facility-marker wording;
10. `public/`/`docs/` parity except for the intentional GitHub Pages-relative favicon path;
11. `.nojekyll`, logo parity, route manifest, and inline JavaScript syntax.

## 12. Hosting

`public/` is the Manus static build output. `docs/` is synchronized from it for GitHub Pages, with a relative favicon path and `.nojekyll` for project-subpath compatibility. A repository URL is not itself a public map URL; before sharing a live link, configure/verify the GitHub Pages environment and visit the deployed site.

## 13. Explicit limitations and decisions still required

P0 does **not** verify or claim current operation, ownership, licence/accreditation, capacity, fees, hours, eligibility, language, accessibility, clinical suitability, confidentiality, address accuracy, contact accuracy, travel time, nearest service, or quality. It does not establish a census of services or a district-level access gap.

Owner/editorial work still needed includes:

- Resolve duplicate-review candidates with reviewer, date, decision, and rationale;
- Review same-location/different-source-label cases;
- Establish an approved verification, correction, archival, privacy, and public-display policy;
- Complete P1 accessibility, contact-action, CI/CD, deployment monitoring, and usability work from the developer handoff;
- Complete P2 reviewed localization, richer source-backed taxonomy, and any future verified-geocode governance.

Until those decisions are complete, describe the map as a **source-derived directory and geographic orientation aid**, not as a verified care-access system.
