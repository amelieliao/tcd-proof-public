# Receipt and Evidence Model

This document explains the public receipt and evidence model used by the TCD Proof demo materials.

It is written for reviewers, customers, engineering teams, security teams, compliance teams, model-governance teams, and auditors who want to understand what a TCD Proof receipt represents and how it can be verified.

This public document does **not** include private runtime source code, private policy files, signing keys, HMAC secrets, SQLite databases, raw customer payloads, or unredacted receipt bodies.

## Core idea

TCD Proof turns a selected AI-assisted action into a governed systems event.

Instead of returning only an application log, model score, or internal audit trail, TCD Proof can produce a signed receipt and a durable evidence path that a reviewer can verify outside the original application.

A governed event can bind:

- who or what initiated the action
- which tenant, subject, workflow, or case context was involved
- which policy or policy set applied
- which route and decision were selected
- what final Terminal Contract was resolved
- what receipt was issued
- what evidence was durably committed
- what runtime, build, image, and configuration fingerprints were expected
- whether independent verification succeeded

The goal is not to expose raw customer content. The goal is to make selected high-stakes AI actions externally checkable through bounded, content-agnostic proof material.

## What this model is for

The receipt and evidence model is designed to answer questions such as:

- Was a receipt actually issued?
- Was the receipt signed?
- Was the signature verified?
- Was the receipt bound to the expected policy?
- Was the receipt bound to the expected configuration?
- Was the receipt bound to the expected build and image identity?
- Did the request pass through PolicyStore and SecurityRouter?
- Did the final decision resolve into a Terminal Contract?
- Was the evidence durably committed?
- Did storage-window chain verification pass?
- Could the receipt still be verified after process restart?

## What this model does not claim

The public demo materials do not claim:

- global consensus
- production HSM deployment
- hardware-rooted signing in the public local run
- raw customer-data inspection
- mathematical proof of every possible runtime behavior
- that local HMAC signing is equivalent to production KMS/HSM signing
- that local SQLite persistence is equivalent to production durable storage

The public demo demonstrates a local, test-backed, full-chain governed receipt path using local HMAC signing and local SQLite persistence.

Production deployments can replace local HMAC and SQLite with stronger key-management, storage, coordination, authentication, and hardware-root profiles.

---

# Key concepts

## Governed event

A governed event is a normalized runtime event created from a selected AI-assisted action.

It can include:

- request identity
- tenant identity
- subject identity
- workflow identity
- transport context
- payload digest or content-agnostic evidence reference
- route identity
- decision identity
- policy reference
- policy-set reference
- runtime fingerprints
- receipt reference
- evidence-chain reference

The governed event is the anchor that lets TCD Proof connect AI runtime behavior to policy, receipt, evidence, and verification.

## Receipt

A receipt is a compact verification artifact.

It is intended to prove that a selected governed action passed through a specific control path and produced a specific verification surface.

A receipt can bind:

- request identity
- tenant identity
- subject identity
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
- commit references
- audit references
- receipt configuration fingerprint
- signing-key identity
- signature metadata
- verification status

A receipt should be bounded and content-agnostic. It should not need to carry raw prompts, completions, cookies, auth headers, or customer payloads.

## Receipt reference

A `receipt_ref` is a stable reference to the issued receipt.

In the public redacted examples, receipt references are shortened or replaced with placeholders such as:

```json
{
  "receipt_ref": "<receipt-ref>"
}
```

In a real local run, a receipt reference may be a hash-like value.

The receipt reference is important because it supports by-reference verification and restart-safe lookup.

## Receipt head

The receipt head is a stable digest-like identifier for receipt integrity.

Verification can check that the receipt head, canonical body, and signature agree.

A successful verification report can show:

```json
{
  "head_verified": true,
  "body_canonical_verified": true,
  "integrity_hash_verified": true,
  "integrity_ok": true
}
```

## Canonical receipt body

The canonical receipt body is the normalized body used for integrity and signature verification.

It is not the same thing as a raw application payload. It is a bounded representation of the governed event and its proof bindings.

A successful verification report can show:

```json
{
  "body_canonical_verified": true
}
```

## Signature

A receipt can be signed so that an external verifier can detect tampering.

The public local demo uses local HMAC signing. Production deployments can use stronger signing profiles.

A successful verification report can show:

