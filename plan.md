# P0 Foundation Plan — Punjab Care Access Map

> **Status: delivered and validated on 2026-10-27.** P1/P2 editorial verification, accessibility, privacy, deployment, and governance work remains outside this P0 implementation.

## Purpose

Implement the owner-approved P0 foundation from the Developer Handoff: provenance-safe import, durable identifiers, an explicit source-record model, duplicate-review output, uncertainty-first map representation, and reproducible build validation. This is a corrective data and representation release. It does not verify service operation, ownership, clinical suitability, hours, fees, accessibility, or location coordinates.

## Product and data decisions

The canonical unit will be a **source-derived directory record**, not a confirmed facility. Each public record will retain the six supplied source fields and an observation-level source lineage. Derived fields will clearly distinguish source-text rules from independently verified facts.

The existing `F001`–`F112` identifiers remain supported as `legacyIds`. New immutable `recordId` values will be stored in a committed registry rather than derived from source row order, record name, or district. Each canonical record will retain the original source row, source-artifact identity and hash, parsed-tuple hash, source-line hash, parser version, and source-reference tokens.

Ownership, record role, service terms, coverage, and map representation will be separate fields. The P0 mapper will use only conservative, versioned source-text rules. Ambiguous or mixed ownership remains `mixed_or_ambiguous_claim` or `not_stated`; service labels are recorded as source mentions, not verified offerings.

The existing district-anchor `lat`/`lon` values and sunflower layout offsets will not be published in the canonical or runtime records. The site will show **district-group counts**, not point markers for individual records. Punjab-wide and statewide records will appear in a separately labelled coverage-scope control/list grouping rather than at an invented map location.

## Design approach

The supplied white-and-green reference design remains the visual base: dark-green header, rounded filter/list panels, responsive sidebar/map composition, and provider-category colour use in textual listings. The map will change its unit of representation from facility-like pins to neutral district-count symbols. A prominent, persistent map statement will explain that the geographic overview groups records by reported district/coverage scope and does not show facility locations.

Provider colours will be attached to source-claim filters and list badges rather than individual map dots. The list remains the authoritative route to each individual source record and its supplied address/contact text. The map stays an orientation and district-browsing tool.

## Implementation approach

1. **Preserve the supplied feedback as project documentation.** Add the developer handoff to the repository and keep its P0/P1/P2 status language intact.
2. **Create a canonical data layer.** Build a v1 canonical dataset, source-artifact manifest, durable-ID registry/crosswalk, and duplicate-candidate report from the current 112-record baseline. Preserve each source record exactly as an observation; do not merge or delete candidates automatically.
3. **Replace the legacy importer.** Add a parameterized, quote-aware Python import path that validates the expected six logical fields, captures hashes and source rows before grouping, and writes standard JSON. Retain the existing R script as legacy/historical compatibility instead of using it for the P0 build.
4. **Create a committed template and build entry point.** Move the approved runtime source into `src/template.html` with explicit data placeholders. Add a Python build script that produces `public/index.html`, `public/manus-routes.json`, and the generated browser dataset from canonical data. The normal build must work from a clean checkout without `/home/ubuntu/upload/...` dependencies.
5. **Implement uncertainty-first map rendering.** Override the current per-record SVG marker renderer with district summary symbols. Keep list selection, district filtering, regions, rivers, zoom/pan, CSV export, and PNG/PDF map exports. Add a separate coverage-scope control for statewide/Punjab-wide records.
6. **Make exports and copy honest.** CSV will contain source fields plus unambiguous display/coverage fields and escape spreadsheet-formula prefixes. PNG/PDF exports will include an in-map uncertainty statement, a district-group key, dataset version, and core caveats. User-facing copy will distinguish supplied address from map representation.
7. **Add deterministic validation.** Validate schema/lineage/ID uniqueness, import behavior, duplicate report shape, no coordinate-bearing runtime records, public/docs data coherence, static JavaScript syntax, Pages subpath behavior, and P0 map-accounting totals.
8. **Regenerate static artifacts and documentation.** Regenerate `public/` and `docs/`, update the overview and handoff status, and preserve current historical scripts as retired intermediate generators.

## Project structure after P0

```text
DEVELOPER_HANDOFF.md             # owner-supplied specification
PROJECT_OVERVIEW.md              # current architecture, data, and limitations
plan.md                          # this P0 plan
data/
  canonical/punjab-care-records.v1.json
  manifests/source-artifact.v1.json
  migrations/legacy-id-crosswalk.v1.json
  reviews/duplicate-candidates.v1.json
  generated/runtime-records.v1.json
  schemas/pca-record-v1.schema.json
src/template.html                # committed static runtime template with placeholders
scripts/
  import_legacy_source.py        # parameterized, provenance-safe legacy importer
  build_p0.py                    # canonical-data validation and static build
  validate_p0.py                 # deterministic P0 checks
  sync_github_pages.py           # generated public/ → docs/ copy
public/                          # generated static runtime
  index.html
  logo.svg
  manus-routes.json
docs/                            # generated GitHub Pages copy
```

## Material constraints

- Do not add a backend, database, accounts, analytics, payment flow, geocoder, map tiles, or clinical decision logic.
- Do not commit the raw upload or private verification material. The source manifest will record hash-based provenance instead.
- Do not claim records are operating, verified, licensed, precise locations, or distinct facilities without evidence.
- Do not silently merge, delete, or reclassify source observations. Duplicate candidates remain visible for owner/editorial review.
- Use repository-relative inputs and CLI arguments. A fresh checkout must build the website from canonical data.
- Keep `docs/` generated from `public/`; do not independently edit both copies.

## Verification evidence

The release must demonstrate: 112 source observations with one legacy ID each; no output `lat`/`lon` fields; all map counts reconcile as 108 records in 22 district groups plus 4 records in two coverage scopes; public and Pages builds agree except for the intentional relative favicon path; the static page parses; and live filters/export controls operate after regeneration.
