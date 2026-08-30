---
name: architecture-map
description: 'Create, update, and audit a repository architecture map report that explains the verified current implementation as an interactive single-file HTML report with drill-down diagrams. Use when the user asks for a technical report, implementation report, or current-state architecture / technology documentation, to synchronize technical documentation after accepted code changes, or mentions architecture-map, 架构地图, 架构报告, 技术报告, 开发报告, 更新技术报告, or 审计技术报告. Not for changelogs, decision rationale, plans, prompts, execution logs, or forward-looking architecture design.'
install-targets: claude
---

# Architecture Map

Maintain a clear, code-evidenced, interactive explanation of how the project **currently works**.

The report is a current-state implementation reference, not a history of how the project arrived there. Explain the actual technology, architecture, wiring, flows, and key mechanisms. Do not narrate the change that prompted the update.

## Reader contract

Write for an experienced maintainer who is new to the repository. Transform the source in this order: **evidence → architecture model → explanation → rendering**. Do not jump directly from files and symbols to diagram nodes or prose.

The report must support two reading depths:

- a **five-minute overview** explains what runs, where the main boundaries are, which use cases matter, where state lives, and how the primary flow reaches an external effect;
- a **twenty-minute trace** lets the reader follow a major use case through its host, core logic, ports/adapters, state changes, failures, and evidence anchors.

Optimize for understanding by a reader who does not already know the package names. Preserve technical precision, but make responsibility, control flow, ownership, and failure outcomes explicit.

## Report format

The report is one self-contained HTML file with no external dependencies; open it directly in a browser. It presents:

- an overview architecture diagram: one node per reader-facing architecture concept, not per package or directory, each with a one-line responsibility;
- drill-down: clicking a module that has sub-modules enters its sub-diagram; a breadcrumb shows the path and navigates back level by level;
- a detail panel: clicking a node shows its explanation, mechanisms, and code evidence anchors; the diagram re-fits into the remaining space, and narrow viewports use a bottom sheet instead of covering the graph;
- a full-canvas interaction model: drag nodes, drag empty canvas to pan, use wheel/buttons to zoom, and use fit/reset controls; node positions persist while the file stays open and are kept separately per drill-down view;
- layered color coding with a legend, obstacle-aware orthogonal dependency/data-flow edges, collision-managed labels, search filtering, and selection highlighting;
- structured text sections as tabs for cross-cutting topics that do not map to a single node: runtime and technologies, data and state, key execution flows, build/test/delivery, and security/failure behavior.

The file separates data from presentation. The `<script type="application/json" id="report-data">` block holds the entire report content as one JSON object; everything else is the versioned shell from `templates/architecture-map.html`, identified by the `architecture-map-template-version` meta tag. Content authoring edits only `report-data`; template fixes are made in the shared template and propagated with `scripts/refresh-template.mjs`, which preserves the report data block exactly and refuses to replace a report created by a newer template version.

The shell's interface language is fixed Chinese (breadcrumb, layer legend, detail panel headings, toolbar, and hints); it is template code, not `report-data`, and is never translated or hand-edited inside a project report. Report content is written in the project's working language — for a Chinese repository the whole report, shell included, reads as Chinese.

### Data schema

```json
{
  "title": "project name",
  "summary": "one-sentence system overview",
  "modules": [
    {
      "id": "unique-id",
      "label": "short module name",
      "parent": "parent module id (omit for top-level modules)",
      "layer": "entry | core | data | infra | external | frontend",
      "summary": "one-line responsibility, rendered under the node label",
      "detail": "canonical explanation, 2-4 sentences",
      "notes": ["non-obvious mechanism, one per bullet"],
      "evidence": ["path/to/file.ext (StableSymbol)"]
    }
  ],
  "edges": [
    { "from": "module id", "to": "module id", "label": "short edge label (optional)", "kind": "flow | dep" }
  ],
  "sections": [
    { "title": "Runtime and Technologies", "blocks": [
      { "type": "p", "text": "paragraph" },
      { "type": "heading", "text": "subsection heading" },
      { "type": "steps", "items": ["first concrete step", "next concrete step"] },
      { "type": "table", "columns": ["field", "meaning"], "rows": [["value", "explanation"]] },
      { "type": "bullets", "items": ["item"] },
      { "type": "code", "text": "command or config" },
      { "type": "anchors", "items": ["path/to/file.ext (Symbol)"] }
    ] }
  ]
}
```

