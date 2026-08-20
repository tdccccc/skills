#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";
import { fileURLToPath } from "node:url";

const marker = '<script type="application/json" id="report-data">';
const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const templatePath = path.resolve(scriptDir, "..", "templates", "architecture-map.html");

function usage() {
  console.log("Usage: node refresh-template.mjs [--check] <report.html>");
}

function extractDataBlock(html, label) {
  const start = html.indexOf(marker);
  if (start < 0) throw new Error(`${label}: report-data block is missing`);
  const contentStart = start + marker.length;
  const closeStart = html.indexOf("</script>", contentStart);
  if (closeStart < 0) throw new Error(`${label}: report-data block is not closed`);
  const end = closeStart + "</script>".length;
  const jsonText = html.slice(contentStart, closeStart);
  try {
    JSON.parse(jsonText);
  } catch (error) {
    throw new Error(`${label}: report-data is invalid JSON: ${error.message}`);
  }
  return { start, end, block: html.slice(start, end) };
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
  if (check) args.shift();
  if (args.length !== 1 || args[0] === "--help" || args[0] === "-h") {
    usage();
    process.exitCode = args.length === 1 ? 0 : 2;
    return;
  }

  const requestedPath = path.resolve(args[0]);
  const reportPath = fs.realpathSync(requestedPath);
  const template = fs.readFileSync(templatePath, "utf8");
  const report = fs.readFileSync(reportPath, "utf8");
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
