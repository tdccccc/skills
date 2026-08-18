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

  const archTab = Array.from(document.querySelectorAll("#tabs .tab")).find(
    (t) => t.textContent === "架构",
  );
  archTab.dispatchEvent(new window.Event("click", { bubbles: true }));
  check("diagram view restored after tab switch", document.getElementById("view-diagram").classList.contains("active"));
  check("diagram keeps svc sub-view", breadcrumb() === "系统 / 业务服务", breadcrumb());

  clickNode("svc.orders");
  check("panel open before escape", document.getElementById("panel").classList.contains("open"));
  window.dispatchEvent(new window.KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
  check("escape closes panel", !document.getElementById("panel").classList.contains("open"));
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
  check("bullets block rendered", body.querySelectorAll("li").length === 2);
  check("code block rendered", body.querySelector("pre")?.textContent === "python app.py");
  check("anchors block rendered", body.querySelectorAll(".chip").length === 1);
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
runFatalSuites();
runDuplicateIdSuite();
runXssSuite();

console.log(`${passed}/${passed + failed} checks passed`);
process.exit(failed ? 1 : 0);
