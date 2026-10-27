# Punjab Care Access Atlas — Delivery ToDo

- [x] Publish a public, responsive static informational website presenting all 112 updated supplied de-addiction, treatment, rehabilitation, OOAT, methadone, and referral records across Punjab, India. The site must run without user accounts, a database, payments, a server, or third-party credentials.
- [x] Keep all listings as interactive markers and provide search across supplied listing information, primary Government, NGO / Trust, and Private category filters, plus detailed provider-type filtering.
- [x] Add an explicit Helpline / Office category so statewide and district referral records are discoverable without being misclassified as facility providers.
- [x] Keep districts clickable for geographic facility exploration and allow users to export the visible/current facility results as CSV.
- [x] Provide individually toggleable district boundary, district-label, cultural-region, and river layers. Preserve Majha, Doaba, Malwa, and Puadh as clearly named cultural-region overlays.
- [x] Show major river overlays with clear, high-contrast labels that name each river directly.
- [x] Restore the supplied reference design: a clean white-and-green interface with a dark-green header, rounded filter and map cards, sans-serif labels, blue/orange/purple provider marks, and the original responsive sidebar/map composition.
- [x] Remove the decorative grid and degree-boundary annotations while retaining the map’s interactive district, cultural-region, and river layers.
- [x] Add live map exports: PNG and one-page PDF downloads reflect the current filtered listings and visible layer state, and include an export map key.
- [x] Add an exhaustive project overview that documents the delivered map, the user-supplied CSV transformation process, data model, derived classifications, map layers, update workflow, exports, hosting preparation, and limitations.
- [x] P0 — Preserve all 112 supplied source records in a canonical record-and-observation model with a source-artifact manifest, original-row lineage, immutable record IDs, `F001`–`F112` legacy-ID crosswalk, explicit unknown states, and no automatic record deletion or merging.
- [x] P0 — Replace the legacy hard-coded importer/build dependency with a parameterized, reproducible checkout-only build that uses a committed source template and writes generated runtime, Pages, manifest, and validation artifacts.
- [x] P0 — Create an owner-reviewable duplicate-candidate report. Candidates must keep their source observations and legacy IDs; duplicate review must never silently merge same-site or similarly named records.
- [x] P0 — Separate source-derived record kind, ownership claim, service mentions, coverage scope, location granularity, and map-presentation semantics. Do not infer current operation, verified ownership, clinical suitability, or verified geographic coordinates.
- [x] P0 — Replace synthetic per-record marker coordinates with district-group map summaries and separate Punjab-wide/statewide coverage controls. Every map, detail, CSV, PNG, and PDF representation must state its uncertainty and must not imply facility locations.
- [x] P0 — Add deterministic P0 validation for canonical data/lineage, generated output coherence, Pages subpath safety, no coordinate-bearing public records, duplicate report shape, and baseline map-accounting totals.
- [ ] Publish the validated static build and confirm the durable public website URL.
