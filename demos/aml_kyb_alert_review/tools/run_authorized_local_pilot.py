#!/usr/bin/env python3
"""Run the AML/KYB action-assurance pilot against an authorized local runtime.

The public repository alone cannot execute the private runtime. This runner is
for reviewers who have both repositories locally. It snapshots the private
runtime into /tmp, runs the service from that snapshot, stores raw local results
under /tmp, and exports only redacted public artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib import request as urlrequest
from urllib.error import URLError


DEMO_REL = Path("demos/aml_kyb_alert_review")
ENTRYPOINT = "tcd.service_http:create_app"
DIAGNOSE_ENDPOINT = "/diagnose"
VERIFY_ENDPOINT = "/verify"


EXCLUDE_DIRS = {
    ".git",
    "venv",
    ".venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "htmlcov",
    ".tcd_runtime",
    "test-results",
    "demo_artifacts",
    "runtime_artifacts",
}
EXCLUDE_SUFFIXES = (
    ".sqlite",
    ".sqlite3",
    ".sqlite-wal",
    ".sqlite-shm",
    ".db",
    ".db-wal",
    ".db-shm",
    ".log",
    ".pid",
    ".pem",
    ".key",
    ".coverage",
    ".tar.gz",
    ".zip",
)
EXCLUDE_PREFIXES = ("FINAL_", "M2_", "M3_", "M4_", "M5_", "M6_", "M7_", "M8_", "K4_", "K7_")


def parse_args() -> argparse.Namespace:
    here = Path(__file__).resolve()
    default_public = here.parents[3]
    default_runtime = default_public.parent / "tcd-safety-sidecar"
    return argparse.ArgumentParser(description=__doc__).parse_args(
        None if len(sys.argv) > 1 else []
    ) if False else _build_parser(default_public, default_runtime).parse_args()


def _build_parser(default_public: Path, default_runtime: Path) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the authorized local AML/KYB pilot")
    parser.add_argument("--runtime-root", type=Path, default=default_runtime)
    parser.add_argument("--public-root", type=Path, default=default_public)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--keep-temp", action="store_true")
    parser.add_argument("--skip-restart", action="store_true")
    return parser


def fail(message: str) -> None:
    raise SystemExit(message)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def post_json(base_url: str, path: str, payload: Any, *, timeout: float = 30.0) -> Any:
    data = json.dumps(payload, sort_keys=True).encode("utf-8")
    req = urlrequest.Request(
        base_url + path,
        data=data,
        headers={"Content-Type": "application/json", "X-Request-Id": "aml-kyb-pilot"},
        method="POST",
    )
    with urlrequest.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def get_json(base_url: str, path: str, *, timeout: float = 5.0) -> Any:
    with urlrequest.urlopen(base_url + path, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def ignore_runtime_artifacts(_dir: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in EXCLUDE_DIRS:
            ignored.add(name)
            continue
        if name.startswith(EXCLUDE_PREFIXES):
            ignored.add(name)
            continue
        if ".bak" in name:
            ignored.add(name)
            continue
        if name in {"env.sh"} or name.startswith(".env"):
            ignored.add(name)
            continue
        if name.endswith(EXCLUDE_SUFFIXES):
            ignored.add(name)
    return ignored


def snapshot_runtime(runtime_root: Path, snapshot: Path) -> None:
    shutil.copytree(runtime_root, snapshot, ignore=ignore_runtime_artifacts)


def choose_python(runtime_root: Path) -> Path:
    candidate = runtime_root / "venv" / "bin" / "python"
    if candidate.exists() and os.access(candidate, os.X_OK):
        return candidate
    return Path(sys.executable)


def scenario_files(public_root: Path) -> list[tuple[dict[str, Any], Path]]:
    scenario_dir = public_root / DEMO_REL / "scenarios"
    manifest = load_json(scenario_dir / "scenario_manifest.json")
    out: list[tuple[dict[str, Any], Path]] = []
    for item in manifest.get("scenarios", []):
        req_file = scenario_dir / str(item["request_file"])
        out.append((dict(item), req_file))
    return out


def make_env(pycache_dir: Path, tmp_dir: Path, snapshot: Path, state: Path, run_id: str) -> dict[str, str]:
    hmac_hex = hashlib.sha256((run_id + ":hmac").encode("utf-8")).hexdigest()
    image_hex = hashlib.sha256((run_id + ":image").encode("utf-8")).hexdigest()
    env = os.environ.copy()
    env.update(
        {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPYCACHEPREFIX": str(pycache_dir),
            "TMPDIR": str(tmp_dir),
            "PYTHONPATH": str(snapshot),
            "TCD_HASH_ALG": "sha256",
            "TCD_BUILD_ID": f"aml-kyb-pilot-build-{run_id}",
            "TCD_IMAGE_DIGEST": f"sha256:{image_hex}",
            "TCD_ATTEST_HMAC_KEY": f"hex:{hmac_hex}",
            "TCD_RECEIPT_HMAC_KEY": f"hex:{hmac_hex}",
            "TCD_ATTEST_HMAC_KEY_ID": "aml-kyb-pilot-hmac",
            "TCD_RECEIPT_HMAC_KEY_ID": "aml-kyb-pilot-hmac",
            "TCD_HTTP_ENABLE_DOCS": "0",
            "TCD_HTTP_STRICT_MODE": "0",
            "TCD_HTTP_REQUIRE_TOKEN": "0",
            "TCD_HTTP_ALLOW_NO_AUTH_LOCAL": "1",
            "TCD_HTTP_ENABLE_AUTHENTICATOR": "1",
            "TCD_HTTP_LOCAL_AUTHENTICATOR_FALLBACK_ENABLE": "1",
            "TCD_HTTP_RECEIPTS_ENABLE_DEFAULT": "1",
            "TCD_HTTP_REQUIRE_RECEIPTS_ON_FAIL": "1",
            "TCD_HTTP_REQUIRE_RECEIPTS_WHEN_PQ": "1",
            "TCD_HTTP_REQUIRE_ATTESTOR_WHEN_RECEIPT_REQUIRED": "1",
            "TCD_HTTP_REQUIRE_FINAL_RECEIPT_SURFACE_STRICT": "1",
            "TCD_HTTP_EXPOSE_VERIFICATION_BUNDLE_PUBLIC": "1",
            "TCD_HTTP_EXPOSE_VERIFY_KEY_PUBLIC": "1",
            "TCD_HTTP_EXPOSE_LEGACY_RECEIPT_ALIASES": "0",
            "TCD_HTTP_RECEIPT_SELF_CHECK": "1",
            "TCD_HTTP_RECEIPT_ISSUE_TIMEOUT_MS": "5000",
            "TCD_HTTP_RECEIPT_SELF_CHECK_TIMEOUT_MS": "5000",
            "TCD_HTTP_RECEIPT_VERIFY_TIMEOUT_MS": "5000",
            "TCD_HTTP_RECEIPT_SURFACE_TIMEOUT_MS": "5000",
            "TCD_HTTP_RECEIPT_USE_SCHEMA_VIEW": "1",
            "TCD_VERIFY_RECEIPT_BODY_MAXBYTES": "1048576",
            "TCD_HTTP_MAX_BODY_BYTES": "1048576",
            "TCD_HTTP_MAX_JSON_COMPONENT_BYTES": "524288",
            "TCD_HTTP_RECEIPT_REF_STORE_PATH": str(state / "receipt_refs.sqlite3"),
            "TCD_HTTP_EVIDENCE_STORE_PATH": str(state / "evidence.sqlite3"),
            "TCD_HTTP_REQUIRE_DURABLE_EVIDENCE": "1",
            "TCD_HTTP_REQUIRE_COMMIT_RECEIPT_AFTER_DURABLE": "1",
            "TCD_HTTP_EVIDENCE_CHAIN_NAMESPACE": "service_http",
            "TCD_HTTP_EVIDENCE_CHAIN_ID": "receipts_aml_kyb_pilot",
            "TCD_POLICY_STORE_ENABLE": "1",
            "TCD_HTTP_SECURITY_ROUTER_ENABLE": "1",
            "TCD_SECURITY_ROUTER_ENABLE": "1",
            "TCD_SECURITY_ROUTER_ATTESTOR_ENABLE": "1",
            "TCD_SECURITY_ROUTER_DURABLE_RECEIPTS": "1",
            "TCD_SECURITY_ROUTER_REQUIRE_LEDGER_WHEN_REQUIRED": "1",
            "TCD_SECURITY_ROUTER_REQUIRE_STORAGE_READY_FOR_RECEIPT": "1",
            "TCD_SECURITY_ROUTER_REQUIRE_TERMINAL_GOVERNANCE_FOR_RECEIPT": "1",
            "TCD_SECURITY_ROUTER_LOCAL_LEDGER_ENABLE": "1",
            "TCD_SECURITY_ROUTER_LOCAL_AUDIT_ENABLE": "1",
            "TCD_SECURITY_ROUTER_OUTBOX_ENABLE": "1",
            "TCD_SECURITY_ROUTER_LEDGER_DB": str(state / "security_router_ledger.sqlite3"),
            "TCD_LEDGER_DB": str(state / "ledger.sqlite3"),
            "TCD_SECURITY_ROUTER_AUDIT_PATH": str(state / "security_router_audit.log"),
            "TCD_SECURITY_ROUTER_OUTBOX_AUDIT_PATH": str(state / "security_router_outbox.log"),
            "TCD_SECURITY_ROUTER_OUTBOX_DB": str(state / "security_router_outbox.sqlite3"),
        }
    )
    return env


def start_service(py: Path, snapshot: Path, env: dict[str, str], port: int, log_path: Path) -> subprocess.Popen[bytes]:
    log_f = log_path.open("wb")
    proc = subprocess.Popen(
        [
            str(py),
            "-m",
            "uvicorn",
            ENTRYPOINT,
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=str(snapshot),
        env=env,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    proc._tcd_log_file = log_f  # type: ignore[attr-defined]
    return proc


def stop_service(proc: subprocess.Popen[bytes] | None) -> bool:
    if proc is None:
        return True
    if proc.poll() is not None:
        log_f = getattr(proc, "_tcd_log_file", None)
        if log_f:
            log_f.close()
        return True
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5)
    log_f = getattr(proc, "_tcd_log_file", None)
    if log_f:
        log_f.close()
    return proc.poll() is not None


def wait_ready(base_url: str, raw_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    deadline = time.time() + 45
    last_error = ""
    while time.time() < deadline:
        try:
            health = get_json(base_url, "/healthz", timeout=2)
            runtime = get_json(base_url, "/runtime/public", timeout=2)
            write_json(raw_dir / "healthz.json", health)
            write_json(raw_dir / "runtime_public.json", runtime)
            return health, runtime
        except (URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            time.sleep(0.25)
    fail(f"service did not become ready: {last_error}")


def first_present(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def extract_surfaces(resp: dict[str, Any]) -> dict[str, Any]:
    components = resp.get("components") if isinstance(resp.get("components"), dict) else {}
    artifacts = resp.get("artifacts") if isinstance(resp.get("artifacts"), dict) else components.get("artifacts", {})
    evidence = resp.get("evidence_identity") if isinstance(resp.get("evidence_identity"), dict) else components.get("evidence_identity", {})
    receipt_public = resp.get("receipt_public") if isinstance(resp.get("receipt_public"), dict) else components.get("receipt", {})
    receipt_verification = resp.get("receipt_verification") if isinstance(resp.get("receipt_verification"), dict) else components.get("receipt_verification", {})
    return {
        "components": components,
        "artifacts": artifacts or {},
        "evidence": evidence or {},
        "receipt_public": receipt_public or {},
        "receipt_verification": receipt_verification or {},
    }


def verify_payload(resp: dict[str, Any], env: dict[str, str], *, by_ref_only: bool = False) -> dict[str, Any]:
    surfaces = extract_surfaces(resp)
    evidence = surfaces["evidence"]
    receipt_public = surfaces["receipt_public"]
    receipt_verification = surfaces["receipt_verification"]
    receipt_ref = first_present(
        resp.get("receipt_ref"),
        surfaces["artifacts"].get("receipt_ref"),
        evidence.get("receipt_ref"),
        receipt_public.get("receipt_ref"),
        receipt_verification.get("receipt_ref"),
    )
    receipt_cfg_fp = first_present(
        resp.get("receipt_cfg_fp"),
        receipt_public.get("cfg_fp"),
        receipt_verification.get("cfg_fp"),
        resp.get("route_config_fingerprint"),
        resp.get("config_fingerprint"),
    )
    service_cfg = resp.get("service_config_fingerprint")
    payload: dict[str, Any] = {
        "receipt_ref": receipt_ref,
        "pq_required": True,
        "require_signature": True,
        "expected_build_id": env["TCD_BUILD_ID"],
        "expected_image_digest": env["TCD_IMAGE_DIGEST"],
        "expected_service_config_fingerprint": service_cfg,
        "expected_receipt_cfg_fp": receipt_cfg_fp,
    }
    if not by_ref_only:
        payload["receipt_verification"] = receipt_verification
    policy_ref = first_present(resp.get("policy_ref"), evidence.get("policy_ref"), receipt_public.get("policy_ref"), receipt_verification.get("policy_ref"))
    policyset_ref = first_present(resp.get("policyset_ref"), evidence.get("policyset_ref"), receipt_public.get("policyset_ref"), receipt_verification.get("policyset_ref"))
    policy_digest = first_present(receipt_public.get("policy_digest"), receipt_verification.get("policy_digest"), evidence.get("policy_digest"))
    if policy_ref:
        payload["expected_policy_ref"] = policy_ref
    if policyset_ref:
        payload["expected_policyset_ref"] = policyset_ref
    if policy_digest:
        payload["expected_policy_digest"] = policy_digest
    return payload


def main() -> int:
    args = parse_args()
    public_root = args.public_root.resolve()
    runtime_root = args.runtime_root.resolve()
    if public_root.name != "tcd-proof-public":
        fail(f"public-root basename must be tcd-proof-public: {public_root}")
    if runtime_root.name != "tcd-safety-sidecar":
        fail(f"runtime-root basename must be tcd-safety-sidecar: {runtime_root}")
    demo_root = public_root / DEMO_REL
    output_dir = (args.output_dir or demo_root / "run_derived").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    run_dir = Path(tempfile.mkdtemp(prefix="tcd-aml-kyb-pilot-", dir="/tmp"))
    snapshot = run_dir / "runtime_snapshot"
    state = run_dir / "state"
    logs = run_dir / "logs"
    raw = run_dir / "raw"
    redacted_tmp = run_dir / "redacted"
    pycache = run_dir / "pycache"
    tmp_dir = run_dir / "tmp"
    for path in (state, logs, raw, redacted_tmp, pycache, tmp_dir):
        path.mkdir(parents=True, exist_ok=True)

    proc: subprocess.Popen[bytes] | None = None
    restart_proc: subprocess.Popen[bytes] | None = None
    try:
        snapshot_runtime(runtime_root, snapshot)
        py = choose_python(runtime_root)
        run_id = time.strftime("%Y%m%d%H%M%S")
        env = make_env(pycache, tmp_dir, snapshot, state, run_id)
        port = find_free_port()
        base_url = f"http://127.0.0.1:{port}"

        proc = start_service(py, snapshot, env, port, logs / "uvicorn.log")
        health, runtime_public = wait_ready(base_url, raw)

        scenario_results: list[dict[str, Any]] = []
        for scenario, req_path in scenario_files(public_root):
            payload = load_json(req_path)
            payload["build_id"] = env["TCD_BUILD_ID"]
            payload["image_digest"] = env["TCD_IMAGE_DIGEST"]
            response = post_json(base_url, DIAGNOSE_ENDPOINT, payload)
            scenario_id = scenario["scenario_id"]
            write_json(raw / f"{scenario_id}.diagnose.request.json", payload)
            write_json(raw / f"{scenario_id}.diagnose.response.json", response)
            vp = verify_payload(response, env)
            write_json(raw / f"{scenario_id}.verify.request.json", vp)
            verify_response = post_json(base_url, VERIFY_ENDPOINT, vp)
            write_json(raw / f"{scenario_id}.verify.response.json", verify_response)
            scenario_results.append(
                {
                    "scenario": scenario,
                    "request_file": str(req_path.name),
                    "diagnose_response_file": f"{scenario_id}.diagnose.response.json",
                    "verify_response_file": f"{scenario_id}.verify.response.json",
                    "diagnose": response,
                    "verify_request": vp,
                    "verify_response": verify_response,
                }
            )

        successful = [r for r in scenario_results if r["verify_response"].get("ok") is True]
        if not successful:
            fail("no scenario produced a successful verification")
        negative_base = successful[0]
        wrong_payload = dict(negative_base["verify_request"])
        wrong_payload["expected_build_id"] = "wrong-build-id-for-negative-verification"
        wrong_response = post_json(base_url, VERIFY_ENDPOINT, wrong_payload)
        if wrong_response.get("ok") is not False:
            fail("wrong-binding verification did not fail")
        write_json(raw / "wrong_binding.verify.request.json", wrong_payload)
        write_json(raw / "wrong_binding.verify.response.json", wrong_response)

        stopped = stop_service(proc)
        proc = None
        if not stopped:
            fail("initial service process did not stop")

        restart_response: dict[str, Any] | None = None
        restart_payload: dict[str, Any] | None = None
        if not args.skip_restart:
            restart_proc = start_service(py, snapshot, env, port, logs / "uvicorn_restart.log")
            wait_ready(base_url, raw)
            restart_payload = verify_payload(negative_base["diagnose"], env, by_ref_only=True)
            write_json(raw / "restart_safe.verify_by_ref.request.json", restart_payload)
            restart_response = post_json(base_url, VERIFY_ENDPOINT, restart_payload)
            if restart_response.get("ok") is not True:
                fail("restart-safe receipt_ref verification failed")
            source = restart_response.get("report", {}).get("verify_input_source")
            if source != "receipt_ref_lookup":
                fail(f"restart verify source was not receipt_ref_lookup: {source}")
            write_json(raw / "restart_safe.verify_by_ref.response.json", restart_response)
            stopped = stop_service(restart_proc)
            restart_proc = None
            if not stopped:
                fail("restart service process did not stop")

        raw_summary = {
            "schema": "tcd.private_raw.aml_kyb_pilot_summary.v1",
            "run_id": run_id,
            "service_entrypoint": ENTRYPOINT,
            "diagnose_endpoint": DIAGNOSE_ENDPOINT,
            "verify_endpoint": VERIFY_ENDPOINT,
            "health": health,
            "runtime_public": runtime_public,
            "scenario_results": scenario_results,
            "wrong_binding": {
                "request": wrong_payload,
                "response": wrong_response,
            },
            "restart_safe": {
                "skipped": bool(args.skip_restart),
                "request": restart_payload,
                "response": restart_response,
            },
        }
        write_json(raw / "pilot_raw_summary.json", raw_summary)

        redactor = demo_root / "tools" / "redact_and_export.py"
        renderer = demo_root / "tools" / "render_assurance_packet.py"
        validator = demo_root / "tools" / "validate_public_export.py"
        subprocess.run(
            [
                sys.executable,
                str(redactor),
                "--raw-dir",
                str(raw),
                "--output-dir",
                str(output_dir),
                "--scenario-manifest",
                str(demo_root / "scenarios" / "scenario_manifest.json"),
            ],
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(renderer),
                "--demo-root",
                str(demo_root),
            ],
            check=True,
        )
        subprocess.run([sys.executable, str(validator), "--demo-root", str(demo_root)], check=True)
        write_json(
            run_dir / "completion_marker.json",
            {
                "schema": "tcd.public.aml_kyb_pilot_completion.v1",
                "status": "complete_success",
                "scenario_count": len(scenario_results),
                "verify_ok": any(r["verify_response"].get("ok") is True for r in scenario_results),
                "wrong_binding_failure": wrong_response.get("ok") is False,
                "restart_safe_verify": bool(restart_response and restart_response.get("ok") is True),
                "raw_artifacts_location": "tmp_run_directory_only",
                "public_artifacts": "run_derived_redacted_only",
            },
        )
        print(json.dumps({"ok": True, "run_dir": str(run_dir), "output_dir": str(output_dir)}, sort_keys=True))
        return 0
    finally:
        stop_service(proc)
        stop_service(restart_proc)
        if not args.keep_temp:
            shutil.rmtree(run_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
