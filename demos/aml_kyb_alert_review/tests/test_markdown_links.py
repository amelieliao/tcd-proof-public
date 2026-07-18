from __future__ import annotations

import re
from pathlib import Path


PUBLIC_ROOT = Path(__file__).resolve().parents[3]


def test_markdown_relative_links_exist() -> None:
    for path in PUBLIC_ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = match.group(1).split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (path.parent / target).resolve()
            assert resolved.exists(), f"{path}: missing link target {target}"
