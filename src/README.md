# Technical README  
  
This directory contains the Python implementation of MemOps.  
  
## Purpose  
  
MemOps is a verification-first CLI for analyzing stuck Bitcoin transactions through mempool-compatible backends.  
  
The technical implementation is intended to stay modular and easy to review.  
  
## Planned Source Layout  
  
- `memops/cli.py`    
  CLI entrypoint and command orchestration  
  
- `memops/adapters/`    
  External integrations such as mempool-compatible REST clients and optional Bitcoin Core RPC clients  
  
- `memops/domain/`    
  Typed models for transactions, analysis results, fee data, and reports  
  
- `memops/services/`    
  Core business logic such as parsing, fee-rate calculations, replaceability checks, and recommendation logic  
  
## Technical Principles  
  
- Keep the CLI thin  
- Keep logic in testable functions  
- Prefer explicit assumptions over hidden magic  
- Treat external APIs as data sources, not as unquestionable truth  
- Keep exports auditable and readable  
  
## Current Status  
  
At the current stage, MemOps is in active MVP development.  
  
The immediate technical priorities are:  
  
1. backend adapter  
2. transaction analysis  
3. stuck-transaction explanation  
4. export artifacts  
5. tests  
  
## Notes  
  
This codebase is intentionally scoped for a single-maintainer MVP and aims for clarity over unnecessary complexity.
