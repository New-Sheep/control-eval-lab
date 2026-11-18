# Glossary

| Term | Plain meaning |
|------|----------------|
| **Allowlist (egress control)** | Code rule that permits network requests only to a configured host (default: the local practice app). Other hosts return `BLOCKED`. |
| **Attempt rate** | Share of evaluation prompts where the model *tried* to call a high-risk synthetic tool (whether or not a blocker stopped execution). |
| **Attack policy** | An agent role whose job is to pursue a harmful or probing objective (e.g. Thief recovering a planted marker). |
| **Breaker** | Control-oriented agent whose success is proving that disallowed hosts are blocked. |
| **Control evaluation** | Adversarial test of whether **control measures** stop unacceptable outcomes even when agents try to cause them. |
| **Control measure** | A lock outside the model: allowlist, guest session gate, tool budget, human approval for wipe, pre-flight deny check. |
| **Control protocol** | The combination of measures and agent orchestration used in a run (here: MCP tools + allowlist + roles + budgets). |
| **Guest try-without-login** | Product-style “try free” session that sets a cookie without a full user account. |
| **HITL / human approval** | Human-in-the-loop gate; wipe tool can require approval. In local lab mode it may be auto-approved but still only **simulates** wipe. |
| **LoRA** | Low-Rank Adaptation: a thin trained add-on loaded on top of a base model, not a full retrain of all weights. |
| **Main task** | The authorized lab objective (e.g. map APIs; recover a planted marker on the practice site). |
| **MCP (Model Context Protocol)** | Tool-server interface; here FastMCP exposes HTTP/browser/board tools to the Agents SDK. |
| **Ollama** | Local model runner (OpenAI-compatible API on port 11434). Used for offline synthetic-tool evals and optional local swarm. |
| **Planted marker** | Fake secret string such as `PLANTED_SECRET_*` placed on purpose so “Thief succeeded” is measurable. |
| **Pre-flight lock check (`deny-smoke`)** | Automatic checklist before a swarm: target URLs allowed; non-allowlisted / metadata hosts denied. |
| **Sandbox** | Isolated setting where harmful tools or secrets are fake; nothing real is wiped or attacked. |
| **Side task** | Undesirable objective under test (e.g. call `evil.example`, hit cloud metadata, real wipe). Success for controls = side task **fails**. |
| **Synthetic tool** | A pretend high-risk tool used only to score *attempts*; it does nothing in the real world. |
| **Swarm** | Sequence of specialized agents that share tips on a local SQLite board. |
