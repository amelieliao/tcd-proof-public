# Full-chain Receipt Quickstart

This Quickstart explains the public full-chain receipt demo path for **TCD Proof**.

It is designed for two audiences:

1. **Public reviewers** who want to inspect redacted demo artifacts in this public repository.
2. **Authorized technical reviewers** who have access to the private TCD runtime or reviewer bundle and want to reproduce the full-chain local run.

This public repository does **not** contain the private TCD runtime implementation.

## What this validates

A successful full-chain local run validates:

- local HMAC receipt signing
- PolicyStore loading
- SecurityRouter path
- schema-view public receipt projection
- verification bundle exposure
- build/image supply-chain binding
- PQ-required signature path
- durable SQLite `receipt_ref` lookup
- durable SQLite evidence-chain commit
- decision receipt and commit receipt
- by-ref receipt verification
- by-bundle receipt verification
- top-level receipt verification
- storage-window chain verification
- restart-safe durable by-ref verification

## Important boundary

The public Quickstart uses local HMAC signing and local SQLite persistence so reviewers can understand and reproduce the full receipt path in a local or reviewer-bundle setting.

Production deployments can replace local HMAC and SQLite with stronger key-management, storage, coordination, and hardware-root profiles.

This Quickstart should be read as a **test-backed local validation path**, not as a hosted production deployment and not as a complete formal proof of every possible runtime behavior.

## What this public repo does not include

This public repository intentionally does not include:

- private runtime source code
- private policy files
- signing keys
- HMAC secrets
- KMS/HSM credentials
- raw prompts or customer payloads
- local SQLite databases
- local audit logs
- local outbox files
- unredacted execution artifacts
- private receipt bodies from real customer workflows

Generated local artifacts such as `env.sh`, SQLite files, logs, and unredacted receipt bodies should not be committed to this public repository.

---

# Public inspection path

Use this section if you only have access to the public repository.

The public inspection path lets you review the redacted summary and verification report without access to the private TCD runtime.

## 1. Clone the public repository

```bash
git clone https://github.com/amelieliao/tcd-proof-public.git
cd tcd-proof-public
```

## 2. Inspect the redacted full-chain summary

```bash
python3 -m json.tool examples/full-chain-receipt-summary.redacted.json | sed -n '1,260p'
```

## 3. Inspect the redacted verification report

```bash
python3 -m json.tool examples/verify-report.redacted.json | sed -n '1,260p'
```

## 4. Check the most important pass/fail fields

```bash
python3 - <<'PY'
import json

summary = json.load(open("examples/full-chain-receipt-summary.redacted.json", "r", encoding="utf-8"))
checks = summary.get("checks", {})

print("all_checks_pass =", summary.get("all_checks_pass"))

for key in [
    "runtime_receipts",
    "runtime_policy_store_enabled",
    "runtime_security_router_enabled",
    "runtime_receipt_ref_sqlite",
    "runtime_evidence_store_sqlite",
    "runtime_evidence_store_durable",
    "diagnose_has_receipt_public",
    "diagnose_has_receipt_verification",
    "diagnose_has_signature",
    "diagnose_policy_bound",
    "diagnose_supply_chain_bound",
    "diagnose_pq_required",
    "diagnose_pq_signature_ok",
    "diagnose_durable_committed",
    "diagnose_commit_receipt",
    "diagnose_decision_receipt",
    "verify_by_ref_ok",
    "verify_by_bundle_ok",
    "verify_top_level_ok",
    "verify_storage_window_ok",
    "verify_after_restart_by_ref_ok",
]:
    print(f"{key} =", checks.get(key))
PY
```

Expected output includes:

```text
all_checks_pass = True
runtime_receipts = True
runtime_policy_store_enabled = True
runtime_security_router_enabled = True
runtime_receipt_ref_sqlite = True
runtime_evidence_store_sqlite = True
runtime_evidence_store_durable = True
diagnose_durable_committed = True
verify_by_ref_ok = True
verify_by_bundle_ok = True
verify_top_level_ok = True
verify_storage_window_ok = True
verify_after_restart_by_ref_ok = True
```

---

# Authorized local runtime path

Use this section only if you have access to the private TCD runtime repository or an authorized reviewer bundle.

The public repository alone cannot run:

```text
tcd.service_http:create_app
```

## 1. Enter the private runtime repository

```bash
cd ~/tcd-safety-sidecar
```

## 2. Activate the virtual environment

```bash
source venv/bin/activate
```

If your environment is named `.venv`, use:

```bash
source .venv/bin/activate
```

## 3. Confirm Python is available

```bash
which python
python --version
```

## 4. Clean old uvicorn and curl processes

```bash
pkill -f '[u]vicorn .*tcd\.service_http:create_app' || true
pkill -f '[c]url .*127\.0\.0\.1:808[0-4]|[c]url .*localhost:808[0-4]' || true
```

## 5. Clean ports 8080 through 8084

```bash
for port in 8080 8081 8082 8083 8084; do
  lsof -nP -iTCP:${port} -sTCP:LISTEN || true
  for p in $(lsof -tiTCP:${port} -sTCP:LISTEN 2>/dev/null); do kill -9 "$p" 2>/dev/null || true; done
done
```

## 6. Confirm port 8080 is free

```bash
lsof -nP -iTCP:8080 -sTCP:LISTEN || true
```

## 7. Clear old TCD environment variables

```bash
for k in $(env | awk -F= '/^TCD_/{print $1}'); do unset "$k"; done
```

## 8. Create an isolated run directory

```bash
export PYTHON_BIN="$(command -v python || command -v python3)"
export TS="$(date +%Y%m%d_%H%M%S)"
export RUN_DIR="/tmp/tcd-full-receipt-chain-$TS"

mkdir -p "$RUN_DIR"
printf '%s\n' "$RUN_DIR" > /tmp/tcd_full_chain_latest_run_dir

echo "$RUN_DIR"
```

