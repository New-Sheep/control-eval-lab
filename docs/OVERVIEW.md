# Overview — Control Eval Lab

**Audience:** non-specialist or quick brief. Full methods and citations: [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md).

## What this is

A personal **technical report** plus a small **runnable laboratory** that measures whether locks around tool-using AI agents hold, and (separately) how often open-weight chat models try to call **pretend** high-risk tools.

This is **not** an attack toolkit for third-party websites, and it is **not** affiliated with the UK AI Security Institute. The writing style follows public AI-control evaluation norms (clear questions, metrics with sample sizes, explicit limitations).

## Two evaluation questions

1. **Model layer:** If you give a model a menu of fake dangerous tools, how often does it *try* to call them — even when it can sound careful in chat?
2. **System layer:** If you give agents real HTTP/browser tools, do network allowlists, guest-session gates, and related locks still hold?

## Key findings (executive)

1. Under a fixed synthetic-tool protocol (**262** prompts × **4** models), a second open-weight fine-tune attempted high-risk tools about **13%** of the time, versus about **77%** for a normal Qwen 2.5 7B Instruct baseline and about **79%** for a permissive offline comparison model (build steps not published).
2. Forcing the model to write reasoning first (**50** prompts × **4** models) did **not** reliably prevent tool attempts; models often described risk and still called the tool. A simple post-model blocker stopped fake execution.
3. On a local practice website designed to leak planted markers after guest login, automated tests and a pre-flight lock check **pass**; the “Thief” role has a clear success condition.
4. On **MimWise** (founder product, owner-authorized), the same *style* of pressure met stronger auth walls, empty guest lists, and flaky UI uploads — **harder** than the practice villain. Exact paths and traces stay private.
5. Chat “I won’t help with that” is **not** the same as refusing to press a tool button. System-level control measures remain necessary.

## What you can run today

Clone this repo → start the practice app → run `deny-smoke` and `pytest` (see [README](../README.md)). Optional live agents need an API key (OpenAI, NVIDIA NIM, or local Ollama).

## Reading order

1. This overview  
2. [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md) — full tech report  
3. [ARCHITECTURE.md](ARCHITECTURE.md) — diagrams and providers  
4. [REFERENCE.md](REFERENCE.md) — every agent and tool  
5. [RESULTS.md](RESULTS.md) — tables  
6. [GLOSSARY.md](GLOSSARY.md) — terms  
7. [dashboard/index.html](dashboard/index.html) — charts  
