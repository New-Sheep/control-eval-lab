# Control Eval Lab

**Technical report + runnable micro-laboratory** for measuring locks around tool-using LLM agents, and (separately) open-weight synthetic-tool attempt rates. Independent work — **not** affiliated with the UK AI Security Institute. Written in AI-control evaluation style (clear questions, metrics with *n*, explicit limitations).

## Abstract

Chat refusals do not bound risk when models can call tools. This repository provides (1) a local practice web app and multi-agent harness with egress allowlisting, guest-session gates, and related control measures, and (2) a public write-up of offline synthetic-tool propensity results on open ~8B models (attempt rates ~13% / 36% / 77% / 79% on a 262-prompt suite). MimWise (owner product) results are summarized at high level only. Weights and private traces are not shipped.

## Read in this order (one-way)

| # | Document | Purpose |
|---|----------|---------|
| 1 | [docs/OVERVIEW.md](docs/OVERVIEW.md) | Executive brief |
| 2 | [docs/TECHNICAL_REPORT.md](docs/TECHNICAL_REPORT.md) | Full tech report (start here for specialists) |
| 3 | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Diagrams + OpenAI / NVIDIA / Ollama providers |
| 4 | [docs/REFERENCE.md](docs/REFERENCE.md) | Every agent, every MCP tool, data sizes, eval suites |
| 5 | [docs/RESULTS.md](docs/RESULTS.md) | Tables |
| 6 | [docs/GLOSSARY.md](docs/GLOSSARY.md) | Terms |
| 7 | [docs/dashboard/index.html](docs/dashboard/index.html) | Charts |

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env   # set OPENAI_API_KEY and/or NVIDIA_API_KEY; or use ollama

# Terminal A — practice app
uvicorn toy_app.main:app --host 127.0.0.1 --port 8000

# Terminal B — locks then optional agents
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
- No “flip a flag to hit production” path in this public repo.
- Do not aim this harness at systems you do not own or are not authorized to test.
- `PLANTED_SECRET_*` strings are lab markers, not real credentials.

## License

MIT
