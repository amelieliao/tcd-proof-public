# Customer Discovery One-Pager

## Problem

Many AI-assisted workflows now produce decisions, recommendations, reviews, escalations, or holds in regulated environments, but the evidence is often trapped inside internal logs or product UI. When a customer, auditor, model-risk reviewer, or security team asks what happened, the answer can be hard to share without exposing sensitive data or asking the reviewer to trust internal systems they cannot inspect.

## Why now

Regulated customers, enterprise buyers, security reviewers, model-risk teams, auditors, and RFP processes increasingly care about whether selected AI actions can be reviewed later. As AI moves from experiments into operational workflows, buyers want to know which actions were governed, which policy or procedure applied, and whether the record can be checked outside the original product experience.

## What TCD Proof does

TCD Proof creates a signed, policy-bound receipt for selected AI-assisted actions, so another party can verify what was governed without exposing raw customer data. The receipt is meant to make the governance step inspectable: what action happened, what decision was returned, what policy or procedure was expected, and whether the proof still verifies later.

## Example: AML/KYB alert review

The public demo uses a synthetic AML/KYB alert. An AI-assisted compliance review produces a decision for the alert, and TCD Proof returns a signed receipt for that governed action. The demo includes a verification OK example, a negative example where the wrong expected policy, configuration, or build binding fails verification, and a restart-safe example showing that the receipt can still be verified by reference after restart.

## What the receipt can prove

- action identity
- policy or procedure reference
- decision outcome
- human review, hold, or escalation state where applicable
- configuration, build, or image binding
- evidence references
- signature and verification status

## What it does not expose

- raw customer data
- raw documents
- raw prompts
- raw model answers
- secrets
- private runtime code

## Who this is for

- AI workflow vendors serving regulated customers
- AML, KYC, KYB, fraud, and compliance platforms
- insurance claims or underwriting AI workflows
- customer assurance and security review teams
- teams facing RFP, audit, model-risk, or governance review questions

## What I am looking for now

I am looking for short discovery conversations with teams building AI-assisted workflows in regulated environments. I am not asking for production deployment yet. I am trying to learn whether external verification of selected AI actions matters in customer reviews, RFPs, audit, model-risk, or security conversations.
