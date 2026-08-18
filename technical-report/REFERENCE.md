# Technical Report Reference

Read this file before creating, updating, or auditing a technical report. It defines how to establish implementation truth and reconcile a current-state report.

## What the report represents

The report is one self-contained HTML file. Its entire content lives in the `report-data` JSON block; everything else in the file is fixed template code. Editing a report means editing that JSON block.

The report describes the implementation visible at the selected baseline:

- default: the repository's current working tree, including uncommitted implementation present on disk;
- explicit revision: the commit, tag, or branch named by the user;
- explicit environment: only claims that can actually be verified for that environment.

Do not call repository state “deployed” or “production” unless deployment evidence establishes that equivalence. If the deployed baseline cannot be verified, describe the repository's configured behavior without making an environment claim.

## Evidence hierarchy

### Capability proof levels

Classify each material capability privately before choosing report wording. These levels express increasing claim strength, but `Configurable` is an optional affordance rather than a prerequisite: hard-coded composition can select and invoke an implementation without exposing a configuration choice.

1. **Declared** — a dependency, symbol, interface, helper, schema, flag, or provider exists. This proves availability only.
2. **Configurable** — a manifest, configuration key, environment resolver, command option, or API shape can express the capability. This proves configurability only.
3. **Selected** — the chosen baseline's executable configuration or composition root registers or directly constructs that implementation.
4. **Invoked** — a real production entry reaches the selected concrete caller and callee with the actual arguments, producing state, output, or an external effect. This is the minimum level for claiming current active behavior.
5. **Externally active** — deployment or environment evidence establishes that the selected behavior is enabled in the named external environment.

A report claim cannot exceed its proved level. Tests may support a level but cannot by themselves promote `Declared` to `Invoked`. Repository code that reaches `Invoked` does not prove `Externally active`; describe repository-configured behavior unless deployment evidence establishes more.

Do not print proof-level labels in the report. Use them to calibrate natural current-state wording. Omit ordinary `Declared` / `Configurable` alternatives that the selected path does not use. Mention one in operation evidence only when it directly supports a correction, scoped `no-impact`, or blocker; otherwise omit it there too. Include non-use in the report only when it materially defines current behavior, such as a caller selecting an incompatible or rejected contract.

### 1. Production source and runtime wiring

Prefer the concrete implementation that executes:

- application and service entry points;
- route, handler, command, job, plugin, and middleware registration;
- dependency injection, module loading, factories, and provider selection;
- concrete callers and callees across important flows;
- persistence, state management, caching, messaging, and external clients;
- authentication, authorization, validation, error handling, retries, and recovery.

Trace behavior through the full active production loop:

```text
executable entry
→ registration / composition
→ selected configuration or provider
→ concrete caller with actual arguments
→ concrete callee / host adapter
→ state, output, or external effect
```

A type, interface, unused module, helper, request flag, environment-variable resolver, provider, test, or dependency declaration alone does not prove that behavior is active. Registration without a reachable production entry proves `Selected`, not `Invoked`.

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

1. languages, runtimes, workspaces, independent packages, and package boundaries;
2. deployable units, startup commands, executable entries, and composition roots;
3. module/service boundaries, dependency direction, and exposed interfaces;
4. process, thread, worker, host, replica, and service boundaries where applicable;
5. object/module lifetimes and process-local, host-local, or shared state;
6. primary synchronous, asynchronous, queued, batched, buffered, and external runtime flows;
7. data ownership, persistence, state, and migrations;
8. external integrations and executable configuration;
9. cross-cutting mechanisms important to correctness, security, reliability, performance, or operations;
10. build, test, packaging, deployment, and observability surfaces actually present.

Do not infer the whole repository from its root manifest, primary workspace, or dominant language. Discover independent services, extensions, workers, plugins, compatibility shims, and separately built packages. A sample deployment definition proves repository-supported configuration, not the topology of an external environment unless the selected baseline establishes it. A worker-count, concurrency, mode, or provider environment variable proves configuration intent only until a startup/composition path reads it and constructs the corresponding runtime behavior; do not multiply replicas by an unconsumed worker-count variable and call the result a process topology.

Do not turn a dependency inventory into the report. Record important technology only when its project responsibility is verified.

### Trace an affected implementation

For `update`, use the accepted change scope and diff to start, then inspect the current implementation beyond the changed lines:

1. find the real executable entry, not a test-only caller;
2. follow registration / composition and baseline-selected configuration or provider;
3. follow the concrete caller with its actual arguments into the concrete callee or host adapter;
4. verify the resulting output, state transition, persistence, or external effect;
5. inspect alternate entries/providers, disabled flags, rejection branches, fallback, bypass, and degraded paths;
6. for cross-component behavior, verify the exact contract produced and accepted on both sides;
7. inspect related schema, migration, deployment, and test surfaces;
8. identify report statements elsewhere whose meaning now depends on this area.

The final text describes this resulting system, not the steps above and not the delta from the previous system. A directly tested helper is still only `Declared` unless a production entry reaches it.

### Verify both sides of cross-component contracts

For integrations between separately parsed, versioned, deployed, or persisted components, inspect both producer/caller and consumer/callee:

- CLI command, argument order, flags, defaults, exit codes, stdout, and stderr versus the invoked parser;
- client method, path, headers, query, payload, defaults, and status/error mapping versus the server route and schema;
- producer serialization, framing, key shape, and version versus consumer deserialization and compatibility handling;
- file writer versus reader; cache-key producer versus lookup; plugin/extension bridge versus host entry;
- timeout, retry, cancellation, and fallback behavior on both sides.

The caller's intent does not prove the callee accepts the exact command, flags, payload, schema, or key it emits. The callee's capability does not prove the caller selects or invokes it. Describe a current incompatibility or rejected path neutrally when it materially affects how the system works; do not narrate how it became incompatible.

### Apply semantic proof gates and seek counter-evidence

Strong semantics require `Invoked` wiring plus evidence for the guarantee itself. Before writing them, inspect both supportive and narrowing evidence:

- **Streaming / incremental processing:** verify producer and consumer behavior, framing, buffering, batching, materialization, backpressure, and whether timers cover network reads or only post-buffer parsing. A stream request flag or streaming response type alone does not prove end-to-end streaming.
- **Atomic / transactional / race-free / quota:** inspect the actual read/write primitive, transaction or lock key, non-atomic read-modify-write sequences, shared-store semantics, and process / worker / replica scope. A process-local lock or shared KV alone does not prove deployment-wide atomicity.
- **Idempotent / exactly-once / ordered:** inspect key derivation, reservation/commit windows, retries, partial failures, duplicate side effects, and expiry/fallback behavior.
- **Timeout / cancellation:** locate the timer, identify the operation it surrounds, and prove whether abort propagates to concrete I/O or merely stops the caller waiting.
- **Secrets / secure storage / authentication coverage:** trace source, precedence, persistence, actual caller arguments, transport, log redaction, route/command coverage, bypasses, and fail-open/fail-closed behavior. A secret-provider abstraction does not prove secure persistence or use.
- **Global / all / always / never / compatible / supported:** inspect every relevant entry and alternate path, then state the smallest proven scope.
- **Production / deployed / externally active:** require external deployment evidence; otherwise describe repository-configured behavior.

For every material claim, actively look for the nearest rejection branch, unsupported command/flag, alternate provider, disabled feature, bypass, fallback, degraded mode, exception swallowing, retry exhaustion, buffering/materialization, process-local state, or non-atomic operation that could falsify or narrow it.

If proof is insufficient, narrow the wording to the exact behavior and scope proved, or omit the claim. If the unproved semantic is central to the requested report, return `blocked`. A current defect or degraded path is current implementation truth and may be stated neutrally; it is not change history.

### Build a private evidence map

Before editing, privately map each material statement to:

- narrow implementation evidence and its capability proof level;
- the exact instance/request/key/process/worker/replica/service/environment scope;
- producer and consumer evidence for cross-component claims;
- the nearest counter-evidence or narrowing path checked.

Use that map to avoid speculation and to identify stale text. Do not save the map as an audit log, research note, or change appendix in the target project.

In the report, put project-relative implementation anchors in module `evidence` arrays and section `anchors` blocks when they materially help a maintainer verify or navigate the explanation:

```text
path/to/file.ext (StableSymbolOrSection)
```

Prefer stable symbols, modules, configuration keys, and section names over dense line-number citations. Never use machine-specific absolute paths. An anchor must point to content that supports the nearby statement; a generic entry point is not evidence for an entire multi-module flow.

## Writing current-state content

### Explain how, not the change

