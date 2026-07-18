#!/usr/bin/env python3
"""Render buyer-facing AML/KYB assurance documents from run-derived artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_FILES = [
    "pilot_summary.redacted.json",
    "action_matrix.redacted.json",
    "receipt_index.redacted.json",
    "verification_matrix.redacted.json",
    "wrong_binding_failures.redacted.json",
    "restart_safe_verification.redacted.json",
    "claims_matrix.redacted.json",
    "run_manifest.redacted.json",
]
ILLUSTRATIVE_FILES = [
    "sample_alert_request.json",
    "sample_receipt_public.json",
    "sample_verify_report.json",
    "sample_wrong_policy_verify_fail.json",
    "sample_restart_safe_verify.json",
    "illustrative_manifest.json",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def artifact(path: Path) -> dict[str, Any]:
    return load_json(path)["artifact"]


def render_assurance_packet(demo_root: Path) -> None:
    run = demo_root / "run_derived"
    summary = artifact(run / "pilot_summary.redacted.json")
    action_matrix = artifact(run / "action_matrix.redacted.json")
    receipt_index = artifact(run / "receipt_index.redacted.json")
    verification_matrix = artifact(run / "verification_matrix.redacted.json")
    wrong = artifact(run / "wrong_binding_failures.redacted.json")
    restart = artifact(run / "restart_safe_verification.redacted.json")
    claims = artifact(run / "claims_matrix.redacted.json")

    action_rows = []
    for item in action_matrix.get("actions", []):
        action_rows.append(
            "| {proposed_business_action} | {actual_tcd_terminal_outcome} | {buyer_facing_workflow_consequence} | {receipt_issued} | {verification_ok} |".format(
                **item
            )
        )
    evidence_rows = []
    for item in receipt_index.get("receipts", []):
        evidence_rows.append(
            f"- `{item.get('scenario_id')}`: receipt `{item.get('receipt_ref')}`, policy `{item.get('policy_ref')}`, "
            f"config `{item.get('receipt_cfg_fp')}`, build `{item.get('build_id')}`, image `{item.get('image_digest')}`, "
            f"ledger `{item.get('ledger_ref')}`, commit `{item.get('commit_ref')}`."
        )
    claim_rows = []
    for item in claims.get("claims", []):
        claim_rows.append(f"| {item['claim']} | {item['status']} | `{item['evidence']}` |")

    wrong_item = (wrong.get("negative_verifications") or [{}])[0]
    packet = f"""# AML/KYB AI Action Assurance Packet

## Executive summary

This packet documents a synthetic local AML/KYB action-assurance run using the current authorized TCD runtime.

The pilot does not evaluate whether an AML model is correct. It demonstrates whether selected AI-assisted workflow actions can be governed, recorded in a cryptographically authenticated receipt, and checked later against the expected policy and runtime context.

All case data is synthetic. No raw customer data, raw prompt, raw model answer, signing secret, database, or private runtime source code is included.

All three actions were blocked by the current authorized runtime profile. The public artifacts preserve this actual result and do not claim that allow or degrade outcomes were demonstrated in this run.

## Workflow scope

- Workflow: synthetic AML/KYB alert review.
- Upstream AI assistance role: summarize synthetic risk factors and propose a business action.
- TCD governance role: issue and verify policy-bound receipts for selected actions.
- Human/compliance reviewer role: use the receipt to review governance evidence without raw case material.
- Scenarios executed: {summary.get('scenario_count')}.
- Actual terminal outcomes observed: `{summary.get('actual_terminal_outcomes_observed')}`.
- Actual signing profile: `{summary.get('actual_signing_profile')}`.
- Actual signature algorithm: `{summary.get('actual_sig_alg')}`.
- Actual storage backend: `{summary.get('actual_storage_backend')}`.

## Actions exercised

| Proposed business action | Actual TCD terminal outcome | Buyer-facing consequence | Receipt issued | Verify OK |
|---|---|---|---|---|
{chr(10).join(action_rows)}

## Evidence produced

{chr(10).join(evidence_rows)}

## Independent verification

Verification is performed independently of the original product response and UI. In the local demo profile, the verifier uses the verification material authorized for that profile. The packet does not claim unrestricted public verification.

Observed verify paths are summarized in [`run_derived/verification_matrix.redacted.json`](run_derived/verification_matrix.redacted.json).

## Negative verification

The pilot executed a real wrong-binding verification. Result: `{wrong_item.get('reason_code')}` with `ok={wrong_item.get('ok')}`.

A valid receipt is not enough by itself. The verifier also checks whether the receipt proves the policy and runtime context the reviewer expected.

## Restart-safe verification

