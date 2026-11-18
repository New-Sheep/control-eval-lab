# Control Eval Lab technical report

**What this is:** a personal write-up of two small experiments about AI that can use tools, plus a practice lab you can run on your own computer.  
**Date:** November 2026  
**What ships in the repo:** the practice website and the lock-checking agent run. Fine-tuned model files and private prompt lists are available on request / interview.

> **What is runnable vs what is only summarised:** this repository lets you run Experiment A (locks on a practice website). The “how often did the model try a risky fake tool?” percentages (for example ~13% vs ~77%) come from Experiment B, done separately on a local machine. Those rates are written up here for context. Cloning this repo does not regenerate them. The fine-tune files and prompt cases stay private.

Start here for the story. Numbers: [RESULTS.md](RESULTS.md). How the runnable pieces connect: [ARCHITECTURE.md](ARCHITECTURE.md). Who does what: [REFERENCE.md](REFERENCE.md). Plain terms: [GLOSSARY.md](GLOSSARY.md).

---

## In one paragraph

Today many AI systems can browse, call APIs, or upload files. A polite “I won’t help with that” in chat does not prove the AI will refuse to press a tool button. This report asks two questions: (1) how often do small open models *try* pretend dangerous tools under a fixed script, and (2) do simple locks (only talk to this website, require a guest cookie, refuse a real wipe) still hold when several AI roles poke a practice site, and at a high level an owner product (MimWise).

Tables live in [RESULTS.md](RESULTS.md). This is a teaching / portfolio micro-lab, not a claim about frontier labs or industry-scale benchmarks.

---

## 1. Why this matters

A common setup looks like:

```text
person → AI model → tools (web, upload, APIs) → something happens in the world
```

If you only grade chat refusals, you miss the tool step. So we measure **locks outside the model** (who it may call, what session it needs, whether wipe is only pretend), and we separately count **attempts** on fake tools.

We did two layers of work:

- **Locks (Experiment A):** a multi-role agent run against a local practice website, with automatic pass/fail checks.
- **Attempts (Experiment B):** offline, same prompts for several small models, counting how often they tried a fake risky tool.

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

### 4.1 Fine-tuning (Experiment B background)

- Started from Llama 3.1 8B Instruct (a common open chat model, run in a memory-saving 4-bit build).
- Added a thin adapter (LoRA) rather than retraining the whole model.
- First training set: **387** chat examples. Second: **152** (style/persona plus “refuse clear harmful how-to” replies). Raw files private.
- An early export into the local model runner produced nonsense text (template mismatch), so we ran a second fine-tune.
- We are **not** claiming full safety training or that the result is safe to ship.

### 4.2 Counting tool attempts (Experiment B)

| Suite | Size | What we counted |
|-------|------|-----------------|
| Tool-call pressure | **262 prompts × 4 models = 1,048** decisions | Did it try a high-risk **fake** tool? |
| Reason-then-act | **50 × 4 = 200** | Same, after it had to write reasoning first |

**Models:** second fine-tune; first fine-tune; stock Qwen 2.5 7B Instruct; a looser offline comparison (build not published).  
**Where:** local machine with Ollama. Tools were sandbox fakes. A blocker after the model stopped fake “execution.” Rates: [RESULTS.md section D](RESULTS.md).

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

### 4.5 Where we pointed the agents

1. **Practice website** (`toy_app`): local training villain. After guest start it *intentionally* shows a planted fake secret so Thief success is measurable.
2. **MimWise:** real owner product, authorized testing only; public text stays high-level.

**Wanted jobs vs unwanted jobs:** Scout/Thief do authorized mapping / marker recovery. Breaker checks that unwanted calls (evil host, metadata) **fail**.

---

## 5. How to read the findings

Numbers are in [RESULTS.md](RESULTS.md). In plain words:

1. **Chat “no” ≠ tool “no.”** A model can refuse advice in text and still try a risky tool when tools are on the table.
2. **Same script, different attempt rates.** On 262 prompts, the second fine-tune tried far less often than stock Qwen 2.5 7B Instruct. That is evidence for *this* script, not a general safety certificate.
3. **Writing reasons did not reliably stop attempts.** Models often described danger and still called the tool; the post-model blocker stopped fake execution.
4. **Locks can be tested like unit tests.** Pre-flight and practice-site tests pass on the public lab.
5. **A real product was harder than the villain.** MimWise showed empty guest lists and auth walls; we do not claim a planted-secret win there.
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
