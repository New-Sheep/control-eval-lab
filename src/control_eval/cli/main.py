"""control-eval CLI — composition root (DIP wiring)."""

from __future__ import annotations

import argparse
import json
import sys

from control_eval.application.deny_smoke import run_deny_smoke
from control_eval.application.swarm import SwarmOrchestrator
from control_eval.domain.allowlist import Allowlist
from control_eval.settings import Settings


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="control-eval", description="Control Eval Lab")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("deny-smoke", help="Run allowlist deny-smoke checks")

    sp = sub.add_parser("swarm", help="Run Scout→Thief→Breaker swarm")
    sp.add_argument("--provider", default="openai", help="openai | nvidia | ollama")
    sp.add_argument("--max-turns", type=int, default=12)
    sp.add_argument(
        "--target",
        default="",
        help="Override TARGET_BASE_URL (localhost only recommended)",
    )

    args = p.parse_args(argv)
    settings = Settings.load()
    if getattr(args, "target", None) and str(args.target).strip():
        # Rebuild settings-like allowlist target via env for child MCP
        import os

        os.environ["TARGET_BASE_URL"] = str(args.target).strip().rstrip("/")
        settings = Settings.load()

    if args.cmd == "deny-smoke":
        allowlist = Allowlist(settings.target_base_url)
        result = run_deny_smoke(allowlist)
        print(json.dumps(result, indent=2))
        return 0 if result.get("pass") else 1

    if args.cmd == "swarm":
        orch = SwarmOrchestrator(settings)
        orch.run(provider=args.provider, max_turns=args.max_turns)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
