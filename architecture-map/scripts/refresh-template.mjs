#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { fileURLToPath } from "node:url";

const marker = '<script type="application/json" id="report-data">';
const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const templatePath = path.resolve(scriptDir, "..", "templates", "architecture-map.html");

const LAYERS = new Set(["entry", "core", "data", "infra", "external", "frontend"]);
const EDGE_KINDS = new Set(["flow", "dep"]);
const TOP_LEVEL_FIELDS = new Set(["title", "summary", "modules", "edges", "sections"]);
const MODULE_FIELDS = new Set([
  "id", "label", "parent", "layer", "summary", "detail", "notes", "evidence",
]);
const EDGE_FIELDS = new Set(["from", "to", "label", "kind"]);
const SECTION_FIELDS = new Set(["title", "blocks"]);
const BLOCK_FIELDS = {
  p: new Set(["type", "text"]),
  heading: new Set(["type", "text"]),
  code: new Set(["type", "text"]),
  steps: new Set(["type", "items"]),
  bullets: new Set(["type", "items"]),
  anchors: new Set(["type", "items"]),
  table: new Set(["type", "columns", "rows"]),
};

function isPlainObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isNonEmptyString(value) {
  return typeof value === "string" && value.trim().length > 0;
}

function isNonEmptyStringArray(value) {
  return Array.isArray(value) && value.length > 0 && value.every(isNonEmptyString);
}

function unknownFields(entry, allowed, label, problems) {
  for (const key of Object.keys(entry)) {
    if (!allowed.has(key)) problems.push(`${label}: unknown field "${key}"`);
  }
}

