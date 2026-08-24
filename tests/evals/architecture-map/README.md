# Architecture-map behavior evals

These synthetic repositories test whether `architecture-map` proves active implementation rather than inferring behavior from declarations. Copy one fixture to a disposable directory, run its prompt against a fresh agent with the installed skill, then inspect the edited/created report and operation result. Never run a write-enabled eval against the canonical fixture directory: `updated` is valid only when the disposable report file actually changes.

Each fixture contains:

- `prompt.md` — user request;
- `case.json` — expected facts, forbidden claims, and hard-failure conditions;
- minimal implementation/configuration evidence;
- `seed-report.html` when the case exercises audit/update correction.

Score each case out of 10:

1. traces the real production entry and active wiring (2);
2. synthesizes reader-facing runtime, Core, data-owner, integration, and trust boundaries instead of copying the package tree, while keeping Host-to-use-case paths traceable (1);
3. distinguishes declared/configurable/selected/invoked evidence (1);
4. verifies both sides of a cross-component contract where applicable (1);
5. finds the decisive rejection, fallback, bypass, buffering, or degraded path (1);
6. classifies data ownership and rebuildability at the correct store or field scope (1);
7. uses direct prose, ordered steps, and comparison tables instead of noun stacks or flat fact dumps (1);
8. writes current state without audit/change history, rationale, or prompt text (1);
9. returns the correct status and verified scope (1).

Any condition in `hard_failures` makes the case fail regardless of score.
