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

MemOps currently provides a thin but real transaction-inspection and diagnosis baseline. It can:

- inspect raw Bitcoin transaction data through a mempool-compatible backend,
- parse raw transactions locally,
- analyze explicit RBF signaling from transaction input sequences,
- render human-readable or JSON inspection output,
- run a first-pass why-stuck diagnosis from transaction summary data plus fee recommendations,
- write auditable diagnosis artifacts to a deterministic export directory layout,
- surface written artifact paths in both text and JSON why-stuck output,
- fail export attempts explicitly with a non-zero CLI result and a user-facing error,
- and keep non-export inspection flows independent from export configuration.

This means the project already demonstrates a real local reasoning layer on top of external backend data rather than acting as a simple API passthrough.

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
uv run memops --why-stuck --json <txid>
```

You can export diagnosis artifacts with the configured export directory:

```bash
uv run memops --why-stuck --export <txid>
```

You can override the export destination explicitly; `--export-dir` also enables export:

```bash
uv run memops --why-stuck --export-dir demo/output <txid>
uv run memops --why-stuck --json --export-dir /tmp/memops-export <txid>
```

When export succeeds, MemOps writes:

- `<export_dir>/<txid>/analysis.json`
- `<export_dir>/<txid>/report.md`

CLI behavior to remember:

- `--export` uses `MEMOPS_EXPORT_DIR`,
- `--export-dir PATH` opts into export and overrides the base directory for that invocation,
- `--export` and `--export-dir` both require `--why-stuck`,
- text mode prints an `Artifacts written:` section on success,
- JSON mode adds an `artifacts` object on success,
- export failures are reported on `stderr` and return a non-zero exit code,
- and non-export inspection commands do not depend on export configuration.

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

`MEMOPS_EXPORT_DIR` is only consulted when export is requested through `--export`.
`--export-dir` overrides it per command.
Non-export commands do not require export configuration.

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

This repository now delivers a working baseline for:

- backend-backed transaction inspection,
- local explicit-RBF analysis,
- initial why-stuck diagnosis,
- deterministic diagnosis artifact export,
- surfaced artifact paths in text and JSON output,
- automated coverage for export success and failure paths,
- and documentation/demo alignment with the shipped CLI behavior.

Delivered today:

- transaction inspection via a configurable mempool-compatible backend
- local raw transaction parsing
- explicit RBF signaling analysis
- first-pass why-stuck diagnosis
- auditable why-stuck diagnosis artifact export
- test coverage for export workflows and failure paths

Next planned capabilities:

- richer fee-pressure context,
- structured RBF planning,
- CPFP / package-relay-aware guidance,
- and later response workflows and operational polish.

That scope is intentionally narrow. The current milestone is about proving a reliable analysis baseline before expanding into more opinionated transaction-response workflows.

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
