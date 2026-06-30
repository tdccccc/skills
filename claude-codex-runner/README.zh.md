# Claude Codex Runner

[English](README.md)

在 Claude Code 中把任务交给 Codex CLI 执行，然后总结结果。

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/tdccccc/skills/main/bootstrap.sh | bash
```

## 使用

### Agent 模式（默认）— 简单任务

搜索、画图、看图、小改动，一句话就能干。Claude Code 自动用 Agent 工具在后台运行 Codex：

```
你：搜一下今天 arxiv 上 astro-ph.CO 更新了多少篇文章
你：画一个 mermaid 时序图，展示用户登录流程
你：把这个函数改成异步版本
```

Agent 跑完后会自动通知你。也支持先写 `docs/tasks/<task-id>/task.md` 再引用。

### Runner 模式 — 复杂任务

跨文件重构、需要精确约束和验证、可能要多轮迭代的任务。写 task.md 后用 runner 管理。

```bash
R=~/.claude/skills/claude-codex-runner/tools/runner

# 启动（后台）
"$R" start docs/tasks/<task-id>/task.md --provider <profile>

# 查看进度
"$R" status <task-id>

# 查看报告
"$R" result <task-id>

# 继续
"$R" resume <task-id> --goal "<后续目标>" --start

# 列出任务
"$R" list

# 取消
"$R" cancel <task-id>
```
