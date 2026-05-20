# Architecture Notes

TCD Proof is a trusted control plane for governed, quantified, and externally verifiable AI inference.

This document explains the public architecture model behind the TCD Proof full-chain receipt demo.

It is written for reviewers, customers, engineering teams, security teams, compliance teams, model-governance teams, and auditors who want to understand how a selected AI-assisted action becomes a verifiable systems event.

This public document does **not** include private runtime source code, private policy files, signing keys, HMAC secrets, SQLite databases, raw customer payloads, or unredacted receipt bodies.

---

# Architecture summary

TCD Proof is organized around three planes plus a governed control-plane mutation loop.

```text
Inference Data Plane
  -> Decision and Policy Plane
  -> Governance and Evidence Plane
  -> External Verification

Governed Mutation Loop
  -> policy reload
  -> config reload
  -> signing-key rotation
  -> verification-key allowlist update
  -> runtime patch gate
  -> rollback or compensation path
```

The core idea is that a selected AI-assisted action should not remain only an application log, a model score, or a prompt-wrapper decision.

Instead, it can become a governed event with:

- request identity
- tenant and subject identity
- policy binding
- route and decision identity
- risk-control state
- Terminal Contract outcome
- signed receipt material
- durable evidence-chain commit
- verification reports
- restart-safe receipt lookup

The public full-chain demo shows this path in a local setting using local HMAC signing and local SQLite persistence.

---

# Public architecture boundary

This public repository contains:

- redacted summaries
- redacted verification reports
- public Quickstart/runbook
- architecture notes
- receipt and evidence explanations

This public repository does **not** contain:

- private TCD runtime source code
- private policy files
- private runtime implementation
- signing keys
- HMAC secrets
- KMS/HSM credentials
- raw prompts
- raw completions
- customer documents
- private SQLite databases
- local audit logs
- unredacted receipt bodies
- unredacted local execution artifacts

The architecture described here is a public explanation of the proof path, not a source-code dump.

---

# High-level flow

A full-chain TCD Proof run follows this conceptual lifecycle:

```text
/diagnose request
  -> hardened request envelope
  -> identity and request context
  -> PolicyStore loading
  -> risk and policy evaluation
  -> SecurityRouter path
  -> Terminal Contract
  -> signed decision receipt
  -> durable evidence-chain commit
  -> signed commit receipt
  -> receipt reference lookup
  -> by-ref verification
  -> by-bundle verification
  -> top-level receipt verification
  -> storage-window chain verification
  -> process restart
  -> restart-safe by-ref verification
```

A successful redacted local run can end with:

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

# Plane 1: Inference Data Plane

The Inference Data Plane is the ingress boundary for governed AI actions.

It receives a request and establishes a bounded event envelope before downstream policy, routing, receipt, or evidence components are allowed to trust the request.

## Responsibilities

The Inference Data Plane is responsible for:

- request identity
- tenant identity
- subject identity
- session identity
- workflow identity
- transport context
- idempotency scope
- request body budget
- request header budget
- rate-limit zone
- payload digest or content-agnostic evidence reference
- strict request envelope
- runtime profile visibility

## Inputs

Representative inputs include:

```json
{
  "tenant": "demo",
  "user": "fullchain_user",
  "session": "fullchain_session",
  "model_id": "model-full-chain",
  "task": "chat",
  "lang": "en",
  "pq_required": true,
  "build_id": "tcd-full-chain-build-<timestamp>",
  "image_digest": "sha256:<redacted>"
}
```

## Output

The output is a governed event with stable identity and content-agnostic anchors.

The event can then be evaluated by the Decision and Policy Plane.

## Why this matters

Without a hardened ingress boundary, later receipt and audit material can become ambiguous.

The receipt should bind to a stable event identity, not to an informal or unbounded request representation.

---

# Plane 2: Decision and Policy Plane

The Decision and Policy Plane turns risk, policy, routing, authentication, and security signals into a final enforceable Terminal Contract.

This plane is where the system moves from “risk interpretation” to “governed action.”

## Responsibilities

The Decision and Policy Plane can include:

- safety detector output
- conservative calibration
- multivariate risk signals
- AlwaysValid Risk Controller state
- policy binding
- policy-set binding
- policy digest
- route identity
- decision identity
- StrategyRouter path
- SecurityRouter path
- Terminal Contract output

## PolicyStore

PolicyStore loads and provides policy material for binding a governed event to policy identity.

A successful full-chain runtime should show:

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

Policy binding can appear as:

```json
{
  "policy_ref": "block_internet_admin@v1#<redacted>",
  "policyset_ref": "set@1#<redacted>"
}
```

