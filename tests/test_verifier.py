from __future__ import annotations

import base64
import copy
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from jsonschema import validate

from tcd_verifier.canonical import canonical_json_bytes, signed_body_bytes
from tcd_verifier.verify import verify_files
from tcd_verifier.verify import public_key_fingerprint


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "fixtures" / "verifier_v0_1"


EXPECTED_CASES = {
    "valid": (0, None),
    "tampered_receipt": (1, "SIGNATURE_INVALID"),
    "wrong_policy": (1, "POLICY_BINDING_MISMATCH"),
    "wrong_build": (1, "BUILD_BINDING_MISMATCH"),
    "missing_required_field": (1, "REQUIRED_FIELD_MISSING"),
    "unsupported_algorithm": (1, "UNSUPPORTED_ALGORITHM"),
}


def _env() -> dict[str, str]:
    env = os.environ.copy()
    src = str(ROOT / "src")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src if not existing else src + os.pathsep + existing
    return env


def _run_verify(case: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    case_dir = FIXTURE_ROOT / case
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tcd_verifier",
            "verify",
            "--receipt",
            str(case_dir / "receipt.json"),
            "--public-key",
            str(case_dir / "public-key.pem"),
            "--expected",
            str(case_dir / "expected-bindings.json"),
            "--json",
        ],
        cwd=ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        check=False,
    )
    return result, json.loads(result.stdout)


def _run_verify_paths(receipt: Path, public_key: Path, expected: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tcd_verifier",
            "verify",
            "--receipt",
            str(receipt),
            "--public-key",
            str(public_key),
            "--expected",
            str(expected),
            "--json",
        ],
        cwd=ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        check=False,
    )
    return result, json.loads(result.stdout)


