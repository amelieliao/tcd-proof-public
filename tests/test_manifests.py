from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from tcd_verifier.manifest import verify_manifest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "manifest",
    [
        ROOT / "fixtures" / "verifier_v0_1" / "test-vector-manifest.json",
        ROOT / "fixtures" / "test-vector-bundle-manifest.json",
    ],
)
def test_fixture_manifests_verify(manifest: Path) -> None:
    report = verify_manifest(manifest)

    assert report["ok"] is True
    assert report["hash_mismatches"] == []
    assert report["omitted_files"] == []
    assert report["self_references"] == []


def _copy_manifest_tree(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    shutil.copytree(ROOT / "fixtures", root / "fixtures")
    shutil.copytree(ROOT / "schemas", root / "schemas")
    shutil.copytree(ROOT / "specs", root / "specs")
    (root / "pyproject.toml").write_text((ROOT / "pyproject.toml").read_text(encoding="utf-8"), encoding="utf-8")
    return root


def test_bundle_manifest_detects_fixture_tampering(tmp_path: Path) -> None:
    root = _copy_manifest_tree(tmp_path)
    receipt = root / "fixtures" / "verifier_v0_1" / "valid" / "receipt.json"
    data = json.loads(receipt.read_text(encoding="utf-8"))
    data["receipt_body"]["claims"]["decision_outcome"] = "tampered_after_manifest"
    receipt.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = verify_manifest(root / "fixtures" / "test-vector-bundle-manifest.json", root=root)

    assert report["ok"] is False
    assert any(item["path"] == "fixtures/verifier_v0_1/valid/receipt.json" for item in report["hash_mismatches"])


def test_bundle_manifest_detects_omitted_fixture(tmp_path: Path) -> None:
    root = _copy_manifest_tree(tmp_path)
    manifest_path = root / "fixtures" / "test-vector-bundle-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["entries"] = [
        entry
        for entry in manifest["entries"]
        if entry["path"] != "fixtures/verifier_v0_1/valid/receipt.json"
    ]
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = verify_manifest(manifest_path, root=root)

    assert report["ok"] is False
    assert "fixtures/verifier_v0_1/valid/receipt.json" in report["omitted_files"]


def test_manifest_self_reference_fails(tmp_path: Path) -> None:
    root = _copy_manifest_tree(tmp_path)
    manifest_path = root / "fixtures" / "test-vector-bundle-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["entries"].append(
        {
            "path": "fixtures/test-vector-bundle-manifest.json",
            "sha256": "0" * 64,
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = verify_manifest(manifest_path, root=root)

    assert report["ok"] is False
    assert report["self_references"] == ["fixtures/test-vector-bundle-manifest.json"]
