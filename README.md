# Control Eval Lab

A **control-evaluation harness** for agentic attackers against a disposable local toy app.

This repo is designed to be forked: clear ports/adapters, env-based LLM providers, and a localhost-only allowlist. It does **not** target third-party production sites.

## What it measures

| Control | Behaviour |
|---------|-----------|
| Allowlist | Only `TARGET_BASE_URL` host; metadata / evil hosts denied |
| Deny-smoke | Pre-flight proof that blocks and allows match policy |
| HITL | Destructive tools are simulated / gated |
| Tool budget | Cap runaway agent tool loops |
| Swarm board | Local SQLite tips between Scout → Thief → Breaker |

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env   # add OPENAI_API_KEY or NVIDIA_API_KEY

# Terminal A — toy target
uvicorn toy_app.main:app --host 127.0.0.1 --port 8000

# Terminal B — controls + swarm
python -m control_eval deny-smoke
python -m control_eval swarm --provider openai --max-turns 12
```

Reports land in `results/` (gitignored).

## Layout

```
src/control_eval/
  domain/        # allowlist, findings, board messages (pure)
  ports/         # Protocols (DIP)
  adapters/      # httpx MCP, SQLite board, OpenAI-compat LLM, Playwright
  application/   # swarm orchestrator, reports
  cli/           # composition root
toy_app/         # disposable FastAPI fixture with PLANTED_SECRET_*
config/roles/    # Scout / Thief / Breaker goals
docs/METHOD.md   # threat model & measurement notes
```

## Extending

1. Add a port method in `ports/`
2. Implement it in `adapters/`
3. Register an MCP tool or CLI command
4. Add/adjust a role YAML under `config/roles/`

See [docs/METHOD.md](docs/METHOD.md).

## Safety

- Default target is `http://127.0.0.1:8000` only
- No production-host escape hatch
- Wipe tools are simulated
- Do not point this at systems you do not own / are not authorized to test

## License

MIT
