# MemOps MVP Assumptions and Limits  
  
## Purpose  
  
This document records the main assumptions and current limits of the MemOps MVP.  
  
The goal is to be explicit about what the project is designed to do, what it is not designed to do, and where certain results may still depend on backend data or future implementation work.  
  
This is especially important for a verification-first project. Honest assumptions improve credibility.  
  
---  
  
## 1. Project Stage  
  
MemOps is currently an **early MVP**.  
  
That means the repository is being prepared to demonstrate:  
  
- a clear product concept,  
- a structured technical direction,  
- and a disciplined open-source foundation.  
  
It does **not** mean the project already supports every possible Bitcoin transaction workflow.  
  
---  
  
## 2. Core Scope Assumption  
  
The MVP is focused on a narrow operational problem:  
  
> analyzing a stuck Bitcoin transaction and helping explain what to do next.  
  
The initial priority is not broad feature coverage. It is correctness and clarity around the core user story.  
  
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
  
The MVP assumes that it should attempt to inspect or derive key properties locally from transaction data, especially from `raw hex`, rather than relying only on summarized explorer fields.  
  
That said, not every piece of information is equally self-contained.  
  
### Examples of what the project aims to reason about locally  
- transaction structure,  
- input and output layout,  
- size-related metrics,  
- sequence values,  
- replaceability signals.  
  
### Examples of values that may still depend on external context  
- some fee calculations that require prevout values,  
- current fee pressure context,  
- confirmation status,  
- and network conditions.  
  
The correct stance is not “local verification of everything no matter what.” The correct stance is:  
  
> **make local verification the default where possible, and make dependencies explicit where not.**  
  
---  
  
## 5. Fee Calculation Assumption  
  
The MVP assumes that a meaningful transaction analysis should include fee reasoning.  
  
However, exact fee calculation may require information about the values of spent outputs. If those values are not fully derivable from the raw transaction alone, the project may rely on backend-provided transaction context or optional node-based validation.  
  
This should always be documented clearly in the output or implementation notes.  
  
The project should avoid pretending that a value was independently verified if it still depended on external data.  
  
---  
  
## 6. Transaction-Type Assumption  
  
The MVP is expected to work best for common transaction patterns and well-understood transaction structures.  
  
It does not assume full support from day one for every advanced or unusual script scenario.  
  
The current product direction favors:  
  
- a strong core flow,  
- clear assumptions,  
- and incremental expansion later.  
  
---  
  
## 7. Replaceability Assumption  
  
MemOps assumes that opt-in RBF detection can be approached by inspecting sequence-related signals in the transaction inputs.  
  
This is useful as a practical operational indicator.  
  
However, the project should still document the difference between:  
  
- policy-related interpretation,  
- local signal detection,  
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
  
This is one reason CPFP is secondary to the core `analyze-tx` and `why-stuck` flow.  
  
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
  
Optional integrations may exist later, but the repository should stay understandable and portable without them.  
  
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
- or automate production operations safely.  
  
Its value is narrower and more realistic:  
  
- explain a stuck transaction better,  
- structure reasoning more clearly,  
- support auditable outputs,  
- and promote a healthier verification model.  
  
---  
  
## Conclusion  
  
MemOps becomes more credible when its assumptions are written down clearly.  
  
The project is strongest when it says:  
  
- what it verifies,  
- what it infers,  
- what it still depends on,  
- and what it intentionally does not do.  
  
That is fully consistent with the philosophy of the repository:  
  
**Don’t trust, verify — and when verification has limits, document them honestly.**
