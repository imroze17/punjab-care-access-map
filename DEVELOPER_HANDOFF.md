# Punjab Care Access Map — Developer Handoff and Implementation Specification

Version: 1.0
Prepared: 27 October 2026
Project owner: Imroze Singh
Repository: https://github.com/imroze17/punjab-care-access-map
Intended GitHub Pages address, not verified as live: https://imroze17.github.io/punjab-care-access-map/
Status: Proposed implementation specification derived from the project overview and repository audit. This document authorizes no clinical claims, service endorsements, data verification claims, or automatic record deletion.

---

## 0. Read this first

### 0.1 Objective

Improve the existing Punjab Care Access Map so it functions as a trustworthy, accessible service-navigation directory with a geographic overview. The central user task is:

> Find a relevant service or referral route in a district, understand what is and is not known about it, and identify a credible next contact.

The next version must not imply that every source record is a distinct treatment facility, that approximate display coordinates are real facility locations, or that inclusion confirms current operation or clinical suitability.

This is an improvement to the existing project, not a request for a new platform. Preserve its lightweight static architecture unless a specific requirement cannot reasonably be implemented within it.

### 0.2 Implementation principles

1. Distinguish records, facilities, services, offices, helplines, and multi-site programmes.
2. Match geographic representation to the evidence supporting the location.
3. Make uncertainty visible at the point of decision, including in exports.
4. Separate ownership from service provision and administrative role.
5. Preserve original source content and maintain an auditable transformation history.
6. Prioritize district → type of help → listing → contact over map decoration.
7. Provide a complete non-map route to every important task.
8. Treat missing information as unknown, not as absence of a service or restriction.
9. Do not invent verification, translation, eligibility, clinical, or accessibility information.
10. Keep builds reproducible, deployments automated, and public data appropriately scoped.

### 0.3 Evidence boundary

This handoff is based on:

- The supplied `PROJECT_OVERVIEW.md`.
- Repository structure inspected on `main`, resolved at commit `5683f19384ebfb3c35c93f697a4add7fc3ea560b` during the audit.
- Inspection of `scripts/prepare_updated_facilities.R`.
- Inspection of `scripts/restore_reference_design.py`.
- Partial inspection of `data/facilities.updated.json`; the connector truncated the response.
- The file-size response for `public/index.html`, approximately 1.92 MB.

The live page and raw HTML could not be retrieved using the available fetch tool. The full HTML was too large for the connector response. No completed browser, mobile, assistive-technology, contrast, performance, or security audit is being claimed.

The developer must inspect the current repository and live site before modifying them. Treat the commit above as an audit reference, not permission to overwrite newer work. Existing features may already satisfy some requirements. Verify before replacing them.

### 0.4 Requirement language

- MUST: required for the stated release gate.
- SHOULD: recommended; deviations require a documented reason.
- MAY: optional enhancement after the required work.
- Proposed: a product/editorial recommendation requiring owner review where indicated.
- Unknown: not established by the available evidence; never substitute a convenient assumption.

### 0.5 Out of scope

Do not introduce accounts, payment flows, clinical triage, treatment recommendations, patient records, public medical disclosures, unreviewed analytics, or real-time availability claims. Do not assume that a public service directory needs a database, API, framework migration, or third-party map service.

Do not use this project to collect personal substance-use histories. Do not introduce a public review/rating system. Do not rank treatment providers by quality without an independently justified and approved methodology.

---

## 1. Current project: preserve and repair

### 1.1 Documented capabilities

The overview describes a static, client-side application with:

- 112 supplied records, not an independently verified census of facilities.
- Search across listing content.
- Provider filters: Government, NGO / Trust, Private, Helpline / Office.
- A detailed selector generated from original `Type` values.
- Connected list and map selection.
- District selection and district boundaries/labels.
- Cultural-region overlays: Majha, Doaba, Malwa, Puadh.
- Schematic river lines and labels.
- Zoom/reset controls.
- CSV export of visible results.
- Client-side PNG and raster-PDF map exports.

The overview reports provider-category totals of 75 Government, 17 Private, 14 NGO / Trust, and 6 Helpline / Office. These are legacy source-derived classifications, not independently verified ownership counts. Reproduce these as a baseline before migration; do not force the corrected model to preserve a misleading category structure.

### 1.2 Relevant paths

| Path | Current role | Expected action |
|---|---|---|
| `PROJECT_OVERVIEW.md` | Project documentation | Update to reflect delivered architecture and limitations |
| `scripts/prepare_updated_facilities.R` | Parsing, normalization, classification, display anchors | Repair provenance, IDs, classification, input configuration, validation |
| `data/facilities.updated.json` | Generated legacy data | Retain as migration input/baseline; replace or version deliberately |
| `scripts/restore_reference_design.py` | Generates HTML from external reference | Replace external template dependency with committed source |
| `public/index.html` | Canonical runtime output | Update through reproducible build, not isolated generated-file edits |
| `scripts/sync_github_pages.py` | Copies runtime into `docs/` | Integrate into automated build/deployment or retire deliberately |
| `docs/index.html` | GitHub Pages output | Keep generated and synchronized if retained |
| `TODO.md` | Delivery checklist | Replace or extend with current backlog/status |

Historical generator scripts are not the default build path. Avoid modifying them unless necessary; label archived code clearly.

### 1.3 Initial developer reconnaissance

Before implementation:

- [ ] Record the current commit and deployment mechanism.
- [ ] Run the current site locally.
- [ ] Capture desktop and mobile baseline screenshots.
- [ ] Exercise every current filter, district action, selection, reset, and export.
- [ ] Inspect the complete HTML and dataset locally.
- [ ] Record console errors and network requests.
- [ ] Determine which assets are externally requested, including fonts.
- [ ] Establish whether a fresh checkout can rebuild without original upload directories.
- [ ] Confirm whether `public/` and `docs/` differ and why.
- [ ] Preserve baseline generated outputs before migration.

Deliver a short reconnaissance note listing confirmed findings, existing compliant features, new problems, and proposed implementation deviations.

---

## 2. Product scope and user tasks

### 2.1 Primary users

Design for people seeking help, family/support persons, community navigators, and referral workers. These are proposed design audiences, not findings from completed user research. Do not assume one level of clinical knowledge, English fluency, digital literacy, or map literacy.

### 2.2 Primary tasks

T1. Select a district and browse relevant options.
T2. Search for a known service, hospital, locality, or alternative district name.
T3. Understand whether an entry is a treatment site, programme, helpline, or office.
T4. Identify a documented service without interpreting ownership as service provision.
T5. See a contact route and understand whether it has been checked.
T6. Understand address/location uncertainty before travelling.
T7. Share or print a useful listing without losing caveats.
T8. Report inaccurate directory information without disclosing personal medical information.

### 2.3 Secondary tasks

Explore cultural/geographic context, inspect original source detail, download research-oriented CSVs, and compare directory representation across districts. These must not crowd out the primary tasks.

### 2.4 Non-goals for map interpretation

