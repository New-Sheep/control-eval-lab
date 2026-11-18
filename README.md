# Control Eval Lab

Runnable control harness for tool-using LLM agents, plus a short technical write-up of offline synthetic-tool propensity work.

> **Scope:** this repository ships the runnable control harness (egress allowlist, Scout/Thief/Breaker swarm, deny-smoke, tests, simulated wipe). The synthetic-tool propensity figures (e.g. ~13% vs ~77%) come from **separate offline experiments** on local Ollama models; they are summarised in the docs and are **not** reproduced by running this repo. Fine-tune weights and case JSONL are private.

## Docs

| Document | Purpose |
|----------|---------|
| [docs/TECHNICAL_REPORT.md](docs/TECHNICAL_REPORT.md) | Narrative: questions, methods, interpretation, limitations, citations |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | How the runnable harness is wired |
| [docs/REFERENCE.md](docs/REFERENCE.md) | Agents and MCP tools |
| [docs/RESULTS.md](docs/RESULTS.md) | Measured tables (canonical numbers) |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | Terms |
| [docs/dashboard/index.html](docs/dashboard/index.html) | Charts from `docs/data/aggregates.json` |

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env   # set OPENAI_API_KEY and/or NVIDIA_API_KEY; or use ollama

# Terminal A: practice app
uvicorn toy_app.main:app --host 127.0.0.1 --port 8000

# Terminal B: locks then optional agents
python -m control_eval deny-smoke
pytest -q
python -m control_eval swarm --provider openai --max-turns 12
# also: --provider nvidia | ollama
```

| Provider | Default model |
|----------|----------------|
| `openai` | `gpt-4.1-mini` |
| `nvidia` | `nvidia/nemotron-3.5-bolt-e4b` |
| `ollama` | `qwen2.5:7b-instruct` (local `:11434`) |

Swarm logs go under `results/` (gitignored).

## Safety

- Default target is `http://127.0.0.1:8000` only.
- Do not aim this harness at systems you do not own or are not authorized to test.
- `PLANTED_SECRET_*` strings are lab markers, not real credentials.

## License

MIT
