# TCD Proof Public Demo

TCD Proof shows how selected AI-assisted actions can produce signed, reviewable receipts. This public repository contains synthetic and redacted materials that demonstrate the receipt contract, independent verification, and completeness reconciliation without exposing raw customer data. The public Ed25519 verifier fixtures are illustrative pilot test vectors; the historical AML/KYB run-derived artifacts are local-runtime HMAC artifacts. Those two tracks are intentionally separate and should not be mixed.

This repository does not include private runtime source code, signing secrets, raw prompts, raw model answers, customer payloads, databases, logs, or unredacted runtime artifacts.

Product overview: TCD Proof is an action-assurance layer for AI-assisted workflows. It is meant to help a buyer, reviewer, auditor, or governance team answer a narrow question later: was this selected action governed by the expected policy and runtime context, and can that proof be checked without replaying the original product UI or exposing raw case data?

## Start Here

1. [Run the public Ed25519 verifier](#1-run-the-public-ed25519-verifier)
2. [Run completeness reconciliation](#2-run-completeness-reconciliation)
3. [Inspect historical run-derived HMAC evidence](#3-inspect-historical-run-derived-hmac-evidence)
4. [Understand the authorized private runtime path](#4-authorized-private-runtime-path)

Buyer-facing demo index:

- [Demo index](docs/demo-index.md)
- [Customer discovery one-pager](docs/customer-discovery-one-pager.md)
- [AML/KYB alert review demo](demos/aml_kyb_alert_review/)

Pilot assurance materials:

- [AML/KYB Action Assurance Profile v0.1](specs/aml-kyb-action-assurance-profile-v0.1.md)
- [OSFI E-23 & Customer Assurance Mapping](docs/osfi-e23-customer-assurance-mapping.md)
- [Pilot Acceptance Scorecard](docs/pilot-acceptance-scorecard.md)

Draft/pilot materials for scoping, reviewer evidence mapping, and acceptance measurement; they support evidence review and do not claim regulatory compliance.

## 1. Run The Public Ed25519 Verifier

The public verifier is a clean-room Python verifier for `illustrative_public_pilot_profile` fixtures. It recomputes canonical signed bytes, verifies the Ed25519 signature, checks key ID and public-key fingerprint, and compares policy, build, image, and config bindings against expected values.

From a clean clone:

```bash
git clone https://github.com/amelieliao/tcd-proof-public.git
cd tcd-proof-public
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Verify the valid fixture:

```bash
python -m tcd_verifier verify \
  --receipt fixtures/verifier_v0_1/valid/receipt.json \
  --public-key fixtures/verifier_v0_1/valid/public-key.pem \
  --expected fixtures/verifier_v0_1/valid/expected-bindings.json
```

Inspect the JSON report:

```bash
python -m tcd_verifier verify \
  --receipt fixtures/verifier_v0_1/valid/receipt.json \
  --public-key fixtures/verifier_v0_1/valid/public-key.pem \
  --expected fixtures/verifier_v0_1/valid/expected-bindings.json \
  --json
```

Run the verifier tests:

```bash
pytest tests/test_verifier.py
```

The negative fixtures prove different failure modes:

| Fixture | Expected result |
|---|---|
| `tampered_receipt` | `SIGNATURE_INVALID` |
| `wrong_policy` | `POLICY_BINDING_MISMATCH` with a valid signature |
| `wrong_build` | `BUILD_BINDING_MISMATCH` with a valid signature |
| `missing_required_field` | `REQUIRED_FIELD_MISSING` |
| `unsupported_algorithm` | `UNSUPPORTED_ALGORITHM` |

Profile specification and schema:

- [TCD Receipt Profile v0.1](specs/tcd-receipt-profile-v0.1.md)
- [TCD Receipt Profile v0.1 JSON Schema](schemas/tcd-receipt-profile-v0.1.schema.json)
- [Public verifier guide](docs/public-verifier.md)
- [Test-vector bundle manifest](fixtures/test-vector-bundle-manifest.json)

## 2. Run Completeness Reconciliation

The reconciliation demo compares an independent upstream eligible-action population with receipt index rows and verification results. It demonstrates the mechanism for finding missing receipts, duplicate receipts, orphan receipts, failed verifications, human overrides, and uncommitted receipts.

Run the complete case:

```bash
python -m tcd_verifier reconcile \
  --eligible-actions fixtures/reconciliation/complete/eligible-actions.json \
  --receipt-index fixtures/reconciliation/complete/receipt-index.json \
  --verification-results fixtures/reconciliation/complete/verification-results.json
```

Run the missing-receipt case and expect a nonzero exit:

```bash
python -m tcd_verifier reconcile \
  --eligible-actions fixtures/reconciliation/missing-receipt/eligible-actions.json \
  --receipt-index fixtures/reconciliation/missing-receipt/receipt-index.json \
  --verification-results fixtures/reconciliation/missing-receipt/verification-results.json \
  --json
```

Run the reconciliation tests:

```bash
pytest tests/test_reconciliation.py
```

This synthetic reconciliation demo proves the reconciliation mechanism. It does not prove that a real customer workflow has no silent gaps.

## 3. Inspect Historical Run-Derived HMAC Evidence

The AML/KYB alert review demo includes historical run-derived artifacts from an authorized local runtime run using local HMAC signing and local SQLite persistence. These artifacts are redacted and provenance-labeled. They are useful for inspecting the shape of a governed action-assurance run, but they are not the same as the public Ed25519 verifier fixtures above.

Open the AML/KYB demo:

```bash
python3 -m json.tool demos/aml_kyb_alert_review/run_derived/pilot_summary.redacted.json
python3 -m json.tool demos/aml_kyb_alert_review/run_derived/verification_matrix.redacted.json
python3 demos/aml_kyb_alert_review/tools/check_demo_acceptance.py --public-root .
```

Key AML/KYB demo files:

- [AML/KYB overview](demos/aml_kyb_alert_review/README.md)
- [AML/KYB walkthrough](demos/aml_kyb_alert_review/demo_walkthrough.md)
- [Assurance packet](demos/aml_kyb_alert_review/assurance_packet.md)
- [Integration gap report](demos/aml_kyb_alert_review/integration_gap_report.md)
- [Run-derived artifact notes](demos/aml_kyb_alert_review/run_derived/README.md)

## Independent Verification Paths

| Path | What it demonstrates |
|---|---|
| Public Ed25519 verifier | A synthetic public receipt fixture can be checked independently against expected bindings. |
| Wrong expected binding | A valid signature can still fail when the reviewer supplies the wrong policy, build, image, or config expectation. |
| Reconciliation | An independent eligible-action population can be compared with receipt and verification coverage. |
| Historical run-derived HMAC evidence | Authorized local-runtime HMAC artifacts can be inspected as redacted evidence of the historical demo run shape. |
| Authorized private runtime path | Reviewers with private runtime access can reproduce the local full-chain path described in the runbook. |

## 4. Authorized Private Runtime Path

The public repository alone cannot run the private TCD runtime. Authorized reviewers with access to a private runtime repository or reviewer bundle can use the local runbook:

- [Full-chain receipt Quickstart](docs/full-chain-receipt-quickstart.md)

Use a placeholder such as `<authorized-runtime-repo>` for the private runtime location. Do not commit local `env.sh` files, SQLite databases, logs, raw runtime outputs, private paths, or unredacted receipt bodies to this public repository.

The current private runtime has not been integrated with the new public Ed25519 profile. The Ed25519 fixtures are illustrative public pilot vectors; the historical run-derived artifacts are HMAC-based local runtime evidence.

## What This Proves

- A selected AI-assisted action can produce a signed receipt.
- A receipt can bind policy, config, build/image identity, evidence references, and verification status.
- An independent verifier can check a public Ed25519 receipt fixture without reading private runtime code.
- Wrong expected policy or build bindings fail even when the receipt signature is valid.
- A completeness mechanism can compare upstream eligible actions with receipt and verification coverage.

## What This Does Not Claim

- production HSM deployment;
- production hardware-root trust;
- global consensus;
- a real AML model;
- real regulated customer data;
- regulatory certification;
- proof that the AI model is always correct;
- proof that a real customer environment has no silent gaps;
- current private runtime integration for the Ed25519 public profile.

## License Boundary

This repository uses the MIT License with copyright held by Amelie Liao. MIT applies only to code, documentation, schemas, and synthetic fixtures actually published in this public repository. It does not cover the private TCD core runtime, unpublished implementation details, secrets, runtime artifacts, customer data, raw prompts, raw model answers, or private receipt bodies.

## Repository Layout

```text
tcd-proof-public/
  README.md
  docs/
    public-verifier.md
    demo-index.md
    customer-discovery-one-pager.md
    full-chain-receipt-quickstart.md
    receipt-and-evidence-model.md
    architecture-notes.md
  specs/
    tcd-receipt-profile-v0.1.md
  schemas/
    tcd-receipt-profile-v0.1.schema.json
  src/tcd_verifier/
  tests/
  fixtures/
    verifier_v0_1/
    reconciliation/
  examples/
  demos/
    aml_kyb_alert_review/
```

## Run All Public Checks

```bash
python -m pip install -e ".[dev]"
pytest
python3 demos/aml_kyb_alert_review/tools/validate_public_export.py --demo-root demos/aml_kyb_alert_review
python3 demos/aml_kyb_alert_review/tools/check_demo_acceptance.py --public-root .
```

## License And Security

- [License](LICENSE)
- [Security policy](SECURITY.md)

## Contact

```text
aliao@tcdproof.com
https://tcdproof.com
```