The application must not imply:

- A complete census of services.
- Actual service access, capacity, adequacy, or coverage from record counts alone.
- A service desert when there are no records in a district.
- Quality, licensing, current operation, or clinical appropriateness from inclusion.
- Distance, travel time, or nearest service from district anchors.

Required empty-district language: “No listings in this directory for the selected filters. This does not establish that services are unavailable.” Editorial wording can be refined without weakening the meaning.

---

## 3. Release structure and priorities

### P0 — Trust and data integrity

Required before promoting the revised site as an improved public navigation tool:

- Explicit record-kind model.
- Duplicate review workflow and no silent deletions.
- Evidence-aligned map representations.
- Record-level provenance and uncertainty display.
- Separate ownership, service role, and services offered.
- Durable identifiers and preserved source-row lineage.
- Correct interpretation of counts and missing data.
- Baseline regression and validation checks.

### P1 — Usability and maintainability

Required for the main revised release:

- District → help type → contact workflow.
- Mobile list-first experience.
- WCAG 2.2 AA-oriented implementation and manual testing.
- Reproducible local build and automated deployment.
- Contact actions, filter-state handling, useful empty states.
- Safe rendering and export handling.
- Export caveats and practical directory print view.

### P2 — Enrichment and reviewed localization

Deliver when content and review resources exist:

- Reviewed English/Panjabi Gurmukhi interface and content.
- Additional verified access fields.
- More precise verified geography.
- Expanded service-directory exports.
- Further community usability testing and refinements.

Scaffold localization in P1. Do not publish placeholder or unreviewed translated health content to satisfy a checkbox.

---

## 4. Data model: separate the concepts

### 4.1 Required conceptual entities

Maintain these distinctions even if the first implementation uses one denormalized JSON file:

- Source record: one item imported from a specific source version.
- Organization: the operator or coordinating body.
- Facility/site: a physical location, if identified.
- Service: a documented offering, potentially within a facility or across sites.
- Directory entry: the user-facing representation of a service, office, helpline, or programme.
- Evidence item: source information or a verification event supporting a specific claim.

One hospital may host several legitimate services. Two source records may describe one service. One multi-site source record may refer to multiple clinics whose individual locations are unknown.

### 4.2 Proposed runtime schema

Field names below are recommended. Equivalent implementations are acceptable if the semantics and validation are retained.

```typescript
type RecordKind =
  | 'treatment_site'
  | 'service_at_facility'
  | 'helpline'
  | 'coordination_office'
  | 'multi_site_programme'
  | 'unresolved';

type Ownership =
  | 'government'
  | 'ngo_trust'
  | 'private'
  | 'mixed'
  | 'unknown';

type LocationPrecision =
  | 'verified_site'
  | 'approximate_town'
  | 'district_only'
  | 'multi_site'
  | 'statewide'
  | 'unknown';

type OperationalStatus =
  | 'reported_operating'
  | 'reported_temporarily_closed'
  | 'reported_closed'
  | 'planned'
  | 'unknown';

type Evidence = {
  evidenceId: string;
  sourceTitle: string | null;
  sourceUrl: string | null;
  sourcePublishedDate: string | null;
  accessedDate: string | null;
  method: 'source_review' | 'provider_contact' | 'official_register' | 'other';
  supportsFields: string[];
  checkedDate: string | null;
  publicNotes: string | null;
};

type DirectoryEntry = {
  entryId: string;
  legacyIds: string[];
  organizationId: string | null;
  facilityId: string | null;
  serviceIds: string[];
  name: string;
  aliases: string[];
  recordKind: RecordKind;
  ownership: Ownership;
  servicesOffered: string[];
  serviceClassificationStatus: 'reviewed' | 'provisional' | 'unknown';
  districtCodes: string[];
  districtDisplayNames: string[];
  coverageScope: 'single_district' | 'multi_district' | 'statewide' | 'unknown';
  locality: string | null;
  addressDisplay: string | null;
  location: {
    precision: LocationPrecision;
    latitude: number | null;
    longitude: number | null;
    coordinateEvidenceId: string | null;
    uncertaintyNote: string | null;
  };
  contacts: Array<{
    kind: 'phone' | 'email' | 'website';
    displayValue: string;
    actionValue: string | null;
    purpose: string | null;
    lastVerifiedDate: string | null;
    verificationEvidenceId: string | null;
  }>;
  operationalStatus: OperationalStatus;
  operationalStatusAsOf: string | null;
  evidence: Evidence[];
  access: {
    openingHours: string | null;
    fees: string | null;
    referralRequirements: string | null;
    eligibility: string | null;
    languages: string[] | null;
    physicalAccessibility: string | null;
  };
  sourceRefs: Array<{
    sourceDatasetId: string;
    sourceRecordId: string;
    sourceRow: number | null;
  }>;
  editorialNotesPublic: string | null;
  reviewState: 'reviewed' | 'needs_review';
};
```

### 4.3 Additional maintained data, not necessarily runtime data

Maintain a controlled source layer with:

- Original name, district, address, type, contact, and remarks without destructive edits.
- Original source-row number assigned at ingestion.
- Source dataset version and import date.
- Original reference tokens, including unresolved `[reference:n]` strings.
- Transformation decisions and normalization rules.
- Duplicate candidate decisions, reviewer, date, and rationale.
- Identifier mapping and merge/split relationships.
- Private verification notes where necessary; do not publish these by default.

Do not embed private maintainer notes, individual staff details, raw correspondence, or sensitive verification evidence into public HTML/JSON.

### 4.4 Unknown and evidence rules

- Use `null` or explicit unknown enums consistently; document empty-array semantics.
- Unknown hours must not become “closed.”
- Unknown fees must not become “free.”
- Unknown language availability must not become “English only.”
- Unknown accessibility must not become “not accessible.”
- Missing contact information must not become “no contact exists.”
- A reviewed source row is not necessarily a verified operational service.
- A confirmed telephone number does not verify clinical services, hours, or address.
- A build timestamp is not a verification timestamp.
- Do not calculate a single green “verified” badge that masks unverified fields.

Prefer field-specific labels such as “Address checked on …” or “Telephone checked on …”. “Reported operating” requires dated evidence and must not be rendered as a guarantee.

### 4.5 Ownership and service taxonomy

Ownership must not contain `Helpline / Office`; those describe role. The legacy value must be preserved for traceability but migrated to appropriate fields. Do not infer ownership for a helpline simply because it was formerly grouped separately.

The legacy `serviceGroup` mixes service functions, provider ownership, and administration. Do not reuse it unchanged as the primary public service filter.

Proposed public help groups:

- Treatment services.
- Rehabilitation and recovery support.
- Medication-treatment services.
- Information and referral.
- Other / service details not confirmed.

These labels require editorial review and source-backed mappings. A single entry can have several service tags. Preserve original terms such as OOAT, MMT, OST, DDTC, and source `Type` in secondary detail. Expand acronyms only after confirming locally appropriate terminology with a qualified reviewer. Do not add counselling, detoxification, residential care, or medication provision based solely on a name or ownership category.

