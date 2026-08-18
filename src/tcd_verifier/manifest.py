"""Hash-manifest verification for public synthetic fixtures."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .errors import FailureCode
from .jsonio import StrictJsonError, strict_json_load


def _failure(code: FailureCode, message: str, **details: Any) -> dict[str, Any]:
    return {
        "ok": False,
        "failure_code": code.value,
        "message": message,
        "details": details,
    }


def _repo_root(manifest_path: Path) -> Path:
    cur = manifest_path.resolve().parent
    for parent in [cur, *cur.parents]:
        if (parent / "pyproject.toml").exists() and (parent / "fixtures").exists():
            return parent
    return Path.cwd().resolve()


def _safe_entry_path(root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def _expected_coverage(root: Path, manifest_path: Path) -> set[str]:
    rel_manifest = manifest_path.resolve().relative_to(root.resolve()).as_posix()
    if rel_manifest == "fixtures/verifier_v0_1/test-vector-manifest.json":
        base = root / "fixtures" / "verifier_v0_1"
        return {
            path.relative_to(root).as_posix()
            for path in base.rglob("*")
            if path.is_file() and path.resolve() != manifest_path.resolve()
        }
    if rel_manifest == "fixtures/test-vector-bundle-manifest.json":
        expected = {
            path.relative_to(root).as_posix()
            for base in [root / "fixtures" / "verifier_v0_1", root / "fixtures" / "reconciliation"]
            for path in base.rglob("*")
            if path.is_file()
        }
        for path in [
            root / "schemas" / "tcd-receipt-profile-v0.1.schema.json",
            root / "specs" / "tcd-receipt-profile-v0.1.md",
        ]:
            expected.add(path.relative_to(root).as_posix())
        expected.discard(rel_manifest)
        return expected
    return set()


def verify_manifest(manifest_path: Path, *, root: Path | None = None) -> dict[str, Any]:
    try:
        manifest = strict_json_load(manifest_path)
    except StrictJsonError as exc:
        return _failure(exc.code, exc.message)
    except OSError as exc:
        return _failure(FailureCode.INVALID_JSON, "manifest is missing or unreadable", error=str(exc))
    if not isinstance(manifest, dict):
        return _failure(FailureCode.SCHEMA_INVALID, "manifest must be a JSON object")
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        return _failure(FailureCode.SCHEMA_INVALID, "manifest entries must be a list")

    root = (root or _repo_root(manifest_path)).resolve()
    manifest_rel = manifest_path.resolve().relative_to(root).as_posix()
    seen: set[str] = set()
    duplicate_entries: list[str] = []
    invalid_entries: list[dict[str, Any]] = []
    missing_files: list[str] = []
    hash_mismatches: list[dict[str, str]] = []
    self_references: list[str] = []
    covered: set[str] = set()

    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            invalid_entries.append({"index": idx, "reason": "entry_must_be_object"})
            continue
        rel = entry.get("path")
        sha = entry.get("sha256")
        path = _safe_entry_path(root, rel)
        if path is None or not isinstance(sha, str) or len(sha) != 64 or any(ch not in "0123456789abcdef" for ch in sha):
            invalid_entries.append({"index": idx, "path": rel, "reason": "invalid_path_or_sha256"})
            continue
        rel_str = path.relative_to(root).as_posix()
        if rel_str in seen:
            duplicate_entries.append(rel_str)
        seen.add(rel_str)
        if rel_str == manifest_rel:
            self_references.append(rel_str)
            continue
        if not path.exists() or not path.is_file():
            missing_files.append(rel_str)
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != sha:
            hash_mismatches.append({"path": rel_str, "expected": sha, "actual": actual})
        covered.add(rel_str)

    expected = _expected_coverage(root, manifest_path)
    omitted_files = sorted(expected - covered)
    orphan_entries = sorted(covered - expected) if expected else []

    ok = not any([invalid_entries, duplicate_entries, missing_files, hash_mismatches, self_references, omitted_files, orphan_entries])
    return {
        "ok": ok,
        "failure_code": None if ok else FailureCode.SCHEMA_INVALID.value,
        "message": "manifest verified" if ok else "manifest verification failed",
        "entries_checked": len(covered),
        "invalid_entries": invalid_entries,
        "duplicate_entries": duplicate_entries,
        "missing_files": missing_files,
        "hash_mismatches": hash_mismatches,
        "self_references": self_references,
        "omitted_files": omitted_files,
        "orphan_entries": orphan_entries,
    }
