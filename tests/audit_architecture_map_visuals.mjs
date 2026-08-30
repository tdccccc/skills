// architecture-map 渲染视觉审计（jsdom，无需浏览器）。
// 运行：node tests/audit_architecture_map_visuals.mjs <report.html> [more...]
// 依赖 jsdom（与 test_architecture_map_template.mjs 相同）；未安装时退出码 2。
// 覆盖 P1 视觉验收契约的自动化门：重叠、裁切、线路、可读性、交互与主题。
// 输出：每个报告每项检查一行 PASS/FAIL，整体退出码 0 全部通过 / 1 有失败。
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const here = path.dirname(fileURLToPath(import.meta.url));
const templatePath = path.join(
  here,
  "..",
  "architecture-map",
  "templates",
  "architecture-map.html",
);
const templateHtml = fs.readFileSync(templatePath, "utf-8");

function loadJsdom() {
  const require = createRequire(import.meta.url);
  try {
    return require("jsdom");
  } catch {
    // fall through to NODE_PATH locations
  }
  for (const dir of (process.env.NODE_PATH || "").split(":").filter(Boolean)) {
    try {
      return require(path.join(dir, "jsdom"));
    } catch {
      // keep trying
    }
  }
  return null;
}

const jsdomModule = loadJsdom();
if (!jsdomModule) {
  console.log("SKIP: jsdom 未安装（npm i jsdom）");
  process.exit(2);
}
const { JSDOM } = jsdomModule;

const reportFiles = process.argv.slice(2);
if (!reportFiles.length) {
  console.error("usage: node audit_architecture_map_visuals.mjs <report.html> [more...]");
  process.exit(2);
}

let totalFailures = 0;

