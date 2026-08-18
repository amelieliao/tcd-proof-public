"""Strict JSON parsing shared by verifier, reconciliation, and manifest checks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import FailureCode


class StrictJsonError(ValueError):
    """Base class for strict JSON parse failures."""

    def __init__(self, code: FailureCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class DuplicateJsonKeyError(StrictJsonError):
    def __init__(self, key: str) -> None:
        super().__init__(FailureCode.DUPLICATE_JSON_KEY, f"duplicate JSON key: {key}")
        self.key = key


class NonFiniteJsonNumberError(StrictJsonError):
    def __init__(self, value: str) -> None:
        super().__init__(FailureCode.NON_FINITE_JSON_NUMBER, f"non-finite JSON number is not allowed: {value}")
        self.value = value


class InvalidJsonError(StrictJsonError):
    def __init__(self, message: str) -> None:
        super().__init__(FailureCode.INVALID_JSON, message)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise DuplicateJsonKeyError(key)
        obj[key] = value
    return obj


def _reject_non_finite(value: str) -> None:
    raise NonFiniteJsonNumberError(value)


def strict_json_loads(text: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_finite,
        )
    except StrictJsonError:
        raise
    except json.JSONDecodeError as exc:
        raise InvalidJsonError(f"malformed JSON at line {exc.lineno}, column {exc.colno}") from exc


def strict_json_load(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidJsonError("JSON input must be valid UTF-8") from exc
    return strict_json_loads(text)
