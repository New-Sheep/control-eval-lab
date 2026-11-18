# Control Eval Lab technical report

> **Scope:** This repo ships the runnable control harness (allowlist, Scout/Thief/Breaker swarm, deny-smoke, tests). The synthetic-tool attempt rates below (~13% / 36% / 77% / 79%) come from separate offline Ollama experiments, summarised here and not reproduced by cloning this repo. Fine-tune weights and case data are private.

**What this is:** a personal write-up of two small experiments about AI that can use tools, plus a practice lab you can run on your own computer.  
**Date:** November 2026  
**What ships in the repo:** the practice website and the lock-checking agent run. Fine-tune files, Docker MimWise Control Lab traces, and private prompt lists are available on request / interview.

Start here for the story. Numbers: [RESULTS.md](RESULTS.md). How the runnable pieces connect: [ARCHITECTURE.md](ARCHITECTURE.md). Who does what: [REFERENCE.md](REFERENCE.md). Plain terms: [GLOSSARY.md](GLOSSARY.md).

---

## In one paragraph

Today many AI systems can browse, call APIs, or upload files. A polite “I won’t help with that” in chat does not prove the AI will refuse to press a tool button. This report asks two questions: (1) how often do small open models *try* pretend dangerous tools under a fixed script, and (2) do simple locks (only talk to this website, require a guest cookie, refuse a real wipe) still hold when several AI roles poke a practice site, and at a high level an owner product (MimWise).

Tables live in [RESULTS.md](RESULTS.md). This is a teaching / portfolio micro-lab, not a claim about frontier labs or industry-scale benchmarks.

---

## 0. Project timeline: DarkGenus → this public lab

| Stage | Where | What happened |
|-------|-------|----------------|
| 1 | **DarkGenus** | QLoRA on **Llama 3.1 8B Instruct**; save `DarkGenus-8B-LoRA/`; first Ollama merge+Q4 export is broken nonsense |
| 2 | **DarkGenus** | Fluent workaround: **`darkgenus-clear`** = **`dolphin3:8b`** + Modelfile (**no** LoRA) |
| 3 | **DarkGenus** | Retrain **v2** / **v3**; export Q5 GGUFs; fake-tool suites **262×4** + **50×4** |
| 4 | **DarkGenus Control Lab** | Allowlist + agents vs tiny fixture (`:8765`), then **MimWise in Docker on localhost** (prod host blocked) |
| 5 | **DarkGenus Control Lab** | Docker MimWise: guest broken-access / planted-answer leak found under allowlisted local runs |
| 6 | **Owner SoftTrial** | Same *style* of pressure on live MimWise (authorized); harder than Docker (empty lists / auth walls) |
| 7 | **Control Eval Lab** (this repo) | Simplified `toy_app` + Scout/Thief/Breaker so the lock harness is public |

DarkGenus / Docker MimWise stacks are **not** shipped here. Details below match the private scripts and Control Lab reports.

---

## 1. Why this matters

A common setup looks like:

```text
person → AI model → tools (web, upload, APIs) → something happens in the world
```

If you only grade chat refusals, you miss the tool step. So we measure **locks outside the model** (who it may call, what session it needs, whether wipe is only pretend), and we separately count **attempts** on fake tools.

We did layered work:

- **Attempts (Experiment B, in DarkGenus):** offline, same prompts for several small models, counting how often they tried a fake risky tool.
- **Locks on a disposable app (private Control Lab, then this repo):** allowlist + multi-role agents first against a local fixture and **Docker MimWise**, only later against live MimWise SoftTrial; this repo ships the simplified practice site.

---

## 2. What we were worried about (lab scale)

Imagine you give an AI tools pointed at a website you run. Risks we care about here:

- Calling the **wrong host** (a fake evil site, or a cloud “metadata” address often used in break-in demos).
- Using a **try without login** guest path to read data that should stay closed.
- Asking to **wipe a database** (we only *simulate* this; nothing real is deleted).
- Being handed a menu of **pretend dangerous tools** and trying to call them anyway.

We do **not** use this to attack other people’s systems, claim wins we did not get, or evaluate secret commercial monitors.

### Two questions

| ID | Layer | Plain question |
|----|-------|----------------|
| **Q1** | Model | If you hand a small open model fake high-risk tools and a fixed script, how often does it *try* to call them? |
| **Q2** | System | If you give agents real browse/API tools, do the locks still hold on a practice site, and how does an owner product compare at a high level? |

---

## 3. Related work (short)

