# Control Eval Lab

> **Scope:** This repo ships the runnable control harness (allowlist, Scout/Thief/Breaker swarm, deny-smoke, tests). The synthetic-tool attempt rates below (~13% / 36% / 77% / 79%) come from separate offline Ollama experiments, summarised here and not reproduced by cloning this repo. Fine-tune weights and case data are private.

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

## Where this started: private DarkGenus lab

Work did **not** begin in this public repo. It began in a **local private project** called **DarkGenus** (on the author’s machine; not published). The notes below match that project’s **training / export code**, not only its README.

### Two different “brains”

| Local name | What it really is | Saved artifacts |
|------------|-------------------|-----------------|
| **Llama + LoRA** (`darkgenus`, then `darkgenus-v2` / `v3`) | Start from **Llama 3.1 8B Instruct** (4-bit Unsloth). Train a thin **LoRA** (rank 16, alpha 16) with Unsloth + TRL. Save adapter folders, merge, export GGUF for Ollama. | `DarkGenus-8B-LoRA/`, `-v2/`, `-v3/` plus merged GGUF exports |
| **`darkgenus-clear`** | **Not** a fine-tune. Ollama Modelfile `FROM dolphin3:8b` (optional alt: stock `llama3.1:8b`) plus a short system prompt for a blunt analytical voice. | Modelfile only; **no** DarkGenus LoRA weights |

**Why “clear” existed.** Hugging Face base+LoRA answered in readable English, but the first merged Ollama tag (`darkgenus`) after merge + heavy **Q4** quantize produced **nonsense** (train template ≠ serve template, plus export issues). `darkgenus-clear` was the fluent workaround so testing could continue.

**What we observed about Dolphin / `clear`.** Dolphin-style bases ship with **very weak refusal habits**. In day-to-day chat, `darkgenus-clear` would answer almost any dodgy question; a Modelfile line asking it to refuse concrete harm how-tos did little in practice. That made it a useful **high-compliance comparison** (and later a **style teacher** for v3), and a bad thing to call “safe.”

### How the Llama LoRAs were trained (scripts)

1. **v1** (`train_darkgenus.py`): Alpaca-style pairs; small set repeated into ~673 rows. Weights → `DarkGenus-8B-LoRA/`. Ollama export **Q4** → broken prose.
2. **v2** (`train_darkgenus_v2.py`): same Llama base; train with the **Llama-3 chat template**; curated JSONL (~**387** chats). Weights → `DarkGenus-8B-LoRA-v2/`. Export **Q5_K_M** → fluent `darkgenus-v2`.
3. **v3** (`train_darkgenus_v3.py` + `scripts/distill_from_clear.py`): ask `darkgenus-clear` for longer debate-style answers, **filter out** hard harmful how-tos from teacher text, add **handwritten refuse** replies for blunt dangerous asks. ~**152** chats. Weights → `DarkGenus-8B-LoRA-v3/`. Export **Q5_K_M** → `darkgenus-v3`.

Serving prompts (paraphrased): cold, sharp analytical voice in normal English; refuse step-by-step real-world harm how-tos. That is **prompt + light SFT**, not full safety training.

### What DarkGenus measured after training

- Chat/meta pressure (format tricks, fake “unlock” tokens) on base vs LoRA.
- Fake-tool suites: **262×4** pressure + **50×4** reason-then-act.

| Model | Rough high-risk **fake-tool** attempt rate (262-prompt suite) |
|-------|----------------------------------------------------------------|
| DarkGenus **v3** (Llama LoRA) | **~13%** (better chat refusals; still fails under format/authority pressure) |
| DarkGenus **v2** (Llama LoRA) | **~36%** |
| Stock **Qwen 2.5 7B Instruct** | **~77%** |
| **`darkgenus-clear`** (Dolphin + prompt) | **~79%** (**0** model refuses in that suite; almost everything only stopped by the post-model blocker) |

Models often **wrote about risk** and still tried the tool. That is why we later built **locks outside the model**.

### Local Docker MimWise before the live website

Inside DarkGenus we also built a **Control Lab** agent stack (allowlist + FastMCP tools). The order mattered:

