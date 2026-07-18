#!/usr/bin/env python3
"""Check the AML/KYB public demo acceptance gate."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


DEMO_REL = Path("demos/aml_kyb_alert_review")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def all_json_parse(root: Path) -> bool:
    for path in root.rglob("*.json"):
        load_json(path)
    return True


def markdown_links_ok(public_root: Path) -> bool:
    import re

    for path in public_root.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = match.group(1).split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            if not (path.parent / target).resolve().exists():
                raise AssertionError(f"missing markdown link: {path}: {target}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-root", type=Path, default=Path.cwd())
    parser.add_argument("--private-status-before", type=Path, default=None)
    parser.add_argument("--private-status-after", type=Path, default=None)
    args = parser.parse_args()
    public_root = args.public_root.resolve()
    demo_root = public_root / DEMO_REL
    run = demo_root / "run_derived"
    failures: list[str] = []

    def check(name: str, cond: bool) -> None:
        if not cond:
            failures.append(name)

    if args.private_status_before and args.private_status_after:
        check("private repo final status equals private repo initial status", args.private_status_before.read_bytes() == args.private_status_after.read_bytes())

    manifest = load_json(demo_root / "scenarios" / "scenario_manifest.json")
    scenario_count = len(manifest.get("scenarios", []))
    summary = load_json(run / "pilot_summary.redacted.json")["artifact"]
    action_matrix = load_json(run / "action_matrix.redacted.json")["artifact"]
    verification_matrix = load_json(run / "verification_matrix.redacted.json")["artifact"]
    wrong = load_json(run / "wrong_binding_failures.redacted.json")["artifact"]
    restart = load_json(run / "restart_safe_verification.redacted.json")["artifact"]

    check("synthetic AML/KYB scenario schema validated", scenario_count >= 1)
    check("at least one actual scenario executed", len(action_matrix.get("actions", [])) >= 1)
    check("at least one actual receipt issued", bool(summary.get("at_least_one_receipt_issued")))
    check("at least one actual verification succeeded", bool(summary.get("at_least_one_verification_ok")))
    check(
        "actual policy binding verified",
        any(v.get("verification", {}).get("policy_binding_verified") is True for v in verification_matrix.get("verifications", [])),
    )
    check(
        "at least one actual wrong-binding verification failed",
        any(v.get("ok") is False for v in wrong.get("negative_verifications", [])),
    )
    check("actual process restart completed", bool(restart.get("process_restart_completed")))
    check("receipt_ref verified after restart", bool(restart.get("verified_after_restart")) and restart.get("verify_input_source") == "receipt_ref_lookup")
    for path in run.glob("*.json"):
        md = load_json(path).get("artifact_metadata", {})
        check(f"{path.name} provenance-labeled", md.get("runtime_generated") is True and md.get("synthetic_data") is True)
    check("all JSON parses", all_json_parse(demo_root))
    check("Markdown links pass", markdown_links_ok(public_root))
    validator = demo_root / "tools" / "validate_public_export.py"
    result = subprocess.run([sys.executable, str(validator), "--demo-root", str(demo_root)], text=True, capture_output=True)
    if result.returncode != 0:
        failures.append("public export validator passes")
        print(result.stdout)
        print(result.stderr)

    if failures:
        print(json.dumps({"ok": False, "failures": failures}, indent=2, sort_keys=True))
        return 1
    print(json.dumps({"ok": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
