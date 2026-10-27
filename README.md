# Punjab Care Access Map

A static directory map of **112 source-derived treatment, recovery, and referral records** in Punjab, India. It is an orientation and directory tool, not a clinical directory, availability checker, facility locator, or service verification system.

## Representation rule

The map intentionally **does not publish or invent facility coordinates**. It aggregates 108 source records into **22 reported-district count symbols**. Four Punjab-wide/statewide records are shown separately through coverage-scope controls. An address shown in a listing is source text, not a verified mapped coordinate. Current operation, ownership, eligibility, hours, fees, accessibility, and clinical services are not independently confirmed.

## Use the directory

The directory is list-first. Browse through the native district selector, ownership-claim controls, coverage controls, source record role, source terms, and normalized search. Filters are reflected in the URL and can be cleared without using the map. The SVG is a visual district overview only; its count symbols do not identify individual facility locations.

Cards and details clearly identify supplied address/contact text and map/location uncertainty. Contacts are displayed as source text, not click-to-call links. CSV, PNG, PDF, and print routes preserve the source-derived/geographic caveats.

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

No package installation, server, database, accounts, geocoder, map tile API, tracking SDK, or private upload is required for a normal build. `public/` and `docs/` are generated; do not edit their contents directly.

## Refresh approved source data

The raw source upload is intentionally not committed. After an approved replacement source is available, run:

```bash
make refresh-data \
  SOURCE=/absolute/path/to/approved-source.txt \
  ARTIFACT_ID=source:approved-artifact \
  DATASET_VERSION=pca-YYYY-MM-vN
```

The importer validates the known six-field source contract, records the supplied artifact identity/hash and source-row lineage, retains the legacy `F001`–`F112` aliases, and uses the committed crosswalk to reuse durable record IDs for unchanged parsed observations. It fails rather than guessing when the source format or legacy reconciliation does not match. A changed/new source record requires a reviewed migration before it can enter the baseline; it is never silently treated as an existing record or silently replaces one.

## Data and review artifacts

- `data/canonical/punjab-care-records.v1.json` — canonical source-record and observation model.
- `data/manifests/source-artifact.v1.json` — source-artifact identity, header contract, parser version, and SHA-256 hash.
- `data/migrations/legacy-id-crosswalk.v1.json` — legacy alias to durable record-ID registry/crosswalk.
- `data/reviews/duplicate-candidates.v1.json` — review prompts only; no source observations are merged, deleted, or hidden automatically.
- `data/generated/runtime-records.v1.json` — browser-safe, coordinate-free derived view.
- `data/config/` and `data/locales/` — public-safe controls, aliases, and approved English interface messages.
- `data/reviewed/` — intentionally empty fail-closed translation/access-evidence registries.

## P1/P2 safeguards and release materials

The generated site uses a same-origin static asset model and restrictive CSP. It does not use browser storage, geolocation, external map tiles, or third-party executable code. See [PRIVACY_AND_SECURITY.md](PRIVACY_AND_SECURITY.md) and [ACCESSIBILITY_NOTES.md](ACCESSIBILITY_NOTES.md) for constraints and required human review.

English is the only publishable interface locale. A non-English locale, correction route, canonical URL, or verified access assertion requires owner approval and the reviewed data pipeline described in [LOCALE_AND_EVIDENCE_GOVERNANCE.md](LOCALE_AND_EVIDENCE_GOVERNANCE.md).

The repository includes an owner-gated GitHub Pages Actions workflow. It does not change Pages settings itself. See [RELEASE_RUNBOOK.md](RELEASE_RUNBOOK.md), [TEST_REPORT.md](TEST_REPORT.md), [QUALITY_REPORT.md](QUALITY_REPORT.md), and [MAINTAINER_CHECKLIST.md](MAINTAINER_CHECKLIST.md) before release.

For data-model detail, read [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md). For the owner-supplied roadmap and implementation status, read [DEVELOPER_HANDOFF.md](DEVELOPER_HANDOFF.md).
