#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPORTER = ROOT / "scripts/import_legacy_source.py"
HEADER = "Name,District,Address / Location,Type,Contact (if available),Remarks\n"


def legacy_entry(record_id: str, name: str, district: str, address: str, record_type: str, contact: str, remarks: str) -> dict:
    return {"id": record_id, "Name": name, "District": district, "Address": address, "Type": record_type, "Contact": contact, "Remarks": remarks, "category": "Government", "serviceGroup": "Legacy test"}


class ImporterTests(unittest.TestCase):
    def run_import(self, source: Path, legacy: Path, target: Path, crosswalk: Path | None = None, artifact_id: str | None = None, dataset_version: str | None = None) -> None:
        command = [sys.executable, str(IMPORTER), "--input", str(source), "--legacy", str(legacy), "--data-root", str(target)]
        if crosswalk:
            command.extend(["--crosswalk", str(crosswalk)])
        if artifact_id:
            command.extend(["--artifact-id", artifact_id])
        if dataset_version:
            command.extend(["--dataset-version", dataset_version])
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)

    def test_reuses_crosswalk_ids_when_rows_are_reordered(self) -> None:
        rows = [
            'Centre One,Test District,"Village A",Private,12345,First note',
            'Centre Two,Another District,"Village B",NGO / Trust,,Second note',
        ]
        legacy = [
            legacy_entry("F001", "Centre One", "Test District", "Village A", "Private", "12345", "First note"),
            legacy_entry("F002", "Centre Two", "Another District", "Village B", "NGO / Trust", "", "Second note"),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            legacy_path = root / "legacy.json"; legacy_path.write_text(json.dumps(legacy), encoding="utf-8")
            first_source = root / "first.txt"; first_source.write_text(HEADER + "\n".join(rows) + "\n", encoding="utf-8")
            first_data = root / "first-data"; self.run_import(first_source, legacy_path, first_data, artifact_id="source:test-first", dataset_version="pca-test-first-v1")
            crosswalk = first_data / "migrations/legacy-id-crosswalk.v1.json"
            first_records = json.loads((first_data / "canonical/punjab-care-records.v1.json").read_text())["records"]
            first_ids = {record["sourceObservations"][0]["parsedFields"]["name"]: record["recordId"] for record in first_records}

            second_source = root / "second.txt"; second_source.write_text(HEADER + "\n".join(reversed(rows)) + "\n", encoding="utf-8")
            second_data = root / "second-data"; self.run_import(second_source, legacy_path, second_data, crosswalk, artifact_id="source:test-second", dataset_version="pca-test-second-v1")
            second_records = json.loads((second_data / "canonical/punjab-care-records.v1.json").read_text())["records"]
            second_ids = {record["sourceObservations"][0]["parsedFields"]["name"]: record["recordId"] for record in second_records}
            self.assertEqual(first_ids, second_ids)
            manifest = json.loads((second_data / "manifests/source-artifact.v1.json").read_text())
            self.assertEqual(manifest["datasetVersion"], "pca-test-second-v1")
            self.assertEqual(manifest["sourceArtifact"]["sourceArtifactId"], "source:test-second")

    def test_rejects_missing_quoted_address_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.txt"; source.write_text(HEADER + "Centre,Test District,Not quoted,Private,,Note\n", encoding="utf-8")
            legacy = root / "legacy.json"; legacy.write_text("[]", encoding="utf-8")
            result = subprocess.run([sys.executable, str(IMPORTER), "--input", str(source), "--legacy", str(legacy), "--data-root", str(root / "data")], cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("expected quoted address anchor", result.stderr)


if __name__ == "__main__":
    unittest.main()
