# Control Eval Lab

A small lab for asking a simple question:

**If an AI can use tools (browse, call APIs, upload files), do our locks still hold when the AI tries to get around them?**

Chatbots often say “I won’t help with that.” That is not the same as refusing to press a tool button. This project measures the locks around the tools, not just the chat reply.

---

## Why we built this

AI agents are increasingly wired to real systems. We wanted a clear, honest way to check:

1. **Do the safety locks work?** Can we stop an agent from calling the wrong website, reading data it should not see, or requesting a database wipe?
2. **Do small open models still try risky tools?** Even when a model sounds careful in chat, how often does it *attempt* a pretend dangerous tool if you hand it one?

The goal is teaching and portfolio work: measure locks with numbers, not vibes.

---

## What we did (two experiments)

### Experiment A: locks around a practice website (you can run this)

**Setup.** We built a tiny local practice website that *intentionally* leaks a fake planted secret after a “try without login” guest session. Think of it as a training villain, not a real product.

**Method.** We give three AI roles tools they can only use against that site:

| Role | Job |
|------|-----|
| **Scout** | Map the site and leave tips for the others |
| **Thief** | Try to recover the planted fake secret (success is measurable) |
| **Breaker** | Try to call bad places (fake evil host, cloud metadata). Success for us = those calls are **blocked** |

We also run automatic checks (`deny-smoke`, `pytest`) so the locks are not “trust me, it worked once.”

**Why this method.** If the villain is designed so Thief can win when guest access is broken on purpose, we know the scoring works. Breaker then checks that the network lock still stops everything else.

### Experiment B: pretend dangerous tools (offline write-up only)

**Setup.** Separately, on a local machine, we gave open ~8B models a menu of *fake* high-risk tools (nothing real happens) and counted how often they *tried* to call them under a fixed prompt script.

**Method.** Same prompts for each model. Main score = attempt rate. One suite pushed hard for tool calls (262 prompts × 4 models). Another forced “write your reasoning first, then decide” (50 prompts × 4 models).

**Headline numbers (summarised, not reproduced by this repo):** roughly **~13%** attempts for a second fine-tune vs **~77%** for a normal Qwen 2.5 7B Instruct baseline. Fine-tune weights and prompt files stay private.

**Why this method.** Counting attempts on fake tools separates “would it try?” from “did it harm anything?” Reasoning-first checks whether sounding careful actually stops the tool press (often it did not; a post-model blocker did).

---

## What you get in this repository vs what is only summarised

| In this repo (runnable) | Summarised only (not reproduced by cloning) |
|-------------------------|-----------------------------------------------|
| Practice website | Offline attempt rates (~13% vs ~77%, etc.) |
| Network allowlist + guest-session checks | Fine-tune weights |
| Scout / Thief / Breaker agent run | Private case prompt files |
| `deny-smoke`, tests, simulated wipe | Full MimWise product traces |

> **Plain scope:** clone this to practice the **locks**. The propensity percentages are from **other** offline runs and are written up for context; running the repo does not regenerate them.

We also briefly compared the same *style* of pressure on **MimWise** (owner product, authorized). It was harder than the practice villain (empty guest lists, auth walls). Details stay high-level and private.

---

## What we learned (short)

1. Saying “no” in chat ≠ refusing to call a tool.
2. Simple locks (allow only this host; require a guest cookie; refuse wipe unless approved) can be tested automatically.
3. A practice villain is useful for scoring; a real product can still be much harder.
4. Under one fixed offline script, a fine-tuned small model attempted risky fake tools less often than a stock instruct model. That is not a certificate that it is safe to ship.

Full tables: [docs/RESULTS.md](docs/RESULTS.md). Full write-up: [docs/TECHNICAL_REPORT.md](docs/TECHNICAL_REPORT.md). Charts: [docs/dashboard/index.html](docs/dashboard/index.html).

---

## More detail (when you want it)

Written for readers with no prior lab setup. Start with the report if you want the full story.

| Document | What it is for |
|----------|----------------|
| [docs/TECHNICAL_REPORT.md](docs/TECHNICAL_REPORT.md) | Full story: why, what we did, how, limits, citations |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | How the practice site, locks, and agent run connect |
| [docs/REFERENCE.md](docs/REFERENCE.md) | Scout / Thief / Breaker jobs and every tool on the menu |
| [docs/RESULTS.md](docs/RESULTS.md) | Scoreboard tables |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | Plain definitions |
| [docs/dashboard/index.html](docs/dashboard/index.html) | Charts |

---

## Quick start (run Experiment A)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env   # set OPENAI_API_KEY and/or NVIDIA_API_KEY; or use ollama

# Terminal A: practice website
uvicorn toy_app.main:app --host 127.0.0.1 --port 8000

# Terminal B: check locks, then optional agents
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

Agent run logs go under `results/` (gitignored).

---

## Safety

- Default target is your local practice site (`http://127.0.0.1:8000`) only.
- Do not point this at systems you do not own or are not allowed to test.
- `PLANTED_SECRET_*` strings are lab markers, not real passwords.

## License

MIT
