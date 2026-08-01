# Technical Report Reference

Read this file before creating, updating, or auditing a technical report. It defines how to establish implementation truth and reconcile a current-state report.

## What the report represents

The report describes the implementation visible at the selected baseline:

- default: the repository's current working tree, including uncommitted implementation present on disk;
- explicit revision: the commit, tag, or branch named by the user;
- explicit environment: only claims that can actually be verified for that environment.

Do not call repository state “deployed” or “production” unless deployment evidence establishes that equivalence. If the deployed baseline cannot be verified, describe the repository's configured behavior without making an environment claim.

## Evidence hierarchy

### 1. Production source and runtime wiring

Prefer the concrete implementation that executes:

- application and service entry points;
- route, handler, command, job, plugin, and middleware registration;
- dependency injection, module loading, factories, and provider selection;
- concrete callers and callees across important flows;
- persistence, state management, caching, messaging, and external clients;
- authentication, authorization, validation, error handling, retries, and recovery.

Trace behavior through wiring to the concrete implementation. A type, interface, unused module, or dependency declaration alone does not prove that behavior is active.

### 2. Executable configuration

Treat configuration that controls the built or running system as implementation evidence:

- package manifests, lockfiles, compiler and build configuration;
- schemas, migrations, generated API contracts, and policy definitions;
- environment-variable loading and feature-flag wiring;
- Dockerfiles, Compose, deployment manifests, infrastructure as code, and CI workflows;
- startup commands, service definitions, and runtime configuration.

A manifest proves that a dependency is available, not how or whether the project uses it. Follow it into initialization and call sites before describing its responsibility.

### 3. Tests as supporting evidence

Tests can confirm intended and exercised behavior, boundaries, failure cases, and integration surfaces. Inspect the production path they invoke. Do not use a test by itself to claim that a production component is registered, deployed, or active.

### 4. Documentation as navigation, not proof

README files, `docs/`, diagrams, ADRs, Helm artifacts, comments, issue text, and generated prose may help with vocabulary, discovery, and historical intent. They do not establish the current implementation.

Never create or preserve a technical claim solely because another document says it is true. Locate supporting source or executable configuration. When prose conflicts with implementation, report the verified current implementation without narrating the conflict.

User prompts, plans, change summaries, diffs, and execution reports are scope signals, not implementation evidence. They must not become report content.

## Investigation mechanics

### Establish the system shape

For `init` and `audit`, inspect enough of the repository to identify:

1. languages, runtimes, workspaces, and package boundaries;
2. executable entry points and exposed interfaces;
3. module/service boundaries and dependency direction;
4. primary runtime flows;
5. data ownership, persistence, state, and migrations;
6. external integrations and executable configuration;
7. cross-cutting mechanisms important to correctness, security, reliability, performance, or operations;
8. build, test, packaging, deployment, and observability surfaces actually present.

Do not turn a dependency inventory into the report. Record important technology only when its project responsibility is verified.

### Trace an affected implementation

For `update`, use the accepted change scope and diff to start, then inspect the current implementation beyond the changed lines:

1. find the entry or registration point;
2. follow configuration and provider selection;
3. identify the concrete implementation;
4. follow important callers, downstream effects, and data/state changes;
5. inspect related schema, migration, deployment, and test surfaces;
6. identify report statements elsewhere whose meaning now depends on this area.

The final text describes this resulting system, not the steps above and not the delta from the previous system.

### Build a private evidence map

Before editing, privately map each material statement to narrow implementation evidence. Use that map to avoid speculation and to identify stale text. Do not save the map as an audit log, research note, or change appendix in the target project.

In the report, use project-relative implementation anchors when they materially help a maintainer verify or navigate the explanation:

```text
`path/to/file.ext` (`StableSymbolOrSection`)
```

Prefer stable symbols, modules, configuration keys, and section names over dense line-number citations. Never use machine-specific absolute paths. An anchor must point to content that supports the nearby statement; a generic entry point is not evidence for an entire multi-module flow.

