# TCD AML/KYB Action Assurance Profile v0.1

Status: Draft / Pilot

Profile version: `0.1`

Base profile: [TCD Receipt Profile v0.1](tcd-receipt-profile-v0.1.md)

This profile defines a pilot contract for selected AML/KYB action-assurance workflows. It extends the base receipt profile conceptually for domain use, while preserving a clear boundary between normative profile requirements, illustrative public Ed25519 pilot vectors, historical runtime-derived HMAC evidence, and future production requirements.

The current public Ed25519 fixtures are illustrative public pilot vectors. They are not private runtime output. The historical AML/KYB artifacts are runtime-derived, HMAC-SHA256, local SQLite, synthetic/redacted evidence from an authorized local run; they are not unrestricted public-verifiable Ed25519 receipts. The current private runtime is not yet integrated with the public Ed25519 profile. Current reconciliation fixtures demonstrate the mechanism, not the absence of silent gaps in a real customer workflow.

## Status and Scope

Intended audience:

- AML/KYB product teams;
- financial-crime SaaS vendors;
- compliance and model-risk reviewers;
- pilot evaluators.

Intended workflows:

- alert review and alert triage;
- investigation assistance;
- KYB onboarding;
- sanctions review;
- hold, block, and escalation decisions;
- human approval and override workflows.

Out of scope:

- proving the correctness of the underlying model;
- replacing the policy owner;
- replacing the human reviewer;
- regulatory certification;
- full governance of every model interaction;
- storing raw case content in a receipt.

## Conformance Language

The keywords `MUST`, `MUST NOT`, `SHOULD`, and `MAY` describe normative requirements for this draft pilot profile.

They do not mean every requirement is implemented by the current public schema, public verifier, or private runtime. Where a requirement is not implemented, this document marks it as `Proposed extension -- not implemented in the current public schema/runtime`.

## Eligible Action Definition

An eligible action is a selected workflow action that falls inside pilot scope before any receipt is considered. Eligibility MUST NOT be defined as "actions that already have receipts."

Eligibility MUST be determined by scope rules agreed before the pilot starts. It MUST be possible to identify the eligible population before checking the receipt index. The eligible population MUST come from an upstream manifest or system-of-record export independent of the receipt index.

Each eligible action MUST have a stable and unique `upstream_action_id`. In the current public reconciliation fixtures this field exists in `actions[].upstream_action_id`. For a production AML/KYB pilot, stability of this ID is a customer workflow integration requirement.

Eligibility SHOULD consider:

- workflow name;
- action type;
- agreed risk or impact threshold;
- tenant or pilot scope;
- time window;
- inclusion or exclusion reason.

Treatment rules:

- Excluded actions SHOULD appear in the upstream source with `eligible: false` and an exclusion reason, or in a separate exclusion log controlled by the pilot owner.
- Out-of-scope actions MUST NOT be counted as missing receipts.
- Duplicate `upstream_action_id` values MUST fail reconciliation or produce an explicit exception.
- Cancelled actions SHOULD preserve the original upstream ID and record terminal state as cancelled; the cancellation reason MUST NOT expose raw case content.
- Retried actions SHOULD preserve the stable upstream action ID and add execution-attempt references. If multiple executions are allowed for one action, the receipt mapping rule MUST define which execution is terminal.
- Idempotent retries SHOULD map to one terminal receipt for the action; duplicate terminal receipts MUST be reported.
- The eligible-action manifest MUST NOT include raw case data, raw documents, raw prompts, raw model answers, signing secrets, or private local paths.

**Proposed pilot manifest shape -- not the current public reconciliation fixture schema.**
This example illustrates additional fields that a future customer pilot manifest may carry. The current public reconciliation fixtures and CLI do not validate or consume all fields shown below. At present, the implemented public reconciliation contract uses the fields demonstrated by the versioned fixtures, including `actions[].upstream_action_id`, `actions[].scenario_id`, and `actions[].eligible`. Extended scope, threshold, tenant, and idempotency references remain proposed pilot-contract fields until a versioned schema and implementation explicitly support them.

Synthetic eligible-action manifest example:

