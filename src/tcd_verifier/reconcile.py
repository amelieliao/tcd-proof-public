"""Completeness reconciliation for public synthetic TCD fixtures."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .errors import FailureCode
from .jsonio import StrictJsonError, strict_json_load


ID_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.:-")


def _valid_id(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and all(ch in ID_CHARS for ch in value)


def _incomplete(message: str, **extra: Any) -> dict[str, Any]:
    report: dict[str, Any] = {
        "ok": False,
        "failure_code": FailureCode.RECONCILIATION_INCOMPLETE.value,
        "message": message,
        "upstream_eligible_actions": 0,
        "received_by_tcd": 0,
        "receipts_issued": 0,
        "receipts_committed": 0,
        "missing": [],
        "duplicates": [],
        "orphan_receipts": [],
        "verification_failures": [],
        "human_overrides": [],
        "unissued_receipts": [],
        "uncommitted_receipts": [],
        "missing_verification_results": [],
        "duplicate_verification_results": [],
        "orphan_verification_results": [],
        "input_errors": [],
        "complete": False,
    }
    report.update(extra)
    return report


def _strict_json_failure(exc: StrictJsonError) -> dict[str, Any]:
    return _incomplete(exc.message, failure_code=exc.code.value)


def _require_list(obj: dict[str, Any], field: str) -> list[Any] | None:
    value = obj.get(field)
    return value if isinstance(value, list) else None


def reconcile(eligible_actions: dict[str, Any], receipt_index: dict[str, Any], verification_results: dict[str, Any]) -> dict[str, Any]:
    raw_actions = _require_list(eligible_actions, "actions")
    raw_receipts = _require_list(receipt_index, "receipts")
    raw_results = _require_list(verification_results, "results")
    input_errors: list[dict[str, Any]] = []
    if raw_actions is None:
        input_errors.append({"input": "eligible_actions", "reason": "actions_must_be_list"})
        raw_actions = []
    if raw_receipts is None:
        input_errors.append({"input": "receipt_index", "reason": "receipts_must_be_list"})
        raw_receipts = []
    if raw_results is None:
        input_errors.append({"input": "verification_results", "reason": "results_must_be_list"})
        raw_results = []

    eligible: list[dict[str, Any]] = []
    for idx, action in enumerate(raw_actions):
        if not isinstance(action, dict):
            input_errors.append({"input": "eligible_actions", "index": idx, "reason": "action_must_be_object"})
            continue
        if action.get("eligible", True) is not True:
            continue
        action_id = action.get("upstream_action_id")
        scenario_id = action.get("scenario_id")
        if not _valid_id(action_id):
            input_errors.append({"input": "eligible_actions", "index": idx, "field": "upstream_action_id", "reason": "missing_or_invalid_id"})
            continue
        if not _valid_id(scenario_id):
            input_errors.append({"input": "eligible_actions", "index": idx, "field": "scenario_id", "reason": "missing_or_invalid_id"})
            continue
        eligible.append(action)

    eligible_action_ids = [str(a["upstream_action_id"]) for a in eligible]
    eligible_scenario_ids = [str(a["scenario_id"]) for a in eligible]
    eligible_id_set = set(eligible_action_ids)

    duplicates: list[dict[str, Any]] = []
    for action_id, count in sorted(Counter(eligible_action_ids).items()):
        if count > 1:
            duplicates.append({"kind": "eligible_upstream_action_id", "upstream_action_id": action_id, "count": count})
    for scenario_id, count in sorted(Counter(eligible_scenario_ids).items()):
        if count > 1:
            duplicates.append({"kind": "eligible_scenario_id", "scenario_id": scenario_id, "count": count})

    receipts: list[dict[str, Any]] = []
    for idx, receipt in enumerate(raw_receipts):
        if not isinstance(receipt, dict):
            input_errors.append({"input": "receipt_index", "index": idx, "reason": "receipt_must_be_object"})
            continue
        action_id = receipt.get("upstream_action_id")
        scenario_id = receipt.get("scenario_id")
        receipt_ref = receipt.get("receipt_ref")
        if not _valid_id(action_id):
            input_errors.append({"input": "receipt_index", "index": idx, "field": "upstream_action_id", "reason": "missing_or_invalid_id"})
            continue
        if not _valid_id(scenario_id):
            input_errors.append({"input": "receipt_index", "index": idx, "field": "scenario_id", "reason": "missing_or_invalid_id"})
            continue
        if not _valid_id(receipt_ref):
            input_errors.append({"input": "receipt_index", "index": idx, "field": "receipt_ref", "reason": "missing_or_invalid_id"})
            continue
        receipts.append(receipt)

    receipt_refs = [str(r["receipt_ref"]) for r in receipts]
    for receipt_ref, count in sorted(Counter(receipt_refs).items()):
        if count > 1:
            duplicates.append({"kind": "receipt_ref", "receipt_ref": receipt_ref, "count": count})

    receipt_action_ids = [str(r["upstream_action_id"]) for r in receipts]
    for action_id, count in sorted(Counter(receipt_action_ids).items()):
        if action_id in eligible_id_set and count > 1:
            duplicates.append({"kind": "action_receipt_mapping", "upstream_action_id": action_id, "count": count})

    by_action: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for receipt in receipts:
        by_action[str(receipt["upstream_action_id"])].append(receipt)

    orphan_receipts = [
        {"upstream_action_id": r.get("upstream_action_id"), "receipt_ref": r.get("receipt_ref")}
        for r in receipts
        if str(r.get("upstream_action_id")) not in eligible_id_set
    ]

    result_rows: list[dict[str, Any]] = []
    for idx, result in enumerate(raw_results):
        if not isinstance(result, dict):
            input_errors.append({"input": "verification_results", "index": idx, "reason": "result_must_be_object"})
            continue
        receipt_ref = result.get("receipt_ref")
        if not _valid_id(receipt_ref):
            input_errors.append({"input": "verification_results", "index": idx, "field": "receipt_ref", "reason": "missing_or_invalid_id"})
            continue
        if "ok" not in result or not isinstance(result.get("ok"), bool):
            input_errors.append({"input": "verification_results", "index": idx, "field": "ok", "reason": "ok_must_be_boolean"})
            continue
        result_rows.append(result)

    result_refs = [str(r["receipt_ref"]) for r in result_rows]
    duplicate_verification_results = [
        {"receipt_ref": receipt_ref, "count": count}
        for receipt_ref, count in sorted(Counter(result_refs).items())
        if count > 1
    ]
    receipt_ref_set = set(receipt_refs)
    orphan_verification_results = [
        {"receipt_ref": r.get("receipt_ref")}
        for r in result_rows
        if str(r.get("receipt_ref")) not in receipt_ref_set
    ]
    results_by_ref: dict[str, dict[str, Any]] = {}
    for result in result_rows:
        ref = str(result["receipt_ref"])
        if ref not in results_by_ref:
            results_by_ref[ref] = result

    missing = []
    unissued = []
    uncommitted = []
    missing_verification_results = []
    verification_failures = []
    human_overrides = []
    committed_ids: set[str] = set()
    issued_ids: set[str] = set()
    received_ids: set[str] = set()

    for action in eligible:
        action_id = str(action["upstream_action_id"])
        rows = by_action.get(action_id, [])
        if not rows:
            missing.append({"upstream_action_id": action_id, "scenario_id": action.get("scenario_id"), "reason": "no_receipt"})
            continue
        for row in rows:
            if row.get("received_by_tcd") is True:
                received_ids.add(action_id)
            if row.get("issued") is True:
                issued_ids.add(action_id)
            else:
                unissued.append({"upstream_action_id": action_id, "receipt_ref": row.get("receipt_ref"), "reason": "issued_not_true"})
            if row.get("committed") is True:
                committed_ids.add(action_id)
            else:
                uncommitted.append({"upstream_action_id": action_id, "receipt_ref": row.get("receipt_ref"), "reason": "committed_not_true"})
            result = results_by_ref.get(str(row.get("receipt_ref")))
            if result is None:
                missing_verification_results.append({"upstream_action_id": action_id, "receipt_ref": row.get("receipt_ref")})
            elif result.get("ok") is not True:
                verification_failures.append({"upstream_action_id": action_id, "receipt_ref": row.get("receipt_ref"), "failure_code": result.get("failure_code")})
        if any(r.get("human_override") for r in rows):
            human_overrides.append({"upstream_action_id": action_id, "scenario_id": action.get("scenario_id")})

    complete = (
        len(committed_ids) == len(eligible)
        and len(issued_ids) == len(eligible)
        and not input_errors
        and not missing
        and not duplicates
        and not orphan_receipts
        and not unissued
        and not uncommitted
        and not missing_verification_results
        and not duplicate_verification_results
        and not orphan_verification_results
        and not verification_failures
    )
    return {
        "ok": complete,
        "failure_code": None if complete else FailureCode.RECONCILIATION_INCOMPLETE.value,
        "message": "reconciliation complete" if complete else "reconciliation incomplete",
        "upstream_eligible_actions": len(eligible),
        "received_by_tcd": len(received_ids),
        "receipts_issued": len(issued_ids),
        "receipts_committed": len(committed_ids),
        "missing": missing,
        "duplicates": duplicates,
        "orphan_receipts": orphan_receipts,
        "verification_failures": verification_failures,
        "human_overrides": human_overrides,
        "unissued_receipts": unissued,
        "uncommitted_receipts": uncommitted,
        "missing_verification_results": missing_verification_results,
        "duplicate_verification_results": duplicate_verification_results,
        "orphan_verification_results": orphan_verification_results,
        "input_errors": input_errors,
        "complete": complete,
    }


def reconcile_files(eligible_actions_path: Path, receipt_index_path: Path, verification_results_path: Path) -> dict[str, Any]:
    try:
        eligible_actions = strict_json_load(eligible_actions_path)
        receipt_index = strict_json_load(receipt_index_path)
        verification_results = strict_json_load(verification_results_path)
    except StrictJsonError as exc:
        return _strict_json_failure(exc)
    except OSError as exc:
        return _incomplete("could not load reconciliation inputs", failure_code=FailureCode.INVALID_JSON.value, input_errors=[{"reason": str(exc)}])
    if not isinstance(eligible_actions, dict) or not isinstance(receipt_index, dict) or not isinstance(verification_results, dict):
        return _incomplete("reconciliation inputs must be JSON objects", input_errors=[{"reason": "input_must_be_object"}])
    return reconcile(eligible_actions, receipt_index, verification_results)