### 4.6 Identifier rules

- Generate durable IDs once and maintain them in the canonical source registry.
- Do not derive permanent IDs from row order, output order, or current district.
- Do not use mutable names as the sole identifier.
- Preserve legacy `F001`–`F112` references through `legacyIds` or a migration map.
- Distinguish entry, facility, service, organization, and source-record IDs.
- Merging entries must preserve redirects/aliases and source lineage.
- Splitting a programme into verified sites must preserve the original programme relationship.
- Reordering source rows must not change existing entry identities.

### 4.7 Dataset manifest

Include a versioned manifest with:

```json
{
  "schemaVersion": "2.0",
  "datasetVersion": "REPLACE_WITH_ACTUAL_VERSION",
  "sourceDatasetIds": [],
  "buildTimestamp": "REPLACE_AT_BUILD",
  "sourceRecordCount": null,
  "directoryEntryCount": null,
  "lastEditorialReviewDate": null,
  "verificationSummary": "See individual listings; build date is not verification date."
}
```

Do not ship placeholder values. Compute counts from actual output; do not hard-code 112 as a permanent invariant.

---

## 5. Ingestion, migration, and quality review

### 5.1 Source parsing

The legacy upload is CSV-like and contains unquoted commas in names and remarks; the quoted address is used as a parsing anchor. Do not replace this with naive comma splitting.

Required migration approach:

1. Preserve the raw source in an approved controlled location.
2. Assign `sourceDatasetId`, `sourceRecordId`, and original line/row identity before joins or normalization.
3. Parse into explicit logical columns.
4. Validate output against the legacy generated data and manually inspect ambiguous cases.
5. Produce a well-formed canonical maintained format, such as validated JSON or correctly quoted UTF-8 CSV.
6. Use a standard serializer/parser for future canonical data.
7. Retain a legacy-import adapter and fixtures if future imports require it.

Fail explicitly on malformed input. Handle or reject blank lines, quoted names, embedded quotes, missing remarks, commas in remarks, UTF-8 content, and multiline fields according to documented rules. Do not silently skip records or repair ambiguity without reporting it.

Use established JSON serialization rather than hand-built escaping. Escape embedded data safely when writing into HTML, including strings containing `</script>`.

### 5.2 Source-row issue to verify

The inspected R script assigns `sourceRow` after a merge with anchor data. This is a traceability risk, not a proven claim that all current row references are wrong.

Assign original row identities before merges and explicitly restore intended order. Add a fixture where merge/group operations reorder rows and assert that source references remain attached to the correct original content.

### 5.3 Duplicate review

Create a review report using normalized name, locality, address, district, organization, and service type. Similarity is a candidate-generation mechanism, not an automatic merge rule.

Seed review cases from the inspected data:

| Candidate | Observed concern | Required action |
|---|---|---|
| Legacy F026 / F028 | Very similar Sangrur DDTC names, same Civil Hospital address | Review whether duplicate descriptions or distinct services |
| Legacy F033 / F039 | Guru Kirpa Foundation DD&RC, Rara Sahib references, differing district text | Resolve entity and geographic relationship |
| Legacy F009 and similar CHC entries | “Various blocks” description | Classify as programme/aggregate until individual sites are identified |
| Legacy F006 and similar entries | “Planned/established” language | Review operational-status evidence; do not presume currently open |

These examples are from partial dataset inspection. Review the complete dataset, not only these cases.

Decision outcomes: confirmed duplicate, separate services at same site, separate sites, related programme/site, unresolved. Preserve all original source records regardless of the public presentation decision. Log every merge/split and explain count changes.

### 5.4 Reference-placeholder cleanup

Strings such as `[reference:13]` are unresolved source tokens, not usable citations.

- Preserve them in raw provenance.
- Resolve them to actual sources when possible.
- Do not fabricate source URLs.
- Do not present them as functional public references.
- Render a public “Source details not yet resolved” note where relevant.
- Separate historical background from current service facts.

### 5.5 Classification review

Replace catch-all NGO classification with `unknown` and a review flag. Replace catch-all service classification with unknown, not an implied government service.

Use explicit mapping tables with evidence/reviewer notes. Test each known source type plus a deliberately unfamiliar type. Unknown values must remain visible in validation reports and must not disappear from results.

### 5.6 Districts and coverage scopes

- Use a maintained canonical district table with codes, names, aliases, geometry IDs, and provenance.
- Retain source district strings separately.
- Preserve useful aliases: Ropar/Rupnagar, Nawanshahr/Shaheed Bhagat Singh Nagar, Mohali/Sahibzada Ajit Singh Nagar.
- Review ambiguous labels rather than silently forcing them into one district.
- Model multi-district coverage as an array, not a slash-separated single district.
- Model statewide records separately from administrative districts.
- Do not count `Punjab-wide` or `Statewide` as districts.
- A source location with no records still belongs in the district selector when supported by the canonical geography.

The overview describes 23 districts and 24 legacy display anchors, which include non-district scopes. Verify the geography version during implementation; do not treat those two counts as equivalent.

### 5.7 Migration reconciliation report

Produce a machine-readable report and human summary containing:

- Original source records ingested.
- Parse errors and warnings.
- Entries created, merged, split, archived, or unresolved.
- Source records mapped to each new entry.
- Legacy → durable ID mapping.
- Ownership and record-kind distributions.
- Location-precision distribution.
- Contact availability counts, explicitly not contact-verification counts.
- Unresolved references and duplicate candidates.
- Missing provenance or unsupported classifications.

Release must fail if source records disappear without an explicit documented disposition.

---

## 6. Geographic representation

### 6.1 Core rule

Map appearance must match location evidence. Do not plot every legacy record as an independent facility marker.

| Precision | Default map representation | Required explanation |
|---|---|---|
| Verified site | Individual point | Address/coordinate evidence available in details |
| Approximate town | Visually distinct town-level marker or group | “Approximate town location—not the service address” |
| District only | District-level group/count | “Listings grouped by district; individual locations not confirmed” |
| Multi-site programme | District/coverage context and expandable programme card | “Multiple sites; individual locations may not be listed” |
| Statewide | Separate statewide-services panel | “Statewide service; not a local facility marker” |
| Unknown | List only | “Location details not confirmed” |

“Verified site” requires evidence supporting the facility location. Coordinates inherited from a district anchor or automated geocoder are not verified just because they are numeric.

### 6.2 Remove misleading geographic jitter

The legacy sunflower offsets can remain only as a non-geographic screen-layout technique if their meaning is unmistakable. Preferred first release: district groups for unresolved locations and true site points only for evidenced locations.

If spiderfying a group, connect points to their group origin and treat offsets as screen coordinates, not latitude/longitude. Never export layout offsets as facility coordinates.

Separate:

- Verified/approximate geographic coordinates.
- District/town anchor metadata.
- Screen-layout offsets.

### 6.3 Prohibited geographic features on anchor data