// Structural invariants for the report-data block. The renderer silently
// contains violations (unknown layers fall back to the core color, duplicate
// ids drop later entries, unknown parents lift to the top level), so this is
// the machine check for the authoring checklist in REFERENCE.md ("Validation
// before writing"). It covers the mechanically decidable subset; prose and
// evidence-quality items remain authoring discipline.
function validateReportData(data, problems) {
  if (!isPlainObject(data)) {
    problems.push("report-data must be a JSON object");
    return;
  }
  for (const key of Object.keys(data)) {
    if (!TOP_LEVEL_FIELDS.has(key)) problems.push(`unknown top-level field "${key}"`);
  }
  if (!isNonEmptyString(data.title)) problems.push("title must be a non-empty string");
  if (!isNonEmptyString(data.summary)) problems.push("summary must be a non-empty string");
  if (!Array.isArray(data.modules) || data.modules.length === 0) {
    problems.push("modules must be a non-empty array");
    return;
  }

  const byId = new Map();
  const order = [];
  data.modules.forEach((m, i) => {
    const label = `modules[${i}]${isPlainObject(m) && isNonEmptyString(m.id) ? ` (${m.id})` : ""}`;
    if (!isPlainObject(m)) {
      problems.push(`${label}: must be an object`);
      return;
    }
    unknownFields(m, MODULE_FIELDS, label, problems);
    if (!isNonEmptyString(m.id) || m.id.includes("\n")) {
      problems.push(`${label}: id must be a non-empty single-line string`);
      return;
    }
    if (byId.has(m.id)) {
      problems.push(`${label}: duplicate module id "${m.id}"`);
      return;
    }
    byId.set(m.id, m);
    order.push(m.id);
    if (!isNonEmptyString(m.label) || m.label.includes("\n")) {
      problems.push(`${label}: label must be a non-empty single-line string`);
    }
    if (!LAYERS.has(m.layer)) {
      problems.push(`${label}: layer must be one of ${[...LAYERS].join(" | ")}`);
    }
    if (!isNonEmptyString(m.summary) || m.summary.includes("\n")) {
      problems.push(`${label}: summary must be a non-empty single-line string`);
    }
    if ("detail" in m && !isNonEmptyString(m.detail)) {
      problems.push(`${label}: detail must be a non-empty string when present`);
    }
    for (const field of ["notes", "evidence"]) {
      if (field in m && !isNonEmptyStringArray(m[field])) {
        problems.push(`${label}: ${field} must be a non-empty array of strings when present`);
      }
    }
    if ("parent" in m && !isNonEmptyString(m.parent)) {
      problems.push(`${label}: parent must be a non-empty string when present`);
    }
  });
  for (const id of order) {
    let depth = 0;
    let cursor = byId.get(id);
    const seen = new Set([id]);
    while (cursor && isNonEmptyString(cursor.parent)) {
      if (!byId.has(cursor.parent)) break;
      depth += 1;
      if (seen.has(cursor.parent)) {
        problems.push(`${id}: parent chain contains a cycle`);
        break;
      }
      seen.add(cursor.parent);
      cursor = byId.get(cursor.parent);
    }
    if (depth > 2) {
      problems.push(`${id}: deeper than three levels (system → module → component)`);
    }
  }
  for (const m of data.modules) {
    if (isPlainObject(m) && isNonEmptyString(m.parent) && !byId.has(m.parent)) {
      problems.push(`modules (${m.id}): parent "${m.parent}" references a missing module`);
    }
  }

  if ("edges" in data && !Array.isArray(data.edges)) {
    problems.push("edges must be an array when present");
  }
  (Array.isArray(data.edges) ? data.edges : []).forEach((e, i) => {
    const label = `edges[${i}]`;
    if (!isPlainObject(e)) {
      problems.push(`${label}: must be an object`);
      return;
    }
    unknownFields(e, EDGE_FIELDS, label, problems);
    if (!(isNonEmptyString(e.from) && byId.has(e.from))) {
      problems.push(`${label}: from must reference an existing module id`);
    }
    if (!(isNonEmptyString(e.to) && byId.has(e.to))) {
      problems.push(`${label}: to must reference an existing module id`);
    }
    if (isNonEmptyString(e.from) && e.from === e.to) {
      problems.push(`${label}: edge from a module to itself`);
    }
    if (!EDGE_KINDS.has(e.kind)) {
      problems.push(`${label}: kind is required and must be flow or dep`);
    }
    if ("label" in e && !isNonEmptyString(e.label)) {
      problems.push(`${label}: label must be a non-empty string when present`);
    }
    const from = byId.get(e.from);
    const to = byId.get(e.to);
    if (from && to && from.layer === "data" && to.layer === "data") {
      problems.push(`${label}: data nodes are passive; never connect two data nodes directly`);
    }
  });

  if ("sections" in data) {
    if (!Array.isArray(data.sections)) {
      problems.push("sections must be an array when present");
      return;
    }
    const seenTitles = new Set();
    data.sections.forEach((s, idx) => {
      const label = `sections[${idx}]`;
      if (!isPlainObject(s)) {
        problems.push(`${label}: must be an object`);
        return;
      }
      unknownFields(s, SECTION_FIELDS, label, problems);
      const title = isNonEmptyString(s.title) ? s.title.trim() : "";
      if (!title) {
        problems.push(`${label}: title must be a non-empty string`);
      } else if (title === "架构") {
        problems.push(`${label}: section title "架构" is reserved for the diagram tab`);
      } else if (seenTitles.has(title)) {
        problems.push(`${label}: duplicate section title "${title}"`);
      } else {
        seenTitles.add(title);
      }
      if (!Array.isArray(s.blocks) || s.blocks.length === 0) {
        problems.push(`${label}: blocks must be a non-empty array`);
        return;
      }
      s.blocks.forEach((b, j) => {
        const blockLabel = `${label}${title ? ` "${title}"` : ""}.blocks[${j}]`;
        if (!isPlainObject(b)) {
          problems.push(`${blockLabel}: block must be an object`);
          return;
        }
        const allowed = BLOCK_FIELDS[b.type];
        if (!allowed) {
          problems.push(
            `${blockLabel}: type must be one of ${Object.keys(BLOCK_FIELDS).join(" | ")}`,
          );
          return;
        }
        unknownFields(b, allowed, blockLabel, problems);
        if (allowed.has("text") && !isNonEmptyString(b.text)) {
          problems.push(`${blockLabel}: text must be non-empty`);
        }
        if (allowed.has("items") && !isNonEmptyStringArray(b.items)) {
          problems.push(`${blockLabel}: items must be a non-empty array of strings`);
        }
        if (allowed.has("columns")) {
          const columnsOk = isNonEmptyStringArray(b.columns);
          if (!columnsOk) {
            problems.push(`${blockLabel}: columns must be a non-empty array of strings`);
          }
          if (!Array.isArray(b.rows) || b.rows.length === 0) {
            problems.push(`${blockLabel}: rows must be a non-empty array`);
          } else if (columnsOk) {
            b.rows.forEach((row, k) => {
              if (!Array.isArray(row) || row.length !== b.columns.length) {
                problems.push(
                  `${blockLabel}.rows[${k}]: must have ${b.columns.length} cells (one per column)`,
                );
              } else if (row.some((cell) => !isNonEmptyString(cell))) {
                problems.push(`${blockLabel}.rows[${k}]: every cell must be a non-empty string`);
              }
            });
          }
        }
      });
    });
  }
}

// Overview density advisory (not a structural failure): mirrors the roughly
// 15 core-node / 12 lifted-edge overview default in REFERENCE.md. The
// top-level count and lifted pairs follow the renderer's lifting rule, so the
// advisory speaks about the rendered overview, not the raw arrays.
function densityAdvisory(data) {
  const byId = new Map();
  data.modules.forEach((m) => byId.set(m.id, m));
  const topIds = [];
  data.modules.forEach((m) => {
    const p = m.parent || null;
    if (!(p && byId.has(p))) topIds.push(m.id);
  });
  function visAnc(id) {
    let cursor = byId.get(id);
    while (cursor) {
      const p = cursor.parent || null;
      if (!(p && byId.has(p))) return cursor.id;
      cursor = byId.get(p);
    }
    return null;
  }
  const lifted = new Set();
  (Array.isArray(data.edges) ? data.edges : []).forEach((e) => {
    if (!(isPlainObject(e) && isNonEmptyString(e.from) && isNonEmptyString(e.to))) return;
    const fromAnc = visAnc(e.from);
    const toAnc = visAnc(e.to);
    if (fromAnc && toAnc && fromAnc !== toAnc) lifted.add(`${fromAnc}\u2192${toAnc}`);
  });
  const notes = [];
  if (topIds.length > 15) {
    notes.push(`${topIds.length} top-level modules exceed the ~15 core-node overview default`);
  }
  if (lifted.size > 12) {
    notes.push(`~${lifted.size} lifted overview edges exceed the ~12-edge default`);
  }
  return notes;
}

