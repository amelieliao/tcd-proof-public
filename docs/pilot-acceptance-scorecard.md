# TCD AML/KYB Pilot Acceptance Scorecard

This is a blank pilot acceptance template for a design partner or reviewer. It must be completed with real pilot evidence before any result is claimed.

The current public Ed25519 fixtures are illustrative public pilot vectors and are not private runtime output. Historical AML/KYB artifacts are runtime-derived, HMAC-SHA256, local SQLite, synthetic/redacted evidence. They are not unrestricted public-verifiable Ed25519 receipts. The current private runtime is not yet integrated with the public Ed25519 profile. Current reconciliation fixtures demonstrate the mechanism, not the absence of silent gaps in a real customer workflow.

## Pilot Metadata

| Field | Value |
|---|---|
| Pilot/customer alias | TBD |
| Workflow | TBD |
| In-scope action types | TBD |
| Pilot window | TBD |
| Upstream source | TBD |
| Reviewer roles | TBD |
| Technical owner | TBD |
| Compliance/model-risk reviewer | TBD |
| Data classification | TBD |
| Deployment mode | TBD |
| Profile/schema version | `0.1` / TBD |
| Baseline period | TBD |
| Evaluation period | TBD |

## Scope Lock

Scope is locked before pilot execution. It must not be rewritten after results are known to improve the pass rate.

| Scope item | Locked value | Evidence/source | Owner | Status |
|---|---|---|---|---|
| Inclusion rules | TBD | TBD | TBD | Not assessed |
| Exclusion rules | TBD | TBD | TBD | Not assessed |
| Eligible-action definition | TBD | TBD | TBD | Not assessed |
| Stable upstream ID | TBD | TBD | TBD | Not assessed |
| Retry/idempotency handling | TBD | TBD | TBD | Not assessed |
| Approved data boundary | TBD | TBD | TBD | Not assessed |
| Expected policy binding | TBD | TBD | TBD | Not assessed |
| Expected build binding | TBD | TBD | TBD | Not assessed |
| Expected image binding | TBD | TBD | TBD | Not assessed |
| Expected model/config binding | TBD | TBD | TBD | Not assessed |
| Expected human-review process | TBD | TBD | TBD | Not assessed |
| Expected override process | TBD | TBD | TBD | Not assessed |

## Hard Acceptance Gates

| Metric / Gate | Definition / Formula | Threshold | Measurement method | Evidence source | Result | Status | Notes / remediation |
|---|---|---|---|---|---|---|---|
| Eligible-action capture | `capture_rate = eligible actions with exactly one mapped receipt where issued is true, committed is true, and exactly one recomputed verification result has ok is true / total unique eligible actions × 100%` | `100%` | Reconcile independent eligible-action manifest to receipt index and verification results. | Eligible-action manifest; receipt index; verification report; reconciliation report | TBD | Not assessed | TBD |
| Missing receipts | Eligible action has no receipt mapping. | `0` | Reconciliation count. | Reconciliation report | TBD | Not assessed | TBD |
| Orphan receipts | Receipt maps to no eligible action. | `0` | Reconciliation count. | Reconciliation report | TBD | Not assessed | TBD |
| Duplicate eligible IDs | Same stable upstream ID appears more than once in eligible population. | `0` | Strict manifest validation and reconciliation. | Eligible-action manifest; reconciliation report | TBD | Not assessed | TBD |
| Duplicate receipt refs or mappings | Same receipt ref or action-to-receipt mapping appears more than allowed. | `0` | Receipt index validation and reconciliation. | Receipt index; reconciliation report | TBD | Not assessed | TBD |
| Issued but not committed | Receipt was issued but lacks committed/durable state. | `0` | Commit/durability check and reconciliation. | Receipt index; commit/durability results | TBD | Not assessed | TBD |
| Verification failures for expected-valid receipts | Expected-valid receipts fail verification. | `0` | Recompute verification from receipt, public key, and expected bindings. | Verification reports | TBD | Not assessed | TBD |
| Negative verification tests | Tampered receipt, wrong policy, wrong build, wrong key/fingerprint, unsupported algorithm/version, and missing mandatory field must fail explicitly with the correct failure category. | `100% of required negative cases fail explicitly; no false pass.` | Run required negative verifier cases. | Negative verification report | TBD | Not assessed | TBD |
| Raw case data exposure | Raw prompt, raw completion, raw document/case payload, signing secret/private key, private local path, SQLite/log/runtime artifact, or real customer identifier beyond approved bounded/redacted references appears in public-safe artifacts. | `0` | Public-export scan and reviewer inspection. | Public export validator; assurance packet | TBD | Not assessed | TBD |
| Reviewer independence | Reviewer verifies without original product UI or private runtime source, using receipt, public key, expected bindings, public verifier, and supporting public-safe artifacts. | Independent pass with no interpretive assistance or technical intervention. | Use the reviewer-independence observation record below. | Reviewer observation record | TBD | Not assessed | If substantive engineering assistance is required, do not mark fully independent pass. |