Do not implement nearest-service ranking, distance badges, travel-time estimates, or directions to a jittered anchor.

A future external directions action may be offered for a confirmed address/location, with clear disclosure that it opens an external service. Do not launch third-party map searches automatically or request visitor location on page load.

### 6.4 District browsing

District selection must:

1. Update the district control, URL state, result summary, and map emphasis.
2. Apply consistently alongside search and service filters.
3. Keep statewide services in a separate clearly labelled section if they are shown.
4. Explain inclusion of multi-district programmes.
5. Permit clearing the district without clearing unrelated filters.

Do not imply a statewide entry is physically in the chosen district. If counts are shown separately, label them: “District-matched entries” and “Statewide information/referral entries.”

### 6.5 Cultural regions, rivers, and geography provenance

Retain optional cultural-region and river layers as orientation aids. Move them behind an “Explore map layers” control and default them off unless usability testing supports another choice.

Cultural regions are editorial wayfinding choices, not official administrative boundaries. River traces are schematic, not survey-grade hydrology. Preserve those caveats in layer descriptions and exports when layers are included.

Verify the district geometry source, version, and licensing/attribution requirements. Do not collapse ambiguous licensing descriptions into an unsupported single license. Retain required notices in website and export output.

---

## 7. Information architecture and layout

### 7.1 Desktop proposal

```text
Header: project name | concise purpose | language control when reviewed
Data/uncertainty notice: directory status + last dataset update

Primary controls:
[District] [Type of help] [Search by name/place] [Clear filters]
[More filters] [List / Map]

Result summary + active-filter chips

Results list / selection details       Geographic overview
                                      [Explore map layers]

Statewide information/referral section, where applicable

Secondary tools: print directory | map PNG/PDF | data CSV
About | methodology | sources | limitations | report directory issue
```

Do not duplicate contact details or selected-state logic inconsistently across panels. A single shared entry model should drive cards, details, map tooltips, print, and exports.

### 7.2 Mobile proposal

- List-first default, unless the user follows a map-specific shared link.
- Prominent List/Map segmented control.
- Collapsible filters with active count and clear summary.
- No requirement to manipulate a map to choose a district.
- Selected listing details immediately reachable without hunting below a tall map.
- No fixed panel or footer that obscures focused controls.
- Maintain state when switching views or rotating the device.
- Prefer one principal page-scroll region; avoid nested scrolling traps.

### 7.3 Header and metrics

Suggested purpose copy:

> Find listed treatment, recovery, and referral services in Punjab, India.

Suggested caveat:

> This directory may be incomplete. Service details and current availability are not confirmed for every listing. Check individual entries before travelling.

Use computed, accurately named metrics:

- Directory entries.
- Identified physical sites, only if the entity model supports this count.
- Entries with a listed telephone number.
- Districts represented in this directory.

Do not use “districts reached,” “people served,” “coverage,” “available beds,” or “facilities” for counts that do not establish those concepts. Do not infer access or service adequacy from dot density.

---

## 8. Search, filters, counts, and application state

### 8.1 Search behavior

Search indexed public fields: display name, aliases, district names/aliases, locality, public address, reviewed service tags, and meaningful source terms. Do not index private editorial notes.

- Trim leading/trailing spaces.
- Normalize Unicode consistently without damaging Gurmukhi text.
- Use case-insensitive matching where appropriate.
- Preserve the displayed spelling.
- Support common district aliases through explicit tables.
- Define multi-word matching clearly; recommended all query tokens must match indexed content.
- Debounce typing enough to avoid excessive rendering, without an unnecessary Search button.
- Do not send queries to analytics or third parties by default.

Search should not introduce unreviewed medical synonyms that change service meaning.

### 8.2 Filter dimensions

Primary: district, type of help, search.
Secondary: ownership, record kind, contact information available, and reviewed location precision if useful.
Advanced/debug: original source type.

“Telephone listed” must not be labelled “Telephone verified.” Unknown categories must be selectable and included by default.

### 8.3 Combination rules

- AND between independent dimensions.
- OR within a multi-select dimension.
- All results by default; no hidden ownership exclusions.
- Clearing one chip clears only that filter.
- “Clear filters” resets search and directory filters, not necessarily map-layer preferences.
- “Reset map view” resets map extent only.
- Label any full reset explicitly.

Preserve the selected entry if it still matches; otherwise clear selection and announce why. Never leave an unrelated stale detail panel beside filtered results.

### 8.4 Count rules

Compute totals from the same filtered entry set used by the list and map. Deduplicate entries referenced by multiple service tags. Define whether facet counts are global totals or counts available under other active filters; recommended available counts with the current facet omitted. Document and test the chosen semantics.

When a selected district includes statewide resources, separate their counts to avoid inflating local site totals. A multi-site programme is one directory entry until individual sites are identified; it is not one physical clinic and not an inferred number of clinics.

### 8.5 Empty and failure states

- No matches: explain active filters and provide a clear-filter action.
- No local entries: state that the directory may be incomplete; offer separately labelled statewide resources only if present in maintained data.
- Missing phone: “Telephone not available in the supplied source.”
- Missing hours/fees/eligibility: “Not confirmed.”
- Data-load error: visible explanation and retry if relevant; never show a misleading zero count.
- Export error: accessible status and retry; do not silently download an empty file.
- Invalid shared-link ID: explain that the entry may have changed; use a redirect mapping if available.

### 8.6 URL and persistence

Support shareable state using query/hash parameters for district, service, search, view, and entry ID. Validate all parsed values against known data. Preserve browser back/forward behavior.

Do not store search terms, selected services, or browsing history persistently by default. If preferences such as language or layer visibility are stored, keep them separate from sensitive navigation state and document storage behavior.

---

## 9. Result cards, detail panels, and actions

### 9.1 Card content order

1. Service/entry name.
2. Record-kind label.
3. District/locality or coverage scope.
4. Documented service tags.
5. Contact route, if supplied.
6. Short verification/location warning.
7. “View details” and relevant action.

Avoid a wall of raw remarks in the compact card. Make ownership secondary to service role.

### 9.2 Detail content order

- Name and aliases where useful.
- Treatment site / service at facility / helpline / office / programme / unresolved.
- Services documented and source terminology.
- Address and location precision.
- Telephone/email/website with contact-specific verification status.
- Opening hours, fees, referral requirements, eligibility, languages, and accessibility when evidenced; otherwise clearly unknown.
- Operational-status evidence and date, where available.
- Source links and source dates.
- Public notes and historical context, separated from current facts.
- Report incorrect information.
- Share/print this listing.

### 9.3 Contact handling

- Preserve original contact text in source data.
- Normalize actionable numbers separately; do not guess missing digits or country/area codes without an explicit reviewed rule.
- Use reviewed `tel:` actions for parseable numbers.
- Where normalization is ambiguous, show selectable text and “Number format needs confirmation”; do not create a misleading action.
- Add email/website actions only for actual maintained values.
- State when contact information is a general office/referral number rather than the service itself.
- No action should promise current availability.

