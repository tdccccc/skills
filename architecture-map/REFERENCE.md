# Architecture Map Reference

Read this file before creating, updating, or auditing an architecture map report. It defines how to establish implementation truth and reconcile a current-state report.

## Contents

- What the report represents
- Evidence hierarchy
- Investigation mechanics
- Architecture synthesis mechanics
- Writing current-state content
- Reader-facing section mechanics
- Authoring the data block
- Mode mechanics and blocking rules

## What the report represents

The report is one self-contained HTML file. Its project-specific content lives in the `report-data` JSON block; everything else is the versioned renderer shell from `templates/architecture-map.html`. Editing implementation claims means editing the data block. Updating renderer behavior means refreshing the whole shell from the shared template while preserving that block.

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

For idempotency or claim semantics, inspect the exact key derivation and the consumer that reserves it. Distinguish a record/index key from an automatic provider idempotency or claim key; state only the verified inputs and scope. A channel/provider field in a record does not prove that channel/provider participates in the claim key. For locks, distinguish process-local exclusion from a shared atomic claim. A process-local `RunLock` cannot be described as making concurrent hosts converge, preventing last-writer-wins, or resolving cross-process conflicts.

For command-line products, trace each subcommand separately through the parser: some commands may return directly, invoke a filesystem/archive helper, or spawn another process without constructing the main runtime. Do not attach a runtime-builder edge or technology claim to the whole command family unless every relevant subcommand reaches it.

For storage and recovery security, separate ordinary path normalization from stronger primitives. A lexical root check on regular reads/writes/renames does not imply no-follow or descriptor protection; report no-follow/descriptor guarantees only for the concrete exclusive-create, recovery, or namespace-guard paths that use them.

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

## Architecture synthesis mechanics

Do not convert discovered files directly into nodes. First write a private system brief with these fields:

0. a system thesis: trigger → runtime unit → core use case → durable state or external effect → user-visible result;
1. runtime units and their composition roots;
2. host-facing entry points and the user or scheduler action that reaches each one;
3. core use cases and the durable result or external effect each produces;
4. port contracts and the host/provider adapters selected at each composition root;
5. authoritative records, rebuildable projections, mixed stores whose fields have different ownership, configuration, checkpoints, caches, claims/locks, and histories;
6. external systems and trust boundaries;
7. one to three golden paths plus the important recovery or bypass path that changes their meaning.

Keep caches, checkpoints, authoritative state, claims, history, and export/import archives as distinct data categories. Record archive/checkpoint sensitivity (for example prompts, research topics, extracted content, or model output) and distinguish verified permission/path checks from broader security assumptions.

For CLI archives, inspect `dataExport` and `dataImport` independently. Export and import are not one symmetric safety boundary: export may validate source Vault paths and write a ZIP, while import may additionally validate the raw ZIP directory, entry names, CRC, compressed/uncompressed limits, compression ratio, and promotion/rollback transaction. Put each guarantee only on the command path that enforces it.

Select two to four primary scenarios for the report. For each one, verify the trigger, ordered steps, hand-offs, durable/external effect, visible result, and the failure or alternate path that changes the reader's understanding. A set of disconnected component facts is not a scenario.

Use the brief to derive the module tree:

- Make a runtime, product surface, core boundary, data owner, or external trust boundary a top-level node when a new maintainer must understand it before reading implementation detail.
- Put packages, adapters, services, commands, and storage files beneath the concept they implement. A directory boundary is supporting evidence, not an automatic architecture boundary.
- Keep host composition roots separate from the host-neutral core. Show adapters under their owning host or runtime, and show core ports under the core when that distinction materially explains dependency direction.
- Do not promote a library to a runtime node merely because it has its own package. State explicitly which process or host loads it.
- Group external providers under an “external systems” concept when their individual identity is secondary at overview level; keep an intermediary service separate when it is independently deployed or changes trust/failure behavior.
- Group persistent artifacts under the component that owns their consistency semantics. Distinguish an authoritative commit from a projection that can be repaired or rebuilt.
- A node owns behavior or a durable artifact with a named writer. Three shapes are not nodes: a value object or DTO passed between modules (a note on its owning module plus at most one producer-to-consumer edge); a shared service hosted inside a process it does not own (the service is a node under its owner; which process hosts it is a runtime fact in the host's notes and the runtime section); and a subcommand or installer that produces an operational artifact such as a cron entry (an operational fact, not a component).
- When one persisted document mixes user-owned fields and generated fields, describe the ownership and repairability per field group. Never call the whole document rebuildable unless every material field can be reconstructed without losing user decisions.
- Keep build, test, packaging, release, and deployment governance out of the runtime overview. Explain those relationships in their section or in a separate drill-down only when they form a real deployable-unit boundary.

Run four comprehension checks before accepting the overview:

1. **Package-name removal:** explain the diagram without package or directory names. If the explanation collapses, the diagram is still an inventory.
2. **Golden-path narration:** narrate the main flow from entry to effect using only visible top-level nodes and edge labels. If a hand-off is missing or requires hidden implementation knowledge, revise the tree or edges.
3. **Runtime-unit check:** for every executable top-level node, name what starts it and whether it stays resident; for every non-executable top-level node, name the boundary or data it owns. If that answer is unclear, the node is probably at the wrong level.
4. **Governance separation:** hide the build/test/release section and verify that the overview still describes how the system runs. If not, engineering workflow has leaked into runtime architecture.

Run the same reader check on every drill-down. First state its **main spine** as trigger → owned use case → durable state or external effect. Then remove an edge from the drawing when it only repeats a helper call, cleanup order, or secondary ownership fact already explained in detail or steps. Keep the fact in the report; change only its visual home. A structural container may be edge-free when its child nodes carry all relationships; do not add a fake ownership arrow just to make the container non-isolated.

For every Host, perform an **entry-to-use-case traceability** check: a reader must be able to identify which scheduled, manual, interactive/reading, and delivery paths that Host can trigger without opening source code. Prefer one aggregated use-case edge and a concrete mapping in the Host detail over separate arrows from every command, screen, or subcommand.

Overview edges are selective. Apply primary-flow selection: include the smallest edge set that narrates the system's main path — the primary invocation, data ownership, deployment, or trust-boundary relationships — and put secondary helper dependencies, repeated provider calls, and file-level relationships into drill-downs or sections. Every visible edge label should state what crosses the boundary, such as “starts daily run”, “writes report and index”, or “sends digest”; avoid labels such as “uses”, “integration”, or a bare method name unless that name is the project’s established vocabulary.

Control and payload may deserve separate edges only when the labels make their roles unmistakable. A completion callback that triggers delivery and a Digest carried by that callback are not two triggers. If the renderer cannot show that distinction clearly, keep the control edge and explain the payload in the ordered flow.

Synthesis can connect verified facts but cannot create a relationship that no runtime wiring, contract, data ownership rule, or deployment boundary supports. Verify both endpoints and the hand-off before adding an edge.

Use diagram edges for actual invocation, ownership, or deployment hand-offs. Put cleanup order, event-append order, retry timing, and other temporal sequencing in `steps` or failure tables unless the implementation has a concrete data/control hand-off. Do not draw a checkpoint-to-report or state-to-history arrow merely because one happens before or after the other.

Data nodes are passive endpoints. An edge that reads or writes a persisted artifact starts from the module that performs the access; two data nodes are never connected directly. When one artifact's content changes another — index repair from an existing report, path reconciliation from verified files, claim finalization into delivery state — name the module that performs the read and write and draw the edge from it. Inside the data module's drill-down that module renders as a dashed external context node, which is exactly the information the reader needs: who touches the data, and with what effect. Target the data module's root rather than individual files unless the file-level target is itself reader-relevant (a fixed-path access, a bypass, or an artifact only one actor writes); several per-file edges otherwise multiply dashed context nodes in every other module's drill-down.

Use five information levels so the reader can stop when they have enough detail:

- **L0:** one-sentence system thesis in the report summary;
- **L1:** top-level overview concepts and primary edges;
- **L2:** drill-down components and their local hand-offs;
- **L3:** cross-cutting tables and ordered scenarios;
- **L4:** project-relative evidence anchors.

The main canvas renders the L1 shape and edge labels only; L2–L4 (drill-down components, cross-cutting tables and scenarios, evidence anchors) are progressive disclosure — reached through the detail panel, drill-down, or sections — and are never required to read the map (strict detail exclusion).

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

### Write for comprehension

Assume the reader understands software engineering but not this repository. Start each module detail with its responsibility and boundary, then explain the concrete flow and only then name implementation details.

Use these sentence tests:

- **Actor:** Who starts or owns the action?
- **Action:** What does it do?
- **Object:** What input, state, file, request, or artifact does it affect?
- **Outcome:** What becomes observable or durable?

If a sentence cannot answer at least the first three, it is likely an abstract noun stack. Rewrite “delivery state and claim coordination” as “Before sending a digest, the delivery service creates a claim in `delivery-state.json`; another host that sees the claim does not send the same digest.”

Treat template phrases as a warning sign, especially “This module is mainly responsible for…”, “The system implements this through…”, “provides unified capability”, and “completes lifecycle management”. Keep one only when the rest of the sentence immediately supplies a specific actor, action, object, and outcome.

Keep a necessary technical term when replacing it would reduce precision, but define it through behavior on first use. Do not soften exact behavior with casual metaphors. Do not make the reader decode abbreviations, package names, or class names before understanding the responsibility.

Translate exact internal states into consequences on first use. For example, write “结果未知（`ambiguous`），所以系统阻止自动重发” and “尽力追加的历史；写失败不会撤销日报完成状态” rather than assuming status names or `best-effort` explain themselves.

Prefer:

```text
The daily pipeline writes the Markdown report first. It then updates generated references in `papers.json`; reading status and priority in the same file remain user-owned state.
```

Avoid:

```text
The persistence layer provides unified durable-commit and projection lifecycle capabilities.
```

### Calibrate claim scope

State the smallest runtime boundary the evidence proves: instance; request or job; key or tenant; process or worker; host or replica; service; deployment; environment.

Do not turn a verified local boundary into a repository-wide guarantee:

- a process-local or per-key lock does not prove cross-worker atomicity;
- shared storage does not by itself prove transactional quota enforcement;
- one middleware, route group, adapter, or entry does not prove all requests or all I/O use it;
- a streaming flag does not prove end-to-end incremental delivery;
- one package or root workspace does not define every component's language or runtime.

Avoid `all`, `every`, `always`, `never`, `global`, `fully`, `strict`, `end-to-end`, `supported`, and `compatible` unless all relevant entries, alternate paths, and topology boundaries were checked. Qualify the component, key, process, host, service, or environment instead.

## Reader-facing section mechanics

Each section's first block must be one short takeaway paragraph that answers its reader question, then use the block type that matches the relationship:

| Reader need | Block | Required content |
| --- | --- | --- |
| Understand a subsection | `heading` | A concrete question or mechanism name |
| Follow execution order | `steps` | Trigger, ordered actions, durable/external result |
| Compare repeated fields | `table` | Explicit columns and one subject per row |
| Understand one consequence | `p` | One idea, named actor, concrete outcome |
| Record a short unordered set | `bullets` | Parallel items with the same grammatical shape |
| Locate implementation | `anchors` | Project-relative file and stable symbol |

Use the five section questions from `SKILL.md` as both the completeness check and the section titles: localize them to the project's language and terms, but do not substitute a parallel category such as "key mechanisms" for Key Execution Flows. Omit a section or subsection that has no material verified answer.

Avoid a section made of one long paragraph or a flat list of unrelated mechanisms. Split it by reader question. Keep a table cell or step focused on one fact cluster; move low-level constants to module notes or evidence unless they change how the system behaves.

Default to this sequence when the topic permits it: direct answer paragraph → comparison table or ordered steps → important exception/recovery table → evidence anchors. Bullets are for a short parallel set, not for dumping every discovered fact.

## Authoring the data block

The whole report content is one JSON object inside the `<script type="application/json" id="report-data">` block. Everything outside that block is fixed template code: never hand-edit it while creating or editing a project report. Template bugs are fixed in `templates/architecture-map.html`, then propagated with `scripts/refresh-template.mjs`.

### Renderer shell and interaction contract

- The shell carries `<meta name="architecture-map-template-version" ...>` and works offline without external assets.
- The shell's UI strings (breadcrumb, layer legend, detail panel headings, toolbar, hints) are fixed Chinese and part of the versioned template. Their language is not a `report-data` field and is not edited per project; `report-data` follows the project's working language, so a Chinese project yields a uniformly Chinese report.
- Users can drag nodes, drag empty canvas to pan, zoom with the wheel/buttons, fit the current diagram, and reset node positions. Dragged positions are view-local and last for the current open-file session.
- Opening the detail drawer reserves diagram space and triggers a re-fit; on narrow viewports it becomes a bottom sheet. Section tabs remain horizontally reachable instead of being clipped.
- The renderer uses layered ordering plus obstacle-aware orthogonal routing. A route that cannot clear nodes is marked as failed rather than silently presented as a clean normal edge.
- Edge labels are assigned non-overlapping positions when possible. A label with no clear slot stays available through the edge title/hover state instead of covering another label or node.
- Run `node <skill-dir>/scripts/refresh-template.mjs --check <report>` to compare the complete shell; the script locates its template relative to its own path, so the working directory only affects how `<report>` is resolved. Exit `0` / `current` means no migration is needed; exit `1` / `stale` means rerun without `--check`. The refresh parses (JSON-validates) and preserves the existing `report-data` block exactly — structural validation is the separate `--validate` mode — uses an atomic same-directory replacement, detects concurrent edits best-effort (it re-reads and compares the report before the rename; a writer landing between that compare and the rename is not caught), and refuses to downgrade a report whose template version is newer than the installed shell.
- Run `node <skill-dir>/scripts/refresh-template.mjs --validate <report>` to machine-check the structural invariants of the data block: field whitelists at every level, unique ids, `parent` references, three-level depth, required layer and edge-kind values, self-edges, data-to-data edges, unique section titles that do not use the reserved `架构` diagram-tab title, and empty or ragged section blocks. Exit `0` prints `valid`; exit `2` lists every problem found. Fix all of them before finishing a run.

### Visual language contract

The rendered report distinguishes node types, boundaries, edge roles, and emphasis with cues that never rely on color alone:

- **Node types** — layers differ by stroke color, legend label, and the detail-panel layer badge; a node that owns a drill-down also carries a `+N` drill-down badge and is reachable through the breadcrumb path.
- **Boundary hierarchy** — top-level nodes are the system's boundaries; entering a drill-down renders the parent as a boundary entry node and cross-boundary endpoints as dashed external context nodes with reduced fill, so boundary membership is readable without decoding colors; the current view's place is always identifiable from the breadcrumb.
- **Edge emphasis (primary-versus-secondary)** — primary flows render solid with a direction arrow; secondary dependencies render dashed; aggregated mixed relationships use a distinct dash pattern. Emphasis raises stroke width and opacity in addition to switching hue, so hover, focus, and critical-path emphasis stay visible without color.
- **Focus and critical path** — selecting a node keeps the node, its directly connected upstream and downstream nodes, and their edges emphasized while unrelated nodes and edges dim (focus dimming); search filtering dims non-matching material the same way. The connected subgraph is the minimum focus scope; continuing that scope along flow edges toward the durable result or external effect defines the **critical path**, which receives the strongest emphasis and must end at a visible boundary, data, or external node.
- **Legend** — the legend lists every layer actually used in the report, so the map is decodable without hovering or color memory.

### Visual acceptance checks

Acceptance separates three validity axes; none substitutes for another:

- **Structural validity** — the `--validate` machine checks of the data block;
- **Visual readability** — the rendered views pass the overlap, clipping, route, readability, interaction, and theme gates below;
- **Evidence validity** — every material claim passes the evidence gates. A readable diagram does not prove an architecture claim, and a verified claim does not excuse an unreadable view; a structural audit is not a visual review and vice versa.

Automated review gates (run on a rendered report file; they never require Chrome or any external asset for generation):

- **Overlap** — no node overlaps another node and visible edge labels do not overlap labels or nodes;
- **Clipping** — node labels, summaries, and edge labels are not clipped out of the view at fit zoom, and truncated wording still exposes the full text on hover or in the detail panel;
- **Routes** — every rendered view has no `route-failed` marker and no proper non-endpoint edge crossing;
- **Readability** — labels hidden until hover are exceptional, the primary path is visually dominant at fit zoom, and the overview stays within its roughly 8–15 core-node default;
- **Interaction** — node drag, canvas pan, wheel/zoom, fit/reset, search, drill-down, breadcrumb, and panel behavior work without console errors;
- **Theme** — where the shell supports light/dark presentation, key views render readably in both themes.

Browser review gates (human step for every report, at desktop and narrow widths): open the offline file directly in the browser, exercise the interaction list above, read the overview at fit zoom in each supported theme, and confirm no console errors or `route-failed` markers; on narrow viewports confirm the bottom-sheet panel and horizontally scrollable tabs remain usable.

These gates run at review time, not at report generation.

### Schema semantics

- `title` / `summary` — project name and a one-sentence system overview shown in the header.
- `modules` — one entry per module. `parent` builds the tree; modules without `parent` (or with an unknown parent) render at the top level. Maximum depth is three levels (system → module → component); deeper content belongs in `detail` / `notes` text.
- `layer` — one of `entry`, `core`, `data`, `infra`, `external`, `frontend`, chosen for the module's role in this project. The template colors nodes by layer and renders a legend.
- `summary` — one short line rendered under the node label; keep it short enough to fit a narrow node (roughly ten to fourteen CJK characters) — longer wording is truncated with an ellipsis on the node, and the full line stays readable in the detail panel; it states the node's responsibility in this system, not an enumeration of its children or a technology list.
- `detail` — the canonical 2-4 sentence explanation; `notes` — non-obvious mechanisms, one per bullet; `evidence` — project-relative anchors supporting the claims.
- `edges` — `from` / `to` reference module ids at any depth. The template lifts edges automatically: an edge between deep components renders at the overview as an edge between their top-level ancestors, and exactly inside the relevant sub-diagram. When several deep relationships lift to the same visible endpoints, the renderer aggregates their count and distinct labels so the overview does not misrepresent the first edge as the only relationship. When one endpoint lies outside the drilled-in module, it renders as a dashed external context node; the drilled-in module itself renders as a boundary entry node when edges touch it. `kind` is `flow` (invocation or data flow, solid) or `dep` (dependency or deployment relation, dashed); `label` is short and optional.
- `sections` — optional tabs for cross-cutting content. Blocks are `p` (paragraph), `heading` (`text`), `steps` (`items`, rendered as an ordered list), `table` (`columns` and `rows`), `bullets` (`items`), `code` (`text`), or `anchors` (`items`). Omit empty sections.

After edge lifting, review the rendered overview rather than only the raw arrays. The overview default is a sparse high-level map of roughly 8–15 core nodes with at most about 12 lifted overview edges; the upper edge of the range is a readability review trigger, not a schema limit. If the overview is denser, group only by verified architecture boundaries (runtime, product, deployable unit, host/core, data ownership, or external trust boundary) and move components into drill-down. Do not omit a material relationship or invent a container to satisfy the target.

### Validation before writing

- the block is valid JSON: no comments, no trailing commas, `"` and `\` escaped, any literal `</script>` written as `<\/script>`;
- module ids are unique; every `parent` references an existing module; no module is deeper than three levels;
- every `layer` is one of the six defined values;
- every edge references existing module ids, has `kind` `flow` or `dep`, and never starts and ends at the same module;
- every module owns behavior or a durable artifact with a named writer; no module exists solely to carry a value between two other modules;
- no edge connects two data nodes, and every edge that reads or writes a data node starts from the module that performs the access;
- no node is a value object, a hosted instance of a service owned elsewhere, or a subcommand/installer feature; each such fact has a canonical home in a host's `detail`/`notes` or in a section;
- data edges target the data module's root unless the file-level target is itself reader-relevant;
- every module is reachable from the top level through `parent` links (no orphan subtrees);
- summaries are one line; anchors use project-relative paths and support the nearby statement;
- the report contains no empty `sections` entries and no unused schema fields.
- section titles are unique after trimming surrounding whitespace and never use the reserved `架构` diagram-tab title;
- every `heading` and `p` has non-empty `text`; every `steps` / `bullets` / `anchors` block has non-empty `items`; every `table` has non-empty `columns`, at least one row, and the same number of cells in each row;
- the overview passes the package-name removal and golden-path narration checks;
- the overview passes the runtime-unit and governance-separation checks;
- every drill-down has a stated main spine, no isolated reader-relevant node (except a structural container whose children carry its relationships), and no helper-edge fan-out obscuring that spine;
- every Host passes the entry-to-use-case traceability check without one arrow per command or screen;
- the report contains a system thesis and two to four verified primary scenarios with trigger, ordered steps, effect, and meaningful failure/alternate path;
- every edge is supported by separately verified endpoints and a real hand-off;
- mixed stores classify user-owned and generated fields separately rather than overgeneralizing rebuildability;
- idempotency/claim keys use the exact verified inputs and state their process/host scope;
- process-local locks are not described as cross-process convergence or conflict resolution;
- CLI edges and runtime claims are scoped to the subcommands that actually build or invoke the runtime;
- caches, checkpoints, claims, authoritative state, and export/import archives are distinguished, including verified sensitivity and path/permission checks;
- every section starts with a takeaway `p` block before tables, steps, bullets, code, or anchors;
- the overview stays on the roughly 8–15 core-node default and reads without detail, notes, or evidence text (strict detail exclusion); facts past L1 are placed in the detail panel, drill-down, or sections (progressive disclosure placement);
- overview edges were chosen by primary-flow selection so the main path is narratable from visible nodes and labels;
- section prose uses named actors and concrete outcomes rather than package inventories or noun-stack summaries;
- visible labels lead with reader concepts, and exact states or jargon are immediately paired with their concrete consequence;
- the rendered overview has no route-failure markers; any labels hidden until hover are understood and the module tree is reconsidered when hiding is widespread;
- every rendered drill-down has no route-failure marker or proper non-endpoint edge crossing; hidden labels remain exceptional.
- after substituting the data block into the current template, `--validate` prints `valid` and `--check` returns `current`.

The renderer does not enforce this checklist. Violations are silently contained: an unknown `layer` renders in the core color, an unknown edge `kind` renders as `flow`, duplicate module ids warn on the console with later entries ignored, and an unknown `parent` renders at the top level. The `--validate` mode covers the mechanically decidable structural items; everything else in the checklist is authoring discipline, not a runtime guarantee.

## Mode mechanics

### `init`

1. Resolve the report path and confirm no established report should be preserved elsewhere.
2. Establish the full repository/runtime topology before generalizing from any primary package.
3. Close active wiring for the material runtime flows and apply semantic proof gates.
4. Build the private system brief and derive reader-facing concepts before naming modules or sections.
5. Copy the current `templates/architecture-map.html` to the report path and replace only the content of the `report-data` block with the generated JSON.
6. Write only verified, applicable modules, edges, and sections; do not hand-edit anything outside the data block.
7. Run `node <skill-dir>/scripts/refresh-template.mjs --validate <report>`, then the package-name removal, golden-path narration, section-question, and writing checks, before accepting the report.

If a report already exists, follow `audit` instead.

### `update`

1. Require an existing report; when none exists, fall back to `init` unless the user explicitly insists on `update` semantics for an established report.
2. Confirm the accepted scope is specific enough to investigate; use Git diff/status only for discovery.
3. Trace each affected implementation to its current boundaries.
4. Determine impact by comparing verified current implementation to the report's `report-data` block — do not accept another agent's impact guess.
5. Prepare a coherent data-block edit: rewrite, add, move, or delete only the affected module entries, edges, and section blocks, including deletion of stale statements.
6. Validate the edited data block with `<skill-dir>/scripts/refresh-template.mjs --validate`; then check the renderer shell with `<skill-dir>/scripts/refresh-template.mjs --check` and refresh it when stale, after preserving the validated data block.
7. If no report statement needs to change within the implementation scope examined and the shell is already current, return scoped `no-impact`; do not imply that unrelated report sections were audited. A shell-only refresh is `updated` and its summary must say that report claims were unchanged.

### `audit`

1. Require an existing report; when none exists, fall back to `init` unless the user explicitly insists on `audit` semantics for an established report.
2. Establish the current system shape independently of the report.
3. Rebuild the private system brief and compare it with the report's concepts, grouping, and golden paths.
4. Verify every material claim and useful implementation anchor in the `report-data` block.
5. Check important current implementation areas for omissions.
6. Reconcile factual drift, misleading grouping, package-inventory structure, and abstract prose in place, editing only the `report-data` block.
7. Validate the reconciled data block with `<skill-dir>/scripts/refresh-template.mjs --validate`; check and refresh the renderer shell with `<skill-dir>/scripts/refresh-template.mjs` when stale.
8. Run the content-boundary checklist below.

## Content-boundary checklist

Before finishing, confirm that:

- each material technical statement is supported by production source or executable configuration;
- tests are not the sole support for a production behavior claim;
- the report does not rely on README, docs, ADR, Helm, comments, prompts, or plans as implementation proof;
- active claims close the production loop from executable entry through selected wiring and actual arguments to effect;
- cross-component claims verify both producer/caller and consumer/callee contracts;
- strong semantics pass their data, concurrency, topology, and counter-evidence gates;
- exact idempotency key inputs, lock scope, ordinary storage checks, and stronger exclusive/recovery checks are not conflated;
- fallback, bypass, rejection, buffering, and degraded paths that narrow claims were checked;
- claim quantifiers match the proved instance/process/worker/replica/service/environment scope;
- dependencies described as active have verified wiring and responsibility;
- removed modules, stale interfaces, obsolete configuration, and broken anchors are absent;
- each mechanism has one canonical detailed explanation and the overview diagram stays compact;
- top-level nodes are reader-facing architecture concepts rather than a copy of the package tree;
- a new maintainer can narrate each golden path using the visible overview nodes and edge labels;
- section structure answers the five reader questions and uses tables or steps where they clarify repeated fields or sequence;
- prose names actors, actions, objects, and outcomes; abstract noun stacks and vague capability claims are absent;
- every prohibition in the SKILL.md Content contract is absent — no transition or “this change” narrative, no rationale or decision trade-offs, no prompt, plan, Helm process, command output, or test-run results, no changelogs, roadmaps, TODOs, risks, or follow-ups;
- non-blocking uncertainty is excluded from report claims and appears only in the optional operation-result `unverified` field;
- every gate in “Validation before writing” holds, including `--validate` printing `valid` and `--check` returning `current` after substituting the data block into the current template;
- the rendered overview has no route-failure marker and remains compact enough for selective intake; density thresholds never caused evidence or material flows to be omitted.

## Blocking rule

Return `blocked` when a trustworthy result cannot be produced, for example:

- the project root, report path, or requested baseline cannot be determined safely;
- a central requested claim cannot be verified from accessible implementation evidence;
- the accepted change scope is mixed with unrelated changes and cannot be isolated;
- completing the requested reconciliation would require guessing external or deployed behavior;
- the report cannot be edited safely.

Investigate and draft before writing. If a blocker prevents a coherent update, leave the report unchanged. State the blocker in the operation result, not in the report.

In a scoped `update`, an important adjacent uncertainty outside the accepted scope may be excluded from report claims and verified `scope`, then returned as `unverified`. In full `init` / `audit`, material uncertainty about an existing claim or important omission requires `blocked`; `unverified` is allowed only for a boundary explicitly outside the report baseline or stated scope. Do not use it to hide an unproved central semantic, make `no-impact` cover an unchecked area, or create a partial report that should have been `blocked`.
