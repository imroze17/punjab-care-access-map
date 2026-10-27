.PHONY: build test validate check refresh-data serve

build:
	python3 scripts/build_p0.py --out-dir public
	python3 scripts/sync_github_pages.py --source public --target docs

test:
	python3 -m unittest discover -s tests -v

validate:
	python3 scripts/validate_p0.py

check: build test validate

# Example: make refresh-data SOURCE=/absolute/path/to/approved-source.txt ARTIFACT_ID=source:agency-2026-11 DATASET_VERSION=pca-2026-11-v1
# The committed crosswalk preserves record IDs for unchanged parsed observations.
refresh-data:
	@test -n "$(SOURCE)" && test -n "$(ARTIFACT_ID)" && test -n "$(DATASET_VERSION)" || (echo "Usage: make refresh-data SOURCE=/absolute/path/to/approved-source.txt ARTIFACT_ID=source:approved-artifact DATASET_VERSION=pca-YYYY-MM-vN"; exit 2)
	python3 scripts/import_legacy_source.py --input "$(SOURCE)" --legacy data/facilities.updated.json --crosswalk data/migrations/legacy-id-crosswalk.v1.json --artifact-id "$(ARTIFACT_ID)" --dataset-version "$(DATASET_VERSION)" --data-root data
	$(MAKE) check

serve: build
	python3 -m http.server 3000 --directory public --bind 0.0.0.0
