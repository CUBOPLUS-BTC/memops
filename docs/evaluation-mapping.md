# CUBO+ Evaluation Mapping for MemOps  
  
## Purpose  
  
This document helps reviewers map the MemOps repository to the main CUBO+ evaluation criteria.  
  
It exists to make the repository easier to audit and easier to understand quickly.  
  
---  
  
## Project Context  
  
MemOps is currently a **single-maintainer MVP**.  
  
That means the repository is intentionally scoped and should be evaluated as:  
  
- a focused open-source tool,  
- a serious technical prototype,  
- and a disciplined CUBO+ submission with clear documentation.  
  
It should not be read as if it were already a large company or a mature commercial product.  
  
---  
  
## Evaluation Mapping Table  
  
| CUBO+ Criterion | What It Requires | Where It Appears in MemOps |  
|---|---|---|  
| Transparency and evolution | Visible progress over time | GitHub commit history, `strategy/worklog-link.md`, linked Google Doc worklog |  
| Technical execution | Clean, organized, functional Python project | `src/`, `src/README.md`, `pyproject.toml`, `Makefile`, future tests under `tests/` |  
| Real authorship and explanation | Clear understanding of both project logic and value | `README.md`, `TEAM.md`, `strategy/pitch-script.md`, commit history |  
| Documentation | Clear reports, instructions, and project explanation | `README.md`, `strategy/`, `docs/`, `src/README.md` |  
| Value proposition | Real usefulness for the Bitcoin ecosystem in El Salvador | `strategy/problem.md`, `strategy/impact-analysis.md`, `strategy/business-model.md`, `strategy/pitch-script.md` |  
| Operational model | Explanation of how the project could be maintained | `strategy/operating-model.md` |  
| Work log | Evidence of progressive non-technical development | `strategy/worklog-link.md` + linked Google Doc |  
| Demo readiness | Clear technical walkthrough and narrative | `docs/demo-script.md`, `demo/README.md` |  
| Open-source seriousness | Clear license and contribution model | `LICENSE`, `CONTRIBUTING.md`, `docs/donation-readiness.md` |  
  
---  
  
## Notes on Single-Maintainer Context  
  
Because MemOps is currently being developed by one person, the project demonstrates “cross-functional understanding” through:  
  
- both technical and strategy documentation being present,  
- a coherent project narrative,  
- clear repository structure,  
- and direct authorship evidence in commits and worklog updates.  
  
This is different from a multi-person team, but it is still a valid and auditable model of ownership.  
  
---  
  
## Reviewer Shortcut  
  
If a reviewer wants the fastest way to understand the project, the recommended reading order is:  
  
1. `README.md`  
2. `strategy/problem.md`  
3. `strategy/impact-analysis.md`  
4. `docs/architecture.md`  
5. `docs/demo-script.md`  
6. `strategy/worklog-link.md`  
  
This sequence provides the clearest picture of what MemOps is, why it matters, and how it is being built.  
  
---  
  
## Conclusion  
  
This mapping exists to reduce reviewer friction.  
  
MemOps aims to be easy to inspect, not difficult to decode. This file is part of that goal.
