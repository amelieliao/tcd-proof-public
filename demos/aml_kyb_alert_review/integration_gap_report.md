# AML/KYB Integration Gap Report

This report is written from the point of view of a potential AML/KYB pilot customer.

| Area | Status | Notes |
|---|---|---|
| customer-specific case/event adapter | adapter_required | Map the customer's case/event into the public DiagnoseRequest fields and context. |
| case identifier mapping | customer_specific | Use customer-owned case IDs or redacted references. |
| tenant mapping | supported_with_configuration | Tenant is a first-class request field. |
| proposed action mapping | adapter_required | Business action lives in scenario/context and must map to core allow/degrade/block. |
| policy/SOP source of truth | customer_specific | Customer policy source must be selected for a pilot. |
| policy versioning | production_hardening_required | Policy references are bound; production versioning process is customer-specific. |
| policy digest generation | supported_now | The run-derived artifacts include policy/config binding checks. |
| human review state | adapter_required | Represent as buyer-facing workflow consequence, not a new core TCD outcome. |
| enhanced due diligence state | adapter_required | Represent as workflow consequence mapped from core degrade. |
| escalation/approval workflow | adapter_required | Needs customer workflow integration. |
| evidence reference API | adapter_required | Pilot currently uses synthetic evidence references. |
| evidence retention | production_hardening_required | Retention policy is deployment-specific. |
| receipt distribution | adapter_required | Decide what receipt view each reviewer may receive. |
| verifier identity | customer_specific | Define authorized verifier roles. |
| verification material distribution | production_hardening_required | Local demo uses demo-authorized verification material. |
| signing-key management | production_hardening_required | Local HMAC is not production key management. |
| KMS/HSM integration | production_hardening_required | Not claimed by this local pilot. |
| key rotation | not_yet_validated | Not exercised by this AML/KYB pilot. |
| key revocation | not_yet_validated | Not exercised by this AML/KYB pilot. |
| durable storage | supported_now | Local durable receipt lookup and evidence storage were exercised. |
| WORM/object lock | production_hardening_required | Not part of the local pilot. |
| multi-tenant isolation | production_hardening_required | Requires deployment validation. |
| authentication/authorization | production_hardening_required | Local pilot disables production auth for localhost execution. |
| customer-specific policy mapping | customer_specific | Must be defined with the pilot customer. |
| PII minimization | supported_now | Public export excludes raw case material. |
| retention/deletion | customer_specific | Depends on customer compliance program. |
| incident response | customer_specific | Needs operational runbook integration. |
| audit export | adapter_required | Receipt packet shape exists; export workflow must be selected. |
| monitoring/SLO | production_hardening_required | Monitoring, alerting, and service-level objectives are not evaluated by this pilot. |
| observability | production_hardening_required | Operational telemetry packaging is not part of the public demo. |
| deployment model | customer_specific | Depends on customer environment. |
| security review | adapter_required | Use this packet as starting material. |
| model-risk review | adapter_required | Map receipt fields to the customer's review process. |
| RFP/customer-assurance packaging | supported_with_configuration | Assurance packet and claims matrix provide a starting packet. |