Capture-rate calculation rules:

- Numerator: unique eligible actions with exactly one mapped receipt where `issued is true`, `committed is true`, and exactly one verifier-recomputed verification result has `ok is true`.
- Denominator: total unique eligible actions from the independent upstream eligible-action manifest.
- The eligible population must be determined before checking whether any receipt exists.
- Capture rate must be recomputed from action-level records and must not trust precomputed summaries, counts, or verification assertions in the inputs.
- Rounding must not turn any value below `100%` into a passing result.
- Duplicate eligible IDs, duplicate receipt refs, duplicate mappings, orphan receipts, orphan verification results, missing verification results, duplicate verification results, verification failures, invalid reconciliation inputs, and issued-but-not-committed receipts remain separate global zero-tolerance hard gates.
- Even if capture rate displays as `100%`, the pilot must not receive `GO` and completeness must not pass if any global zero-tolerance gate fails.

## Reviewer Independence Observation

| Field | Recorded value | Requirement / allowed values |
|---|---|---|
| Pilot/review ID |  | Non-customer-sensitive identifier |
| Reviewer name or pseudonymous reviewer ID |  | Do not publish personal information without permission |
| Reviewer organization/type |  | Vendor / bank / credit union / regulated fintech / independent advisor / other |
| Reviewer role |  | Compliance / model risk / vendor risk / security / product / engineering / audit / other |
| Relationship to TCD |  | Independent reviewer / design partner / internal test reviewer |
| Verification start time |  | UTC timestamp |
| Verification end time |  | UTC timestamp |
| Elapsed verification time |  | Minutes, calculated from start/end |
| Original vendor product UI used |  | Yes / No |
| Founder or engineer live assistance occurred |  | None / logistical only / interpretive / technical intervention |
| Assistance details |  | Required unless value is `None` |
| Materials supplied before start |  | Receipt, public key, expected bindings, written instructions, hashes, other |
| Verification environment |  | Reviewer-controlled / shared sandbox / vendor-controlled / other |
| Verification result |  | Pass / Fail / Inconclusive |
| Questions or blockers encountered |  | No raw case data |
| Reviewer confirmation |  | Name/ID, date, or approved acknowledgement mechanism |

Observation rules:

1. Timing starts when the reviewer has the complete pre-agreed materials and begins the verification steps.
2. Timing ends when the reviewer has a clear verification result and completes the result record.
3. The reviewer must not enter the original vendor/product UI.
4. The reviewer may use written instructions supplied before the start.
5. `logistical only` may include providing file location, starting an environment, or resolving access issues unrelated to verification logic.
6. Live interpretation, running commands for the reviewer, modifying evidence, or explaining how to bypass a failure does not count as independent completion.
7. If interpretive assistance or technical intervention occurs, that review record cannot be used to prove that an independent reviewer completed verification.
8. The public scorecard must not record raw case data, customer secrets, or personal information without permission.
9. The `≤15 minutes` target is an operational target. Missing receipts, false-positive verification, accepted invalid signatures, raw-data exposure, or failed reviewer independence remain hard gates.

## Completeness Metrics

| Metric | Count / value | Evidence source | Status | Notes |
|---|---|---|---|---|
| Eligible actions observed | TBD | Eligible-action manifest | Not assessed | TBD |
| Receipts issued | TBD | Receipt index | Not assessed | TBD |
| Receipts committed | TBD | Receipt index or commit/durability results | Not assessed | TBD |
| Successfully verified | TBD | Recomputed verification results | Not assessed | TBD |
| Missing | TBD | Reconciliation report | Not assessed | TBD |
| Orphaned | TBD | Reconciliation report | Not assessed | TBD |
| Duplicates | TBD | Reconciliation report | Not assessed | TBD |
| Verification failures | TBD | Verification report; reconciliation report | Not assessed | TBD |
| Issued but uncommitted | TBD | Receipt index; reconciliation report | Not assessed | TBD |
| Human overrides | TBD | Approval/override records; reconciliation report | Not assessed | Human overrides do not need to be zero. |
| Unauthorized or unexplained overrides | TBD | Approval/override records; reconciliation report | Not assessed | Must be zero for GO. |
| Complete true/false | TBD | Reconciliation report | Not assessed | TBD |

Human override quality gates:

| Override requirement | Threshold | Result | Status | Notes |
|---|---|---|---|---|
| Authorized actor role present | `100%` | TBD | Not assessed | No raw personal identity unless explicitly approved. |
| Reason code present | `100%` | TBD | Not assessed | Controlled code, no raw notes. |
| Linked to eligible action and receipt | `100%` | TBD | Not assessed | Must reconcile to stable upstream ID. |
| No raw personal/customer content | `100%` | TBD | Not assessed | Bounded/redacted references only. |

