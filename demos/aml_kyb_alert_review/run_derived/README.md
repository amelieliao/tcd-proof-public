# Run-Derived AML/KYB Artifacts

This directory is populated by `../tools/run_authorized_local_pilot.py`.

The files are generated from an authorized local execution of the current private runtime snapshot, then redacted for public review. They are synthetic and exclude raw case material, signing secrets, local databases, logs, process IDs, and private runtime source code.

Current run summary:

- scenarios executed: 3
- actual terminal outcomes observed: `block`
- receipts issued: yes
- verify OK path: yes
- wrong-binding failure: yes
- restart-safe verification by receipt reference: yes
- signing profile: local HMAC demo profile
- signature algorithm recorded for this local run: HMAC-SHA-256
