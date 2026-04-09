# MemOps MVP Assumptions and Limits  
  
## Purpose  
  
This document records the main assumptions and current limits of the MemOps MVP.  
  
The goal is to be explicit about what the project is designed to do, what it is not designed to do, and where certain results still depend on backend data rather than independent local verification.  
  
This is especially important for a verification-first project. Honest assumptions improve credibility.  
  
---  
  
## 1. Project Stage  
  
MemOps is currently an **early executable MVP**.  
  
That means the repository already demonstrates:  
  
- a working inspection CLI,  
- a working why-stuck diagnosis mode,  
- a clear technical direction,  
- and a disciplined open-source foundation.  
  
It does **not** mean the project already supports every possible Bitcoin transaction workflow.  
  
---  
  
## 2. Core Scope Assumption  
  
The current scope is intentionally narrow:  
  
> inspect a Bitcoin transaction directly and provide an initial why-stuck diagnosis.  
  
Today that means MemOps can:  
  
- inspect raw transaction structure locally,  
- detect explicit opt-in RBF signaling locally,  
- compare a transaction against current backend fee recommendations,  
- and produce a reviewable recommendation such as waiting or considering a fee bump path.  
  
It does **not** yet mean full stuck-transaction rescue planning.  
  
---  
  
## 3. Backend Assumption  
  
MemOps assumes access to a **mempool-compatible backend**.  
  
The project is designed to support:  
  
- the public mempool.space instance as a default example,  
- and self-hosted mempool-compatible backends through configuration.  
  
However, the exact behavior or schema of every deployment should not be assumed blindly. Compatibility must be validated against the target backend used in testing or demo.  
  
---  
  
## 4. Local Verification Assumption  
  
MemOps is built around the principle of local verification where feasible.  
  
At the current stage, MemOps reasons locally about:  
  
- raw transaction structure,  
- input and output counts,  
- sequence values,  
- segwit detection,  
- and explicit opt-in RBF signaling.  
  
However, the current why-stuck mode also depends on normalized backend data for:  
  
- transaction fee summary fields,  
- transaction weight,  
- confirmation status,  
- and current fee recommendation bands.  
  
The correct stance is not “local verification of everything no matter what.” The correct stance is:  
  
> **make local verification the default where possible, and make dependencies explicit where not.**  
  
---  
  
## 5. Fee Calculation Assumption  
  
The current why-stuck implementation computes fee-rate context from **backend-provided fee and weight data**.  
  
That means the project can currently derive:  
  
- virtual size from backend weight,  
- fee rate in sat/vB,  
- fee-band position relative to current recommendations,  
- and a target recommendation band.  
  
What it does **not** currently do is independently recompute the transaction fee from prevout values. That would require additional prevout data retrieval or optional node-based validation.  
  
The project should therefore avoid pretending that current fee-rate context is fully self-verified from raw transaction bytes alone.  
  
---  
  
## 6. Transaction-Type Assumption  
  
The current parser is intentionally narrow and extracts minimal metadata needed for inspection and replaceability reasoning.  
  
The MVP is expected to work best for common transaction patterns and well-understood structures. It does not assume full support from day one for every advanced or unusual script scenario.  
  
The product direction still favors:  
  
- a strong core flow,  
- clear assumptions,  
- and incremental expansion later.  
  
---  
  
## 7. Replaceability Assumption  
  
MemOps assumes that explicit opt-in RBF detection can be approached by inspecting sequence-related signals in the transaction inputs.  
  
This is useful as a practical operational indicator, and the current implementation derives it locally from raw transaction data.  
  
However, the project should still document the difference between:  
  
- local explicit-RBF signal detection,  
- policy-related interpretation,  
- and actual network acceptance behavior in a live environment.  
  
In other words, replacement reasoning should be presented carefully and not as magical certainty.  
  
---  
  
## 8. CPFP and Ownership Assumption  
  
If CPFP planning is explored later, the project will need some way to reason about output ownership.  
  
The MVP assumes that ownership cannot be guessed safely without explicit context.  
  
A later CPFP flow would therefore likely depend on one of the following:  
  
- a wallet snapshot,  
- explicit user input,  
- or controlled demo data.  
  
This is one reason CPFP remains secondary to the current inspection and why-stuck flow.  
  
---  
  
## 9. Safety Assumption  
  
MemOps assumes that analysis and planning should be separated from irreversible actions.  
  
The MVP is therefore not intended to:  
  
- auto-sign transactions,  
- auto-broadcast by default,  
- or act as a custodial system.  
  
This is an intentional design choice.  
  
---  
  
## 10. Infrastructure Assumption  
  
The project should remain runnable without mandatory cloud infrastructure or hidden services.  
  
Optional integrations may exist later, but the repository should stay understandable and portable without that dependency.  
  
This matters for both open-source reuse and CUBO+ evaluation.  
  
---  
  
## 11. Demo Assumption  
  
The demo should use a controlled and explainable case.  
  
That may include:  
  
- a real transaction used only for analysis,  
- a historical example,  
- or a clearly documented prepared scenario.  
  
The demonstration should not depend on improvisation or unexplained external conditions.  
  
---  
  
## 12. Honest Boundary of the MVP  
  
The MemOps MVP does **not** claim to:  
  
- eliminate mempool congestion,  
- guarantee confirmation,  
- replace a wallet,  
- replace a full node,  
- independently verify every fee-related field,  
- automatically generate a final RBF transaction,  
- automatically plan CPFP,  
- or automate production operations safely.  
  
Its value is narrower and more realistic:  
  
- inspect a transaction locally where feasible,  
- explain likely fee-related confirmation issues,  
- structure why-stuck reasoning more clearly,  
- support auditable outputs,  
- and promote a healthier verification model.  
  
---  
  
## Conclusion  
  
MemOps becomes more credible when its assumptions are written down clearly.  
  
The project is strongest when it says:  
  
- what it verifies locally,  
- what it normalizes from backend data,  
- what it infers,  
- what it still depends on,  
- and what it intentionally does not do.  
  
That is fully consistent with the philosophy of the repository:  
  
**Don’t trust, verify — and when verification has limits, document them honestly.**
