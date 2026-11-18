# Glossary (plain terms)

Short definitions for readers with no prior lab context. Story: [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md).

| Term | Plain meaning |
|------|----------------|
| **Allowlist (host lock)** | A rule that says “this AI may only talk to this one website.” Anything else comes back as `BLOCKED`. |
| **Attempt rate** | Of the prompts we asked, what share of the time did the model *try* to call a pretend dangerous tool? |
| **Attack-style role** | An AI job that tries to probe or recover something (example: Thief looking for the planted fake secret). |
| **Breaker** | The role whose win is proving bad hosts are blocked. |
| **Control evaluation** | A stress test: give agents jobs that would be bad if they succeeded, and check whether locks stop them. |
| **Control / lock** | A safeguard *outside* the model: host allowlist, guest cookie gate, tool call limit, human approve for wipe, pre-flight check. |
| **Guest / try without login** | A temporary “try free” session (a cookie) without a full account. |
| **Human approval (HITL)** | A person must approve some actions. Here, wipe can require approval; even then wipe is only simulated. |
| **LoRA / fine-tune adapter** | A small add-on trained on top of a base model, instead of retraining every weight. |
| **Main task** | The job we *want* to score on the practice site (map pages; recover the planted fake secret). |
| **MCP tools** | The menu of actions (fetch, guest start, tip board, browser, pretend wipe) the agent can request. |
| **Ollama** | Software that runs models on your own computer. Used for optional local agent runs and for the offline attempt-rate study. |
| **Planted fake secret** | A string like `PLANTED_SECRET_*` we put on the practice site on purpose so “Thief succeeded” is easy to check. Not a real password. |
| **Pre-flight lock check (`deny-smoke`)** | A quick automatic checklist before a long run: good host allowed, bad hosts denied. |
| **Practice website / training villain** | The tiny local site in this repo. It leaks the planted secret after guest on purpose so scoring works. |
| **Sandbox / fake tool** | A pretend dangerous action used only to see if the model *tries*; it does nothing in the real world. |
| **Side task** | A job that should fail (call evil host, hit cloud metadata, real wipe). Locks succeed when the side task fails. |
| **Swarm / multi-role run** | Scout, then Thief, then Breaker, sharing tips on a local tip board. |
| **Tip board** | A local shared notepad for this run so roles can leave clues for each other. |