The same wording rules apply to every text field in the data block: module `summary`, `detail`, `notes`, section `blocks`, and edge `label`.

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

- replace stale module `summary` / `detail` / `notes` wording with the current implementation;
- delete module entries, their edges, and section content for removed components;
- move `detail` / `notes` content to the module or section that now owns the responsibility;
- merge duplicate descriptions across modules and sections;
- remove empty or inapplicable modules, edges, and sections;
- preserve accurate unrelated entries and all template code;
- do not retain the old account for comparison.

Use **one fact, one canonical home**:

- overview diagram: compact system shape only;
- module `detail` / `notes`: the canonical explanation of that module's internals and key mechanisms;
- `edges` with labels: dependency direction and runtime flows: step-by-step execution;
- sections: cross-cutting content (runtime/technology responsibilities, data and state, security and failure, build and deployment).

Explain a mechanism in detail once, in its owning module or section. Elsewhere state only the local consequence or use a short reference. During update/audit, search for and remove stale or duplicated versions scattered across modules and sections.

Do not add a note saying that text was updated, corrected, migrated, or superseded.

### Keep explanation proportional

Explain details that a maintainer needs to understand the system:

- non-obvious wiring or control flow;
- cross-module behavior;
- technology responsibility and operational role;
- correctness, security, reliability, data, and failure mechanisms;
- important runtime or deployment constraints enforced by implementation.

Avoid exhaustive file lists, dependency dumps, routine helper internals, and facts obvious from a single conventional declaration unless they clarify the system.

### Calibrate claim scope

State the smallest runtime boundary the evidence proves: instance; request or job; key or tenant; process or worker; host or replica; service; deployment; environment.

Do not turn a verified local boundary into a repository-wide guarantee:

- a process-local or per-key lock does not prove cross-worker atomicity;
- shared storage does not by itself prove transactional quota enforcement;
- one middleware, route group, adapter, or entry does not prove all requests or all I/O use it;
- a streaming flag does not prove end-to-end incremental delivery;
- one package or root workspace does not define every component's language or runtime.

Avoid `all`, `every`, `always`, `never`, `global`, `fully`, `strict`, `end-to-end`, `supported`, and `compatible` unless all relevant entries, alternate paths, and topology boundaries were checked. Qualify the component, key, process, host, service, or environment instead.

## Authoring the data block

The whole report content is one JSON object inside the `<script type="application/json" id="report-data">` block. Everything outside that block is fixed template code: never modify it while creating or editing a report. Template bugs are fixed in `templates/technical-report.html`, not in an individual report.

### Schema semantics

- `title` / `summary` — project name and a one-sentence system overview shown in the header.
- `modules` — one entry per module. `parent` builds the tree; modules without `parent` (or with an unknown parent) render at the top level. Maximum depth is three levels (system → module → component); deeper content belongs in `detail` / `notes` text.
- `layer` — one of `entry`, `core`, `data`, `infra`, `external`, `frontend`, chosen for the module's role in this project. The template colors nodes by layer and renders a legend.
- `summary` — one short line rendered under the node label; keep it under roughly thirty characters.
- `detail` — the canonical 2-4 sentence explanation; `notes` — non-obvious mechanisms, one per bullet; `evidence` — project-relative anchors supporting the claims.
- `edges` — `from` / `to` reference module ids at any depth. The template lifts edges automatically: an edge between deep components renders at the overview as an edge between their top-level ancestors, and exactly inside the relevant sub-diagram. When one endpoint lies outside the drilled-in module, it renders as a dashed external context node; the drilled-in module itself renders as a boundary entry node when edges touch it. `kind` is `flow` (invocation or data flow, solid) or `dep` (dependency or deployment relation, dashed); `label` is short and optional.
- `sections` — optional tabs for cross-cutting content. Each block is `p` (paragraph), `bullets` (`items`), `code` (`text`), or `anchors` (`items`). Omit empty sections.

### Validation before writing

