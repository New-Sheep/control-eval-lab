# What this project is about (short summary)

**Prefer the full story:** [JOURNEY.md](JOURNEY.md) — fine-tune → fake-tool eval → agents/MCP → Docker SoftTrial → MimWise → this public lab.

---

## In one paragraph

I wanted a **safe, public** way to show two related skills:

1. Building **guardrails around AI agents** that can call tools (browse, upload, hit APIs).
2. Measuring whether a **chat model** that says “no” to a bad request will still try to press a dangerous **tool button** if you give it tools.

This repo is mainly the first skill (runnable code). The second skill is a research memo without shipping model files or nasty training data.

---

## The two tracks

### Track A — Controls around agents (this codebase)

**Everyday question:** If I give an AI HTTP and browser tools, can I still force it to only talk to my toy app?

**What I built:** toy SoftTrial app, shared allowlist, deny-smoke, Scout → Thief → Breaker swarm.

**Read next:** [METHOD.md](METHOD.md) → [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md)

### Track B — Model behaviour with tools (memo only)

**Everyday question:** If a model refuses harmful chat, will it still try a dangerous tool?

**What I did:** LoRA on Llama 3.1 8B; fake-tool suites (~262 / ~50); attempt rates (~13/36/77/79%); weights stay private.

**Read next:** [REFUSAL_EVAL.md](REFUSAL_EVAL.md) · charts: [dashboard/index.html](dashboard/index.html)

```text
Track B asks:  "Does the model try something bad?"
Track A asks:  "If it tries, do the locks hold?"
```

---

## Design choices (plain English)

| Choice | Why |
|--------|-----|
| Toy app on `127.0.0.1` only | Public repo never needs a real company URL |
| Planted fake secrets | “Thief succeeded” is measurable |
| One shared allowlist | HTTP and browser obey the same gate |
| Scout / Thief / Breaker default | Small enough to understand |
| No model weights in git | Method > shipping risky artifacts |
| MimWise notes sanitized | Owner-authorized final test; no cookies / exploit recipes |

---

## What success means (and doesn’t)

**Track A (fixture):** deny-smoke PASS; Breaker sees BLOCKED; Thief can recover planted markers after guest (intentional villain).  
**Track B:** clear attempt-rate tables + honest limits (8B open models, fixed prompts).

**Not claimed:** permission to attack other people’s sites; frontier-lab monitor results; “safe to ship” fine-tune.

---

## Figures

- [dashboard/index.html](dashboard/index.html)  
- [data/aggregates.json](data/aggregates.json)  
- Rebuild: `python docs/dashboard/build_dashboard.py`

## Reading order

1. [JOURNEY.md](JOURNEY.md)  
2. [METHOD.md](METHOD.md)  
3. [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md)  
4. [REFUSAL_EVAL.md](REFUSAL_EVAL.md)  
5. [README](../README.md)  