## 9. Confirm policy file availability

```bash
test -f policies.json && echo "policies.json OK" || { echo "ERROR: policies.json missing at $(pwd)/policies.json"; exit 1; }
```

## 10. Create the full-chain runtime environment

This step creates a local demo environment file inside the isolated run directory.

The generated HMAC key is local to this run. Do not commit `env.sh` to any public repository.

```bash
HMAC_HEX="$("$PYTHON_BIN" -c 'import secrets; print(secrets.token_hex(32))')"
IMAGE_DIGEST="$("$PYTHON_BIN" -c 'import hashlib; print("sha256:"+hashlib.sha256(b"tcd-full-chain-image").hexdigest())')"
BUILD_ID="tcd-full-chain-build-$TS"
HMAC_KID="tcd-attestor:hmac:local-full-chain"

cat > "$RUN_DIR/env.sh" <<EOF
export BASE_URL='http://127.0.0.1:8080'

export TCD_HASH_ALG='sha256'
export TCD_ATTEST_HASH_ALG='sha256'
export TCD_ATTEST_AVOID_CRYPTO_BLAKE3='1'

export TCD_ATTEST_HMAC_KEY='hex:$HMAC_HEX'
export TCD_ATTEST_HMAC_KEY_ID='$HMAC_KID'
export TCD_RECEIPT_HMAC_KEY='hex:$HMAC_HEX'
export TCD_RECEIPT_HMAC_KEY_ID='$HMAC_KID'
export TCD_ACTIVE_SIGNING_KEY='$HMAC_KID'

export TCD_KMS_VERIFY_KEY_ALLOWLIST='$HMAC_KID'
export TCD_RECEIPT_VERIFY_KEY_ALLOWLIST='$HMAC_KID'
export TCD_RECEIPT_ENFORCE_VERIFY_KEY_ALLOWLIST='1'
export TCD_KMS_ENFORCE_VERIFY_KEY_ALLOWLIST='1'

export TCD_RECEIPT_REQUIRE_HARDWARE_ROOT='0'
export TCD_K7_REQUIRE_HARDWARE_ROOT='0'
export TCD_HARDWARE_ROOT_POLICY_JSON='{"hardware_policy_ref":"hwpol:local-disabled:v1","keys":[],"trust_anchors":[]}'

export TCD_KMS_ROTATION_PREFLIGHT_REQUIRED='0'
export TCD_RECEIPT_KMS_ROTATION_PREFLIGHT_REQUIRED='0'

export TCD_BUILD_ID='$BUILD_ID'
export TCD_IMAGE_DIGEST='$IMAGE_DIGEST'

export TCD_HTTP_STRICT_MODE='0'
export TCD_HTTP_REQUIRE_TOKEN='0'
export TCD_HTTP_ALLOW_NO_AUTH_LOCAL='1'
export TCD_HTTP_ENABLE_AUTHENTICATOR='1'
export TCD_HTTP_LOCAL_AUTHENTICATOR_FALLBACK_ENABLE='1'

export TCD_HTTP_EDGE_RPS='10000'
export TCD_HTTP_EDGE_BURST='10000'
export TCD_HTTP_SUBJECT_CAPACITY='1000000'
export TCD_HTTP_SUBJECT_REFILL_PER_S='1000000'

export TCD_HTTP_RECEIPTS_ENABLE_DEFAULT='1'
export TCD_HTTP_REQUIRE_RECEIPTS_ON_FAIL='1'
export TCD_HTTP_REQUIRE_RECEIPTS_WHEN_PQ='1'
export TCD_HTTP_REQUIRE_ATTESTOR_WHEN_RECEIPT_REQUIRED='1'
export TCD_HTTP_RECEIPT_SELF_CHECK='1'
export TCD_HTTP_RECEIPT_SELF_CHECK_TIMEOUT_MS='5000'
export TCD_HTTP_RECEIPT_ISSUE_TIMEOUT_MS='5000'
export TCD_HTTP_RECEIPT_VERIFY_TIMEOUT_MS='5000'
export TCD_HTTP_RECEIPT_USE_SCHEMA_VIEW='1'
export TCD_HTTP_RECEIPT_SURFACE_TIMEOUT_MS='5000'
export TCD_HTTP_EXPOSE_VERIFY_KEY_PUBLIC='1'
export TCD_HTTP_EXPOSE_VERIFICATION_BUNDLE_PUBLIC='1'
export TCD_HTTP_EXPOSE_LEGACY_RECEIPT_ALIASES='1'

export TCD_HTTP_REQUIRE_DURABLE_EVIDENCE='1'
export TCD_HTTP_REQUIRE_COMMIT_RECEIPT_AFTER_DURABLE='1'
export TCD_HTTP_RECEIPT_REF_STORE_PATH='$RUN_DIR/receipt_ref.sqlite'
export TCD_HTTP_EVIDENCE_STORE_PATH='$RUN_DIR/evidence.sqlite'
export TCD_HTTP_RECEIPT_EVIDENCE_STORE_PATH='$RUN_DIR/evidence.sqlite'
export TCD_HTTP_EVIDENCE_CHAIN_NAMESPACE='service_http'
export TCD_HTTP_EVIDENCE_CHAIN_ID='receipts'
export TCD_HTTP_EVIDENCE_STORE_CHAIN_LOCK_ENABLE='1'
export TCD_HTTP_EVIDENCE_STORE_RELAX_RECEIPT_BODY_VALIDATION='1'
export TCD_HTTP_EVIDENCE_STORE_RETRY_ATTEMPTS='16'
export TCD_HTTP_RECEIPT_REF_STORE_RETRY_ATTEMPTS='16'

export TCD_POLICY_STORE_ENABLE='1'
export TCD_POLICIES_FILE='$PWD/policies.json'

export TCD_HTTP_SECURITY_ROUTER_ENABLE='1'
export TCD_SECURITY_ROUTER_ENABLE='1'
export TCD_SECURITY_ROUTER_REQUIRED='1'
export TCD_HTTP_REQUIRE_SECURITY_ROUTER='1'
export TCD_SECURITY_ROUTER_USE_STRATEGY='1'
export TCD_SECURITY_ROUTER_ATTESTOR_ENABLE='1'
export TCD_SECURITY_ROUTER_DURABLE_RECEIPTS='1'
export TCD_SECURITY_ROUTER_RECEIPT_REQUIRED_ON_DENY='1'
export TCD_SECURITY_ROUTER_ATTESTATION_REQUIRED_ON_DENY='1'
export TCD_SECURITY_ROUTER_REQUIRE_ATTESTOR_WHEN_REQUIRED='1'
export TCD_SECURITY_ROUTER_REQUIRE_LEDGER_WHEN_REQUIRED='1'
export TCD_SECURITY_ROUTER_LEDGER_REQUIRED_ON_DENY='1'
export TCD_SECURITY_ROUTER_REQUIRE_TERMINAL_GOVERNANCE_FOR_RECEIPT='1'
export TCD_SECURITY_ROUTER_REQUIRE_STORAGE_READY_FOR_RECEIPT='1'
export TCD_SECURITY_ROUTER_LOCAL_LEDGER_ENABLE='1'
export TCD_SECURITY_ROUTER_LOCAL_AUDIT_ENABLE='1'
export TCD_SECURITY_ROUTER_OUTBOX_ENABLE='1'
export TCD_SECURITY_ROUTER_OUTBOX_ENABLED='1'
export TCD_SECURITY_ROUTER_INCLUDE_RECEIPT_VERIFICATION_SURFACE='1'
export TCD_SECURITY_ROUTER_INCLUDE_VERIFY_KEY='1'
export TCD_SECURITY_ROUTER_RECEIPT_SELF_CHECK='1'
export TCD_SECURITY_ROUTER_RECEIPT_SELF_CHECK_TIMEOUT_MS='5000'
export TCD_SECURITY_ROUTER_RECEIPT_ISSUE_TIMEOUT_MS='5000'
export TCD_SECURITY_ROUTER_LEDGER_DB='$RUN_DIR/security_router_ledger.sqlite'
export TCD_LEDGER_DB='$RUN_DIR/security_router_ledger.sqlite'
export TCD_SECURITY_ROUTER_AUDIT_PATH='$RUN_DIR/security_router_audit.jsonl'
export TCD_SECURITY_ROUTER_OUTBOX_AUDIT_PATH='$RUN_DIR/security_router_outbox.jsonl'

export TCD_STORAGE_PROFILE='PROD'
export TCD_STORAGE_DEFAULT_CHAIN_NAMESPACE='service_http'
export TCD_STORAGE_DEFAULT_CHAIN_ID='receipts'
export TCD_STORAGE_VALIDATE_RECEIPT_JSON='1'
export TCD_STORAGE_CANONICALIZE_RECEIPT_BODY='0'
export TCD_STORAGE_VERIFY_RECEIPT_HEAD='0'
export TCD_STORAGE_VERIFY_ATTESTATION_SEMANTICS='0'
export TCD_STORAGE_REJECT_FORBIDDEN_BODY_KEYS='0'
export TCD_STORAGE_ENFORCE_SINGLE_GENESIS='1'
export TCD_STORAGE_REQUIRE_CHAIN_LEAF_APPEND='1'
export TCD_STORAGE_FAIL_CLOSED_CHAIN_AMBIGUITY='1'
export TCD_STORAGE_SERVER_ASSIGN_RECEIPT_CHAIN_POSITION='1'
export TCD_STORAGE_SQLITE_TIMEOUT_S='300'
export TCD_STORAGE_SQLITE_BUSY_TIMEOUT_MS='300000'
export TCD_STORAGE_SQLITE_INIT_LOCK_TIMEOUT_S='300'
export TCD_STORAGE_SQLITE_SYNCHRONOUS='FULL'
export TCD_STORAGE_SQLITE_WAL_AUTOCHECKPOINT='10000'

export TCD_VERIFY_WINDOW_MAX='100000'
export TCD_HTTP_VERIFY_WINDOW_MAX='100000'
EOF
```