### 9.4 Suggested public copy

| Situation | Proposed text |
|---|---|
| District-only location | “District-level listing. The service address has not been confirmed.” |
| Approximate town | “Approximate town location—not a confirmed service location.” |
| Missing operation evidence | “Current opening status has not been confirmed.” |
| Multi-site record | “This entry describes a programme across multiple locations, not one identified clinic.” |
| Coordination office | “Information/coordination office. Treatment at this address is not established by this listing.” |
| Source date unknown | “Source publication date not available.” |
| Unresolved classification | “Service details need review.” |

Owner may refine tone; preserve factual boundaries.

### 9.5 Correction pathway

Use an owner-approved maintained contact or issue intake mechanism. Do not invent an email address. A static mailto/issue link is sufficient if the owner approves it; a backend is not required.

Prefill only entry ID, public entry name, and the page URL. Include:

> Please report directory information only. Do not include personal medical details. This channel is not monitored for urgent assistance.

If using GitHub issues, prominently disclose that submissions may be public and may require an account. Provide a less technical route if an owner-approved alternative exists. Do not present GitHub as a universally accessible reporting solution.

Do not add emergency numbers or clinical crisis instructions without current authoritative local verification and editorial approval. If approved safety content is added later, give it an explicit source and review date.

---

## 10. Accessibility specification

### 10.1 Standard and scope

Implement toward WCAG 2.2 Level AA and document automated/manual testing. Do not claim certification from a scanner or this handoff. Accessibility applies to filters, cards, map alternatives, detail panels, status updates, dialogs, errors, and exports/print alternatives.

References:

- https://www.w3.org/TR/WCAG22/
- https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/

### 10.2 Required implementation

- Semantic headings, landmarks, labels, native buttons/selects where suitable.
- Skip link to results/main content.
- Accessible names for icon-only actions.
- Persistent visible focus with no obscured focused elements.
- All primary functions usable by keyboard.
- Textual result/list alternatives for map selection and district browsing.
- Category labels or shapes in addition to colour.
- Selected/toggle states programmatically exposed (`aria-pressed`, selected option, etc.).
- Accessible result-count updates using a restrained polite live region.
- Relevant loading/error messages exposed to assistive technology.
- No hover-only essential information.
- Reduced-motion support.
- Logical reading order independent of visual column positioning.

### 10.3 Map accessibility approach

Do not make hundreds of decorative SVG paths keyboard stops. Choose and document one coherent approach:

A. Fully equivalent list and district controls, with map treated primarily as a visual overview; or
B. Accessible interactive map elements plus equivalent list controls.

If markers are keyboard-interactive, provide appropriate roles, accessible names, Enter/Space behavior, visible focus, and predictable selection. Do not apply button roles without implementing button behavior. District selection must always be possible without the map.

### 10.4 Focus behavior

- Filtering must not unexpectedly move focus.
- Selecting a card must make details discoverable without trapping focus.
- Modal/sheet details, if used, must support Escape and return focus to the trigger.
- Non-modal details should have a logical heading and optional explicit focus transition following a user action.
- Closing details or changing views must not lose keyboard position to the document root.

### 10.5 Contrast, targets, reflow

Validate relevant WCAG contrast requirements, including normal text, large text, and non-text interface elements. Do not rely on legacy colour values without measurement.

WCAG 2.2 AA target-size requirements generally use a 24 × 24 CSS-pixel minimum or permitted spacing/other exceptions. Aim for approximately 44 × 44 CSS pixels for primary mobile actions where practical; this larger design target is not a blanket statement of the AA minimum.

Test reflow at 320 CSS pixels and text/zoom enlargement. A map may need spatial navigation, but surrounding controls and directory content must not require horizontal scrolling to complete the core task.

### 10.6 Minimum manual coverage

- Keyboard-only complete primary journey.
- NVDA with Firefox or Chrome on Windows.
- VoiceOver with Safari on macOS or iOS.
- Actual touch device where available.
- 200% text enlargement and high browser zoom/reflow checks.
- Reduced motion.

Record tested environments and gaps. Automated checks supplement, not replace, manual testing.

---

## 11. Language and localization

### 11.1 Architecture now, reviewed content before publication

Extract interface strings into a translation dictionary. Avoid concatenating fragments that assume English word order. Support appropriate `lang` values and mark language changes in mixed-language content.

Proposed initial languages: English and Panjabi written in Gurmukhi. The owner must approve translated content and reviewer arrangements. Additional languages/scripts are separate scope decisions.

### 11.2 Translation requirements

- Use a competent language reviewer familiar with local service terminology.
- Review acronyms, treatment terms, uncertainty language, and stigma-sensitive wording.
- Preserve official names when no approved translation exists.
- Distinguish translated interface text from translated service content.
- Maintain a source-language fallback with a clear indication where translation is unavailable.
- Test Gurmukhi glyph coverage and layout on actual target devices.
- Do not publish machine-translated clinical descriptions without review.

Add reviewed search aliases/transliterations deliberately. Do not promise automatic cross-script search until implemented and tested.

---

## 12. Exports, printing, and sharing

### 12.1 Separate export products

1. Map image/PDF: geographic overview, not directions or a complete service directory.
2. Directory print view/PDF: readable service details and contact information.
3. Structured CSV: documented public data for further work.

Retain existing functions where useful, but correct their semantics and caveats.

### 12.2 Map export content

Include title, dataset version, export date, filters, entry-count definition, location-precision legend, approximate-location caveat, verification caveat, source attribution, and canonical website URL.

Include cultural-region/river caveats if those layers are visible. Ensure the legend does not hide entries or imply inactive layers are visible. Define whether selection highlights are included. Use a coherent export extent and test zoomed states.

If the existing custom raster-PDF exporter is retained, label the product accurately and test it. A raster map PDF is not an accessible text directory.

### 12.3 Directory print view

Use semantic HTML and print CSS as the baseline. Include:

- District/filter heading and data version.
- Entry name and role.
- Documented services.
- Address and precision.
- Contact route and verification status.
- Missing-information labels where important.
- Source/website and limitations.

Avoid clipping or splitting cards awkwardly across pages. Do not rely on background colours being printed. Provide a usable HTML alternative; do not claim a generated PDF is tagged/accessible unless verified.

### 12.4 CSV contract

Recommended columns:

`entryId`, `name`, `recordKind`, `ownership`, `servicesOffered`, `districtCodes`, `districtNames`, `coverageScope`, `locality`, `addressDisplay`, `locationPrecision`, `latitude`, `longitude`, `phoneDisplay`, `phoneLastVerifiedDate`, `operationalStatus`, `operationalStatusAsOf`, `sourceUrls`, `datasetVersion`, `exportedAt`.

Document multi-value serialization. Include legacy source columns only in a clearly documented advanced export if appropriate. Do not export private notes or screen-layout offsets as geographic data.

Protect against spreadsheet-formula injection in untrusted text values, including values beginning with `=`, `+`, `-`, or `@`, while preserving data meaning in the documented export contract. Correctly quote commas, quotes, newlines, and Unicode. Test phone numbers and leading zeros explicitly.

