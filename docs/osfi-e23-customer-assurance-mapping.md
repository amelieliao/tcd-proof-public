# OSFI Guideline E-23 and Customer Assurance Evidence Mapping

Official source reviewed:

- OSFI, [Guideline E-23 - Model Risk Management (2027)](https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027), publication type: Guideline, date: September 11, 2025, effective date: May 1, 2027.
- OSFI, [Guideline E-23 - Model Risk Management (2027) - Letter](https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027-letter), date: September 11, 2025, states that the guideline takes effect for federally regulated financial institutions on May 1, 2027.

This is an evidence mapping, not a legal opinion or compliance determination. TCD supports evidence for selected review questions. This mapping does not mean TCD complies with, certifies, or determines compliance with OSFI E-23. Final applicability and acceptance remain with the institution, its reviewers, legal/compliance functions, and OSFI where applicable.

This document uses official OSFI headings and topics as anchors, then separates explicit guideline topics from customer-assurance or RFP questions informed by those topics. It does not quote or restate the guideline as a legal requirement.

## Current TCD Evidence Boundary

The current public Ed25519 fixtures are illustrative public pilot vectors. They are not private runtime output. The historical AML/KYB artifacts are runtime-derived, HMAC-SHA256, local SQLite, synthetic/redacted evidence; they are not unrestricted public-verifiable Ed25519 receipts. The current private runtime is not yet integrated with the public Ed25519 profile. Current reconciliation fixtures demonstrate the mechanism, not the absence of silent gaps in a real customer workflow.

Status categories used below:

- `Currently demonstrated -- illustrative public fixture`
- `Currently demonstrated -- historical HMAC runtime evidence`
- `Proposed pilot requirement`
- `Requires customer workflow integration`
- `Requires private-runtime implementation`
- `Requires institutional policy/attestation`
- `Not evidenced`

## Evidence Mapping