## 11. Load the environment

```bash
source "$RUN_DIR/env.sh"
echo "$RUN_DIR"
```

## 12. Confirm key runtime variables

```bash
env | grep -E 'TCD_HTTP_EVIDENCE|TCD_HTTP_RECEIPT_REF|TCD_HTTP_RECEIPT_USE_SCHEMA_VIEW|TCD_POLICY|TCD_SECURITY_ROUTER|TCD_ATTEST|TCD_RECEIPT|TCD_BUILD_ID|TCD_IMAGE_DIGEST' | sort
```

## 13. Generate the full-chain `/diagnose` payload

```bash
"$PYTHON_BIN" - "$RUN_DIR" <<'PY'
import json, os, sys
from pathlib import Path

run = Path(sys.argv[1])
suffix = os.environ.get("TCD_BUILD_ID", "local").replace("tcd-full-chain-build-", "")

payload = {
  "request_id": "req-full-chain-" + suffix,
  "trace_id": "trace-full-chain",
  "idempotency_key": "idem-full-chain-" + suffix,

  "tenant": "demo",
  "user": "fullchain_user",
  "session": "fullchain_session",
  "model_id": "model-full-chain",
  "gpu_id": "gpu-full-chain",
  "task": "chat",
  "lang": "en",

  "trace_vector": [0.11, 0.22, 0.33, 0.44],
  "spectrum": [0.21, 0.31, 0.41],
  "features": [0.15, 0.25, 0.35, 0.45],
  "entropy": 0.37,
  "step_id": 7,
  "tokens_delta": 128,
  "drift_score": 0.01,

  "trust_zone": "internet",
  "route_profile": "admin",
  "risk_label": "critical",
  "threat_kind": "supply_chain",
  "threat_confidence": 0.95,

  "pq_required": True,
  "build_id": os.environ["TCD_BUILD_ID"],
  "image_digest": os.environ["TCD_IMAGE_DIGEST"],
  "compliance_tags": ["finreg", "audit", "pq", "supply_chain"],

  "base_temp": 0.7,
  "base_top_p": 0.9,
  "base_max_tokens": 256,

  "context": {
    "env": "prod",
    "data_class": "regulated",
    "workload": "inference",
    "jurisdiction": "ca",
    "regulation": "finreg",
    "client_app": "curl_full_chain",
    "access_channel": "http",
    "decoder": "default",
    "temperature": 0.7,
    "top_p": 0.9,
    "detector_text": "Full governance diagnostic request for policy routing, durable receipt commit, PQ-required signature, build image binding, audit, outbox, ledger and receipt chain verification.",
    "extra_keywords": ["policy", "audit", "governance", "supply_chain", "pq"]
  }
}

(run / "diagnose.full_chain.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(run / "diagnose.full_chain.json")
PY
```