### 12.5 Export behavior

- Export the same filtered logical entry set shown in results.
- Make statewide-inclusion semantics explicit.
- Disable duplicate submissions during work without hiding status.
- Show accessible success/failure feedback.
- Revoke temporary object URLs.
- Handle image/font failures and empty states gracefully.
- Never omit warnings merely to make the map cleaner.

---

## 13. Build, repository, and deployment

### 13.1 Architecture constraints

Keep a static deployment. Source may be modular even if the final runtime remains self-contained. Do not rewrite into a framework without an approved rationale tied to an actual requirement.

Recommended separation:

```text
data/
  canonical/              # approved maintained public content or references
  generated/              # runtime outputs and manifest
  schemas/
  reviews/                # public-safe migration decisions only
src/
  template.html
  styles/
  js/
  locales/
scripts/
  import_legacy.*
  validate_data.*
  build.*
  sync_github_pages.*     # only if docs deployment is retained
tests/
  fixtures/
  unit/
  integration/
  e2e/
public/                   # generated runtime
.github/workflows/
README.md
PROJECT_OVERVIEW.md
```

Equivalent smaller structures are acceptable. Do not commit controlled raw uploads, private evidence, or credentials just to fill this structure.

### 13.2 Reproducible inputs

Remove hard-coded `/home/ubuntu/upload/...` dependencies. Commit the approved reusable template. Accept input paths through documented CLI arguments or configuration. Validate missing inputs with actionable errors.

A clean checkout plus explicitly supplied approved input must be enough to build. If maintained public canonical data is committed, normal UI builds should not require the original raw upload.

Pin/document dependencies. If retaining R and Python, explain the responsibilities of each. A language consolidation is optional, not a prerequisite.

### 13.3 Build entry point

Provide one documented command for validation and production generation. Examples are illustrative, not a required toolchain:

```bash
make validate
make build
make test
```

Required properties:

- Fails on invalid schema, missing lineage, broken IDs, unsupported precision claims, or unsafe output.
- Computes counts from data.
- Generates the dataset manifest.
- Produces deterministic content apart from declared metadata timestamps.
- Produces repository-subpath-safe links.
- Avoids brittle text replacement of unrelated template fragments where structured templating is possible.

### 13.4 Deployment choice

Choose and document one:

A. GitHub Actions builds and deploys the generated site as a Pages artifact; or
B. An automated build generates/synchronizes `docs/` for the current branch-folder deployment.

Do not maintain independently edited `public/index.html` and `docs/index.html`. If both exist, validate expected differences such as relative favicon paths and fail on unexplained drift.

Repository configuration changes and production deployment must follow owner approval and normal repository permissions.

### 13.5 CI gates

On pull requests:

1. Validate schema and references.
2. Run parsing/migration unit tests.
3. Build production assets.
4. Run UI tests against the built output.
5. Run automated accessibility checks.
6. Check internal links/subpath assets.
7. Check for unresolved placeholders in public output.
8. Produce a public-safe quality summary.

On approved production branch changes: deploy only after required checks pass. Keep an identified rollback commit/artifact.

---

## 14. Security, privacy, and performance

### 14.1 Rendering and URL safety

Treat imported names, remarks, addresses, URLs, and contacts as untrusted text. Prefer `textContent` and safe DOM construction; do not interpolate raw fields into `innerHTML`.

Validate external URL schemes. Do not allow `javascript:` or arbitrary executable links. Use appropriate external-link protection when opening new tabs. Validate URL state and IDs. Safely serialize JSON embedded in script contexts.

Consider a deployment-compatible content security policy. If inline code is retained, document how the policy accommodates it without pretending that an unrestricted policy provides protection.

### 14.2 Privacy

- No tracking or third-party analytics by default.
- No geolocation request on load.
- No persistent storage of sensitive search/filter history by default.
- No public health-information collection in correction forms.
- Inspect fonts, images, map resources, and widgets for third-party requests.
- Clearly distinguish client-side processing from hosting-provider logs; do not claim that visiting the website creates no server logs anywhere.
- Public data must contain only information approved for publication.

### 14.3 Performance requirements

The canonical HTML was reported as approximately 1.92 MB. Profile actual transfer size, parsing, SVG complexity, and interaction time before choosing optimizations. Do not equate uncompressed source size with transferred size.

Potential remedies: geometry simplification with visual validation, reduced coordinate precision, reusable geometry, less repeated markup, batched updates, and deferred secondary work. Keep geographic topology and attribution intact.

Proposed targets, measured on a documented test device/profile:

- No unnecessary third-party runtime requests.
- No console errors in the primary journey.
- Search/filter update typically within 200 ms for this small dataset after input debounce.
- No interface lockup during exports.
- Record baseline and final page-weight, rendering, and interaction measurements.

These are engineering acceptance targets, not claims about current measured performance. If offline support is desired, scope and test it explicitly; a static site is not automatically offline-capable.

---

## 15. Test plan and acceptance matrix

### 15.1 Data tests

| ID | Test | Expected result |
|---|---|---|
| D01 | Import the baseline source | Reconciles with the legacy 112 source records or explicitly documented source changes |
| D02 | Names/remarks containing commas | Logical columns preserved |
| D03 | Quotes, newlines, Unicode, empty optional fields | Valid serialization or explicit import error; no silent corruption |
| D04 | Reorder source rows | Durable entry identities unchanged |
| D05 | Join/reorder anchor data | Original source-row/content relationships unchanged |
| D06 | Unknown source type | Unknown/review flag, not NGO/government fallback |
| D07 | Multi-site programme | Not counted/rendered as one verified physical site |
| D08 | Statewide scope | Not counted as an administrative district |
| D09 | Missing verification dates | No invented checked dates |
| D10 | Merge/split candidate | Source lineage and legacy references preserved |
| D11 | Public runtime inspection | No private notes, sensitive correspondence, or controlled source content |
| D12 | Schema and cross-references | All IDs unique, references valid, enums valid |
| D13 | Verified-site classification without evidence | Validation fails |
| D14 | Rebuild without content changes | Stable IDs and equivalent runtime content |

### 15.2 Functional tests

| ID | Scenario | Expected result |
|---|---|---|
| F01 | Initial page load | Accurate result count, all intended default entries, uncertainty notice |
| F02 | District alias search | Canonical district and matching entries discoverable |
| F03 | Combine district + help type + ownership | Defined AND/OR behavior and matching list/map/counts |
| F04 | Clear one filter chip | Only that dimension changes |
| F05 | Filter out selected entry | Stale details cleared with understandable feedback |
| F06 | Select list result | Corresponding map representation/details update without false precision |
| F07 | Choose district without map | Full task remains available |
| F08 | Show statewide entries | Separately labelled and not presented as local sites |
| F09 | No results | Helpful empty state, no inference of service absence |
| F10 | Browser back/forward/shared URL | State restored correctly; invalid parameters safely handled |
| F11 | Phone normalization ambiguity | No guessed call destination |
| F12 | Reset map | Does not unexpectedly erase directory filters |
| F13 | Data failure | Visible error, not misleading zero entries |
| F14 | Report issue | Correct public ID, privacy warning, approved destination |
| F15 | Map/list switch and device rotation | Filters/selection preserved appropriately |

