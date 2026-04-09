# Technical README  
  
This directory contains the Python implementation of MemOps.  
  
## Purpose  
  
MemOps is being built as a verification-first CLI for Bitcoin transaction analysis through mempool-compatible backends.  
  
The current executable baseline focuses on transaction inspection, not yet full stuck-transaction diagnosis. The implemented flow is:  
  
1. accept a `txid`,  
2. fetch raw transaction hex from a backend,  
3. parse the transaction locally,  
4. analyze explicit opt-in RBF signaling,  
5. and render the result as text or JSON.  
  
---  
  
## Current Source Layout  
  
### `memops/__main__.py`  
Module entrypoint for:  
  
```bash  
python -m memops  
```  
  
### `memops/cli.py`  
Argparse-based CLI entrypoint and output formatting.  
  
Current responsibilities:  
  
- parse command-line arguments,  
- choose report or JSON output,  
- initialize the configured backend,  
- and surface user-facing errors clearly.  
  
### `memops/config.py`  
Runtime configuration loaded through `pydantic-settings`.  
  
Current responsibilities:  
  
- load `MEMOPS_*` settings,  
- support local `.env` files,  
- normalize backend configuration,  
- and expose cached settings.  
  
### `memops/backends/`  
Backend contracts and concrete retrieval logic.  
  
Current modules:  
  
- `contracts.py`    
  Protocols, value objects, and normalization helpers.  
- `mempool.py`    
  Mempool-compatible backend implementation for raw transaction retrieval.  
  
### `memops/services/`  
Core logic for local inspection.  
  
Current modules:  
  
- `policy.py`    
  Pure helpers for explicit opt-in RBF detection.  
- `tx_parser.py`    
  Raw transaction parsing helpers.  
- `analysis.py`    
  Parsed-transaction analysis logic.  
- `inspection.py`    
  End-to-end workflow: fetch, parse, and analyze.  
  
### `memops/domain/`  
Reserved for broader domain models as the project grows.  
  
### `memops/adapters/`  
Reserved for future external integrations beyond the current backend module structure.  
  
---  
  
## Current Execution Flow  
  
The current CLI path is intentionally simple:  
  
1. the user provides a `txid`,  
2. the CLI resolves settings and backend configuration,  
3. the backend fetches `/api/tx/{txid}/hex`,  
4. the raw transaction is parsed locally,  
5. explicit RBF signaling is derived from sequence values,  
6. the result is rendered as text or JSON.  
  
This is important because the project already does more than print a backend response. It retrieves data externally, but the inspection logic happens locally.  
  
---  
  
## Technical Principles  
  
- Keep the CLI thin.  
- Keep policy and parsing logic testable.  
- Prefer explicit assumptions over hidden behavior.  
- Treat external backends as data sources, not unquestionable truth.  
- Keep outputs auditable and easy to inspect.  
  
---  
  
## Current Status  
  
Implemented today:  
  
- backend configuration via settings  
- `.env` support  
- mempool-compatible transaction retrieval  
- local raw transaction parsing  
- explicit RBF detection  
- end-to-end inspection service  
- CLI text output  
- CLI JSON output  
- console-script entrypoint  
  
Next technical priorities:  
  
1. fee-context retrieval  
2. `why-stuck` reasoning  
3. export artifacts  
4. structured RBF planning  
  
The codebase is intentionally scoped for a single-maintainer MVP and aims for clarity over unnecessary complexity.
