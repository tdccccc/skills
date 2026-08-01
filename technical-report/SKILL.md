---
name: technical-report
description: 'Create, update, and audit a repository technical report that explains the verified current implementation. Use when the user asks for a technical report, implementation report, architecture or technology documentation, to synchronize technical documentation after accepted code changes, or mentions technical-report, 技术报告, 开发报告, 更新技术报告, or 审计技术报告. Not for changelogs, decision rationale, plans, prompts, or execution logs.'
install-targets: claude
---

# Technical Report

Maintain a clear, code-evidenced explanation of how the project **currently works**.

The report is a current-state implementation reference, not a history of how the project arrived there. Explain the actual technology, architecture, wiring, flows, and key mechanisms. Do not narrate the change that prompted the update.

## Content contract

Write only the verified current implementation:

- what important technologies and frameworks are actually in use;
- what responsibilities they have in this project;
- how entry points, modules, interfaces, data, and runtime flows connect;
- how important implementation mechanisms operate;
- how executable configuration, integrations, build, tests, deployment, security, and failure behavior are currently defined.

Do **not** put any of the following into the report:

- the transition from an old implementation to a new one, before/after comparisons, or change summaries;
- why a change was requested, why an implementation was changed, or why an option was chosen;
- the user's prompt, conversation, requirement wording, or instructions to the agent;
- Helm goals, phases, checkpoints, task progress, journals, or execution reports;
- attempted, rejected, superseded, or reverted approaches;
- command transcripts, test-run results, audit trails, or agent activity;
- changelogs, decision history, roadmaps, TODOs, risks, or follow-up work;
- dates, authors, generation status, or update metadata.

When implementation changes, replace or remove stale statements in place. Never preserve the old account merely to explain the transition. Git holds file history; Helm journal holds execution history; ADRs hold durable decision rationale.

Existing documentation can help locate code or supply canonical domain terms, but it is not proof of implementation. Verify technical claims in production source code and executable configuration. Read `REFERENCE.md` before investigating or editing.

## Project artifact

Default path:

```text
<project-root>/docs/technical-report.md
```

Use a user-specified path when provided. If an existing report uses another clearly established path, keep that path rather than creating a duplicate.

Supporting files live next to this `SKILL.md`:

- `REFERENCE.md` — evidence, investigation, update, and audit mechanics;
- `templates/technical-report.md` — report structure.

Resolve them relative to this skill's install directory. When creating a report, adapt the template to the verified project and remove every empty or inapplicable section.

## Modes

Infer the mode from the request and repository state. Resolve a missing report deterministically:

- explicit `init`, an unspecified first request, or the first Helm synchronization after the user enables technical-report maintenance → `init`, even when an accepted change scope is available;
- explicit `update` or `audit` that expects an already established report → `blocked` with a recommendation to run `init`.

After initialization, accepted changes use `update`; accuracy checks use `audit`.

### `init`

Use when no report exists or the user asks to establish one.

1. Inspect the repository broadly enough to explain its current system shape and important implementation paths.
2. Create the report from the template using verified implementation evidence.
3. Include only applicable sections with substantive current-state content.

If the report already exists, do not overwrite it from scratch. Treat `init` as a full `audit` so repeated initialization is safe.

### `update`

Use after an accepted implementation change or when the user gives a reliable change scope.

1. Use the accepted diff, changed paths, and task context only to locate the potentially affected implementation.
2. Trace each affected area through its complete **current** wiring, concrete implementation, callers, data/configuration, and relevant verification surface. A diff alone is not sufficient evidence for the resulting description.
3. Compare that implementation with the existing report.
4. Rewrite, add, move, or delete only the affected current-state content; repair neighboring statements when their meaning changed.
5. Leave unrelated accurate sections untouched.

If no report exists, return `blocked` and recommend `init`; do not silently create a partial report.

### `audit`

Use when the user asks whether the report is accurate, when the impact scope is unreliable, or when drift may extend beyond a known change.

1. Re-establish the project's current system shape from implementation evidence.
2. Verify every material report claim and implementation anchor.
3. Find important implemented areas the report omits.
4. Remove stale, unsupported, historical, rationale, prompt-derived, plan-derived, and process-oriented content.
5. Reconcile the report in place. Do not append an audit section or audit history.

If no report exists, return `blocked` and recommend `init`.

## Workflow

1. Determine the project root, report path, mode, and implementation baseline. Default to the current working tree; honor an explicitly requested revision or environment.
2. Read applicable repository instructions. Read the current report when it exists.
3. Inspect manifests and discover runtime/build/deployment entry points, then trace the relevant production implementation and executable configuration.
4. Use tests to understand the existing verification surface, never as the sole proof of production behavior.
5. Build a private evidence map connecting each planned technical statement to implementation evidence. Do not write investigation notes into the project.
6. Draft the complete report edit before writing. If a central requested area cannot be verified, stop with `blocked` rather than leave speculative or half-reconciled content.
7. Create the report or edit it in place. Preserve accurate unaffected content and the project's useful terminology.
8. Re-read the resulting claims against implementation evidence and the prohibited-content list.
9. Return exactly one result status.

## Result contract

Return a concise operation result outside the report:

```text
status: updated | no-impact | blocked
report: <report path>
scope: <verified implementation/report scope>
summary: <one-sentence result>
evidence: <concise list of implementation/configuration areas inspected>
```

For `blocked`, also return:

```text
blocker: <what prevents a trustworthy report update>
```

Meanings:

- `updated` — the report was created or its content changed;
- `no-impact` — the required investigation found no report change within the verified scope (`update`) or across the full report (`init` / `audit`); it never claims that unexamined sections were audited;
- `blocked` — the requested synchronization cannot be completed reliably or safely.

For `update` + `no-impact`, `scope`, `summary`, and `evidence` must identify the accepted-change scope actually examined. Never state or imply that the report is accurate as a whole unless the run was a full `init` / `audit`.

Do not invent `created`, `partial`, or `success` statuses. A `blocked` run must not leave speculative or knowingly half-complete report edits.