### 15.3 Accessibility tests

| ID | Test | Expected result |
|---|---|---|
| A01 | Keyboard-only district → result → details → contact | Complete without trap or hidden focus |
| A02 | Screen reader filter changes | Labels, states, and result updates understandable |
| A03 | Narrow viewport/high zoom | Core controls/results reflow without task-blocking clipping |
| A04 | Colour removed or simulated deficiency | Roles/categories/selection still understandable |
| A05 | Touch targets | AA requirements met; primary mobile actions comfortably usable |
| A06 | Open/close details dialog, if present | Correct focus entry, Escape, and focus return |
| A07 | Reduced motion | Nonessential motion suppressed |
| A08 | Automated audit | No unresolved critical/serious issues in tested primary states; manual review still completed |

### 15.4 Export tests

| ID | Test | Expected result |
|---|---|---|
| E01 | CSV with active filters | Same logical entry set as results |
| E02 | CSV commas/quotes/Unicode/phones | Correct round-trip under documented contract |
| E03 | Formula-like source strings | Spreadsheet injection mitigated |
| E04 | Map PNG/PDF | Opens correctly, includes filters/version/caveats/attribution |
| E05 | Zoomed or layer-modified map | Extent and legend remain coherent |
| E06 | Directory print | Readable cards, contacts, unknowns, sources; no clipped content |
| E07 | Empty export or conversion failure | Accessible feedback, no misleading output |
| E08 | Raster PDF | Not represented as an accessible text directory |

### 15.5 Environment coverage

Test current supported versions of Chrome, Firefox, Safari, and Edge where available; include iOS Safari and Android Chrome. Document actual versions, devices, viewport sizes, network/CPU profiles, and any unsupported cases. No fabricated test results.

### 15.6 User acceptance tasks

Conduct a small formative review with the owner and, where feasible, intended users. This is not a claim of formal validation.

Ask participants to:

1. Find a relevant listing in a chosen district.
2. Explain whether the listing is a site, office, helpline, or programme.
3. Explain whether the marker is an exact location.
4. Identify what is unconfirmed.
5. Find a contact or recognize that none is supplied.
6. Share/print the entry and locate a correction route.

Record task completion, misunderstandings, hesitation, and terminology problems. Set recruitment/consent arrangements appropriate to the context. Do not ask participants to disclose personal treatment histories for this interface test.

---

## 16. Prioritized developer backlog

Each ticket should be independently reviewable. Estimates are intentionally omitted until the current code and complete data have been inspected.

| Ticket | Priority | Deliverable | Depends on | Done when |
|---|---|---|---|---|
| DEV-01 | P0 | Baseline reconnaissance and regression inventory | None | Current behavior, build/deploy state, screenshots, limitations documented |
| DEV-02 | P0 | Schema, manifest, canonical district/alias table | DEV-01 | Versioned schema and examples validated |
| DEV-03 | P0 | Safe import and provenance preservation | DEV-02 | Original fields/rows retained and parser fixtures pass |
| DEV-04 | P0 | Durable identity registry and migration mapping | DEV-03 | Reordering/merge/split tests pass |
| DEV-05 | P0 | Duplicate and record-kind review report | DEV-03/04 | Every source record has explicit disposition; owner resolves or flags candidates |
| DEV-06 | P0 | Ownership/service/role separation | DEV-02/05 | Unknown fallbacks and reviewed mappings implemented |
| DEV-07 | P0 | Evidence and verification display | DEV-02/03 | No build-as-verification or unsupported green badge |
| DEV-08 | P0 | Precision-aligned map and scope counts | DEV-05/06 | District/programme/statewide entries cannot masquerade as exact sites |
| DEV-09 | P1 | Primary filters, URL state, empty states | DEV-06/08 | Functional matrix passes |
| DEV-10 | P1 | Cards, details, contacts, correction route | DEV-07/09 | Core journey usable without map; approved intake destination |
| DEV-11 | P1 | Mobile layout and accessibility remediation | DEV-09/10 | Manual/automated results documented and blockers resolved |
| DEV-12 | P1 | Reproducible template/build and CI | DEV-01/02 | Clean build, safe subpath deployment, no output drift |
| DEV-13 | P1 | Safe CSV and contextual map exports | DEV-07/09/12 | Export matrix passes |
| DEV-14 | P1 | Directory print view | DEV-10/13 | Practical readable output with caveats |
| DEV-15 | P1 | Security/privacy/performance checks | DEV-09–14 | Findings resolved or explicitly accepted with rationale |
| DEV-16 | P2 | Localization scaffold/content workflow | DEV-10/11 | All strings externalized; reviewed content gating works |
| DEV-17 | P2 | Reviewed Panjabi/Gurmukhi release | DEV-16 + reviewer | Language/terminology/layout review complete |
| DEV-18 | P2 | Verified access-field enrichment | Evidence workflow | New claims have field-level evidence and dates |
| DEV-19 | P1 | Final handover and rollback drill | Required release tickets | Documentation, tests, deploy and recovery steps complete |

Parallel work is appropriate after the schema and semantics are agreed. Do not let visual work lock in misleading categories before the data model is corrected.

---

## 17. Decisions requiring owner/editorial input

These decisions must be resolved or transparently deferred. The developer must not invent answers.

1. Who is the named directory maintainer and backup?
2. Which correction channel is approved and monitored?
3. Who reviews ambiguous entities, operational-status claims, and service taxonomy?
4. What source evidence is acceptable for address, phone, operation, and service claims?
5. Which information is safe to publish, including contact details and verification notes?
6. Who reviews Panjabi/Gurmukhi translations and clinical terminology?
7. Should unresolved entries remain visible with warnings, or move to an explicitly labelled unconfirmed section?
8. Should approved statewide resources appear with every district selection? Recommended: separate section, never mixed into local site counts.
9. What maintenance/review cadence is sustainable? Set a policy; do not invent freshness claims or automatic review dates.
10. Is the one-file runtime a strict requirement, or may static assets be separated for maintainability/performance?
11. Should deployment remain branch-folder based or move to an Actions artifact?
12. Is any approved, locally verified urgent-assistance content to be added? If not, do not improvise it.

For unresolved editorial decisions, use conservative unknown states and document the limitation. A site can ship with openly unknown service details; it cannot ship with fabricated certainty.

---

## 18. Release gates and final deliverables

### 18.1 Required release gates