```json
{
  "schema": "tcd.eligible_actions.aml_kyb.v0.1",
  "profile_version": "0.1",
  "synthetic_data": true,
  "pilot_scope_ref": "pilot-scope:example-aml-kyb-v0.1",
  "time_window": {
    "start": "2026-01-01T00:00:00Z",
    "end": "2026-01-31T23:59:59Z"
  },
  "actions": [
    {
      "upstream_action_id": "act_synthetic_001",
      "scenario_id": "aml_kyb_synthetic_hold_001",
      "eligible": true,
      "workflow": "aml_kyb_alert_review",
      "action_type": "hold_for_edd",
      "risk_threshold_ref": "risk-threshold:pilot-high-impact",
      "tenant_scope_ref": "tenant-scope:pilot-redacted",
      "inclusion_reason": "in_scope_action_type_and_time_window",
      "idempotency_key_ref": "idem-ref:synthetic-001",
      "raw_case_data_included": false
    }
  ]
}
```

Fields that are not accepted or consumed by the current versioned implementation/schema MUST NOT be described as currently enforced by the verifier or reconciliation CLI. If these fields become mandatory normative fields in a future pilot, they will need a new versioned schema/profile contract and corresponding tests.

## Action Taxonomy

The profile separates action semantics instead of collapsing them into one generic decision field.

| Concept | Meaning | Current field or status |
|---|---|---|
| Proposed action | The model- or assistant-suggested next step before governance is applied. | Proposed extension -- not implemented in the current public schema/runtime |
| Governed/required action | The action required by policy or procedure after governance checks. | Proposed extension -- not implemented in the current public schema/runtime |
| Terminal outcome | The final state recorded for the selected action. | `receipt_body.claims.decision_outcome` in the current public schema |
| Downstream business consequence | Business effect such as account hold, onboarding block, or escalation queue placement. | Proposed extension -- not implemented in the current public schema/runtime |
| Human disposition | Human approval, rejection, override, timeout, or unavailable state. | Partly represented by `receipt_body.claims.human_review_state`; detailed states are proposed extensions |

Action categories:

- alert clear or close recommendation;
- hold for enhanced due diligence;
- onboarding block;
- sanctions escalation;
- investigation escalation;
- human approval;
- human rejection;
- override;
- policy, config, or model change affecting a selected action.

## Mandatory Receipt Fields

The table below aligns AML/KYB semantic requirements with the current base public schema where possible. Missing domain fields are intentionally marked as proposed extensions rather than treated as implemented.

