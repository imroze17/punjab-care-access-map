# Locale and Access-Evidence Governance

## Current publication state

English is the only approved public interface locale. `data/locales/en.v1.json` contains reviewed English interface messages. `data/reviewed/locale-overlays.v1.json` is intentionally empty, and the build validates that only English is published.

No Panjabi/Gurmukhi pack is included. Do not copy machine-generated or partial health-directory text into a public locale file. A non-English public release needs a complete reviewed overlay, a documented qualified reviewer, an owner approval record, and updated human accessibility review for the rendered locale.

## Translation overlay contract

The translation schema separates source-derived fields from reviewed display text. A translation must never overwrite source lineage, legacy IDs, durable IDs, unverified contact text, or source-derived evidence labels. It should identify the canonical record field, locale, reviewer/approval metadata, and the source version it was reviewed against.

When a source record changes, matching translated fields must be re-reviewed before publication. If an overlay is missing, stale, incomplete, or unapproved, the build must fail closed rather than fall back to a partial public translation.

## Access evidence contract

The site currently makes no verified claims about operating status, opening hours, fees, eligibility, disability access, transport, appointment requirements, or service availability. `data/reviewed/access-evidence.v1.json` is intentionally empty.

A future access field requires a field-specific evidence item with its record ID, the exact public assertion, evidence source, evidence date, reviewer/approval metadata, and expiry/review handling. A general directory entry or the original import alone is not enough evidence for a current access claim.

## Approval sequence

1. Obtain owner approval for the exact field or locale scope.
2. Collect field-specific dated evidence or a complete translated overlay from a qualified reviewer.
3. Add reviewed structured data without modifying the original source observation.
4. Extend the builder and validator so incomplete/stale material fails closed.
5. Re-run `make check`, perform human language/accessibility review, and document the release decision.
