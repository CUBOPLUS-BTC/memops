# Contributing to MemOps

Thank you for your interest in MemOps.

MemOps is an early-stage, verification-first Bitcoin incident response CLI designed for mempool-compatible backends. The project is currently maintained by a single developer and is being built in public with a strong emphasis on clarity, auditability, and disciplined scope.

Because the project is still in an MVP stage, contributions are welcome, but they should remain aligned with the core purpose of the repository.

---

## Project Principles

Contributions should respect the following principles:

- **Don’t trust, verify**
- **Small scope, high clarity**
- **Open-source and reviewable**
- **Mempool-compatible, not single-endpoint locked**
- **Auditability over automation theater**
- **No unnecessary product or cloud complexity**

---

## Good First Contribution Areas

At this stage, the most useful contributions would typically be:

- documentation improvements,
- typo fixes,
- clearer assumptions,
- reproducible demo notes,
- tests for pure logic,
- API compatibility notes,
- and bug reports with clear reproduction steps.

---

## Before Opening a Large Change

If you want to propose a major change, please open an Issue first and explain:

- what problem you want to solve,
- why it matters,
- how it fits the scope of MemOps,
- and what tradeoffs it introduces.

This helps protect the project from unnecessary scope expansion.

---

## Scope Boundaries

MemOps is intentionally **not** trying to become:

- a wallet,
- a full block explorer,
- a cloud platform,
- a retail app,
- or a broad enterprise dashboard.

Contributions that push the project outside its core mission may be declined or deferred.

---

## Documentation Expectations

If a contribution changes behavior, assumptions, or user-visible outputs, please update the relevant documentation as well.

That may include one or more of the following:

- `README.md`
- `src/README.md`
- files under `docs/`
- files under `strategy/`

---

## Code Quality Expectations

For technical contributions, the preferred direction is:

- small and reviewable changes,
- testable logic,
- minimal hidden behavior,
- and explicit assumptions.

The project values clarity more than cleverness.

---

## Branching and Pull Request Workflow

Starting in Phase 2, MemOps follows a lightweight GitHub Flow suitable for a single-maintainer MVP:

- `main` is the stable branch and should remain demoable.
- New work starts from short-lived branches such as `feat/...`, `fix/...`, `docs/...`, `test/...`, `chore/...`, `ci/...`, or `refactor/...`.
- Branches should be pushed early to preserve visible progress.
- Opening a Draft PR early is encouraged.
- Merges into `main` should happen through pull requests after CI passes.
- Preferred merge method: **Rebase and merge**.
- **Squash and merge** may be used for noisy cleanup-only branches, but preserving small logical commits is preferred.
- Stable milestones should be tagged on `main` (for example `phase-1-complete`, `v0.1.0`).

Phase 1 was bootstrapped directly on `main` with small atomic commits as part of the executable MVP baseline. Future work uses the branch-based workflow above to keep `main` stable while preserving auditability.


---

## Security and Safety Notes

MemOps operates in a sensitive domain: Bitcoin transaction handling and incident response logic.

For that reason:

- do not add hidden signing flows,
- do not add automatic irreversible behavior by default,
- do not commit secrets, private keys, or sensitive credentials,
- and do not assume production-grade safety without clearly documenting limitations.

---

## Reporting Issues

When reporting a bug or limitation, try to include:

- what you expected,
- what actually happened,
- the relevant command or context,
- whether the issue came from backend data, local logic, or export behavior,
- and enough detail for the problem to be reproduced.

---

## Maintenance Model

MemOps is currently maintained on a **best-effort basis**.

That means contributions may not be reviewed immediately, and the project does not promise commercial support or guaranteed response times. This is an intentional and honest operating model for an early open-source project.

---

## License

By contributing to MemOps, you agree that your contributions may be included in the project under the same license as the repository.

---

## Final Note

MemOps is strongest when it stays focused.

If you want to help, the best contributions are the ones that make the project:

- easier to understand,
- easier to verify,
- easier to run,
- and more useful for real Bitcoin operations.