| Reviewer / RFP question | OSFI E-23 topic or official reference | Relevant receipt field(s) | Supporting artifact | Evidence TCD supports | What TCD does not prove | Current production gap | Current status |
|---|---|---|---|---|---|---|---|
| Can the institution identify the model or AI-assisted workflow involved in a selected action? | Explicit topic: Appendix 1 model information tracking; C.1 Model identification. | `profile`, `profile_version`, `receipt_body.claims.action_type`; model ID is proposed. | Receipt; model/config manifest. | Supports evidence for linking a selected action to workflow and proposed model identity. | Does not prove the institution's model inventory is complete. | Dedicated model ID/version field and customer model inventory integration. | Proposed pilot requirement |
| Is a third-party or vendor model/platform involved? | Explicit topic: B.2 MRM framework covers models or data sourced externally; C.1 identifies vendor/third-party models; D.2 Model review references third-party models and platforms. | Vendor/model origin is not in current schema. | Policy/build/model/config manifest; production-boundary statement. | Provides an artifact relevant to vendor-model identification for a selected action. | Does not prove third-party risk review is complete. | Vendor origin and dependency references must come from customer or vendor governance source. | Requires institutional policy/attestation |
| Who owns the model or workflow? | Explicit topic: A.4 Key Terms, Model Owner; Appendix 1 model owner. | Owner is not in current schema. | Customer questionnaire/control reference; policy manifest. | May help a reviewer assess whether receipt evidence can point to an owner-controlled policy reference. | Does not identify or validate the model owner by itself. | Owner mapping must be supplied by institution or customer workflow. | Requires institutional policy/attestation |
| Who reviewed or approved use of the model? | Explicit topic: A.4 Model Reviewer and Model Approver; D.2 Model review and Model approval. | `receipt_body.claims.human_review_state`; reviewer/approver role is proposed. | Approval/override record; assurance packet. | Supports evidence for whether a selected action had a linked review or approval state. | Does not prove reviewer independence or institutional authority without external attestation. | Structured reviewer role and approval reference are proposed. | Proposed pilot requirement |
| Is this use case approved and within intended use? | Explicit topic: B.3 Use of models; D.2 Model rationale; Appendix 1 approved uses. | `receipt_body.claims.action_type`, `policy_ref`, `policy_digest`. | Expected-bindings file; policy/config manifest. | Supports evidence for comparing selected action context to an expected policy reference. | Does not prove the institution approved the use case. | Approved-use source of truth must be integrated. | Requires institutional policy/attestation |
| Are known limitations represented in the evidence pack? | Explicit topic: D.2 Model development documentation and Appendix 1 limitations. | Limitations are not in current schema. | Production-boundary statement; policy/model manifest. | Provides an artifact relevant to limitation disclosures for a selected action review. | Does not prove limitations are adequate or accepted. | Limitation references must be authored by model owner/reviewer. | Proposed pilot requirement |
| Can the reviewer see data source references without raw case data? | Explicit topic: D.2 Model data, including data governance, lineage, provenance, and privacy. | `receipt_body.req.payload_digest`, `receipt_body.e.refs[]`, `receipt_body.claims.evidence_set_ref`. | Receipt; evidence package reference. | Supports evidence for data-source or evidence references using hashes, digests, and redacted IDs. | Does not prove data quality, representativeness, or lawful use. | Customer data-source manifest and approved redaction rules are required. | Currently demonstrated -- illustrative public fixture |
| Can model dependencies be identified? | Explicit topic: Appendix 1 model dependencies; D.2 Model monitoring tracks external dependencies. | `build_id`, `image_digest`, `cfg_fp`; dependency details are proposed. | Build/model/config manifest. | Supports evidence for binding selected action to build, image, and config identity. | Does not prove all external dependencies are inventoried. | Dependency manifest must be integrated. | Proposed pilot requirement |
| Can model/config/build version be verified later? | Explicit topic: Appendix 1 model version; D.2 Model deployment and monitoring. | `receipt_body.claims.build_id`, `image_digest`, `cfg_fp`; model version proposed. | Receipt; expected-bindings file; verification report. | Supports evidence for independent verification of build/image/config bindings. | Does not prove the model version field exists in current schema. | Dedicated model version/config digest is proposed. | Currently demonstrated -- illustrative public fixture |
| Was deployment approval linked to the action context? | Explicit topic: D.2 Model approval and Model deployment. | Deployment approval is not in current schema. | Approval record; policy/build/model/config manifest. | May help a reviewer assess whether selected action evidence can reference approved deployment state. | Does not prove deployment was approved. | Deployment approval reference must come from institution. | Requires institutional policy/attestation |
| Was change control applied to policy, config, model, build, or image changes? | Explicit topic: D.1 policies/procedures/controls; D.2 Model deployment change control; D.2 Model monitoring tracks operational changes. | `policy_ref`, `policy_digest`, `build_id`, `image_digest`, `cfg_fp`; model change field proposed. | Expected-bindings file; policy/build/model/config manifest. | Supports evidence for detecting stale or wrong expected bindings for selected actions. | Does not prove the change-control process is sufficient. | Change-control source and model-version binding require integration. | Proposed pilot requirement |
| How are exceptions handled? | Explicit topic: D.2 Model deployment references exception handling and overlays; D.2 Model approval allows justified use with known limitations. | Exception state is not dedicated; `human_review_state` may indicate review. | Incident or exception record; approval/override record. | Provides an artifact relevant to exception traceability for selected actions. | Does not decide whether an exception was appropriate. | Structured exception/override record required. | Proposed pilot requirement |
| Was human review required and performed? | Explicit topic: A.4 Model User/Reviewer/Approver roles; D.1 roles and accountability; D.2 Model review/approval. | `receipt_body.claims.human_review_state`; detailed role and approval reference proposed. | Receipt; approval record; verification report. | Supports evidence for human-review state attached to a selected action. | Does not prove the human reviewer made a correct decision. | Role, timestamp, and authorization evidence need customer-safe integration. | Proposed pilot requirement |
| Was an override authorized and linked to the action? | Customer-assurance question informed by the guideline; not quoted as an explicit OSFI requirement. Related to D.2 exception handling, overlays, monitoring, and decommissioning references to excessive overrides. | Override fields are proposed; `human_review_state` is partial. | Approval/override record; reconciliation report. | Supports evidence for counting and linking overrides when structured override records exist. | Does not prove an override was acceptable to the institution. | Override reason code, actor role, and authorization evidence are proposed. | Proposed pilot requirement |
| Is monitoring status available for the model or selected action class? | Explicit topic: D.2 Model monitoring; Appendix 1 monitoring status and next review date. | Monitoring status is not in current receipt schema. | Model/config manifest; monitoring or exception record. | Provides an artifact relevant to monitoring-state review if supplied externally. | Does not perform model monitoring by itself. | Monitoring source of truth required. | Requires customer workflow integration |
| Is validation or review evidence linked? | Explicit topic: D.2 Model review and Appendix 1 most recent model review. | Review reference is proposed. | Validation/review evidence; assurance packet. | May help a reviewer assess whether selected action evidence links to review artifacts. | Does not validate model conceptual soundness. | Review evidence reference must come from model-risk process. | Requires institutional policy/attestation |
| Is there explainability or rationale evidence for the action? | Explicit topic: D.2 Model rationale, Model development explainability requirements, Model review explainability, and Model deployment explanatory outputs. | `receipt_body.e.refs[]`, `receipt_body.comp.decision_ref`; rationale field proposed. | Evidence package reference; redacted rationale reference. | Supports evidence for a bounded reference to rationale artifacts. | Does not prove the rationale is complete, fair, or persuasive. | Rationale artifact and redaction policy require integration. | Proposed pilot requirement |
| Can evidence be retained and reviewed later? | Explicit topic: model inventory retention for decommissioned models in C.1 and documentation across D.1/D.2; Appendix 1 information tracking. | `receipt_ref`, `e.refs[]`, `witness.restart_safe_reference`. | Receipt; verification report; evidence package reference. | Supports evidence for later review by reference when artifacts are retained. | Does not prove institution retention obligations are met. | Retention/deletion policy and storage controls are institution-specific. | Requires institutional policy/attestation |
| Can the artifact support auditability of selected actions? | Explicit topic: B.2 reporting and framework processes; D.1 documented controls; D.2 review/deployment/monitoring documentation. | Receipt fields, evidence refs, `auth_sig`, verification report. | Receipt; verification report; assurance packet. | Supports evidence for independent verification of selected receipt integrity and bindings. | Does not replace audit judgment or audit procedures. | Production audit workflow and access model required. | Currently demonstrated -- illustrative public fixture |
| Is there incident or remediation trace for failures? | Explicit topic: C.2 remediation actions when risk falls outside appetite; D.2 monitoring contingency and escalation procedures. | Incident/remediation fields are proposed. | Incident or exception record; reconciliation report. | Provides an artifact relevant to failure traceability if incident records are linked. | Does not prove remediation was sufficient. | Incident workflow integration required. | Proposed pilot requirement |
| Is selected-action evidence complete for the agreed scope? | Customer-assurance question informed by the guideline; not quoted as an explicit OSFI requirement. Related to B.2 MRM framework, C.1 model identification, and D.1 documented controls. | `upstream_action_id`, `receipt_ref`; reconciliation input fields. | Eligible-action manifest; receipt index; recomputed verification results; reconciliation report. | Supports evidence for reconciliation against an independent eligible-action manifest. | Does not prove a real production workflow has no silent gaps without a trusted upstream source. | Independent upstream source and workflow controls required. | Currently demonstrated -- illustrative public fixture |

