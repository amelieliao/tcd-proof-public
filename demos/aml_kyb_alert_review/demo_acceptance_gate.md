# AML/KYB Demo Acceptance Gate

Run:

```bash
python demos/aml_kyb_alert_review/tools/check_demo_acceptance.py --public-root .
```

Minimum passing conditions:

- private repo final status equals private repo initial status
- synthetic AML/KYB scenario schema validated
- at least one actual scenario executed
- at least one actual receipt issued
- at least one actual verification succeeded
- actual policy binding verified
- at least one actual wrong-binding verification failed
- actual process restart completed
- receipt_ref verified after restart
- all run-derived artifacts provenance-labeled
- no raw customer data
- no raw prompt/completion
- no signing secret
- no SQLite/log/PID in public repo
- all JSON parses
- Markdown links pass
- public export validator passes
- no unrelated public files changed
- no private files changed
