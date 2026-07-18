# AML/KYB AI Action Assurance Packet

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
- Scenarios executed: 3.
- Actual terminal outcomes observed: `['block']`.
- Actual signing profile: `hmac_local_demo`.
- Actual signature algorithm: `hmac-sha256`.
- Actual storage backend: `{'evidence_store': 'sqlite', 'receipt_ref_store': 'sqlite'}`.

## Actions exercised

| Proposed business action | Actual TCD terminal outcome | Buyer-facing consequence | Receipt issued | Verify OK |
|---|---|---|---|---|
| clear_low_risk_alert | block | workflow_blocked_by_core_tcd_outcome | True | True |
| hold_for_enhanced_due_diligence | block | workflow_blocked_by_core_tcd_outcome | True | True |
| block_high_risk_onboarding | block | onboarding_blocked | True | True |

## Evidence produced

- `synthetic-clear-low-risk`: receipt `receipt_ref:redacted-run-001`, policy `policy_ref:redacted-run-001`, config `receipt_cfg_fp:redacted-run-001`, build `build_id:redacted-run-001`, image `image_digest:redacted-run-001`, ledger `ledger_ref:redacted-run-001`, commit `commit_ref:redacted-run-001`.
- `synthetic-hold-for-enhanced-due-diligence`: receipt `receipt_ref:redacted-run-002`, policy `policy_ref:redacted-run-001`, config `receipt_cfg_fp:redacted-run-001`, build `build_id:redacted-run-001`, image `image_digest:redacted-run-001`, ledger `ledger_ref:redacted-run-002`, commit `commit_ref:redacted-run-002`.
- `synthetic-block-high-risk-onboarding`: receipt `receipt_ref:redacted-run-003`, policy `policy_ref:redacted-run-001`, config `receipt_cfg_fp:redacted-run-001`, build `build_id:redacted-run-001`, image `image_digest:redacted-run-001`, ledger `ledger_ref:redacted-run-003`, commit `commit_ref:redacted-run-003`.

## Independent verification

Verification is performed independently of the original product response and UI. In the local demo profile, the verifier uses the verification material authorized for that profile. The packet does not claim unrestricted public verification.

Observed verify paths are summarized in [`run_derived/verification_matrix.redacted.json`](run_derived/verification_matrix.redacted.json).

## Negative verification

The pilot executed a real wrong-binding verification. Result: `BUILD_BINDING_MISMATCH` with `ok=False`.

A valid receipt is not enough by itself. The verifier also checks whether the receipt proves the policy and runtime context the reviewer expected.

## Restart-safe verification

The service process was stopped and restarted with the same durable local stores. The pilot then verified by receipt reference only. Result: `verified_after_restart=True`, source `receipt_ref_lookup`.

## What this demonstrates

| Claim | Status | Evidence |
|---|---|---|
| A real AML/KYB-specific receipt was issued | demonstrated_locally | `receipt_index.redacted.json` |
| At least one receipt verified successfully | demonstrated_locally | `verification_matrix.redacted.json` |
| Wrong expected build binding fails verification | demonstrated_locally | `wrong_binding_failures.redacted.json` |
| Receipt verifies after process restart by receipt_ref | demonstrated_locally | `restart_safe_verification.redacted.json` |
| Production HSM deployment | not_claimed | `../production_boundaries.md` |
| Regulatory certification | not_claimed | `../production_boundaries.md` |

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
