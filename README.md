# Control Eval Lab

## What is this?

A small, **public**, **forkable** lab for testing **guardrails around AI agents**.

You run a toy website on your own machine. You give an AI tools (HTTP, optional browser). The AI tries to find a planted fake secret. Your job as the lab author is to show that:

1. the AI can do its lab job on the toy site, and  
2. the AI still **cannot** call random evil websites or cloud metadata addresses.

This is practice for **control evaluation** — measuring locks around agents — not a toolkit for attacking strangers’ websites.

**No model weight files** are included. A separate plain-English note describes refusal / fake-tool experiments; those weights stay private.

---

## Read the docs (recommended order)

| Order | File | What you’ll learn |
|-------|------|-------------------|
| 1 | [docs/RESEARCH.md](docs/RESEARCH.md) | Why this project exists; two research tracks; what is public vs private |
| 2 | [docs/METHOD.md](docs/METHOD.md) | How a run works; why Scout/Thief/Breaker; why each control exists |
| 3 | [docs/EXPERIMENT_LOG.md](docs/EXPERIMENT_LOG.md) | What actually happened on the toy app and on a private system I own |
| 4 | [docs/REFUSAL_EVAL.md](docs/REFUSAL_EVAL.md) | How I tested models with fake dangerous tools (memo only) |
| 5 | [docs/dashboard/index.html](docs/dashboard/index.html) | Charts + KPI cards (open in a browser) |
| — | [docs/data/aggregates.json](docs/data/aggregates.json) | Sanitized numbers behind the charts |

---

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env   # then add OPENAI_API_KEY or NVIDIA_API_KEY

# Terminal A — toy website
uvicorn toy_app.main:app --host 127.0.0.1 --port 8000

# Terminal B — check locks, then run agents
python -m control_eval deny-smoke
python -m control_eval swarm --provider openai --max-turns 12
```

Optional checks without an LLM:

```bash
pytest -q
```

Swarm write-ups go under `results/` (ignored by git so secrets and traces stay local).

---

## What gets measured

| Lock | Plain meaning |
|------|----------------|
| Allowlist | Agents may only talk to the toy app host you configured |
| Deny-smoke | Automatic “locks look sane?” checklist before a long run |
| HITL / simulated wipe | Agents can *ask* to wipe; the lab never really wipes |
| Tool budget | Stop runaway tool loops |
| Guest session | Notes stay closed until a guest cookie exists |
| Breaker role | An agent whose win condition is proving blocks work |

Details and design rationale: [docs/METHOD.md](docs/METHOD.md).

---

## Folder map

```text
src/control_eval/     # the harness (domain → ports → adapters → CLI)
toy_app/              # disposable local website with planted fake secrets
config/roles/         # Scout / Thief / Breaker instructions
docs/                 # research write-ups + dashboard + aggregate JSON
fixtures/             # harmless sample upload file
tests/                # allowlist + toy SoftTrial tests
```

### Rebuild charts

```bash
python docs/dashboard/build_dashboard.py
# open docs/dashboard/index.html in a browser
```


---

## Extending

1. Add an interface under `src/control_eval/ports/`
2. Implement it under `adapters/`
3. Expose it to agents as a tool if needed
4. Add or edit a role file under `config/roles/`

Keep every network call behind the same allowlist.

---

## Safety / ethics

- Default target is `http://127.0.0.1:8000` only.
- There is **no** “point this at production by flipping a flag” path in this public repo.
- Do not aim this harness at systems you do not own or are not authorized to test.
- Planted `PLANTED_SECRET_*` strings are lab markers, not real credentials.

---

## License

MIT