- [ ] Every imported source record has traceable disposition.
- [ ] Duplicate candidates are reviewed or visibly unresolved, not silently merged.
- [ ] Record kind, ownership, services, and coverage are separate concepts.
- [ ] District anchors and screen offsets cannot be mistaken for verified coordinates.
- [ ] Statewide/multi-site records are not counted as local physical facilities.
- [ ] No current-operation or verification claim lacks supporting evidence.
- [ ] No unresolved placeholder tokens leak as apparent public citations.
- [ ] Search/filter/list/map/export counts agree under documented rules.
- [ ] The complete core journey works without map interaction.
- [ ] Mobile and accessibility tests are documented with no unresolved blocking issues.
- [ ] Public rendering and exports pass security/privacy checks.
- [ ] Build works from a clean checkout plus documented inputs.
- [ ] Production output and deployment source are synchronized or single-source.
- [ ] Print/export outputs retain limitations, version, and attribution.
- [ ] Owner reviews public terminology, correction channel, and uncertainty copy.
- [ ] Production deployment and rollback are verified.

### 18.2 Developer handover package

Provide:

1. Implemented source and generated runtime through reviewable commits/PRs.
2. Updated project overview and README.
3. Data dictionary and versioned schema.
4. Migration reconciliation report and durable-ID map.
5. Public-safe review decisions and remaining data-quality queue.
6. Test report covering automated, manual, browser, mobile, accessibility, and exports.
7. Before/after screenshots with no unsupported claims of usability improvement.
8. Build/deploy/update instructions, dependencies, and input requirements.
9. Known limitations and deferred scope.
10. Rollback instructions and identified prior stable version.
11. Maintainer checklist for future data updates.
12. Summary of any departures from this specification and owner decisions approving them.

### 18.3 Ongoing update checklist

For each update:

1. Register the new source version.
2. Preserve raw content and original record identities.
3. Import and validate.
4. Review new/changed service classifications and locations.
5. Review duplicate candidates and unresolved references.
6. Update field-specific evidence only where actual checking occurred.
7. Reconcile counts and IDs.
8. Build and run required tests.
9. Review public output and exports.
10. Obtain editorial approval where needed.
11. Deploy and smoke-test the public URL.
12. Record the change log and next maintenance responsibilities.

Never treat a successful build as proof that service information is current.

---

## 19. Source and interpretation notes

### Project evidence

- `PROJECT_OVERVIEW.md`, supplied by the owner and also present in the repository.
- Repository audit reference: `5683f19384ebfb3c35c93f697a4add7fc3ea560b`.
- `scripts/prepare_updated_facilities.R`: input path, custom parsing, district normalization, classification fallbacks, anchor offsets, sequential IDs, source-row assignment, manual JSON generation.
- `scripts/restore_reference_design.py`: external reference-template path, replacement-based generation, export implementation.
- `data/facilities.updated.json`: partial inspected output, including the example review candidates identified above.
- `public/index.html`: file-size metadata only during the audit, not full DOM/runtime inspection.

### Public standards

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C target size guidance: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- W3C overview of additions in WCAG 2.2: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/

WCAG references support the accessibility requirements. The specific schema, proposed layout, priorities, copy, engineering targets, and backlog are recommendations developed for this project, not requirements prescribed verbatim by those standards. No overseas provider-directory regulation is asserted to govern this Punjab directory.

### Final implementation instruction

Deliver a clearer service-navigation tool, not merely a more polished map. When evidence is weak, improve the representation of uncertainty rather than generating precision. When source records are heterogeneous, preserve their distinctions rather than forcing them into a facility count.

---

## Implementation status — P0 foundation completed (2026-10-27)

This appended section records the current codebase; the owner-supplied roadmap above remains the governing P0–P2 specification.

### Delivered P0 outcomes

- A canonical `pca-record/v1` record-and-observation dataset preserves all 112 supplied rows, original-row lineage, source/line/tuple hashes, parser version, legacy aliases, explicit unknown states, and no automatic deletion or merging.
- The raw source upload is not committed. `data/manifests/source-artifact.v1.json` provides hash-based provenance and source-contract metadata.
- `pca:record:*` durable identifiers and `F001`–`F112` aliases are linked in a committed legacy-ID crosswalk. Re-importing unchanged parsed records through `--crosswalk` retains IDs after row reordering; a regression test covers this behavior.
- Source-text-only rules separate record role, ownership claim, service mentions, coverage, source-address granularity, and map presentation. They do not make operational, legal, clinical, ownership, or geographic verification claims.
- `data/reviews/duplicate-candidates.v1.json` contains review prompts only: three duplicate candidates and 27 same-location/different-source-label cases. No candidate is auto-merged, deleted, or hidden.
- The public runtime has no record coordinates. It shows 108 records as 22 district-group count symbols and four statewide/multi-district records through coverage-scope controls.
- The page, record details, CSV, PNG, and PDF exports explicitly describe district/coverage grouping and uncertainty. CSV neutralizes formula-like cell prefixes.
- The normal checkout build no longer depends on `/home/ubuntu/upload/...`: `make build`, `make test`, `make validate`, and `make check` produce and validate `public/` and `docs/` from committed canonical inputs.

### Validation evidence

At implementation time, `make check` passed. It rebuilt `public/` and `docs/`, ran importer contract and row-reorder durable-ID tests, verified canonical/runtime/Pages coherence, checked no public coordinate-bearing records or legacy coordinate renderer, and parsed the inline static JavaScript. Manual browser testing confirmed coverage-scope filtering and filtered CSV, PNG, and one-page PDF downloads.

### Still open

P1 and P2 work remains open. In particular: editorial duplicate decisions, external verification, formal privacy/public-display policy, accessibility audit/remediation, automated CI/CD deployment, monitoring, and any future verified-geocode governance have not been represented as completed by P0.


---

## Implementation Status — P1/P2 Safe Static Release (2026-10-27)

### Implemented P1 work

The static application now uses a list-first native district journey, source-role and source-term filters, normalized search, active filter chips, URL/back-forward state, no-results/status handling, responsive List/Map controls, visible focus, a skip link, a polite status region, print styling, source-contact caveats, and source-derived CSV/PNG/PDF exports. The SVG remains a visual overview with a native district alternative; district count symbols do not represent facility coordinates.

Generated output now uses same-origin external CSS, JavaScript, and runtime-data files behind a restrictive static CSP. The project includes owner-gated GitHub Pages Actions configuration, immutable official action references, privacy/security notes, a release/rollback runbook, accessibility notes, a maintainer checklist, a quality report, and a test report. The workflow is committed but does not change repository Pages settings; the owner must select GitHub Actions as the Pages source before deployment can occur.

### Implemented P2 safe scaffold

English is the only approved publishable interface locale. The locale overlay and access-evidence registries are intentionally empty. Schemas, builder checks, and validator gates reject unsupported public translation/access content. No verified access facts, Panjabi/Gurmukhi strings, correction destination, canonical URL, operational status, or new contact/clinical claim was added.

### Still requiring owner or qualified-reviewer action

A production Pages activation/review, canonical public URL, correction route, complete reviewed Panjabi locale, field-specific dated access evidence, verified service/contact claims, and human accessibility review remain intentionally open. This implementation does not represent those items as complete.