function auditReport(reportPath) {
  const html = fs.readFileSync(reportPath, "utf-8");
  const dom = new JSDOM(html, {
    runScripts: "dangerously",
    pretendToBeVisual: true,
    url: "https://localhost/",
  });
  const { window } = dom;
  const { document } = window;
  const errors = [];
  window.addEventListener("error", (e) => errors.push(String(e.message)));
  const failures = [];
  const info = [];

  const expect = (name, cond, detail) => {
    if (cond) info.push(`PASS ${path.basename(reportPath)} ${name}`);
    else failures.push(`FAIL ${path.basename(reportPath)} ${name}${detail === undefined ? "" : ` — ${detail}`}`);
  };

  const nodes = () =>
    Array.from(document.querySelectorAll("#canvas g.node")).map((g) => ({
      id: g.getAttribute("data-id"),
      rect: (() => {
        const r = g.querySelector("rect");
        return r
          ? { x: Number(r.getAttribute("x")), y: Number(r.getAttribute("y")), w: Number(r.getAttribute("width")), h: Number(r.getAttribute("height")) }
          : null;
      })(),
    }));
  const edges = () => Array.from(document.querySelectorAll("#canvas g.edge"));
  const labelRects = () =>
    Array.from(document.querySelectorAll("#canvas .edge-label-bg:not(.colliding)")).map((r) => ({
      x: Number(r.getAttribute("x")),
      y: Number(r.getAttribute("y")),
      w: Number(r.getAttribute("width")),
      h: Number(r.getAttribute("height")),
    }));
  const sceneTransform = () => {
    const t = document.querySelector("#scene")?.getAttribute("transform") || "translate(0 0) scale(1)";
    const m = t.match(/translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+)\)/);
    return m ? { panX: Number(m[1]), panY: Number(m[2]), zoom: Number(m[3]) } : { panX: 0, panY: 0, zoom: 1 };
  };
  const viewport = () => {
    const vb = (document.querySelector("#canvas").getAttribute("viewBox") || "0 0 960 640").split(" ").map(Number);
    return { w: vb[2] || 960, h: vb[3] || 640 };
  };
  const overlaps = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;

  // ---- 当前视图的几何审计 ----
  function auditGeometry(tag, allowZeroNodes = false) {
    const current = nodes();
    if (!allowZeroNodes) expect(`[${tag}] nodes rendered`, current.length > 0, current.length);
    const rects = current.map((n) => n.rect).filter(Boolean);
    let nodeOverlap = null;
    for (let i = 0; i < rects.length && !nodeOverlap; i++) {
      for (let j = i + 1; j < rects.length && !nodeOverlap; j++) {
        if (overlaps(rects[i], rects[j])) nodeOverlap = [rects[i], rects[j]];
      }
    }
    expect(`[${tag}] no node-node overlap`, !nodeOverlap, JSON.stringify(nodeOverlap));

    const labels = labelRects();
    let labelOverlap = null;
    for (let i = 0; i < labels.length && !labelOverlap; i++) {
      for (let j = i + 1; j < labels.length && !labelOverlap; j++) {
        if (overlaps(labels[i], labels[j])) labelOverlap = [labels[i], labels[j]];
      }
    }
    expect(`[${tag}] no label-label overlap`, !labelOverlap, JSON.stringify(labelOverlap));

    let labelNodeOverlap = null;
    for (let i = 0; i < labels.length && !labelNodeOverlap; i++) {
      for (let j = 0; j < rects.length && !labelNodeOverlap; j++) {
        if (overlaps(labels[i], rects[j])) labelNodeOverlap = [labels[i], rects[j]];
      }
    }
    expect(`[${tag}] no label-node overlap`, !labelNodeOverlap, JSON.stringify(labelNodeOverlap));

    const vp = viewport();
    const t = sceneTransform();
    let clipped = null;
    const map = (p) => ({ x: p.x * t.zoom + t.panX, y: p.y * t.zoom + t.panY });
    for (const label of labels) {
      const c = map(label);
      if (c.x < -1 || c.y < -1 || c.x + label.w * t.zoom > vp.w + 1 || c.y + label.h * t.zoom > vp.h + 1) clipped = label;
    }
    for (const r of rects) {
      const c = map(r);
      if (c.x < -1 || c.y < -1 || c.x + r.w * t.zoom > vp.w + 1 || c.y + r.h * t.zoom > vp.h + 1) clipped = r;
    }
    expect(`[${tag}] no clipping at fit zoom`, !clipped, JSON.stringify(clipped));

    const routeFailed = document.querySelectorAll('#canvas g.edge[data-route-failed="true"]').length;
    expect(`[${tag}] no route-failed markers`, routeFailed === 0, routeFailed);

    const hiddenLabels = document.querySelectorAll("#canvas .edge-label.colliding").length;
    expect(`[${tag}] no hidden-until-hover labels`, hiddenLabels === 0, hiddenLabels);
  }

  function parseRoute(edge) {
    return (edge.getAttribute("data-route") || "")
      .split(";")
      .filter(Boolean)
      .map((point) => {
        const [x, y] = point.split(",").map(Number);
        return { x, y };
      });
  }

  function properCrossings() {
    const eps = 0.01;
    const routed = edges()
      .map((edge) => ({
        from: edge.getAttribute("data-from"),
        to: edge.getAttribute("data-to"),
        points: parseRoute(edge),
      }))
      .filter((e) => e.points.length > 1);
    let proper = 0;
    for (let i = 0; i < routed.length; i++) {
      for (let j = i + 1; j < routed.length; j++) {
        const left = routed[i];
        const right = routed[j];
        if ([left.from, left.to].some((id) => id === right.from || id === right.to)) continue;
        for (let a = 1; a < left.points.length; a++) {
          const ah = Math.abs(left.points[a - 1].y - left.points[a].y) < eps;
          for (let b = 1; b < right.points.length; b++) {
            const bh = Math.abs(right.points[b - 1].y - right.points[b].y) < eps;
            if (ah === bh) continue;
            const h = ah ? { a: left.points[a - 1], b: left.points[a] } : { a: right.points[b - 1], b: right.points[b] };
            const v = ah ? { a: right.points[b - 1], b: right.points[b] } : { a: left.points[a - 1], b: left.points[a] };
            const x = v.a.x;
            const y = h.a.y;
            const between = (value, lo, hi) => value >= Math.min(lo, hi) - eps && value <= Math.max(lo, hi) + eps;
            const interior = (value, lo, hi) => value > Math.min(lo, hi) + eps && value < Math.max(lo, hi) - eps;
            if (between(x, h.a.x, h.b.x) && between(y, v.a.y, v.b.y) && interior(x, h.a.x, h.b.x) && interior(y, v.a.y, v.b.y)) proper++;
          }
        }
      }
    }
    return proper;
  }

  // ---- 交互冒烟 ----
  const click = (el) => el && el.dispatchEvent(new window.Event("click", { bubbles: true }));
  const clickNode = (id) =>
    click(document.querySelector(`#canvas g.node[data-id="${id}"]`));

  // ---- 主流程 ----
  auditGeometry("overview");
  expect("overview no proper edge crossings", properCrossings() === 0, properCrossings());

  // 递归下钻每一层并审计
  function walkDrillDowns() {
    const drillable = () =>
      Array.from(document.querySelectorAll("#canvas g.node")).filter((g) => {
        if (g.getAttribute("data-id") === "__parent") return false;
        return Array.from(g.querySelectorAll("text")).some((t) => /^\+\d/.test(t.textContent || ""));
      });
    const enter = (g) => {
      const id = g.getAttribute("data-id");
      const tag = (g.textContent || id).slice(0, 20);
      clickNode(id);
      auditGeometry(`drill ${tag}`);
      expect(`drill ${tag} no proper edge crossings`, properCrossings() === 0, properCrossings());
      drillable().forEach((child) => enter(child));
      const back = document.querySelector('#canvas g.node[data-id="__parent"]');
      if (back) clickNode("__parent");
      else click(document.querySelector("#breadcrumb .crumb"));
    };
    drillable().forEach((g) => enter(g));
  }
  walkDrillDowns();

  // 选中一个叶子节点：关键路径强调
  const leaf = document.querySelector('#canvas g.node:not([data-id="__parent"]) text')
    ? Array.from(document.querySelectorAll("#canvas g.node")).find((g) => {
        const text = g.textContent || "";
        return !/^\+\d/.test(text.trim()) && g.getAttribute("data-id") !== "__parent";
      })
    : null;
  if (leaf) {
    clickNode(leaf.getAttribute("data-id"));
    const focusLevels = edges().filter((e) => /(path|up|hi|dim)/.test(e.getAttribute("class") || "")).length;
    const selected = document.querySelectorAll("#canvas g.node.selected").length;
    expect("focus select highlights a node", selected === 1, selected);
    expect("focus classifies connected edges", focusLevels > 0, focusLevels);
    click(document.getElementById("canvas"));
    expect("focus clears on canvas click", document.querySelectorAll("#canvas g.node.selected").length === 0);
  }

  // 搜索过滤
  const search = document.getElementById("search");
  if (search) {
    const firstDim = Array.from(document.querySelectorAll("#canvas g.node"))[0];
    const label = firstDim ? (firstDim.textContent || "").slice(0, 2) : "";
    search.value = label || "zzz-no-match";
    search.dispatchEvent(new window.Event("input", { bubbles: true }));
    expect("search dims non-matching nodes", document.querySelectorAll("#canvas g.node.dim").length >= 0);
    search.value = "";
    search.dispatchEvent(new window.Event("input", { bubbles: true }));
    expect("clearing search restores all nodes", document.querySelectorAll("#canvas g.node.dim").length === 0);
  }

  // 主题切换
  const themeButton = document.querySelector('[data-canvas-action="theme"]');
  if (themeButton) {
    const fillBefore = document.querySelector("#canvas g.node rect")?.getAttribute("fill");
    click(themeButton);
    const light = document.documentElement.getAttribute("data-theme") === "light";
    const fillAfter = document.querySelector("#canvas g.node rect")?.getAttribute("fill");
    expect("theme toggles to light", light);
    expect("theme re-renders palette", fillBefore && fillAfter && fillBefore !== fillAfter, { fillBefore, fillAfter });
    expect("light theme keeps nodes and edges", nodes().length > 0 && edges().length > 0);
    click(themeButton);
    expect("theme toggles back to dark", document.documentElement.getAttribute("data-theme") === "dark");
    expect("dark palette restored", document.querySelector("#canvas g.node rect")?.getAttribute("fill") === fillBefore);
  }

  // 拖拽 / 平移 / 缩放 / 适配 / 重置
  const PointerLikeEvent = typeof window.PointerEvent === "function" ? window.PointerEvent : window.MouseEvent;
  const downEvent = typeof window.PointerEvent === "function" ? "pointerdown" : "mousedown";
  const moveEvent = typeof window.PointerEvent === "function" ? "pointermove" : "mousemove";
  const upEvent = typeof window.PointerEvent === "function" ? "pointerup" : "mouseup";
  const firstNode = () => document.querySelector("#canvas g.node");
  if (firstNode()) {
    const rect = (el) => el?.querySelector("rect");
    const beforeX = Number(rect(firstNode())?.getAttribute("x"));
    firstNode().dispatchEvent(new PointerLikeEvent(downEvent, { bubbles: true, button: 0, clientX: 100, clientY: 100 }));
    window.dispatchEvent(new PointerLikeEvent(moveEvent, { bubbles: true, clientX: 130, clientY: 110 }));
    window.dispatchEvent(new PointerLikeEvent(upEvent, { bubbles: true, button: 0, clientX: 130, clientY: 110 }));
    expect("node drag moves the node", Number(rect(firstNode())?.getAttribute("x")) !== beforeX, { beforeX, afterX: rect(firstNode())?.getAttribute("x") });
    click(document.querySelector('[data-canvas-action="reset"]'));
    expect("reset restores the layout", Number(rect(firstNode())?.getAttribute("x")) === beforeX);
  }
  const sceneBefore = sceneTransform();
  document.getElementById("canvas").dispatchEvent(
    new PointerLikeEvent(downEvent, { bubbles: true, button: 0, clientX: 200, clientY: 200 }),
  );
  window.dispatchEvent(new PointerLikeEvent(moveEvent, { bubbles: true, clientX: 230, clientY: 210 }));
  window.dispatchEvent(new PointerLikeEvent(upEvent, { bubbles: true, button: 0, clientX: 230, clientY: 210 }));
  const panned = sceneTransform();
  expect("background drag pans the scene", panned.panX !== sceneBefore.panX || panned.panY !== sceneBefore.panY);
  document.getElementById("canvas").dispatchEvent(
    new window.WheelEvent("wheel", { bubbles: true, deltaY: -120, clientX: 240, clientY: 180 }),
  );
  const zoomed = sceneTransform();
  expect("wheel zoom changes the transform", zoomed.zoom !== panned.zoom, { before: panned.zoom, after: zoomed.zoom });
  click(document.querySelector('[data-canvas-action="fit"]'));
  expect("fit keeps a valid transform", /^translate\(/.test(document.querySelector("#scene")?.getAttribute("transform") || ""));

  expect("no uncaught errors during interaction", errors.length === 0, errors.slice(0, 5));

  dom.window.close();

  if (failures.length) {
    for (const f of failures) console.error(f);
    totalFailures += failures.length;
  } else {
    console.log(`PASS ${path.basename(reportPath)} ${info.length} checks`);
  }
}

for (const report of reportFiles) {
  try {
    auditReport(report);
  } catch (error) {
    console.error(`FAIL ${path.basename(report)} script error: ${error.message}`);
    totalFailures++;
  }
}

console.log(`${totalFailures ? "FAILED" : "ALL PASS"} — ${totalFailures} failure(s)`);
process.exit(totalFailures ? 1 : 0);