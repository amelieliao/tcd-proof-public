# Demo Walkthrough: AML/KYB Alert Review

This walkthrough is written for customer discovery and advisor review. It avoids raw prompts, completions, documents, headers, cookies, auth tokens, signing secrets, SQLite files, runtime logs, and local private paths.

## 1. Diagnose a synthetic alert

Send `sample_alert_request.json` as the JSON body to:

```text
POST /diagnose
```

Expected buyer-facing result:

- TCD Proof returns a governed decision for the synthetic AML/KYB alert.
- The decision is `human_review` / `hold_for_review` in this sample.
- The response contains a redacted `receipt_public` view.
- The response contains or references verification material for an independent verifier.
- The response includes a `receipt_ref` similar to `receipt_ref:<redacted-demo-receipt-ref>`.

## 2. Extract the receipt reference

From the diagnose response, copy only the redacted receipt reference for demo narration:

```text
receipt_ref:<redacted-demo-receipt-ref>
```

Buyer message:

> This is the shareable handle for the governed AI-assisted action. It is not a raw prompt, raw document, auth token, or signing secret.

## 3. Show the public receipt

Open `sample_receipt_public.json`.

Point out:

- the decision was held for human review;
- the receipt is bound to a demo AML/KYB policy;
- the receipt is bound to redacted config, build, and image placeholders;
- the receipt has audit, attestation, ledger, commit, and chain references;
- the public view intentionally redacts raw case material and signature bytes.

## 4. Independently verify the receipt

Submit the receipt material or the receipt reference to:

```text
POST /verify
```

Use `sample_verify_report.json` as the expected OK story.

Buyer message:

> The verifier is not just checking that a response existed. It checks the signature, policy binding, config binding, build binding, image binding, PQ-required path, and evidence references.

## 5. Demonstrate a negative verification

Submit the same receipt while asking the verifier to expect the wrong policy, wrong config, or wrong build.

Use `sample_wrong_policy_verify_fail.json` as the expected fail story.

Buyer message:

> A real receipt can still fail verification when the verifier asks for the wrong governance context. That is important because a signature alone is not enough; the proof must bind to the expected policy and runtime context.

## 6. Demonstrate restart-safe verification

After restart, submit only:

```text
receipt_ref:<redacted-demo-receipt-ref>
```

Use `sample_restart_safe_verify.json` as the expected OK story.

Buyer message:

> The receipt can be verified by reference after restart. The proof is not merely an in-memory response object.

## Demo boundaries

This demo does not claim production HSM deployment, production hardware-root trust, global consensus, a real AML model, real regulated-customer data, or regulatory certification.

It demonstrates the product shape: every governed AI-assisted action can return a signed, policy-bound receipt that an independent party can verify.
