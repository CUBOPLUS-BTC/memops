# Demo Script for MemOps  
  
## Purpose  
  
This document defines the intended Demo Day flow for MemOps.  
  
The goal of the demo is not to show many features. The goal is to make one idea clear:  
  
> **MemOps is not another explorer. It is a verification-first operational tool for stuck Bitcoin transactions.**  
  
The demo should therefore stay disciplined, clear, and short.  
  
---  
  
## Primary Audience Takeaway  
  
By the end of the demo, the audience should understand:  
  
- what problem MemOps addresses,  
- why explorer visibility is not enough,  
- how MemOps uses a mempool-compatible backend without becoming a trivial wrapper,  
- and why the project fits the “Don’t trust, verify” philosophy.  
  
---  
  
## Demo Structure  
  
The full demonstration should support a 5-minute non-technical pitch followed by a short technical walkthrough.  
  
The technical part should be built around the smallest number of commands needed to prove the value of the project.  
  
---  
  
## Pre-Demo Checklist  
  
Before the presentation, confirm the following:  
  
- the repository is up to date,  
- the selected demo transaction is documented,  
- the backend endpoint being used is working,  
- the terminal output is readable,  
- export paths are known,  
- fallback screenshots or sample outputs are available,  
- and internet dependency has been reduced as much as possible.  
  
If a live backend is used, also prepare a fallback explanation in case the service is slow or unavailable.  
  
---  
  
## Recommended Demo Flow  
  
## 1. Opening framing  
  
Suggested message:  
  
> “MemOps is a verification-first Bitcoin incident response CLI. Public explorers show what is happening, but operators also need help deciding what to do next when a transaction is stuck.”  
  
This establishes the product category clearly.  
  
---  
  
## 2. Present the scenario  
  
Explain the chosen case in plain terms:  
  
- a transaction is unconfirmed,  
- fee pressure is high or relevant,  
- and the operator needs a more structured answer than what an explorer alone provides.  
  
Keep this short. Do not spend too much time on Bitcoin theory before showing the tool.  
  
---  
  
## 3. Run `analyze-tx`  
  
Goal of this step:  
  
- show that MemOps starts from a `txid`,  
- reaches a mempool-compatible backend,  
- retrieves transaction data,  
- and performs structured analysis rather than only showing raw API output.  
  
What to highlight while presenting:  
  
- transaction identification,  
- local inspection or recomputation,  
- replaceability signals,  
- and structured output.  
  
Suggested speaking line:  
  
> “The point here is not only to fetch transaction data. It is to inspect it in a way that supports later reasoning.”  
  
---  
  
## 4. Run `why-stuck`  
  
This is the key moment of the demo.  
  
Goal of this step:  
  
- explain why the transaction is likely stuck,  
- compare it against current fee pressure,  
- and produce a recommendation.  
  
What to highlight:  
  
- fee position versus current context,  
- whether waiting is reasonable,  
- whether replacement looks possible,  
- and the clarity of the recommendation.  
  
Suggested speaking line:  
  
> “This is the core of the project: not just seeing that the transaction is unconfirmed, but receiving a structured explanation of why and what to consider next.”  
  
---  
  
## 5. Show exports  
  
If available, show:  
  
- `analysis.json`  
- `report.md`  
- and later `plan.json` or other artifacts  
  
This step is important because it proves that the tool is not only interactive but also auditable.  
  
Suggested speaking line:  
  
> “MemOps leaves behind artifacts that can be reviewed later instead of relying only on terminal output or screenshots.”  
  
---  
  
## 6. Optional: show `plan-rbf`  
  
Only do this if the feature is stable enough.  
  
If shown, keep the focus on:  
  
- structured next-step planning,  
- safety,  
- and auditability.  
  
Do not spend too much time on low-level details if the feature is still early.  
  
Suggested speaking line:  
  
> “The purpose is not to automate irreversible action by default. It is to prepare an auditable next step.”  
  
---  
  
## Demo Timing Suggestion  
  
### Non-technical framing  
~1.5 to 2 minutes  
  
### Technical walkthrough  
~2.5 to 3.5 minutes  
  
This keeps the full demo compact and credible.  
  
---  
  
## Fallback Plan  
  
If the live backend fails or the environment becomes unstable, use one or more of the following:  
  
- a saved export from a previous successful run,  
- screenshots of expected command outputs,  
- a documented historical case,  
- or a dry walkthrough of the analysis logic using prepared artifacts.  
  
The fallback plan should still communicate the value proposition clearly.  
  
---  
  
## What Not to Do in the Demo  
  
Avoid these mistakes:  
  
- trying to show too many commands,  
- explaining too many future features,  
- spending too much time on infrastructure,  
- or turning the demo into a generic explorer tour.  
  
The strength of MemOps is precision, not feature count.  
  
---  
  
## Closing Line  
  
Recommended ending:  
  
> “MemOps does not try to become another explorer. It adds a verification-first reasoning layer between mempool visibility and operational action.”  
  
---  
  
## Final Note  
  
The best MemOps demo is not the longest one.  
  
It is the one that clearly proves:  
  
- there is a real operational problem,  
- the tool addresses it in a disciplined way,  
- and the project is small on purpose, not small by accident.
