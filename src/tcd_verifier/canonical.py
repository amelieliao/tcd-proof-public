"""Canonical JSON helpers for TCD Receipt Profile v0.1."""

from __future__ import annotations

import copy
import json
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    """Return UTF-8 canonical JSON bytes used by the public pilot profile."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8", errors="strict")


def unsigned_receipt_body(receipt_body: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of a receipt body with the authenticity signature removed."""
    body = copy.deepcopy(receipt_body)
    body.pop("auth_sig", None)
    return body


def signed_body_bytes(receipt_body: dict[str, Any]) -> bytes:
    """Return canonical bytes covered by the Ed25519 authenticity signature."""
    return canonical_json_bytes(unsigned_receipt_body(receipt_body))
