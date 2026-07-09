# AML/KYB Alert Review Demo

This is a buyer-facing demo of TCD Proof for a synthetic AI-assisted AML/KYB alert review.

The demo shows how an AI-assisted compliance decision can produce a signed, policy-bound receipt that an independent reviewer can verify later. The goal is not to prove that the AI model is correct. The goal is to prove that the AI-assisted action was governed: which policy applied, what decision was made, what runtime/build context was bound into the receipt, and whether the receipt still verifies after restart.

## Scenario

A synthetic fintech compliance team receives an AML/KYB alert for a business customer. An AI assistant summarizes risk factors and proposes whether the alert should be allowed, degraded, blocked, or sent to manual review.

TCD Proof sits beside that AI workflow and returns:

- a decision for the alert review;
- a public receipt reference that can be shared with a customer, auditor, advisor, or security reviewer;
- a redacted public receipt view;
- an independent verification report;
- a negative verification example showing that the receipt fails when the verifier asks for the wrong policy, config, or build;
- a restart-safe verification example showing that verification can work by receipt reference after service restart.

## What a buyer should notice

TCD Proof makes the governance step inspectable. A reviewer can ask, "Did this AI-assisted action follow the expected policy?" and get a verifiable answer rather than a trust-me log line.

The receipt binds the decision to policy, config, build, image, and evidence references. That makes the output useful for customer assurance, RFP review, internal audit, and regulated workflow design.

## What this demo does not claim

This demo does not claim:

- production HSM deployment;
- production hardware-root trust;
- global consensus;
- a real AML model;
- real bank, customer, merchant, or personal data;
- regulatory certification;
- proof that a model output is factually correct.

The files are synthetic and redacted. They are suitable for customer discovery, advisor review, and tcdproof.com-style product storytelling.

## Files

- `sample_alert_request.json`: synthetic AML/KYB alert review request.
- `sample_receipt_public.json`: redacted public receipt view.
- `sample_verify_report.json`: independent verify OK example.
- `sample_wrong_policy_verify_fail.json`: verify failure caused by wrong expected policy/config/build.
- `sample_restart_safe_verify.json`: by-reference verification after restart.
- `demo_walkthrough.md`: demo flow from diagnose to verify.
