"""Clean-room Ed25519 verifier for TCD Receipt Profile v0.1."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

from .canonical import signed_body_bytes
from .errors import FailureCode
from .jsonio import StrictJsonError, strict_json_load
from .models import (
    PROFILE,
    PROFILE_VERSION,
    RECEIPT_SCHEMA,
    SIGNATURE_ALGORITHM,
    VerificationReport,
    failure,
    get_path,
    require_path,
)


REQUIRED_RECEIPT_PATHS = [
    "schema",
    "profile",
    "profile_version",
    "runtime_generated",
    "synthetic_data",
    "claim_status",
    "receipt_body.v",
    "receipt_body.schema",
    "receipt_body.ts_ns",
    "receipt_body.nonce",
    "receipt_body.attestor.id",
    "receipt_body.claims.event_id",
    "receipt_body.claims.upstream_action_id",
    "receipt_body.claims.scenario_id",
    "receipt_body.claims.policy_ref",
    "receipt_body.claims.policy_digest",
    "receipt_body.claims.build_id",
    "receipt_body.claims.image_digest",
    "receipt_body.claims.cfg_fp",
    "receipt_body.auth_sig.alg",
    "receipt_body.auth_sig.key_id",
    "receipt_body.auth_sig.public_key_fingerprint",
    "receipt_body.auth_sig.val",
]


EXPECTED_BINDING_KEYS = {
    "schema",
    "profile",
    "profile_version",
    "key_id",
    "public_key_fingerprint",
    "policy_ref",
    "policy_digest",
    "build_id",
    "image_digest",
    "cfg_fp",
    "service_config_fingerprint",
    "config",
    "required_fields",
}
EXPECTED_CONFIG_KEYS = {"cfg_fp", "service_config_fingerprint"}
SIGNATURE_LENGTH_BYTES = 64


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / "tcd-receipt-profile-v0.1.schema.json"


def _load_receipt_schema() -> tuple[dict[str, Any] | None, VerificationReport | None]:
    try:
        schema = strict_json_load(_schema_path())
    except StrictJsonError as exc:
        return None, failure(exc.code, "receipt schema JSON is invalid", details={"error": exc.message})
    except OSError as exc:
        return None, failure(FailureCode.SCHEMA_INVALID, "receipt schema file is missing or unreadable", details={"error": str(exc)})
    if not isinstance(schema, dict):
        return None, failure(FailureCode.SCHEMA_INVALID, "receipt schema must be a JSON object")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        return None, failure(FailureCode.SCHEMA_INVALID, "receipt schema is invalid", details={"error": exc.message})
    return schema, None


def _json_path(error: ValidationError) -> str:
    path = "$"
    for part in error.absolute_path:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def _schema_failure(error: ValidationError) -> VerificationReport:
    details = {"path": _json_path(error), "validator": error.validator}
    if error.validator == "required":
        missing = []
        if error.message.startswith("'"):
            missing.append(error.message.split("'", 2)[1])
        return failure(FailureCode.REQUIRED_FIELD_MISSING, "receipt is missing required field(s)", checks={"schema": False}, details={**details, "missing": missing})
    return failure(FailureCode.SCHEMA_INVALID, "receipt schema validation failed", checks={"schema": False}, details=details)


def _validate_receipt_schema(receipt: dict[str, Any]) -> VerificationReport | None:
    schema, schema_failure = _load_receipt_schema()
    if schema_failure:
        return schema_failure
    assert schema is not None
    validator = Draft202012Validator(schema)
    error = next(validator.iter_errors(receipt), None)
    if error:
        return _schema_failure(error)
    return None


def _validate_expected_bindings(expected: dict[str, Any]) -> VerificationReport | None:
    unknown = sorted(set(expected) - EXPECTED_BINDING_KEYS)
    if unknown:
        return failure(FailureCode.SCHEMA_INVALID, "expected bindings contain unknown field(s)", details={"unknown_fields": unknown})
    config = expected.get("config")
    if config is not None:
        if not isinstance(config, dict):
            return failure(FailureCode.SCHEMA_INVALID, "expected config bindings must be a JSON object")
        unknown_config = sorted(set(config) - EXPECTED_CONFIG_KEYS)
        if unknown_config:
            return failure(FailureCode.SCHEMA_INVALID, "expected config bindings contain unknown field(s)", details={"unknown_fields": unknown_config})
    required_fields = expected.get("required_fields")
    if required_fields is not None:
        if not isinstance(required_fields, list) or not all(isinstance(item, str) and item for item in required_fields):
            return failure(FailureCode.SCHEMA_INVALID, "expected required_fields must be a list of non-empty strings")
    return None


def public_key_fingerprint(public_key: Ed25519PublicKey) -> str:
    spki = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return "sha256:" + hashlib.sha256(spki).hexdigest()


def load_public_key(path: Path) -> Ed25519PublicKey:
    data = path.read_bytes()
    key = serialization.load_pem_public_key(data)
    if not isinstance(key, Ed25519PublicKey):
        raise ValueError("public key must be Ed25519")
    return key


def _check_required(receipt: dict[str, Any], expected: dict[str, Any]) -> VerificationReport | None:
    required = list(REQUIRED_RECEIPT_PATHS)
    required.extend(str(x) for x in expected.get("required_fields", []) if x)
    missing = []
    for path in required:
        try:
            require_path(receipt, path)
        except KeyError:
            missing.append(path)
    if missing:
        return failure(
            FailureCode.REQUIRED_FIELD_MISSING,
            "receipt is missing required field(s)",
            checks={"schema": False},
            details={"missing": missing},
        )
    return None


def _expected_config(expected: dict[str, Any], name: str) -> Any:
    config = expected.get("config")
    if isinstance(config, dict) and name in config:
        return config[name]
    return expected.get(name)


def verify_receipt(receipt: dict[str, Any], public_key: Ed25519PublicKey, expected: dict[str, Any]) -> VerificationReport:
    checks: dict[str, bool | None] = {
        "schema": None,
        "profile": None,
        "algorithm": None,
        "key_id": None,
        "public_key_fingerprint": None,
        "signature": None,
        "policy_binding": None,
        "build_binding": None,
        "image_binding": None,
        "config_binding": None,
    }

    required_failure = _check_required(receipt, expected)
    if required_failure:
        return required_failure
    checks["schema"] = True

    if receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("profile") != PROFILE or str(receipt.get("profile_version")) != PROFILE_VERSION:
        return failure(
            FailureCode.UNSUPPORTED_PROFILE,
            "receipt profile is not supported by this verifier",
            checks={**checks, "profile": False},
            details={
                "schema": receipt.get("schema"),
                "profile": receipt.get("profile"),
                "profile_version": receipt.get("profile_version"),
            },
        )
    if get_path(receipt, "receipt_body.schema") != RECEIPT_SCHEMA:
        return failure(
            FailureCode.SCHEMA_INVALID,
            "receipt body schema does not match the top-level profile schema",
            checks={**checks, "schema": False},
            details={"receipt_body_schema": get_path(receipt, "receipt_body.schema")},
        )
    if receipt.get("runtime_generated") is not False or receipt.get("synthetic_data") is not True:
        return failure(
            FailureCode.UNSUPPORTED_PROFILE,
            "fixture must be synthetic and non-runtime-generated for this pilot profile",
            checks={**checks, "profile": False},
        )
    checks["profile"] = True

    body = receipt["receipt_body"]
    auth_sig = body["auth_sig"]
    if auth_sig.get("alg") != SIGNATURE_ALGORITHM:
        return failure(
            FailureCode.UNSUPPORTED_ALGORITHM,
            "unsupported authenticity signature algorithm",
            checks={**checks, "algorithm": False},
            details={"algorithm": auth_sig.get("alg")},
        )
    checks["algorithm"] = True

    expected_key_id = expected.get("key_id")
    if expected_key_id and auth_sig.get("key_id") != expected_key_id:
        return failure(
            FailureCode.KEY_ID_MISMATCH,
            "receipt key ID does not match expected key ID",
            checks={**checks, "key_id": False},
            details={"receipt_key_id": auth_sig.get("key_id"), "expected_key_id": expected_key_id},
        )
    checks["key_id"] = True

    computed_fp = public_key_fingerprint(public_key)
    expected_fp = expected.get("public_key_fingerprint")
    if auth_sig.get("public_key_fingerprint") != computed_fp or (expected_fp and expected_fp != computed_fp):
        return failure(
            FailureCode.PUBLIC_KEY_FINGERPRINT_MISMATCH,
            "public key fingerprint does not match receipt or expected bindings",
            checks={**checks, "public_key_fingerprint": False},
            details={
                "receipt_public_key_fingerprint": auth_sig.get("public_key_fingerprint"),
                "expected_public_key_fingerprint": expected_fp,
                "computed_public_key_fingerprint": computed_fp,
            },
        )
    checks["public_key_fingerprint"] = True

    try:
        sig_bytes = base64.b64decode(str(auth_sig.get("val")).encode("ascii"), validate=True)
        if len(sig_bytes) != SIGNATURE_LENGTH_BYTES:
            raise ValueError("Ed25519 signatures must be 64 bytes")
        public_key.verify(sig_bytes, signed_body_bytes(body))
    except (InvalidSignature, ValueError, TypeError):
        return failure(
            FailureCode.SIGNATURE_INVALID,
            "Ed25519 signature verification failed",
            checks={**checks, "signature": False},
        )
    checks["signature"] = True

    claims = body["claims"]
    expected_policy_ref = expected.get("policy_ref")
    expected_policy_digest = expected.get("policy_digest")
    if expected_policy_ref and claims.get("policy_ref") != expected_policy_ref:
        return failure(FailureCode.POLICY_BINDING_MISMATCH, "policy_ref binding mismatch", checks={**checks, "policy_binding": False})
    if expected_policy_digest and claims.get("policy_digest") != expected_policy_digest:
        return failure(FailureCode.POLICY_BINDING_MISMATCH, "policy_digest binding mismatch", checks={**checks, "policy_binding": False})
    checks["policy_binding"] = True

    if expected.get("build_id") and claims.get("build_id") != expected.get("build_id"):
        return failure(FailureCode.BUILD_BINDING_MISMATCH, "build_id binding mismatch", checks={**checks, "build_binding": False})
    checks["build_binding"] = True

    if expected.get("image_digest") and claims.get("image_digest") != expected.get("image_digest"):
        return failure(FailureCode.IMAGE_BINDING_MISMATCH, "image_digest binding mismatch", checks={**checks, "image_binding": False})
    checks["image_binding"] = True

    for field in ("cfg_fp", "service_config_fingerprint"):
        expected_value = _expected_config(expected, field)
        if expected_value and claims.get(field) != expected_value:
            return failure(
                FailureCode.CONFIG_BINDING_MISMATCH,
                f"{field} binding mismatch",
                checks={**checks, "config_binding": False},
                details={"field": field},
            )
    checks["config_binding"] = True

    details = {
        "profile": PROFILE,
        "profile_version": PROFILE_VERSION,
        "signature_algorithm": SIGNATURE_ALGORITHM,
        "key_id": auth_sig.get("key_id"),
        "public_key_fingerprint": computed_fp,
        "event_id": get_path(receipt, "receipt_body.claims.event_id"),
        "upstream_action_id": get_path(receipt, "receipt_body.claims.upstream_action_id"),
        "scenario_id": get_path(receipt, "receipt_body.claims.scenario_id"),
        "receipt_ref": receipt.get("receipt_ref"),
    }
    return VerificationReport(ok=True, message="receipt verified", checks=checks, details=details)


def verify_files(receipt_path: Path, public_key_path: Path, expected_path: Path) -> VerificationReport:
    try:
        receipt = strict_json_load(receipt_path)
        expected = strict_json_load(expected_path)
        public_key = load_public_key(public_key_path)
    except StrictJsonError as exc:
        return failure(exc.code, exc.message)
    except Exception as exc:
        return failure(FailureCode.SCHEMA_INVALID, "could not load verification inputs", details={"error": str(exc)})
    if not isinstance(receipt, dict) or not isinstance(expected, dict):
        return failure(FailureCode.SCHEMA_INVALID, "receipt and expected bindings must be JSON objects")
    expected_failure = _validate_expected_bindings(expected)
    if expected_failure:
        return expected_failure
    schema_failure = _validate_receipt_schema(receipt)
    if schema_failure:
        return schema_failure
    return verify_receipt(receipt, public_key, expected)
