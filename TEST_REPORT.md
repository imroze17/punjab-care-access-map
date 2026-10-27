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

## Required human review before public accessibility or service claims

The following are not represented as completed certification or verification: keyboard testing with assistive technology, desktop/mobile screen-reader testing, touch-device testing, forced-colors/high-contrast testing, 200% zoom/reflow review, print review on target browsers, review of a future Panjabi locale, service-operation verification, contact verification, access verification, and production GitHub Pages deployment verification.

## Release decision guidance

This report supports a code/data release review. It does not authorize a production Pages claim. A repository owner must enable GitHub Actions as the Pages source and review the deployment workflow before a production URL is considered live. See [RELEASE_RUNBOOK.md](RELEASE_RUNBOOK.md).