## Artifact Types

Supporting artifacts may include:

- receipt;
- expected-bindings file;
- verification report;
- eligible-action manifest;
- reconciliation report;
- policy/build/model/config manifest;
- approval/override record;
- assurance packet;
- production-boundary statement;
- incident or exception record.

The current public repository does not show all of these as runtime-generated artifacts. Several are proposed pilot requirements or require customer workflow integration. Public-safe artifacts should use hashes, digests, bounded references, and redacted identifiers rather than raw case content.

## Priority Gaps for a First AML/KYB Pilot

| Priority gap | Why it matters | Proposed owner | Current status |
|---|---|---|---|
| Independent eligible-action source | Needed to assess completeness without relying on receipt presence. | Customer workflow owner and TCD pilot owner | Requires customer workflow integration |
| Model/version/config source of truth | Needed to bind actions to approved model context. | Model owner or vendor owner | Proposed pilot requirement |
| Approval/override record | Needed to distinguish authorized exceptions from silent failures. | Compliance/model-risk reviewer | Proposed pilot requirement |
| Data redaction and evidence boundary | Needed to avoid raw case data exposure. | Customer data owner and TCD pilot owner | Requires institutional policy/attestation |
| Reviewer acceptance criteria | Needed before claiming assurance value. | Customer assurance or model-risk reviewer | Not evidenced |

## Questions to Validate With a Real Reviewer

- Which E-23-informed review questions matter in the customer's actual AML/KYB review process?
- Is a signed receipt plus expected bindings enough to answer selected RFP or assurance questions?
- What evidence must be institution-authored rather than vendor-authored?
- Can a reviewer independently verify a selected action without using the original product UI?
- Which fields are unacceptable even when redacted or hashed?
- What retention, deletion, and data residency requirements apply to receipt and evidence references?

## Items Requiring Institutional or Customer Input

TCD cannot answer the following without customer or institutional input:

- whether a model is in the institution's model inventory;
- approved use, limitation, owner, reviewer, and approver records;
- model risk rating and monitoring status;
- accepted override and approval process;
- authoritative upstream eligible-action population;
- data classification and redaction boundary;
- evidence retention and access-control policy;
- final reviewer acceptance.
