# Public Verifier Guide

This guide covers the public Ed25519 verifier for TCD Receipt Profile v0.1. It does not require the private runtime repository and does not read historical run-derived HMAC artifacts.

The fixtures are synthetic test vectors:

- `profile`: `illustrative_public_pilot_profile`
- `signature_algorithm`: `Ed25519`
- `runtime_generated`: `false`
- `synthetic_data`: `true`
- `claim_status`: `illustrative_verifier_test_vector`

The profile is documented in [TCD Receipt Profile v0.1](../specs/tcd-receipt-profile-v0.1.md).

## Setup

From a clean clone:

```bash
git clone https://github.com/amelieliao/tcd-proof-public.git
cd tcd-proof-public
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Verify A Valid Receipt

```bash
python -m tcd_verifier verify \
  --receipt fixtures/verifier_v0_1/valid/receipt.json \
  --public-key fixtures/verifier_v0_1/valid/public-key.pem \
  --expected fixtures/verifier_v0_1/valid/expected-bindings.json \
  --json
```

Expected result:

```json
{
  "ok": true,
  "failure_code": null
}
```

The verifier recomputes the canonical receipt-body bytes, verifies the Ed25519 signature, checks the key identity, and then checks expected policy, build, image, and config bindings.

Before signature verification, the verifier uses strict JSON parsing and the v0.1 JSON Schema. Duplicate JSON keys, malformed JSON, `NaN`, `Infinity`, and `-Infinity` fail before canonicalization. The top-level wrapper, `auth_sig`, and expected binding objects reject unknown fields. Extra signed fixture material must use `receipt_body.extensions`, which is included in the canonical signed bytes.

The v0.1 canonicalization rule is the exact rule defined by this repository: UTF-8, `sort_keys=True`, compact separators, `ensure_ascii=False`, and `allow_nan=False`, with no Unicode normalization. It is not a claim of generic cross-language canonical JSON compatibility. Other implementations should reproduce the v0.1 bytes exactly and validate against the test vectors.

## Verify Expected Failures

Tampered signed field:

```bash
python -m tcd_verifier verify \
  --receipt fixtures/verifier_v0_1/tampered_receipt/receipt.json \
  --public-key fixtures/verifier_v0_1/tampered_receipt/public-key.pem \
  --expected fixtures/verifier_v0_1/tampered_receipt/expected-bindings.json \
  --json
```

Expected failure code: `SIGNATURE_INVALID`.

Wrong expected policy:

```bash
python -m tcd_verifier verify \
  --receipt fixtures/verifier_v0_1/wrong_policy/receipt.json \
  --public-key fixtures/verifier_v0_1/wrong_policy/public-key.pem \
  --expected fixtures/verifier_v0_1/wrong_policy/expected-bindings.json \
  --json
```

Expected failure code: `POLICY_BINDING_MISMATCH`. The receipt signature remains valid; the expected binding is wrong.

Wrong expected build:

```bash
python -m tcd_verifier verify \
  --receipt fixtures/verifier_v0_1/wrong_build/receipt.json \
  --public-key fixtures/verifier_v0_1/wrong_build/public-key.pem \
  --expected fixtures/verifier_v0_1/wrong_build/expected-bindings.json \
  --json
```

Expected failure code: `BUILD_BINDING_MISMATCH`. The receipt signature remains valid; the expected build binding is wrong.

Missing required field:

```bash
python -m tcd_verifier verify \
  --receipt fixtures/verifier_v0_1/missing_required_field/receipt.json \
  --public-key fixtures/verifier_v0_1/missing_required_field/public-key.pem \
  --expected fixtures/verifier_v0_1/missing_required_field/expected-bindings.json \
  --json
```

Expected failure code: `REQUIRED_FIELD_MISSING`.

Unsupported algorithm:

```bash
python -m tcd_verifier verify \
  --receipt fixtures/verifier_v0_1/unsupported_algorithm/receipt.json \
  --public-key fixtures/verifier_v0_1/unsupported_algorithm/public-key.pem \
  --expected fixtures/verifier_v0_1/unsupported_algorithm/expected-bindings.json \
  --json
```

Expected failure code: `UNSUPPORTED_ALGORITHM`.

## Reconciliation

Run the complete synthetic case:

```bash
python -m tcd_verifier reconcile \
  --eligible-actions fixtures/reconciliation/complete/eligible-actions.json \
  --receipt-index fixtures/reconciliation/complete/receipt-index.json \
  --verification-results fixtures/reconciliation/complete/verification-results.json \
  --json
```

Expected result:

```json
{
  "upstream_eligible_actions": 3,
  "receipts_committed": 3,
  "missing": [],
  "complete": true
}
```

Run the missing-receipt case:

```bash
python -m tcd_verifier reconcile \
  --eligible-actions fixtures/reconciliation/missing-receipt/eligible-actions.json \
  --receipt-index fixtures/reconciliation/missing-receipt/receipt-index.json \
  --verification-results fixtures/reconciliation/missing-receipt/verification-results.json \
  --json
```

Expected result:

```json
{
  "receipts_committed": 2,
  "complete": false
}
```

The JSON report lists the missing `upstream_action_id`.

## Run Tests

```bash
pytest tests/test_verifier.py tests/test_reconciliation.py
```

The tests assert:

- valid fixture succeeds;
- tampered fixture fails with `SIGNATURE_INVALID`;
- wrong policy fails with `POLICY_BINDING_MISMATCH`;
- wrong build fails with `BUILD_BINDING_MISMATCH`;
- missing field fails with `REQUIRED_FIELD_MISSING`;
- unsupported algorithm fails with `UNSUPPORTED_ALGORITHM`;
- complete reconciliation succeeds;
- missing, duplicate, orphan, verification-failure, and uncommitted reconciliation cases fail.

## Boundaries

This verifier does not prove AI decision correctness, regulatory compliance, production HSM deployment, hardware-rooted production signing, global consensus, or real-world workflow completeness. It proves that the public fixture contract can be independently verified and that expected binding failures are distinguishable from signature failures.

The public MIT License applies only to files published in this public repository. It does not cover the private core runtime or any unpublished implementation, secrets, runtime artifacts, customer data, raw prompts, raw model answers, or private receipt bodies.
