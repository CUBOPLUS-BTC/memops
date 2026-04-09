# MemOps  
  
**Verification-first Bitcoin transaction inspection CLI for mempool-compatible backends**  
  
MemOps is an open-source Python CLI being built toward verification-first Bitcoin incident response workflows.  
  
The current executable MVP focuses on one narrow job: fetch a transaction by `txid`, inspect its raw hex locally, and report explicit opt-in RBF signaling in a reviewable way.  
  
---  
  
## Why MemOps Exists  
  
Bitcoin explorers are useful for visibility, but visibility is not the same as operational response.  
  
When a transaction is stuck, operators need more than a status page. They need a workflow that helps them:  
  
- inspect the transaction directly,  
- verify critical details locally when possible,  
- understand whether the transaction explicitly signals opt-in RBF,  
- and produce outputs that are easy to review or script against.  
  
MemOps is being built for that purpose.  
  
---  
  
## Design Principles  
  
- **Don’t trust, verify**  
- **Open-source by default**  
- **Mempool-compatible, not single-endpoint locked**  
- **Small scope, high clarity**  
- **Auditability over automation theater**  
  
---  
  
## Current MVP Capabilities  
  
The current executable baseline can:  
  
- accept a Bitcoin `txid`,  
- fetch raw transaction hex from a mempool-compatible backend,  
- parse basic transaction structure locally,  
- report version, input count, output count, locktime, sequence values, and segwit detection,  
- detect explicit opt-in RBF signaling from input sequence values,  
- render a human-readable report,  
- render a machine-readable JSON payload,  
- and load runtime settings from environment variables or a local `.env` file.  
  
---  
  
## Current CLI Usage  
  
After syncing the project with `uv`, you can inspect a transaction with:  
  
```bash  
uv run memops <txid>  
```  
  
JSON output is also available:  
  
```bash  
uv run memops --json <txid>  
```  
  
The module entrypoint works too:  
  
```bash  
uv run python -m memops <txid>  
```  
  
Help output:  
  
```bash  
uv run memops --help  
```  
  
Typical human-readable output looks like:  
  
```text  
txid: <txid>  
version: 2  
inputs: 1  
outputs: 2  
locktime: 0  
segwit: yes  
explicit_rbf: yes  
signaling_inputs: 0  
```  
  
The JSON mode includes:  
  
- `txid`  
- `raw_hex`  
- `parsed`  
- `analysis`  
  
This makes the current CLI useful both for direct inspection and for shell scripting.  
  
---  
  
## Configuration  
  
MemOps reads settings from environment variables and from a local `.env` file by default.  
  
You can start from the example file:  
  
```bash  
cp .env.example .env  
```  
  
Example:  
  
```dotenv  
MEMOPS_BACKEND_URL=https://mempool.space  
MEMOPS_NETWORK=mainnet  
MEMOPS_EXPORT_DIR=./demo/output  
```  
  
Current settings:  
  
- `MEMOPS_BACKEND_URL`    
  Base URL for a mempool-compatible backend.  
  
- `MEMOPS_NETWORK`    
  Supported values: `mainnet`, `testnet`, `signet`, `regtest`.  
  
- `MEMOPS_EXPORT_DIR`    
  Reserved for upcoming export workflows.  
  
The default backend example is `https://mempool.space`, but the project is intended to remain backend-configurable.  
  
---  
  
## What MemOps Is Not  
  
MemOps is **not**:  
  
- a wallet,  
- a broadcaster,  
- a block explorer replacement,  
- a custodial product,  
- a cloud-only service,  
- or an officially affiliated mempool.space product.  
  
The goal is to add a verification-first reasoning layer, not to hide irreversible actions behind a simple interface.  
  
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
├── docs/  
├── strategy/  
├── demo/  
└── tests/  
```  
  
Key implementation areas:  
  
- `src/memops/backends/` — backend contracts and mempool-compatible retrieval  
- `src/memops/services/` — parsing, analysis, and inspection workflow  
- `src/memops/cli.py` — command-line entrypoint  
- `tests/` — automated validation of policy, parsing, backend behavior, configuration, and CLI output  
  
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
uv run ruff format .  
uv run ruff check .  
uv run pytest -q  
```  
  
CLI smoke test:  
  
```bash  
uv run memops --help  
```  
  
---  
  
## Project Status  
  
MemOps now has an executable MVP baseline.  
  
### Delivered baseline  
  
- settings model with `.env` support  
- mempool-compatible backend adapter  
- local raw transaction parsing  
- explicit RBF detection  
- end-to-end inspection workflow  
- human-readable CLI output  
- JSON CLI output  
- `memops` console script  
  
### Next planned capabilities  
  
The next milestone is to move from **inspection** to **diagnosis**, including work such as:  
  
- fee-pressure context,  
- `why-stuck` reasoning,  
- auditable export artifacts,  
- and structured RBF planning.  
  
The project is still intentionally scoped as a focused single-maintainer MVP.  
  
---  
  
## CUBO+ Context  
  
MemOps was initially developed in the context of the CUBO+ evaluation path, where projects are assessed on:  
  
- technical execution,  
- visible development progress,  
- documentation quality,  
- and real-world relevance for the Bitcoin ecosystem in El Salvador.  
  
The long-term goal is to leave the project in a state that remains useful beyond the evaluation itself.  
  
---  
  
## Non-Affiliation Notice  
  
MemOps is an independent project.  
  
It is **not officially affiliated with mempool.space**. Any compatibility with mempool-compatible backends is intended as technical interoperability, not branding appropriation.  
  
---  
  
## Documentation  
  
Key project documents include:  
  
- `docs/architecture.md`  
- `docs/assumptions.md`  
- `docs/demo-script.md`  
- `strategy/problem.md`  
- `strategy/impact-analysis.md`  
- `strategy/operating-model.md`  
- `strategy/business-model.md`  
- `strategy/roadmap.md`  
- `strategy/pitch-script.md`  
  
---  
  
## License  
  
This project is released under the **MIT License**.
