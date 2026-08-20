// architecture-map 模板渲染器行为冒烟测试（jsdom）。
// 运行：node tests/test_architecture_map_template.mjs
// 依赖 jsdom（npm i jsdom）；未安装时退出码 2，python 包装测试会跳过。
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
    // fall through to NODE_PATH locations (CI / local installs)
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

let passed = 0;
let failed = 0;
function check(name, cond, detail) {
  if (cond) {
    passed++;
  } else {
    failed++;
    console.log("FAIL:", name, detail === undefined ? "" : detail);
  }
}

function buildHtml(block) {
  return templateHtml.replace(
    /<script type="application\/json" id="report-data">[\s\S]*?<\/script>/,
    '<script type="application/json" id="report-data">\n' + block + "\n</script>",
  );
}

function loadDom(block, beforeParse) {
  return new JSDOM(buildHtml(block), {
    runScripts: "dangerously",
    pretendToBeVisual: true,
    ...(beforeParse ? { beforeParse } : {}),
  });
}

function routeInteractions(document) {
  const eps = 0.01;
  const edges = Array.from(document.querySelectorAll("#canvas g.edge")).map((edge) => {
    const points = edge
      .getAttribute("data-route")
      .split(";")
      .map((point) => {
        const [x, y] = point.split(",").map(Number);
        return { x, y };
      });
    return {
      from: edge.getAttribute("data-from"),
      to: edge.getAttribute("data-to"),
      segments: points.slice(1).map((point, index) => ({ a: points[index], b: point })),
    };
  });
  const result = { proper: [], touch: [], overlap: [] };
  const between = (value, a, b) => value >= Math.min(a, b) - eps && value <= Math.max(a, b) + eps;
  const interior = (value, a, b) => value > Math.min(a, b) + eps && value < Math.max(a, b) - eps;
  for (let i = 0; i < edges.length; i++) {
    for (let j = i + 1; j < edges.length; j++) {
      const left = edges[i];
      const right = edges[j];
      if ([left.from, left.to].some((id) => id === right.from || id === right.to)) continue;
      const kinds = new Set();
      for (const a of left.segments) {
        const ah = Math.abs(a.a.y - a.b.y) < eps;
        for (const b of right.segments) {
          const bh = Math.abs(b.a.y - b.b.y) < eps;
          if (ah === bh) {
            const sameLine = ah ? Math.abs(a.a.y - b.a.y) < eps : Math.abs(a.a.x - b.a.x) < eps;
            if (!sameLine) continue;
            const a1 = ah ? a.a.x : a.a.y;
            const a2 = ah ? a.b.x : a.b.y;
            const b1 = ah ? b.a.x : b.a.y;
            const b2 = ah ? b.b.x : b.b.y;
            const overlap = Math.min(Math.max(a1, a2), Math.max(b1, b2)) - Math.max(Math.min(a1, a2), Math.min(b1, b2));
            if (overlap > eps) kinds.add("overlap");
            else if (Math.abs(overlap) <= eps) kinds.add("touch");
            continue;
          }
          const h = ah ? a : b;
          const v = ah ? b : a;
          const x = v.a.x;
          const y = h.a.y;
          if (!between(x, h.a.x, h.b.x) || !between(y, v.a.y, v.b.y)) continue;
          if (interior(x, h.a.x, h.b.x) && interior(y, v.a.y, v.b.y)) kinds.add("proper");
          else kinds.add("touch");
        }
      }
      const pair = `${left.from}→${left.to} × ${right.from}→${right.to}`;
      kinds.forEach((kind) => result[kind].push(pair));
    }
  }
  return result;
}

const defaultBlock = templateHtml.match(
  /<script type="application\/json" id="report-data">([\s\S]*?)<\/script>/,
)[1];

