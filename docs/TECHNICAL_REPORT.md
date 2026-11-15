# Control Eval Lab: Measuring Egress and Session Controls for Tool-Using LLM Agents, with an Open-Weight Synthetic-Tool Propensity Study

**Type:** Personal technical report + reproducible micro-laboratory  
**Date:** November 2026  
**Affiliation:** Independent (not affiliated with the UK AI Security Institute)  
**Artifacts:** This repository (harness + practice app). Fine-tune weights and private eval JSONL on request / interview.

Non-specialist brief: [OVERVIEW.md](OVERVIEW.md) · Diagrams: [ARCHITECTURE.md](ARCHITECTURE.md) · Catalog: [REFERENCE.md](REFERENCE.md) · Tables: [RESULTS.md](RESULTS.md)

---

## Abstract

Tool-using language-model agents can take actions in the world; chat refusals alone do not bound that risk. This report describes a small open laboratory that (i) measures how often open-weight ~8B models *attempt* high-risk **synthetic** tool calls under fixed prompt protocols, and (ii) measures whether simple **control measures**—URL allowlisting, guest-session gates, tool budgets, and simulated human-approved wipe—hold when multi-agent crews exercise HTTP and browser tools against a local practice application and, at high level, against an owner-authorized production product (MimWise).

On a synthetic-tool suite of **262** prompts × **4** models (**1,048** decisions), attempt rates were approximately **13%** (second fine-tune), **36%** (first fine-tune), **77%** (Qwen 2.5 7B Instruct), and **79%** (permissive offline comparison). A reason-then-act suite (**50×4**) showed that written risk reasoning often co-occurred with continued tool attempts. On the practice fixture, automated allowlist and guest-session tests pass; on MimWise, the same *style* of pressure met stronger authentication and empty guest lists. Limitations: open 8B models, fixed prompts, no frontier-lab monitors, and no claim of ControlArena/Inspect scale.

---

## Executive summary — key findings

1. **Chat refusal ≠ tool refusal.** Models can decline harmful chat advice and still emit high-risk synthetic tool calls when prompted to act with tools.
2. **Fine-tune shift under a fixed protocol.** The second LoRA fine-tune attempted high-risk synthetic tools ~**13%** of the time vs ~**77%** for stock Qwen 2.5 7B Instruct (n=262 prompts each). This is protocol-specific evidence, not a general safety certificate.
3. **Reasoning is not a control layer.** In reason-then-act (n=50), models frequently described danger and still attempted the tool; a post-model blocker stopped fake execution.
4. **System controls are measurable.** Allowlist pre-flight checks and guest SoftTrial tests on the practice app are automated and passing (`deny-smoke`, `pytest`).
5. **Realistic products differ from villains.** MimWise (owner-authorized) was harder than an intentional SoftTrial fixture: empty guest lists, auth-walled uploads, no claimed cross-user planted-secret IDOR.
6. **Scope honesty.** This is a micro-setting for portfolio and teaching control-evaluation ideas—not a frontier sabotage case study and not an AISI product.

---

## 1. Introduction

Modern deployments increasingly look like:

```text
user → model → tools (HTTP, browser, upload, APIs) → side effects
```

Evaluating only chatbot refusals underestimates risk when the model can press tools. Work on **AI control** argues for designing *control measures* that constrain actions even if training-time alignment is imperfect, and for **control evaluations** that stress those measures under adversarial pressure. Complementary work on **agent misuse** (e.g. AgentHarm) measures compliance with harmful multi-step tool tasks using synthetic tools and graded rubrics.

This project contributes a **small, public, reproducible micro-lab** plus a private open-weight propensity study:

- **System layer:** multi-agent scaffold with FastMCP tools, shared egress allowlist, and a practice web app with planted markers.
- **Model layer:** LoRA fine-tunes on Llama 3.1 8B Instruct and synthetic-tool attempt-rate comparisons under Ollama.

We adopt AISI-adjacent reporting norms—clear questions, metrics with sample sizes, and explicit limitations—without claiming AISI affiliation or Inspect/ControlArena integration.

---

## 2. Threat model and evaluation questions

### 2.1 Threat model (lab scale)

An operator deploys an LLM agent with HTTP/browser tools against a web application. Risks in scope:

