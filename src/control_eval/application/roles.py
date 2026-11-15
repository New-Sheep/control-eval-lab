"""Load swarm roles from config/roles/*.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_goal(text: str, *, target: str) -> str:
    return (text or "").replace("{TARGET_BASE_URL}", target).replace("{BASE_URL}", target)


def load_roles(roles_dir: Path, *, target: str) -> list[dict[str, Any]]:
    path = Path(roles_dir) / "default_crew.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing roles file: {path}")
    roles = json.loads(path.read_text(encoding="utf-8"))
    for r in roles:
        if "goal" in r:
            r["goal"] = render_goal(r["goal"], target=target)
    return roles