| Semantic requirement | Existing public field/path | Required status | Purpose | Data-minimization rule | Current implementation status |
|---|---|---|---|---|---|
| Receipt/profile version | `schema`, `profile`, `profile_version`, `receipt_body.v`, `receipt_body.schema` | MUST | Bind the artifact to the verifier contract. | No case data. | Implemented in public schema and verifier. |
| Receipt/event identity | `receipt_ref`, `receipt_body.claims.event_id` | MUST | Identify the receipt and event being verified. | Use opaque IDs. | Implemented in public schema. |
| Upstream eligible-action identity | `receipt_body.claims.upstream_action_id` | MUST | Reconcile a receipt to an independently known eligible action. | Use stable opaque ID. | Implemented in public schema and reconciliation fixtures. |
| Scenario identity | `receipt_body.claims.scenario_id` | MUST for public fixtures | Link synthetic scenario and reconciliation inputs. | Synthetic or redacted ID only. | Implemented in public schema. |
| Tenant/workflow/action type | `receipt_body.claims.action_type`; tenant is not present | SHOULD for workflow, MUST for pilot scoping | Separate AML/KYB workflow and action category. | Tenant should be bounded or redacted. | `action_type` implemented; tenant is a proposed extension. |
| Timestamps | `receipt_body.ts_ns` | MUST | Establish receipt issuance ordering context. | Timestamp only; no raw event payload. | Implemented in public schema. |
| Policy reference/version/digest | `receipt_body.claims.policy_ref`, `receipt_body.claims.policy_digest` | MUST | Bind action to stated policy context. | Use reference and digest, not policy body if sensitive. | Implemented in public schema and expected bindings. |
| Build/image/config identity or digest | `receipt_body.claims.build_id`, `receipt_body.claims.image_digest`, `receipt_body.claims.cfg_fp` | MUST | Bind action to runtime or fixture context. | Use IDs and digests. | Implemented in public schema and expected bindings. |
| Model/config identity where applicable | None dedicated; `cfg_fp` may cover config | SHOULD for AML/KYB pilots | Identify model or model config used for the selected action. | Use version IDs/digests only. | Proposed extension -- not implemented in the current public schema/runtime. |
| Proposed action | None dedicated | SHOULD for AML/KYB pilots | Preserve assistant recommendation separately from governed outcome. | Use controlled enum or redacted code. | Proposed extension -- not implemented in the current public schema/runtime. |
| Governed/terminal outcome | `receipt_body.claims.decision_outcome`, optional `receipt_body.comp.decision_outcome` | MUST | Record final action state. | Controlled value; no notes. | Implemented for generic outcome. |
| Human-review state | `receipt_body.claims.human_review_state` | SHOULD in current schema, MUST when human review applies | Show whether review was required, requested, or completed. | Role/state only; no names or notes. | Implemented as a string field; detailed states are proposed extensions. |
| Approval/override state | None dedicated | MUST when approval or override applies | Link override or approval to authorization evidence. | Role, reason code, reference only. | Proposed extension -- not implemented in the current public schema/runtime. |
| Evidence references | `receipt_body.e.refs[]`, `receipt_body.claims.evidence_set_ref` | SHOULD, MUST when evidence exists | Bind supporting evidence without exposing contents. | Hashes, digests, bounded references, redacted identifiers. | Implemented in public schema. |
| Signature algorithm | `receipt_body.auth_sig.alg` | MUST | Identify verification algorithm. | Algorithm name only. | Implemented; public profile requires Ed25519. |
| Key identity | `receipt_body.auth_sig.key_id` | MUST | Bind signature to expected key context. | Key ID only, no private material. | Implemented. |
| Public-key fingerprint | `receipt_body.auth_sig.public_key_fingerprint` | MUST for Ed25519 public profile | Bind receipt to verifier-supplied public key. | Fingerprint only. | Implemented. |
| Commit/durability state | None in public receipt schema; reconciliation fixture has `issued`, `committed` | MUST for production pilot completeness | Distinguish issued from durable committed receipts. | State booleans only. | Proposed extension for receipt; demonstrated in synthetic reconciliation fixtures and historical HMAC evidence. |
| Verification status/reference | Verification report outside receipt | MUST for reconciliation | Show recomputed verification result. | Machine-readable result, no raw case content. | Implemented as verifier report, not as signed receipt field. |
| Chain/parent reference | `receipt_body.witness.restart_safe_reference` is present; no parent-chain field | SHOULD where supported | Support by-reference or chain verification. | Reference only. | Partial public support; richer parent reference is a proposed extension. |

Raw prompts, raw completions, raw documents, full customer payloads, signing secrets, private keys, private local paths, SQLite files, logs, and unredacted receipt bodies MUST NOT enter public receipts.

## Optional Fields

| Optional field | Privacy limit | Current implementation status |
|---|---|---|
| Reviewer role | Role or group only; no personal identity unless institution explicitly approves. | Proposed extension -- not implemented in the current public schema/runtime |
| Override reason code | Controlled code, no free-form notes. | Proposed extension -- not implemented in the current public schema/runtime |
| Approval reference | Opaque approval record reference only. | Proposed extension -- not implemented in the current public schema/runtime |
| Redacted external case reference | Bounded reference approved by customer data policy. | Proposed extension -- not implemented in the current public schema/runtime |
| Sanctions-list/config version | Version ID or digest only. | Proposed extension -- not implemented in the current public schema/runtime |
| Model version/config digest | Version ID and digest only. | Proposed extension -- not implemented in the current public schema/runtime |
| Review SLA timestamps | Timestamp fields only; no reviewer notes. | Proposed extension -- not implemented in the current public schema/runtime |
| Evidence package reference | Content-addressed or redacted reference. | Partly supported through `receipt_body.e.refs[]`; package-level semantics are proposed. |
| Customer questionnaire/control reference | Reference to public-safe control answer or attestation. | Proposed extension -- not implemented in the current public schema/runtime |

