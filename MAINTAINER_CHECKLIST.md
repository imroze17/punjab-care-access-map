# Maintainer Checklist

## Before changing source-derived records

- Confirm that the proposed source is approved for public directory use.
- Run `make refresh-data` with an explicit `SOURCE`, `ARTIFACT_ID`, and `DATASET_VERSION` only after a reviewer has approved the change.
- Inspect the source-artifact manifest, crosswalk, parser warnings, and duplicate-candidate report. Never merge or delete similar records as an import side effect.
- Preserve unknown, mixed, and unverified states. Do not infer current availability, ownership, clinical suitability, location coordinates, hours, fees, eligibility, disability access, or service quality.
- Run `make check` and inspect the generated `public/` and `docs/` differences before committing.

## Before changing interface or map behaviour

- Keep the list usable without the SVG map. The native district selector must remain the complete district-browsing route.
- Keep district counts and coverage scope distinct from individual facility locations. Do not add point coordinates without verified evidence and an approved representation decision.
- Keep the cultural-region wash, rivers, and labels optional. They are wayfinding aids, not administrative or clinical evidence.
- Do not add stateful browsing storage, tracking, geolocation, third-party map tiles, web fonts, or a backend without an owner-reviewed privacy and deployment decision.
- Check keyboard focus, narrow-screen List/Map controls, print output, no-results state, active-filter chips, and map/export caveats.

## Before publishing new public content

- Do not add a correction destination or canonical site URL until the owner approves the exact public value and response process.
- Do not publish a new language pack unless a qualified reviewer has supplied a complete overlay and approval metadata. Do not publish partial translation.
- Do not add access/eligibility/status/contact assertions without field-specific, dated evidence in the reviewed evidence pipeline.
- Keep raw source files and private review material out of Git.
- Review [PRIVACY_AND_SECURITY.md](PRIVACY_AND_SECURITY.md), [ACCESSIBILITY_NOTES.md](ACCESSIBILITY_NOTES.md), and [TEST_REPORT.md](TEST_REPORT.md).

## Before a production Pages release

- Run `make check`, `git diff --check`, and the manual checks listed in [TEST_REPORT.md](TEST_REPORT.md).
- Confirm the working tree contains regenerated `public/` and `docs/` output and no raw upload.
- Confirm the GitHub Actions workflow succeeded on the exact `main` commit.
- Follow [RELEASE_RUNBOOK.md](RELEASE_RUNBOOK.md). Do not call a production Pages URL live until the owner enabled the GitHub Actions Pages source and the deployment job reports success.
