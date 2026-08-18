---
name: technical-report
description: 'Create, update, and audit a repository technical report that explains the verified current implementation as an interactive single-file HTML architecture report with drill-down diagrams. Use when the user asks for a technical report, implementation report, architecture or technology documentation, to synchronize technical documentation after accepted code changes, or mentions technical-report, 技术报告, 开发报告, 更新技术报告, or 审计技术报告. Not for changelogs, decision rationale, plans, prompts, or execution logs.'
install-targets: claude
---

# Technical Report

Maintain a clear, code-evidenced, interactive explanation of how the project **currently works**.

The report is a current-state implementation reference, not a history of how the project arrived there. Explain the actual technology, architecture, wiring, flows, and key mechanisms. Do not narrate the change that prompted the update.

## Report format

The report is one self-contained HTML file with no external dependencies; open it directly in a browser. It presents:

- an overview architecture diagram: one node per top-level module, each with a one-line summary;
- drill-down: clicking a module that has sub-modules enters its sub-diagram; a breadcrumb shows the path and navigates back level by level;
- a detail panel: clicking a node shows its explanation, mechanisms, and code evidence anchors;
- layered color coding with a legend, dependency/data-flow edges with labels, search filtering, and selection highlighting;
- optional text sections as tabs for cross-cutting topics that do not map to a single node: runtime and technologies, data and state, security and failure behavior, build and deployment.

The file separates data from presentation. The `<script type="application/json" id="report-data">` block holds the entire report content as one JSON object; everything else is fixed template code from `templates/technical-report.html`. Report generation copies the template and replaces only the content of the `report-data` block; it never modifies template code.

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
      { "type": "bullets", "items": ["item"] },
      { "type": "code", "text": "command or config" },
      { "type": "anchors", "items": ["path/to/file.ext (Symbol)"] }
    ] }
  ]
}
```

Authoring rules:

- The `modules` array forms a tree through `parent`. Top-level modules omit `parent`. Maximum depth is three levels: system → module → component. Deeper detail belongs in `detail` / `notes` text.
- `id` values are unique, short, lowercase; dots may mirror the hierarchy but `parent` defines it.
- `layer` takes one of the six values above; the template defines node colors and a legend for them. Assign the layer that best describes the module's role in this project.
- `summary` is one short line shown under the node label; keep it under roughly thirty characters.
- `detail` holds the canonical detailed explanation of the module; `notes` holds non-obvious mechanisms as short bullets. One fact has one canonical home: explain a mechanism in the owning module's `detail`/`notes`, or in a section when it crosses modules; elsewhere reference it briefly or not at all.
- Every material claim carries evidence anchors in `evidence` or in an `anchors` block: project-relative `path/to/file.ext (StableSymbol)` form, pointing at content that supports the nearby statement. No machine-specific absolute paths.
- Edges may connect modules at any depth. The template lifts them automatically: an edge between two deep components renders at the overview as an edge between their top-level ancestors, and exactly inside the relevant sub-diagram. When one endpoint lies outside the drilled-in module, it renders as a dashed external context node; the drilled-in module itself renders as a boundary entry node when edges touch it. `kind` is `flow` for invocation or data flow (solid line) and `dep` for dependency or deployment relation (dashed line). `label` is optional and short.
- `sections` holds only applicable topics with substantive current-state content; omit empty sections. Use a section for cross-cutting content (runtime/technology responsibilities, data and state, security and failure behavior, build/deployment) that does not belong to one module.
- The `report-data` block must be valid JSON: no comments, no trailing commas, `"` and `\` escaped, and any literal `</script>` inside a string written as `<\/script>`.

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

A capability is not current behavior until the selected production path actually reaches and uses it. Before writing a material active-behavior claim, close this evidence loop:

```text
executable entry
→ registration / composition
→ baseline-selected configuration or provider
→ concrete caller with actual arguments
→ concrete callee or host adapter
→ resulting state, output, or external effect
```

A dependency, symbol, interface, helper, flag, environment-variable resolver, provider, test, or request option proves only that a capability exists. It does not prove that a current production path selects or invokes it. Ordinary declared/configurable capabilities that are not selected should stay out of the report. Mention one in operation evidence only when it directly explains a corrected claim, scoped `no-impact`, or blocker; otherwise omit it there too. Include non-use in the report only when it creates a material current behavior or user-facing limitation.

For cross-component behavior, verify both sides of the current contract. For strong semantics such as streaming, atomicity, idempotency, timeout, cancellation, secrets, global coverage, compatibility, or deployment status, also verify runtime scope and the nearest rejection, fallback, bypass, buffering, or degraded path that could narrow the claim. Report wording must not be stronger or broader than this evidence.

Existing documentation can help locate code or supply canonical domain terms, but it is not proof of implementation. Verify technical claims in production source code and executable configuration. Read `REFERENCE.md` before investigating or editing; it defines capability proof levels and semantic proof gates.

## Project artifact

Default path:

```text
<project-root>/docs/technical-report.html
```

Use a user-specified path when provided. If an existing report uses another clearly established path, keep that path rather than creating a duplicate.

Supporting files live next to this `SKILL.md`:

- `REFERENCE.md` — evidence, investigation, update, and audit mechanics;
- `templates/technical-report.html` — the fixed HTML template whose `report-data` block is filled per report.

### Migration from a markdown report

