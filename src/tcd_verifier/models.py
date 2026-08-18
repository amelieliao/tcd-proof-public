"""Small data helpers for TCD Receipt Profile v0.1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .errors import FailureCode


PROFILE = "illustrative_public_pilot_profile"
PROFILE_VERSION = "0.1"
RECEIPT_SCHEMA = "tcd.receipt.profile.v0.1"
SIGNATURE_ALGORITHM = "Ed25519"


@dataclass
class VerificationReport:
    ok: bool
    failure_code: str | None = None
    message: str = ""
    checks: dict[str, bool | None] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "failure_code": self.failure_code,
            "message": self.message,
            "checks": self.checks,
            "details": self.details,
        }


def failure(code: FailureCode, message: str, *, checks: dict[str, bool | None] | None = None, details: dict[str, Any] | None = None) -> VerificationReport:
    return VerificationReport(
        ok=False,
        failure_code=code.value,
        message=message,
        checks=checks or {},
        details=details or {},
    )


def get_path(obj: dict[str, Any], path: str) -> Any:
    cur: Any = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def require_path(obj: dict[str, Any], path: str) -> Any:
    value = get_path(obj, path)
    if value in (None, ""):
        raise KeyError(path)
    return value