The service process was stopped and restarted with the same durable local stores. The pilot then verified by receipt reference only. Result: `verified_after_restart={restart.get('verified_after_restart')}`, source `{restart.get('verify_input_source')}`.

## What this demonstrates

| Claim | Status | Evidence |
|---|---|---|
{chr(10).join(claim_rows)}

## What this does not demonstrate

- no real AML model
- no real customer data
- no regulatory certification
- no production HSM claim
- no production hardware-root claim
- no global consensus
- no proof that the AI decision was factually correct
- no claim of complete production readiness

## Recommended next pilot step

Run one selected customer workflow with synthetic or redacted inputs, a narrow set of actions, and an explicit reviewer audience. Do not start with a full platform rollout.
"""
    write_text(demo_root / "assurance_packet.md", packet)


def render_gap_report(demo_root: Path) -> None:
    rows = [
        ("customer-specific case/event adapter", "adapter_required", "Map the customer's case/event into the public DiagnoseRequest fields and context."),
        ("case identifier mapping", "customer_specific", "Use customer-owned case IDs or redacted references."),
        ("tenant mapping", "supported_with_configuration", "Tenant is a first-class request field."),
        ("proposed action mapping", "adapter_required", "Business action lives in scenario/context and must map to core allow/degrade/block."),
        ("policy/SOP source of truth", "customer_specific", "Customer policy source must be selected for a pilot."),
        ("policy versioning", "production_hardening_required", "Policy references are bound; production versioning process is customer-specific."),
        ("policy digest generation", "supported_now", "The run-derived artifacts include policy/config binding checks."),
        ("human review state", "adapter_required", "Represent as buyer-facing workflow consequence, not a new core TCD outcome."),
        ("enhanced due diligence state", "adapter_required", "Represent as workflow consequence mapped from core degrade."),
        ("escalation/approval workflow", "adapter_required", "Needs customer workflow integration."),
        ("evidence reference API", "adapter_required", "Pilot currently uses synthetic evidence references."),
        ("evidence retention", "production_hardening_required", "Retention policy is deployment-specific."),
        ("receipt distribution", "adapter_required", "Decide what receipt view each reviewer may receive."),
        ("verifier identity", "customer_specific", "Define authorized verifier roles."),
        ("verification material distribution", "production_hardening_required", "Local demo uses demo-authorized verification material."),
        ("signing-key management", "production_hardening_required", "Local HMAC is not production key management."),
        ("KMS/HSM integration", "production_hardening_required", "Not claimed by this local pilot."),
        ("key rotation", "not_yet_validated", "Not exercised by this AML/KYB pilot."),
        ("key revocation", "not_yet_validated", "Not exercised by this AML/KYB pilot."),
        ("durable storage", "supported_now", "Local durable receipt lookup and evidence storage were exercised."),
        ("WORM/object lock", "production_hardening_required", "Not part of the local pilot."),
        ("multi-tenant isolation", "production_hardening_required", "Requires deployment validation."),
        ("authentication/authorization", "production_hardening_required", "Local pilot disables production auth for localhost execution."),
        ("customer-specific policy mapping", "customer_specific", "Must be defined with the pilot customer."),
        ("PII minimization", "supported_now", "Public export excludes raw case material."),
        ("retention/deletion", "customer_specific", "Depends on customer compliance program."),
        ("incident response", "customer_specific", "Needs operational runbook integration."),
        ("audit export", "adapter_required", "Receipt packet shape exists; export workflow must be selected."),
        ("monitoring/SLO", "production_hardening_required", "Monitoring, alerting, and service-level objectives are not evaluated by this pilot."),
        ("observability", "production_hardening_required", "Operational telemetry packaging is not part of the public demo."),
        ("deployment model", "customer_specific", "Depends on customer environment."),
        ("security review", "adapter_required", "Use this packet as starting material."),
        ("model-risk review", "adapter_required", "Map receipt fields to the customer's review process."),
        ("RFP/customer-assurance packaging", "supported_with_configuration", "Assurance packet and claims matrix provide a starting packet."),
    ]
    body = ["# AML/KYB Integration Gap Report", "", "This report is written from the point of view of a potential AML/KYB pilot customer.", "", "| Area | Status | Notes |", "|---|---|---|"]
    body.extend(f"| {a} | {s} | {n} |" for a, s, n in rows)
    write_text(demo_root / "integration_gap_report.md", "\n".join(body))


def render_boundaries(demo_root: Path) -> None:
    summary = artifact(demo_root / "run_derived" / "pilot_summary.redacted.json")
    storage = summary.get("actual_storage_backend", {})
    text = f"""# AML/KYB Production Boundaries