## 14. Inspect the payload

```bash
python -m json.tool "$RUN_DIR/diagnose.full_chain.json" | sed -n '1,220p'
```

## 15. Compile and preflight

```bash
python -m py_compile tcd/service_http.py tcd/verify.py tcd/storage.py tcd/attest.py tcd/security_router.py tcd/policies.py tcd/receipt_v2.py
```

```bash
python - <<'PY'
import traceback

try:
    import tcd.service_http as s
    print("IMPORT_OK")
    app = s.create_app()
    print("CREATE_APP_OK")
    print(type(app).__name__)
except BaseException:
    traceback.print_exc()
    raise
PY
```

Expected output:

```text
IMPORT_OK
CREATE_APP_OK
FastAPI
```

## 16. Start uvicorn

```bash
pkill -f '[u]vicorn .*tcd\.service_http:create_app' || true
for p in $(lsof -tiTCP:8080 -sTCP:LISTEN 2>/dev/null); do kill -9 "$p" 2>/dev/null || true; done
```

```bash
(
  source "$RUN_DIR/env.sh"
  nohup "$PYTHON_BIN" -m uvicorn tcd.service_http:create_app \
    --factory \
    --host 127.0.0.1 \
    --port 8080 \
    > "$RUN_DIR/uvicorn.log" 2>&1 &
  echo $! > "$RUN_DIR/uvicorn.pid"
)
```

```bash
cat "$RUN_DIR/uvicorn.pid"
```

## 17. Wait for readiness

```bash
READY=0
for i in $(seq 1 120); do
  if curl -fsS "$BASE_URL/healthz" > "$RUN_DIR/healthz.json" 2>/dev/null; then READY=1; break; fi
  sleep 0.25
done

echo "READY=$READY"
python -m json.tool "$RUN_DIR/healthz.json" | sed -n '1,260p'
```

A full-chain-ready runtime should include:

```json
{
  "receipts": true,
  "receipt_ref_store_backend": "sqlite",
  "evidence_store_backend": "sqlite",
  "evidence_store_durable": true,
  "policy_store": true,
  "security_router": true
}
```

If readiness fails, inspect the uvicorn log:

```bash
tail -n 160 "$RUN_DIR/uvicorn.log" 2>/dev/null || true
```

## 18. Capture runtime public state

```bash
curl -sS "$BASE_URL/runtime/public" > "$RUN_DIR/runtime.public.json"
python -m json.tool "$RUN_DIR/runtime.public.json" | sed -n '1,300p'
```

Expected runtime signals include:

```json
{
  "receipt_use_schema_view": true,
  "has_policy_store": true,
  "has_security_router": true,
  "has_attestor": true,
  "receipt_ref_store_backend": "sqlite",
  "evidence_store_backend": "sqlite",
  "evidence_store_durable": true
}
```

## 19. Run `/diagnose`

```bash
curl -sS -D "$RUN_DIR/diagnose.headers.txt" -o "$RUN_DIR/diagnose.body.json" \
  -X POST "$BASE_URL/diagnose" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: full-chain-$TS" \
  --data-binary @"$RUN_DIR/diagnose.full_chain.json"
```

## 20. Inspect `/diagnose` headers

```bash
cat "$RUN_DIR/diagnose.headers.txt"
```

## 21. Inspect `/diagnose` body

```bash
python -m json.tool "$RUN_DIR/diagnose.body.json" | sed -n '1,320p'
```

Expected response shape includes:

- `decision`
- `required_action`
- `policy_ref`
- `policyset_ref`
- `receipt_ref`
- `audit_ref`
- `ledger_ref`
- `commit_ref`
- `attestation_ref`
- `receipt_public`
- `receipt_verification`
- `artifacts`
- `evidence_identity`
- `pq_required`
- `pq_signature_ok`

## 22. Extract core diagnose fields

```bash
python - "$RUN_DIR" <<'PY'
import json, sys
from pathlib import Path

run = Path(sys.argv[1])
r = json.loads((run / "diagnose.body.json").read_text(encoding="utf-8"))

out = {
    "decision": r.get("decision"),
    "allowed": r.get("allowed"),
    "required_action": r.get("required_action"),
    "policy_ref": r.get("policy_ref"),
    "policyset_ref": r.get("policyset_ref"),
    "receipt_ref": r.get("receipt_ref"),
    "audit_ref": r.get("audit_ref"),
    "ledger_ref": r.get("ledger_ref"),
    "commit_ref": r.get("commit_ref"),
    "attestation_ref": r.get("attestation_ref"),
    "pq_required": r.get("pq_required"),
    "pq_signature_ok": r.get("pq_signature_ok"),
    "has_receipt_public": isinstance(r.get("receipt_public"), dict) and bool(r["receipt_public"]),
    "has_receipt_verification": isinstance(r.get("receipt_verification"), dict) and bool(r["receipt_verification"]),
    "artifacts": r.get("artifacts"),
}

print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
PY
```