function usage() {
  console.log("Usage: node refresh-template.mjs [mode] <report.html>");
  console.log("  (no mode)  refresh the shell, preserving the report-data block");
  console.log("  --check    print current/stale without writing (exit 0 current, 1 stale)");
  console.log("  --validate validate the report-data block only (exit 0 valid, 2 invalid)");
}

function extractDataBlock(html, label) {
  const start = html.indexOf(marker);
  if (start < 0) throw new Error(`${label}: report-data block is missing`);
  const contentStart = start + marker.length;
  const closeStart = html.indexOf("</script>", contentStart);
  if (closeStart < 0) throw new Error(`${label}: report-data block is not closed`);
  const end = closeStart + "</script>".length;
  const jsonText = html.slice(contentStart, closeStart);
  let data;
  try {
    data = JSON.parse(jsonText);
  } catch (error) {
    throw new Error(`${label}: report-data is invalid JSON: ${error.message}`);
  }
  return { start, end, block: html.slice(start, end), data };
}

function extractTemplateVersion(html, label, allowMissing = false) {
  const headEnd = html.search(/<\/head\s*>/i);
  const head = headEnd >= 0 ? html.slice(0, headEnd) : html;
  const tags = head.match(/<meta\b[^>]*>/gi) || [];
  const tag = tags.find((candidate) =>
    /\bname\s*=\s*["']architecture-map-template-version["']/i.test(candidate),
  );
  if (!tag) {
    if (allowMissing) return 0;
    throw new Error(`${label}: architecture-map-template-version meta tag is missing`);
  }
  const match = tag.match(/\bcontent\s*=\s*["']([0-9]+)["']/i);
  if (!match) {
    throw new Error(`${label}: architecture-map-template-version is not a non-negative integer`);
  }
  return Number(match[1]);
}

function main() {
  const args = process.argv.slice(2);
  const check = args[0] === "--check";
  const validate = args[0] === "--validate";
  if (check || validate) args.shift();
  if (args.length !== 1 || args[0] === "--help" || args[0] === "-h") {
    usage();
    process.exitCode = args.length === 1 ? 0 : 2;
    return;
  }

  const requestedPath = path.resolve(args[0]);
  const reportPath = fs.realpathSync(requestedPath);
  const report = fs.readFileSync(reportPath, "utf8");

  if (validate) {
    const problems = [];
    try {
      const { data } = extractDataBlock(report, reportPath);
      validateReportData(data, problems);
    } catch (error) {
      problems.push(error.message);
    }
    if (problems.length) {
      for (const problem of problems) console.error(`invalid: ${problem}`);
      console.error(
        `${problems.length} problem${problems.length > 1 ? "s" : ""} found in ${reportPath}`,
      );
      process.exitCode = 2;
      return;
    }
    console.log(`valid: ${reportPath}`);
    const { data } = extractDataBlock(report, reportPath);
    for (const note of densityAdvisory(data)) {
      console.log(
        `advisory: ${note}; consider grouping along verified boundaries and pushing detail into drill-down`,
      );
    }
    return;
  }

  const template = fs.readFileSync(templatePath, "utf8");
  const templateVersion = extractTemplateVersion(template, "template");
  const reportVersion = extractTemplateVersion(report, reportPath, true);
  if (reportVersion > templateVersion) {
    throw new Error(
      `${reportPath}: report template v${reportVersion} is newer than installed template v${templateVersion}; refusing to downgrade`,
    );
  }
  const templateData = extractDataBlock(template, "template");
  const reportData = extractDataBlock(report, reportPath);
  const refreshed =
    template.slice(0, templateData.start) +
    reportData.block +
    template.slice(templateData.end);
  const current = refreshed === report;

  if (check) {
    console.log(`${current ? "current" : "stale"}: ${reportPath}`);
    process.exitCode = current ? 0 : 1;
    return;
  }
  if (current) {
    console.log(`current: ${reportPath}`);
    return;
  }

  const stat = fs.statSync(reportPath);
  const tempPath = `${reportPath}.architecture-map-${process.pid}-${randomUUID()}.tmp`;
  try {
    fs.writeFileSync(tempPath, refreshed, {
      encoding: "utf8",
      mode: stat.mode & 0o777,
      flag: "wx",
    });
    if (fs.readFileSync(reportPath, "utf8") !== report) {
      throw new Error(`${reportPath}: report changed during refresh; retry after reviewing the concurrent edit`);
    }
    fs.renameSync(tempPath, reportPath);
  } finally {
    if (fs.existsSync(tempPath)) fs.unlinkSync(tempPath);
  }
  console.log(`updated: ${reportPath}`);
}

try {
  main();
} catch (error) {
  console.error(`error: ${error.message}`);
  process.exitCode = 2;
}
