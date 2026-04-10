# Assumptions

## Product boundary

MemOps is currently an analysis-first CLI for stuck Bitcoin transactions. The current milestone assumes the tool helps an operator inspect and explain a transaction, but does not yet take corrective action on the network.

## Backend assumptions

- MemOps talks to a mempool-compatible HTTP backend.  
- The backend is expected to provide transaction lookup, transaction summary data, and fee recommendation endpoints.  
- Transaction summary fee and size fields may arrive with different levels of completeness, so MemOps normalizes them into fee evidence before why-stuck reasoning.  
- Backend responses may fail or be unavailable, and those failures should remain user-visible.  
- Local reasoning in MemOps should remain possible even though data retrieval is external.  

## Export assumptions

- Export is only supported in `--why-stuck` mode.
- `--export` uses `MEMOPS_EXPORT_DIR` as the base directory.
- `--export-dir PATH` both enables export and overrides the base directory for a single invocation.
- Successful exports write to a deterministic layout:  
  - `<base_dir>/<txid>/analysis.json`  
  - `<base_dir>/<txid>/report.md`  
- Exported `analysis.json` may expose normalized `summary.fee_evidence` metadata for auditability.  
- Export currently targets the local filesystem only.  
- Export failures should be explicit, user-facing, and return a non-zero CLI exit code.
- The current milestone does not assume atomic multi-file writes, artifact versioning, or remote artifact storage.

## Diagnosis assumptions

- The why-stuck diagnosis is an initial heuristic layer, not final policy truth.  
- Current recommendations are based on normalized transaction fee evidence, fee recommendations, and explicit RBF signaling.  
- Normalized fee evidence currently distinguishes `exact` evidence from `incomplete` evidence.  
- The current fee-context workflow only proceeds when fee evidence is exact enough to derive an effective fee rate; incomplete evidence should fail explicitly instead of guessing.  
- Structured why-stuck JSON and exported analysis JSON may expose `summary.fee_evidence` for auditability.  
- Fee-pressure interpretation is intentionally simple in the current baseline and should deepen in later milestones.  

## Non-goals for the current baseline

- wallet integration
- automatic fee bumping
- transaction signing
- automatic rebroadcasting
- CPFP execution
- long-running daemon behavior

## Demo and testing assumptions

- Demo flows should use known-good txids and real shipped commands.
- Export success should be demonstrated directly; export failure behavior can be described verbally unless a prepared example exists.
- Automated tests should remain deterministic, local, and fast.
