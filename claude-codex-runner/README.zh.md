# Claude Codex Runner

[English](README.md)

在 Claude Code 中把任务交给 Codex CLI 执行，然后总结结果。

## 两种执行模式

### Agent 模式（默认）— 简单任务

搜索网页、生成图表、理解图片、写短脚本、小范围代码改动。

**流程：** 用户提出请求 → Claude Code 直接用 Agent 工具调 `codex exec`（后台运行）→ Agent 返回结果 → Claude 总结给你。

不需要写 task.md，一句话就能干。

适合场景：
- "搜一下今天 arxiv 上 astro-ph.CO 更新了多少篇文章"
- "画一个 mermaid 时序图，展示用户登录流程"
- "分析这张图 /path/to/fig.png"
- "把这个函数改成异步版本"

如果需要结构化约束，也可以先写一个 `docs/tasks/<task-id>/task.md`，然后在 Agent prompt 里引用它。

### Runner 模式 — 复杂任务

跨文件重构、需要精确范围约束、验证步骤、可能需要多轮迭代的任务。

**流程：** 写 task.md → `runner start` 后台跑 → `runner status` 查进度 → `runner result` 读报告 → 需要时 `runner resume` 继续。

```bash
# 入口
R=~/.claude/skills/claude-codex-runner/tools/runner

# 启动（后台）
"$R" start docs/tasks/<task-id>/task.md --provider <profile>

# 查看进度（带最近日志输出）
"$R" status <task-id>

# 查看报告
"$R" result <task-id>

# 继续未完成的任务
"$R" resume <task-id> --goal "<后续目标>" --start

# 列出所有任务
"$R" list

# 取消任务
"$R" cancel <task-id>
```

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash
```

默认安装到 Claude Code。源码仓库是 [github.com/tdccccc/skills](https://github.com/tdccccc/skills)。

## 设计原则

- **Claude Code 是分析大脑 + 结果阅读器**：理解需求、约束范围、读报告总结
- **Codex 是执行器**：负责工程实现、网络搜索、多模态理解、图表生成
- **`-a never` = 自动批准**：不弹确认框，安全性由 sandbox 隔离保证
- **默认 workspace-write**：Codex 需要写 report 和目标文件
- **沙箱兜底**：`read-only` / `workspace-write` / `danger-full-access`

## 目录结构

```
claude-codex-runner/
├── SKILL.md                       # 主文档（Claude Code 读取）
├── README.md                      # 本文件
├── README.zh.md                   # 中文文档
├── tools/
│   ├── runner                     # 入口脚本（bash）
│   └── codex_runner/              # Python 包
│       ├── cli.py                 # CLI 子命令
│       └── runner.py              # 核心逻辑
└── references/                    # 参考文档
    ├── task-template.md
    ├── codex-task-contract.md
    └── runner-workflow.md
```

## 配置 MCP 工具（可选）

Codex 开箱即可搜索网页和生成图表。如果需要额外能力（数据库访问、外部 API 等），直接在 Codex 中配置 MCP：

```bash
codex mcp add <name> -- <command>
# 或
codex mcp add <name> --url <url>
```

MCP 配置后自动在 `codex exec` 模式中生效，runner 不需要任何修改。