If an established markdown report exists (`docs/technical-report.md` or a custom established path) and no HTML report exists, migrate on the next run: use the markdown only to locate candidate claims and structure, re-verify every material claim against implementation evidence, generate the HTML report, then delete the markdown file. Git preserves its history. Do not keep both files; the HTML report is the single canonical report.

## Modes

Infer the mode from the request and repository state. Resolve a missing report deterministically:

- explicit `init`, an unspecified first request, or the first Helm synchronization after the user enables technical-report maintenance → `init`, even when an accepted change scope is available;
- explicit `update` or `audit` that expects an already established report → `blocked` with a recommendation to run `init`.

After initialization, accepted changes use `update`; accuracy checks use `audit`.

### `init`

Use when no report exists or the user asks to establish one.

1. Establish the repository and runtime topology: independent packages and deployable units, executable and composition roots, process / worker / replica boundaries, local versus shared state, and important cross-component communication.
2. Trace important implementation paths through the active evidence loop rather than generalize from the root manifest or primary package.
3. Compose the `report-data` object (schema above) from verified implementation evidence.
4. Copy `templates/technical-report.html` to the report path and replace only the content of the `report-data` block with the generated JSON.
5. Include only applicable modules, edges, and sections with substantive current-state content.

If the report already exists, do not overwrite it from scratch. Treat `init` as a full `audit` so repeated initialization is safe.

### `update`

Use after an accepted implementation change or when the user gives a reliable change scope.

1. Use the accepted diff, changed paths, and task context only to locate the potentially affected implementation.
2. Close the active evidence loop for each affected area, including the actual arguments passed between concrete callers, callees, and host adapters. A diff alone is not sufficient evidence for the resulting description.
3. For cross-component behavior, verify the exact contract emitted and accepted on both sides.
4. Search for rejection, alternate-provider, fallback, bypass, buffering, and degraded paths that narrow the resulting claim.
5. Compare the verified current implementation with the existing report's `report-data` block.
6. Rewrite, add, move, or delete only the affected module entries, edges, and section blocks; write the edited JSON back into the `report-data` block, leaving template code untouched.
7. Leave unrelated accurate entries untouched.

If no report exists, return `blocked` and recommend `init`; do not silently create a partial report.

### `audit`

Use when the user asks whether the report is accurate, when the impact scope is unreliable, or when drift may extend beyond a known change.

1. Re-establish the project's repository/runtime topology and active implementation paths independently of the report.
2. Verify every material report claim, implementation anchor, capability proof level, and claimed runtime scope.
3. Re-prove strong semantics and broad quantifiers against both sides of each contract and adverse paths.
4. Find important implemented areas the report omits.
5. Remove stale, unsupported, over-broad, historical, rationale, prompt-derived, plan-derived, and process-oriented content.
6. Reconcile the `report-data` block in place. Do not append an audit section or audit history.

If no report exists, return `blocked` and recommend `init`.

## Workflow

1. Determine the project root, report path, mode, and implementation baseline. Default to the current working tree; honor an explicitly requested revision or environment.
2. Read applicable repository instructions. Read the current report's `report-data` block when it exists.
3. Establish applicable repository/runtime topology, then discover executable and composition roots, selected providers, build/deployment definitions, and relevant cross-component boundaries.
4. Trace material claims through active production wiring and both sides of any contract. Use tests to understand the verification surface, never as the sole proof of production behavior.
5. Build a private evidence map for each planned claim: evidence anchors, capability proof level, precise runtime scope, both contract sides where applicable, and nearest counter-evidence. Do not write investigation notes into the project.
6. Challenge strong semantics and broad quantifiers against fallback, bypass, rejection, buffering, and degraded paths. Narrow or omit claims whose semantics are not proved.
7. Draft the complete report edit before writing. If a central requested area cannot be verified, stop with `blocked` rather than leave speculative or half-reconciled content.
8. Create the report by copying the template and filling the `report-data` block, or edit the existing data block in place. Preserve accurate unaffected entries, template code, and the project's useful terminology.
9. Re-read the resulting claims against implementation evidence, claimed scope, canonical module/section placement, and the prohibited-content list.
10. Return exactly one result status.

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

Omit this field when empty; never emit `unverified: none`. It is operation metadata only and must not enter the technical report.

For `blocked`, also return:

```text
blocker: <what prevents a trustworthy report update>
```

Meanings:

- `updated` — the report was created or its content changed;
- `no-impact` — the required investigation found no report change within the verified scope (`update`) or across the full report (`init` / `audit`); it never claims that unexamined sections were audited;
- `blocked` — the requested synchronization cannot be completed reliably or safely.

For `update` + `no-impact`, `scope`, `summary`, and `evidence` must identify the accepted-change scope actually examined. Never state or imply that the report is accurate as a whole unless the run was a full `init` / `audit`. A `no-impact` scope cannot include an area listed as `unverified`.

`unverified` is not a fourth status and cannot conceal a central evidence gap. In a full `init` / `audit`, any uncertainty that prevents validating a material report claim or detecting an important omission requires `blocked`; optional `unverified` may only name something explicitly outside the report's stated baseline or scope. In scoped `update`, it may also name an adjacent non-blocking area excluded from both the edit and verified `scope`. If the requested report cannot be trustworthy without that area, return `blocked` instead.

Do not invent `created`, `partial`, or `success` statuses. A `blocked` run must not leave speculative or knowingly half-complete report edits.