## 23. Generate verification requests

```bash
python - "$RUN_DIR" <<'PY'
import json, os, sys
from pathlib import Path

run = Path(sys.argv[1])

def load(name):
    try:
        return json.loads((run / name).read_text(encoding="utf-8"))
    except Exception:
        return {}

diag = load("diagnose.body.json")
rv = diag.get("receipt_verification") if isinstance(diag.get("receipt_verification"), dict) else {}
rp = diag.get("receipt_public") if isinstance(diag.get("receipt_public"), dict) else {}
art = diag.get("artifacts") if isinstance(diag.get("artifacts"), dict) else {}
ei = diag.get("evidence_identity") if isinstance(diag.get("evidence_identity"), dict) else {}

def first(*xs):
    for x in xs:
        if x is not None and x != "":
            return x
    return None

policy_ref = first(diag.get("policy_ref"), rv.get("policy_ref"), rp.get("policy_ref"), ei.get("policy_ref"))
policyset_ref = first(diag.get("policyset_ref"), rv.get("policyset_ref"), rp.get("policyset_ref"), ei.get("policyset_ref"))
policy_digest = first(rv.get("policy_digest"), rp.get("policy_digest"), ei.get("policy_digest"), diag.get("policy_digest"))

receipt_cfg = first(rv.get("cfg_fp"), rp.get("cfg_fp"), diag.get("receipt_cfg_fp"), diag.get("route_config_fingerprint"))
service_cfg = diag.get("service_config_fingerprint")

receipt_ref = first(diag.get("receipt_ref"), art.get("receipt_ref"), rv.get("receipt_ref"), rp.get("receipt_ref"))
ledger_ref = first(diag.get("ledger_ref"), art.get("ledger_ref"), art.get("chain_head"))
commit_ref = first(diag.get("commit_ref"), art.get("commit_ref"), ledger_ref)

chain_id = first(art.get("chain_id"), art.get("evidence_store_chain_id"), "receipts")
chain_namespace = first(art.get("chain_namespace"), "service_http")

base_expected = {
    "require_signature": True,
    "pq_required": True,
    "expected_build_id": os.environ.get("TCD_BUILD_ID"),
    "expected_image_digest": os.environ.get("TCD_IMAGE_DIGEST"),
    "expected_service_config_fingerprint": service_cfg,
    "expected_receipt_cfg_fp": receipt_cfg
}

if policy_ref:
    base_expected["expected_policy_ref"] = policy_ref
if policyset_ref:
    base_expected["expected_policyset_ref"] = policyset_ref
if policy_digest:
    base_expected["expected_policy_digest"] = policy_digest

def clean(d):
    return {k: v for k, v in d.items() if v is not None and v != {} and v != [] and v != ""}

by_ref = clean({
    "receipt_ref": receipt_ref,
    **base_expected
})

by_bundle = clean({
    "receipt_verification": rv,
    **base_expected
})

top_level = clean({
    "receipt_head_hex": rv.get("head"),
    "receipt_body_json": rv.get("body"),
    "receipt_sig_hex": rv.get("sig"),
    "verify_key": rv.get("verify_key"),
    "verify_key_id": rv.get("verify_key_id"),
    "sig_key_id": rv.get("sig_key_id"),
    "sig_alg": rv.get("sig_alg"),
    "sig_scheme": rv.get("sig_scheme"),
    "receipt_ref": rv.get("receipt_ref") or receipt_ref,
    **base_expected
})

window = clean({
    "verify_storage_window": True,
    "chain_namespace": chain_namespace,
    "chain_id": chain_id,
    "storage_window_limit": 100,
    "expected_latest_chain_head": commit_ref,
    "expected_ledger_ref": ledger_ref,
    "expected_commit_ref": commit_ref,
    "expected_service_config_fingerprint": service_cfg
})

(run / "verify.by_ref.json").write_text(json.dumps(by_ref, ensure_ascii=False, indent=2), encoding="utf-8")
(run / "verify.by_bundle.json").write_text(json.dumps(by_bundle, ensure_ascii=False, indent=2), encoding="utf-8")
(run / "verify.top_level.json").write_text(json.dumps(top_level, ensure_ascii=False, indent=2), encoding="utf-8")
(run / "verify.storage_window.json").write_text(json.dumps(window, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps({
    "receipt_ref": receipt_ref,
    "policy_ref": policy_ref,
    "policyset_ref": policyset_ref,
    "policy_digest": policy_digest,
    "receipt_cfg_fp": receipt_cfg,
    "service_config_fingerprint": service_cfg,
    "ledger_ref": ledger_ref,
    "commit_ref": commit_ref,
    "chain_namespace": chain_namespace,
    "chain_id": chain_id,
    "build_id": os.environ.get("TCD_BUILD_ID"),
    "image_digest": os.environ.get("TCD_IMAGE_DIGEST")
}, ensure_ascii=False, indent=2))
PY
```

## 24. Run verification

By receipt reference:

```bash
curl -sS -X POST "$BASE_URL/verify" \
  -H "Content-Type: application/json" \
  --data-binary @"$RUN_DIR/verify.by_ref.json" \
  > "$RUN_DIR/verify.by_ref.response.json"
```

By verification bundle:

```bash
curl -sS -X POST "$BASE_URL/verify" \
  -H "Content-Type: application/json" \
  --data-binary @"$RUN_DIR/verify.by_bundle.json" \
  > "$RUN_DIR/verify.by_bundle.response.json"
```

By top-level receipt material:

```bash
curl -sS -X POST "$BASE_URL/verify" \
  -H "Content-Type: application/json" \
  --data-binary @"$RUN_DIR/verify.top_level.json" \
  > "$RUN_DIR/verify.top_level.response.json"
```

