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
  
At this point, MemOps has already delivered both:  
  
- an executable inspection baseline, and  
- an initial why-stuck diagnosis baseline.  
  
The next milestone after this branch is to make those results more auditable and more operationally useful without losing clarity.  
  
---  
  
## 1. Current Development Context  
  
MemOps is no longer only a repository structure or architecture plan.  
  
The project now includes:  
  
- configuration loading from environment variables and `.env`,  
- a mempool-compatible backend adapter,  
- local raw transaction parsing,  
- explicit opt-in RBF detection,  
- transaction summary retrieval,  
- fee recommendation retrieval,  
- fee-context analysis,  
- an initial why-stuck diagnosis policy,  
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
The project established a real inspection pipeline:  
  
1. accept `txid`,  
2. fetch raw hex,  
3. parse locally,  
4. analyze locally,  
5. render reviewable output.  
  
That remains the base for everything that follows.  
  
---  
  
## 3. Phase 2 Delivered Diagnosis Baseline  
  
Phase 2 extends MemOps from inspection into an initial diagnosis workflow.  
  
### 3.1 Diagnosis data retrieval  
Delivered:  
  
- normalized backend transaction summary retrieval  
- normalized backend fee recommendation retrieval  
  
### 3.2 Fee-context reasoning  
Delivered:  
  
- fee-rate calculation from backend fee and weight data  
- virtual size derivation from transaction weight  
- fee-band classification against current recommendations  
- target fee-band selection  
- shortfall calculation versus the next band  
  
### 3.3 Why-stuck policy  
Delivered:  
  
- diagnosis categories for confirmed, low-fee, priority-gap, and competitive-fee cases  
- severity classification  
- recommended next actions such as:  
  - `none`  
  - `wait`  
  - `bump_fee_rbf`  
  - `consider_manual_cpfp`  
  
### 3.4 Executable CLI diagnosis mode  
Delivered:  
  
- `memops --why-stuck <txid>`  
- `memops --why-stuck --json <txid>`  
  
### 3.5 Phase 2 result  
The project now has a real diagnosis pipeline:  
  
1. accept `txid`,  
2. inspect raw transaction structure locally,  
3. retrieve backend fee context,  
4. classify current fee position,  
5. apply why-stuck policy,  
6. render a structured explanation and recommendation.  
  
This is an **initial diagnosis baseline**, not yet a full rescue workflow.  
  
---  
  
## 4. P0 — Next Core Milestone After `v0.2.0`  
  
The next priority is to make the current diagnosis baseline more auditable and more actionable without over-expanding the product.  
  
## 4.1 Auditable export artifacts  
  
The project should generate outputs that can be reviewed outside the terminal.  
  
Minimum desired exports:  
  
- `analysis.json`  
- `report.md`  
  
### Success condition  
The tool leaves behind artifacts that are useful for review, demos, and later incident documentation.  
  
---  
  
## 4.2 Richer fee-pressure context  
  
After the current fee recommendation baseline, MemOps should retrieve and normalize richer fee-market context such as:  
  
- mempool block or fee-pressure data,  
- additional recommendation context,  
- and other backend data that helps explain transaction position more clearly.  
  
### Success condition  
The CLI can explain transaction position with more context than a single recommendation snapshot.  
  
---  
  
## 4.3 Demo and artifact readiness  
  
The project should include at least one reproducible case that shows:  
  
- inspection output,  
- why-stuck output,  
- and saved artifacts once exports are implemented.  
  
### Success condition  
The demo remains repeatable and not dependent on improvisation.  
  
---  
  
## 5. P0.5 — Strongly Desired After Exports  
  
## 5.1 `plan-rbf`  
  
After the current why-stuck baseline, the most important extension is structured RBF planning.  
  
It should eventually:  
  
- confirm whether replacement is plausible,  
- estimate target fee conditions,  
- calculate fee delta,  
- and produce an auditable plan.  
  
### Rule  
Do not pursue this if it weakens the current why-stuck quality or export discipline.  
  
---  
  
## 6. P1 — Strong Differentiators  
  
Only attempt these after the diagnosis baseline and exports are stable.  
  
### 6.1 `plan-cpfp`  
Potentially useful, but more complex.  
  
It may require:  
  
- ownership assumptions,  
- package reasoning,  
- and child fee estimation.  
  
### 6.2 `watch-tx` or `watch-mempool`  
A monitoring mode could later improve operational usefulness.  
  
### 6.3 `triage-batch`  
Batch handling for multiple transactions may become useful later, but it is clearly secondary to the core single-transaction flow.  
  
---  
  
## 7. P2 — Post-Evaluation Extensions  
  
Possible future work:  
  
- SQLite persistence  
- deeper Bitcoin Core validation  
- broader transaction-type support  
- more advanced package analysis  
- richer report generation  
- stronger release workflows  
  
These should only be pursued after the current MVP becomes a stronger and more auditable diagnostic tool.  
  
---  
  
## 8. What Gets Cut First If Time Becomes Tight  
  
To protect quality, these items should be cut before the core is weakened:  
  
- CPFP planning  
- live monitoring  
- batch triage  
- persistence  
- cloud extras  
- non-essential integrations  
  
The following should **not** be cut or regressed:  
  
- backend configurability  
- local transaction inspection  
- explicit RBF analysis  
- why-stuck diagnosis mode  
- honest documentation  
- automated tests  
- demo readiness  
  
---  
  
## 9. Definition of Done for `v0.2.0`  
  
MemOps should be considered ready for the `v0.2.0` milestone if it can demonstrate the following:  
  
### Technical  
- inspect a real transaction from a `txid`  
- retrieve and inspect raw hex  
- compute and present key transaction metadata locally  
- detect explicit opt-in RBF signaling  
- retrieve normalized transaction summary data  
- retrieve normalized fee recommendations  
- explain likely why a transaction is stuck  
- produce a clear recommendation  
- emit both human-readable and JSON outputs  
  
### Documentation  
- clear root README  
- technical README in `src/`  
- roadmap aligned with the actual repository state  
- reproducible demo script  
- assumptions aligned with current implementation  
  
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
Phase 2 proved that MemOps can move beyond inspection into an initial diagnosis layer.  
  
The next step is not to over-expand the tool. The next step is to make the current diagnosis baseline more auditable, more reusable, and more operationally useful.  
  
That path best supports both the CUBO+ evaluation context and the long-term open-source value of the project.