def _load_case(case: str = "valid") -> tuple[dict, dict, Path]:
    case_dir = FIXTURE_ROOT / case
    receipt = json.loads((case_dir / "receipt.json").read_text(encoding="utf-8"))
    expected = json.loads((case_dir / "expected-bindings.json").read_text(encoding="utf-8"))
    return receipt, expected, case_dir / "public-key.pem"


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_case(tmp_path: Path, receipt: dict, expected: dict, public_key: Path | bytes) -> tuple[Path, Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    receipt_path = tmp_path / "receipt.json"
    expected_path = tmp_path / "expected-bindings.json"
    public_key_path = tmp_path / "public-key.pem"
    _write_json(receipt_path, receipt)
    _write_json(expected_path, expected)
    if isinstance(public_key, bytes):
        public_key_path.write_bytes(public_key)
    else:
        public_key_path.write_bytes(public_key.read_bytes())
    return receipt_path, public_key_path, expected_path


@pytest.mark.parametrize("case", sorted(EXPECTED_CASES))
def test_verifier_cli_exit_codes_and_failure_codes(case: str) -> None:
    expected_exit, expected_failure_code = EXPECTED_CASES[case]
    result, report = _run_verify(case)

    assert result.returncode == expected_exit, result.stderr
    assert report["ok"] is (expected_exit == 0)
    assert report["failure_code"] == expected_failure_code


@pytest.mark.parametrize("case", sorted(EXPECTED_CASES))
def test_fixture_reports_match_fresh_verification(case: str) -> None:
    case_dir = FIXTURE_ROOT / case
    expected_report = json.loads((case_dir / "verification-report.json").read_text(encoding="utf-8"))

    fresh = verify_files(
        case_dir / "receipt.json",
        case_dir / "public-key.pem",
        case_dir / "expected-bindings.json",
    ).to_dict()

    assert fresh["ok"] == expected_report["ok"]
    assert fresh["failure_code"] == expected_report["failure_code"]


def test_valid_receipt_matches_public_schema() -> None:
    schema = json.loads((ROOT / "schemas" / "tcd-receipt-profile-v0.1.schema.json").read_text(encoding="utf-8"))
    receipt = json.loads((FIXTURE_ROOT / "valid" / "receipt.json").read_text(encoding="utf-8"))

    validate(receipt, schema)


def test_tampered_receipt_changes_signed_field_without_resigning() -> None:
    valid = json.loads((FIXTURE_ROOT / "valid" / "receipt.json").read_text(encoding="utf-8"))
    tampered = json.loads((FIXTURE_ROOT / "tampered_receipt" / "receipt.json").read_text(encoding="utf-8"))

    assert tampered["receipt_body"]["auth_sig"]["val"] == valid["receipt_body"]["auth_sig"]["val"]
    assert tampered["receipt_body"]["claims"]["decision_outcome"] != valid["receipt_body"]["claims"]["decision_outcome"]


@pytest.mark.parametrize(
    ("case", "binding_check"),
    [
        ("wrong_policy", "policy_binding"),
        ("wrong_build", "build_binding"),
    ],
)
def test_binding_failures_keep_signature_valid(case: str, binding_check: str) -> None:
    _, report = _run_verify(case)

    assert report["checks"]["signature"] is True
    assert report["checks"][binding_check] is False


@pytest.mark.parametrize(
    ("filename", "content", "expected_failure_code"),
    [
        ("receipt.json", '{"schema":"a","schema":"b"}', "DUPLICATE_JSON_KEY"),
        ("expected-bindings.json", '{"key_id":"a","key_id":"b"}', "DUPLICATE_JSON_KEY"),
        ("receipt.json", '{"schema": NaN}', "NON_FINITE_JSON_NUMBER"),
        ("receipt.json", '{"schema": Infinity}', "NON_FINITE_JSON_NUMBER"),
        ("receipt.json", '{"schema": -Infinity}', "NON_FINITE_JSON_NUMBER"),
        ("receipt.json", '{"schema": ', "INVALID_JSON"),
    ],
)
def test_strict_json_input_failures(tmp_path: Path, filename: str, content: str, expected_failure_code: str) -> None:
    receipt, expected, public_key = _load_case()
    receipt_path, public_key_path, expected_path = _write_case(tmp_path, receipt, expected, public_key)
    (tmp_path / filename).write_text(content, encoding="utf-8")

    result, report = _run_verify_paths(receipt_path, public_key_path, expected_path)

    assert result.returncode != 0
    assert report["failure_code"] == expected_failure_code


@pytest.mark.parametrize(
    ("mutator", "expected_failure_code"),
    [
        (lambda receipt, expected: receipt.update({"unexpected": True}), "SCHEMA_INVALID"),
        (lambda receipt, expected: receipt["receipt_body"]["auth_sig"].update({"unexpected": True}), "SCHEMA_INVALID"),
        (lambda receipt, expected: expected.update({"unexpected_binding": True}), "SCHEMA_INVALID"),
        (lambda receipt, expected: receipt["receipt_body"].pop("auth_sig"), "REQUIRED_FIELD_MISSING"),
    ],
)
def test_schema_and_expected_binding_failures(tmp_path: Path, mutator, expected_failure_code: str) -> None:
    receipt, expected, public_key = _load_case()
    mutator(receipt, expected)
    paths = _write_case(tmp_path, receipt, expected, public_key)

    result, report = _run_verify_paths(*paths)

    assert result.returncode != 0
    assert report["failure_code"] == expected_failure_code


def test_signed_body_bytes_remove_entire_auth_sig() -> None:
    body = {"z": 2, "auth_sig": {"alg": "Ed25519", "val": "ignored"}}

    assert signed_body_bytes(body) == canonical_json_bytes({"z": 2})


def test_extensions_are_signed_and_tampering_fails(tmp_path: Path) -> None:
    receipt, expected, _public_key = _load_case()
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    fp = public_key_fingerprint(public_key)
    body = receipt["receipt_body"]
    body["extensions"] = {"review_packet_ref": "extension:synthetic:v0.1", "flags": {"synthetic": True}}
    body.pop("auth_sig", None)
    body["auth_sig"] = {
        "alg": "Ed25519",
        "key_id": "tcd-public-pilot-ed25519-extension-test",
        "public_key_fingerprint": fp,
        "val": base64.b64encode(private_key.sign(signed_body_bytes(body))).decode("ascii"),
    }
    expected["key_id"] = body["auth_sig"]["key_id"]
    expected["public_key_fingerprint"] = fp
    paths = _write_case(tmp_path, receipt, expected, public_pem)

    result, report = _run_verify_paths(*paths)

    assert result.returncode == 0
    assert report["ok"] is True

    tampered = copy.deepcopy(receipt)
    tampered["receipt_body"]["extensions"]["flags"]["synthetic"] = False
    tampered_paths = _write_case(tmp_path / "tampered", tampered, expected, public_pem)
    tampered_result, tampered_report = _run_verify_paths(*tampered_paths)

    assert tampered_result.returncode != 0
    assert tampered_report["failure_code"] == "SIGNATURE_INVALID"


@pytest.mark.parametrize(
    ("signature_value", "expected_failure_code"),
    [
        ("not-base64!!!", "SIGNATURE_INVALID"),
        (base64.b64encode(b"x" * 63).decode("ascii"), "SIGNATURE_INVALID"),
    ],
)
def test_signature_encoding_and_length_are_strict(tmp_path: Path, signature_value: str, expected_failure_code: str) -> None:
    receipt, expected, public_key = _load_case()
    receipt["receipt_body"]["auth_sig"]["val"] = signature_value
    paths = _write_case(tmp_path, receipt, expected, public_key)

    result, report = _run_verify_paths(*paths)

    assert result.returncode != 0
    assert report["failure_code"] == expected_failure_code


def test_public_key_must_be_ed25519(tmp_path: Path) -> None:
    receipt, expected, _public_key = _load_case()
    rsa_public = rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key()
    rsa_pem = rsa_public.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    paths = _write_case(tmp_path, receipt, expected, rsa_pem)

    result, report = _run_verify_paths(*paths)

    assert result.returncode != 0
    assert report["failure_code"] == "SCHEMA_INVALID"


def test_public_key_fingerprint_is_recomputed_from_supplied_key(tmp_path: Path) -> None:
    receipt, expected, public_key = _load_case()
    receipt["receipt_body"]["auth_sig"]["public_key_fingerprint"] = "sha256:" + "0" * 64
    paths = _write_case(tmp_path, receipt, expected, public_key)

    result, report = _run_verify_paths(*paths)

    assert result.returncode != 0
    assert report["failure_code"] == "PUBLIC_KEY_FINGERPRINT_MISMATCH"