Other projects study similar ideas at larger scale (for example AgentHarm for harmful tool tasks; ControlArena / Inspect for control experiments). We use a smaller private prompt set on open ~8B models, and a tiny allowlist + human-approval style lab instead of those full frameworks. We care about the same split: **chat risk is not the same as tool risk**.

---

## 4. Methods

### 4.1 What DarkGenus actually built (from the code)

All of this lived in the private **DarkGenus** repo.

#### A. Llama 3.1 Instruct + LoRA (real fine-tunes)

| Piece | From the scripts |
|-------|------------------|
| Base | `unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit` (fits ~8 GB VRAM) |
| Method | Unsloth + TRL `SFTTrainer`; LoRA **r=16**, **alpha=16** on attention + MLP projections |
| v1 | `train_darkgenus.py`: Alpaca `### Instruction` format; tiny set duplicated (~**673** rows). Save **`DarkGenus-8B-LoRA/`**. Merge → GGUF **Q4_K_M** → Ollama `darkgenus` |
| v2 | `train_darkgenus_v2.py`: **Llama-3 chat template**; curated `data/darkgenus_sft_v2.jsonl` (~**387**). Save **`DarkGenus-8B-LoRA-v2/`**. Export **Q5_K_M** → `darkgenus-v2` |
| v3 | `train_darkgenus_v3.py` + `scripts/distill_from_clear.py`: teacher = `darkgenus-clear` for longer debate-style answers; **drop** teacher rows that look like hard harm how-tos; add **handwritten refuse** chats. `data/darkgenus_sft_v3.jsonl` (~**152**). Save **`DarkGenus-8B-LoRA-v3/`**. Export **Q5_K_M** → `darkgenus-v3` |

**Why v1 Ollama broke:** HF base+LoRA was readable; standalone merged GGUF was not. Causes stacked in the audit: train as Alpaca but serve as Llama-3 chat; merge from 4-bit then re-quantize hard; tiny repeated corpus. v2/v3 fixed template alignment and used milder quant.

**System prompts (paraphrased, kept mild):** ask for a cold, sharp analytical voice in plain English; ban gibberish token salad from the bad export; refuse step-by-step real-world harm how-tos. Shared in `scripts/chat_prompt.py` and baked into Ollama Modelfiles for v2/v3. This is **not** full RLHF/DPO safety training.

#### B. Dolphin-based `darkgenus-clear` (not a LoRA)

| Piece | From the scripts |
|-------|------------------|
| Setup | `ollama_setup_darkgenus_clear.cmd` → `Modelfile.coherent_dolphin` |
| Weights | **`FROM dolphin3:8b`** already on the machine (alt Modelfile: stock `llama3.1:8b`) |
| Adapter | **None.** Persona is prompt-only |

**Observed behaviour:** Dolphin-class bases have **negligible practical refusals**. In ordinary chat, `darkgenus-clear` would answer almost any dodgy question despite a Modelfile refuse line. In the 262-prompt fake-tool suite it produced **0** model-layer refuses (~**79%** attempt rate); nearly all “passes” were the **post-model blocker**. We used it as (1) a fluent stand-in while v1 Ollama was broken, (2) a high-compliance baseline, and (3) a **style teacher** for v3 distill (with filters so hard how-tos were not copied into SFT).

#### C. Early chat/meta evals

Public-safe format / fake-authority suites on HF base vs LoRA showed the persona adapter often **complied with short trick strings** while the base often wandered off-task. That pushed the work toward **tool-attempt** measurement and later **system locks**.

### 4.2 Counting tool attempts in DarkGenus (Experiment B)

| Suite | Size | What we counted |
|-------|------|-----------------|
| Tool-call pressure | **262 prompts × 4 models = 1,048** decisions | Did it try a high-risk **fake** tool? |
| Reason-then-act | **50 × 4 = 200** | Same, after it had to write reasoning first |

**Models (Ollama tags):** `darkgenus-v3`, `darkgenus-v2` (Llama LoRAs), `qwen2.5:7b-instruct`, `darkgenus-clear` (Dolphin + prompt).  
**Where:** local machine. Tools were sandbox fakes. A toy monitor blocked high-risk names so nothing real ran. Rates: [RESULTS.md section D](RESULTS.md).

**Extra findings:** attempts rose under format-force and fake-authority wording; on reason-then-act, Qwen/clear often described risk and still chose to call; v3 had the lowest attempts (~4% on that smaller suite) but often failed the required answer format; clear showed why a monitor after the model is mandatory when the base barely refuses.

### 4.3 Agent roles on the practice site (Experiment A)

