# Script guide

## Active P0/P1/P2-safe path

- `import_legacy_source.py` — controlled import from an approved raw source into canonical data. The raw source is deliberately external to the repository.
- `build_p0.py` — builds the coordinate-free browser runtime and the modular same-origin `public/` assets from committed canonical data.
- `sync_github_pages.py` — mirrors `public/` into `docs/` with the required project-subpath favicon adjustment.
- `validate_p0.py` — deterministic lineage, public-safety, CSP, locale/access-gate, Pages, and static-JavaScript checks.

Use `make build`, `make test`, `make validate`, or `make check` from the repository root. Do not hand-edit generated `public/` or `docs/`.

## Retired historical helpers

- `prepare_updated_facilities.R`
- `restore_reference_design.py`
- `build_atlas_page.py`
- `refine_atlas_exports.py`
- `create_p0_template.py`

These files document earlier import/design/migration work. They are **not** called by the P0/P1 Makefile or normal build. Some intentionally retain former marker-language strings for historical reproducibility; they must not be used to regenerate the current public site.
