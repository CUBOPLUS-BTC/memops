# MemOps Roadmap  
  
## Executive Summary  
  
MemOps is being built as a focused MVP within the constraints of a short development window and a single maintainer.  
  
That means the roadmap must stay disciplined. The project should prioritize:  
  
- real technical execution,  
- visible progress,  
- honest documentation,  
- and a demo that proves the repository already works.  
  
The rule behind this roadmap remains simple:  
  
> **A smaller and correct MVP is more valuable than a broader but unfinished one.**  
  
At this point, MemOps has already delivered an executable inspection baseline. The next milestone is to move from **inspection** to **diagnosis**.  
  
---  
  
## 1. Current Development Context  
  
MemOps is no longer only a repository structure or architecture plan.  
  
The project now includes:  
  
- configuration loading from environment variables and `.env`,  
- a mempool-compatible backend adapter,  
- local raw transaction parsing,  
- explicit opt-in RBF detection,  
- a working CLI,  
- JSON output,  
- automated tests,  
- and a console-script entrypoint.  
  
This matters because the roadmap should reflect the real state of the repository, not an outdated future-state description.  
  
---  
  
## 2. Phase 1 Delivered Baseline  
  
Phase 1 established the technical base needed for a credible executable MVP.  
  
### 2.1 Repository foundation  
Delivered:  
  
- root `README.md`  
- `src/README.md`  
- `LICENSE`  
- strategy documents  
- technical docs in `docs/`  
- project configuration  
- visible Git history  
- automated tests  
  
### 2.2 Configurable backend support  
Delivered:  
  
- configurable backend URL  
- configurable network selection  
- support for mempool-compatible endpoint structure  
- settings loading from environment variables and `.env`  
  
### 2.3 Local transaction inspection  
Delivered:  
  
- raw transaction retrieval by `txid`  
- local parsing of transaction structure  
- sequence extraction  
- segwit detection  
- explicit opt-in RBF signaling analysis  
  
### 2.4 Executable CLI baseline  
Delivered:  
  
- human-readable CLI output  
- JSON CLI output  
- `python -m memops`  
- `memops` console script  
  
### 2.5 Phase 1 result  
The project now has a real inspection pipeline:  
  
1. accept `txid`,  
2. fetch raw hex,  
3. parse locally,  
4. analyze locally,  
5. render reviewable output.  
  
That is the current baseline on which the next milestone depends.  
  
---  
  
## 3. P0 — Next Core Milestone  
  
The next priority is to move from **transaction inspection** to **stuck-transaction diagnosis**.  
  
## 3.1 `why-stuck`  
This is now the most important next command.  
  
It should:  
  
- compare the transaction against current fee conditions,  
- explain why the transaction is likely not confirming,  
- indicate whether waiting is reasonable,  
- identify whether RBF appears possible,  
- and produce a clear recommendation.  
  
Possible outputs may include:  
  
- `wait`  
- `rbf`  
- `cpfp`  
- `cannot-rescue`  
  
### Success condition  
MemOps can answer the main user question:  
  
> **Why is this transaction stuck, and what should be done next?**  
  
---  
  
## 3.2 Fee-context retrieval  
  
To support `why-stuck`, MemOps should retrieve and normalize fee-market context such as:  
  
- recommended fee bands,  
- mempool pressure indicators,  
- and other backend data needed for comparison.  
  
### Success condition  
The CLI can explain transaction position relative to current conditions, not only transaction structure.  
  
---  
  
## 3.3 Auditable export artifacts  
  
The project should generate outputs that can be reviewed outside the terminal.  
  
Minimum desired exports:  
  
- `analysis.json`  
- `report.md`  
  
### Success condition  
The tool leaves behind artifacts that are useful for review, demos, and later incident documentation.  
  
---  
  
## 3.4 Demo readiness  
  
The project should include at least one reproducible case that shows:  
  
- current inspection output,  
- JSON output,  
- and, once implemented, `why-stuck` reasoning.  
  
### Success condition  
The demo is repeatable and not dependent on improvisation.  
  
---  
  
## 4. P0.5 — Strongly Desired After Diagnosis  
  
## 4.1 `plan-rbf`  
After `why-stuck`, the most important extension is structured RBF planning.  
  
It should eventually:  
  
- confirm whether replacement is plausible,  
- estimate target fee conditions,  
- calculate fee delta,  
- and produce an auditable plan.  
  
### Rule  
Do not pursue this if it weakens `why-stuck` quality.  
  
---  
  
## 5. P1 — Strong Differentiators  
  
Only attempt these after the diagnosis milestone is stable.  
  
### 5.1 `plan-cpfp`  
Potentially useful, but more complex.  
  
It may require:  
  
- ownership assumptions,  
- package reasoning,  
- and child fee estimation.  
  
### 5.2 `watch-tx` or `watch-mempool`  
A monitoring mode could later improve operational usefulness.  
  
### 5.3 `triage-batch`  
Batch handling for multiple transactions may become useful later, but it is clearly secondary to the core single-transaction flow.  
  
---  
  
## 6. P2 — Post-Evaluation Extensions  
  
Possible future work:  
  
- SQLite persistence  
- deeper Bitcoin Core validation  
- broader transaction-type support  
- more advanced package analysis  
- richer report generation  
- stronger release workflows  
  
These should only be pursued after the current MVP becomes a strong diagnostic tool.  
  
---  
  
## 7. What Gets Cut First If Time Becomes Tight  
  
To protect quality, these items should be cut before the core is weakened:  
  
- CPFP planning  
- live monitoring  
- batch triage  
- persistence  
- cloud extras  
- non-essential integrations  
  
The following should **not** be cut:  
  
- backend configurability  
- local transaction inspection  
- honest documentation  
- automated tests  
- `why-stuck`  
- auditable exports  
- demo readiness  
  
---  
  
## 8. Definition of Done for the Next Milestone  
  
MemOps should be considered ready for the next evaluation milestone if it can demonstrate the following:  
  
### Technical  
- inspect a real transaction from a `txid`  
- retrieve and inspect raw hex  
- compute and present key transaction metadata locally  
- detect explicit opt-in RBF signaling  
- explain why a transaction is likely stuck  
- produce a clear recommendation  
- export machine-readable and human-readable artifacts  
  
### Documentation  
- clear root README  
- technical README in `src/`  
- roadmap aligned with the actual repository state  
- reproducible demo script  
  
### Open-source readiness  
- public license  
- no-affiliation disclaimer  
- repository structure that a third party can understand  
- visible evolution in Git history  
  
### Demo readiness  
- a prepared scenario  
- a clear narrative  
- commands that match the implementation  
- outputs that can be shown and explained honestly  
  
---  
  
## Conclusion  
  
The roadmap for MemOps remains intentionally strict because that is the professional choice for a single-maintainer MVP.  
  
Phase 1 proved that the repository is executable.  
  
The next step is to prove that MemOps can move beyond inspection and deliver clear operational diagnosis.  
  
That is the path that best supports both the CUBO+ evaluation context and the long-term open-source value of the project.
