from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


DEMO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = DEMO_ROOT / "tools" / "validate_public_export.py"


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--demo-root", str(root)],
        text=True,
        capture_output=True,
    )


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def assert_rejected(tmp_path: Path, relative: str, content: str | bytes | object) -> None:
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    elif isinstance(content, str):
        path.write_text(content, encoding="utf-8")
    else:
        write_json(path, content)
    result = run_validator(tmp_path)
    assert result.returncode != 0, result.stdout + result.stderr


def test_validator_rejects_sensitive_public_export_fixtures(tmp_path: Path) -> None:
    private_path = "/" + "Users" + "/example/private/path\n"
    private_key_header = "-----BEGIN " + "PRIVATE KEY-----\n"
    bearer_token = "Bearer " + "abcdefghijklmnopqrstuvwxyz1234567890\n"
    bad_cases: list[tuple[str, str | bytes | object]] = [
        ("bad-private-path.md", private_path),
        ("bad-private-key.md", private_key_header),
        ("bad-bearer-token.md", bearer_token),
        ("bad-hmac-secret.json", {"hmac_secret": "super-secret-local-hmac-value"}),
        ("bad.sqlite", b"sqlite bytes"),
        ("bad.log", b"log bytes"),
        ("env.sh", "export TOKEN=bad\n"),
        ("bad-raw-prompt.json", {"raw_prompt": "summarize this case"}),
        ("bad-raw-completion.json", {"raw_completion": "model answer"}),
        ("bad-secret-token.json", {"secret_token": "secret-like-token-1234567890"}),
    ]
    for index, (relative, content) in enumerate(bad_cases):
        case_root = tmp_path / f"bad-{index}"
        assert_rejected(case_root, relative, content)


def test_validator_allows_safe_boundary_language(tmp_path: Path) -> None:
    write_json(
        tmp_path / "safe.json",
        {
            "base_max_tokens": 512,
            "token_budget": "small demo budget",
            "artifact_metadata": {
                "raw_customer_data_present": False,
                "raw_prompt_present": False,
                "raw_completion_present": False,
                "signing_secret_present": False,
            },
        },
    )
    (tmp_path / "target.md").write_text("# Target\n", encoding="utf-8")
    (tmp_path / "safe.md").write_text(
        "\n".join(
            [
                "# Safe public notes",
                "",
                "The token budget is documented without storing credential material.",
                "This packet does not expose raw customer data.",
                "WAL files are not published.",
                "See [target](target.md).",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    result = run_validator(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
