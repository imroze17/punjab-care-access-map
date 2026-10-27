# Punjab Care Access Map

A static directory map of **112 source-derived treatment, recovery, and referral records** in Punjab, India. It is an orientation and directory tool, not a clinical directory, availability checker, facility locator, or service verification system.

## P0 representation rule

The map intentionally **does not publish or invent facility coordinates**. It aggregates 108 source records into **22 reported-district count symbols**. Four Punjab-wide/statewide records are shown separately through coverage-scope controls. An address shown in a listing is source text, not a verified mapped coordinate. Current operation, ownership, eligibility, hours, fees, accessibility, and clinical services are not independently confirmed.

## Run locally

```bash
make check
make serve
```

The static site is served from `public/` on port 3000. The generated GitHub Pages copy lives in `docs/` and is synchronized from `public/` by the build.

## Build and validate

```bash
make build       # canonical data -> public/ -> docs/
make test        # importer regression tests
make validate    # canonical/runtime/Pages/static-JS coherence checks
make check       # build + test + validate
```

No package installation, server, database, accounts, geocoder, map tile API, or private upload is required for a normal build. `public/index.html` is generated; do not edit it directly.

## Refresh approved source data

The raw source upload is intentionally not committed. After an approved replacement source is available, run:

```bash
make refresh-data \
  SOURCE=/absolute/path/to/approved-source.txt \
  ARTIFACT_ID=source:approved-artifact \
  DATASET_VERSION=pca-YYYY-MM-vN
```

The importer validates the known six-field source contract, records the supplied artifact identity/hash and source-row lineage, retains the legacy `F001`–`F112` aliases, and uses the committed crosswalk to reuse durable record IDs for unchanged parsed observations. It fails rather than guessing when the source format or legacy reconciliation does not match. A changed/new source record requires a reviewed migration before it can enter this P0 baseline; it is never silently treated as an existing record or silently replaces one.

## Data and review artifacts

- `data/canonical/punjab-care-records.v1.json` — canonical source-record and observation model.
- `data/manifests/source-artifact.v1.json` — source-artifact identity, header contract, parser version, and SHA-256 hash.
- `data/migrations/legacy-id-crosswalk.v1.json` — legacy alias to durable record-ID registry/crosswalk.
- `data/reviews/duplicate-candidates.v1.json` — review prompts only; no source observations are merged, deleted, or hidden automatically.
- `data/generated/runtime-records.v1.json` — browser-safe, coordinate-free derived view.

See [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for the data model, rule boundaries, output accounting, map/export behavior, and outstanding editorial work. See [DEVELOPER_HANDOFF.md](DEVELOPER_HANDOFF.md) for the requested P0–P2 roadmap.

## CSV and map exports

The interactive page provides a filtered CSV export plus PNG/PDF map exports. CSV includes durable/legacy IDs, source fields, source-derived claim/role/scope fields, location granularity, map representation, and dataset version. The exporter neutralizes spreadsheet formula prefixes. PNG/PDF exports include the district-group interpretation and dataset version.