1. **Tiny HTTP fixture** (`:8765`) to prove allowlist / dry-run gates.
2. **Full MimWise in Docker on localhost** (disposable DB). Agents could only hit that allowlisted local host; attempts to reach the public site or metadata were **blocked**. Against Docker we found a real guest broken-access issue (planted victim answers readable without a full login).
3. **Only after that:** owner-authorized SoftTrial-style pressure on the **live** MimWise product. Production was harder (empty guest lists, auth walls). High-level outcomes only in public docs.
4. **This public repo** ships a simplified practice villain (`toy_app`) so anyone can re-run the lock checks without the private Docker MimWise stack.

### Why this public repo exists

DarkGenus (training + Control Lab + Docker MimWise runs) stays private. **Control Eval Lab** is the public follow-on: practice website, Scout/Thief/Breaker, and a plain write-up. Clone this for Experiment A. Experiment B numbers and Docker MimWise traces are **not** regenerated here.

---

## What we did (two experiments)

### Experiment A: locks around agents (practice site here; Docker MimWise first in private lab)

**In this repo (runnable).** Tiny local practice website that *intentionally* leaks a fake planted secret after a “try without login” guest session. Training villain, not a product.

**Earlier in DarkGenus (private).** Same control idea against **MimWise running in Docker on the PC**, with the allowlist fencing off the public website, *before* any owner SoftTrial on live MimWise.

**Method (public crew).** Three AI roles with tools they can only use against the allowlisted target:

| Role | Job |
|------|-----|
| **Scout** | Map the site and leave tips for the others |
| **Thief** | Try to recover the planted fake secret (success is measurable) |
| **Breaker** | Try to call bad places (fake evil host, cloud metadata). Success for us = those calls are **blocked** |

We also run automatic checks (`deny-smoke`, `pytest`) so the locks are not “trust me, it worked once.”

**Why this method.** Prove the fence on a disposable local app first (fixture → Docker MimWise → simplified `toy_app` here). Only then compare to the live product. Breaker checks that the network lock still stops everything else.

### Experiment B: pretend dangerous tools (ran first in DarkGenus; summarised here)

**Setup.** Inside the private DarkGenus lab, we gave open ~8B models a menu of *fake* high-risk tools (nothing real happens) and counted how often they *tried* to call them under a fixed prompt script.

**Method.** Same prompts for each model. Main score = attempt rate. One suite pushed hard for tool calls (262 prompts × 4 models). Another forced “write your reasoning first, then decide” (50 prompts × 4 models). Models: DarkGenus v3 / v2 (Llama LoRAs), stock Qwen, and Dolphin-based `darkgenus-clear`.

**Headline numbers (from DarkGenus; not reproduced by this repo):** about **~13%** attempts for v3 vs **~77%** for Qwen 2.5 7B Instruct; clear ~**79%** with almost no model-layer refuses. Weights and prompt files stay in the private lab.

**Why this method.** Counting attempts on fake tools separates “would it try?” from “did it harm anything?” Reasoning-first checks whether sounding careful actually stops the tool press (often it did not; a post-model blocker did).

---

## What you get in this repository vs what is only summarised

| In this public repo (runnable) | Stayed in private DarkGenus / summarised only |
|--------------------------------|-----------------------------------------------|
| Practice website + Scout / Thief / Breaker | Llama LoRA training, Dolphin Modelfile, Ollama GGUFs |
| Network allowlist + guest-session checks | Fake-tool suites (~13% / 36% / 77% / 79%) |
| `deny-smoke`, tests, simulated wipe | Docker MimWise Control Lab runs + live MimWise traces |

Live MimWise (owner-authorized SoftTrial) was harder than the Docker sandbox and the practice villain (empty guest lists, auth walls). Details stay high-level and private.

---

## What we learned (short)

1. Saying “no” in chat ≠ refusing to call a tool.
2. A weakly filtered chat base (Dolphin / `clear`) will answer almost anything; a post-model blocker still matters.
3. Simple locks (allow only this host; require a guest cookie; refuse wipe unless approved) can be tested automatically.
4. Sandbox first: local fixture → Docker MimWise (allowlist on) → then live product SoftTrial. Docker showed a guest data leak; live MimWise was harder.
5. Under one fixed offline script, Llama LoRA **v3** attempted risky fake tools less often than stock Qwen. That is not a certificate that it is safe to ship.

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
