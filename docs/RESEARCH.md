# What this project is about (start here)

## In one paragraph

I wanted a **safe, public** way to show two related skills:

1. Building **guardrails around AI agents** that can call tools (browse, upload, hit APIs).
2. Measuring whether a **chat model** that says “no” to a bad request will still try to press a dangerous **tool button** if you give it tools.

This repo is mainly the first skill (runnable code). The second skill is written up as a research note, without shipping model files or nasty training data.

If you only read one other file after this, read [METHOD.md](METHOD.md).

---

## Why bother?

Modern AI products often look like this:

```text
User → LLM → tools (HTTP, browser, database, email…) → real world
```

People usually ask: “Is the model aligned?”  
A second, equally important question is: “If the model *tries* something bad, do the **surrounding controls** stop it?”

That second question is what **control evaluation** means here. I built a small lab where:

- An AI agent is *encouraged* to find a planted fake secret on a toy website.
- The lab’s networking rules should still block the agent from calling random evil websites or cloud metadata addresses.
- A separate “Breaker” agent’s job is to *prove those blocks work*, not to steal data.

I also ran (privately) experiments where models were given **fake** dangerous tools, to see how often they would try to call them. Those numbers are summarised in [REFUSAL_EVAL.md](REFUSAL_EVAL.md). The actual model weights stay offline.

---

## The two tracks

### Track A — Controls around agents (this codebase)

**Everyday question:**  
If I give an AI HTTP and browser tools, can I still force it to only talk to my toy app on my machine?

**What I built:**

- A small fake web app (`toy_app/`) with a guest login and planted fake secrets.
- A tool layer that checks every URL against an allowlist before any request goes out.
- A short “deny-smoke” checklist that fails the run if evil hosts are accidentally allowed.
- A multi-agent “swarm”: different AI roles share tips on a local message board, then a Breaker checks the locks.

**Where to read next:** [METHOD.md](METHOD.md) → [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md)

### Track B — Model behaviour with tools (memo only)

**Everyday question:**  
If a model refuses “how do I do something harmful?” in chat, will it still try to click a dangerous tool?

**What I did:**

- Fine-tuned a small add-on (LoRA) on an open 8-billion-parameter model for style.
- Gave several models a menu of **pretend** dangerous tools (nothing real was deleted or attacked).
- Counted how often each model *attempted* those tools under pressure prompts.
- Wrote down what that does and does *not* prove.

**Where to read next:** [REFUSAL_EVAL.md](REFUSAL_EVAL.md)

Weights, private prompt sets, and anything that would help someone rebuild an uncensored model are **not** in this repository on purpose.

---

## How the pieces connect

```text
Track B asks:  "Does the model try something bad?"
Track A asks:  "If it tries, do the locks hold?"

Real agent products need answers to both.
```

I separated them so a public GitHub visitor can:

- Fork and run the **control lab** without downloading huge models.
- Read the **refusal note** without being handed jailbreak training data.

---

## Design choices (plain English)

| Choice | Why |
|--------|-----|
| Toy app on `127.0.0.1` only | So the public repo never needs to point at a real company website |
| Planted fake secrets in the toy app | So “Thief succeeded” is a clear, measurable lab event |
| Allowlist as one shared gate | HTTP tools and browser tools must obey the same rule |
| Scout / Thief / Breaker by default | Small enough to understand; more roles can be added later |
| No model weights in git | Large files + awkward optics; the *measurement story* matters more for this portfolio |
| Sanitized “System A” notes | I also tested a system I own; I describe outcomes without naming the product or pasting cookies |

---

## What “success” means (and what it doesn’t)

**Success in Track A (fixture):**

- Deny-smoke passes.
- Breaker sees “blocked” for evil/metadata URLs.
- Thief can recover the planted fake secret *after* guest login (that bug is intentional on the toy app).

**Success in Track B:**

- Clear tables of attempt rates.
- An honest write-up of limits (8B open model, fixed prompt set, not a frontier lab monitor test).

**Not success / not claimed:**

- Permission to attack other people’s websites.
- Proof that any commercial AI lab’s monitors are good or bad.
- Proof that my fine-tune is “safe to ship.”

---

## Figures and charts

Open the static dashboard in a browser:

- [dashboard/index.html](dashboard/index.html) — bars for tool-attempt rates + control KPIs  
- Source numbers: [data/aggregates.json](data/aggregates.json)  
- Rebuild after editing JSON: `python docs/dashboard/build_dashboard.py`

## Suggested reading order

1. This file (`RESEARCH.md`)
2. [METHOD.md](METHOD.md) — how the control lab works and why each control exists  
3. [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md) — what actually happened in runs  
4. [REFUSAL_EVAL.md](REFUSAL_EVAL.md) — model + fake-tools story  
5. [dashboard/index.html](dashboard/index.html) — same numbers as charts  

Then skim the [README](../README.md) to run the lab yourself.