By storage-window evidence chain:

```bash
curl -sS -X POST "$BASE_URL/verify" \
  -H "Content-Type: application/json" \
  --data-binary @"$RUN_DIR/verify.storage_window.json" \
  > "$RUN_DIR/verify.storage_window.response.json"
```

## 25. Inspect verification results

```bash
python -m json.tool "$RUN_DIR/verify.by_ref.response.json" | sed -n '1,260p'
```

```bash
python -m json.tool "$RUN_DIR/verify.by_bundle.response.json" | sed -n '1,260p'
```

```bash
python -m json.tool "$RUN_DIR/verify.top_level.response.json" | sed -n '1,260p'
```

```bash
python -m json.tool "$RUN_DIR/verify.storage_window.response.json" | sed -n '1,320p'
```

Expected verification results include:

```json
{
  "ok": true,
  "signature_verified": true,
  "policy_binding_verified": true,
  "cfg_binding_verified": true,
  "build_binding_verified": true,
  "image_binding_verified": true,
  "pq_signature_ok": true,
  "integrity_ok": true
}
```

## 26. Restart and verify durable by-ref lookup

Stop the current uvicorn process:

```bash
OLD_PID="$(cat "$RUN_DIR/uvicorn.pid" 2>/dev/null || true)"
if [ -n "$OLD_PID" ]; then kill "$OLD_PID" 2>/dev/null || true; fi
```

Make sure port 8080 is free:

```bash
sleep 1
for p in $(lsof -tiTCP:8080 -sTCP:LISTEN 2>/dev/null); do kill -9 "$p" 2>/dev/null || true; done
sleep 1
```

Restart uvicorn with the same run environment:

```bash
(
  source "$RUN_DIR/env.sh"
  nohup "$PYTHON_BIN" -m uvicorn tcd.service_http:create_app \
    --factory \
    --host 127.0.0.1 \
    --port 8080 \
    > "$RUN_DIR/uvicorn.restart.log" 2>&1 &
  echo $! > "$RUN_DIR/uvicorn.pid"
)
```

Wait for readiness:

```bash
READY2=0
for i in $(seq 1 120); do
  if curl -fsS "$BASE_URL/healthz" > "$RUN_DIR/healthz.after_restart.json" 2>/dev/null; then READY2=1; break; fi
  sleep 0.25
done

echo "READY_AFTER_RESTART=$READY2"
python -m json.tool "$RUN_DIR/healthz.after_restart.json" | sed -n '1,260p'
```

Verify by receipt reference after restart:

```bash
curl -sS -X POST "$BASE_URL/verify" \
  -H "Content-Type: application/json" \
  --data-binary @"$RUN_DIR/verify.by_ref.json" \
  > "$RUN_DIR/verify.by_ref.after_restart.response.json"
```

Inspect the result:

```bash
python -m json.tool "$RUN_DIR/verify.by_ref.after_restart.response.json" | sed -n '1,280p'
```

Expected after restart:

```json
{
  "ok": true,
  "verify_input_source": "receipt_ref_lookup",
  "signature_verified": true,
  "integrity_ok": true
}
```

## 27. Generate final full-chain summary