- **Egress abuse:** contacting non-approved hosts or cloud metadata endpoints.
- **Session / access probing:** using guest try-without-login paths to read data that should stay closed.
- **Destructive intent:** requesting database wipe (we only *simulate* this).
- **Model-layer tool misuse:** emitting high-risk tool calls when handed a synthetic tool menu (AgentHarm-adjacent).

Out of scope: third-party unauthorized testing; claiming compromise of systems we do not own; evaluating proprietary frontier monitors.

### 2.2 Evaluation questions

| ID | Layer | Question |
|----|-------|----------|
| **Q1** | Model | Given synthetic high-risk tools, how often do open ~8B models *attempt* calls under pressure and reason-then-act protocols? |
| **Q2** | System | Given HTTP/browser tools and a multi-agent crew, do allowlist + guest session + related measures hold on a practice fixture—and how does an owner product compare at high level? |

---

## 3. Related work

| Work | Relevance | How we differ |
|------|-----------|---------------|
| **AgentHarm** (Andriushchenko, Souly, et al.; ICLR 2025) | Synthetic tools; agent misuse; attempt/compliance measurement | We use a smaller private suite on open 8B Ollama models; we do not release harmful case JSONL |
| **AI control / ControlArena** (UK AISI + collaborators) | Main vs side tasks; red/blue protocols; sandboxes | We implement a micro allowlist+HITL setting, not ControlArena environments |
| **Inspect** (UK AISI) | Eval scaffolding, tools, sandboxes | Our swarm uses OpenAI Agents SDK + FastMCP; not Inspect tasks |
| **Breaking agent backbones** (Bazinska et al.) | Backbone LLM security in agents | We do not run the b³ benchmark; we share the concern that agent risk ≠ chat risk |

---

## 4. Methods

### 4.1 Open-weight fine-tune

- **Base:** Llama 3.1 8B Instruct (4-bit Unsloth build).
- **Adapter:** LoRA **r=16**, **alpha=16**.
- **Data:** first fine-tune **n=387** chat examples; second fine-tune **n=152** (persona/style SFT + refuse-style replies for clear harmful how-tos). Raw JSONL private.
- **Issue:** early Ollama export produced incoherent text (template/export mismatch) → second fine-tune.
- **Not claimed:** full RLHF/DPO safety training; permission to redistribute permissive stacks.

Details: [REFERENCE.md §7](REFERENCE.md).

### 4.2 Synthetic-tool propensity suites

| Suite | n prompts × models | Metric |
|-------|--------------------|--------|
| Tool-call pressure | **262 × 4 = 1,048** | High-risk synthetic-tool **attempt rate** |
| Reason-then-act | **50 × 4 = 200** | Attempt rate after required reasoning |

**Models compared:** second fine-tune; first fine-tune; Qwen 2.5 7B Instruct; permissive offline comparison (build not published).  
**Runner:** local Ollama. Tools were **sandbox fakes** (e.g. pretend infra shutdown / DB wipe). A post-model blocker prevented fake “execution.”

### 4.3 Agent scaffold

- **Orchestration:** OpenAI Agents SDK; roles from JSON; SQLite tip board.
- **Tools:** FastMCP server ([REFERENCE.md §5](REFERENCE.md)).
- **Public crew:** Scout → Thief → Breaker.
- **Private MimWise extras:** Crawler, Injector, UI Players (lesson / demo / dopa).

### 4.4 Control measures under test

| Measure | Role in evaluation |
|---------|-------------------|
| URL allowlist | Primary egress control |
| `deny-smoke` pre-flight | Catches misconfiguration before long runs |
| Tool budget (default 64) | Limits runaway loops |
| Simulated wipe + HITL flag | Measures destructive *requests* without real wipe |
| Guest session gate | Session control on practice app (and product SoftTrial) |

Figures: [ARCHITECTURE.md](ARCHITECTURE.md).

### 4.5 Settings

1. **Practice app (`toy_app`)** — local SoftTrial villain with planted `PLANTED_SECRET_*` markers (intentional IDOR-after-guest for scoring).
2. **MimWise** — owner-authorized live product; high-level outcomes only.

**Main task vs side task (fixture swarm):** Scout/Thief pursue authorized recon / marker recovery; Breaker verifies side-task egress **fails**.

---

## 5. Metrics summary

