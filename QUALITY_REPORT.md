# Quality Report

## Current checked state

The committed canonical dataset contains 112 source-derived records with a durable record ID, a legacy alias, source observation lineage, source hashes, source-text rule metadata, and explicit unknown/ambiguous states. The generated public runtime publishes no latitude/longitude fields. It represents 108 records as counts within 22 reported district groups and four as separate Punjab-wide/statewide coverage records.

The static build is reproducible from committed canonical inputs. Generated `public/` and `docs/` output are synchronized, apart from the intentional relative favicon reference in the Pages copy. The public shell uses external same-origin CSS, JavaScript, and runtime-data assets and a restrictive static CSP. The validator rejects an unsafe CSP exception, direct contact actions, HTML interpolation paths, persistent browser storage, geolocation, raw-upload dependencies in active sources, and unapproved locale/access content.

## Deliberate non-claims

The site does not verify that any listing is operating, licensed, reachable, eligible, affordable, accessible, clinically appropriate, or located at a precise coordinate. A map count is not a facility pin. Service terms and ownership labels are derived from supplied source text and are not independent findings.

## Release blockers that remain by design

No canonical production URL or correction route is configured. English is the only approved published interface language. The reviewed translation overlay and access-evidence registry are empty. The GitHub Actions workflow is committed but the repository owner must select GitHub Actions as the GitHub Pages publishing source and review the deployment environment before the public Pages deployment can occur.

## Review use

Use this report alongside [TEST_REPORT.md](TEST_REPORT.md), [MAINTAINER_CHECKLIST.md](MAINTAINER_CHECKLIST.md), and [PRIVACY_AND_SECURITY.md](PRIVACY_AND_SECURITY.md). A reviewer should reject a release if it weakens any of the current provenance, uncertainty, no-coordinate, or fail-closed content gates.
