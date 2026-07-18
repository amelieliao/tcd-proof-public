from __future__ import annotations

import json
from pathlib import Path


DEMO_ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_demo_json_parse() -> None:
    for path in DEMO_ROOT.rglob("*.json"):
        load_json(path)


def test_run_derived_artifacts_have_provenance() -> None:
    run_dir = DEMO_ROOT / "run_derived"
    expected = {
        "pilot_summary.redacted.json",
        "action_matrix.redacted.json",
        "receipt_index.redacted.json",
        "verification_matrix.redacted.json",
        "wrong_binding_failures.redacted.json",
        "restart_safe_verification.redacted.json",
        "claims_matrix.redacted.json",
        "run_manifest.redacted.json",
    }
    assert expected.issubset({p.name for p in run_dir.glob("*.json")})
    for name in expected:
        obj = load_json(run_dir / name)
        metadata = obj["artifact_metadata"]
        assert metadata["artifact_status"] == "run_derived_redacted"
        assert metadata["runtime_generated"] is True
        assert metadata["synthetic_data"] is True
        assert metadata["raw_customer_data_present"] is False
        assert metadata["signing_secret_present"] is False


def test_action_matrix_records_actual_runtime_outcomes() -> None:
    obj = load_json(DEMO_ROOT / "run_derived" / "action_matrix.redacted.json")
    actions = obj["artifact"]["actions"]
    assert len(actions) == 3
    for action in actions:
        assert "proposed_business_action" in action
        assert "expected_scenario_hint" in action
        assert action["actual_tcd_terminal_outcome"] == "block"
        assert action["buyer_facing_workflow_consequence"]
        assert action["receipt_issued"] is True
        assert action["verification_ok"] is True
        assert action["limitations"]
        assert "core_policy_was_not_modified_for_display_purposes" in action["limitations"]


def test_illustrative_manifest_marks_static_samples() -> None:
    obj = load_json(DEMO_ROOT / "illustrative_manifest.json")
    assert obj["runtime_generated"] is False
    assert obj["not_evidence_of_execution"] is True
    assert {item["path"] for item in obj["files"]} >= {
        "sample_alert_request.json",
        "sample_receipt_public.json",
        "sample_verify_report.json",
        "sample_wrong_policy_verify_fail.json",
        "sample_restart_safe_verify.json",
    }