A successful verification report can show:

```json
{
  "policy_binding_verified": true
}
```

## SecurityRouter

SecurityRouter is the orchestration path that resolves security-relevant routing and governance conditions.

A successful full-chain runtime should show:

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

A successful full-chain summary can show:

```json
{
  "diagnose_security_router_surface": true
}
```

This means the receipt path was produced through the SecurityRouter surface, not only a local fallback path.

## AlwaysValid Risk Controller

TCD Proof can bind risk-control state rather than only a single static score.

The AlwaysValid Risk Controller can track:

- p-value or calibrated risk signal
- e-process state
- alpha-wealth state
- controller mode
- statistical guarantee scope
- trigger state
- risk-budget semantics

The purpose is to separate the statistical control state from the final business decision.

## Terminal Contract

The Terminal Contract is the final enforceable decision output.

It collapses risk, policy, route, authentication, and security-router signals into a normalized action.

A representative Terminal Contract:

```json
{
  "decision": "block",
  "allowed": false,
  "required_action": "block",
  "enforcement_mode": "must_enforce"
}
```

The Terminal Contract is important because it gives downstream systems an explicit control decision rather than an ambiguous advisory signal.

## Terminal Contract outcomes

Representative outcomes include:

- `allow`
- `degrade`
- `block`

A successful full-chain demo request may resolve to:

```json
{
  "decision": "block",
  "allowed": false,
  "required_action": "block"
}
```

---

# Plane 3: Governance and Evidence Plane

The Governance and Evidence Plane turns the governed decision into verifiable proof material.

It is responsible for receipt issuance, receipt surfaces, attestation references, evidence persistence, ledger/commit references, and independent verification.

## Responsibilities

The Governance and Evidence Plane can include:

- signed receipt issuance
- public receipt surface
- verification receipt surface
- canonical receipt body
- receipt head
- receipt signature
- signing-key identity
- verification-key allowlist status
- durable receipt reference lookup
- durable evidence-chain commit
- decision receipt
- commit receipt
- audit reference
- ledger reference
- commit reference
- attestation reference
- storage-window verification
- restart-safe by-reference verification

## Receipt issuance

A receipt is issued for the governed event.

A successful receipt path can show:

```json
{
  "receipt_issued": true,
  "receipt_ref": "<receipt-ref>"
}
```

## Receipt surfaces

TCD Proof separates receipt views so public, verification, audit, and storage needs do not all share the same data surface.

### Public receipt surface

The public receipt surface is a bounded external view.

It can expose receipt identity and high-level proof state without exposing raw customer content.

A successful full-chain summary can show:

```json
{
  "diagnose_has_receipt_public": true
}
```

### Verification receipt surface

The verification receipt surface contains enough material for independent verification.

A successful full-chain summary can show:

```json
{
  "diagnose_has_receipt_verification": true,
  "diagnose_has_signature": true
}
```

### Audit surface

The audit surface can include richer operational references for authorized review, such as:

- audit reference
- route identity
- decision identity
- policy reference
- enforcement outcome
- storage status
- receipt state
- evidence state

### Storage surface

The storage surface supports durable persistence and replay-safe lookup.

It can include:

- receipt reference
- receipt head
- chain namespace
- chain id
- chain head
- commit reference
- previous link
- integrity state

The public repository does not include local SQLite files or unredacted storage rows.

## Durable evidence commit

A successful full-chain local run should show durable evidence commit state:

```json
{
  "receipt_surface_kind": "durable_committed",
  "receipt_delivery_state": "committed",
  "ledger_stage": "committed",
  "evidence_durable": true,
  "evidence_storage_ready": true
}
```

## Decision receipt and commit receipt

The full-chain path validates that both decision and commit receipt material exists.

A successful summary can show:

```json
{
  "diagnose_decision_receipt": true,
  "diagnose_commit_receipt": true
}
```

This distinguishes the decision proof from the durable commit proof.

## Evidence-chain verification

The evidence chain can be verified over a bounded storage window.

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

## Restart-safe by-reference verification

The full-chain demo verifies that the receipt reference still works after process restart.

A successful final summary can show:

```json
{
  "verify_after_restart_by_ref_ok": true
}
```

A successful after-restart verification report can show:

```json
{
  "ok": true,
  "verify_input_source": "receipt_ref_lookup",
  "signature_verified": true,
  "integrity_ok": true
}
```

---

# Governed Mutation Loop

The Governed Mutation Loop controls changes to the control plane itself.

The purpose is to avoid invisible side effects in high-stakes AI systems.