function runOverviewSuite() {
  const dom = loadDom(defaultBlock);
  const { window } = dom;
  const { document } = window;

  const nodes = () =>
    Array.from(document.querySelectorAll("#canvas g.node")).map((g) =>
      g.getAttribute("data-id"),
    );
  const edges = () => document.querySelectorAll("#canvas g.edge").length;
  const breadcrumb = () =>
    document.getElementById("breadcrumb").textContent.replace(/\s+/g, " ").trim();
  const clickNode = (id) => {
    const g = document.querySelector(`#canvas g.node[data-id="${id}"]`);
    if (!g) throw new Error("node not found: " + id);
    g.dispatchEvent(new window.Event("click", { bubbles: true }));
  };

  check("title rendered", document.getElementById("title").textContent.includes("示例"));
  check("overview has 6 top-level nodes", nodes().length === 6, nodes());
  check("overview has 6 edges", edges() === 6, edges());
  const aggregatedApiEdge = document.querySelector('#canvas g.edge[data-from="api"][data-to="svc"]');
  check(
    "lifted parallel relationships are explicitly aggregated",
    aggregatedApiEdge?.getAttribute("data-edge-count") === "3",
    aggregatedApiEdge?.outerHTML,
  );
  check(
    "aggregated edge title preserves distinct relationship labels",
    aggregatedApiEdge?.querySelector("title")?.textContent.includes("分发") &&
      aggregatedApiEdge?.querySelector("title")?.textContent.includes("回调"),
    aggregatedApiEdge?.querySelector("title")?.textContent,
  );
  check("overview breadcrumb is 系统", breadcrumb() === "系统", breadcrumb());
  const tabs = Array.from(document.querySelectorAll("#tabs .tab")).map(
    (t) => t.textContent,
  );
  check(
    "tabs include 架构 and 技术栈与运行时",
    JSON.stringify(tabs) === JSON.stringify(["架构", "技术栈与运行时"]),
    tabs,
  );
  const legend = document.getElementById("legend").textContent;
  check(
    "legend lists six layers",
    ["入口", "核心逻辑", "数据存储", "基础设施", "外部系统", "前端"].every((s) =>
      legend.includes(s),
    ),
  );

  clickNode("api");
  check(
    "drill-down breadcrumb shows path",
    breadcrumb() === "系统 / HTTP API",
    breadcrumb(),
  );
  const subNodes = nodes();
  check(
    "api sub-view shows children, boundary, context nodes",
    ["api.auth", "api.orders", "api.pay", "__parent", "web", "svc.orders", "svc.pay", "gateway"].every(
      (id) => subNodes.includes(id),
    ) && subNodes.length === 8,
    subNodes,
  );
  check("panel is open", document.getElementById("panel").classList.contains("open"));
  check(
    "open panel reserves diagram space",
    document.getElementById("view-diagram").classList.contains("panel-open"),
  );
  check("panel shows module title", document.querySelector("#panel h2").textContent === "HTTP API");
  const panelText = document.getElementById("panel").textContent;
  check("panel shows 机制说明", panelText.includes("机制说明"));
  check("panel shows 代码证据", panelText.includes("代码证据"));
  check("panel evidence chips", document.querySelectorAll("#panel .chip").length === 2);
  check("panel hint mentions drill-down", panelText.includes("子模块"));

  clickNode("api.auth");
  check("leaf breadcrumb unchanged", breadcrumb() === "系统 / HTTP API", breadcrumb());
  check("leaf panel title", document.querySelector("#panel h2").textContent === "鉴权中间件");
  check(
    "leaf selection highlights one node",
    document.querySelectorAll("#canvas g.node.selected").length === 1,
  );
  check(
    "leaf selection highlights connected edges",
    document.querySelectorAll("#canvas g.edge.hi").length === 1,
  );

  clickNode("__parent");
  check("boundary click goes up", breadcrumb() === "系统", breadcrumb());
  check("back to 6 nodes", nodes().length === 6, nodes());

  clickNode("svc");
  check("svc sub-view breadcrumb", breadcrumb() === "系统 / 业务服务", breadcrumb());
  const svcNodes = nodes();
  check(
    "svc sub-view has children + external context",
    ["svc.orders", "svc.pay", "db", "queue", "gateway"].every((id) =>
      svcNodes.includes(id),
    ) &&
      svcNodes.includes("api.auth") &&
      svcNodes.includes("api.orders") &&
      svcNodes.includes("api.pay"),
    svcNodes,
  );

  const search = document.getElementById("search");
  search.value = "订单域";
  search.dispatchEvent(new window.Event("input", { bubbles: true }));
  const dimmed = Array.from(document.querySelectorAll("#canvas g.node.dim")).map((g) =>
    g.getAttribute("data-id"),
  );
  check(
    "search dims non-matching nodes",
    dimmed.length === svcNodes.length - 2 &&
      !dimmed.includes("svc.orders") &&
      !dimmed.includes("api.orders") &&
      dimmed.includes("svc.pay"),
    dimmed,
  );
  search.value = "";
  search.dispatchEvent(new window.Event("input", { bubbles: true }));
  check("clearing search restores", document.querySelectorAll("#canvas g.node.dim").length === 0);

  const sectionTab = Array.from(document.querySelectorAll("#tabs .tab")).find(
    (t) => t.textContent === "技术栈与运行时",
  );
  sectionTab.dispatchEvent(new window.Event("click", { bubbles: true }));
  check("section view active", document.getElementById("view-section").classList.contains("active"));
  const sectionText = document.getElementById("section-body").textContent;
  check("section renders paragraph", sectionText.includes("FastAPI"));
  check("section renders bullets", sectionText.includes("React 18 + Vite"));
  check("section renders anchors", sectionText.includes("api/pyproject.toml (dependencies)"));
  check("search hidden in section view", document.getElementById("search").classList.contains("hidden"));
  check("legend hidden in section view", document.getElementById("legend").classList.contains("hidden"));

  const archTab = Array.from(document.querySelectorAll("#tabs .tab")).find(
    (t) => t.textContent === "架构",
  );
  archTab.dispatchEvent(new window.Event("click", { bubbles: true }));
  check("diagram view restored after tab switch", document.getElementById("view-diagram").classList.contains("active"));
  check("diagram keeps svc sub-view", breadcrumb() === "系统 / 业务服务", breadcrumb());
  check("legend restored in diagram view", !document.getElementById("legend").classList.contains("hidden"));

  clickNode("svc.orders");
  check("panel open before escape", document.getElementById("panel").classList.contains("open"));
  window.dispatchEvent(new window.KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
  check("escape closes panel", !document.getElementById("panel").classList.contains("open"));
  check(
    "closing panel releases diagram space",
    !document.getElementById("view-diagram").classList.contains("panel-open"),
  );
  dom.window.close();
}

function runSectionBlocksSuite() {
  const block = JSON.stringify({
    title: "块类型",
    summary: "",
    modules: [{ id: "a", label: "模块", layer: "core", summary: "s" }],
    edges: [],
    sections: [
      {
        title: "全部块类型",
        blocks: [
          { type: "p", text: "段落文字" },
          { type: "heading", text: "执行顺序" },
          { type: "steps", items: ["读取输入", "写出结果"] },
          {
            type: "table",
            columns: ["数据", "写入者"],
            rows: [["report.md", "Pipeline"], ["papers.json", "Index service"]],
          },
          { type: "bullets", items: ["条目一", "条目二"] },
          { type: "code", text: "python app.py" },
          { type: "anchors", items: ["app.py (main)"] },
        ],
      },
    ],
  });
  const dom = loadDom(block);
  const { window } = dom;
  const { document } = window;
  const tab = Array.from(document.querySelectorAll("#tabs .tab")).find(
    (t) => t.textContent === "全部块类型",
  );
  check("custom section tab exists", !!tab);
  tab.dispatchEvent(new window.Event("click", { bubbles: true }));
  const body = document.getElementById("section-body");
  check("p block rendered", body.textContent.includes("段落文字"));
  check("heading block rendered", body.querySelector("h3")?.textContent === "执行顺序");
  check("steps block rendered as ordered list", body.querySelectorAll("ol.steps li").length === 2);
  check("table block renders headers and rows", body.querySelectorAll("table.report-table th").length === 2 && body.querySelectorAll("table.report-table tbody tr").length === 2);
  check("bullets block rendered", body.querySelectorAll("ul li").length === 2);
  check("code block rendered", body.querySelector("pre")?.textContent === "python app.py");
  check("anchors block rendered", body.querySelectorAll(".chip").length === 1);
  dom.window.close();
}

async function runInteractionSuite() {
  const dom = loadDom(defaultBlock);
  const { window } = dom;
  const { document } = window;
  const node = () => document.querySelector('#canvas g.node[data-id="web"]');
  const rect = () => node().querySelector("rect");
  const scene = () => document.querySelector("#canvas g.scene");
  const transform = () => scene().getAttribute("transform") || "";
  const PointerLikeEvent = typeof window.PointerEvent === "function" ? window.PointerEvent : window.MouseEvent;
  const downEvent = typeof window.PointerEvent === "function" ? "pointerdown" : "mousedown";
  const moveEvent = typeof window.PointerEvent === "function" ? "pointermove" : "mousemove";
  const upEvent = typeof window.PointerEvent === "function" ? "pointerup" : "mouseup";

  check("diagram toolbar is present", !!document.getElementById("diagram-toolbar"));
  check(
    "toolbar exposes fit and reset actions",
    !!document.querySelector('[data-canvas-action="fit"]') &&
      !!document.querySelector('[data-canvas-action="reset"]'),
  );
  check("scene has an initial transform", /^translate\(/.test(transform()), transform());

  const beforeX = Number(rect().getAttribute("x"));
  const beforeY = Number(rect().getAttribute("y"));
  node().dispatchEvent(
    new PointerLikeEvent(downEvent, { bubbles: true, button: 0, clientX: 100, clientY: 100 }),
  );
  window.dispatchEvent(
    new PointerLikeEvent(moveEvent, { bubbles: true, clientX: 140, clientY: 125 }),
  );
  window.dispatchEvent(
    new PointerLikeEvent(upEvent, { bubbles: true, button: 0, clientX: 140, clientY: 125 }),
  );
  const afterX = Number(rect().getAttribute("x"));
  const afterY = Number(rect().getAttribute("y"));
  check("node drag changes node position", afterX !== beforeX || afterY !== beforeY, {
    beforeX,
    beforeY,
    afterX,
    afterY,
  });
  check(
    "node drag does not open the detail panel as a click",
    !document.getElementById("panel").classList.contains("open"),
  );
  check("node drag class is cleared on mouseup", !node().classList.contains("dragging"));
  await new Promise((resolve) => window.setTimeout(resolve, 20));
  node().dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  check(
    "delayed synthetic click after a node drag is suppressed",
    !document.getElementById("panel").classList.contains("open"),
  );

  const beforePan = transform();
  document.getElementById("canvas").dispatchEvent(
    new PointerLikeEvent(downEvent, { bubbles: true, button: 0, clientX: 200, clientY: 200 }),
  );
  window.dispatchEvent(
    new PointerLikeEvent(moveEvent, { bubbles: true, clientX: 230, clientY: 220 }),
  );
  window.dispatchEvent(
    new PointerLikeEvent(upEvent, { bubbles: true, button: 0, clientX: 230, clientY: 220 }),
  );
  check("background drag pans the scene", transform() !== beforePan, {
    beforePan,
    afterPan: transform(),
  });

  const beforeZoom = transform();
  document.getElementById("canvas").dispatchEvent(
    new window.WheelEvent("wheel", { bubbles: true, deltaY: -120, clientX: 240, clientY: 180 }),
  );
  check("wheel zoom changes the scene transform", transform() !== beforeZoom, {
    beforeZoom,
    afterZoom: transform(),
  });
  const zoomOut = document.querySelector('[data-canvas-action="zoom-out"]');
  check("zoom controls are present", !!zoomOut && !!document.querySelector('[data-canvas-action="zoom-in"]'));
  zoomOut.dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  document.querySelector('[data-canvas-action="fit"]').dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  check("fit action keeps a scene transform", /^translate\(/.test(transform()), transform());
  document.querySelector('[data-canvas-action="reset"]').dispatchEvent(new window.MouseEvent("click", { bubbles: true }));
  check("reset action restores the node to its layout position", Number(rect().getAttribute("x")) === beforeX);
  dom.window.close();
}

function runMixedEdgeSuite() {
  const block = JSON.stringify({
    title: "混合聚合边",
    summary: "",
    modules: [
      { id: "left", label: "Left", layer: "entry", summary: "" },
      { id: "left.flow", parent: "left", label: "Flow", layer: "entry", summary: "" },
      { id: "left.dep", parent: "left", label: "Dependency", layer: "entry", summary: "" },
      { id: "right", label: "Right", layer: "core", summary: "" },
      { id: "right.flow", parent: "right", label: "Flow target", layer: "core", summary: "" },
      { id: "right.dep", parent: "right", label: "Dependency target", layer: "core", summary: "" },
    ],
    edges: [
      { from: "left.flow", to: "right.flow", label: "invoke", kind: "flow" },
      { from: "left.dep", to: "right.dep", label: "deploy", kind: "dep" },
    ],
    sections: [],
  });
  const dom = loadDom(block);
  const { document } = dom.window;
  const edge = document.querySelector('#canvas g.edge[data-from="left"][data-to="right"]');
  check("mixed lifted relationships remain aggregated", edge?.getAttribute("data-edge-count") === "2");
  check("mixed lifted relationships expose both kinds", edge?.getAttribute("data-edge-kinds") === "flow,dep");
  check("mixed lifted relationships use a distinct edge style", edge?.classList.contains("mixed"));
  check(
    "mixed lifted relationship title preserves both semantics",
    edge?.querySelector("title")?.textContent.includes("调用/数据流") &&
      edge?.querySelector("title")?.textContent.includes("依赖/部署"),
    edge?.querySelector("title")?.textContent,
  );
  dom.window.close();
}

function runRoutingSuite() {
  const block = JSON.stringify({
    title: "避障路由",
    summary: "",
    modules: [
      { id: "source", label: "Source", layer: "entry", summary: "" },
      { id: "middle", label: "Middle", layer: "core", summary: "" },
      { id: "target", label: "Target", layer: "data", summary: "" },
    ],
    edges: [
      { from: "source", to: "middle", label: "step one", kind: "flow" },
      { from: "middle", to: "target", label: "step two", kind: "flow" },
      { from: "source", to: "target", label: "long path", kind: "dep" },
    ],
    sections: [],
  });
  const dom = loadDom(block);
  const { document } = dom.window;
  const rects = {};
  document.querySelectorAll("#canvas g.node").forEach((node) => {
    const rect = node.querySelector("rect");
    rects[node.getAttribute("data-id")] = {
      x: Number(rect.getAttribute("x")),
      y: Number(rect.getAttribute("y")),
      w: Number(rect.getAttribute("width")),
      h: Number(rect.getAttribute("height")),
    };
  });
  function parseRoute(edge) {
    return edge
      .getAttribute("data-route")
      .split(";")
      .map((point) => {
        const [x, y] = point.split(",").map(Number);
        return { x, y };
      });
  }
  function crossesRect(a, b, rect) {
    const eps = 0.01;
    if (Math.abs(a.y - b.y) < eps) {
      if (!(a.y > rect.y + eps && a.y < rect.y + rect.h - eps)) return false;
      return Math.max(a.x, b.x) > rect.x + eps && Math.min(a.x, b.x) < rect.x + rect.w - eps;
    }
    if (Math.abs(a.x - b.x) < eps) {
      if (!(a.x > rect.x + eps && a.x < rect.x + rect.w - eps)) return false;
      return Math.max(a.y, b.y) > rect.y + eps && Math.min(a.y, b.y) < rect.y + rect.h - eps;
    }
    return true;
  }
  let allOrthogonal = true;
  let obstacleFree = true;
  document.querySelectorAll("#canvas g.edge").forEach((edge) => {
    const from = edge.getAttribute("data-from");
    const to = edge.getAttribute("data-to");
    const route = parseRoute(edge);
    for (let i = 1; i < route.length; i++) {
      const a = route[i - 1];
      const b = route[i];
      if (Math.abs(a.x - b.x) > 0.01 && Math.abs(a.y - b.y) > 0.01) allOrthogonal = false;
      for (const [id, rect] of Object.entries(rects)) {
        if (id !== from && id !== to && crossesRect(a, b, rect)) obstacleFree = false;
      }
    }
  });
  check("all edge routes are orthogonal", allOrthogonal);
  check("edge routes avoid non-endpoint nodes", obstacleFree);
  const longEdge = document.querySelector('#canvas g.edge[data-from="source"][data-to="target"]');
  check("long edge exposes a routed polyline", parseRoute(longEdge).length >= 4, longEdge.getAttribute("data-route"));
  check("normal routing does not use the failure fallback", document.querySelectorAll('#canvas g.edge[data-route-failed="true"]').length === 0);

  const visibleLabels = Array.from(document.querySelectorAll("#canvas .edge-label-bg:not(.colliding)")).map(
    (rect) => ({
      x: Number(rect.getAttribute("x")),
      y: Number(rect.getAttribute("y")),
      w: Number(rect.getAttribute("width")),
      h: Number(rect.getAttribute("height")),
    }),
  );
  let labelsOverlap = false;
  for (let i = 0; i < visibleLabels.length; i++) {
    for (let j = i + 1; j < visibleLabels.length; j++) {
      const a = visibleLabels[i];
      const b = visibleLabels[j];
      if (a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y) labelsOverlap = true;
    }
  }
  check("visible edge labels do not overlap", !labelsOverlap, visibleLabels);
  dom.window.close();
}

function runLongLabelSuite() {
  const block = JSON.stringify({
    title: "长标签",
    summary: "",
    modules: [
      { id: "left", label: "Left", layer: "entry", summary: "" },
      { id: "right", label: "Right", layer: "core", summary: "" },
    ],
    edges: [
      { from: "left", to: "right", label: "按 recipient/device 路由", kind: "flow" },
    ],
    sections: [],
  });
  const dom = loadDom(block);
  const { document } = dom.window;
  const edge = document.querySelector("#canvas g.edge");
  check("long short-edge label remains visible", !edge.querySelector(".edge-label.colliding"));
  check(
    "long short-edge label keeps the full hover title",
    edge.querySelector("title")?.textContent === "按 recipient/device 路由",
    edge.querySelector("title")?.textContent,
  );
  check(
    "long short-edge label may use an ellipsis",
    edge.querySelector(".edge-label")?.textContent.length <= "按 recipient/device 路由".length,
    edge.querySelector(".edge-label")?.textContent,
  );
  dom.window.close();
}

function runArxivRoutingSuite() {
  const block = JSON.stringify({
    title: "reader-first arxiv routing fixture",
    summary: "",
    modules: [
      { id: "plugin", label: "Obsidian 插件 / Host", layer: "frontend", summary: "组装 Core，承载 UI 与调度" },
      { id: "plugin.composition", parent: "plugin", label: "Composition root", layer: "frontend", summary: "构造端口并注册产品入口" },
      { id: "plugin.adapters", parent: "plugin", label: "Obsidian adapters", layer: "infra", summary: "实现六个 Host 端口" },
      { id: "cli", label: "CLI / 一次性 Host", layer: "entry", summary: "按命令组装 Core 后退出" },
      { id: "cli.command", parent: "cli", label: "命令入口", layer: "entry", summary: "解析 run、email 与 schedule" },
      { id: "cli.composition", parent: "cli", label: "Runtime builder", layer: "entry", summary: "构造共享 Core runtime" },
      { id: "cli.adapters", parent: "cli", label: "Node adapters", layer: "infra", summary: "库，不是独立进程" },
      { id: "core", label: "共享业务 Core", layer: "core", summary: "日报、阅读、状态与投递规则" },
      { id: "core.ports", parent: "core", label: "Host 端口契约", layer: "core", summary: "隔离 Obsidian 与 Node API" },
      { id: "core.scheduler", parent: "core", label: "调度器", layer: "core", summary: "提交运行状态并触发用例" },
      { id: "core.daily", parent: "core", label: "日报生成", layer: "core", summary: "发现、过滤、总结、写 Markdown" },
      { id: "core.digest", parent: "core", label: "Digest 投影", layer: "core", summary: "从完成结果构造邮件内容" },
      { id: "core.delivery", parent: "core", label: "邮件投递", layer: "core", summary: "完成提交后 self 或 hosted 发送" },
      { id: "core.persistence", parent: "core", label: "一致性服务", layer: "core", summary: "索引、状态、checkpoint 与 claim" },
      { id: "vault", label: "共享 Vault 数据", layer: "data", summary: "Markdown 与跨 Host 运行记忆" },
      { id: "vault.paper-index", parent: "vault", label: "papers.json", layer: "data", summary: "用户状态与可修复字段并存" },
      { id: "vscode", label: "VS Code Companion", layer: "frontend", summary: "直接读索引并启动 CLI" },
      { id: "vscode.index", parent: "vscode", label: "索引读写", layer: "frontend", summary: "绕过 Core 直接改 JSON" },
      { id: "vscode.cli", parent: "vscode", label: "CLI bridge", layer: "frontend", summary: "ProcessExecution 启动命令" },
      { id: "relay", label: "官方邮件 Relay", layer: "infra", summary: "验证、限流、幂等与代发" },
      { id: "relay.http", parent: "relay", label: "Worker API", layer: "infra", summary: "鉴权并路由 deliver 请求" },
      { id: "relay.resend", parent: "relay", label: "Resend client", layer: "infra", summary: "提交最终邮件请求" },
      { id: "external", label: "外部 API", layer: "external", summary: "arXiv、LLM 与 Resend" },
      { id: "external.resend", parent: "external", label: "Resend", layer: "external", summary: "最终邮件提供商" },
    ],
    edges: [
      { from: "plugin.composition", to: "plugin.adapters", label: "构造六个端口", kind: "dep" },
      { from: "plugin.composition", to: "core.ports", label: "组装并调用", kind: "dep" },
      { from: "cli.composition", to: "cli.adapters", label: "构造 Node 端口", kind: "dep" },
      { from: "cli.composition", to: "core.ports", label: "组装并调用", kind: "dep" },
      { from: "vscode.cli", to: "cli.command", label: "启动命令", kind: "flow" },
      { from: "core.scheduler", to: "core.daily", label: "按日期运行", kind: "flow" },
      { from: "core.daily", to: "core.digest", label: "返回邮件投影", kind: "flow" },
      { from: "core.scheduler", to: "core.delivery", label: "completed 后回调", kind: "flow" },
      { from: "core.daily", to: "core.persistence", label: "提交报告与索引", kind: "flow" },
      { from: "core", to: "vault", label: "写报告与运行状态", kind: "flow" },
      { from: "vscode.index", to: "vault.paper-index", label: "直接读写", kind: "flow" },
      { from: "core", to: "external", label: "论文、LLM 与 self 邮件", kind: "flow" },
      { from: "core.delivery", to: "relay.http", label: "hosted 投递", kind: "flow" },
      { from: "relay.http", to: "relay.resend", label: "通过 gate 后发送", kind: "flow" },
      { from: "relay.resend", to: "external.resend", label: "邮件请求", kind: "flow" },
    ],
    sections: [],
  });
  const dom = loadDom(block);
  const { document, Event } = dom.window;
  const root = routeInteractions(document);
  check("arxiv overview routes have no non-shared touches", root.touch.length === 0, root);
  check("arxiv overview routes have no overlaps", root.overlap.length === 0, root);
  check("reader-first overview has 7 top-level concepts", document.querySelectorAll("#canvas g.node").length === 7);
  check("reader-first overview has no proper crossings", root.proper.length === 0, root);
  document
    .querySelector('#canvas g.node[data-id="core"]')
    .dispatchEvent(new Event("click", { bubbles: true }));
  const core = routeInteractions(document);
  check(
    "core drill-down routes have no non-shared interactions",
    core.proper.length === 0 && core.touch.length === 0 && core.overlap.length === 0,
    core,
  );
  dom.window.close();
}

function runFatalSuites() {
  for (const [name, block] of [
    ["malformed JSON", '{ "title": '],
    ["string JSON", '"just a string"'],
    ["null JSON", "null"],
  ]) {
    const dom = loadDom(block);
    const { window } = dom;
    const { document } = window;
    check(
      `${name} shows fatal overlay`,
      !document.getElementById("fatal").classList.contains("hidden"),
    );
    check(`${name} renders no tabs`, document.querySelectorAll("#tabs .tab").length === 0);
    dom.window.close();
  }
}

function runDuplicateIdSuite() {
  const block = JSON.stringify({
    title: "dup",
    summary: "",
    modules: [
      { id: "a", label: "第一个", layer: "core", summary: "" },
      { id: "a", label: "第二个", layer: "entry", summary: "" },
    ],
    edges: [],
    sections: [],
  });
  const warnings = [];
  const dom = loadDom(block, (window) => {
    window.console.warn = (...args) => warnings.push(args.join(" "));
  });
  const { window } = dom;
  const { document } = window;
  check("duplicate id warns on console", warnings.length === 1 && warnings[0].includes("重复的模块 id"), warnings);
  check("duplicate id keeps first entry", document.querySelectorAll("#canvas g.node").length === 1);
  check(
    "duplicate id renders first label",
    document.querySelector("#canvas g.node text").textContent === "第一个",
  );
  dom.window.close();
}

function runXssSuite() {
  const block = JSON.stringify({
    title: '<img src=x onerror="window.__pwned=1">',
    summary: "",
    modules: [
      {
        id: "a",
        label: '<img src=x onerror="window.__pwned=1">',
        layer: "core",
        summary: '<script>window.__pwned=2<\\/script>',
        detail: '<svg onload="window.__pwned=3"></svg>',
      },
    ],
    edges: [],
    sections: [],
  });
  const dom = loadDom(block);
  const { window } = dom;
  const { document } = window;
  check("xss payload not executed", window.__pwned === undefined, window.__pwned);
  check("xss payload not injected as elements", document.querySelector("#canvas img, #canvas script, #canvas svg") === null);
  check(
    "xss payload rendered as literal text",
    document.getElementById("title").textContent.includes("<img"),
  );
  const node = document.querySelector('#canvas g.node[data-id="a"]');
  node.dispatchEvent(new window.Event("click", { bubbles: true }));
  check("xss payload literal in panel", document.getElementById("panel").textContent.includes("<svg"));
  dom.window.close();
}

runOverviewSuite();
runSectionBlocksSuite();
await runInteractionSuite();
runMixedEdgeSuite();
runRoutingSuite();
runLongLabelSuite();
runArxivRoutingSuite();
runFatalSuites();
runDuplicateIdSuite();
runXssSuite();

console.log(`${passed}/${passed + failed} checks passed`);
process.exit(failed ? 1 : 0);
