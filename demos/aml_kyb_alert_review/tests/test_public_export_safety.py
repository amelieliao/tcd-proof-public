from __future__ import annotations

import subprocess
import sys
from pathlib import Path


DEMO_ROOT = Path(__file__).resolve().parents[1]


def test_public_export_validator_passes() -> None:
    validator = DEMO_ROOT / "tools" / "validate_public_export.py"
    result = subprocess.run(
        [sys.executable, str(validator), "--demo-root", str(DEMO_ROOT)],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_run_derived_contains_no_old_illustrative_placeholder() -> None:
    run_dir = DEMO_ROOT / "run_derived"
    for path in run_dir.glob("*.json"):
        assert "<redacted-demo-" not in path.read_text(encoding="utf-8")
