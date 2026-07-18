# Demo Walkthrough: AML/KYB Alert Review

This walkthrough is written for customer discovery and advisor review. It avoids raw prompts, completions, documents, headers, cookies, auth tokens, signing secrets, SQLite files, runtime logs, and local private paths.

## 1. Start with artifact status

Use `illustrative_manifest.json` to explain that the static samples show product shape only. They are synthetic and are not evidence that the runtime executed.

Use `run_derived/` and `assurance_packet.md` for the actual run-derived evidence. The current authorized local run executed three synthetic scenarios, and all three returned the core TCD terminal outcome `block`.

All three actions were blocked by the current authorized runtime profile. The public artifacts preserve this actual result and do not claim that allow or degrade outcomes were demonstrated in this run.

## 2. Diagnose synthetic alerts

For the illustrative shape, show `sample_alert_request.json`.

For the actual run-derived pilot, the runner submitted the three requests in `scenarios/` to:

```text
POST /diagnose
```

Expected buyer-facing result:

- TCD Proof returns a governed decision for the synthetic AML/KYB alert.
- In the current run-derived pilot, each scenario returned `block`.
- The response contains a redacted `receipt_public` view.
- The response contains or references verification material for an independent verifier.
- The public run-derived files replace receipt references with stable redacted tokens.

## 3. Extract the receipt reference

From the run-derived receipt index, use only the redacted receipt reference for demo narration:

```text
receipt_ref:redacted-run-001
```

Buyer message:

> This is the shareable handle for the governed AI-assisted action. It is not a raw prompt, raw document, auth token, or signing secret.

## 4. Show the public receipt

Open `sample_receipt_public.json` to show the illustrative receipt shape, then open `run_derived/receipt_index.redacted.json` for actual run-derived receipt references.

Point out:

- the current run-derived decision was `block` for all three synthetic actions;
- the receipt is bound to a demo AML/KYB policy;
- the receipt is bound to redacted config, build, and image references;
- the receipt has audit, attestation, ledger, commit, and chain references;
- the public view intentionally redacts raw case material and signature bytes.

## 5. Independently verify the receipt

Submit the receipt material or the receipt reference to:

```text
POST /verify
```

Use `sample_verify_report.json` as the illustrative OK story. Use `run_derived/verification_matrix.redacted.json` for the actual run-derived OK evidence.

Buyer message:

> The verifier is not just checking that a response existed. It checks the signature, policy binding, config binding, build binding, image binding, PQ-required path, and evidence references.

## 6. Demonstrate a negative verification

Submit the same receipt while asking the verifier to expect the wrong policy, wrong config, wrong build, or wrong image binding supported by the current verifier path.

Use `sample_wrong_policy_verify_fail.json` as an illustrative fail story. Use `run_derived/wrong_binding_failures.redacted.json` for the actual run-derived failure. In this run, the wrong-binding test used `expected_build_id`.

Buyer message:

> A real receipt can still fail verification when the verifier asks for the wrong governance context. That is important because a signature alone is not enough; the proof must bind to the expected policy and runtime context.

## 7. Demonstrate restart-safe verification

After restart, submit only:

```text
receipt_ref:redacted-run-001
```

Use `sample_restart_safe_verify.json` as the illustrative OK story. Use `run_derived/restart_safe_verification.redacted.json` for the actual run-derived result.

Buyer message:

> The receipt can be verified by reference after restart. The proof is not merely an in-memory response object.

## Demo boundaries

This demo does not claim production HSM deployment, production hardware-root trust, global consensus, a real AML model, real regulated-customer data, or regulatory certification.

It demonstrates the product shape and the current local run evidence: selected governed AI-assisted actions can return signed, policy-bound receipts that an independent verifier can check under the local demo profile. It does not claim unrestricted public verification or a production post-quantum signature algorithm.