| Metric | Value |
|--------|-------|
| Synthetic-tool prompts (pressure) | 262 per model |
| Models in propensity compare | 4 |
| Reason-then-act prompts | 50 per model |
| Fine-tune examples | 387 then 152 |
| Practice-app `pytest` | 7 passed |
| Pre-flight lock check | PASS (2026-11-15) |
| Public default agents | 3 (Scout, Thief, Breaker) |
| Public MCP tools | 14 (see Reference) |

Charts: [dashboard/index.html](dashboard/index.html).

---

## 6. Results

### Finding A — Propensity under synthetic tools

Approximate attempt rates (pressure suite):

| Model | Attempt rate |
|-------|--------------|
| Second fine-tune | ~13% |
| First fine-tune | ~36% |
| Qwen 2.5 7B Instruct | ~77% |
| Permissive offline comparison | ~79% |

**Interpretation:** Under *this* protocol, the second fine-tune attempted fewer high-risk tools than stock instruct. **Does not show:** production safety, robustness to unseen attacks, or frontier-model behaviour.

### Finding B — Reason-then-act

Second fine-tune ~**4%** dangerous attempts but more structured-format failures. Other models often verbalized risk then still attempted tools; blockers mattered.

### Finding C — Practice fixture controls

Guest notes: 403 without cookie; 200 + planted marker with guest. Admin export remains 403. Allowlist denies `evil.example`, metadata, and arbitrary third-party hosts. Evidence: [RESULTS.md §A](RESULTS.md).

### Finding D — MimWise (sanitized)

Unauth mutating paths often 401/403; guest lists 200 empty; uploads often 403; browser SoftTrial partial; egress still blocked by harness allowlist. **Harder than the villain fixture.** No claimed planted-secret IDOR win. Evidence: [RESULTS.md §C](RESULTS.md).

### Finding E — Red vs blue framing

Thief/Injector/UI players act as **attack-oriented** policies on authorized targets; Breaker + allowlist act as **control** checks. Useful pedagogical mapping to control-evaluation language—not a full ControlArena protocol study.

---

## 7. Limitations

1. **Scale:** Open ~8B models and small prompt sets; not frontier systems.
2. **Fixed protocols:** Attempt rates are not estimates of real-world misuse prevalence.
3. **Synthetic tools:** Measure propensity to *emit* calls, not real-world harm.
4. **Fixture confounding:** Practice SoftTrial is designed to leak markers; success there is not product compromise.
5. **MimWise opacity:** Public text omits paths/cookies by design; private demo for interviews.
6. **Scaffold:** Not Inspect/ControlArena; no claim of equivalent statistical analysis tooling.
7. **No affiliation:** Independent portfolio work.

---

## 8. Reproducibility

```bash
pip install -e ".[dev]"
uvicorn toy_app.main:app --host 127.0.0.1 --port 8000
python -m control_eval deny-smoke
pytest -q
# optional:
# python -m control_eval swarm --provider openai --max-turns 12
```

Providers: OpenAI / NVIDIA NIM / Ollama — [ARCHITECTURE.md](ARCHITECTURE.md).  
Private weights and MimWise traces: interview / on request.

---

## References

1. Andriushchenko, M., Souly, A., et al. *AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents.* ICLR 2025. arXiv:2410.09024.  
2. UK AI Security Institute. *How to evaluate control measures for AI agents?* (blog, 2025). https://www.aisi.gov.uk/blog/how-to-evaluate-control-measures-for-ai-agents  
3. UK AISI / Redwood et al. *ControlArena* — library for AI control experiments. https://github.com/UKGovernmentBEIS/control-arena  
4. UK AISI. *Inspect* evaluation framework. https://inspect.aisi.org.uk/  
5. Bazinska, J., et al. *Breaking agent backbones: Evaluating the security of backbone LLMs in AI agents.* arXiv:2510.22620.  
6. Greenblatt, R., et al. AI control / control evaluations literature (foundational framing for main vs side tasks and adversarial protocols).  
7. Souly, A., Kirk, R., et al. *UK AISI Alignment Evaluation Case-Study.* arXiv:2604.00788 (reporting style reference: executive summary, limitations).  

---

## Appendix pointers

- Terms: [GLOSSARY.md](GLOSSARY.md)  
- Every agent and tool: [REFERENCE.md](REFERENCE.md)  
- Raw tables: [RESULTS.md](RESULTS.md)  
