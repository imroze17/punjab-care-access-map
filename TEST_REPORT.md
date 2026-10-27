# Test Report

**Release scope:** P0 foundation and P1/P2-safe static implementation
**Recorded:** 2026-10-27
**Environment:** Sandbox static server, Chromium, Python, Node.js

## Executed checks

`make check` rebuilds `public/` and `docs/` from committed canonical inputs, runs importer regression tests, validates canonical lineage and generated output, and checks generated JavaScript syntax. The P1/P2 validator additionally confirms the 112 coordinate-free runtime records, 108 records across 22 district groups, four coverage-scope records, 23 district aliases, English-only publication, no reviewed access claims, a same-origin external asset shell, a restrictive CSP without an unsafe-inline exception, and Pages/public output parity.

The live browser check selected **Amritsar** through the native district selector. The page showed seven matching records, one district group, zero coverage records, an active district chip, and `?district=Amritsar` in the URL. Applying the OOAT source-term control reduced the result set to two records and added the source-term URL/chip state. Selecting a record displayed supplied address/contact text with unconfirmed/location caveats; changing the source-term filter closed the now-nonmatching selection with a status message.

The live CSV check exported the filtered two-record result and then the full directory. The full export contained 112 rows and the expected public fields: entry/legacy IDs, source district, source terms, coverage scope, map representation, dataset version, and export notice. Every formula-like value was escaped before export. Live PNG and PDF map export buttons produced a 2080×1700 PNG and a valid one-page PDF 1.4 file.

Desktop and narrow-viewport captures confirmed the repaired two-column desktop directory/map layout and the narrow default List/optional Map control. The map retains district-group count symbols and the persistent statement that it does not show facility locations.

A valid record ID combined with an incompatible Rupnagar district filter was opened through a direct URL. The runtime cleared the incompatible selection before rendering, retained the two matching Rupnagar records, and announced that the selected listing no longer matched the active filters. A headless print-to-PDF check of the filtered directory confirmed the print-only context includes the active district filter, dataset version, source-derived-directory statement, no-facility-location statement, and current-operation/service caveat.

## Phase 1 UI/UX redesign — verified 2026-10-27

**Scope:** design tokens, typography scale, contrast remediation. No layout,
taxonomy, microcopy or export changes (Phases 2–4).

All measurements below come from a live Chromium session driven over CDP against
the built `public/` output, reading `getComputedStyle` from the rendered DOM.
Contrast ratios were computed from rendered foreground/effective-background pairs
using the WCAG relative-luminance formula.

### Automated

`make check` passes: build, 2 importer regression tests, and `validate_p0.py`
including four new Phase 1 guards (token layer ordering, pinned token values,
a 14px interface-text floor, opaque legend/map-note surfaces). Each new guard was
verified to **fail** when deliberately violated, not merely to pass:

- injecting `font-size:.71rem` → `validation failed: interface text below the 0.875rem (14px) floor: .71rem`
- altering `--color-text-secondary` → `validation failed: token --color-text-secondary is '#8a9690', expected '#59645f'`

### Typography

29 interface text styles probed. **0 render below 14px** (previously 17 of 17
probed styles were below 14px). Smallest rendered interface text is 14px. The
service name `.facility-name` moved from 12.64px to 18px.

### Contrast

29 of 29 probed styles meet WCAG AA for their rendered size and weight. The five
previously failing pairs (`.metric span` 3.81:1, `.map-export span` 3.85:1,
`.section-label` 3.94:1, `.footer-note` 4.09:1, `.legend-title` 4.15:1) now
measure 5.60–15.57:1. Lowest passing ratio is 5.51:1. Full table in
[design/CONTRAST_TABLE.md](design/CONTRAST_TABLE.md).

### Keyboard focus

16 controls traversed with real dispatched `Tab` key events; 147 focusable
elements then individually checked. **Every element matching `:focus-visible`
renders a visible indicator.** An initial reading showed `.filter-button` with a
0px outline; this was traced to `transition: .15s ease` defaulting to
`transition-property: all`, which animated the outline in — the ring reaches the
full 3px plus halo after settling. Transitions are now scoped to colour and
shadow properties. This was a measurement artifact, not a shipped defect.

### Responsive

No horizontal overflow at 320, 390, 600, 768, 820, 900, 1100, 1280 or 1440px.
A regression introduced during this phase (`flex-shrink:0` on `.metric-row`
causing 109px of overflow at 768px) was found by that sweep and fixed before
commit. Mobile still defaults to the list view with the map panel hidden.

### Interaction regression check

112 cards render; 23 district paths and 22 district-group markers draw. District
filter returns 6 records for Bathinda and emits the expected filter chip; search
input, clear, and card selection all behave as before the restyle.

### Defect found and fixed in existing code

`src/p1-runtime.js:567` inserted the "Source terms mentioned" label before the
*role* select rather than before its own select, rendering two stacked labels
followed by two selects. Present and byte-identical in commit `1b6bba8`, so
pre-existing; the larger Phase 1 label type made it visible. Now reads
label → select → label → select.

### Not covered

Hover/pressed/disabled states beyond those listed, SVG map geometry contrast,
export PNG/PDF raster output, print rendering, assistive-technology testing,
touch-device testing, forced-colors mode, and 200% zoom reflow. Map district
labels are overlapped by district-group count markers at the default extent —
a pre-existing issue deferred to Phase 2 (§12.4). The two-column split remains
cramped between 721–900px; collapsing it earlier is a Phase 2 decision (§6.2).
No WCAG certification is claimed.

## Required human review before public accessibility or service claims


The following are not represented as completed certification or verification: keyboard testing with assistive technology, desktop/mobile screen-reader testing, touch-device testing, forced-colors/high-contrast testing, 200% zoom/reflow review, print review on target browsers, review of a future Panjabi locale, service-operation verification, contact verification, access verification, and production GitHub Pages deployment verification.

## Release decision guidance

This report supports a code/data release review. It does not authorize a production Pages claim. A repository owner must enable GitHub Actions as the Pages source and review the deployment workflow before a production URL is considered live. See [RELEASE_RUNBOOK.md](RELEASE_RUNBOOK.md).
