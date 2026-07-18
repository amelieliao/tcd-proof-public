#!/usr/bin/env python3
"""Validate that AML/KYB public export files are parseable and public-safe."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


FORBIDDEN_EXTENSIONS = {
    ".sqlite",
    ".sqlite3",
    ".sqlite-wal",
    ".sqlite-shm",
    ".db",
    ".db-wal",
    ".db-shm",
    ".log",
    ".pid",
    ".pem",
    ".key",
}
FORBIDDEN_FILENAMES = {"env.sh", ".env"}
PATH_PATTERNS = [
    re.compile(r"/Users/[A-Za-z0-9._/-]+"),
    re.compile(r"/home/[A-Za-z0-9._/-]+"),
    re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\s)]+"),
]
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]{20,}\b", re.I),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bASIA[0-9A-Z]{16}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
    re.compile(r"\bghp_[0-9A-Za-z_]{20,}\b"),
    re.compile(r"\bgithub_pat_[0-9A-Za-z_]+\b"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    re.compile(r"\b(?:\+?1[-. ]?)?\(?[2-9]\d{2}\)?[-. ]?\d{3}[-. ]?\d{4}\b"),
]
FORBIDDEN_TERMS = [
    "raw prompt",
    "raw completion",
    "raw document",
    "raw request body",
    "raw response body",
    "authorization header",
    "auth token",
    "bearer token",
    "api key",
    "private key",
    "signing secret",
    "hmac secret",
    "kms credentials",
    "hsm credentials",
    "env.sh",
    "outbox db",
    "unredacted private policy",
    "private source code",
    "private stack trace",
    "private repo filesystem inventory",
]
NEGATIVE_CONTEXT = [
    "no ",
    "not ",
    "without ",
    "avoid",
    "avoids",
    "exclude",
    "excludes",
    "excluded",
    "does not",
    "do not",
    "not claim",
    "forbid",
    "forbidden",
    "omitted",
    "redacted",
    "not included",
    "must not",
]
SENSITIVE_KEY_PARTS = [
    "auth_token",
    "bearer_token",
    "authorization",
    "cookie",
    "api_key",
    "apikey",
    "private_key",
    "hmac_key",
    "hmac_secret",
    "signing_secret",
    "access_token",
    "secret_token",
    "session_token",
    "raw_customer_data",
    "raw_prompt",
    "raw_completion",
    "raw_document",
    "raw_request_body",
    "raw_response_body",
    "password",
]


def is_negative_context(line: str) -> bool:
    low = line.lower()
    return any(marker in low for marker in NEGATIVE_CONTEXT)


def fail(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path}: {message}")


def inspect_text(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    for pat in PATH_PATTERNS + SECRET_PATTERNS:
        if pat.search(text):
            fail(errors, path, f"forbidden pattern: {pat.pattern}")
    if path.suffix.lower() != ".md":
        return
    for idx, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for term in FORBIDDEN_TERMS:
            if term in low and not is_negative_context(line):
                fail(errors, path, f"forbidden term outside safety boundary at line {idx}: {term}")


def inspect_json_value(path: Path, obj: Any, errors: list[str], key_path: str = "") -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            low_key = str(key).lower()
            child = f"{key_path}.{key}" if key_path else str(key)
            if any(part in low_key for part in SENSITIVE_KEY_PARTS):
                if value not in (False, None, "", "redacted", "omitted", "not_included", "omitted_or_redacted"):
                    if not (isinstance(value, str) and ("redacted" in value.lower() or "not_included" in value.lower())):
                        fail(errors, path, f"secret-like JSON key has non-redacted value: {child}")
            inspect_json_value(path, value, errors, child)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            inspect_json_value(path, value, errors, f"{key_path}[{i}]")


def inspect_json_contracts(demo_root: Path, errors: list[str]) -> None:
    run_dir = demo_root / "run_derived"
    for path in run_dir.glob("*.json"):
        obj = json.loads(path.read_text(encoding="utf-8"))
        md = obj.get("artifact_metadata") if isinstance(obj, dict) else None
        if not isinstance(md, dict) or md.get("runtime_generated") is not True:
            fail(errors, path, "run-derived JSON missing artifact_metadata.runtime_generated=true")
        if "<redacted-demo-" in path.read_text(encoding="utf-8"):
            fail(errors, path, "run-derived JSON contains old illustrative placeholder")
    illustrative = demo_root / "illustrative_manifest.json"
    if illustrative.exists():
        obj = json.loads(illustrative.read_text(encoding="utf-8"))
        if obj.get("runtime_generated") is not False:
            fail(errors, illustrative, "illustrative manifest must have runtime_generated=false")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    demo_root = args.demo_root.resolve()
    errors: list[str] = []
    for path in sorted(demo_root.rglob("*")):
        if path.is_dir():
            continue
        if path.name in FORBIDDEN_FILENAMES or path.suffix.lower() in FORBIDDEN_EXTENSIONS:
            fail(errors, path, "forbidden file type in public demo export")
            continue
        if path.suffix.lower() in {".json", ".md", ".py", ".txt"}:
            inspect_text(path, errors)
        if path.suffix.lower() == ".json":
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                fail(errors, path, f"invalid JSON: {exc}")
                continue
            inspect_json_value(path, obj, errors)
    inspect_json_contracts(demo_root, errors)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(json.dumps({"ok": True, "demo_root": str(demo_root)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
