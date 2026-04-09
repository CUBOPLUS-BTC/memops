# Technical README  
  
This directory contains the Python implementation of MemOps.  
  
## Purpose  
  
MemOps is being built as a verification-first CLI for Bitcoin transaction inspection and initial stuck-transaction diagnosis through mempool-compatible backends.  
  
The current executable baseline supports two closely related flows:  
  
1. **inspection**  
   - accept a `txid`,  
   - fetch raw transaction hex from a backend,  
   - parse the transaction locally,  
   - analyze explicit opt-in RBF signaling,  
   - render text or JSON output.  
  
2. **why-stuck diagnosis**  
   - inspect the transaction locally,  
   - fetch normalized backend transaction summary data,  
   - fetch normalized backend fee recommendations,  
   - build fee context,  
   - apply local why-stuck policy,  
   - render text or JSON output.  
  
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
- choose inspection mode or `--why-stuck` mode,  
- choose text or JSON output,  
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
  Mempool-compatible backend implementation for:  
  - raw transaction hex retrieval,  
  - transaction summary retrieval,  
  - fee recommendation retrieval.  
  
### `memops/diagnostics/`  
Pure diagnosis logic that does not own CLI or transport concerns.  
  
Current modules:  
  
- `fee_context.py`    
  Fee-rate calculation, fee-band classification, and target band selection.  
- `policy.py`    
  Why-stuck policy derived from fee context plus explicit-RBF signaling.  
  
### `memops/services/`  
Core orchestration logic.  
  
Current modules:  
  
- `policy.py`    
  Pure helpers for explicit opt-in RBF detection.  
- `tx_parser.py`    
  Raw transaction parsing helpers.  
- `analysis.py`    
  Parsed-transaction analysis logic.  
- `inspection.py`    
  End-to-end workflow: fetch, parse, and analyze.  
- `diagnosis.py`    
  End-to-end workflow: inspect locally, retrieve fee context, and produce a why-stuck diagnosis.  
  
### `memops/domain/`  
Reserved for broader domain models as the project grows.  
  
### `memops/adapters/`  
Reserved for future external integrations beyond the current backend module structure.  
  
---  
  
## Current Execution Flow  
  
The current CLI path is intentionally simple.  
  
### Inspection mode  
  
1. the user provides a `txid`,  
2. the CLI resolves settings and backend configuration,  
3. the backend fetches `/api/tx/{txid}/hex`,  
4. the raw transaction is parsed locally,  
5. explicit RBF signaling is derived from sequence values,  
6. the result is rendered as text or JSON.  
  
### Why-stuck mode  
  
1. the user provides a `txid` and `--why-stuck`,  
2. the CLI resolves settings and backend configuration,  
3. the inspection workflow fetches raw hex and analyzes explicit RBF locally,  
4. the backend fetches `/api/tx/{txid}`,  
5. the backend fetches `/api/v1/fees/recommended`,  
6. the service builds fee context from normalized backend data,  
7. local why-stuck policy produces a diagnosis and recommendation,  
8. the result is rendered as text or JSON.  
  
This matters because MemOps still does more than print backend responses. It retrieves data externally, but important reasoning remains in local services.  
  
---  
  
## Technical Principles  
  
- Keep the CLI thin.  
- Keep policy, parsing, and fee-context logic testable.  
- Prefer explicit assumptions over hidden behavior.  
- Treat external backends as data sources, not unquestionable truth.  
- Keep outputs auditable and easy to inspect.  
  
---  
  
## Current Status  
  
Implemented today:  
  
- backend configuration via settings  
- `.env` support  
- mempool-compatible transaction retrieval  
- mempool-compatible transaction summary retrieval  
- mempool-compatible fee recommendation retrieval  
- local raw transaction parsing  
- explicit RBF detection  
- fee-context classification  
- why-stuck diagnosis policy  
- end-to-end inspection service  
- end-to-end diagnosis service  
- CLI text output  
- CLI JSON output  
- console-script entrypoint  
  
Next technical priorities:  
  
1. auditable export artifacts  
2. richer fee-pressure context  
3. structured RBF planning  
4. optional dependency cleanup  
  
The codebase is intentionally scoped for a single-maintainer MVP and aims for clarity over unnecessary complexity.
