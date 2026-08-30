#!/usr/bin/env bash
# architecture-map 真实浏览器冒烟检查（headless Chrome，可选依赖）。
# 运行：tests/smoke_architecture_map_browser.sh <report.html> [more...]
# 在没有 Chrome/Node 的环境输出 SKIP 并退出 2；全部通过退出 0；有失败退出 1。
# 在两种视口（1600x1000 桌面、1024x768 窄屏）渲染报告并注入探针检查：
# 无 fatal 遮罩、图表视图激活、面板关闭、节点/边/图例渲染、无 route-failed
# 标记、无隐藏标签、主题可切换重绘、无未捕获错误。
set -u

CHROME=""
for candidate in google-chrome google-chrome-stable chromium chromium-browser; do
  if command -v "$candidate" >/dev/null 2>&1; then CHROME="$candidate"; break; fi
done
if [ -z "$CHROME" ]; then
  echo "SKIP: google-chrome / chromium 未安装"
  exit 2
fi
if ! command -v node >/dev/null 2>&1; then
  echo "SKIP: node 未安装"
  exit 2
fi
if [ "$#" -eq 0 ]; then
  echo "usage: tests/smoke_architecture_map_browser.sh <report.html> [more...]" >&2
  exit 2
fi

PASSED=0
FAILURES=0

for report in "$@"; do
  if [ ! -f "$report" ]; then
    echo "FAIL $report file not found"
    FAILURES=$((FAILURES + 1))
    continue
  fi
  WORKDIR="$(mktemp -d)"
  cp "$report" "$WORKDIR/copy.html"

  # 注入探针：记录页面状态并切换一次主题（探针只在临时副本中，报告本身不变）
  if ! node -e '
    const fs = require("fs");
    const html = fs.readFileSync(process.argv[1], "utf8");
    const probe = `<script>
    (function () {
      var errors = [];
      window.addEventListener("error", function (e) { errors.push(String(e.message || e.error)); });
      window.addEventListener("unhandledrejection", function () { errors.push("unhandledrejection"); });
      function record() {
        var tabs = document.getElementById("tabs");
        var report = {
          width: window.innerWidth,
          theme: document.documentElement.getAttribute("data-theme"),
          fatalHidden: document.getElementById("fatal").classList.contains("hidden"),
          panelOpen: document.getElementById("panel").classList.contains("open"),
          diagramActive: document.getElementById("view-diagram").classList.contains("active"),
          nodes: document.querySelectorAll("#canvas g.node").length,
          edges: document.querySelectorAll("#canvas g.edge").length,
          legendRows: document.querySelectorAll("#legend .legend-row").length,
          routeFailed: document.querySelectorAll("#canvas g.edge[data-route-failed=\\"true\\"]").length,
          hiddenLabels: document.querySelectorAll("#canvas .edge-label.colliding").length,
          tabsScrollable: tabs.scrollWidth > tabs.clientWidth,
          errors: errors,
          themeAfterToggle: null,
          nodeFillChanged: null
        };
        var btn = document.querySelector("[data-canvas-action=\\"theme\\"]");
        if (btn) {
          var fill = document.querySelector("#canvas g.node rect").getAttribute("fill");
          btn.click();
          report.themeAfterToggle = document.documentElement.getAttribute("data-theme");
          report.nodeFillChanged = document.querySelector("#canvas g.node rect").getAttribute("fill") !== fill;
        }
        var div = document.createElement("div");
        div.id = "smoke-report";
        div.textContent = JSON.stringify(report);
        document.body.appendChild(div);
      }
      window.addEventListener("load", function () { setTimeout(record, 250); });
    })();
    <\/script>`;
    fs.writeFileSync(process.argv[1], html.replace("</body>", probe + "\n</body>"));
  ' "$WORKDIR/copy.html"; then
    echo "FAIL $report probe injection failed"
    FAILURES=$((FAILURES + 1))
    rm -rf "$WORKDIR"
    continue
  fi

  for size in "1600 1000" "1024 768"; do
    read -r W H <<< "$size"
    DUMP="$("$CHROME" --headless=new --disable-gpu --dump-dom --hide-scrollbars \
      --window-size="$W,$H" --virtual-time-budget=2000 \
      "file://$WORKDIR/copy.html" 2>/dev/null)"
    RESULT="$(printf '%s' "$DUMP" | node -e '
      const dump = require("fs").readFileSync(0, "utf8");
      const m = dump.match(/<div id="smoke-report">([\s\S]*?)<\/div>/);
      if (!m) { console.log("FAIL " + process.argv[1] + " smoke-report div missing"); process.exit(1); }
      const r = JSON.parse(m[1]);
      const problems = [];
      if (r.theme !== "dark") problems.push("theme=" + r.theme);
      if (r.fatalHidden !== true) problems.push("fatal overlay visible");
      if (r.panelOpen !== false) problems.push("panel open");
      if (r.diagramActive !== true) problems.push("diagram view inactive");
      if (!(r.nodes > 0)) problems.push("no nodes");
      if (!(r.legendRows > 0)) problems.push("no legend");
      if (r.routeFailed !== 0) problems.push("routeFailed=" + r.routeFailed);
      if (r.hiddenLabels !== 0) problems.push("hiddenLabels=" + r.hiddenLabels);
      if (r.themeAfterToggle !== "light") problems.push("theme toggle failed");
      if (r.nodeFillChanged !== true) problems.push("theme did not re-render palette");
      if (r.errors.length) problems.push("console errors: " + r.errors.join("; "));
      if (!problems.length) {
        console.log("PASS " + process.argv[1] + " " + r.width + "px " + r.nodes + " nodes " + r.edges + " edges");
      } else {
        console.log("FAIL " + process.argv[1] + " " + r.width + "px " + problems.join(", "));
      }
      process.exit(problems.length ? 1 : 0);
    ' "report=$(basename "$report")")"
    echo "$RESULT"
    case "$RESULT" in
      PASS*) PASSED=$((PASSED + 1)) ;;
      *) FAILURES=$((FAILURES + 1)) ;;
    esac
  done
  rm -rf "$WORKDIR"
done

if [ "$FAILURES" -eq 0 ]; then
  echo "ALL PASS ($PASSED smoke runs)"
  exit 0
fi
echo "FAILED — $FAILURES failure(s)"
exit 1