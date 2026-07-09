# TCD Proof Public Demo
This repository shows how TCD Proof turns a selected AI-assisted action into a signed, reviewable receipt with policy binding, evidence references, and independent verification.
The examples are redacted and do not include customer data, raw prompts, model answers, secrets, or private runtime code.
## What you can find here
- redacted receipt summaries
- independent verification reports
- evidence-chain commit examples
- Quickstart docs for running the local demo
---
## Repository layout
```text
tcd-proof-public/
  README.md
  .gitignore
  docs/
    full-chain-receipt-quickstart.md
    receipt-and-evidence-model.md
    architecture-notes.md
  examples/
    full-chain-receipt-summary.redacted.json
    verify-report.redacted.json
```
---
## Included materials
| File | Purpose |
|---|---|
| [`docs/full-chain-receipt-quickstart.md`](docs/full-chain-receipt-quickstart.md) | Public Quickstart and reviewer runbook for the full-chain receipt path |
| [`examples/full-chain-receipt-summary.redacted.json`](examples/full-chain-receipt-summary.redacted.json) | Redacted representative final summary from a successful full-chain local run |
| [`examples/verify-report.redacted.json`](examples/verify-report.redacted.json) | Redacted representative verification report |
| [`docs/receipt-and-evidence-model.md`](docs/receipt-and-evidence-model.md) | Explanation of receipt, evidence, ledger, and verification concepts |
| [`docs/architecture-notes.md`](docs/architecture-notes.md) | Public architecture notes for the TCD Proof control-plane flow |
---
## Buyer-facing vertical demo: AML/KYB Alert Review
This repository also includes a synthetic buyer-facing demo for an AI-assisted AML/KYB alert review:
[`demos/aml_kyb_alert_review/`](demos/aml_kyb_alert_review/)
The demo is designed for customer discovery, advisor review, investor conversations, and website-linked product storytelling. It shows how TCD Proof can turn a selected compliance workflow action into a signed, policy-bound receipt that can be independently verified later.
The scenario is intentionally narrow: a synthetic fintech compliance team receives an AML/KYB alert, an AI assistant summarizes risk factors, and TCD Proof records the governed action as a reviewable proof artifact.
The demo shows:
- a synthetic AML/KYB alert review request
- a redacted public receipt view
- an independent verify OK report
- a negative verification example where the wrong expected policy/config/build fails
- a restart-safe by-reference verification example
The key buyer message is:
> TCD Proof is not trying to prove that the AI model is correct. It proves that a selected AI-assisted action was governed, signed, policy-bound, and independently reviewable without exposing raw customer data.
Included demo files:
| File | Purpose |
|---|---|
| [`demos/aml_kyb_alert_review/README.md`](demos/aml_kyb_alert_review/README.md) | Buyer-facing explanation of the AML/KYB alert review scenario |
| [`demos/aml_kyb_alert_review/demo_walkthrough.md`](demos/aml_kyb_alert_review/demo_walkthrough.md) | Step-by-step walkthrough from diagnose to verify |
| [`demos/aml_kyb_alert_review/sample_alert_request.json`](demos/aml_kyb_alert_review/sample_alert_request.json) | Synthetic alert review request |
| [`demos/aml_kyb_alert_review/sample_receipt_public.json`](demos/aml_kyb_alert_review/sample_receipt_public.json) | Redacted public receipt view |
| [`demos/aml_kyb_alert_review/sample_verify_report.json`](demos/aml_kyb_alert_review/sample_verify_report.json) | Independent verification OK report |
| [`demos/aml_kyb_alert_review/sample_wrong_policy_verify_fail.json`](demos/aml_kyb_alert_review/sample_wrong_policy_verify_fail.json) | Negative verification example |
| [`demos/aml_kyb_alert_review/sample_restart_safe_verify.json`](demos/aml_kyb_alert_review/sample_restart_safe_verify.json) | Restart-safe by-reference verification example |
This demo does not claim production HSM deployment, production hardware-root trust, global consensus, a real AML model, real bank data, real customer data, or regulatory certification.
---
## Full-chain receipt demo
TCD Proof is not only a receipt formatter. A local full-chain run exercises the complete governed proof path:
1. A `/diagnose` request enters the hardened HTTP surface.
2. PolicyStore and SecurityRouter resolve a Terminal Contract.
3. TCD issues signed decision and commit receipts.
4. Receipt references and evidence-chain state are persisted in local SQLite.
5. Independent verification succeeds by receipt reference, verification bundle, top-level receipt material, storage-window chain traversal, and after process restart.
A representative redacted result ends with:
```json
{
  "all_checks_pass": true,
  "receipt_surface_kind": "durable_committed",
  "receipt_delivery_state": "committed",
  "ledger_stage": "committed",
  "evidence_durable": true,
  "signature_verified": true,
  "policy_binding_verified": true,
  "cfg_binding_verified": true,
  "build_binding_verified": true,
  "image_binding_verified": true,
  "verify_after_restart_by_ref_ok": true
}
```
---
## What the full-chain run validates
The local full-chain run validates:
- local HMAC receipt signing
- PolicyStore loading
- SecurityRouter path
- schema-view public receipt projection
- verification bundle exposure
- build/image supply-chain binding
- PQ-required signature path
- durable SQLite `receipt_ref` lookup
- durable SQLite evidence-chain commit
- decision receipt and commit receipt
- by-ref receipt verification
- by-bundle receipt verification
- top-level receipt verification
- storage-window chain verification
- restart-safe durable by-ref verification
---
## Representative outcome
A successful full-chain run produces a final summary like:
```json
{
  "all_checks_pass": true,
  "diagnose_core": {
    "decision": "block",
    "allowed": false,
    "required_action": "block",
    "receipt_surface_kind": "durable_committed",
    "receipt_delivery_state": "committed",
    "ledger_stage": "committed",
    "evidence_durable": true,
    "evidence_storage_ready": true,
    "pq_required": true,
    "pq_signature_ok": true
  },
  "supply_chain_binding": {
    "verify_supply_chain_binding_verified": true,
    "by_ref_build_binding_verified": true,
    "by_ref_image_binding_verified": true,
    "by_bundle_build_binding_verified": true,
    "by_bundle_image_binding_verified": true,
    "top_level_build_binding_verified": true,
    "top_level_image_binding_verified": true,
    "after_restart_build_binding_verified": true,
    "after_restart_image_binding_verified": true
  }
}
```
The redacted example summary is available here:
[`examples/full-chain-receipt-summary.redacted.json`](examples/full-chain-receipt-summary.redacted.json)
---
## Independent verification paths
The demo includes multiple verification modes.
| Verification path | What it demonstrates |
|---|---|
| by-ref verification | A receipt can be looked up and verified by durable `receipt_ref` |
| by-bundle verification | A returned `receipt_verification` bundle can be verified independently |
| top-level receipt verification | Direct receipt material can be verified without relying on the original response shape |
| storage-window verification | The durable evidence-chain window can be checked for expected head, ledger, and commit state |
| after-restart by-ref verification | The receipt remains verifiable after restarting the local service |
A representative redacted verification report is available here:
[`examples/verify-report.redacted.json`](examples/verify-report.redacted.json)
---
## Important interpretation note
In some runs, the public `/diagnose` receipt surface may not directly expose build/image fields while independent verification still confirms build and image binding.
That case is represented as:
```json
{
  "diagnose_supply_chain_surface_present": false,
  "verify_supply_chain_binding_verified": true,
  "build_binding_verified": true,
  "image_binding_verified": true
}
```
For audit review, the stronger statement is the verification-backed statement:
```json
{
  "verify_supply_chain_binding_verified": true,
  "build_binding_verified": true,
  "image_binding_verified": true
}
```
---
## Public inspection path
### 1. Clone this public repository
```bash
git clone https://github.com/amelieliao/tcd-proof-public.git
cd tcd-proof-public
```
### 2. Inspect the redacted full-chain summary
```bash
python3 -m json.tool examples/full-chain-receipt-summary.redacted.json | sed -n '1,260p'
```
### 3. Inspect the redacted verification report
```bash
python3 -m json.tool examples/verify-report.redacted.json | sed -n '1,260p'
```
### 4. Check the most important pass/fail fields
```bash
python3 - <<'PY'
import json
summary = json.load(open("examples/full-chain-receipt-summary.redacted.json", "r", encoding="utf-8"))
checks = summary.get("checks", {})
print("all_checks_pass =", summary.get("all_checks_pass"))
for key in [
    "runtime_receipts",
    "runtime_schema_view_enabled",
    "runtime_policy_store_enabled",
    "runtime_security_router_enabled",
    "runtime_receipt_ref_sqlite",
    "runtime_evidence_store_sqlite",
    "runtime_evidence_store_durable",
    "diagnose_has_receipt_public",
    "diagnose_has_receipt_verification",
    "diagnose_has_signature",
    "diagnose_policy_bound",
    "diagnose_supply_chain_bound",
    "diagnose_pq_required",
    "diagnose_pq_signature_ok",
    "diagnose_durable_committed",
    "diagnose_commit_receipt",
    "diagnose_decision_receipt",
    "diagnose_attestation_ref",
    "diagnose_audit_ref",
    "diagnose_security_router_surface",
    "verify_by_ref_ok",
    "verify_by_bundle_ok",
    "verify_top_level_ok",
    "verify_storage_window_ok",
    "verify_after_restart_by_ref_ok",
]:
    print(f"{key} =", checks.get(key))
PY
```
Expected output includes:
```text
all_checks_pass = True
runtime_receipts = True
runtime_policy_store_enabled = True
runtime_security_router_enabled = True
runtime_receipt_ref_sqlite = True
runtime_evidence_store_sqlite = True
runtime_evidence_store_durable = True
diagnose_durable_committed = True
verify_by_ref_ok = True
verify_by_bundle_ok = True
verify_top_level_ok = True
verify_storage_window_ok = True
verify_after_restart_by_ref_ok = True
```
---
## Authorized local runtime path
The public repository alone cannot run `tcd.service_http:create_app`.
The local runtime path described in [`docs/full-chain-receipt-quickstart.md`](docs/full-chain-receipt-quickstart.md) is intended for authorized technical reviewers who have access to the private TCD runtime repository or a reviewer demo bundle.
The public Quickstart documents the shape of the run and the expected proof result, while avoiding public exposure of private implementation code, secrets, databases, or unredacted logs.
---
## Receipt and evidence model
The receipt and evidence model is described here:
[`docs/receipt-and-evidence-model.md`](docs/receipt-and-evidence-model.md)
A TCD Proof receipt can bind:
- request identity
- tenant and subject identity
- workflow or action type
- route identity
- decision identity
- policy reference
- policy-set reference
- policy digest
- Terminal Contract outcome
- model/config/build/runtime fingerprints
- risk controller state
- evidence references
- ledger references
- audit references
- receipt configuration fingerprint
- signing-key identity
- signature metadata
- verification status
The evidence model separates public receipt views, verification views, audit views, ledger state, and durable storage references so the proof path can remain bounded and content-agnostic.
---
## Architecture notes
The public architecture notes are available here:
[`docs/architecture-notes.md`](docs/architecture-notes.md)
The demo materials describe a three-plane architecture:
1. **Inference Data Plane**  
   Establishes request identity, transport context, envelope validity, rate limits, idempotency scope, and payload digest.