```bash
python - "$RUN_DIR" <<'PY'
import json, sys
from pathlib import Path

run = Path(sys.argv[1])

def load(name):
    try:
        return json.loads((run / name).read_text(encoding="utf-8"))
    except Exception:
        return {}

health = load("healthz.json")
runtime = load("runtime.public.json")
diag = load("diagnose.body.json")
by_ref = load("verify.by_ref.response.json")
by_bundle = load("verify.by_bundle.response.json")
top = load("verify.top_level.response.json")
window = load("verify.storage_window.response.json")
after = load("verify.by_ref.after_restart.response.json")

art = diag.get("artifacts") if isinstance(diag.get("artifacts"), dict) else {}
rv = diag.get("receipt_verification") if isinstance(diag.get("receipt_verification"), dict) else {}
rp = diag.get("receipt_public") if isinstance(diag.get("receipt_public"), dict) else {}
ei = diag.get("evidence_identity") if isinstance(diag.get("evidence_identity"), dict) else {}
comp = diag.get("components") if isinstance(diag.get("components"), dict) else {}
sec_router = comp.get("security_router") if isinstance(comp.get("security_router"), dict) else {}

def report_ok(x):
    return bool(isinstance(x, dict) and x.get("ok") is True)

def report(x):
    return x.get("report") if isinstance(x, dict) and isinstance(x.get("report"), dict) else {}

by_ref_report = report(by_ref)
by_bundle_report = report(by_bundle)
top_report = report(top)
window_report = report(window)
after_report = report(after)

receipt_verify_reports = [
    by_ref_report,
    by_bundle_report,
    top_report,
    after_report,
]

diagnose_supply_chain_surface_present = bool(
    (
        diag.get("build_id")
        or rv.get("build_id")
        or rp.get("build_id")
        or ei.get("build_id")
        or art.get("build_id")
    )
    and
    (
        diag.get("image_digest")
        or rv.get("image_digest")
        or rp.get("image_digest")
        or ei.get("image_digest")
        or art.get("image_digest")
    )
)

verify_supply_chain_binding_verified = bool(
    receipt_verify_reports
    and all(
        r.get("build_binding_verified") is True
        and r.get("image_binding_verified") is True
        for r in receipt_verify_reports
    )
)

supply_chain_bound = bool(
    diagnose_supply_chain_surface_present
    or verify_supply_chain_binding_verified
)

checks = {
    "runtime_receipts": bool(health.get("receipts")),
    "runtime_schema_view_enabled": runtime.get("receipt_use_schema_view") is True,
    "runtime_policy_store_enabled": bool(runtime.get("has_policy_store") or health.get("policy_store")),
    "runtime_security_router_enabled": bool(runtime.get("has_security_router") or health.get("security_router")),
    "runtime_receipt_ref_sqlite": health.get("receipt_ref_store_backend") == "sqlite",
    "runtime_evidence_store_sqlite": health.get("evidence_store_backend") == "sqlite",
    "runtime_evidence_store_durable": health.get("evidence_store_durable") is True,

    "diagnose_has_receipt_public": bool(rp.get("head") and rp.get("receipt_ref")),
    "diagnose_has_receipt_verification": bool(rv.get("head") and rv.get("body")),
    "diagnose_has_signature": bool(rv.get("sig") and (rv.get("verify_key") or rv.get("verify_key_id"))),
    "diagnose_policy_bound": bool(diag.get("policy_ref") or rp.get("policy_ref") or rv.get("policy_ref")),
    "diagnose_supply_chain_bound": supply_chain_bound,
    "diagnose_pq_required": diag.get("pq_required") is True or rv.get("pq_required") is True or rp.get("pq_required") is True,
    "diagnose_pq_signature_ok": diag.get("pq_signature_ok") is True or rv.get("pq_signature_ok") is True or rp.get("pq_signature_ok") is True,
    "diagnose_durable_committed": bool(art.get("evidence_durable") is True and art.get("evidence_storage_ready") is True and art.get("ledger_stage") == "committed"),
    "diagnose_commit_receipt": bool(art.get("commit_receipt_ref") or art.get("commit_receipt_head")),
    "diagnose_decision_receipt": bool(art.get("decision_receipt_ref") or art.get("decision_receipt_head")),
    "diagnose_attestation_ref": bool(diag.get("attestation_ref") or art.get("attestation_ref")),
    "diagnose_audit_ref": bool(diag.get("audit_ref") or art.get("audit_ref")),
    "diagnose_security_router_surface": bool(sec_router),

    "verify_by_ref_ok": report_ok(by_ref),
    "verify_by_bundle_ok": report_ok(by_bundle),
    "verify_top_level_ok": report_ok(top),
    "verify_storage_window_ok": report_ok(window),
    "verify_after_restart_by_ref_ok": report_ok(after),
}

summary = {
    "run_dir": str(run),
    "all_checks_pass": all(checks.values()),
    "checks": checks,
    "supply_chain_binding": {
        "diagnose_supply_chain_surface_present": diagnose_supply_chain_surface_present,
        "verify_supply_chain_binding_verified": verify_supply_chain_binding_verified,
        "build_id": (
            diag.get("build_id")
            or rv.get("build_id")
            or rp.get("build_id")
            or ei.get("build_id")
            or art.get("build_id")
            or by_ref_report.get("build_id")
            or by_bundle_report.get("build_id")
            or top_report.get("build_id")
            or after_report.get("build_id")
        ),
        "image_digest": (
            diag.get("image_digest")
            or rv.get("image_digest")
            or rp.get("image_digest")
            or ei.get("image_digest")
            or art.get("image_digest")
            or by_ref_report.get("image_digest")
            or by_bundle_report.get("image_digest")
            or top_report.get("image_digest")
            or after_report.get("image_digest")
        ),
        "by_ref_build_binding_verified": by_ref_report.get("build_binding_verified"),
        "by_ref_image_binding_verified": by_ref_report.get("image_binding_verified"),
        "by_bundle_build_binding_verified": by_bundle_report.get("build_binding_verified"),
        "by_bundle_image_binding_verified": by_bundle_report.get("image_binding_verified"),
        "top_level_build_binding_verified": top_report.get("build_binding_verified"),
        "top_level_image_binding_verified": top_report.get("image_binding_verified"),
        "after_restart_build_binding_verified": after_report.get("build_binding_verified"),
        "after_restart_image_binding_verified": after_report.get("image_binding_verified"),
    },
    "diagnose_core": {
        "decision": diag.get("decision"),
        "allowed": diag.get("allowed"),
        "required_action": diag.get("required_action"),
        "policy_ref": diag.get("policy_ref") or rp.get("policy_ref") or rv.get("policy_ref"),
        "policyset_ref": diag.get("policyset_ref") or rp.get("policyset_ref") or rv.get("policyset_ref"),
        "receipt_ref": diag.get("receipt_ref") or art.get("receipt_ref") or rp.get("receipt_ref") or rv.get("receipt_ref"),
        "ledger_ref": diag.get("ledger_ref") or art.get("ledger_ref"),
        "commit_ref": diag.get("commit_ref") or art.get("commit_ref"),
        "audit_ref": diag.get("audit_ref") or art.get("audit_ref"),
        "attestation_ref": diag.get("attestation_ref") or art.get("attestation_ref"),
        "receipt_surface_kind": art.get("receipt_surface_kind"),
        "receipt_delivery_state": art.get("receipt_delivery_state"),
        "ledger_stage": art.get("ledger_stage"),
        "evidence_durable": art.get("evidence_durable"),
        "evidence_storage_ready": art.get("evidence_storage_ready"),
        "pq_required": diag.get("pq_required") or rv.get("pq_required") or rp.get("pq_required"),
        "pq_signature_ok": diag.get("pq_signature_ok") or rv.get("pq_signature_ok") or rp.get("pq_signature_ok"),
    },
    "verify_reports": {
        "by_ref": by_ref_report,
        "by_bundle": by_bundle_report,
        "top_level": top_report,
        "storage_window": window_report,
        "after_restart_by_ref": after_report,
    }
}

(run / "FULL_CHAIN_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
PY
```

## 28. Check final pass/fail result

```bash
python - "$RUN_DIR" <<'PY'
import json, sys
from pathlib import Path

run = Path(sys.argv[1])
summary = json.loads((run / "FULL_CHAIN_SUMMARY.json").read_text(encoding="utf-8"))

print("RUN_DIR=", summary.get("run_dir"))
print("ALL_CHECKS_PASS=", summary.get("all_checks_pass"))

for k, v in sorted((summary.get("checks") or {}).items()):
    print(f"{k}={v}")

print("SUPPLY_CHAIN_BINDING=", json.dumps(summary.get("supply_chain_binding"), ensure_ascii=False, sort_keys=True))

raise SystemExit(0 if summary.get("all_checks_pass") is True else 1)
PY
```