```json
{
  "signature_verified": true,
  "sig_alg": "hmac-sha256",
  "sig_scheme": "hmac",
  "sig_key_id": "tcd-attestor:hmac:local-full-chain"
}
```

## Verification report

A verification report is an independent check of the receipt material.

It can verify:

- receipt head
- canonical body
- integrity hash
- signature
- signing key allowlist
- policy binding
- configuration binding
- build binding
- image binding
- PQ-required signature path
- evidence-chain window
- restart-safe by-reference lookup

A successful report can show:

```json
{
  "ok": true,
  "reason_code": "OK",
  "signature_verified": true,
  "policy_binding_verified": true,
  "cfg_binding_verified": true,
  "build_binding_verified": true,
  "image_binding_verified": true,
  "pq_signature_ok": true,
  "integrity_ok": true,
  "warnings": []
}
```

## Evidence chain

The evidence chain is the durable storage path for receipt evidence.

A successful local full-chain run validates:

- receipt reference persistence
- evidence-chain commit
- chain head tracking
- storage-window verification
- restart-safe lookup
- anti-fork chain-window checks
- commit receipt presence
- decision receipt presence

A successful storage-window verification can show:

```json
{
  "ok": true,
  "verify_input_source": "evidence_store_window",
  "checked": 2,
  "links_checked": 1,
  "genesis_count": 1,
  "tip_count": 1,
  "latest_matches_expected": true,
  "latest_matches_ledger_ref": true,
  "latest_matches_commit_ref": true,
  "integrity_ok": true
}
```

## Ledger reference

A ledger reference points to the durable chain state or commit state associated with the receipt.

In the redacted public examples, this is represented as:

```json
{
  "ledger_ref": "<ledger-head>"
}
```

A successful run can show that the ledger stage reached `committed`:

```json
{
  "ledger_stage": "committed"
}
```

## Commit reference

A commit reference points to the evidence-chain commit associated with the receipt.

In the redacted public examples, this is represented as:

```json
{
  "commit_ref": "<commit-head>"
}
```

A successful full-chain run should show that a commit receipt exists and that the evidence delivery state is committed.

## Audit reference

An audit reference points to a durable audit event or audit path associated with the governed action.

In the redacted public examples, this is represented as:

```json
{
  "audit_ref": "<audit-ref>"
}
```

The audit reference is separate from raw customer data. It is intended to help reviewers connect the governed event to audit metadata without exposing private payloads.

## Attestation reference

An attestation reference points to the attestation material or attested receipt issuance path.

In the redacted public examples, this is represented as:

```json
{
  "attestation_ref": "<attestation-ref>"
}
```

The public local demo uses local HMAC signing and does not claim production hardware-rooted attestation.

## Terminal Contract

The Terminal Contract is the final enforceable decision output.

It normalizes risk, policy, route, authentication, and security-router signals into an explicit final action.

A representative Terminal Contract can look like:

```json
{
  "decision": "block",
  "allowed": false,
  "required_action": "block",
  "enforcement_mode": "must_enforce"
}
```

The Terminal Contract is important because it gives downstream systems a concrete instruction rather than an ambiguous advisory score.

Typical outcomes include:

- `allow`
- `degrade`
- `block`

The full-chain demo uses a representative request that resolves to:

```json
{
  "decision": "block",
  "allowed": false,
  "required_action": "block"
}
```

## PolicyStore

PolicyStore is the policy-loading and policy-binding component in the full-chain run.

A successful runtime should show that policy storage is enabled:

```json
{
  "policy_store": true
}
```

or:

```json
{
  "has_policy_store": true
}
```

A successful receipt or verification path should bind the governed event to a policy reference, policy-set reference, and/or policy digest.

## SecurityRouter

SecurityRouter is the security orchestration path in the full-chain run.

A successful runtime should show that SecurityRouter is enabled:

```json
{
  "security_router": true
}
```

or:

```json
{
  "has_security_router": true
}
```

A successful full-chain result should show that the receipt surface was produced through the SecurityRouter path rather than a local fallback-only path.

In the redacted summary, this appears as:

```json
{
  "diagnose_security_router_surface": true
}
```

---

# Receipt surfaces

TCD Proof separates receipt views so that public, audit, verification, and internal storage needs do not all share the same data surface.

This separation is important because public proof should be bounded and content-agnostic, while verification may require canonical material that is not intended for broad public display.

## Public receipt surface