## ROI and Efficiency Baseline

Do not prefill improvements. Record observed values only.

| Metric | Before pilot | During/after pilot | Absolute change | Percentage change where meaningful | Sample size | Measurement notes |
|---|---|---|---|---|---|---|
| Evidence reconstruction time | TBD | TBD | TBD | TBD | TBD | TBD |
| Reviewer verification time | TBD | TBD | TBD | TBD | TBD | TBD |
| RFP/security-questionnaire response time | TBD | TBD | TBD | TBD | TBD | TBD |
| Missing required fields | TBD | TBD | TBD | TBD | TBD | TBD |
| Manual systems/screenshots/log exports used | TBD | TBD | TBD | TBD | TBD | TBD |
| Engineering assistance time | TBD | TBD | TBD | TBD | TBD | TBD |
| Clarification cycles | TBD | TBD | TBD | TBD | TBD | TBD |
| Reviewer confidence/acceptance result | TBD | TBD | TBD | TBD | TBD | Qualitative result; do not convert to percentage without agreed method. |

## Reviewer Question Coverage

| Actual reviewer/RFP/audit question | Required evidence | Receipt/artifact field used | Answered fully / partially / not answered | Reviewer comments | Missing field or process | Remediation owner | Retest required |
|---|---|---|---|---|---|---|---|
| TBD | TBD | TBD | Not assessed | TBD | TBD | TBD | TBD |
| Would this evidence be acceptable for the reviewer's actual workflow without relying on the vendor's original product UI? | Reviewer judgment using receipt, expected bindings, verifier, and public-safe bundle. | TBD | Not assessed | Allowed answers: Yes; Yes, with conditions; No; Not assessed. | TBD | TBD | TBD |

## Production Gaps

| Gap | Severity | Owner | Remediation | Due date | Pilot blocker yes/no | Evidence required for closure |
|---|---|---|---|---|---|---|
| Missing integration | TBD | TBD | TBD | TBD | TBD | TBD |
| Key management | TBD | TBD | TBD | TBD | TBD | TBD |
| Data residency | TBD | TBD | TBD | TBD | TBD | TBD |
| Tenant isolation | TBD | TBD | TBD | TBD | TBD | TBD |
| Retention/deletion | TBD | TBD | TBD | TBD | TBD | TBD |
| Deployment model | TBD | TBD | TBD | TBD | TBD | TBD |
| Incident contact | TBD | TBD | TBD | TBD | TBD | TBD |
| Failure behavior | TBD | TBD | TBD | TBD | TBD | TBD |
| Receipt-delivery failure | TBD | TBD | TBD | TBD | TBD | TBD |
| Monitoring | TBD | TBD | TBD | TBD | TBD | TBD |
| SLA | TBD | TBD | TBD | TBD | TBD | TBD |
| KMS/HSM | TBD | TBD | TBD | TBD | TBD | TBD |
| Access control | TBD | TBD | TBD | TBD | TBD | TBD |
| Institutional attestation | TBD | TBD | TBD | TBD | TBD | TBD |
| Unresolved policy/model-risk question | TBD | TBD | TBD | TBD | TBD | TBD |

## Final Decision

Final decision must be one of:

- `GO`
- `CONDITIONAL GO`
- `NO-GO`

Decision rules:

| Decision | Rule |
|---|---|
| `GO` | All hard integrity, privacy, and completeness gates pass; capture rate is 100%; missing, orphaned, duplicate, and uncommitted counts are 0; all required negative tests fail explicitly; raw case data exposure is 0; reviewer can independently verify; reviewer questions reach agreed coverage; no unresolved pilot-blocking production gap remains. |
| `CONDITIONAL GO` | All hard integrity, privacy, and completeness gates pass, and remaining issues are explicit, fixable, non-security-critical integration, UX, timing, or question-coverage gaps. Each condition must have owner, remediation, and retest date. Conditional go cannot be used for missing receipts, false-positive verification, raw-data exposure, accepted invalid signatures, unauthorized overrides, or incomplete eligible population. |
| `NO-GO` | Any capture rate below 100%, silent gap, missing/orphaned/duplicate receipt, issued-but-uncommitted receipt, expected-valid verification failure, negative-test false pass, raw-data exposure, inability for reviewer to independently verify, untrusted upstream eligible population, or unresolved critical production gap. |

Decision record:

| Field | Value |
|---|---|
| Decision | Not assessed |
| Decision date | TBD |
| Decision owners | TBD |
| Conditions | TBD |
| Retest plan | TBD |
| Evidence bundle reference | TBD |
| Signatures/acknowledgements | TBD |