2. **Decision and Policy Plane**  
   Turns detector, calibration, risk, policy, route, and security signals into a final Terminal Contract.
3. **Governance and Evidence Plane**  
   Issues signed receipts, persists durable evidence, records audit/ledger/commit references, and supports independent verification.
The architecture also includes a governed mutation loop for policy reloads, configuration changes, signing-key rotation, allowlist updates, runtime patch gates, calibration changes, retries, rollback, and compensation paths.
---
## How this maps to the TCD Proof website
The website buttons can point to:
**Run local Quickstart**
```text
https://github.com/amelieliao/tcd-proof-public/blob/main/docs/full-chain-receipt-quickstart.md
```
**View redacted summary**
```text
https://github.com/amelieliao/tcd-proof-public/blob/main/examples/full-chain-receipt-summary.redacted.json
```
Suggested HTML:
```html
<a class="btn btn-secondary" href="https://github.com/amelieliao/tcd-proof-public/blob/main/docs/full-chain-receipt-quickstart.md" target="_blank" rel="noopener">
  Run the local Quickstart
</a>
<a class="btn btn-secondary" href="https://github.com/amelieliao/tcd-proof-public/blob/main/examples/full-chain-receipt-summary.redacted.json" target="_blank" rel="noopener">
  View redacted summary
</a>
```
These links will work after the files are pushed to `tcd-proof-public/main`.
---
## Quick links
- [Run or review the local full-chain Quickstart](docs/full-chain-receipt-quickstart.md)
- [View redacted full-chain summary](examples/full-chain-receipt-summary.redacted.json)
- [View redacted verification report](examples/verify-report.redacted.json)
- [Read receipt and evidence model overview](docs/receipt-and-evidence-model.md)
- [Read architecture notes](docs/architecture-notes.md)
---
## Contact
For an async demo pack or reviewer access:
```text
aliao@tcdproof.com
```
Website:
```text
https://tcdproof.com
```