# MemOps  
  
**Verification-first Bitcoin incident response CLI for mempool-compatible backends**  
  
MemOps is an open-source Python CLI designed to help operators analyze stuck Bitcoin transactions, reason about fee pressure, and prepare auditable next steps.  
  
The project is being built as a focused MVP for the **CUBO+ evaluation stage** and is intended to continue as an open-source project afterward.  
  
---  
  
## Why MemOps Exists  
  
Bitcoin explorers are useful for visibility, but visibility is not the same as operational response.  
  
When a transaction is stuck, operators need more than a status page. They need a workflow that helps them:  
  
- inspect the transaction more directly,  
- verify critical details locally when possible,  
- understand why it is likely not confirming,  
- and document the reasoning behind the next action.  
  
MemOps is built for that purpose.  
  
---  
  
## Design Principles  
  
- **Don’t trust, verify**  
- **Open-source by default**  
- **Mempool-compatible, not single-endpoint locked**  
- **Small scope, high clarity**  
- **Auditability over automation theater**  
  
---  
  
## Target MVP Scope  
  
The target MVP of MemOps focuses on:  
  
- transaction analysis from a `txid`  
- retrieval of transaction data from a mempool-compatible backend  
- local parsing and validation of key transaction properties  
- explanation of why a transaction is likely stuck  
- auditable exports such as JSON and Markdown reports  
  
Planned core commands include:  
  
- `analyze-tx`  
- `why-stuck`  
- `plan-rbf`  
  
---  
  
## What MemOps Is Not  
  
MemOps is **not**:  
  
- a wallet  
- a block explorer  
- a custodial product  
- a retail app  
- a cloud-only service  
- an officially affiliated mempool.space product  
  
---  
  
## Backend Compatibility  
  
MemOps is designed to work with:  
  
- the public `mempool.space` endpoint as a default example  
- self-hosted **mempool-compatible** backends via configuration  
  
This matters because the project is intended to support stronger operational sovereignty rather than dependence on one public interface.  
  
---  
  
## Project Status  
  
MemOps is currently in an **early MVP stage**.  
  
At this point, the repository is focused on:  
  
- project structure  
- technical and strategy documentation  
- backend integration planning  
- core CLI implementation  
  
The project is currently maintained by a **single developer**, so scope is intentionally controlled.  
  
---  
  
## Repository Structure  
  
```text  
.  
├── README.md  
├── LICENSE  
├── Makefile  
├── pyproject.toml  
├── src/  
│   ├── README.md  
│   └── memops/  
├── strategy/  
├── docs/  
├── demo/  
└── tests/  
```  
  
---  
  
## Development Setup  
  
This project uses Python 3.12 and `uv`.  
  
Example setup:  
  
```bash  
uv python install 3.12  
uv sync --python 3.12 --group dev  
```  
  
Basic checks:  
  
```bash  
make lint  
make test  
```  
  
---  
  
## CUBO+ Context  
  
MemOps was initially developed in the context of the CUBO+ evaluation path, where projects are assessed on:  
  
- technical execution  
- visible development progress  
- documentation quality  
- and real-world relevance for the Bitcoin ecosystem in El Salvador  
  
The long-term goal is to leave the project in a state that is useful beyond the evaluation itself.  
  
---  
  
## Non-Affiliation Notice  
  
MemOps is an independent project.  
  
It is **not officially affiliated with mempool.space**. Any compatibility with mempool-compatible backends is intended as technical interoperability, not branding appropriation.  
  
---  
  
## Documentation  
  
Key project documents include:  
  
- `strategy/problem.md`  
- `strategy/impact-analysis.md`  
- `strategy/operating-model.md`  
- `strategy/business-model.md`  
- `strategy/roadmap.md`  
- `strategy/pitch-script.md`  
  
Technical documentation should live in the `docs/` directory.  
  
---  
  
## License  
  
This project is released under the **MIT License**.
