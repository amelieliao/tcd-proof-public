"""CLI for public TCD verifier and reconciliation commands."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .manifest import verify_manifest
from .reconcile import reconcile_files
from .verify import verify_files


def _print_report(report: dict, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    if report.get("ok") is True or report.get("complete") is True:
        print("OK")
    else:
        code = report.get("failure_code") or "RECONCILIATION_INCOMPLETE"
        message = report.get("message") or "reconciliation incomplete"
        print(f"FAIL {code}: {message}")
        if report.get("missing"):
            ids = ", ".join(str(x.get("upstream_action_id")) for x in report["missing"])
            print(f"missing upstream_action_id: {ids}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tcd_verifier")
    sub = parser.add_subparsers(dest="command", required=True)

    verify = sub.add_parser("verify", help="Verify a TCD Receipt Profile v0.1 fixture")
    verify.add_argument("--receipt", type=Path, required=True)
    verify.add_argument("--public-key", type=Path, required=True)
    verify.add_argument("--expected", type=Path, required=True)
    verify.add_argument("--json", action="store_true", dest="json_output")

    reconcile = sub.add_parser("reconcile", help="Reconcile upstream actions against receipt coverage")
    reconcile.add_argument("--eligible-actions", type=Path, required=True)
    reconcile.add_argument("--receipt-index", type=Path, required=True)
    reconcile.add_argument("--verification-results", type=Path, required=True)
    reconcile.add_argument("--json", action="store_true", dest="json_output")

    manifest = sub.add_parser("manifest-check", help="Verify a public fixture hash manifest")
    manifest.add_argument("--manifest", type=Path, required=True)
    manifest.add_argument("--json", action="store_true", dest="json_output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "verify":
        report = verify_files(args.receipt, args.public_key, args.expected).to_dict()
        _print_report(report, as_json=args.json_output)
        return 0 if report["ok"] else 1
    if args.command == "reconcile":
        report = reconcile_files(args.eligible_actions, args.receipt_index, args.verification_results)
        _print_report(report, as_json=args.json_output)
        return 0 if report["complete"] else 1
    if args.command == "manifest-check":
        report = verify_manifest(args.manifest)
        _print_report(report, as_json=args.json_output)
        return 0 if report["ok"] else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
