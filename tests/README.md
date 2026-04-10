# Tests Folder

This directory is reserved for the automated tests of MemOps.

The project aims to keep important logic testable from the beginning, especially around:

- transaction parsing,
- size-related calculations,
- replaceability signals,
- recommendation logic,
- and backend adapter behavior.

Because MemOps is still in an early MVP phase, this folder may start small. That is acceptable as long as the core logic is developed with testability in mind.

The long-term goal is not test quantity for its own sake, but confidence in the parts of the project that affect reasoning and auditability.
