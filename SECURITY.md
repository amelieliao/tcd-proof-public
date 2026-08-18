# Security Policy

## Scope

This public repository contains synthetic fixtures, redacted examples, public documentation, and a clean-room verifier. It must not contain private runtime source code, secrets, private signing material, raw customer data, raw prompts, raw model answers, local databases, logs, or unredacted runtime artifacts.

## Reporting

If you find a public exposure risk in this repository, please contact:

```text
aliao@tcdproof.com
```

Please do not include secrets, private keys, raw customer data, raw prompts, raw completions, or private runtime paths in a report. A short description, file path, and line number are enough.

## Supported Materials

Security review currently covers:

- the public Ed25519 verifier;
- synthetic test vectors;
- reconciliation fixtures;
- public documentation;
- redacted AML/KYB demo artifacts.

The public Ed25519 profile is an illustrative pilot profile. It is not a production HSM deployment, not a hardware-rooted production signing profile, not regulatory certification, and not currently integrated with the private runtime.

## License Boundary

This public repository uses the MIT License. That license applies only to code, documentation, schemas, and synthetic fixtures that are actually published in this repository. It does not cover the private TCD core runtime, unpublished implementation details, secrets, runtime artifacts, customer data, raw prompts, raw model answers, or private receipt bodies.