- the block is valid JSON: no comments, no trailing commas, `"` and `\` escaped, any literal `</script>` written as `<\/script>`;
- module ids are unique; every `parent` references an existing module; no module is deeper than three levels;
- every `layer` is one of the six defined values;
- every edge references existing module ids and has `kind` `flow` or `dep`;
- every module is reachable from the top level through `parent` links (no orphan subtrees);
- summaries are one line; anchors use project-relative paths and support the nearby statement;
- the report contains no empty `sections` entries and no unused schema fields.

## Mode mechanics

### `init`

1. Resolve the report path and confirm no established report should be preserved elsewhere.
2. Establish the full repository/runtime topology before generalizing from any primary package.
3. Close active wiring for the material runtime flows and apply semantic proof gates.
4. Copy `templates/technical-report.html` to the report path and replace only the content of the `report-data` block with the generated JSON.
5. Write only verified, applicable modules, edges, and sections; do not change anything outside the data block.
6. Check that the top-level diagram is compact enough for selective intake reading and detailed mechanisms each have one canonical home.

If a markdown report exists without an HTML report, migrate it first (see SKILL.md): use it as a claim inventory only, re-verify every material claim, then delete the markdown file after the HTML report is written.

If a report already exists, follow `audit` instead.

### `update`

1. Require an existing report.
2. Confirm the accepted scope is specific enough to investigate; use Git diff/status only for discovery.
3. Trace each affected implementation to its current boundaries.
4. Determine impact by comparing verified current implementation to the report's `report-data` block — do not accept another agent's impact guess.
5. Prepare a coherent data-block edit: rewrite, add, move, or delete only the affected module entries, edges, and section blocks, including deletion of stale statements.
6. If no report statement needs to change within the implementation scope examined for this accepted change, return scoped `no-impact`; do not imply that unrelated report sections were audited.

### `audit`

1. Require an existing report.
2. Establish the current system shape independently of the report.
3. Verify every material claim and useful implementation anchor in the `report-data` block.
4. Check important current implementation areas for omissions.
5. Reconcile all detected drift in place, editing only the `report-data` block.
6. Run the content-boundary checklist below.

## Content-boundary checklist

Before finishing, confirm that:

- each material technical statement is supported by production source or executable configuration;
- tests are not the sole support for a production behavior claim;
- the report does not rely on README, docs, ADR, Helm, comments, prompts, or plans as implementation proof;
- active claims close the production loop from executable entry through selected wiring and actual arguments to effect;
- cross-component claims verify both producer/caller and consumer/callee contracts;
- strong semantics pass their data, concurrency, topology, and counter-evidence gates;
- fallback, bypass, rejection, buffering, and degraded paths that narrow claims were checked;
- claim quantifiers match the proved instance/process/worker/replica/service/environment scope;
- dependencies described as active have verified wiring and responsibility;
- removed modules, stale interfaces, obsolete configuration, and broken anchors are absent;
- each mechanism has one canonical detailed explanation and the overview diagram stays compact;
- the report contains no before/after story or “this change” narrative;
- rationale and decision trade-offs are absent;
- prompts, requirements, phases, checkpoints, task progress, command output, and test-run results are absent;
- changelogs, history, audit trails, roadmaps, TODOs, risks, and follow-ups are absent;
- non-blocking uncertainty is excluded from report claims and appears only in the optional operation-result `unverified` field;
- no empty modules or sections remain;
- the `report-data` block is valid JSON and is the only part of the HTML file that differs from `templates/technical-report.html`;
- module ids are unique, every `parent` exists, no module is deeper than three levels, and every `layer` value is one of the six defined layers;
- every edge references existing module ids with a valid `kind`;
- module summaries are one line and each material claim has supporting `evidence` anchors or section `anchors`;
- any literal `</script>` inside the data block appears as `<\/script>`.

## Blocking rule

Return `blocked` when a trustworthy result cannot be produced, for example:

- the project root, report path, or requested baseline cannot be determined safely;
- a central requested claim cannot be verified from accessible implementation evidence;
- the accepted change scope is mixed with unrelated changes and cannot be isolated;
- completing the requested reconciliation would require guessing external or deployed behavior;
- the report cannot be edited safely.

Investigate and draft before writing. If a blocker prevents a coherent update, leave the report unchanged. State the blocker in the operation result, not in the report.

In a scoped `update`, an important adjacent uncertainty outside the accepted scope may be excluded from report claims and verified `scope`, then returned as `unverified`. In full `init` / `audit`, material uncertainty about an existing claim or important omission requires `blocked`; `unverified` is allowed only for a boundary explicitly outside the report baseline or stated scope. Do not use it to hide an unproved central semantic, make `no-impact` cover an unchecked area, or create a partial report that should have been `blocked`.
