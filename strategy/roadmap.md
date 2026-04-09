# MemOps Roadmap  
  
## Executive Summary  
  
MemOps is being built as a focused MVP within the constraints of a short development window and a single maintainer.  
  
For that reason, the roadmap is intentionally narrow. It prioritizes:  
  
- real technical execution,  
- visible progress,  
- clear documentation,  
- and a demo that proves the project is more than a wrapper around an API.  
  
The rule behind this roadmap is simple:  
  
> **A smaller and correct MVP is more valuable than a broader but unfinished one.**  
  
This document organizes the project into three levels of priority:  
  
- **P0 — Core MVP:** required for a credible CUBO+ submission  
- **P1 — Strong differentiators:** only if P0 is stable  
- **P2 — Post-hackathon extensions:** useful later, not required now  
  
---  
  
## 1. Current Development Context  
  
MemOps is currently in its early build stage.  
  
At this point, the repository already defines:  
  
- the project identity,  
- the open-source positioning,  
- the strategy documentation,  
- and the target architecture.  
  
The next priority is technical execution.  
  
Because the project is being built by one developer, the roadmap must stay realistic. It should emphasize depth over breadth.  
  
---  
  
## 2. P0 — Core MVP  
  
These items define whether MemOps exists as a serious project.  
  
## 2.1 Repository foundation  
  
The repository should look complete, understandable, and auditable.  
  
Minimum requirements:  
  
- root `README.md`  
- `src/README.md`  
- `LICENSE`  
- strategy documents  
- technical docs in `docs/`  
- basic project configuration  
- visible daily progress in GitHub  
  
### Success condition  
A third party should be able to understand what MemOps is and how the repository is organized.  
  
---  
  
## 2.2 Configurable mempool-compatible backend support  
  
MemOps must be able to work with:  
  
- the public mempool.space endpoint as a default example,  
- and self-hosted mempool-compatible backends through configuration.  
  
### Success condition  
The tool should not be locked to a single public website.  
  
---  
  
## 2.3 `analyze-tx`  
  
This is the first mandatory technical command.  
  
It should:  
  
- accept a `txid`,  
- query a mempool-compatible backend,  
- retrieve the `raw hex`,  
- inspect the transaction locally,  
- recompute key metrics where applicable,  
- detect replaceability signals such as opt-in RBF,  
- and produce structured output.  
  
### Success condition  
MemOps can analyze a real transaction in a way that is visibly more rigorous than simply repeating explorer output.  
  
---  
  
## 2.4 `why-stuck`  
  
This is the most important product-level command in the MVP.  
  
It should:  
  
- compare the transaction’s fee position against current fee pressure,  
- explain why the transaction is likely not confirming,  
- identify whether RBF appears possible,  
- indicate whether waiting is reasonable,  
- and output a recommended action.  
  
Possible outputs include:  
  
- `wait`  
- `rbf`  
- `cpfp`  
- `cannot-rescue`  
  
### Success condition  
The tool can answer the main human question of the project:  
  
> **Why is this transaction stuck, and what should be done next?**  
  
---  
  
## 2.5 Basic export artifacts  
  
The CLI should generate outputs that can be reviewed outside the terminal.  
  
Minimum exports:  
  
- `analysis.json`  
- `report.md`  
  
If `plan-rbf` is ready, then also:  
  
- `plan.json`  
  
### Success condition  
The project leaves auditable evidence, not just terminal output.  
  
---  
  
## 2.6 Demo readiness  
  
The project should include at least one reproducible case for Demo Day.  
  
That may include:  
  
- one real or historical mainnet transaction for analysis,  
- and one documented rescue scenario or prepared example for planning logic.  
  
### Success condition  
The demo is repeatable and not dependent on improvisation.  
  
---  
  
## 3. P0.5 — Strongly Desired if Time Allows  
  
These are very valuable, but they should not break P0 stability.  
  
## 3.1 `plan-rbf`  
  
This is the most important extension after `analyze-tx` and `why-stuck`.  
  
It should:  
  
- confirm whether replacement is plausible,  
- estimate the target fee needed,  
- calculate fee delta,  
- produce an auditable plan,  
- and, if implemented in time, generate a PSBT artifact.  
  
### Success condition  
MemOps does not stop at diagnosis; it also prepares a structured next step.  
  
---  
  
## 4. P1 — Strong Differentiators  
  
Only attempt these if P0 is working and documented.  
  
## 4.1 `plan-cpfp`  
  
Potentially useful, but more complex for a solo-maintainer timeline.  
  
It may include:  
  
- ownership checks,  
- package logic,  
- and child fee estimation.  
  
### Rule  
Do not pursue this if it endangers `why-stuck` or `plan-rbf`.  
  
## 4.2 `watch-tx` or `watch-mempool`  
  
A live or near-live monitoring mode could strengthen the operational feel of the project.  
  
Possible implementation styles:  
  
- polling first,  
- WebSocket later if verified safely.  
  
### Rule  
Only add if the core analysis flow is already solid.  
  
## 4.3 `triage-batch`  
  
A batch mode for multiple transactions could make MemOps feel more operationally mature.  
  
But this is clearly secondary to the core user story.  
  
---  
  
## 5. P2 — Post-Hackathon Extensions  
  
These items are valuable for long-term growth, but they are not necessary for the current evaluation stage.  
  
Possible future work:  
  
- SQLite persistence  
- deeper Bitcoin Core validation  
- more advanced package analysis  
- broader transaction script support  
- stronger release and contribution workflows  
  
These should be considered only after the MVP is credible.  
  
---  
  
## 6. What Gets Cut First If Time Becomes Tight  
  
To protect the quality of the project, these items should be cut before the core is weakened:  
  
- CPFP planning  
- live monitoring  
- batch triage  
- persistence  
- cloud extras  
- non-essential integrations  
  
The following should **not** be cut:  
  
- configurable backend support  
- local transaction inspection  
- `analyze-tx`  
- `why-stuck`  
- export artifacts  
- technical documentation  
- honest worklog and visible progress  
  
---  
  
## 7. Definition of Done for the CUBO+ Evaluation Stage  
  
MemOps should be considered ready for the evaluation stage if it can demonstrate the following:  
  
### Technical  
- analyze a real transaction from a `txid`  
- retrieve and inspect `raw hex`  
- compute or validate key transaction metrics locally  
- detect opt-in replacement signals  
- explain why a transaction is likely stuck  
- produce a clear recommendation  
- export machine-readable and human-readable outputs  
  
### Documentation  
- clear root README  
- technical README in or near `src/`  
- strategy documentation in English  
- basic architecture and assumptions docs  
- reproducible demo script  
  
### Open-source readiness  
- public license  
- no-affiliation disclaimer  
- repository structure that a third party can understand  
- visible evolution in GitHub  
  
### Demo readiness  
- a prepared scenario  
- a clear narrative  
- a technical walkthrough that matches the narrative  
- outputs that can be shown and explained  
  
---  
  
## Conclusion  
  
The roadmap for MemOps is intentionally strict because that is the professional choice for a single-maintainer MVP.  
  
The goal is not to win by listing more features.  
  
The goal is to demonstrate one thing clearly:  
  
**MemOps can turn mempool visibility into verifiable operational reasoning.**  
  
If that is achieved with a clean repository, real code, and a disciplined demo, the project will already be strong.
