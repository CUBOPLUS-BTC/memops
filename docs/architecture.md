# MemOps Architecture Overview

## Purpose

MemOps is designed as a verification-first Bitcoin incident response CLI for mempool-compatible backends.

Its purpose is not to replace a block explorer and not to act as a wallet. Instead, it aims to help operators move from passive transaction visibility to clearer operational reasoning when a transaction appears stuck.

This document describes the intended high-level architecture of the project.

---

## Design Goals

The architecture of MemOps is guided by the following goals:

- keep the tool small and understandable,
- separate external data access from internal reasoning,
- make important logic testable,
- support mempool-compatible backends rather than a single public endpoint,
- and keep outputs auditable.

These goals are especially important because the project is currently a single-maintainer MVP. A simple and disciplined structure is easier to maintain and easier for others to review later.

---

## Trust Model

MemOps follows a simple trust model:

> **External backends are data sources, not the final source of truth for reasoning.**

This means the project may use a backend to retrieve:

- transaction summaries,
- raw transaction hex,
- fee market data,
- and other contextual information,

but the project should still perform local interpretation and verification where possible.

The architectural implication is important:

- backend adapters gather data,
- services reason about the data,
- and the CLI presents the result.

This keeps the logic transparent.

---

## High-Level Components

The planned architecture is divided into four main layers.

### 1. CLI Layer

The CLI is the user entrypoint.

Its job is intentionally narrow:

- parse user input,
- call the appropriate internal service,
- display results,
- and trigger exports when requested.

The CLI should remain thin. It should orchestrate behavior, not contain the core reasoning.

---

### 2. Adapter Layer

Adapters handle communication with external systems.

Planned examples include:

- a mempool-compatible REST adapter,
- an optional Bitcoin Core RPC adapter,
- file or export adapters where needed.

Adapters should focus on:

- requesting data,
- handling response formats,
- and exposing normalized data to the rest of the application.

They should not contain the main business logic of transaction diagnosis.

---

### 3. Domain Layer

The domain layer holds the project’s core data models.

These models may represent concepts such as:

- transaction analysis results,
- fee context,
- replacement eligibility,
- recommendations,
- exportable reports,
- and structured command outputs.

The domain layer exists to make the system easier to reason about and less dependent on raw API payload shapes.

---

### 4. Service Layer

The service layer contains the main logic of the project.

This is where MemOps should implement behavior such as:

- transaction inspection,
- size and fee-rate calculations,
- replaceability checks,
- stuck-transaction reasoning,
- recommendation generation,
- and report building.

In other words:

- adapters fetch data,
- services interpret it,
- and the CLI exposes it.

That is the core architectural pattern of the project.

---

## Intended Data Flow

A typical command flow should look like this:

1. The user provides a `txid`.
2. The CLI calls the appropriate service.
3. The service requests transaction and fee context through a mempool-compatible adapter.
4. The raw transaction hex is retrieved.
5. The transaction is parsed and relevant fields are inspected locally.
6. The service compares the transaction against current fee conditions.
7. The system produces:
   - an analysis result,
   - a recommendation,
   - and optional export artifacts.

This flow is important because it shows that MemOps is not just reprinting backend responses. It is adding an explicit reasoning layer.

---

## Why Backend Configurability Matters

MemOps is designed for mempool-compatible backends, not for one single public website.

That architectural choice matters for two reasons:

1. **Operational flexibility**
   Users may want to run the same workflow against a public instance or a self-hosted one.

2. **Sovereignty and resilience**
   A tool that can only operate against one public endpoint is less useful for technical users who care about infrastructure choice.

For that reason, the backend URL should be configurable rather than hardcoded.

---

## Why Analysis Is Separated from Signing and Broadcast

MemOps is not designed to take irreversible action by default.

Even in scenarios where the project may later prepare an RBF plan or PSBT, the architecture should preserve a clear boundary between:

- analysis,
- planning,
- signing,
- and broadcasting.

This is both a safety decision and a clarity decision.

It keeps the project aligned with its intended purpose: a verification-first operational tool, not a hidden wallet flow.

---

## Current Architectural Maturity

At the current stage, this architecture should be understood as the intended design direction for the MVP.

The repository is being structured early around this model so that:

- the code stays organized as it grows,
- the logic remains testable,
- and the project is easier to evaluate and maintain.

This is more valuable for MemOps than adding many features too early.

---

## Conclusion

The architecture of MemOps is intentionally simple.

Its goal is to support one core idea well:

**take backend data, inspect what matters locally, and turn transaction visibility into structured operational reasoning.**

That is why the project is organized around:

- a thin CLI,
- isolated adapters,
- explicit domain models,
- and testable service logic.
