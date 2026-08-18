from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "fixtures" / "reconciliation"


def _env() -> dict[str, str]:
    env = os.environ.copy()
    src = str(ROOT / "src")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src if not existing else src + os.pathsep + existing
    return env


def _run_reconcile(case: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    case_dir = FIXTURE_ROOT / case
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tcd_verifier",
            "reconcile",
            "--eligible-actions",
            str(case_dir / "eligible-actions.json"),
            "--receipt-index",
            str(case_dir / "receipt-index.json"),
            "--verification-results",
            str(case_dir / "verification-results.json"),
            "--json",
        ],
        cwd=ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        check=False,
    )
    return result, json.loads(result.stdout)


def _run_reconcile_paths(eligible_actions: Path, receipt_index: Path, verification_results: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tcd_verifier",
            "reconcile",
            "--eligible-actions",
            str(eligible_actions),
            "--receipt-index",
            str(receipt_index),
            "--verification-results",
            str(verification_results),
            "--json",
        ],
        cwd=ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        check=False,
    )
    return result, json.loads(result.stdout)


def _load_complete() -> tuple[dict, dict, dict]:
    case_dir = FIXTURE_ROOT / "complete"
    return (
        json.loads((case_dir / "eligible-actions.json").read_text(encoding="utf-8")),
        json.loads((case_dir / "receipt-index.json").read_text(encoding="utf-8")),
        json.loads((case_dir / "verification-results.json").read_text(encoding="utf-8")),
    )


def _write_inputs(tmp_path: Path, eligible: dict, receipts: dict, results: dict) -> tuple[Path, Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    eligible_path = tmp_path / "eligible-actions.json"
    receipts_path = tmp_path / "receipt-index.json"
    results_path = tmp_path / "verification-results.json"
    eligible_path.write_text(json.dumps(eligible, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipts_path.write_text(json.dumps(receipts, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    results_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return eligible_path, receipts_path, results_path


def test_complete_reconciliation_succeeds() -> None:
    result, report = _run_reconcile("complete")

    assert result.returncode == 0, result.stderr
    assert report["upstream_eligible_actions"] == 3
    assert report["receipts_committed"] == 3
    assert report["missing"] == []
    assert report["complete"] is True


def test_missing_receipt_reconciliation_fails_with_action_id() -> None:
    result, report = _run_reconcile("missing-receipt")

    assert result.returncode != 0
    assert report["upstream_eligible_actions"] == 3
    assert report["receipts_committed"] == 2
    assert report["complete"] is False
    assert [item["upstream_action_id"] for item in report["missing"]] == ["upstream-action-003"]


@pytest.mark.parametrize(
    ("case", "field"),
    [
        ("duplicate-receipt", "duplicates"),
        ("orphan-receipt", "orphan_receipts"),
        ("verification-failure", "verification_failures"),
        ("uncommitted-receipt", "uncommitted_receipts"),
    ],
)
def test_incomplete_reconciliation_cases_fail(case: str, field: str) -> None:
    result, report = _run_reconcile(case)

    assert result.returncode != 0
    assert report["complete"] is False
    assert report[field]


@pytest.mark.parametrize(
    ("mutator", "field"),
    [
        (lambda eligible, receipts, results: eligible["actions"].append(dict(eligible["actions"][0])), "duplicates"),
        (lambda eligible, receipts, results: eligible["actions"][1].update({"scenario_id": eligible["actions"][0]["scenario_id"]}), "duplicates"),
        (lambda eligible, receipts, results: receipts["receipts"][1].update({"receipt_ref": receipts["receipts"][0]["receipt_ref"]}), "duplicates"),
        (lambda eligible, receipts, results: receipts["receipts"].append({**receipts["receipts"][0], "receipt_ref": "receipt:synthetic:reconcile:001-extra"}), "duplicates"),
        (lambda eligible, receipts, results: receipts["receipts"][0].update({"issued": False, "committed": True}), "unissued_receipts"),
        (lambda eligible, receipts, results: receipts["receipts"][0].pop("issued"), "unissued_receipts"),
        (lambda eligible, receipts, results: receipts["receipts"][0].update({"issued": "true"}), "unissued_receipts"),
        (lambda eligible, receipts, results: results["results"].pop(0), "missing_verification_results"),
        (lambda eligible, receipts, results: results["results"].append(dict(results["results"][0])), "duplicate_verification_results"),
        (lambda eligible, receipts, results: results["results"].append({"receipt_ref": "receipt:synthetic:orphan-result", "ok": True}), "orphan_verification_results"),
    ],
)
def test_strict_reconciliation_incomplete_cases_fail(tmp_path: Path, mutator, field: str) -> None:
    eligible, receipts, results = _load_complete()
    mutator(eligible, receipts, results)
    paths = _write_inputs(tmp_path, eligible, receipts, results)

    result, report = _run_reconcile_paths(*paths)

    assert result.returncode != 0
    assert report["complete"] is False
    assert report[field]


@pytest.mark.parametrize(
    ("filename", "content", "failure_code"),
    [
        ("eligible-actions.json", '{"actions":[],"actions":[]}', "DUPLICATE_JSON_KEY"),
        ("eligible-actions.json", '{"actions": NaN}', "NON_FINITE_JSON_NUMBER"),
        ("eligible-actions.json", '{"actions": Infinity}', "NON_FINITE_JSON_NUMBER"),
        ("eligible-actions.json", '{"actions": -Infinity}', "NON_FINITE_JSON_NUMBER"),
    ],
)
def test_reconciliation_strict_json_failures(tmp_path: Path, filename: str, content: str, failure_code: str) -> None:
    eligible, receipts, results = _load_complete()
    paths = _write_inputs(tmp_path, eligible, receipts, results)
    (tmp_path / filename).write_text(content, encoding="utf-8")

    result, report = _run_reconcile_paths(*paths)

    assert result.returncode != 0
    assert report["failure_code"] == failure_code