## Writing current-state content

### Explain how, not the change

Good current-state wording:

```text
Requests enter through `ApiRouter`, which applies authentication middleware before dispatching to feature handlers.
```

Bad change/history wording:

```text
Authentication was moved from each handler into shared middleware during the latest refactor.
```

Good framework wording:

```text
FastAPI owns HTTP routing and request validation; repository providers supply persistence implementations to route handlers.
```

Bad inventory wording:

```text
The project uses FastAPI and SQLAlchemy.
```

Good current limitation wording, when enforced by implementation:

```text
The importer accepts CSV input only; `InputFormat` rejects other media types before parsing.
```

Bad future-work wording:

```text
The importer does not support JSON yet and should add it later.
```

### Reconcile in place

When reality changes:

- replace stale wording with the current implementation;
- delete descriptions of removed components;
- move content when responsibilities moved;
- merge duplicate descriptions;
- remove empty or inapplicable sections;
- preserve accurate unrelated content;
- do not retain the old account for comparison.

Do not add a note saying that text was updated, corrected, migrated, or superseded.

### Keep explanation proportional

Explain details that a maintainer needs to understand the system:

- non-obvious wiring or control flow;
- cross-module behavior;
- technology responsibility and operational role;
- correctness, security, reliability, data, and failure mechanisms;
- important runtime or deployment constraints enforced by implementation.

Avoid exhaustive file lists, dependency dumps, routine helper internals, and facts obvious from a single conventional declaration unless they clarify the system.

## Mode mechanics

### `init`

1. Resolve the report path and confirm no established report should be preserved elsewhere.
2. Establish the system shape.
3. Copy `templates/technical-report.md` as a structural starting point.
4. Write only verified, applicable sections; delete instructions and empty headings.
5. Check that the opening overview is compact enough for selective intake reading.

If a report already exists, follow `audit` instead.

### `update`

1. Require an existing report.
2. Confirm the accepted scope is specific enough to investigate; use Git diff/status only for discovery.
3. Trace each affected implementation to its current boundaries.
4. Determine impact by comparing verified current implementation to the report — do not accept another agent's impact guess.
5. Prepare a coherent section-level edit, including deletion of stale statements.
6. If no report statement needs to change within the implementation scope examined for this accepted change, return scoped `no-impact`; do not imply that unrelated report sections were audited.

### `audit`

1. Require an existing report.
2. Establish the current system shape independently of the report.
3. Verify every material claim and useful implementation anchor.
4. Check important current implementation areas for omissions.
5. Reconcile all detected drift in place.
6. Run the content-boundary checklist below.

## Content-boundary checklist

Before finishing, confirm that:

- each material technical statement is supported by production source or executable configuration;
- tests are not the sole support for a production behavior claim;
- the report does not rely on README, docs, ADR, Helm, comments, prompts, or plans as implementation proof;
- dependencies described as active have verified wiring and responsibility;
- removed modules, stale interfaces, obsolete configuration, and broken anchors are absent;
- the report contains no before/after story or “this change” narrative;
- rationale and decision trade-offs are absent;
- prompts, requirements, phases, checkpoints, task progress, command output, and test-run results are absent;
- changelogs, history, audit trails, roadmaps, TODOs, risks, and follow-ups are absent;
- the overview remains concise and no empty template sections remain.

## Blocking rule

Return `blocked` when a trustworthy result cannot be produced, for example:

- the project root, report path, or requested baseline cannot be determined safely;
- a central requested claim cannot be verified from accessible implementation evidence;
- the accepted change scope is mixed with unrelated changes and cannot be isolated;
- completing the requested reconciliation would require guessing external or deployed behavior;
- the report cannot be edited safely.

Investigate and draft before writing. If a blocker prevents a coherent update, leave the report unchanged. State the blocker in the operation result, not in the report.
