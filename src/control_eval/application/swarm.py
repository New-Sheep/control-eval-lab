"""SwarmOrchestrator — Scout → Thief → Breaker."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from control_eval.adapters.sqlite_board import SqliteBoard
from control_eval.application.agent_runner import run_agent_goal
from control_eval.application.deny_smoke import run_deny_smoke
from control_eval.application.reports import write_swarm_report
from control_eval.application.roles import load_roles
from control_eval.domain.allowlist import Allowlist
from control_eval.settings import Settings


class SwarmOrchestrator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.allowlist = Allowlist(settings.target_base_url)
        self.board = SqliteBoard(settings.board_db)

    def preflight_guest(self) -> dict[str, Any]:
        url = self.settings.target_base_url.rstrip("/") + "/api/guest/start"
        out: dict[str, Any] = {"url": url, "ok": False}
        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as c:
                resp = c.post(url, json={})
            out["status_code"] = resp.status_code
            parts = [f"{n}={v}" for n, v in resp.cookies.items()]
            if not parts:
                for k, v in resp.headers.items():
                    if k.lower() == "set-cookie":
                        first = v.split(";", 1)[0].strip()
                        if first and "=" in first:
                            parts.append(first)
            header = "; ".join(parts)
            out["cookie_names"] = [p.split("=", 1)[0] for p in parts]
            out["ok"] = resp.status_code < 400 and bool(parts)
            if header:
                os.environ["CONTROL_EVAL_GUEST_COOKIE"] = header
                out["seeded_env"] = True
        except Exception as e:  # noqa: BLE001
            out["error"] = f"{type(e).__name__}:{e}"
        return out

    async def _run_roles(
        self,
        *,
        run_id: str,
        provider: str,
        max_turns: int,
        roles: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for role in roles:
            agent_id = role["agent_id"]
            os.environ["SWARM_AGENT_ID"] = agent_id
            os.environ["SWARM_RUN_ID"] = run_id
            goal = (
                f"You are role={role['id']} agent_id={agent_id} "
                f"in Scout→Thief→Breaker (run_id={run_id}).\n{role['goal']}"
            )
            print(f"\n=== {agent_id} ===", flush=True)
            try:
                r = await run_agent_goal(
                    goal,
                    scenario_id=f"swarm_{agent_id}",
                    max_turns=max_turns,
                    provider=provider,
                    settings=self.settings,
                )
                r["agent_id"] = agent_id
                r["role"] = role["id"]
                results.append(r)
                print((r.get("final_output") or "")[:1200], flush=True)
            except Exception as e:  # noqa: BLE001
                err = {
                    "agent_id": agent_id,
                    "role": role["id"],
                    "error": f"{type(e).__name__}:{e}",
                }
                results.append(err)
                print(f"ERROR: {err}", flush=True)
        return results

    def run(
        self,
        *,
        provider: str = "openai",
        max_turns: int = 12,
    ) -> dict[str, Any]:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        os.environ["SWARM_RUN_ID"] = run_id
        os.environ["TARGET_BASE_URL"] = self.settings.target_base_url
        self.board.reset(run_id)

        deny = run_deny_smoke(self.allowlist)
        guest = self.preflight_guest()
        print(json.dumps({"deny_smoke": deny, "guest_preflight": guest}, indent=2))
        if not deny.get("pass"):
            raise SystemExit("Deny-smoke failed — abort.")

        roles = load_roles(self.settings.roles_dir, target=self.settings.target_base_url)
        results = asyncio.run(
            self._run_roles(
                run_id=run_id,
                provider=provider,
                max_turns=max_turns,
                roles=roles,
            )
        )

        msgs = self.board.read(80, run_id=run_id)
        board_stats = self.board.stats(run_id)
        payload = {
            "run_id": run_id,
            "target": self.settings.target_base_url,
            "provider": provider,
            "max_turns": max_turns,
            "deny_smoke": deny,
            "guest_preflight": guest,
            "board": board_stats,
            "results": results,
        }
        out_json = self.settings.results_dir / "swarm_last_run.json"
        out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        report = self.settings.results_dir / "SWARM_REPORT.md"
        write_swarm_report(
            run_id=run_id,
            target=self.settings.target_base_url,
            results=results,
            board_stats=board_stats,
            deny=deny,
            board_messages=[
                {"agent_id": m.agent_id, "body": m.body, "ts": m.ts} for m in msgs
            ],
            out_path=report,
        )
        print(f"Wrote {out_json}", flush=True)
        print(f"Wrote {report}", flush=True)
        return payload
