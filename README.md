# MemOps  
  
**Verification-first Bitcoin transaction inspection and initial why-stuck diagnosis CLI for mempool-compatible backends**  
  
MemOps is an open-source Python CLI being built toward verification-first Bitcoin incident response workflows.  
  
The current executable baseline now covers two narrow but real jobs:  
  
1. fetch a transaction by `txid` and inspect its raw hex locally, and  
2. provide an initial `why-stuck` diagnosis using normalized backend fee context plus local explicit opt-in RBF analysis.  
  
---  
  
## Why MemOps Exists  
  
Bitcoin explorers are useful for visibility, but visibility is not the same as operational response.  
  
When a transaction is stuck, operators need more than a status page. They need a workflow that helps them:  
  
- inspect the transaction directly,  
- verify important transaction fields locally when possible,  
- understand whether the transaction explicitly signals opt-in RBF,  
- compare the transaction fee position against current backend fee conditions,  
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
  
## Current Capabilities  
  
The current executable baseline can:  
  
- accept a Bitcoin `txid`,  
- fetch raw transaction hex from a mempool-compatible backend,  
- parse basic transaction structure locally,  
- report version, input count, output count, locktime, sequence values, and segwit detection,  
- detect explicit opt-in RBF signaling from input sequence values,  
- fetch normalized transaction summary data from the backend,  
- fetch normalized backend fee recommendations,  
- build fee-rate context from backend fee and weight data,  
- classify the transaction relative to current fee recommendation bands,  
- provide an initial `why-stuck` diagnosis and recommendation,  
- render a human-readable report,  
- render machine-readable JSON output,  
- write auditable why-stuck diagnosis artifacts to a deterministic export directory layout,
- and load runtime settings from environment variables or a local `.env` file.  
  
---  
  
## Current CLI Usage  
  
After syncing the project with `uv`, you can inspect a transaction with:  
  
```bash  
uv run memops <txid>  
```  
  
JSON inspection output is also available:  
  
```bash  
uv run memops --json <txid>  
```  
  
You can run the initial why-stuck diagnosis with:  
  
```bash  
uv run memops --why-stuck <txid>  
```  
  
And its JSON mode with:  
  
```bash  
uv run memops --why-stuck --json <txid>  
```  
  
You can also export diagnosis artifacts to the configured export directory:  
  
```bash  
uv run memops --why-stuck --export <txid>  
```  
  
You can override the export destination explicitly:  
  
```bash  
uv run memops --why-stuck --export-dir demo/output <txid>  
```  
  
And JSON mode can export while also surfacing artifact paths:  
  
```bash  
uv run memops --why-stuck --json --export <txid>  
```  
  
When export is enabled, MemOps writes:  
  
- `<export_dir>/<txid>/analysis.json`  
- `<export_dir>/<txid>/report.md`  
  
In text mode, the CLI appends an `Artifacts written:` section.  
In JSON mode, the output includes an `artifacts` object with the written paths.  
  
The module entrypoint works too:  
  
```bash  
uv run python -m memops <txid>  
uv run python -m memops --why-stuck <txid>  
```  
  
Help output:  
  
```bash  
uv run memops --help  
```  
  
A typical human-readable `why-stuck` report looks like:  
  
```text  
txid: <txid>  
confirmed: no  
fee_sats: 1200  
weight_wu: 400  
virtual_size_vbytes: 100  
fee_rate_sat_vb: 12.00  
market_position: below_hour  
target_fee_rate_sat_vb: 15  
fee_rate_shortfall_sat_vb: 3.00  
explicit_rbf: yes  
recommended_action: wait  
severity: warning  
reason: fee_below_priority_band  
summary: The transaction is paying below the faster confirmation bands.  
explanation: ...  
```  
  
The JSON modes are intentionally structured for scripting and review:  
  
- inspection JSON includes:  
  - `txid`  
  - `raw_hex`  
  - `parsed`  
  - `analysis`  
- why-stuck JSON adds:  
  - `summary`  
  - `fee_context`  
  - `diagnosis`  
- why-stuck JSON with export also adds:  
  - `artifacts`  
  
This keeps the current CLI useful both for direct terminal use and for shell-based workflows.  
  
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
    
  Base directory used by `--why-stuck --export` for diagnosis artifacts.  
  
The default backend example is `https://mempool.space`, but the project is intended to remain backend-configurable. 
  
---  
  
## What MemOps Is Not  
  
MemOps is **not**:  
  
- a wallet,  
- a broadcaster,  
- a block explorer replacement,  
- a custodial product,  
- a cloud-only service,  
- an officially affiliated mempool.space product,  
- or a full stuck-transaction rescue automation system.  
  
The current `why-stuck` mode is an **initial diagnosis layer**, not a complete replacement, CPFP, or incident-response engine.  
  
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
- `src/memops/diagnostics/` — fee-context classification and why-stuck policy  
- `src/memops/services/` — inspection and diagnosis workflow orchestration  
- `src/memops/cli.py` — command-line entrypoint  
- `tests/` — automated validation of parsing, policy, backend behavior, diagnosis logic, and CLI output  
  
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
  
MemOps now includes both an executable inspection baseline and an initial why-stuck diagnosis baseline.  
  
### Delivered today  
  
- settings model with `.env` support  
- mempool-compatible backend adapter  
- local raw transaction parsing  
- explicit RBF detection  
- transaction summary retrieval  
- fee recommendation retrieval  
- fee-context classification  
- end-to-end inspection workflow  
- end-to-end why-stuck diagnosis workflow  
- human-readable CLI output  
- JSON CLI output  
- `memops` console script  
- auditable why-stuck diagnosis artifact export 
  
### Next planned capabilities  
  
The next milestone after this diagnosis baseline is likely to include work such as:  
  
- richer fee-pressure context,  
- structured RBF planning,  
- export failure-path hardening,  
- and optional cleanup of unused runtime dependencies. 
  
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
