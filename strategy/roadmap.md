# Roadmap

## Repository state today

The repository now ships a working baseline for:

- configurable backend-backed transaction inspection
- local raw transaction parsing
- explicit RBF signaling analysis
- first-pass why-stuck diagnosis
- deterministic diagnosis artifact export
- surfaced artifact paths in CLI text and JSON output
- automated coverage for export success and failure paths
- documentation and demo material aligned with shipped behavior

## Completed in the current milestone

- [x] CLI entrypoint for inspection mode
- [x] JSON output for inspection mode
- [x] mempool-compatible backend integration
- [x] local transaction parsing
- [x] explicit RBF analysis
- [x] why-stuck mode and structured diagnosis output
- [x] export mode for why-stuck artifacts
- [x] deterministic artifact layout and surfaced paths
- [x] service and CLI test coverage for export workflows
- [x] README, demo script, assumptions, and handoff updates

## Next priorities

### 1. Improve decision quality

- [ ] richer fee-pressure context beyond a simple band comparison
- [ ] stronger explanation text for diagnosis outcomes
- [ ] clearer distinction between `wait`, `consider_rbf`, and `consider_cpfp` recommendations
- [ ] edge-case handling for confirmed, replaced, or obviously non-actionable transactions

### 2. Add response-planning outputs

- [ ] structured RBF planning output
- [ ] CPFP / package-relay-aware guidance
- [ ] explicit prerequisites and caveats for each proposed action
- [ ] better operator-facing summaries for incident-response usage

### 3. Operational polish

- [ ] fixture-backed demo assets for reliable presentations
- [ ] better filesystem and backend error taxonomy
- [ ] optional dependency cleanup
- [ ] packaging and release polish

## Non-goals right now

The next milestone should not jump straight to:

- wallet automation
- transaction signing
- automatic broadcasting
- background services
- broad workflow orchestration

The strategy remains: deepen trust in analysis quality before expanding into action-taking behavior.