The public receipt surface is a bounded view intended for external or customer-facing review.

It should expose enough material to identify and reason about the receipt without exposing raw customer content.

Typical public fields can include:

- `receipt_ref`
- `head`
- `policy_ref`
- `policyset_ref`
- `cfg_fp`
- `event_id`
- `decision_id`
- `route_plan_id`
- `receipt_surface_kind`
- `receipt_delivery_state`
- `ledger_stage`
- `outbox_status`
- `evidence_durable`
- `evidence_storage_ready`
- `integrity_ok`

A successful full-chain run should show that a public receipt surface exists:

```json
{
  "diagnose_has_receipt_public": true
}
```

## Verification receipt surface

The verification surface contains enough material for independent verification.

It can include:

- receipt head
- canonical receipt body
- signature
- verify key or verify key identifier
- signing algorithm
- receipt config fingerprint
- policy binding fields
- build and image binding fields
- PQ-required signature fields
- verification metadata

A successful full-chain run should show that a verification receipt surface exists:

```json
{
  "diagnose_has_receipt_verification": true
}
```

## Audit surface

The audit surface can contain richer operational metadata for authorized reviewers.

It should still avoid exposing raw customer content unless a deployment explicitly permits that under controlled review.

Typical audit-oriented fields can include:

- audit reference
- route identity
- decision identity
- evidence references
- policy references
- enforcement outcome
- reason codes
- delivery state
- storage status
- chain status

## Storage surface

The storage surface is optimized for durable persistence and replay-safe verification.

It can include:

- receipt reference
- receipt head
- chain namespace
- chain id
- chain head
- previous link
- commit reference
- storage timestamp
- verification-relevant digests
- key allowlist status
- integrity status

The public examples do not include raw storage rows or local SQLite files.

---

# What a receipt can bind

A TCD Proof receipt can bind multiple categories of evidence.

## Identity binding

A receipt can bind the governed event to:

- request identity
- tenant identity
- subject identity
- session identity
- workflow identity
- route identity
- decision identity

Example redacted fields:

```json
{
  "tenant": "demo",
  "receipt_ref": "<receipt-ref>",
  "decision": "block",
  "required_action": "block"
}
```

## Policy binding

A policy-bound receipt can show which policy or policy set influenced the Terminal Contract.

Typical fields include:

- `policy_ref`
- `policyset_ref`
- `policy_digest`
- `policy_binding_verified`

A successful verification report can show:

```json
{
  "policy_binding_verified": true
}
```

A redacted summary can show:

```json
{
  "policy_ref": "block_internet_admin@v1#<redacted>",
  "policyset_ref": "set@1#<redacted>"
}
```

## Configuration binding

A receipt can bind runtime and receipt configuration.

Typical fields include:

- service config fingerprint
- route config fingerprint
- receipt config fingerprint
- expected config fingerprint
- config binding verification status

A successful verification report can show:

```json
{
  "cfg_binding_verified": true,
  "service_config_binding_verified": true
}
```

## Build and image binding

The full-chain demo includes supply-chain binding for runtime build and image identity.

A successful verification report can show:

```json
{
  "build_binding_verified": true,
  "image_binding_verified": true
}
```

In the public demo, the `/diagnose` response may not expose build and image fields directly, while the independent verification report still verifies build and image binding.

This can be represented as:

```json
{
  "diagnose_supply_chain_surface_present": false,
  "verify_supply_chain_binding_verified": true
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

## Terminal Contract binding

A receipt can bind the final Terminal Contract.

Typical fields include:

- `decision`
- `allowed`
- `required_action`
- `enforcement_mode`
- `reason_code`

Representative output:

```json
{
  "decision": "block",
  "allowed": false,
  "required_action": "block",
  "enforcement_mode": "must_enforce"
}
```

## Evidence binding

A receipt can bind the governed event to evidence references without carrying raw customer content.

Typical fields include:

- `receipt_ref`
- `audit_ref`
- `ledger_ref`
- `commit_ref`
- `attestation_ref`
- `chain_id`
- `chain_namespace`
- `evidence_durable`
- `evidence_storage_ready`

Representative redacted output:

```json
{
  "receipt_ref": "<receipt-ref>",
  "ledger_ref": "<ledger-head>",
  "commit_ref": "<commit-head>",
  "audit_ref": "<audit-ref>",
  "attestation_ref": "<attestation-ref>",
  "evidence_durable": true,
  "evidence_storage_ready": true
}
```

## Signature binding

A receipt can bind the canonical body to a signing key identity and signature.

A successful verification report can show:

```json
{
  "signature_verified": true,
  "verify_key_allowed": true,
  "key_allowlist_status": "allowed",
  "key_allowlist_enforced": true,
  "sig_key_id": "tcd-attestor:hmac:local-full-chain",
  "sig_alg": "hmac-sha256",
  "sig_scheme": "hmac"
}
```

## PQ-required signature path

The public full-chain demo exercises a PQ-required signature path.

A successful verification report can show:

```json
{
  "pq_required": true,
  "pq_signature_required": true,
  "pq_signature_ok": true
}
```

This field indicates that the receipt path carried a PQ-required requirement and verified the required signature condition for the demo profile.

---

# Evidence-chain verification

Evidence-chain verification checks the durable evidence path rather than only the receipt material.

A storage-window verification can check:

- number of rows checked
- number of links checked
- duplicate count
- fork count
- cycle count
- missing previous links
- bad heads
- bad rows
- genesis count
- tip count
- latest chain head
- expected latest chain head
- expected ledger reference
- expected commit reference
- key allowlist state
- integrity state

A successful storage-window verification can show:

```json
{
  "ok": true,
  "checked": 2,
  "links_checked": 1,
  "duplicates": 0,
  "forks": 0,
  "cycles": 0,
  "missing_prev": 0,
  "bad_heads": 0,
  "bad_rows": 0,
  "genesis_count": 1,
  "tip_count": 1,
  "latest_matches_expected": true,
  "latest_matches_ledger_ref": true,
  "latest_matches_commit_ref": true,
  "integrity_ok": true
}
```

## Why storage-window verification matters

By-ref receipt verification proves that a receipt can be looked up and verified.

Storage-window verification adds a separate check: the durable evidence chain itself is coherent over a bounded window.

This helps reviewers distinguish:

- a valid standalone receipt
- a valid receipt reference lookup
- a durable evidence-chain state
- a restart-safe persisted receipt path

---

# Restart-safe verification

The full-chain demo also verifies that by-reference lookup still works after process restart.

This validates that the receipt reference was not only held in memory.

A successful restart-safe by-ref verification can show:

```json
{
  "verify_after_restart_by_ref_ok": true
}
```

The verification report can show:

```json
{
  "ok": true,
  "verify_input_source": "receipt_ref_lookup",
  "signature_verified": true,
  "integrity_ok": true
}
```

---

# Full-chain demo lifecycle

The public full-chain demo follows this conceptual sequence:

```text
/diagnose request
  -> hardened request envelope
  -> PolicyStore loading
  -> SecurityRouter path
  -> Terminal Contract
  -> signed decision receipt
  -> durable evidence-chain commit
  -> signed commit receipt
  -> by-ref verification
  -> by-bundle verification
  -> top-level receipt verification
  -> storage-window chain verification
  -> process restart
  -> restart-safe by-ref verification