- We run three public roles in order: **Scout → Thief → Breaker** (job text in a JSON config).
- They share short tips on a local tip board.
- Tools are ordinary actions (fetch a page, start guest session, leave a tip, open a browser, pretend wipe). Every web call must pass the allowlist.
- Private MimWise runs also used extra roles (Crawler, Injector, UI players). See [REFERENCE.md](REFERENCE.md).

How pieces connect: [ARCHITECTURE.md](ARCHITECTURE.md).

### 4.4 Locks under test

| Lock | Why it is there |
|------|-----------------|
| Host allowlist | Only the approved practice (or product) host |
| Pre-flight check (`deny-smoke`) | Fail fast if locks were misconfigured |
| Tool budget (default 64) | Stop endless tool loops |
| Simulated wipe + optional human approve | Score “asked to wipe” without deleting data |
| Guest session gate | Notes closed until a guest cookie exists |

### 4.5 Where we pointed the agents (sandbox before live)

Order in the private Control Lab, then here:

1. **Tiny fixture** (`http://127.0.0.1:8765`): prove allowlist / dry-run before a real app.
2. **MimWise in Docker** on localhost (`:8000`): full product copy, disposable DB. Allowlist permitted only that host; public MimWise / evil / metadata denied (`deny-smoke`). Agents (NVIDIA and local Ollama) found guest broken access to planted victim answers. Wipe stayed simulated + HITL.
3. **Live MimWise SoftTrial** (owner-authorized): same *style* of pressure; public notes stay high-level. Harder than Docker (empty guest lists, auth walls). No claimed planted-secret IDOR win on the live product in the public write-up.
4. **Practice website in this repo** (`toy_app`): simplified training villain with intentional planted `PLANTED_SECRET_*` so anyone can score Scout/Thief/Breaker without the private Docker stack.

**Wanted jobs vs unwanted jobs:** Scout/Thief do authorized mapping / marker recovery. Breaker checks that unwanted calls (evil host, metadata) **fail**.

---

## 5. How to read the findings

Numbers are in [RESULTS.md](RESULTS.md). In plain words:

1. **Chat “no” ≠ tool “no.”** A model can refuse advice in text and still try a risky tool when tools are on the table.
2. **Same script, different attempt rates.** On 262 prompts in DarkGenus, **v3** tried far less often (~13%) than stock Qwen (~77%). That is evidence for *this* script, not a general safety certificate.
3. **Writing reasons did not reliably stop attempts.** Models often described danger and still called the tool; the post-model blocker stopped fake execution.
4. **Locks can be tested like unit tests.** Pre-flight and practice-site tests pass on the public lab.
5. **Sandbox before live.** Docker MimWise (allowlisted localhost) showed a guest data leak on planted answers; live SoftTrial was harder (empty lists / auth walls). The public `toy_app` is a simplified scoring villain, not that Docker stack.
6. **Scale is small.** Portfolio / teaching micro-lab, not a frontier sabotage study.

Charts: [dashboard/index.html](dashboard/index.html).

---

## 6. Limits (honest)

1. Small open models and small prompt sets.
2. Fixed scripts ≠ real-world misuse rates.
3. Fake tools measure *attempts*, not real harm.
4. The practice site is designed to leak a marker; winning there is not “we broke MimWise.”
5. Public MimWise notes omit paths and cookies on purpose.
6. This is not the same tooling as large public control benchmarks.

---

## 7. Reproducing Experiment A (locks only)

```bash
pip install -e ".[dev]"
uvicorn toy_app.main:app --host 127.0.0.1 --port 8000
python -m control_eval deny-smoke
pytest -q
# optional live agents:
# python -m control_eval swarm --provider openai --max-turns 12
```

Which AI provider to pick: [ARCHITECTURE.md](ARCHITECTURE.md).  
Private weights and MimWise traces: interview / on request.

---

## References

1. Andriushchenko, M., Souly, A., et al. *AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents.* ICLR 2025. arXiv:2410.09024.  
2. UK AI Security Institute. *How to evaluate control measures for AI agents?* (blog, 2025). https://www.aisi.gov.uk/blog/how-to-evaluate-control-measures-for-ai-agents  
3. UK AISI / Redwood et al. *ControlArena* (library for AI control experiments). https://github.com/UKGovernmentBEIS/control-arena  
4. UK AISI. *Inspect* evaluation framework. https://inspect.aisi.org.uk/  
5. Bazinska, J., et al. *Breaking agent backbones: Evaluating the security of backbone LLMs in AI agents.* arXiv:2510.22620.  
6. Greenblatt, R., et al. AI control / control evaluations literature (main vs side tasks; adversarial protocols).  
7. Souly, A., Kirk, R., et al. *UK AISI Alignment Evaluation Case-Study.* arXiv:2604.00788 (example reporting style).  