## Human Approval and Override Semantics

Human disposition states:

- `no_human_review_required`: policy did not require a human reviewer for the selected action.
- `human_review_requested`: review was required or requested, but final disposition is not yet present.
- `approved`: authorized reviewer approved the governed action.
- `rejected`: authorized reviewer rejected the proposed or governed action.
- `overridden`: authorized actor changed the governed path under an allowed exception process.
- `override_revoked_or_superseded`: a prior override no longer controls the terminal state.
- `reviewer_unavailable_or_timeout`: review was not completed inside the required window.
- `approval_record_missing`: the receipt or reconciliation inputs cannot link the action to required approval evidence.

An override does not automatically represent failure. It is a governed exception state that MUST be linked to the action, actor role, timestamp, reason code, and authorization evidence. Public-safe artifacts MUST NOT expose personal identity, raw reviewer notes, raw documents, or raw case payloads.

Unauthorized, unexplained, or unlinked overrides MUST fail verification or reconciliation, or produce a clear exception that prevents `complete=true`.

## Policy, Config, and Model Update Semantics

| Change event | Required for pilot | Currently evidenced | Gap |
|---|---|---|---|
| Policy version change before action | Expected policy reference and digest must match the receipt. | Public verifier checks `policy_ref` and `policy_digest`. | Customer integration must provide authoritative expected bindings. |
| Policy digest mismatch | Verifier must return policy binding failure. | Public wrong-policy fixture covers this class. | None for illustrative profile; production expected-binding source remains a pilot requirement. |
| Configuration update before action | Expected `cfg_fp` or config digest must match receipt. | Public verifier checks `cfg_fp`. | Rich config provenance is proposed. |
| Model version/config update before action | Model version or model config digest should be bound. | Not evidenced as dedicated field. | Proposed extension -- not implemented in the current public schema/runtime. |
| Build/image change before action | Expected build and image digests must match receipt. | Public verifier checks `build_id` and `image_digest`. | Production build/image source of truth remains a pilot requirement. |
| Change during action | Receipt should identify the binding active for the terminal action. | Not specifically evidenced. | Requires workflow integration and timestamp semantics. |
| Stale expected binding | Verification should fail with a binding mismatch or explicit stale-binding exception. | Wrong-policy and wrong-build public vectors demonstrate mismatch handling. | Dedicated stale-version code is proposed. |
| Unsupported or missing version | Verifier should fail closed. | Public verifier returns unsupported profile or required-field failure. | Domain-specific model version rules are proposed. |

## Verification Procedure

For the public Ed25519 pilot profile, a verifier SHOULD:

1. Parse JSON using strict rules.
2. Reject duplicate keys and non-finite values.
3. Validate the applicable schema/profile.
4. Identify the supported algorithm and key.
5. Remove the full `auth_sig` object and reconstruct canonical signed bytes using the base profile v0.1 rules.
6. Verify the Ed25519 signature for the public pilot profile.
7. Verify key ID and public-key fingerprint.
8. Verify expected policy, build, image, config, and model bindings where applicable.
9. Verify action and eligible-action identity.
10. Verify issued, committed, and durable state where that state is available.
11. Verify chain or parent relationship where supported.
12. Return explicit machine-readable pass/failure codes.

Historical HMAC evidence MUST NOT be described as unrestricted third-party public Ed25519 verification. It is runtime-derived local evidence for the historical AML/KYB demo path.

## Completeness and Reconciliation Procedure

Inputs:

- input A: independent eligible-action manifest;
- input B: receipt index;
- input C: recomputed verification results;
- optional input D: commit/durability results.

Algorithm:

1. Parse all inputs strictly.
2. Validate each input shape and ID field.
3. Count eligible actions from input A without silently collapsing duplicates.
4. Count receipt refs and action-to-receipt mappings from input B.
5. Count recomputed verification results from input C.
6. Detect duplicate eligible IDs, duplicate receipt refs, duplicate mappings, missing receipts, orphan receipts, issued-but-uncommitted receipts, verification failures, unsupported versions, unauthorized overrides, and eligible actions with no terminal state.
7. Recompute all counts from input rows. Do not trust input summary totals.
8. Set `complete=true` only when every eligible action has exactly one allowed valid receipt mapping, every expected receipt is issued and committed, every expected receipt has a successful recomputed verification result, and no blocking duplicate, orphan, missing, uncommitted, unsupported, unauthorized, or terminal-state exception exists.