```

## Step 1: Governed request enters the runtime

A selected request enters the HTTP service surface.

The runtime establishes:

- request identity
- tenant identity
- subject identity
- idempotency scope
- bounded request envelope
- route and policy context
- build and image context

## Step 2: Policy and security routing resolve the control path

PolicyStore and SecurityRouter participate in resolving the governed path.

A successful runtime should show:

```json
{
  "policy_store": true,
  "security_router": true
}
```

## Step 3: Terminal Contract is resolved

The system resolves the final enforceable decision.

Representative output:

```json
{
  "decision": "block",
  "allowed": false,
  "required_action": "block"
}
```

## Step 4: Receipt is issued

A signed receipt is issued for the governed event.

Successful receipt issuance can be represented as:

```json
{
  "receipt_issued": true,
  "receipt_ref": "<receipt-ref>"
}
```

## Step 5: Evidence is durably committed

Evidence references and chain state are persisted.

Successful durable commit can show:

```json
{
  "receipt_surface_kind": "durable_committed",
  "receipt_delivery_state": "committed",
  "ledger_stage": "committed",
  "evidence_durable": true,
  "evidence_storage_ready": true
}
```

## Step 6: Receipt is independently verified

Independent verification can happen by:

- receipt reference
- verification bundle
- top-level receipt material
- evidence storage window
- receipt reference after restart

A successful final summary can show:

```json
{
  "verify_by_ref_ok": true,
  "verify_by_bundle_ok": true,
  "verify_top_level_ok": true,
  "verify_storage_window_ok": true,
  "verify_after_restart_by_ref_ok": true
}
```

---

# How to read the redacted summary

The redacted summary file is expected at:

```text
examples/full-chain-receipt-summary.redacted.json
```

The most important top-level field is:

```json
{
  "all_checks_pass": true
}
```

A representative successful summary includes:

```json
{
  "all_checks_pass": true,
  "checks": {
    "runtime_receipts": true,
    "runtime_schema_view_enabled": true,
    "runtime_policy_store_enabled": true,
    "runtime_security_router_enabled": true,
    "runtime_receipt_ref_sqlite": true,
    "runtime_evidence_store_sqlite": true,
    "runtime_evidence_store_durable": true,
    "diagnose_has_receipt_public": true,
    "diagnose_has_receipt_verification": true,
    "diagnose_has_signature": true,
    "diagnose_policy_bound": true,
    "diagnose_supply_chain_bound": true,
    "diagnose_pq_required": true,
    "diagnose_pq_signature_ok": true,
    "diagnose_durable_committed": true,
    "diagnose_commit_receipt": true,
    "diagnose_decision_receipt": true,
    "diagnose_attestation_ref": true,
    "diagnose_audit_ref": true,
    "diagnose_security_router_surface": true,
    "verify_by_ref_ok": true,
    "verify_by_bundle_ok": true,
    "verify_top_level_ok": true,
    "verify_storage_window_ok": true,
    "verify_after_restart_by_ref_ok": true
  }
}
```

## Key checks

| Check | Meaning |
|---|---|
| `runtime_receipts` | Receipt support was enabled at runtime |
| `runtime_schema_view_enabled` | Schema-view receipt projection was enabled |
| `runtime_policy_store_enabled` | PolicyStore was loaded |
| `runtime_security_router_enabled` | SecurityRouter path was enabled |
| `runtime_receipt_ref_sqlite` | Receipt reference lookup used SQLite |
| `runtime_evidence_store_sqlite` | Evidence store used SQLite |
| `runtime_evidence_store_durable` | Evidence store reported durable status |
| `diagnose_has_receipt_public` | `/diagnose` returned a public receipt view |
| `diagnose_has_receipt_verification` | `/diagnose` returned verification material |
| `diagnose_has_signature` | Receipt verification material included signature material |
| `diagnose_policy_bound` | Receipt path included policy binding |
| `diagnose_supply_chain_bound` | Supply-chain binding was proven through diagnose surface or verification reports |
| `diagnose_pq_required` | PQ-required path was active |
| `diagnose_pq_signature_ok` | PQ-required signature path verified |
| `diagnose_durable_committed` | Evidence reached durable committed state |
| `diagnose_commit_receipt` | Commit receipt was present |
| `diagnose_decision_receipt` | Decision receipt was present |
| `diagnose_attestation_ref` | Attestation reference was present |
| `diagnose_audit_ref` | Audit reference was present |
| `diagnose_security_router_surface` | SecurityRouter proof surface was present |
| `verify_by_ref_ok` | Receipt verified by receipt reference |
| `verify_by_bundle_ok` | Receipt verified by verification bundle |
| `verify_top_level_ok` | Receipt verified from top-level material |
| `verify_storage_window_ok` | Evidence chain verified over storage window |
| `verify_after_restart_by_ref_ok` | Receipt reference verified after process restart |

---

# How to read the redacted verification report

The redacted verification report is expected at:

```text
examples/verify-report.redacted.json
```

It shows representative verification outcomes across several verification modes.

## By-reference verification

By-reference verification uses a stored receipt reference.

Expected shape:

```json
{
  "ok": true,
  "verify_input_source": "receipt_ref_lookup",
  "signature_verified": true,
  "policy_binding_verified": true,
  "cfg_binding_verified": true,
  "build_binding_verified": true,
  "image_binding_verified": true,
  "integrity_ok": true
}
```

## By-bundle verification

By-bundle verification uses the verification material returned by the receipt surface.

Expected shape:

```json
{
  "ok": true,
  "verify_input_source": "receipt_verification",
  "signature_verified": true,
  "policy_binding_verified": true,
  "cfg_binding_verified": true,
  "build_binding_verified": true,
  "image_binding_verified": true,
  "integrity_ok": true
}
```

## Top-level receipt verification

Top-level verification uses explicitly supplied receipt head, body, signature, and verification key material.

Expected shape:

```json
{
  "ok": true,
  "verify_input_source": "top_level",
  "signature_verified": true,
  "policy_binding_verified": true,
  "cfg_binding_verified": true,
  "build_binding_verified": true,
  "image_binding_verified": true,
  "integrity_ok": true
}
```

## Storage-window verification

Storage-window verification checks evidence-chain integrity over a bounded window.

Expected shape:

```json
{
  "ok": true,
  "verify_input_source": "evidence_store_window",
  "latest_matches_expected": true,
  "latest_matches_ledger_ref": true,
  "latest_matches_commit_ref": true,
  "integrity_ok": true
}
```

## After-restart by-reference verification

After-restart by-reference verification checks that the receipt reference remains available after process restart.

Expected shape:

```json
{
  "ok": true,
  "verify_input_source": "receipt_ref_lookup",
  "signature_verified": true,
  "integrity_ok": true
}
```

---

# Privacy and redaction model

The public demo materials are intentionally redacted.

## Redacted fields

The public examples may redact:

- full receipt references
- full ledger heads
- full commit heads
- full audit references
- full attestation references
- full policy digests
- full config fingerprints
- full image digests
- local paths
- local process ids
- local database paths
- signing-key material
- HMAC keys
- raw receipt bodies

## Content not included

The public examples should not include:

- raw prompts
- raw completions
- customer documents
- cookies
- auth headers
- access tokens
- API keys
- HMAC secrets
- KMS credentials
- private runtime logs
- local SQLite databases
- private policy files

## Why redaction is acceptable

The purpose of the public demo is to show the receipt and verification model, not to disclose private runtime internals or sensitive workflow data.

For reviewers with appropriate authorization, unredacted artifacts can be provided through a controlled async demo pack or private reviewer bundle.

---

# Local demo profile vs production profile

## Public local demo profile

The public local demo uses:

```json
{
  "signing": "local_hmac_demo",
  "storage": "local_sqlite_demo",
  "hardware_root_required": false,
  "raw_customer_content_included": false
}
```

This profile is useful for:

- local reproducibility
- reviewer understanding
- proof-path demonstration
- receipt verification walkthrough
- evidence-chain validation walkthrough

## Production profile

A production deployment can use stronger profiles such as:

- KMS-backed signing
- HSM-backed signing
- hardware-root key provenance
- stricter authentication
- external durable storage
- coordinated multi-node evidence stores
- stricter policy controls
- stronger runtime and deployment attestation
- operational monitoring and alerting

The public local demo does not claim to be a production HSM or hardware-root deployment.

---

# Relationship to the Quickstart

The Quickstart at:

```text
docs/full-chain-receipt-quickstart.md
```

shows how an authorized reviewer can reproduce the full-chain run locally if they have access to the private runtime or reviewer bundle.

This document explains what the artifacts mean.

Use them together:

- Quickstart: how the local run is executed
- Receipt and Evidence Model: how to interpret the receipt, evidence, and verification output
- Redacted Summary: what a successful final result looks like
- Redacted Verify Report: what independent verification reports look like

---

# Representative final result

A successful full-chain run should produce a summary shaped like:

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
  },
  "verification_summary": {
    "by_ref": true,
    "by_bundle": true,
    "top_level": true,
    "storage_window": true,
    "after_restart_by_ref": true
  }
}
```

The key reviewer takeaway is:

```json
{
  "all_checks_pass": true,
  "signature_verified": true,
  "policy_binding_verified": true,
  "cfg_binding_verified": true,
  "build_binding_verified": true,
  "image_binding_verified": true,
  "evidence_durable": true,
  "ledger_stage": "committed"
}
```

---

# Summary

TCD Proof receipts are intended to make selected AI-assisted actions:

- identity-bound
- policy-bound
- runtime-bound
- config-bound
- build/image-bound
- Terminal Contract-bound
- evidence-backed
- signature-verifiable
- restart-safe
- externally reviewable

The public demo shows this through redacted local artifacts and verification reports while keeping private runtime code, secrets, raw payloads, and unredacted receipt material out of the public repository.