## Examples of governed mutations

Examples include:

- policy reload
- configuration reload
- signing-key rotation
- verification-key allowlist update
- runtime patch gate
- calibration update
- trust update
- outbox retry
- rollback path
- compensation path

## Why this matters

In governed AI systems, runtime control changes can be as important as inference decisions.

A change to policy, key status, allowlist configuration, or runtime routing can affect whether an AI action is allowed, degraded, blocked, or verifiable.

TCD Proof treats those changes as governed control-plane events rather than invisible operational side effects.

## Mutation-loop evidence

A governed mutation path can produce:

- audit events
- prepare references
- commit references
- rollback references
- compensation references
- key status evidence
- configuration fingerprints
- policy activation references

The public demo focuses on the full-chain receipt path, not a complete production mutation suite.

---

# Verification architecture

TCD Proof supports multiple verification modes.

The public full-chain demo validates:

- by-reference verification
- by-bundle verification
- top-level receipt verification
- storage-window chain verification
- after-restart by-reference verification

## By-reference verification

By-reference verification uses a `receipt_ref`.

Representative successful output:

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

By-bundle verification uses receipt verification material returned by the receipt surface.

Representative successful output:

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

Top-level verification uses directly supplied receipt head, body, signature, and verification key material.

Representative successful output:

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

## Storage-window chain verification

Storage-window verification checks durable chain state over a bounded window.

Representative successful output:

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

After-restart verification confirms that receipt lookup is durable and not only memory-backed.

Representative successful output:

```json
{
  "ok": true,
  "verify_input_source": "receipt_ref_lookup",
  "signature_verified": true,
  "integrity_ok": true
}
```

---

# Supply-chain binding

The full-chain demo includes build and image binding.

A successful verification report can show:

```json
{
  "build_binding_verified": true,
  "image_binding_verified": true
}
```

In some runs, the public `/diagnose` response may not directly expose build and image fields, while independent verification still confirms build and image binding.

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

This distinction is important because a public proof surface may intentionally hide or bound some runtime fields, while the verification report can still validate the expected binding.

---

# PQ-required signature path

The full-chain demo exercises a PQ-required signature path.

A successful verification report can show:

```json
{
  "pq_required": true,
  "pq_signature_required": true,
  "pq_signature_ok": true
}
```

This indicates that the receipt path carried the expected PQ-required condition and that the verification path confirmed it for the demo profile.

---

# Local demo profile

The public full-chain demo uses a local profile:

```json
{
  "signing": "local_hmac_demo",
  "storage": "local_sqlite_demo",
  "hardware_root_required": false,
  "raw_customer_content_included": false
}
```

This local profile is useful for:

- reviewer understanding
- local reproducibility
- proof-path demonstration
- receipt verification walkthrough
- evidence-chain validation walkthrough
- restart-safe lookup validation

## Local demo components

The public local run demonstrates:

- local HMAC receipt signing
- local SQLite receipt reference lookup
- local SQLite evidence-chain commit
- PolicyStore loading
- SecurityRouter path
- schema-view receipt projection
- verification bundle exposure
- build/image binding
- PQ-required signature path
- decision receipt and commit receipt
- by-ref verification
- by-bundle verification
- top-level verification
- storage-window verification
- restart-safe by-ref verification

## Local demo boundaries

The local demo does not claim:

- global consensus
- production HSM deployment
- hardware-rooted production signing
- raw customer-data inspection
- full production deployment equivalence
- formal proof of every runtime behavior

---

# Production deployment profile

Production deployments can replace local demo components with stronger profiles.

Examples include:

- KMS-backed signing
- HSM-backed signing
- hardware-root key provenance
- stronger key rotation controls
- stricter verification-key allowlists
- external durable storage
- coordinated multi-node evidence stores
- stricter authentication
- stricter policy activation controls
- stronger runtime attestation
- operational alerting
- production telemetry
- privacy profile enforcement

A production profile may still preserve the same conceptual flow:

```text
governed request
  -> policy and risk control
  -> Terminal Contract
  -> signed receipt
  -> durable evidence
  -> external verification
```

The difference is that production deployments can strengthen the signing, storage, coordination, and trust-root layers.

---

# Public vs private materials

## Public repository

The public repository contains:

- `README.md`
- `docs/full-chain-receipt-quickstart.md`
- `docs/receipt-and-evidence-model.md`
- `docs/architecture-notes.md`
- `examples/full-chain-receipt-summary.redacted.json`
- `examples/verify-report.redacted.json`

These files are designed for public review.

## Private runtime repository

The private runtime repository can contain:

- implementation code
- private policies
- runtime integrations
- storage implementation
- signing implementation
- internal tests
- full unredacted local artifacts
- private operational logs
- reviewer-bundle generation tools

The public repository intentionally does not include those materials.

---

# Reviewer checklist

A reviewer reading the public demo materials should look for the following indicators.

## Runtime readiness

```json
{
  "runtime_receipts": true,
  "runtime_policy_store_enabled": true,
  "runtime_security_router_enabled": true,
  "runtime_receipt_ref_sqlite": true,
  "runtime_evidence_store_sqlite": true,
  "runtime_evidence_store_durable": true
}
```

## Receipt issuance

```json
{
  "diagnose_has_receipt_public": true,
  "diagnose_has_receipt_verification": true,
  "diagnose_has_signature": true
}
```

## Policy and Terminal Contract

```json
{
  "diagnose_policy_bound": true,
  "decision": "block",
  "allowed": false,
  "required_action": "block"
}
```

## Durable evidence

```json
{
  "receipt_surface_kind": "durable_committed",
  "receipt_delivery_state": "committed",
  "ledger_stage": "committed",
  "evidence_durable": true,
  "evidence_storage_ready": true
}
```

## Verification

```json
{
  "verify_by_ref_ok": true,
  "verify_by_bundle_ok": true,
  "verify_top_level_ok": true,
  "verify_storage_window_ok": true,
  "verify_after_restart_by_ref_ok": true
}
```

## Binding verification

```json
{
  "signature_verified": true,
  "policy_binding_verified": true,
  "cfg_binding_verified": true,
  "build_binding_verified": true,
  "image_binding_verified": true
}
```

## Final result

```json
{
  "all_checks_pass": true
}
```

---

# Architecture diagram

A compact view of the full-chain architecture:

```text
┌─────────────────────────────────────────────────────────────────┐
│                        Inference Data Plane                      │
│                                                                 │
│  request envelope                                                │
│  tenant / subject / session identity                             │
│  transport context                                                │
│  idempotency scope                                                │
│  body and header budgets                                          │
│  payload digest or content-agnostic evidence anchor               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Decision and Policy Plane                   │
│                                                                 │
│  PolicyStore                                                     │
│  detector and calibration signals                                │
│  AlwaysValid Risk Controller                                     │
│  StrategyRouter                                                  │
│  SecurityRouter                                                  │
│  route identity                                                  │
│  decision identity                                               │
│  Terminal Contract                                               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Governance and Evidence Plane                 │
│                                                                 │
│  signed receipt                                                  │
│  public receipt surface                                          │
│  verification receipt surface                                    │
│  decision receipt                                                │
│  commit receipt                                                  │
│  durable receipt_ref lookup                                      │
│  durable evidence-chain commit                                   │
│  ledger / audit / attestation refs                               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       External Verification                      │
│                                                                 │
│  by-ref verification                                             │
│  by-bundle verification                                          │
│  top-level receipt verification                                  │
│  storage-window chain verification                               │
│  restart-safe by-ref verification                                │
└─────────────────────────────────────────────────────────────────┘

             Governed Mutation Loop:
             policy reload / config reload / key rotation /
             allowlist update / runtime patch gate /
             rollback / compensation / audit
```

---

# Relationship to other public files

Use this document together with:

- `docs/full-chain-receipt-quickstart.md`
- `docs/receipt-and-evidence-model.md`
- `examples/full-chain-receipt-summary.redacted.json`
- `examples/verify-report.redacted.json`

Suggested reading order:

1. `README.md`
2. `docs/architecture-notes.md`
3. `docs/receipt-and-evidence-model.md`
4. `examples/full-chain-receipt-summary.redacted.json`
5. `examples/verify-report.redacted.json`
6. `docs/full-chain-receipt-quickstart.md`

---

# Summary

TCD Proof is designed around a governed proof path:

```text
AI-assisted action
  -> governed event
  -> policy and risk control
  -> Terminal Contract
  -> signed receipt
  -> durable evidence
  -> independent verification
```

The public full-chain demo shows that a selected AI-assisted action can be represented as a verifiable systems event with:

- identity binding
- policy binding
- configuration binding
- build/image binding
- Terminal Contract resolution
- signed receipt issuance
- durable evidence-chain commit
- by-reference verification
- by-bundle verification
- top-level verification
- storage-window verification
- restart-safe lookup

The public demo uses local HMAC signing and local SQLite persistence. Production deployments can strengthen the same architecture with KMS/HSM-backed signing, hardware-root key provenance, external durable storage, stricter authentication, and coordinated multi-node evidence profiles.