# TCD Proof Demo Index

TCD Proof helps selected AI-assisted workflow actions leave behind a signed, reviewable receipt. This public repository shows the shape of that proof using redacted examples and a synthetic AML/KYB alert review demo. A signed receipt is valuable because it gives a buyer, reviewer, advisor, or investor something concrete to verify later instead of relying on a screenshot or a trust-me status message. The AML/KYB demo shows how an AI-assisted compliance review can produce a governed decision, a public receipt view, a verification OK story, a failure story for wrong expected bindings, and restart-safe verification. The full-chain receipt demo shows the broader path from governed action to receipt, evidence references, and independent verification. Independent verification matters because the reviewer can check the receipt against expected policy and runtime context without needing access to the original product UI. The public examples avoid raw customer data so the proof can be shared for discovery and review without exposing sensitive case material.

This page is for non-engineering buyers, advisors, Velocity reviewers, and investors who want the shortest path through the demo materials.

## Start here

Read the materials in this order:

1. [Repository README](../README.md)
2. [AML/KYB alert review overview](../demos/aml_kyb_alert_review/README.md)
3. [AML/KYB demo walkthrough](../demos/aml_kyb_alert_review/demo_walkthrough.md)
4. [Redacted full-chain receipt summary](../examples/full-chain-receipt-summary.redacted.json)
5. [Redacted verification report](../examples/verify-report.redacted.json)
6. [Receipt and evidence model](receipt-and-evidence-model.md)
7. [Architecture notes](architecture-notes.md)

## What this proves

- A selected AI-assisted action can produce a signed receipt.
- The receipt can bind the action to policy, configuration, build or image context, evidence references, and verification status.
- A verifier can check the receipt independently after the action has happened.
- Verification can fail when the verifier expects the wrong policy, configuration, or build context.
- A receipt can remain verifiable by reference after restart, so the proof is not just an in-memory response.

## What this does not claim

This public demo does not claim:

- production HSM deployment;
- production hardware-root trust;
- global consensus;
- a real AML model;
- real regulated customer data;
- regulatory certification;
- proof that the AI model is always correct.

## How to use this in customer discovery

Use this demo to discuss concrete buyer questions:

1. Which AI-assisted actions in your workflow would customers, auditors, or reviewers most want to inspect later?
2. When a decision is questioned, what evidence do you currently share, and how much of it depends on internal logs or product screenshots?
3. Would a signed receipt make customer assurance, RFP, audit, model-risk, or security review conversations easier?
4. Which policy, procedure, configuration, build, or evidence references would need to be bound into a useful receipt?
5. What sensitive material must stay out of the receipt for it to be shareable with external reviewers?
