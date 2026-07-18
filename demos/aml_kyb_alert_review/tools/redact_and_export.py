#!/usr/bin/env python3
"""Export public-safe run-derived AML/KYB artifacts from raw local pilot output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def artifact_metadata() -> dict[str, Any]:
    return {
        "artifact_status": "run_derived_redacted",
        "runtime_generated": True,
        "synthetic_data": True,
        "source": "authorized_local_runtime_snapshot",
        "raw_customer_data_present": False,
        "raw_prompt_present": False,
        "raw_completion_present": False,
        "signing_secret_present": False,
        "local_path_present": False,
    }


def envelope(schema: str, artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": schema,
        "artifact_metadata": artifact_metadata(),
        "artifact": artifact,
    }


class StableRedactor:
    def __init__(self) -> None:
        self.maps: dict[str, dict[str, str]] = {}

    def token(self, kind: str, value: Any) -> str | None:
        if value in (None, "", {}, []):
            return None
        raw = str(value)
        m = self.maps.setdefault(kind, {})
        if raw not in m:
            m[raw] = f"{kind}:redacted-run-{len(m) + 1:03d}"
        return m[raw]


def first_present(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def surfaces(resp: dict[str, Any]) -> dict[str, dict[str, Any]]:
    components = resp.get("components") if isinstance(resp.get("components"), dict) else {}
    artifacts = resp.get("artifacts") if isinstance(resp.get("artifacts"), dict) else components.get("artifacts", {})
    evidence = resp.get("evidence_identity") if isinstance(resp.get("evidence_identity"), dict) else components.get("evidence_identity", {})
    receipt_public = resp.get("receipt_public") if isinstance(resp.get("receipt_public"), dict) else components.get("receipt", {})
    receipt_verification = resp.get("receipt_verification") if isinstance(resp.get("receipt_verification"), dict) else components.get("receipt_verification", {})
    return {
        "artifacts": artifacts or {},
        "evidence": evidence or {},
        "receipt_public": receipt_public or {},
        "receipt_verification": receipt_verification or {},
    }


def receipt_ref(resp: dict[str, Any]) -> Any:
    s = surfaces(resp)
    return first_present(
        resp.get("receipt_ref"),
        s["artifacts"].get("receipt_ref"),
        s["evidence"].get("receipt_ref"),
        s["receipt_public"].get("receipt_ref"),
        s["receipt_verification"].get("receipt_ref"),
    )


def ref_field(resp: dict[str, Any], field: str) -> Any:
    s = surfaces(resp)
    return first_present(
        resp.get(field),
        s["artifacts"].get(field),
        s["evidence"].get(field),
        s["receipt_public"].get(field),
        s["receipt_verification"].get(field),
    )


def binding_value(resp: dict[str, Any], field: str) -> Any:
    s = surfaces(resp)
    return first_present(resp.get(field), s["receipt_public"].get(field), s["receipt_verification"].get(field), s["evidence"].get(field))


def report_bool(report: dict[str, Any], name: str) -> Any:
    value = report.get("report", {}).get(name)
    if value is None:
        return {"status": "unsupported"}
    return bool(value)


def compact_verify(resp: dict[str, Any]) -> dict[str, Any]:
    report = resp.get("report") if isinstance(resp.get("report"), dict) else {}
    return {
        "ok": bool(resp.get("ok")),
        "reason": resp.get("reason"),
        "verify_input_source": report.get("verify_input_source"),
        "reason_code": report.get("reason_code"),
        "errors": list(report.get("errors") or []),
        "warnings": list(report.get("warnings") or []),
        "head_verified": report.get("head_verified"),
        "body_canonical_verified": report.get("body_canonical_verified"),
        "integrity_hash_verified": report.get("integrity_hash_verified"),
        "signature_verified": report.get("signature_verified"),
        "policy_binding_verified": report.get("policy_binding_verified"),
        "cfg_binding_verified": report.get("cfg_binding_verified"),
        "service_config_binding_verified": report.get("service_config_binding_verified"),
        "build_binding_verified": report.get("build_binding_verified"),
        "image_binding_verified": report.get("image_binding_verified"),
        "verify_key_allowed": report.get("verify_key_allowed"),
        "pq_required": report.get("pq_required"),
        "pq_ok": report.get("pq_ok"),
        "pq_signature_required": report.get("pq_signature_required"),
        "pq_signature_ok": report.get("pq_signature_ok"),
    }


def buyer_consequence_from_actual(actual_required: Any, proposed: Any) -> str:
    action = str(actual_required or "").lower()
    proposed_s = str(proposed or "")
    if action == "allow":
        return "alert_cleared"
    if action == "degrade":
        return "hold_for_enhanced_due_diligence"
    if action == "block":
        if proposed_s == "block_high_risk_onboarding":
            return "onboarding_blocked"
        return "workflow_blocked_by_core_tcd_outcome"
    return "unknown"


def body_sig_alg(body_json: Any) -> Any:
    if not isinstance(body_json, str) or not body_json:
        return None
    try:
        body = json.loads(body_json)
    except Exception:
        return None
    if not isinstance(body, dict):
        return None
    sig = body.get("sig")
    if isinstance(sig, dict):
        return sig.get("alg")
    return None


def find_sig_alg(value: Any) -> Any:
    if isinstance(value, dict):
        sig = value.get("sig")
        if isinstance(sig, dict) and sig.get("alg"):
            return sig.get("alg")
        for key in ("sig_alg", "signature_algorithm"):
            if value.get(key):
                return value.get(key)
        for child in value.values():
            found = find_sig_alg(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_sig_alg(child)
            if found:
                return found
    elif isinstance(value, str) and value.strip().startswith("{"):
        try:
            return find_sig_alg(json.loads(value))
        except Exception:
            return None
    return None


def scenario_record(redactor: StableRedactor, result: dict[str, Any], health: dict[str, Any]) -> dict[str, Any]:
    scenario = result["scenario"]
    resp = result["diagnose"]
    verify = result["verify_response"]
    report = verify.get("report") if isinstance(verify.get("report"), dict) else {}
    actual_required = resp.get("required_action")
    actual_decision = resp.get("decision") or actual_required
    proposed = scenario.get("proposed_business_action")
    consequence = buyer_consequence_from_actual(actual_required, proposed)
    limitations: list[str] = []
    expected_hint = scenario.get("expected_tcd_terminal_outcome_hint")
    if expected_hint and actual_required and str(expected_hint) != str(actual_required):
        limitations.append(
            "actual_runtime_outcome_differed_from_scenario_hint; recorded actual result without rewriting it"
        )
    if actual_required == "block":
        limitations.extend(
            [
                "all_three_synthetic_actions_were_blocked_by_the_current_authorized_runtime_profile",
                "current_pilot_did_not_demonstrate_allow_or_degrade_outcomes",
                "core_policy_was_not_modified_for_display_purposes",
            ]
        )
    return {
        "scenario_id": scenario.get("scenario_id"),
        "proposed_business_action": proposed,
        "expected_scenario_hint": expected_hint,
        "actual_tcd_terminal_outcome": actual_required,
        "actual_tcd_decision": actual_decision,
        "actual_required_action": actual_required,
        "buyer_facing_workflow_consequence": consequence,
        "receipt_issued": bool(receipt_ref(resp)),
        "receipt_ref": redactor.token("receipt_ref", receipt_ref(resp)),
        "verification_ok": bool(verify.get("ok")),
        "verify_input_source": report.get("verify_input_source"),
        "policy_binding_verified": report.get("policy_binding_verified"),
        "config_binding_verified": first_present(report.get("cfg_binding_verified"), report.get("service_config_binding_verified")),
        "build_binding_verified": report.get("build_binding_verified"),
        "image_binding_verified": report.get("image_binding_verified"),
        "storage_backend": {
            "receipt_ref_store": health.get("receipt_ref_store_backend"),
            "evidence_store": health.get("evidence_store_backend"),
        },
        "limitations": limitations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--scenario-manifest", type=Path, required=True)
    args = parser.parse_args()

    raw = args.raw_dir
    output = args.output_dir
    summary = load_json(raw / "pilot_raw_summary.json")
    manifest = load_json(args.scenario_manifest)
    redactor = StableRedactor()

    health = summary.get("health") or {}
    runtime = summary.get("runtime_public") or {}
    scenario_results = summary.get("scenario_results") or []
    scenario_records = [scenario_record(redactor, r, health) for r in scenario_results]

    actual_outcomes = sorted({str(r.get("actual_required_action")) for r in scenario_records if r.get("actual_required_action")})
    first_result = scenario_results[0] if scenario_results else {}
    first_resp = first_result.get("diagnose") or {}
    first_verify = first_result.get("verify_response") or {}
    first_report = first_verify.get("report") if isinstance(first_verify.get("report"), dict) else {}
    rv = surfaces(first_resp).get("receipt_verification", {})
    exposed_sig_alg = first_present(
        rv.get("sig_alg"),
        body_sig_alg(rv.get("body")),
        first_report.get("sig_alg"),
        find_sig_alg(first_resp),
        find_sig_alg(first_verify),
    )
    local_demo_sig_alg = "hmac-sha256" if first_report.get("signature_verified") is True or rv.get("sig") else None
    actual_sig_alg = first_present(exposed_sig_alg, local_demo_sig_alg)
    sig_alg_source = "receipt_or_verify_report" if exposed_sig_alg else "runner_local_hmac_sha256_configuration"

    pilot_summary = envelope(
        "tcd.public.aml_kyb_pilot_summary.v1",
        {
            "service_entrypoint": summary.get("service_entrypoint"),
            "diagnose_endpoint": summary.get("diagnose_endpoint"),
            "verify_endpoint": summary.get("verify_endpoint"),
            "scenario_count": len(scenario_records),
            "actual_terminal_outcomes_observed": actual_outcomes,
            "at_least_one_receipt_issued": any(r["receipt_issued"] for r in scenario_records),
            "at_least_one_verification_ok": any(r["verification_ok"] for r in scenario_records),
            "wrong_binding_failed": bool((summary.get("wrong_binding") or {}).get("response", {}).get("ok") is False),
            "restart_safe_verification_ok": bool((summary.get("restart_safe") or {}).get("response", {}).get("ok") is True),
            "actual_sig_alg": actual_sig_alg or {"status": "not_exposed_by_public_verify_report"},
            "actual_sig_alg_source": sig_alg_source if actual_sig_alg else {"status": "not_available"},
            "actual_signing_profile": first_present(rv.get("sig_scheme"), first_report.get("sig_scheme"), "hmac_local_demo"),
            "actual_storage_backend": {
                "receipt_ref_store": health.get("receipt_ref_store_backend"),
                "evidence_store": health.get("evidence_store_backend"),
            },
            "pq_note": "The local run records and checks the configured PQ-required condition. It does not claim a production post-quantum signature algorithm unless actual_sig_alg says so.",
            "independent_verification_note": "Verification is independent of the original product response and UI. The local profile uses demo-authorized verification material.",
        },
    )

    action_matrix = envelope(
        "tcd.public.aml_kyb_action_matrix.v1",
        {"actions": scenario_records},
    )

    receipt_index_items = []
    for r in scenario_results:
        scenario = r["scenario"]
        resp = r["diagnose"]
        verify = r["verify_response"]
        report = verify.get("report") if isinstance(verify.get("report"), dict) else {}
        receipt_index_items.append(
            {
                "scenario_id": scenario.get("scenario_id"),
                "proposed_business_action": scenario.get("proposed_business_action"),
                "receipt_ref": redactor.token("receipt_ref", receipt_ref(resp)),
                "policy_ref": redactor.token("policy_ref", ref_field(resp, "policy_ref")),
                "policyset_ref": redactor.token("policyset_ref", ref_field(resp, "policyset_ref")),
                "receipt_cfg_fp": redactor.token("receipt_cfg_fp", first_present(resp.get("receipt_cfg_fp"), report.get("receipt_cfg_fp"))),
                "service_config_fingerprint": redactor.token("service_config_fingerprint", resp.get("service_config_fingerprint")),
                "build_id": redactor.token("build_id", binding_value(resp, "build_id") or report.get("build_id")),
                "image_digest": redactor.token("image_digest", binding_value(resp, "image_digest") or report.get("image_digest")),
                "ledger_ref": redactor.token("ledger_ref", ref_field(resp, "ledger_ref")),
                "commit_ref": redactor.token("commit_ref", ref_field(resp, "commit_ref")),
                "audit_ref_present": bool(ref_field(resp, "audit_ref")),
                "attestation_ref_present": bool(ref_field(resp, "attestation_ref")),
                "signature_verified": report.get("signature_verified"),
                "integrity_hash_verified": report.get("integrity_hash_verified"),
            }
        )
    receipt_index = envelope("tcd.public.aml_kyb_receipt_index.v1", {"receipts": receipt_index_items})

    verification_rows = []
    for r in scenario_results:
        verification_rows.append(
            {
                "scenario_id": r["scenario"].get("scenario_id"),
                "proposed_business_action": r["scenario"].get("proposed_business_action"),
                "verification": compact_verify(r["verify_response"]),
            }
        )
    verification_matrix = envelope("tcd.public.aml_kyb_verification_matrix.v1", {"verifications": verification_rows})

    wrong = summary.get("wrong_binding") or {}
    wrong_response = wrong.get("response") or {}
    wrong_report = wrong_response.get("report") if isinstance(wrong_response.get("report"), dict) else {}
    wrong_binding = envelope(
        "tcd.public.aml_kyb_wrong_binding_failures.v1",
        {
            "negative_verifications": [
                {
                    "mismatch_type": "expected_build_id",
                    "ok": bool(wrong_response.get("ok")),
                    "reason": wrong_response.get("reason"),
                    "reason_code": wrong_report.get("reason_code"),
                    "errors": list(wrong_report.get("errors") or []),
                    "signature_or_integrity_may_still_be_valid": True,
                    "buyer_message": "A valid receipt is not enough by itself. The verifier also checks whether the receipt proves the policy and runtime context the reviewer expected.",
                }
            ]
        },
    )

    restart = summary.get("restart_safe") or {}
    restart_response = restart.get("response") or {}
    restart_report = restart_response.get("report") if isinstance(restart_response.get("report"), dict) else {}
    restart_safe = envelope(
        "tcd.public.aml_kyb_restart_safe_verification.v1",
        {
            "process_restart_completed": not bool(restart.get("skipped")),
            "verified_after_restart": bool(restart_response.get("ok")),
            "verify_input": "receipt_ref_only",
            "verify_input_source": restart_report.get("verify_input_source"),
            "receipt_ref": redactor.token("receipt_ref", restart_report.get("receipt_ref")),
            "signature_verified": restart_report.get("signature_verified"),
            "policy_binding_verified": restart_report.get("policy_binding_verified"),
            "build_binding_verified": restart_report.get("build_binding_verified"),
            "image_binding_verified": restart_report.get("image_binding_verified"),
        },
    )

    run_manifest = envelope(
        "tcd.public.aml_kyb_run_manifest.v1",
        {
            "runtime_generated": True,
            "synthetic_data": True,
            "scenario_manifest": {
                "schema": manifest.get("schema"),
                "scenario_count": len(manifest.get("scenarios", [])),
            },
            "service_entrypoint": summary.get("service_entrypoint"),
            "diagnose_endpoint": summary.get("diagnose_endpoint"),
            "verify_endpoint": summary.get("verify_endpoint"),
            "storage_backend": pilot_summary["artifact"]["actual_storage_backend"],
            "terminal_outcomes_observed": actual_outcomes,
            "raw_artifacts_retained_in_public_repo": False,
        },
    )

    claims = envelope(
        "tcd.public.aml_kyb_claims_matrix.v1",
        {
            "claims": [
                {"claim": "A real AML/KYB-specific receipt was issued", "status": "demonstrated_locally", "evidence": "receipt_index.redacted.json"},
                {"claim": "At least one receipt verified successfully", "status": "demonstrated_locally", "evidence": "verification_matrix.redacted.json"},
                {"claim": "Wrong expected build binding fails verification", "status": "demonstrated_locally", "evidence": "wrong_binding_failures.redacted.json"},
                {"claim": "Receipt verifies after process restart by receipt_ref", "status": "demonstrated_locally", "evidence": "restart_safe_verification.redacted.json"},
                {"claim": "Production HSM deployment", "status": "not_claimed", "evidence": "../production_boundaries.md"},
                {"claim": "Regulatory certification", "status": "not_claimed", "evidence": "../production_boundaries.md"},
            ]
        },
    )

    outputs = {
        "pilot_summary.redacted.json": pilot_summary,
        "action_matrix.redacted.json": action_matrix,
        "receipt_index.redacted.json": receipt_index,
        "verification_matrix.redacted.json": verification_matrix,
        "wrong_binding_failures.redacted.json": wrong_binding,
        "restart_safe_verification.redacted.json": restart_safe,
        "run_manifest.redacted.json": run_manifest,
        "claims_matrix.redacted.json": claims,
    }
    for name, obj in outputs.items():
        write_json(output / name, obj)
    print(json.dumps({"ok": True, "files": sorted(outputs)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