Authoring rules:

- The `modules` array forms a tree through `parent`; top-level modules omit it. Maximum depth is three levels: system → module → component. Deeper detail belongs in `detail` / `notes` text.
- `id` values are unique, short, lowercase; dots may mirror the hierarchy but `parent` defines it.
- `layer` takes one of the six values above; the template defines node colors and a legend for them. Assign the layer that best describes the module's role in this project.
- A node owns behavior or a durable artifact with a named writer; REFERENCE.md (Architecture synthesis mechanics) defines the three shapes that are not nodes — value objects/DTOs, services hosted in a process they do not own, and operational subcommands — and where each of those facts has its canonical home.
- `detail` holds the canonical explanation, `notes` the non-obvious mechanisms; one fact has one canonical home (REFERENCE.md, "Reconcile in place").
- Every material claim carries evidence anchors in `evidence` or an `anchors` block, project-relative `path/to/file.ext (StableSymbol)` form. The anchor symbol must be the exact symbol the nearby statement names or directly invokes — not a wrapper or callee one level deeper — and anchors never use machine-specific absolute paths.
- Edges may connect modules at any depth; the template lifts, aggregates, and renders them (dashed external context, boundary entry node). See REFERENCE.md (Schema semantics) for the full lifting rules.
- Data and state nodes are passive: the actor performs the access, and two data nodes are never connected directly. See REFERENCE.md (Schema semantics) for the root-versus-file targeting rule.
- Treat roughly 5–8 top-level nodes and at most about 12 lifted overview edges as a readability review threshold, not a schema limit. When the rendered overview exceeds it, group modules only along verified runtime, product, deployable-unit, host/core, data-ownership, or external-system boundaries and push detail into drill-down. Never invent a boundary, omit a material flow, or weaken evidence merely to hit the threshold.
- `sections` holds only applicable topics with substantive current-state content; omit empty sections. Section titles are the reader questions themselves, localized; do not invent parallel categories — ordered execution paths belong under Key Execution Flows, not a "key mechanisms" section. Use `heading` to separate questions, `steps` for ordered execution paths, and `table` for repeated fields such as runtime units, data ownership, build artifacts, or failure handling.
- The `report-data` block must be valid JSON: no comments, no trailing commas, `"` and `\` escaped, and any literal `</script>` inside a string written as `<\/script>`.

## Architecture synthesis

Build the architecture model before authoring `modules` or `edges`:

First write a private **system thesis** in this shape: **trigger → runtime unit → core use case → durable state or external effect → user-visible result**. Then select two to four primary scenarios; each scenario must name its trigger, ordered actions, result, and the failure or alternate path that changes its meaning.

1. Identify the **runtime and composition roots**: processes, plugin hosts, workers, CLIs, services, extensions, and the code that wires each one.
2. Identify the **core use cases** a maintainer would name when explaining what the product does. Separate scheduled, manual, interactive, background, and delivery flows when they have different callers or effects.
3. Identify ports and adapters. Show where host-specific APIs stop and host-neutral logic begins; do not flatten a host, adapter, core service, and external provider into peers merely because they occupy separate folders.
4. Identify data ownership: authoritative records and rebuildable projections, configuration, checkpoints, run history, claims/locks, caches, and external state. Record who writes each item and who reads it. If one file mixes user-owned state with generated fields, classify the fields separately; never label the whole file as a projection merely because some fields can be repaired.
5. Identify external systems and trust boundaries, including an intermediary service that ultimately calls another provider.
6. Trace one to three **golden paths** from a real entry point to a durable result or external effect, including the ownership hand-off between components.
7. Write a one-sentence system story, then choose top-level concepts that let a new maintainer tell that story without package names. Put implementation components underneath those concepts.

Keep caches, checkpoints, authoritative state, claims, history, and export/import archives as separate data categories, and trace export and import as separate command paths (REFERENCE.md, Architecture synthesis mechanics, for the per-field and per-check rules).

Do not use the package tree as the overview architecture. A package, directory, class, or service becomes a top-level node only when it is itself a reader-relevant runtime, ownership, product, or trust boundary. The overview is the system map; drill-downs hold implementation structure.

Keep runtime architecture separate from engineering governance. Build workflows, release groups, registries, and test commands belong in the build/test/delivery section unless they are themselves invoked by the runtime path. A shared library is not a process, and an independently built package is not automatically a peer runtime node.

Synthesis may connect only relationships whose endpoints and hand-off were separately verified. Do not invent an architectural edge to make the story cleaner; temporal facts belong in `steps` or failure tables unless a concrete data or control hand-off crosses the edge (REFERENCE.md, Architecture synthesis mechanics).

Run a **main-spine pass** on the overview and every drill-down before accepting the graph:

- Write the one sentence that the current view must make visible: who starts the work, which use case owns it, where the durable result lands, and which external effect may follow.
- Keep the edges required to narrate that sentence. Move helper calls, repeated provider calls, cleanup order, and secondary ownership facts into module details, ordered steps, or comparison tables.
- Preserve Host-to-use-case traceability without drawing a fan-out from every command or screen. Prefer one Host composition/port relation plus at most one aggregated use-case trigger relation; enumerate the concrete Scheduler, manual, reading, and delivery mappings in the Host detail and flow steps.
- When control and data travel separately, label them separately. For example, “completed 后触发投递” is a control edge while “可选 Digest 数据” is a payload edge; never let two arrows look like two independent triggers.
- Treat roughly 8–16 visible nodes and about 15 rendered edges in a drill-down as a readability review trigger, not a schema limit. A reader-relevant node must not be isolated unless it is a structural container whose children carry all of its relationships, and a material hand-off must not be deleted merely to hit the number.
- When a drill-down's external-context fan-out pushes it past that trigger, consolidate per-file or per-artifact edges onto the data or boundary root node and keep the file-level mapping in the root's detail; prefer fewer dashed context nodes over maximal endpoint precision.

Accept a rendered view only when its primary path is visually dominant, it has no route-failure marker or proper non-endpoint edge crossing, and labels hidden until hover are exceptional rather than the normal way to read the graph. Fix the module tree, edge selection, labels, or ordering when these checks fail.

## Reader-facing writing

Use direct subject–verb–object sentences: name the caller or owner, the action it performs, the object it changes, and the observable result. Avoid noun-stack summaries such as “index, checkpoint, operation and scheduling” or labels that merely list technologies.

- Lead visible labels and headings with the reader-facing concept; put package names, class names, and exact implementation terms in `detail` or evidence after the responsibility is clear. Prefer “插件组装入口” over an unexplained “Composition root”.
- Introduce a technical term only when it distinguishes real behavior, then explain what it means here. For example, explain that a “projection” is a file that can be rebuilt from the authoritative report rather than assuming the reader knows the term.
- When an exact state or mechanism name matters, pair it with its consequence (see REFERENCE.md, “Write for comprehension”, for the `ambiguous` example), not a row made only of status names.
- Prefer “The scheduler writes run-state after the pipeline finishes” over “run-state lifecycle management”.
- Prefer one idea per sentence and one question per paragraph. Split repeated comparisons into a table and execution order into steps.
- Open each section with the direct answer to its reader question, then use `table` or `steps` for the detail. Do not make a flat bullet inventory the primary explanation.
- Make table columns answer concrete questions such as “谁启动 / 做什么 / 写到哪里 / 失败后怎样”. A row that only names abstractions, technologies, or mechanisms must be rewritten until a reader can predict the observable result.
- Avoid vague verbs and adjectives such as “supports”, “provides capability”, “unified”, “complete”, “robust”, or “flexible” unless the sentence immediately states the concrete mechanism and scope; treat template-like openings (REFERENCE.md, “Write for comprehension”) the same way.
- Keep exact identifiers, filenames, commands, and limits where they help the reader trace the implementation; do not turn them into an unstructured inventory.
- Keep audit narration out of reader-facing sections. Do not say that a README is stale, a claim was corrected, or an agent checked a contract; state the current executable boundary and any uncovered compatibility risk directly.

Structure the overview and sections around six reader questions. The first (Overview) is answered by the diagram itself; the remaining five become the section tabs:

- **Overview — What is the system shape and primary path?** Separate runtime/host, shared core, data ownership, independent integration, and external trust boundaries, then make the main trigger-to-effect path narratable from the visible graph.
- **Runtime and Technologies — What actually runs?** Name each runtime unit, how it starts, what technology owns its boundary, and what it calls. State explicitly when a shared core library is not a separate process.
- **Data and State — Who writes it, who reads it, and can it be rebuilt?** Distinguish configuration, authoritative output, rebuildable projection, checkpoint, cache, lock/claim, and history.
- **Key Execution Flows — What starts the flow, what happens in order, and what is produced?** Use ordered steps for the main success path and short decision tables for important alternate or recovery paths.
- **Build, Test, and Delivery — What is built, checked, published, or deployed?** Connect each command or workflow to a concrete artifact and destination.
- **Security and Failure Behavior — What is trusted, rejected, retried, degraded, or exposed to the user?** Name the boundary, enforcement point, fallback, and visible outcome.

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

## Implementation-proof gate

A capability is not current behavior until the selected production path actually reaches and uses it. Before writing a material active-behavior claim, close the full evidence loop: executable entry → registration / composition → selected configuration or provider → concrete caller with actual arguments → concrete callee / host adapter → state, output, or external effect (REFERENCE.md, "Production source and runtime wiring", gates every hop).

A dependency, symbol, interface, helper, flag, environment-variable resolver, provider, test, or request option proves only that a capability exists. It does not prove that a current production path selects or invokes it. Ordinary declared/configurable capabilities that are not selected should stay out of the report. Mention one in operation evidence only when it directly explains a corrected claim, scoped `no-impact`, or blocker; otherwise omit it there too. Include non-use in the report only when it creates a material current behavior or user-facing limitation.

For cross-component behavior, verify both sides of the current contract. For strong semantics such as streaming, atomicity, idempotency, timeout, cancellation, secrets, global coverage, compatibility, or deployment status, also verify runtime scope and the nearest rejection, fallback, bypass, buffering, or degraded path that could narrow the claim. Report wording must not be stronger or broader than this evidence.

Treat key derivation and lock scope as implementation facts, not implied semantics: inspect the exact idempotency/claim key inputs (do not add channel, provider, tenant, or date dimensions merely because state records those fields), and describe a process-local lock only as process-local. Do not claim that concurrent hosts eventually converge unless a shared atomic primitive and its conflict behavior are verified.

Trace command families separately. A CLI command parser or runtime builder does not prove that every subcommand constructs the same runtime; follow each subcommand until it returns directly, builds a runtime, or invokes an external process.

Existing documentation can help locate code or supply canonical domain terms, but it is not proof of implementation. Verify technical claims in production source code and executable configuration. Read `REFERENCE.md` before investigating or editing; it defines capability proof levels and semantic proof gates.

## Project artifact

Default path:

```text
<project-root>/docs/architecture-map.html
```

Use a user-specified path when provided. If an existing report uses another clearly established path, keep that path rather than creating a duplicate.

Supporting files live next to this `SKILL.md`:

- `REFERENCE.md` — evidence, investigation, update, and audit mechanics;
- `templates/architecture-map.html` — the fixed HTML template whose `report-data` block is filled per report.
- `scripts/refresh-template.mjs` — checks the shell (`--check`), machine-validates the `report-data` block (`--validate`), or refreshes an existing report shell while preserving that block exactly.

## Modes

Infer the mode from the request and repository state. Resolve a missing report deterministically:

- explicit `init`, an unspecified first request, or the first Helm synchronization after the user enables architecture-map maintenance → `init`, even when an accepted change scope is available;
- an `update` or `audit` request when no report exists → `init`: a maintenance intent without a report means establishing one;
- explicit `update` or `audit` that expects an already established report → `blocked` with a recommendation to run `init`.

After initialization, accepted changes use `update`; accuracy checks use `audit`.

### `init`

Use when no report exists or the user asks to establish one.

1. Establish the repository and runtime topology: independent packages and deployable units, executable and composition roots, process / worker / replica boundaries, local versus shared state, and important cross-component communication.
2. Trace important implementation paths through the active evidence loop rather than generalize from the root manifest or primary package.
3. Build the private system brief and architecture model: runtime units, core use cases, ports/adapters, data ownership, trust boundaries, and golden paths.
4. Compose the reader-facing `report-data` object from that model and the verified evidence; do not expose the discovery order or package tree as the explanation.
5. Copy the current `templates/architecture-map.html` to the report path and replace only the content of the `report-data` block with the generated JSON; the copied shell must carry the current template-version marker.
6. Include only applicable modules, edges, and sections with substantive current-state content.

If the report already exists, do not overwrite it from scratch. Treat `init` as a full `audit` so repeated initialization is safe.

### `update`

Use after an accepted implementation change or when the user gives a reliable change scope.

1. Use the accepted diff, changed paths, and task context only to locate the potentially affected implementation.
2. Close the active evidence loop for each affected area, including the actual arguments passed between concrete callers, callees, and host adapters. A diff alone is not sufficient evidence for the resulting description.
3. For cross-component behavior, verify the exact contract emitted and accepted on both sides.
4. Search for rejection, alternate-provider, fallback, bypass, buffering, and degraded paths that narrow the resulting claim.
5. Compare the verified current implementation with the existing report's `report-data` block.
6. Rewrite, add, move, or delete only the affected module entries, edges, and section blocks; write the edited JSON back into the `report-data` block without hand-editing the report shell.
7. Run `node <skill-dir>/scripts/refresh-template.mjs --validate <report>` and fix every reported structural problem in the data block. Then run the same script with `--check <report>`. When stale, run it without `--check` to replace the shell with the current template while preserving the just-verified data block. The script locates its template relative to its own path, so any working directory works; only `<report>` is resolved against the current directory.
8. Leave unrelated accurate entries untouched.

If no report exists, fall back to `init` per the mode resolution above; return `blocked` and recommend `init` only when the user explicitly insists on `update` semantics for an established report.

### `audit`

Use when the user asks whether the report is accurate, when the impact scope is unreliable, or when drift may extend beyond a known change.

1. Re-establish the project's repository/runtime topology and active implementation paths independently of the report.
2. Rebuild the private architecture model independently of the existing module tree and prose.
3. Verify every material report claim, implementation anchor, capability proof level, and claimed runtime scope.
4. Re-prove strong semantics and broad quantifiers against both sides of each contract and adverse paths.
5. Find important implemented areas the report omits and architecture concepts it groups misleadingly.
6. Remove stale, unsupported, over-broad, historical, rationale, prompt-derived, plan-derived, process-oriented, package-inventory, and noun-stack content.
7. Reconcile the `report-data` block in place. Do not append an audit section or audit history.
8. Check the data block with `node <skill-dir>/scripts/refresh-template.mjs --validate <report>` and the shell with `node <skill-dir>/scripts/refresh-template.mjs --check <report>`; refresh the shell when stale. Shell migration never substitutes for verifying report claims.

If no report exists, fall back to `init` per the mode resolution above; return `blocked` and recommend `init` only when the user explicitly insists on `audit` semantics for an established report.

## Workflow

1. Determine the project root, report path, mode, and implementation baseline. Default to the current working tree; honor an explicitly requested revision or environment.
2. Read applicable repository instructions. Read the current report's `report-data` block when it exists, and check whether its versioned shell matches the installed template.
3. Establish applicable repository/runtime topology, then discover executable and composition roots, selected providers, build/deployment definitions, and relevant cross-component boundaries.
4. Build the private system brief and architecture model before deciding module boundaries or section structure.
5. Trace material claims through active production wiring and both sides of any contract. Use tests to understand the verification surface, never as the sole proof of production behavior.
6. Build a private evidence map for each planned claim: evidence anchors, capability proof level, precise runtime scope, both contract sides where applicable, and nearest counter-evidence. Do not write investigation notes into the project.
7. Challenge strong semantics and broad quantifiers against fallback, bypass, rejection, buffering, and degraded paths. Narrow or omit claims whose semantics are not proved.
8. Check exact key derivation, process/host lock scope, command-specific runtime construction, and the separation of caches/checkpoints/authoritative state/export archives before writing strong claims or edges.
9. Draft the complete report edit, then run the package-name removal, golden-path narration, section-question, and subject–verb–object checks. If a central requested area cannot be verified, stop with `blocked` rather than leave speculative or half-reconciled content.
10. Create the report by copying the current template and filling the `report-data` block, or edit the existing data block in place and refresh a stale shell with `<skill-dir>/scripts/refresh-template.mjs`. Before finishing, run `node <skill-dir>/scripts/refresh-template.mjs --validate <report>` and fix every reported structural problem. Preserve accurate unaffected entries and the project's useful terminology; never hand-merge renderer code into a project report.
11. Re-read the resulting claims against implementation evidence, claimed scope, reader contract, canonical module/section placement, and the prohibited-content list.
12. Return exactly one result status.

## Result contract

Return a concise operation result outside the report:

```text
status: updated | no-impact | blocked
report: <report path>
scope: <verified implementation/report scope>
summary: <one-sentence result>
evidence: <concise list of implementation/configuration areas inspected>
```

When an important but non-blocking area could not be verified and was excluded from both the report and the verified `scope`, optionally add:

```text
unverified: <material uncertainty excluded from the report and verified scope>
```

Omit this field when empty; never emit `unverified: none`. It is operation metadata only and must not enter the architecture map report.

For `blocked`, also return:

```text
blocker: <what prevents a trustworthy report update>
```

Meanings:

- `updated` — the report was created, its verified content changed, or its stale template shell was refreshed;
- `no-impact` — the required investigation found no report-data change within the verified scope (`update`) or across the full report (`init` / `audit`), and the template shell was already current; it never claims that unexamined sections were audited;
- `blocked` — the requested synchronization cannot be completed reliably or safely.

For `update` + `no-impact`, `scope`, `summary`, and `evidence` must identify the accepted-change scope actually examined. Never state or imply that the report is accurate as a whole unless the run was a full `init` / `audit`. A `no-impact` scope cannot include an area listed as `unverified`.

`unverified` is not a fourth status and cannot conceal a central evidence gap. In a full `init` / `audit`, any uncertainty that prevents validating a material report claim or detecting an important omission requires `blocked`; optional `unverified` may only name something explicitly outside the report's stated baseline or scope. In scoped `update`, it may also name an adjacent non-blocking area excluded from both the edit and verified `scope`. If the requested report cannot be trustworthy without that area, return `blocked` instead.

Do not invent `created`, `partial`, or `success` statuses. A `blocked` run must not leave speculative or knowingly half-complete report edits.
