# AML/KYB Production Boundaries

## Local pilot demonstrated

- Service entrypoint: `tcd.service_http:create_app`.
- Diagnose endpoint: `/diagnose`.
- Verify endpoint: `/verify`.
- Actual signing profile: `hmac_local_demo`.
- Actual signature algorithm: `hmac-sha256`.
- Actual storage backend: receipt lookup `sqlite`, evidence store `sqlite`.
- Receipt issuance for synthetic AML/KYB actions.
- Actual verify OK path.
- Wrong expected binding failure.
- Policy/config/build/image binding checks where exposed by the verifier.
- Durable lookup and restart behavior for receipt reference verification.

## Production deployment requirement

- production key management
- KMS/HSM integration where required
- asymmetric or public verification where required
- WORM or replicated storage where required
- multi-region recovery
- tenant isolation
- production access control
- retention and deletion controls
- customer deployment validation

## Important boundaries

- Local HMAC does not equal production HSM.
- A policy-required PQ path does not automatically equal a real post-quantum signature algorithm.
- Synthetic AML signals do not equal a real AML model.
- Governance evidence does not equal model correctness.
- Technical evidence does not equal regulatory certification.
- Local restart-safe verification does not equal multi-region disaster recovery.
- A receipt reference does not equal raw evidence custody.
- Independent-of-UI verification does not automatically equal unrestricted public verification.