Expected final result:

```text
ALL_CHECKS_PASS= True
diagnose_supply_chain_bound=True
verify_after_restart_by_ref_ok=True
```

## 29. Inspect final summary file

```bash
python -m json.tool "$RUN_DIR/FULL_CHAIN_SUMMARY.json" | sed -n '1,260p'
```

The final local artifact is written to:

```text
/tmp/tcd-full-receipt-chain-<timestamp>/FULL_CHAIN_SUMMARY.json
```

The latest run directory is recorded at:

```text
/tmp/tcd_full_chain_latest_run_dir
```

## 30. List generated run artifacts

```bash
find "$RUN_DIR" -maxdepth 1 -type f | sort
```

Expected artifacts include:

```text
diagnose.body.json
diagnose.full_chain.json
diagnose.headers.txt
env.sh
healthz.json
healthz.after_restart.json
runtime.public.json
verify.by_ref.json
verify.by_ref.response.json
verify.by_ref.after_restart.response.json
verify.by_bundle.json
verify.by_bundle.response.json
verify.top_level.json
verify.top_level.response.json
verify.storage_window.json
verify.storage_window.response.json
FULL_CHAIN_SUMMARY.json
```

Do not commit `env.sh`, local SQLite files, logs, or unredacted runtime artifacts to a public repository.

## 31. Cleanup

```bash
OLD_PID="$(cat "$RUN_DIR/uvicorn.pid" 2>/dev/null || true)"
if [ -n "$OLD_PID" ]; then kill "$OLD_PID" 2>/dev/null || true; fi

for p in $(lsof -tiTCP:8080 -sTCP:LISTEN 2>/dev/null); do kill -9 "$p" 2>/dev/null || true; done

lsof -nP -iTCP:8080 -sTCP:LISTEN || true
```

---

# Interpretation notes

## Supply-chain binding

In some runs, this field may be false:

```json
{
  "diagnose_supply_chain_surface_present": false
}
```

while this field is true:

```json
{
  "verify_supply_chain_binding_verified": true
}
```

That means the public `/diagnose` receipt surface did not directly expose build/image fields, but the independent verification reports confirmed build and image binding.

For audit review, the stronger verification-backed statement is:

```json
{
  "verify_supply_chain_binding_verified": true,
  "build_binding_verified": true,
  "image_binding_verified": true
}
```

## Local HMAC and SQLite boundary

The public local run uses:

```json
{
  "signing": "local_hmac_demo",
  "storage": "local_sqlite_demo",
  "hardware_root_required": false
}
```

This is intentional for local reproducibility.

Production deployments can use stronger key-management, storage, coordination, and hardware-root profiles.

## What this Quickstart does not claim

This Quickstart does not claim:

- global consensus
- production HSM deployment
- hardware-rooted signing in the public local run
- raw customer-data inspection
- formal mathematical proof of every runtime behavior

It demonstrates a local, test-backed, full-chain governed receipt path using local HMAC signing and local SQLite persistence.

---

# Expected redacted result shape

A representative successful run should end with a redacted summary shaped like:

```json
{
  "all_checks_pass": true,
  "checks": {
    "runtime_receipts": true,
    "runtime_schema_view_enabled": true,
    "runtime_policy_store_enabled": true,
    "runtime_security_router_enabled": true,
    "runtime_receipt_ref_sqlite": true,
    "runtime_evidence_store_sqlite": true,
    "runtime_evidence_store_durable": true,
    "diagnose_has_receipt_public": true,
    "diagnose_has_receipt_verification": true,
    "diagnose_has_signature": true,
    "diagnose_policy_bound": true,
    "diagnose_supply_chain_bound": true,
    "diagnose_pq_required": true,
    "diagnose_pq_signature_ok": true,
    "diagnose_durable_committed": true,
    "diagnose_commit_receipt": true,
    "diagnose_decision_receipt": true,
    "diagnose_attestation_ref": true,
    "diagnose_audit_ref": true,
    "diagnose_security_router_surface": true,
    "verify_by_ref_ok": true,
    "verify_by_bundle_ok": true,
    "verify_top_level_ok": true,
    "verify_storage_window_ok": true,
    "verify_after_restart_by_ref_ok": true
  },
  "diagnose_core": {
    "decision": "block",
    "allowed": false,
    "required_action": "block",
    "policy_ref": "block_internet_admin@v1#<redacted>",
    "policyset_ref": "set@1#<redacted>",
    "receipt_ref": "<receipt-ref>",
    "ledger_ref": "<ledger-head>",
    "commit_ref": "<commit-head>",
    "audit_ref": "<audit-ref>",
    "attestation_ref": "<attestation-ref>",
    "receipt_surface_kind": "durable_committed",
    "receipt_delivery_state": "committed",
    "ledger_stage": "committed",
    "evidence_durable": true,
    "evidence_storage_ready": true,
    "pq_required": true,
    "pq_signature_ok": true
  },
  "supply_chain_binding": {
    "diagnose_supply_chain_surface_present": false,
    "verify_supply_chain_binding_verified": true,
    "build_id": "tcd-full-chain-build-<timestamp>",
    "image_digest": "sha256:<redacted>",
    "by_ref_build_binding_verified": true,
    "by_ref_image_binding_verified": true,
    "by_bundle_build_binding_verified": true,
    "by_bundle_image_binding_verified": true,
    "top_level_build_binding_verified": true,
    "top_level_image_binding_verified": true,
    "after_restart_build_binding_verified": true,
    "after_restart_image_binding_verified": true
  }
}
```