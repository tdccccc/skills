# P1 — reader-first-report

goal_ref: ../goal.md
updated: 2026-08-19

## Outcome

The architecture-map skill consistently produces a traceable, low-noise system map and plain technical explanations, demonstrated by the corrected arxiv-daily report.

## Assumptions

- The verified arxiv-daily Host/Core/Vault/Relay model from the independent source review is the correct baseline.
- Secondary helper and sequencing relationships can move from diagram edges into module details, steps, or tables without hiding material behavior.

## Approach

Tighten the reusable synthesis and writing gates, simplify the arxiv-daily Core graph around its control/data spine, rewrite jargon-heavy section text, refresh every versioned shell, then run automated and real-browser checks.

## Test strategy

- change kind: behavior change to generated report guidance and renderer shell, plus report-data correction
- strategy: Green characterization baseline with focused contract assertions and rendered-artifact audits
- Red / baseline signal: the current full test run fails because seed shells are stale; the current Core drill-down has eight proper crossings and the report still contains overly abstract wording.
- Green / regression checks: Python contract tests, jsdom template suite, refresh-template checks, report-data structural audit, route/collision audit, and Chromium smoke at 1600x1000 and 1024x768.
- exception: report prose and graph semantics are validated by evidence review and rendered inspection rather than a synthetic Red for every sentence.

## Tasks

- [ ] Add main-spine, Host-to-use-case, drill-down density, and plain-language section gates to the skill with contract coverage.
- [ ] Reconcile arxiv-daily report data, simplify Core edges, and rewrite the five supporting sections.
- [ ] Refresh seed reports and the target shell; run focused and repository regression checks.
- [ ] Run real Chromium interaction/readability smoke tests at desktop and narrow sizes.

## Verification

- Pending.

## Abort / reshape triggers

- If simplifying the graph removes a material runtime hand-off or leaves a core use case untraceable, reshape the module tree instead of deleting more edges.
- If the shared renderer cannot keep the report readable at 1024px without project-specific CSS, move the fix into the shared template rather than patching the target shell.
