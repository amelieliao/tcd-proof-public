# Full-chain Receipt Quickstart

This Quickstart explains the public full-chain receipt demo path for TCD Proof.

It is designed for two audiences:

1. **Public reviewers** who want to inspect the redacted demo artifacts in this repository.
2. **Authorized technical reviewers** who have access to the private TCD runtime or reviewer bundle and want to reproduce the full-chain run locally.

This public repository does not contain the private TCD runtime implementation.

## What the full-chain run validates

A successful local full-chain run validates:

- local HMAC receipt signing
- PolicyStore loading
- SecurityRouter path
- schema-view public receipt projection
- verification bundle exposure
- build/image supply-chain binding
- PQ-required signature path
- durable SQLite receipt_ref lookup
- durable SQLite evidence-chain commit
- decision receipt and commit receipt
- by-ref receipt verification
- by-bundle receipt verification
- top-level receipt verification
- storage-window chain verification
- restart-safe durable by-ref verification

## Public inspection path

You can inspect the public redacted summary without access to the private runtime.

### 1. Clone this public repository

```bash
git clone https://github.com/amelieliao/tcd-proof-public.git
cd tcd-proof-public