Human overrides are counted separately and do not automatically fail completeness. Unauthorized, unexplained, or unlinked overrides are blocking exceptions.

Real-world completeness depends on the independence and integrity of the upstream eligible-action source. The current synthetic reconciliation fixtures demonstrate the mechanism, not the absence of silent gaps in a real customer workflow.

Synthetic reconciliation report example:

```json
{
  "synthetic_data": true,
  "eligible_actions_observed": 3,
  "receipts_issued": 3,
  "receipts_committed": 3,
  "successfully_verified": 3,
  "missing": 0,
  "orphaned": 0,
  "duplicate_eligible_ids": 0,
  "duplicate_receipt_refs": 0,
  "verification_failures": 0,
  "issued_but_uncommitted": 0,
  "human_overrides": 1,
  "unauthorized_unexplained_overrides": 0,
  "complete": true
}
```

## Failure Cases

| Failure case | Condition | Expected result | Type | Expected evidence/report field |
|---|---|---|---|---|
| Malformed JSON | Input is not valid UTF-8 JSON. | Reject before verification. | Hard failure | `INVALID_JSON` |
| Duplicate JSON keys | Same object has repeated key. | Reject before canonicalization. | Hard failure | `DUPLICATE_JSON_KEY` |
| NaN/Infinity | Non-finite JSON value appears. | Reject before canonicalization. | Hard failure | `NON_FINITE_JSON_NUMBER` |
| Schema failure | Receipt violates schema. | Reject before signature verification. | Hard failure | `SCHEMA_INVALID` |
| Missing mandatory field | Required base or pilot field missing. | Reject. | Hard failure | `REQUIRED_FIELD_MISSING` |
| Unsupported profile/version | Unknown profile or version. | Fail closed. | Hard failure | `UNSUPPORTED_PROFILE` |
| Unsupported algorithm | Algorithm is not allowed for the profile. | Fail closed. | Hard failure | `UNSUPPORTED_ALGORITHM` |
| Invalid signature | Signature cannot verify over canonical bytes. | Reject. | Hard failure | `SIGNATURE_INVALID` |
| Wrong key/fingerprint | Supplied key does not match receipt or expected fingerprint. | Reject. | Hard failure | `PUBLIC_KEY_FINGERPRINT_MISMATCH` or `KEY_ID_MISMATCH` |
| Tampered receipt | Signed content changed after signing. | Reject. | Hard failure | `SIGNATURE_INVALID` |
| Wrong policy | Expected policy binding differs. | Reject while preserving signature result. | Hard failure | `POLICY_BINDING_MISMATCH` |
| Wrong build/image/config/model binding | Expected binding differs. | Reject or explicit binding exception. | Hard failure | `BUILD_BINDING_MISMATCH`, `IMAGE_BINDING_MISMATCH`, `CONFIG_BINDING_MISMATCH`, or proposed model-binding code |
| Missing receipt | Eligible action has no receipt mapping. | Reconciliation incomplete. | Hard failure | `missing` |
| Orphan receipt | Receipt maps to no eligible action. | Reconciliation incomplete. | Hard failure | `orphan_receipts` |
| Duplicate eligible action | Same upstream ID appears more than once. | Reconciliation incomplete. | Hard failure | `duplicates` |
| Duplicate receipt | Receipt ref or mapping duplicated. | Reconciliation incomplete. | Hard failure | `duplicates` |
| Issued but uncommitted | Receipt issued but not durable/committed. | Reconciliation incomplete. | Hard failure | `uncommitted_receipts` |
| Receipt-delivery failure | Action completed but receipt not delivered. | Reconciliation incomplete or explicit delivery exception. | Hard failure | `missing` or proposed `delivery_failures` |
| Missing approval | Human approval required but no linked evidence exists. | Verification or reconciliation exception. | Hard failure | proposed `approval_record_missing` |
| Unauthorized override | Override lacks allowed role or reason. | Blocking exception. | Hard failure | proposed `unauthorized_overrides` |
| Stale policy/config/model version | Expected binding is older or unsupported. | Binding failure or stale-binding exception. | Hard failure or explicit exception | binding mismatch or proposed `stale_binding` |
| Raw-data exposure | Receipt or artifact includes disallowed raw content. | Reject public artifact. | Hard failure | `raw_data_exposure` |
| Incomplete upstream population | Eligible-action source cannot be trusted. | Cannot conclude completeness. | Explicit exception | `upstream_population_incomplete` |
| Verifier unavailable or inconclusive | Verification cannot be recomputed. | No pass result. | Explicit exception | `verification_inconclusive` |

