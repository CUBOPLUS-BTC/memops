# Operating Model for MemOps

## Executive Summary

MemOps is currently a **single-maintainer open-source project**.

That fact matters, and this operating model is written to reflect reality rather than to imitate the structure of a larger organization. MemOps is not presented as if it already had a broad maintainer community, a formal governance system, or commercial support operations. At this stage, it is a focused, public, and technically disciplined MVP being built by one developer.

The project is operated through a GitHub repository that serves as the main source of truth for:

- code,
- documentation,
- test files,
- strategy documents,
- work history,
- and visible progress over time.

The operating goal is simple:

> **Build a small, credible, verification-first tool in public, document it clearly, and leave it in a state that can be understood, reviewed, and extended later.**

This approach is more honest, more maintainable, and more aligned with both CUBO+ evaluation and open-source practice.

---

## 1. Current Stage and Operating Assumption

At the time of this document, MemOps is being developed by one maintainer.

That means the operating model must stay lightweight and realistic. It should prioritize:

- clear scope,
- visible progress,
- small and understandable changes,
- reproducible documentation,
- and best-effort maintenance.

The repository should be ready for future contributions, but it should not pretend that such a contribution model is already active.

This distinction is important. A professional operating model is not the one that sounds bigger. It is the one that matches the real state of the project.

---

## 2. Operating Principles

### 2.1 Public by default

Everything that is not sensitive from a security perspective should be kept public:

- source code,
- technical notes,
- strategy documents,
- issues,
- planned changes,
- and development history.

This is especially important for a verification-first Bitcoin tool. Auditability is part of its credibility.

### 2.2 Verification-first in both product and development

The philosophy of the product should also shape the way it is maintained.

That means:

- small and reviewable changes,
- explicit assumptions,
- reproducible examples,
- tests for core logic,
- and documentation that explains limits as well as features.

MemOps should not only work. It should also be understandable.

### 2.3 Scope discipline over feature inflation

Because the project is maintained by one person, scope discipline is essential.

The operating rule is:

> **A smaller and correct tool is more valuable than a broader but unstable one.**

For that reason, the project should protect its core priorities:

- local transaction inspection,
- mempool-compatible backend support,
- stuck transaction diagnosis,
- and auditable outputs.

Anything that weakens those goals should be cut or deferred.

### 2.4 No mandatory cloud dependence

The project should not require hidden infrastructure, cloud lock-in, or private services in order to run or be reviewed.

MemOps may later use optional external infrastructure for testing or demonstration, but the repository itself should remain portable and understandable without that dependency.

### 2.5 Documentation is part of the operating model

Documentation is not separate from development. It is part of development.

Each meaningful change should ideally leave a visible trace in one or more of the following:

- source files,
- tests,
- README updates,
- technical docs,
- or worklog entries.

For CUBO+ and for open-source continuity, that visibility matters.

---

## 3. GitHub as the Operational Center

The repository is the main operating center of MemOps.

It should contain:

- the Python source code,
- tests,
- technical documentation,
- strategy documents,
- demo guidance,
- and the visible history of project evolution.

For this project, GitHub is not only a hosting platform. It is also:

- an audit trail,
- a documentation hub,
- and the main evidence of authorship and progress.

This is especially relevant because CUBO+ explicitly evaluates real development history rather than last-minute uploads.

---

## 4. Development Workflow

## 4.1 Small, visible progress

Even as a solo maintainer, development should be structured in small, visible increments.

That means:

- committing regularly,
- documenting milestones as they happen,
- avoiding massive end-of-sprint dumps,
- and maintaining a worklog that matches the technical evolution.

This improves credibility and reduces the risk of a repository that looks assembled all at once.

## 4.2 Source structure

The technical implementation should remain organized around clear boundaries such as:

- adapters,
- domain models,
- services,
- and CLI orchestration.

This keeps the project understandable and helps future contributors enter the codebase more easily if the project continues.

## 4.3 Issues and task tracking

At the current stage, formal issue management can stay simple.

Even if the project does not yet have external contributors, it is still useful to track work through:

- GitHub Issues,
- a public roadmap,
- and the external worklog required by CUBO+.

This creates traceability and shows that development decisions were made intentionally.

---

## 5. Quality Standards

MemOps does not need enterprise bureaucracy, but it does need quality standards.

At minimum, the project should aim for:

- clean Python structure,
- readable CLI behavior,
- tests for core transaction logic,
- clear assumptions about what is and is not verified locally,
- and documentation that a third party can follow.

Core logic that deserves special care includes:

- transaction parsing,
- fee-rate calculations,
- size calculations,
- replaceability detection,
- and recommendation logic.

These are not areas where “it seems to work” is enough.

---

## 6. Release and Maintenance Policy

### 6.1 Best-effort maintenance

MemOps should be presented honestly as a best-effort open-source project.

There is no need to claim:

- formal SLAs,
- always-on support,
- or a commercial support structure.

The right message is simpler and more credible:

> MemOps is built in public, documented carefully, and maintained according to the time and capacity of its maintainer and any future contributors.

### 6.2 Versioning

Because the project is in an early stage, a `0.x` versioning approach is appropriate.

This signals that the project is usable as an MVP but still evolving.

### 6.3 Releases when useful, not on fake schedules

Releases should happen when there is a meaningful and stable improvement to publish.

A small project gains more from a few clear releases than from frequent version tags with little substance.

---

## 7. Future Contribution Model

MemOps should be prepared for future contributions, but it should not pretend that a contributor community already exists.

A realistic contribution model at this stage is:

- public repository,
- clear README,
- clear license,
- contribution guidelines,
- and issues that explain what is still needed.

If other developers later want to contribute, the project should be ready to accept help. But today, the operating model remains centered on a single maintainer.

That honesty strengthens the project rather than weakening it.

---

## 8. Why Open Source Is the Right Operating Choice

MemOps is more credible as open-source software than as a closed tool.

That is true for several reasons:

1. **Auditability matters.**
   A tool that analyzes Bitcoin transactions and proposes next steps should be inspectable.

2. **The target users value sovereignty.**
   Operators, self-hosters, and technical teams are more likely to trust tools they can review and run on their own terms.

3. **The project is infrastructure-oriented.**
   MemOps is closer to operational tooling than to a retail product. Open-source is a natural fit.

4. **It matches the long-term intention of the repository.**
   The goal is to leave the project in a donation-ready, reusable, and maintainable state.

---

## Conclusion

MemOps should be operated as what it currently is:

- a focused,
- technically serious,
- single-maintainer,
- open-source MVP.

Its operating model should stay lightweight, public, auditable, and disciplined. That is the best fit for both the CUBO+ evaluation context and the future open-source life of the project.

The goal is not to simulate the structure of a large organization.

The goal is to build a small tool well enough that others can understand it, evaluate it, and potentially continue it later.