## Local pilot demonstrated

- Service entrypoint: `{summary.get('service_entrypoint')}`.
- Diagnose endpoint: `{summary.get('diagnose_endpoint')}`.
- Verify endpoint: `{summary.get('verify_endpoint')}`.
- Actual signing profile: `{summary.get('actual_signing_profile')}`.
- Actual signature algorithm: `{summary.get('actual_sig_alg')}`.
- Actual storage backend: receipt lookup `{storage.get('receipt_ref_store')}`, evidence store `{storage.get('evidence_store')}`.
- Receipt issuance for synthetic AML/KYB actions.
- Actual verify OK path.
- Wrong expected binding failure.
- Policy/config/build/image binding checks where exposed by the verifier.
- Durable lookup and restart behavior for receipt reference verification.

## Production deployment requirement

- production key management
- KMS/HSM integration where required
- asymmetric or public verification where required
- WORM or replicated storage where required
- multi-region recovery
- tenant isolation
- production access control
- retention and deletion controls
- customer deployment validation

## Important boundaries

- Local HMAC does not equal production HSM.
- A policy-required PQ path does not automatically equal a real post-quantum signature algorithm.
- Synthetic AML signals do not equal a real AML model.
- Governance evidence does not equal model correctness.
- Technical evidence does not equal regulatory certification.
- Local restart-safe verification does not equal multi-region disaster recovery.
- A receipt reference does not equal raw evidence custody.
- Independent-of-UI verification does not automatically equal unrestricted public verification.
"""
    write_text(demo_root / "production_boundaries.md", text)


def render_claims_matrix(demo_root: Path) -> None:
    claims = artifact(demo_root / "run_derived" / "claims_matrix.redacted.json")
    lines = ["# AML/KYB Claims Matrix", "", "| Claim | Status | Evidence |", "|---|---|---|"]
    for item in claims.get("claims", []):
        lines.append(f"| {item['claim']} | {item['status']} | `{item['evidence']}` |")
    write_text(demo_root / "claims_matrix.md", "\n".join(lines))


def render_acceptance_gate(demo_root: Path) -> None:
    text = """# AML/KYB Demo Acceptance Gate

Run:

```bash
python demos/aml_kyb_alert_review/tools/check_demo_acceptance.py --public-root .
```

Minimum passing conditions:

- private repo final status equals private repo initial status
- synthetic AML/KYB scenario schema validated
- at least one actual scenario executed
- at least one actual receipt issued
- at least one actual verification succeeded
- actual policy binding verified
- at least one actual wrong-binding verification failed
- actual process restart completed
- receipt_ref verified after restart
- all run-derived artifacts provenance-labeled
- no raw customer data
- no raw prompt/completion
- no signing secret
- no SQLite/log/PID in public repo
- all JSON parses
- Markdown links pass
- public export validator passes
- no unrelated public files changed
- no private files changed
"""
    write_text(demo_root / "demo_acceptance_gate.md", text)


def render_artifact_manifest(demo_root: Path) -> None:
    files: list[dict[str, Any]] = []
    for name in ILLUSTRATIVE_FILES:
        p = demo_root / name
        if p.exists():
            files.append(
                {
                    "path": name,
                    "source_category": "illustrative_static_sample",
                    "runtime_generated": False,
                    "synthetic_data": True,
                    "public_safe": True,
                    "sha256": sha256_file(p),
                    "claim_status": "illustrative_not_execution_evidence",
                }
            )
    for name in ["run_derived/README.md"] + [f"run_derived/{n}" for n in RUN_FILES]:
        p = demo_root / name
        if p.exists():
            files.append(
                {
                    "path": name,
                    "source_category": "run_derived_redacted" if name.endswith(".json") else "run_derived_documentation",
                    "runtime_generated": name.endswith(".json"),
                    "synthetic_data": True,
                    "public_safe": True,
                    "sha256": sha256_file(p),
                    "claim_status": "evidence" if name.endswith(".json") else "documentation",
                }
            )
    manifest = {
        "schema": "tcd.public.aml_kyb_artifact_manifest.v1",
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "synthetic_data": True,
        "public_safe": True,
        "files": files,
    }
    write_json(demo_root / "artifact_manifest.json", manifest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root", type=Path, required=True)
    args = parser.parse_args()
    demo_root = args.demo_root.resolve()
    render_assurance_packet(demo_root)
    render_gap_report(demo_root)
    render_boundaries(demo_root)
    render_claims_matrix(demo_root)
    render_acceptance_gate(demo_root)
    render_artifact_manifest(demo_root)
    print(json.dumps({"ok": True, "demo_root": str(demo_root)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