## Claims and Non-Claims

| Supported claim | Explicit non-claim |
|---|---|
| Supports evidence that a selected action was bound to stated policy, build, image, config, and evidence context. | Does not prove the AI decision was correct. |
| Supports independent verification of the illustrative public Ed25519 pilot receipt. | Does not mean the current private runtime emits the public Ed25519 profile. |
| Supports reconciliation against an independent eligible-action manifest. | Does not prove every production action was captured without an independent upstream source. |
| Supports detection of specified mismatches and missing evidence. | Does not show that a regulator or bank accepts the artifact. |
| Supports customer-assurance review of selected action evidence. | Does not establish OSFI E-23 compliance or regulatory acceptability. |
| Supports a synthetic public demonstration path. | Does not mean the current synthetic fixtures constitute customer validation. |

## Version Compatibility

The base profile identifier is `tcd.receipt.profile.v0.1`. The public illustrative profile is `illustrative_public_pilot_profile`, version `0.1`.

Compatibility rules:

- Verifiers MUST fail closed on unsupported profile identifiers or unsupported profile versions.
- Unknown required fields MUST NOT be silently ignored.
- Accepted extensions MUST be placed in an explicit extension container and covered by signed bytes.
- Future major or incompatible profile versions SHOULD use a new profile identifier or version.
- Deprecated fields SHOULD remain verifiable for fixtures that claim the older supported profile, or the verifier SHOULD return an explicit unsupported-version failure.
- Fixture, schema, and expected-binding versions SHOULD align.
- This profile inherits the base v0.1 canonicalization rules and does not claim RFC 8785/JCS compatibility.

## Current Implementation Status

| Requirement | Public illustrative support | Historical runtime evidence | Current gap | Pilot requirement |
|---|---|---|---|---|
| Illustrative Ed25519 verifier | Exists. | Not applicable to HMAC artifacts. | Private runtime Ed25519 integration does not exist. | Decide whether pilot requires public Ed25519 receipts. |
| Strict parsing, schema validation, and negative vectors | Exists for public verifier. | Not shown as public Ed25519 verification. | Domain-specific AML/KYB fields are not in current schema. | Add or agree extensions before production pilot. |
| Synthetic reconciliation mechanism | Exists. | Historical artifacts include runtime-derived matrices. | Does not prove real-customer completeness. | Integrate with independent upstream source. |
| Runtime-derived HMAC evidence | Not public Ed25519. | Exists; HMAC-SHA256, local SQLite, synthetic/redacted. | Not unrestricted public verification. | Define accepted evidence path for pilot reviewers. |
| Human approval and override semantics | Partial generic `human_review_state`. | Some action outcomes are visible in redacted artifacts. | Approval/override fields not implemented as structured schema fields. | Define customer-safe approval/override record. |
| Policy/config/model binding | Policy/build/image/config implemented; model field is not dedicated. | Historical HMAC evidence shows local runtime proof path. | Model version/config digest is proposed. | Bind model/config source of truth. |
| Production KMS/HSM | Not evidenced. | Not evidenced. | Production key-management not proven. | Define pilot key-management expectation. |
| Reviewer acceptance | Not evidenced. | Not evidenced. | No public pilot acceptance result. | Use scorecard before claiming acceptance. |
| Real-customer completeness proof | Not evidenced. | Not evidenced. | Requires trusted customer upstream population. | Establish independent eligible-action manifest. |
